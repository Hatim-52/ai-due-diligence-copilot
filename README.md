# AI Due Diligence Copilot

> **An AI-powered research and analysis workspace for evaluating companies, financial risks, filings, and uploaded documents using Retrieval-Augmented Generation (RAG).**

The **AI Due Diligence Copilot** is a full-stack application designed to help investment analysts, researchers, and deal teams quickly investigate portfolio companies and extract relevant information from financial and business documents.

Instead of manually searching through lengthy filings and reports, users can select a company, explore financial and risk metrics, upload their own documents, and ask natural-language questions. The system retrieves relevant document sections and uses **Google Gemini** to generate grounded responses with source context.

---

## ✨ Features

### 🏢 Portfolio Company Analysis

Explore preloaded due-diligence information for multiple companies across different industries:

* SaaS
* CleanTech / Energy
* HealthTech / Biotechnology
* Financial and operational metrics
* Company summaries
* Key business risks
* Source references

### 📊 Financial & Risk Dashboard

Each company includes an interactive dashboard for quickly reviewing:

* Revenue trends
* Leverage metrics
* Financial performance
* Critical, high, and medium-risk categories
* Operational risks
* Liquidity and financing concerns
* Source references for identified risks

### 🤖 AI Due Diligence Chat

Ask natural-language questions about a company's filings and receive AI-generated answers.

Example questions:

```text
What are the major financial risks?

When does the company's debt mature?

What is causing the margin compression?

What are the major legal risks?

How dependent is the company on government incentives?
```

The application retrieves relevant document chunks before generating the response, helping keep answers grounded in the available source material.

### 📄 Custom Document Upload

Upload your own due-diligence material and query it through the same RAG interface.

Supported formats:

* `.pdf`
* `.txt`
* `.md`

Uploaded documents are:

1. Parsed
2. Split into overlapping chunks
3. Embedded using Gemini
4. Stored in the local vector database
5. Made available for semantic retrieval

### 🔎 Retrieval-Augmented Generation

The RAG pipeline combines document retrieval with LLM generation.

**Retrieval flow:**

```text
User Question
      ↓
Query Embedding
      ↓
Vector Similarity Search
      ↓
Relevant Document Chunks
      ↓
Context Construction
      ↓
Google Gemini
      ↓
Grounded Response + Sources
```

The application also provides a keyword-based retrieval fallback when the Gemini API is unavailable.

### 📚 Source-Aware Responses

Retrieved document sections are attached to generated responses so users can understand where the information came from.

This is particularly useful for due-diligence workflows where conclusions should be traceable back to the underlying documents.

### 📴 Offline / Demo Mode

The application can still operate without an active Gemini API key.

In offline mode, the system uses:

* Local document retrieval
* Keyword matching
* Predefined company analysis responses
* Uploaded document excerpts

This makes the project easier to demonstrate and develop without requiring an API call for every interaction.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────────┐
                         │      User / Analyst     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Web Dashboard       │
                         │ HTML + CSS + JavaScript │
                         │        + Vite           │
                         └────────────┬────────────┘
                                      │
                              REST API Requests
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      FastAPI Backend     │
                         │                          │
                         │ • Company Data           │
                         │ • File Upload            │
                         │ • Query Processing       │
                         │ • RAG Pipeline            │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                ┌─────────────────┐       ┌──────────────────┐
                │ Document Parser │       │   RAG Engine     │
                │     pypdf       │       │                  │
                └────────┬────────┘       │ • Chunking       │
                         │                │ • Embeddings     │
                         ▼                │ • Retrieval      │
                ┌─────────────────┐       │ • Context        │
                │ Document Chunks │──────►│ • Generation     │
                └─────────────────┘       └────────┬─────────┘
                                                   │
                                      ┌────────────┴───────────┐
                                      │                        │
                                      ▼                        ▼
                              ┌───────────────┐        ┌───────────────┐
                              │ Gemini API    │        │ Local Vector  │
                              │               │        │ Database      │
                              │ • Embeddings  │        │               │
                              │ • Generation  │        │ JSON Storage  │
                              └───────────────┘        └───────────────┘
