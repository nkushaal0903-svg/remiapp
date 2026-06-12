"""Internationalization (i18n) and localization (l10n) support for REMI.

This module separates the *mechanism* of supporting multiple locales (i18n)
from the actual translated strings for each locale (l10n). Adding a new
language only requires adding a new entry to the TRANSLATIONS dictionary.

Supported locales:
    en  - English (default fallback)
    hi  - Hindi  (Devanagari)
    te  - Telugu (Telugu script)
"""

from __future__ import annotations

import re

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = {"en", "hi", "te"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # UI labels
        "app_title": "REMI",
        "app_subtitle": "Upload a file, get a summary, then ask follow-up questions.",
        "drop_file": "Drop your file here",
        "click_to_browse": "or click anywhere in this area to browse",
        "supported_formats": "Supported formats: PDF, DOCX, PPTX, TXT, MD",
        "upload_reading": "Reading and summarizing...",
        "new_document": "New document",
        "summary_heading": "Summary",
        "pages_label": "{count} pages",
        "slides_label": "{count} slides",
        "lines_label": "{count} lines",
        "pages_unit": "pages",
        "slides_unit": "slides",
        "lines_unit": "lines",
        "truncation_warning": "Large document — REMI read the first {pages_read} {unit}.",
        "chat_welcome_title": "Welcome to REMI",
        "chat_welcome_text": "Ask me anything about your document. I will find the most relevant sections and answer from them.",
        "question_placeholder": "Ask a question about your document...",
        "send_button": "Send",
        "thinking": "REMI is thinking...",
        "unsupported_file_alert": "Please upload a supported file (.pdf, .docx, .pptx, .txt, .md).",
        "upload_failed_prefix": "Upload failed",
        "request_failed_prefix": "Request failed",
        "error_prefix": "Error",
        # API errors
        "no_file_provided": "No file provided.",
        "file_empty": "Uploaded file is empty.",
        "unsupported_file_type": "Unsupported file type: '{ext}'. Supported: .pdf, .docx, .pptx, .txt, .md",
        "no_extractable_text": "No extractable text found in the file.",
        "api_key_missing": "OPENAI_API_KEY not configured.",
        "question_empty": "Question cannot be empty.",
        "document_not_found": "Document not found. Upload a file first.",
        "no_context_found": "No document context found.",
        "llm_api_error": "LLM API error ({status}).",
        "llm_request_failed": "LLM request failed: {error}",
        # LLM prompt additions
        "respond_in_language": "Respond in {language}.",
    },
    "hi": {
        # UI labels
        "app_title": "REMI",
        "app_subtitle": "फ़ाइल अपलोड करें, सारांश प्राप्त करें, फिर अनुवर्ती प्रश्न पूछें।",
        "drop_file": "अपनी फ़ाइल यहाँ छोड़ें",
        "click_to_browse": "या ब्राउज़ करने के लिए इस क्षेत्र में कहीं भी क्लिक करें",
        "supported_formats": "समर्थित प्रारूप: PDF, DOCX, PPTX, TXT, MD",
        "upload_reading": "पढ़ रहा हूँ और सारांश तैयार कर रहा हूँ...",
        "new_document": "नया दस्तावेज़",
        "summary_heading": "सारांश",
        "pages_label": "{count} पृष्ठ",
        "slides_label": "{count} स्लाइड",
        "lines_label": "{count} पंक्तियाँ",
        "pages_unit": "पृष्ठ",
        "slides_unit": "स्लाइड",
        "lines_unit": "पंक्तियाँ",
        "truncation_warning": "बड़ा दस्तावेज़ — REMI ने पहले {pages_read} {unit} पढ़े।",
        "chat_welcome_title": "REMI में आपका स्वागत है",
        "chat_welcome_text": "अपने दस्तावेज़ के बारे में कुछ भी पूछें। मैं सबसे प्रासंगिक अनुभाग ढूंढूंगा और उनसे उत्तर दूंगा।",
        "question_placeholder": "अपने दस्तावेज़ के बारे में एक प्रश्न पूछें...",
        "send_button": "भेजें",
        "thinking": "REMI सोच रहा है...",
        "unsupported_file_alert": "कृपया एक समर्थित फ़ाइल अपलोड करें (.pdf, .docx, .pptx, .txt, .md)।",
        "upload_failed_prefix": "अपलोड विफल",
        "request_failed_prefix": "अनुरोध विफल",
        "error_prefix": "त्रुटि",
        # API errors
        "no_file_provided": "कोई फ़ाइल प्रदान नहीं की गई।",
        "file_empty": "अपलोड की गई फ़ाइल खाली है।",
        "unsupported_file_type": "असमर्थित फ़ाइल प्रकार: '{ext}'। समर्थित: .pdf, .docx, .pptx, .txt, .md",
        "no_extractable_text": "फ़ाइल में कोई निकाला जा सकने वाला टेक्स्ट नहीं मिला।",
        "api_key_missing": "OPENAI_API_KEY कॉन्फ़िगर नहीं है।",
        "question_empty": "प्रश्न खाली नहीं हो सकता।",
        "document_not_found": "दस्तावेज़ नहीं मिला। पहले एक फ़ाइल अपलोड करें।",
        "no_context_found": "कोई दस्तावेज़ संदर्भ नहीं मिला।",
        "llm_api_error": "LLM API त्रुटि ({status})।",
        "llm_request_failed": "LLM अनुरोध विफल: {error}",
        # LLM prompt additions
        "respond_in_language": "{language} में उत्तर दें।",
    },
    "te": {
        # UI labels
        "app_title": "REMI",
        "app_subtitle": "ఫైల్‌ను అప్‌లోడ్ చేయండి, సారాంశం పొందండి, తర్వాత అనుసరణ ప్రశ్నలు అడగండి.",
        "drop_file": "మీ ఫైల్‌ను ఇక్కడ జాపండి",
        "click_to_browse": "లేదా బ్రౌజ్ చేయడానికి ఈ ప్రాంతంలో ఎక్కడైనా క్లిక్ చేయండి",
        "supported_formats": "మద్దతు ఉన్న ఫార్మాట్‌లు: PDF, DOCX, PPTX, TXT, MD",
        "upload_reading": "చదువుతూ సారాంశం తయారు చేస్తున్నాను...",
        "new_document": "కొత్త పత్రం",
        "summary_heading": "సారాంశం",
        "pages_label": "{count} పేజీలు",
        "slides_label": "{count} స్లైడ్లు",
        "lines_label": "{count} పంక్తులు",
        "pages_unit": "పేజీలు",
        "slides_unit": "స్లైడ్లు",
        "lines_unit": "పంక్తులు",
        "truncation_warning": "పెద్ద పత్రం — REMI మొదటి {pages_read} {unit} మాత్రమే చదివింది.",
        "chat_welcome_title": "REMI కు స్వాగతం",
        "chat_welcome_text": "మీ పత్రం గురించి ఏదైనా అడగండి. నేను అత్యంత సంబంధిత విభాగాలను కనుగొని అవి నుండి సమాధానం ఇస్తాను.",
        "question_placeholder": "మీ పత్రం గురించి ఒక ప్రశ్న అడగండి...",
        "send_button": "పంపు",
        "thinking": "REMI ఆలోచిస్తోంది...",
        "unsupported_file_alert": "దయచేసి మద్దతు ఉన్న ఫైల్‌ను అప్‌లోడ్ చేయండి (.pdf, .docx, .pptx, .txt, .md).",
        "upload_failed_prefix": "అప్‌లోడ్ విఫలమైంది",
        "request_failed_prefix": "అభ్యర్థన విఫలమైంది",
        "error_prefix": "లోపం",
        # API errors
        "no_file_provided": "ఫైల్ ఇవ్వలేదు.",
        "file_empty": "అప్‌లోడ్ చేసిన ఫైల్ ఖాళీగా ఉంది.",
        "unsupported_file_type": "మద్దతు లేని ఫైల్ రకం: '{ext}'. మద్దతు ఉన్నవి: .pdf, .docx, .pptx, .txt, .md",
        "no_extractable_text": "ఫైల్‌లో నిర్ధారించగల పాఠ్యం ఏదీ కనుగొనబడలేదు.",
        "api_key_missing": "OPENAI_API_KEY కాన్ఫిగర్ చేయబడలేదు.",
        "question_empty": "ప్రశ్న ఖాళీగా ఉండకూడదు.",
        "document_not_found": "పత్రం కనుగొనబడలేదు. ముందు ఒక ఫైల్ అప్‌లోడ్ చేయండి.",
        "no_context_found": "పత్రం సందర్భం కనుగొనబడలేదు.",
        "llm_api_error": "LLM API లోపం ({status}).",
        "llm_request_failed": "LLM అభ్యర్థన విఫలమైంది: {error}",
        # LLM prompt additions
        "respond_in_language": "{language} లో సమాధానం ఇవ్వండి.",
    },
}

