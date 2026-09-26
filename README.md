# AI Due Diligence Copilot

An AI-powered Due Diligence Copilot designed to assist investment analysts and deal teams in analyzing portfolio companies, cross-referencing financials, extracting insights from uploaded pitch decks/PDFs, and conducting grounded Q&A with retrieval-augmented generation (RAG).

---

## Features

- **Portfolio Company Analysis**: Preloaded due diligence datasets across SaaS, FinTech, CleanTech, and HealthTech metrics.
- **Document Ingestion & Parsing**: Upload custom PDFs, markdown, or text files with automatic text extraction and chunking.
- **Dual RAG Engine**:
  - **Vector Semantic Search**: Embedding generation via Google Gemini Embeddings API (`gemini-embedding-001`).
  - **BM25 Lexical Keyword Search**: Fallback and hybrid scoring for exact matches and domain acronyms.
- **Synthesis & Due Diligence Reporting**: Grounded generation powered by Google Gemini (`gemini-2.5-flash`).
- **Interactive Visualizations**: Financial charts, runway projections, and risk metric tracking.

---

## Tech Stack

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [httpx](https://www.python-httpx.org/), [pypdf](https://pypdf.readthedocs.io/)
- **Frontend**: Vanilla JS (ES Modules), HTML5, CSS3, [Vite](https://vitejs.dev/)
- **AI / Embeddings**: Google Gemini API (`gemini-2.5-flash` / `gemini-embedding-001`)

---

## Getting Started

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ (optional, for Vite frontend development)
- A Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/))

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd ai-due-diligence-copilot
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Install Node dependencies** (optional, for frontend dev):
   ```bash
   npm install
   ```

### 3. Environment Configuration

Copy the example environment file and add your Google Gemini API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
PORT=8000
```

> **Note**: You can also enter your Gemini API Key directly in the frontend UI settings if you prefer not to store it in `.env`.

---

## Running the Application

### Option A: Full-Stack via Python (Recommended)

Run the unified server (serves both API and frontend UI):

```bash
python main.py
```

- **Application URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Frontend Dev Mode (Vite)

If developing frontend components with hot reloading:

```bash
npm run dev
```

---

## Project Structure

```text
├── backend/
│   ├── data.py              # Mock portfolio company due diligence dataset
│   ├── main.py              # FastAPI endpoints (upload, query, status, static)
│   ├── rag.py               # Vector store, chunking, BM25, and Gemini API integration
│   └── requirements.txt     # Python dependencies
├── src/
│   ├── css/                 # Stylesheets & themes
│   └── js/                  # Frontend UI, charts, and RAG client logic
├── uploads/                 # Storage directory for uploaded documents (.gitkeep tracked)
├── .env.example             # Template for environment variables
├── .gitignore               # Ignored environments, uploads, and caches
├── index.html               # Main dashboard UI
├── main.py                  # Server runner and launcher
└── package.json             # Frontend dev dependencies (Vite)
```

---

## License

MIT License.