```

---

# 🧠 RAG Pipeline

The project's retrieval pipeline follows these stages:

### 1. Document Ingestion

Uploaded PDFs, Markdown, and text files are parsed and converted into plain text.

### 2. Chunking

Documents are divided into overlapping chunks to make retrieval more precise while preserving surrounding context.

```text
Document
   │
   ├── Chunk 1
   ├── Chunk 2
   ├── Chunk 3
   ├── Chunk 4
   └── ...
```

### 3. Embedding Generation

Each chunk is converted into a numerical vector using:

```text
gemini-embedding-001
```

### 4. Vector Storage

Embeddings and metadata are persisted locally in:

```text
vector_db.json
```

Stored metadata includes information such as:

* Source document
* Company ID
* Section
* Document ID
* Chunk position

### 5. Query Retrieval

When a user asks a question:

```text
Question
   ↓
Gemini Embedding
   ↓
Cosine Similarity
   ↓
Top Relevant Chunks
```

The system retrieves the most relevant chunks from the selected company or uploaded document collection.

### 6. Response Generation

The retrieved context is passed to Gemini along with the user's question.

```text
Retrieved Context + User Question
                ↓
          Gemini 2.5 Flash
                ↓
        Grounded AI Response
```

---

# 🖥️ Application Modules

The interface is divided into four main areas.

### Dashboard

Provides an overview of the selected company, including financial information and visualizations.

### Risk Analysis

Displays categorized risks with severity levels and source references.

### AI Chat Copilot

Provides natural-language interaction with the company's indexed information.

### Document Manager

Allows users to upload and manage custom documents for RAG-based analysis.

---

# 🛠️ Tech Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* JavaScript ES Modules
* Vite
* Chart.js

## Backend

* Python 3.10+
* FastAPI
* Uvicorn
* HTTPX
* pypdf
* python-dotenv
* python-multipart

## AI

* Google Gemini API
* `gemini-2.5-flash` — response generation
* `gemini-embedding-001` — document/query embeddings

## Retrieval & Storage

* Vector embeddings
* Cosine similarity
* Keyword-based fallback retrieval
* Local JSON-based vector database
* Document metadata

---

# 📁 Project Structure

```text
ai-due-diligence-copilot/
│
├── backend/
│   ├── data.py
│   ├── main.py
│   ├── rag.py
│   └── requirements.txt
│
├── src/
│   ├── assets/
│   │   └── editorial_bg.jpg
│   │
│   ├── js/
│   │   ├── app.js
│   │   ├── charts.js
│   │   ├── data.js
│   │   └── rag.js
│   │
│   └── styles/
│       └── main.css
│
├── uploads/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── index.html
├── main.py
├── package.json
└── README.md
```

---

# ⚙️ Getting Started

## Prerequisites

Make sure you have the following installed:

* Python 3.10+
* Node.js 18+
* npm
* Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-due-diligence-copilot.git
cd ai-due-diligence-copilot
```

---

## 2. Create a Python Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Install Frontend Dependencies

```bash
npm install
```

---

# 🔐 Environment Configuration

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

On Windows, you can also create the file manually.

Add your Gemini configuration:

```env
GEMINI_API_KEY=your_api_key_here

GEMINI_MODEL=gemini-2.5-flash

GEMINI_EMBEDDING_MODEL=gemini-embedding-001

PORT=8000
```

> **Security:** Never commit your real `.env` file or API key to GitHub.

---

# ▶️ Running the Application

## Recommended: Full-Stack Mode

From the project root:

```bash
python main.py
```

The application will start at:

```text
http://localhost:8000
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

---

## Frontend Development Mode

For frontend development with Vite:

```bash
npm run dev
```

This provides Vite's development server and hot reload functionality.

---

# 🔌 API Endpoints

The FastAPI backend exposes the following core endpoints:

| Endpoint         | Method | Purpose                               |
| ---------------- | ------ | ------------------------------------- |
| `/api/companies` | GET    | Retrieve portfolio company data       |
| `/api/status`    | GET    | Check Gemini/API status               |
| `/api/upload`    | POST   | Upload and index documents            |
| `/api/query`     | POST   | Execute RAG queries                   |
| `/docs`          | GET    | Interactive FastAPI API documentation |

---

# 📄 Supported Documents

Custom documents can be uploaded in:

| Format   | Supported |
| -------- | --------- |
| PDF      | ✅         |
| TXT      | ✅         |
| Markdown | ✅         |

Uploaded files are parsed, chunked, embedded, and indexed for retrieval.

The current backend enforces a **20 MB maximum upload size**.

---

# 🔄 Example Workflow

A typical analyst workflow looks like this:

```text
1. Select a portfolio company
             ↓
2. Review company dashboard
             ↓
3. Inspect financial & operational risks
             ↓
4. Open source references
             ↓
5. Upload additional documents
             ↓
6. Documents are parsed & indexed
             ↓
7. Ask questions in AI Chat
             ↓
8. Retrieve relevant evidence
             ↓
9. Generate AI-assisted analysis
```

---

# 💡 Example Use Cases

### Investment Research

Quickly investigate:

* Revenue performance
* Debt maturity
* Liquidity
* Operating losses
* Customer concentration
* Capital expenditure
* Financing requirements

### Risk Assessment

Identify and investigate:

* Legal risks
* Regulatory dependencies
* Operational constraints
* Supply-chain risks
* Technology dependencies
* Financing risks

### Document Analysis

Upload:

```text
10-K filings
Investor presentations
Financial reports
Due diligence reports
Management presentations
Research documents
```

and query them using natural language.

---

# 🎯 Why This Project?

Traditional due-diligence workflows often require analysts to manually search through large amounts of unstructured information.

The goal of this project is to demonstrate how **RAG, embeddings, document processing, and LLMs** can be combined into a practical research workflow.

The project focuses on:

* Grounded AI responses
* Document-level retrieval
* Source-aware analysis
* Financial risk exploration
* Custom document ingestion
* Local persistence
* AI-assisted research

---

# 🚧 Current Limitations

This project is intended as a technical demonstration and is not a replacement for professional investment, legal, financial, or compliance review.

Current limitations include:

* Local JSON vector storage rather than a production vector database
* Limited document formats
* Retrieval quality depends on document quality and embedding performance
* Gemini API is required for full generative RAG functionality
* Offline mode provides limited simulated analysis
* No authentication or multi-user access control
* No production-grade document access isolation
* Financial information in the demonstration dataset is illustrative

---

# 🚀 Future Improvements

Potential improvements include:

* [ ] Replace JSON vector storage with ChromaDB, Qdrant, or pgvector
* [ ] Add hybrid BM25 + vector retrieval
* [ ] Add reranking for retrieved chunks
* [ ] Add document-level permissions
* [ ] Add user authentication
* [ ] Add persistent chat sessions
* [ ] Add RAG evaluation metrics
* [ ] Add retrieval precision/recall evaluation
* [ ] Add automated due-diligence report generation
* [ ] Add Excel/CSV financial analysis
* [ ] Add more document formats
* [ ] Add structured financial statement extraction
* [ ] Add deployment configuration
* [ ] Add automated testing and CI/CD

---

# 🧪 Development

Run the frontend build:

```bash
npm run build
```

Preview the production frontend:

```bash
npm run preview
```

Run the backend:

```bash
python main.py
```

---

# 🔒 Security Notes

API keys should be stored in environment variables rather than committed to source control.

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
venv/
__pycache__/
vector_db.json
uploads/*
```

Only commit:

```text
.env.example
```

with placeholder values.

---

# 📌 Project Highlights

This project demonstrates practical implementation of:

```text
Full-Stack Development
        +
FastAPI
        +
Document Processing
        +
Vector Embeddings
        +
Semantic Retrieval
        +
RAG
        +
LLM Integration
        +
Data Visualization
        +
AI-Assisted Research
```

It is designed as a portfolio project demonstrating how modern AI systems can be integrated into a realistic business-analysis workflow.

---

# 📜 License

This project is licensed under the **MIT License**.

---

## ⭐ If you find this project useful

Feel free to star the repository and explore the implementation.