LANGUAGE_NAMES: dict[str, dict[str, str]] = {
    "en": {"en": "English", "hi": "Hindi", "te": "Telugu"},
    "hi": {"en": "अंग्रेज़ी", "hi": "हिन्दी", "te": "तेलुगु"},
    "te": {"en": "ఆంగ్లం", "hi": "హిందీ", "te": "తెలుగు"},
}


def get_locale(accept_language: str | None) -> str:
    """Pick the best supported locale from an Accept-Language header value.

    Examples:
        "hi-IN,hi;q=0.9,en;q=0.8" -> "hi"
        "te-IN,te;q=0.9"          -> "te"
        "fr-FR,fr;q=0.9"          -> "en" (fallback)
    """
    if not accept_language:
        return DEFAULT_LOCALE

    # Parse entries like "en-US;q=0.8" into (language, q-value).
    entries: list[tuple[str, float]] = []
    for part in accept_language.split(","):
        part = part.strip()
        if not part:
            continue
        if ";" in part:
            lang, q_str = part.split(";", 1)
            lang = lang.strip().lower()
            q_match = re.search(r"q=([0-9.]+)", q_str)
            q = float(q_match.group(1)) if q_match else 1.0
        else:
            lang = part.strip().lower()
            q = 1.0
        entries.append((lang, q))

    # Sort by quality descending; exact matches win over region variants.
    entries.sort(key=lambda x: x[1], reverse=True)

    for lang, _ in entries:
        if lang in SUPPORTED_LOCALES:
            return lang
        # Accept region variants (e.g. "hi-in" -> "hi").
        base = lang.split("-")[0]
        if base in SUPPORTED_LOCALES:
            return base

    return DEFAULT_LOCALE


def t(key: str, lang: str = DEFAULT_LOCALE, **kwargs) -> str:
    """Return the localized string for *key* in *lang*.

    Missing keys fall back to English, then return the key itself so the
    application never crashes because of a missing translation.
    """
    lang = lang if lang in SUPPORTED_LOCALES else DEFAULT_LOCALE
    text = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LOCALE]).get(
        key,
        TRANSLATIONS[DEFAULT_LOCALE].get(key, key),
    )
    return text.format(**kwargs) if kwargs else text


def get_language_name(lang: str, in_locale: str | None = None) -> str:
    """Return the human-readable name of a locale.

    Args:
        lang: The locale code to describe.
        in_locale: The locale in which to describe it. Defaults to English.
    """
    in_locale = in_locale if in_locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    return LANGUAGE_NAMES.get(in_locale, LANGUAGE_NAMES[DEFAULT_LOCALE]).get(
        lang, lang
    )
