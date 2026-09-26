import hashlib
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import time

from pypdf import PdfReader

import os
from dotenv import load_dotenv
load_dotenv()

from backend.data import COMPANIES_DATA
from backend.rag import CUSTOM_DOCUMENTS, execute_rag_query, index_document, save_custom_documents

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="Due Diligence AI Copilot Backend")

# Serve static files from the src directory
app.mount("/src", StaticFiles(directory="src"), name="src")

# Serve the main index.html at root
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

class QueryPayload(BaseModel):
    companyId: str
    query: str
    apiKey: Optional[str] = None

@app.get("/api/companies")
async def get_companies():
    """Returns the pre-loaded dictionary of portfolio companies."""
    return COMPANIES_DATA

@app.get("/api/status")
async def get_status():
    """Returns status information, including whether a Gemini API key is configured on the server."""
    api_key = os.environ.get("GEMINI_API_KEY")
    return {
        "hasApiKey": bool(api_key and api_key.strip() and api_key != "your_api_key_here")
    }

@app.post("/api/upload")
async def upload_document(
    file: UploadFile,
    companyId: Optional[str] = Form("custom"),
    apiKey: Optional[str] = Form(None)
):
    """
    Receives document uploads (PDF, TXT, MD), saves them to disk, parses text,
    indexes into the vector store, and returns file metadata.
    """
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}

    filename = file.filename
    content_type = file.content_type
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{extension}'. Allowed: {', '.join('.' + e for e in sorted(ALLOWED_EXTENSIONS))}"
        )

    # Read with size cap to avoid OOM on huge files
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size / (1024*1024):.1f} MB). Maximum allowed size is {MAX_UPLOAD_SIZE // (1024*1024)} MB."
        )

    # Dedup check: reject re-uploads of identical content
    content_hash = hashlib.sha256(file_bytes).hexdigest()
    for existing_doc in CUSTOM_DOCUMENTS:
        if existing_doc.get("content_hash") == content_hash:
            print(f"Duplicate upload detected for '{filename}' (hash={content_hash[:12]}…), returning existing doc '{existing_doc['id']}'.")
            return {
                "id": existing_doc["id"],
                "name": existing_doc["name"],
                "size": existing_doc["size"],
                "type": existing_doc["type"],
                "companyId": existing_doc["companyId"],
                "duplicate": True
            }

    try:
        # Save uploaded file to disk
        file_path = os.path.join("uploads", filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        if extension == "pdf":
            # Run blocking PDF extraction in a thread to avoid blocking the event loop
            def _extract_pdf_text(raw_bytes):
                pdf_file = io.BytesIO(raw_bytes)
                reader = PdfReader(pdf_file)
                text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text += f"[Page {i + 1}]\n{page_text}\n\n"
                return text

            extracted_text = await run_in_threadpool(_extract_pdf_text, file_bytes)
        elif extension in ["txt", "md"]:
            # Extract plain text
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload a .pdf, .txt, or .md file."
            )
            
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the uploaded document."
            )
            
        # Register in backend document library and persist to disk
        doc_id = f"doc-{int(time.time() * 1000)}"
        doc_obj = {
            "id": doc_id,
            "name": filename,
            "content": extracted_text,
            "content_hash": content_hash,
            "companyId": companyId if companyId else "custom",
            "size": file_size,
            "type": content_type or "text/plain",
            "section": "Uploaded Document"
        }
        
        CUSTOM_DOCUMENTS.append(doc_obj)
        save_custom_documents()
        
        # Index in vector store if API key exists
        active_api_key = os.environ.get("GEMINI_API_KEY") or apiKey
        if active_api_key and active_api_key.strip():
            try:
                await index_document(
                    api_key=active_api_key,
                    doc_text=extracted_text,
                    source_name=filename,
                    company_id=companyId if companyId else "custom",
                    section_name="Uploaded Document",
                    doc_id=doc_id
                )
                print(f"Indexed upload '{filename}' into vector DB.")
            except Exception as index_err:
                print(f"Vector indexing failed on upload for '{filename}': {str(index_err)}. Will re-try on query.")
        
        # Return metadata matching the frontend state schema
        return {
            "id": doc_id,
            "name": filename,
            "size": file_size,
            "type": content_type or "text/plain",
            "companyId": companyId if companyId else "custom"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

@app.post("/api/query")
async def query_copilot(payload: QueryPayload):
    """
    Performs RAG query against filings and custom documents.
    Synthesizes response using Gemini (if key available) or simulated responses.
    """
    try:
        result = await execute_rag_query(
            company_id=payload.companyId,
            query=payload.query,
            api_key=payload.apiKey
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running RAG query: {str(e)}"
        )

if __name__ == "__main__":
    import sys
    import uvicorn
    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent
    os.chdir(root_dir)
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    port = int(os.environ.get("PORT", 8000))
    dev_mode = os.environ.get("DEV_MODE", "").lower() in ("1", "true", "yes")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=dev_mode)
