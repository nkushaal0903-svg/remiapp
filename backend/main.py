from dotenv import load_dotenv
load_dotenv()

import os
import re
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ingest import ingest_file
from retrieval import chunk_text, embed_chunks, retrieve
from i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, get_language_name, get_locale, t

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-nano")

# ~80,000 tokens * 4 chars/token
MAX_CHARS = 320_000

# In-memory stores
DOCUMENT_STORE: dict[str, str] = {}
CONVERSATION_HISTORY: dict[str, list[dict]] = {}

BASE_SYSTEM_PROMPT_ASK = (
    "You are REMI, an assistant that answers questions about ONE document the "
    "user uploaded. Relevant excerpts from the document are provided to you. The "
    "user will often ask short, vague, or generic questions ('what about the costs?', "
    "'explain that part', 'is it safe?'). Infer what they mean from the excerpts "
    "and the conversation so far. Never ask them to rephrase unless the question "
    "is truly impossible to interpret. Answer ONLY from the excerpts provided. "
    "When relevant, cite the page (e.g. 'see Page 4'). If the excerpts do not "
    "contain the answer, say so plainly instead of guessing. "
    "You may only see part of the document. Answer from the provided chunks; "
    "if the answer might be elsewhere in the document, say so rather than guessing."
)


def system_prompt_ask(lang: str = DEFAULT_LOCALE) -> str:
    """Return the ask-system prompt localized to the user's language."""
    return f"{BASE_SYSTEM_PROMPT_ASK} {t('respond_in_language', lang, language=get_language_name(lang, 'en'))}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY is not set. LLM calls will fail.")
    yield


app = FastAPI(title="REMI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend index.html from the project root
FRONTEND_INDEX = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")


@app.get("/")
async def root():
    return FileResponse(FRONTEND_INDEX)


@app.get("/health")
def health():
    return {"status": "ok"}


def resolve_locale(accept_language: str | None = None, lang: str | None = None) -> str:
    """Resolve the active locale from an explicit code or Accept-Language header."""
    if lang and lang in SUPPORTED_LOCALES:
        return lang
    return get_locale(accept_language)


async def call_llm(messages: list[dict], lang: str = DEFAULT_LOCALE) -> str:
    """Call OpenAI chat-completions and return the assistant's content."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail=t("api_key_missing", lang))

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": messages,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def summarize_text(text: str, lang: str = DEFAULT_LOCALE) -> str:
    """Call OpenAI API to summarize the document text in the user's language."""
    system_prompt = (
        "You are REMI. Summarize the document clearly: a 3-4 sentence overview, "
        "then the key points as a short bullet list. Be faithful to the document; "
        "do not invent anything. "
        f"{t('respond_in_language', lang, language=get_language_name(lang, 'en'))}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    return await call_llm(messages, lang)


async def rewrite_query(history: list[dict], question: str, lang: str = DEFAULT_LOCALE) -> str:
    """Rewrite a follow-up question into a standalone search query."""
    system_prompt = (
        "You are a search query rewriter. Given a conversation about a document "
        "and a follow-up question, rewrite the question into a concise standalone "
        "search query (3-6 keywords or a short phrase) that captures the user's "
        "intent. Output ONLY the rewritten query, with no quotes, labels, or explanation. "
        f"{t('respond_in_language', lang, language=get_language_name(lang, 'en'))}"
    )

    recent = history[-6:]  # last 3 Q&A pairs max
    parts = []
    for msg in recent:
        label = "User" if msg["role"] == "user" else "Assistant"
        parts.append(f"{label}: {msg['content']}")
    parts.append(f"User: {question}")

    user_prompt = "\n".join(parts) + "\n\nRewrite the latest user question into a standalone search query:"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    rewritten = await call_llm(messages, lang)
    return rewritten.strip()


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    accept_language: str | None = Header(None, alias="accept-language"),
    lang: str | None = Query(None),
):
    locale = resolve_locale(accept_language, lang)

    if not file.filename:
        raise HTTPException(status_code=400, detail=t("no_file_provided", locale))

    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".pptx", ".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail=t("unsupported_file_type", locale, ext=ext),
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail=t("file_empty", locale))

    suffix = ext
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        text, page_count, file_type = ingest_file(tmp_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read file: {exc}")
    finally:
        os.unlink(tmp_path)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail=t("no_extractable_text", locale),
        )

    # Truncate if too large for the model's context window
    truncated = False
    pages_read = page_count
    original_len = len(text)
    if original_len > MAX_CHARS:
        text = text[:MAX_CHARS]
        truncated = True
        if file_type == "pdf":
            matches = list(re.finditer(r"\[Page (\d+)\]", text))
            if matches:
                pages_read = int(matches[-1].group(1))
        elif file_type == "pptx":
            matches = list(re.finditer(r"\[Slide (\d+)\]", text))
            if matches:
                pages_read = int(matches[-1].group(1))
        else:
            # Proportional estimate for docx / text
            pages_read = max(1, int(page_count * MAX_CHARS / original_len))

    document_id = str(uuid.uuid4())
    DOCUMENT_STORE[document_id] = text
    CONVERSATION_HISTORY[document_id] = []

    # Chunk, embed, and store for RAG
    chunks = chunk_text(text)
    embed_chunks(document_id, chunks)

    try:
        summary = await summarize_text(text, locale)
    except httpx.HTTPStatusError as exc:
        detail = t("llm_api_error", locale, status=exc.response.status_code)
        try:
            detail = exc.response.json().get("error", {}).get("message", detail)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=detail)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=t("llm_request_failed", locale, error=str(exc)),
        )

    return {
        "document_id": document_id,
        "summary": summary,
        "page_count": page_count,
        "truncated": truncated,
        "pages_read": pages_read,
        "file_type": file_type,
    }


class AskRequest(BaseModel):
    document_id: str
    question: str


@app.post("/ask")
async def ask(
    body: AskRequest,
    accept_language: str | None = Header(None, alias="accept-language"),
    lang: str | None = Query(None),
):
    locale = resolve_locale(accept_language, lang)
    document_id = body.document_id
    question = body.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail=t("question_empty", locale))

    if document_id not in DOCUMENT_STORE:
        raise HTTPException(
            status_code=404,
            detail=t("document_not_found", locale),
        )

    history = CONVERSATION_HISTORY.get(document_id, [])

    # 1. Rewrite the question into a standalone search query
    try:
        search_query = await rewrite_query(history, question, locale)
        if not search_query:
            search_query = question
    except Exception:
        search_query = question

    # 2. Retrieve relevant chunks using the rewritten query
    chunks = retrieve(document_id, search_query, k=8)
    if not chunks:
        raise HTTPException(status_code=404, detail=t("no_context_found", locale))

    context = "\n\n---\n\n".join(chunks)

    # Build messages: system -> retrieved excerpts -> history -> new question
    messages: list[dict] = [{"role": "system", "content": system_prompt_ask(locale)}]
    messages.append({"role": "user", "content": f"Here are relevant excerpts from the document:\n\n{context}"})
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        answer = await call_llm(messages, locale)
    except httpx.HTTPStatusError as exc:
        detail = t("llm_api_error", locale, status=exc.response.status_code)
        try:
            detail = exc.response.json().get("error", {}).get("message", detail)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=detail)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=t("llm_request_failed", locale, error=str(exc)),
        )

    # Update history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    CONVERSATION_HISTORY[document_id] = history

    return {"answer": answer}
