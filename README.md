# REMI

**REMI** is a lightweight, fully-local RAG (Retrieval-Augmented Generation) document chatbot. Upload any PDF, Word, PowerPoint, or text file and instantly chat with it — get summaries, ask follow-up questions, and receive cited answers grounded in your document.

![Tech stack](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-format Support** | PDF, DOCX, PPTX, TXT, MD |
| 🧠 **Smart Summaries** | Auto-generated document overview on upload |
| 💬 **Context-aware Chat** | Follow-up questions automatically rewritten for better retrieval |
| 🔍 **In-memory RAG** | Sentence-transformer embeddings with cosine-similarity search |
| 🎨 **Liquid Glass UI** | Modern glassmorphism frontend with zero build step |
| ⚡ **Zero Database** | 100% in-memory — no Docker, no Postgres, no ChromaDB |
| 🌐 **Multilingual** | Localized UI + API responses in English, Hindi, and Telugu |

---

## 🏗 Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐
│  Frontend   │ ◄─────────────► │   FastAPI    │
│  (index.html)│                 │   Backend    │
└─────────────┘                 └──────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              ┌─────────┐      ┌─────────────┐     ┌──────────┐
              │ ingest  │      │  sentence   │     │  OpenAI  │
              │(pymupdf │      │ transformers│     │   API    │
              │ docx..) │      │  (MiniLM)   │     │          │
              └─────────┘      └─────────────┘     └──────────┘
```

---

## 🚀 Quick Start

### 1. Clone & enter

```bash
git clone https://github.com/nkushaal0903-svg/remiapp.git
cd remiapp
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API key

Create a `.env` file inside `backend/`:

```env
OPENAI_API_KEY=sk-your-key-here
```

> Optional: set `OPENAI_BASE_URL` and `OPENAI_MODEL` to use a different provider.

### 4. Run

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open frontend

Simply open `frontend/index.html` in your browser, or serve it:

```bash
# Using Python
cd frontend
python -m http.server 3000

# Then visit http://localhost:3000
```

---

## 📁 Project Structure

```
remiapp/
├── backend/
│   ├── main.py           # FastAPI routes (upload, ask, health)
│   ├── i18n.py           # Locale resolution + translation catalog
│   ├── ingest.py         # File parsing (PDF, DOCX, PPTX, TXT, MD)
│   ├── retrieval.py      # Chunking, embedding, similarity search
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Your OpenAI API key
├── frontend/
│   └── index.html        # Complete single-page UI with language switcher
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check |
| `POST` | `/upload` | Upload a document (multipart/form-data) |
| `POST` | `/ask`    | Ask a question about the uploaded document |

Both `/upload` and `/ask` honor the `Accept-Language` header and an optional `lang` query parameter (`en`, `hi`, `ta`).

### Supported languages

REMI is localized into:

| Locale | Language | Script |
|--------|----------|--------|
| `en`   | English  | Latin  |
| `hi`   | Hindi    | Devanagari |
| `te`   | Telugu   | Telugu |

Switch languages from the header in the UI, or call the API with `?lang=hi` / `?lang=te`. The choice is persisted in `localStorage`.

### Example: Upload

```bash
curl -X POST "http://localhost:8000/upload?lang=te" \
  -F "file=@document.pdf"
```

### Example: Ask

```bash
curl -X POST "http://localhost:8000/ask?lang=te" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "uuid-string", "question": "ప్రధాన నిర్ణయాలు ఏమిటి?"}'
```

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "summary": "This document discusses...",
  "page_count": 12,
  "truncated": false,
  "pages_read": 12,
  "file_type": "pdf"
}
```

### Example: Ask

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "uuid-string", "question": "What are the key findings?"}'
```

**Response:**
```json
{
  "answer": "According to Page 4, the key findings are..."
}
```

---

## ⚙️ How It Works

1. **Ingest** — Extracts text from your file with page/slide markers preserved.
2. **Chunk** — Splits text into 1,000-character overlapping chunks at paragraph boundaries.
3. **Embed** — Encodes chunks with `all-MiniLM-L6-v2` (~90MB download on first run).
4. **Retrieve** — When you ask a question, it's rewritten into a standalone search query, then the top-8 most similar chunks are fetched via cosine similarity.
5. **Answer** — The LLM receives the relevant excerpts + conversation history and answers **only from the provided context**.

---

## 🌍 i18n vs l10n

This project follows the W3C/Mozilla distinction:

- **Internationalization (i18n)** is the design and development that *enables* easy localization. REMI's i18n layer is the locale resolver, the `t()` helper, and the `data-i18n` markup in the frontend — none of these know Hindi or Telugu specifically, but they make adding those languages possible.
- **Localization (l10n)** is the actual *adaptation* of content to a locale. The translation dictionaries in `backend/i18n.py` and the frontend `TRANSLATIONS` object are the l10n artifacts.

Adding a fourth language (e.g. `kn` Kannada or `te` Telugu) only requires adding a new dictionary entry on both sides; the rest of the code stays unchanged.

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| File Parsing | PyMuPDF, python-docx, python-pptx |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | OpenAI API (configurable base URL & model) |
| HTTP Client | httpx |
| Frontend | Vanilla HTML/CSS/JS (no build tools) |

---

## 📝 License

MIT

---

<p align="center">Built with ❤️ by <a href="https://github.com/nkushaal0903-svg">nkushaal0903-svg</a></p>
