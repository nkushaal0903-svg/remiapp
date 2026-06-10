"""Generate a short 'About REMI' PDF."""

from fpdf import FPDF


class REMIPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(10, 132, 255)
        self.cell(0, 14, "REMI", new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "", 12)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, "Document Chatbot - Project Overview", new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        y = self.get_y()
        self.line(15, y, 195, y)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(50, 50, 50)
        self.set_x(15)
        self.multi_cell(180, 6, text)
        self.ln(4)

    def bullet(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(50, 50, 50)
        self.set_x(15)
        bullet_text = chr(149) + " " + text
        self.multi_cell(180, 6, bullet_text)


pdf = REMIPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

pdf.section_title("What is REMI?")
pdf.body_text(
    "REMI is a lightweight, intelligent document chatbot. Upload a PDF, Word document, "
    "PowerPoint, or text file and REMI instantly summarizes it and lets you ask follow-up "
    "questions in plain English."
)

pdf.section_title("What does it do?")
pdf.bullet("Ingests documents: PDF, DOCX, PPTX, TXT, and Markdown.")
pdf.bullet("Auto-generates a concise summary with key bullet points.")
pdf.bullet("Answers questions using only the content of your uploaded document.")
pdf.bullet("Handles vague follow-up questions by rewriting them into better search queries.")
pdf.bullet("Cites page and slide numbers so you can verify every answer.")
pdf.ln(2)

pdf.section_title("How it works")
pdf.body_text(
    "Instead of sending the entire document to the language model on every question, REMI uses "
    "Retrieval-Augmented Generation (RAG). The document is split into overlapping chunks, "
    "embedded with a local sentence-transformer model, and stored in memory. When you ask a "
    "question, REMI rewrites it into a standalone search query, retrieves the top 8 most "
    "relevant chunks, and passes only those to the LLM along with the conversation history."
)

pdf.section_title("Technology Stack")
pdf.bullet("Backend: Python + FastAPI")
pdf.bullet("PDF parsing: PyMuPDF (fitz)")
pdf.bullet("Office docs: python-docx, python-pptx")
pdf.bullet("Embeddings: sentence-transformers (all-MiniLM-L6-v2)")
pdf.bullet("Vector search: In-memory numpy cosine similarity")
pdf.bullet("LLM: OpenAI GPT API (default: gpt-5.4-nano)")
pdf.bullet("Frontend: Vanilla HTML, CSS, JavaScript (liquid-glass UI)")
pdf.bullet("Environment: python-dotenv for configuration")
pdf.ln(2)

pdf.section_title("Architecture Notes")
pdf.body_text(
    "Everything runs in a single, readable project with a /backend folder for the FastAPI "
    "application and a /frontend folder containing one self-contained HTML file. No build step, "
    "no framework dependencies on the frontend, and no external vector database - keeping the "
    "stack minimal and easy to run locally."
)

pdf.section_title("Configuration")
pdf.body_text(
    "Create a .env file in the project root and add your OpenAI API key:"
)
pdf.set_font("Courier", "", 10)
pdf.set_text_color(30, 30, 30)
pdf.set_fill_color(240, 240, 240)
pdf.cell(0, 8, "OPENAI_API_KEY=your_key_here", new_x="LMARGIN", new_y="NEXT", fill=True)
pdf.ln(4)

pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.set_x(15)
pdf.multi_cell(
    180,
    6,
    "Model name and base URL are also configurable via OPENAI_MODEL and OPENAI_BASE_URL.",
)

output_path = "REMI_About.pdf"
pdf.output(output_path)
print(f"Created: {output_path}")
