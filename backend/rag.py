import re
import httpx
import os
import json
import math
from backend.data import COMPANIES_DATA

CUSTOM_DOCUMENTS_PATH = "./custom_documents.json"

def _load_custom_documents():
    """Load custom documents from disk on startup."""
    if os.path.exists(CUSTOM_DOCUMENTS_PATH):
        try:
            with open(CUSTOM_DOCUMENTS_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
            print(f"Loaded {len(docs)} custom document(s) from '{CUSTOM_DOCUMENTS_PATH}'.")
            return docs
        except Exception as e:
            print(f"Warning: Failed to load custom documents: {e}")
    return []

def save_custom_documents():
    """Persist the custom documents list to disk."""
    try:
        with open(CUSTOM_DOCUMENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(CUSTOM_DOCUMENTS, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save custom documents: {e}")

# Persisted store for custom uploaded documents
CUSTOM_DOCUMENTS = _load_custom_documents()

# English Stop Words
STOP_WORDS = {
    'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'was', 'were',
    'but', 'not', 'you', 'your', 'their', 'they', 'our', 'will', 'have', 'has',
    'had', 'been', 'about', 'than', 'then', 'into', 'only', 'other', 'some'
}

def cosine_similarity(v1, v2):
    """Computes cosine similarity between two numeric vectors in pure Python."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 > 0 and norm_v2 > 0:
        return dot_product / (norm_v1 * norm_v2)
    return 0.0

class MinivectorDB:
    """
    A lightweight, pure-Python persistent vector database.
    Replicates the core subset of the ChromaDB collection API:
    - upsert(ids, embeddings, metadatas, documents)
    - query(query_embeddings, n_results, where)
    - get(where, limit)
    - count()
    """
    def __init__(self, filepath="./vector_db.json"):
        self.filepath = filepath
        self.data = {}  # Schema: { id: { "vector": list[float], "metadata": dict, "document": str } }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"Loaded {len(self.data)} vector entries from '{self.filepath}'.")
            except Exception as e:
                print(f"Warning: Failed to load vector database file: {str(e)}")
                self.data = {}

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save vector database file: {str(e)}")

    def count(self):
        return len(self.data)

    def upsert(self, ids, embeddings, metadatas, documents):
        for i, doc_id in enumerate(ids):
            self.data[doc_id] = {
                "vector": embeddings[i],
                "metadata": metadatas[i],
                "document": documents[i]
            }
        self.save()

    def get(self, where=None, limit=1):
        results = {"ids": []}
        for doc_id, item in self.data.items():
            meta = item["metadata"]
            match = True
            if where:
                for k, v in where.items():
                    if meta.get(k) != v:
                        match = False
                        break
            if match:
                results["ids"].append(doc_id)
                if len(results["ids"]) >= limit:
                    break
        return results

    def query(self, query_embeddings, n_results=3, where=None):
        query_emb = query_embeddings[0]
        candidates = []
        
        for doc_id, item in self.data.items():
            meta = item["metadata"]
            
            # Filter matches
            if where:
                if "$or" in where:
                    or_match = False
                    for cond in where["$or"]:
                        cond_match = True
                        for k, v in cond.items():
                            if meta.get(k) != v:
                                cond_match = False
                                break
                        if cond_match:
                            or_match = True
                            break
                    if not or_match:
                        continue
                else:
                    match = True
                    for k, v in where.items():
                        if meta.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue
            
            # Compute cosine similarity
            sim = cosine_similarity(query_emb, item["vector"])
            candidates.append({
                "id": doc_id,
                "document": item["document"],
                "metadata": meta,
                "score": sim
            })
            
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:n_results]
        
        return {
            "documents": [[c["document"] for c in top_candidates]],
            "metadatas": [[c["metadata"] for c in top_candidates]],
            "ids": [[c["id"] for c in top_candidates]]
        }

# Instantiate the Mini vector database
collection = MinivectorDB("./vector_db.json")

def tokenize(text):
    """Clean and tokenize text into words."""
    cleaned = re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()?"\']', ' ', text.lower())
    return [word for word in cleaned.split() if len(word) > 2]

def chunk_document(document_text, source_name, company_id, section_name, chunk_size=600, overlap=150):
    """Chunks text into overlapping blocks without cutting words if possible."""
    chunks = []
    start = 0
    while start < len(document_text):
        end = min(start + chunk_size, len(document_text))
        chunk_text = document_text[start:end]
        
        # Adjust chunk boundary to not cut words
        if end < len(document_text):
            last_space = chunk_text.rfind(' ')
            if last_space > chunk_size * 0.7:
                chunk_text = chunk_text[:last_space]
                
        chunks.append({
            "text": chunk_text.strip(),
            "source": source_name,
            "companyId": company_id,
            "section": section_name,
            "startIndex": start,
            "endIndex": start + len(chunk_text)
        })
        
        start += (len(chunk_text) - overlap)
        if start >= len(document_text) or len(chunk_text) <= overlap:
            break
            
    return chunks

def retrieve_relevant_chunks(query, chunks, top_k=3):
    """Retrieve top_k relevant chunks based on keyword overlap scores."""
    query_tokens = [t for t in tokenize(query) if t not in STOP_WORDS]
    if not query_tokens:
        return chunks[:top_k]
        
    scored_chunks = []
    for chunk in chunks:
        score = 0.0
        chunk_text_lower = chunk["text"].lower()
        
        # Score based on term frequency and phrase matches
        for token in query_tokens:
            matches = len(re.findall(r'\b' + re.escape(token) + r'\b', chunk_text_lower))
            if matches > 0:
                score += matches * 1.5
            elif token in chunk_text_lower:
                score += 0.5
                
        # Phrase match bonus
        phrase = " ".join(query_tokens)
        if phrase in chunk_text_lower:
            score += 5.0
            
        scored_chunks.append((chunk, score))
        
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    highest_score = scored_chunks[0][1] if scored_chunks else 0.0
    filtered = [item[0] for item in scored_chunks if item[1] > 0 or highest_score == 0.0]
    
    return filtered[:top_k]

async def call_gemini_api(api_key, prompt, model_name=None):
    """Fetch structured response from the Gemini API."""
    if not model_name:
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        
    if response.status_code != 200:
        try:
            error_data = response.json()
            message = error_data.get("error", {}).get("message", response.reason_phrase)
        except Exception:
            message = response.reason_phrase
        raise Exception(f"Gemini API Error: {message}")
        
    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise Exception(f"Failed to parse Gemini API response structure: {str(e)}")

async def get_gemini_embeddings(api_key: str, texts: list[str], model_name: str = None) -> list[list[float]]:
    """
    Generates vector embeddings using Gemini's embedding API.
    Defaults to gemini-embedding-001 (configurable via GEMINI_EMBEDDING_MODEL).
    Sends batch embedding requests for speed.
    """
    if not texts:
        return []
    
    if not model_name:
        model_name = os.environ.get("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
        
    batch_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:batchEmbedContents?key={api_key}"
    
    requests_payload = []
    for text in texts:
        requests_payload.append({
            "model": f"models/{model_name}",
            "content": {
                "parts": [{"text": text}]
            }
        })
    
    payload = {
        "requests": requests_payload
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(batch_url, json=payload, timeout=60.0)
        
    if response.status_code != 200:
        raise Exception(f"Gemini Embedding API Error: {response.text}")
        
    data = response.json()
    embeddings = []
    for emb_data in data.get("embeddings", []):
        embeddings.append(emb_data["values"])
    return embeddings

async def index_document(api_key: str, doc_text: str, source_name: str, company_id: str, section_name: str, doc_id: str):
    """
    Chunks document text, generates vector embeddings via Gemini, and upserts them to the database.
    """
    chunks = chunk_document(doc_text, source_name, company_id, section_name)
    if not chunks:
        return
        
    texts = [c["text"] for c in chunks]
    embeddings = await get_gemini_embeddings(api_key, texts)
    
    ids = [f"{company_id}-{doc_id}-{i}" for i in range(len(chunks))]
    metadatas = []
    documents = []
    
    for chunk in chunks:
        metadatas.append({
            "source": chunk["source"],
            "companyId": chunk["companyId"],
            "section": chunk["section"] or "N/A",
            "startIndex": chunk["startIndex"],
            "endIndex": chunk["endIndex"],
            "docId": doc_id
        })
        documents.append(chunk["text"])
        
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

async def init_vector_db(api_key: str):
    """Initializes Vector DB with standard filings if it's currently empty."""
    count = collection.count()
    if count > 0:
        return
        
    print("Vector database is empty. Indexing default company filings...")
    for comp_id, comp in COMPANIES_DATA.items():
        for f in comp.get("filings", []):
            await index_document(
                api_key=api_key,
                doc_text=f["content"],
                source_name=comp["name"],
                company_id=comp_id,
                section_name=f["section"],
                doc_id=f["section"]
            )
    print(f"Successfully indexed standard filings. Total items in Vector DB: {collection.count()}")

async def sync_custom_documents_to_vector_db(api_key: str):
    """Late-indexes any custom documents that haven't been vector-indexed yet."""
    for doc in CUSTOM_DOCUMENTS:
        doc_id = doc["id"]
        res = collection.get(where={"docId": doc_id}, limit=1)
        if not res or not res.get("ids") or len(res["ids"]) == 0:
            await index_document(
                api_key=api_key,
                doc_text=doc["content"],
                source_name=doc["name"],
                company_id=doc["companyId"],
                section_name="Uploaded Document",
                doc_id=doc_id
            )
            print(f"Late-indexed custom document '{doc['name']}' in vector DB.")

def run_keyword_search_fallback(company_id, query):
    """Fallback search using tokenizer and term frequency when offline."""
    document_chunks = []
    if company_id and company_id != "custom" and company_id in COMPANIES_DATA:
        comp = COMPANIES_DATA[company_id]
        for f in comp.get("filings", []):
            chunks = chunk_document(f["content"], comp["name"], company_id, f["section"])
            document_chunks.extend(chunks)
            
    for doc in CUSTOM_DOCUMENTS:
        if not company_id or company_id == "custom" or doc.get("companyId") == company_id:
            chunks = chunk_document(
                doc["content"], 
                doc["name"], 
                doc.get("companyId") or "custom", 
                doc.get("section") or "Uploaded Segment"
            )
            document_chunks.extend(chunks)
            
    return retrieve_relevant_chunks(query, document_chunks, 3)

def generate_simulated_response(company_id, query, retrieved_chunks):
    """Simulated offline LLM responses for demonstration when no API key is active."""
    query_lower = query.lower()
    company = COMPANIES_DATA.get(company_id, {"name": "Uploaded Document"})
    
    if company_id == "custom" or company_id not in COMPANIES_DATA:
        synthesis = f"Based on the uploaded document **{retrieved_chunks[0]['source'] if retrieved_chunks else 'Custom Document'}**, here is what I found regarding your query:\n\n"
        for index, chunk in enumerate(retrieved_chunks):
            synthesis += f"* **From {chunk.get('section') or f'Extract {index + 1}'}**: {chunk['text'][:180]}...\n"
        synthesis += f"\n*(Note: To get complete dynamic answers that analyze the full text contextually, please enter your Gemini API Key in the settings panel or configure it on the server.)*"
        return {
            "answer": synthesis,
            "citations": retrieved_chunks
        }
        
    answer = ""
    if company_id == "acme":
        if any(w in query_lower for w in ["lawsuit", "sue", "sentinel", "legal", "court"]):
            answer = """### Acme SaaS Legal Risk: Patent Infringement Lawsuit

Acme SaaS Corporation is currently facing a **critical legal risk** regarding a patent infringement lawsuit filed by **Sentinel Technologies** on August 14, 2025, in the U.S. District Court for the District of Delaware. 

**Key Details:**
* **Allegation:** Sentinel claims that Acme's database synchronization and caching layer violates US Patents 8,421,902 and 9,102,442 [Acme SaaS Corporation - Section: Legal Proceedings & Contingencies].
* **Damages Sought:** Sentinel is seeking **$45.0 million** in damages for past infringement, as well as a **permanent injunction** against Acme's primary ERP platform [Acme SaaS Corporation - Section: Legal Proceedings & Contingencies].
* **Current Status:** The trial is scheduled for **early 2027**, and discovery is ongoing. Acme has engaged specialized counsel to defend the lawsuit [Acme SaaS Corporation - Section: Legal Proceedings & Contingencies].

**Impact on Business:**
If Acme loses this lawsuit, it could result in:
1. Crippling financial damages ($45M exceeds their current total cash reserves of $38M) [Acme SaaS Corporation - Section: Liquidity and Capital Resources].
2. An injunction that could prevent Acme from selling or operating its core ERP platform, threatening their entire subscription revenue stream."""
        elif any(w in query_lower for w in ["debt", "refinance", "cash", "liquidity", "going concern"]):
            answer = """### Acme SaaS Financial Risk: Debt Wall & Liquidity

Acme SaaS Corporation faces severe capital constraints and a major debt wall maturing in **October 2026**.

**Key Metrics & Risks:**
* **Total Debt:** The company has **$120.0 million** in outstanding debt, represented by Senior Secured Notes bearing interest at **8.5%** per annum [Acme SaaS Corporation - Section: Liquidity and Capital Resources].
* **Maturity Date:** The full principal is due on **October 15, 2026** [Acme SaaS Corporation - Section: Liquidity and Capital Resources].
* **Cash Position:** Acme's cash reserves declined to **$38.0 million** as of December 31, 2025, from $52.0 million in 2024, driven by a negative Free Cash Flow of **$14.0 million** [Acme SaaS Corporation - Section: Financial Performance & MD&A].
* **Refinancing Risk:** The company is currently discussing refinancing with investment banks. If credit markets tighten, refinancing might fail, raising "substantial doubt about our ability to continue as a going concern" [Acme SaaS Corporation - Section: Liquidity and Capital Resources]."""
        elif any(w in query_lower for w in ["growth", "revenue", "margins", "performance"]):
            answer = """### Acme SaaS Financial Performance Summary

Acme has demonstrated impressive top-line growth, but is operating with high costs that drag down bottom-line margins.

**Key Points:**
* **Revenue Growth:** FY 2025 revenue reached **$91.0 million**, representing a **42% increase** YoY, driven by strong core ERP adoption and a **118% Net Revenue Retention (NRR)** [Acme SaaS Corporation - Section: Financial Performance & MD&A].
* **Operating Loss:** Despite high sales, operating expenses rose 38% to $96.5 million, resulting in a **Net Loss of $5.5 million** [Acme SaaS Corporation - Section: Financial Performance & MD&A].
* **Margin Compression:** Cloud hosting fees (AWS database compute and transit) increased by 25%, causing gross subscription margins to compress from **78% in 2024 to 74% in 2025** [Acme SaaS Corporation - Section: Operational Risks & Cloud Hosting].
* **Customer Acquisition Cost**: Sales and marketing costs stand at **$42.0 million** (approx. 46% of total revenue) due to rep headcount growth and high commissions [Acme SaaS Corporation - Section: Financial Performance & MD&A]."""
            
    elif company_id == "solaris":
        if any(w in query_lower for w in ["grid", "connect", "interconnect", "transmission", "ercot", "caiso"]):
            answer = """### Solaris Energy: Grid Interconnection Backlog

Solaris Energy Partners' operational timeline is heavily constrained by regional electric transmission grids.

**Key Issues:**
* **Study & Connection Delays:** Queue times to secure final interconnection study approvals and physical grid linkups average **18 months** (specifically within ERCOT in Texas and CAISO in California) [Solaris Energy Partners - Section: Grid Integration & Transmission Constraints].
* **PPA Penalties:** Under their signed Power Purchase Agreements (PPAs), failure to deliver electricity by scheduled commercial operation dates triggers strict daily penalties ranging from **$15,000 to $50,000 per day** [Solaris Energy Partners - Section: Grid Integration & Transmission Constraints].
* **Asset Idle Risk:** Completed solar installations cannot generate revenue while waiting in connection queues, locking up valuable capital [Solaris Energy Partners - Section: Grid Integration & Transmission Constraints]."""
        elif any(w in query_lower for w in ["subsidy", "tax", "policy", "itc", "ptc", "government"]):
            answer = """### Solaris Energy: Regulatory & Subsidy Dependencies

Solaris Energy Partners' project profitability depends heavily on federal climate policies.

**Key Subsidies:**
* **Tax Credits:** The business relies on the **Federal Investment Tax Credit (ITC)** (claiming 30% of installation costs) and the **Production Tax Credit (PTC)** based on power generated [Solaris Energy Partners - Section: Regulatory Environment & Tax Subsidies].
* **Policy Risk:** Political administration shifts or reforms that reduce or sunset these tax benefits present a major risk.
* **Financial Impact:** Eliminating these subsidies would drop expected Project Internal Rates of Return (IRRs) from **9% to under 5%**, rendering future projects completely uneconomical [Solaris Energy Partners - Section: Regulatory Environment & Tax Subsidies]."""
        elif any(w in query_lower for w in ["debt", "bond", "leverage", "capex", "financial"]):
            answer = """### Solaris Energy: Financial Position & CapEx

Solaris is highly leveraged due to the intensive capital required to construct utility-scale solar farms.

**Financial Status:**
* **Total Debt:** Reached **$350.0 million** as of Dec 31, 2025, driven by a **$90.0 million Green Bond** issue in 2025 [Solaris Energy Partners - Section: Capital Expenditures & Financing].
* **Leverage Ratio:** The company's **Debt-to-Equity ratio stands at 2.1**, which may limit their capacity to secure future project-level construction loans [Solaris Energy Partners - Section: Capital Expenditures & Financing].
* **Cash Flow Constraint:** Operational cash flow was $55.0 million, but distribution payouts to unitholders consumed $38.0 million, leaving cash reserves tight at **$22.0 million** [Solaris Energy Partners - Section: Capital Expenditures & Financing].
* **CapEx:** Upfront Capital Expenditures totaled **$142.0 million** in 2025 [Solaris Energy Partners - Section: Capital Expenditures & Financing]."""
            
    elif company_id == "biohealth":
        if any(w in query_lower for w in ["side effect", "cardiovax", "trial", "clinical", "fda", "nausea"]):
            answer = """### BioHealth Labs: CardioVax Phase III Safety & FDA Risks

BioHealth Labs' primary drug candidate, **CardioVax-200**, is showing mixed clinical results that could block regulatory approval.

**Clinical Observations:**
* **Efficacy (Positive):** CardioVax-200 met statistical significance in Phase III trials (450 patients), demonstrating a **22% improvement in Left Ventricular Ejection Fraction (LVEF)** [BioHealth Labs Inc. - Section: Clinical Development & CardioVax Trials].
* **Safety Signals (Negative):** Approximately **12.4% of patients** in the treatment group experienced moderate-to-severe adverse events, including transient sinus tachycardia (heart rate spikes) and severe nausea [BioHealth Labs Inc. - Section: Clinical Development & CardioVax Trials].
* **Regulatory Impact:** These safety side effects could lead the FDA to demand a longer monitoring period, require a larger trial database, or issue a Complete Response Letter (CRL), delaying market launch by **12 to 24 months** [BioHealth Labs Inc. - Section: Clinical Development & CardioVax Trials]."""
        elif any(w in query_lower for w in ["runway", "cash", "burn", "finance", "survive"]):
            answer = """### BioHealth Labs: Cash Runway & Financial Burn

BioHealth Labs is a clinical-stage company with no active revenues and a high burn rate.

**Financial Health:**
* **Revenue:** **$0.0** (standard for clinical-stage biotechnology) [BioHealth Labs Inc. - Section: Overview & Clinical Pipeline].
* **Operating Loss:** Net Loss rose to **$38.4 million** in FY 2025 due to research development and clinical site fees [BioHealth Labs Inc. - Section: Capital Runway & R&D Burn].
* **Cash Position:** The company holds **$45.0 million** in cash [BioHealth Labs Inc. - Section: Capital Runway & R&D Burn].
* **Monthly Burn Rate:** Net cash burn stands at **$3.2 million per month** [BioHealth Labs Inc. - Section: Capital Runway & R&D Burn].
* **Runway:** The cash reserves will only fund operations for **14 months** (exhausted by February 2027), necessitating dilutive equity financing before BLA submission [BioHealth Labs Inc. - Section: Capital Runway & R&D Burn]."""
        elif any(w in query_lower for w in ["patent", "oncology", "expire", "ip", "generic"]):
            answer = """### BioHealth Labs: Patent Expiration & Intellectual Property Risk

While BioHealth has secured IP for its main candidate CardioVax through 2039, its secondary platform faces generic threats.

**IP Details:**
* **Oncology Patent Expirations:** The secondary oncology drug delivery platform relies on US Patents 7,902,411 and 8,011,202, which are scheduled to expire in **June and August 2028** respectively [BioHealth Labs Inc. - Section: Intellectual Property & Patents].
* **Market Exposure:** Upon expiration, generic drug manufacturers can introduce bio-similar versions, erode BioHealth's oncology pricing power and market share [BioHealth Labs Inc. - Section: Intellectual Property & Patents]."""

    if not answer:
        primary_source = retrieved_chunks[0] if retrieved_chunks else None
        source_name = (primary_source["section"] or primary_source["source"]) if primary_source else company.get("name", "Unknown File")
        context_snippets = "\n\n* ".join([f"{c['text'][:180]}..." for c in retrieved_chunks])
        
        answer = f"""### Analysis of {company.get('name', 'Uploaded Filings')}

Based on the retrieved filings regarding *"{query}"*, here is an executive summary of the relevant disclosures:

1. **Retrieved Findings**: The filings disclose key details regarding this topic, particularly in **{source_name}**. 
2. **Context Summary**: 
* {context_snippets}
3. **Implications**: The active disclosure suggests key operational or financial considerations that require close due diligence review.

*Tip: For a fully context-aware dynamic response synthesized by a live model, enter your Gemini API Key in the settings panel or configure it on the server.*"""

    return {
        "answer": answer,
        "citations": retrieved_chunks
    }

async def execute_rag_query(company_id, query, api_key=None):
    """Orchestrates document retrieval (Vector Database vs Fallback Keyword) and prompts Gemini."""
    active_api_key = os.environ.get("GEMINI_API_KEY") or api_key
    
    # Check if we can run Live Vector Search with our database
    if active_api_key and active_api_key.strip():
        try:
            # Ensure standard filings are indexed
            await init_vector_db(active_api_key)
            # Ensure all custom uploaded docs are indexed
            await sync_custom_documents_to_vector_db(active_api_key)
            
            # 1. Embed query
            query_embeddings = await get_gemini_embeddings(active_api_key, [query])
            if not query_embeddings:
                raise Exception("Query embedding generation returned empty.")
            query_emb = query_embeddings[0]
            
            # 2. Setup meta filter scope
            where_filter = {}
            if company_id == "custom":
                where_filter = {"companyId": "custom"}
            elif company_id:
                where_filter = {
                    "$or": [
                        {"companyId": company_id},
                        {"companyId": "custom"}
                    ]
                }
                
            # 3. Query Vector Database
            results = collection.query(
                query_embeddings=[query_emb],
                n_results=3,
                where=where_filter
            )
            
            # 4. Map results to unified output structure
            retrieved_chunks = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                for i in range(len(docs)):
                    m = metas[i]
                    retrieved_chunks.append({
                        "text": docs[i],
                        "source": m["source"],
                        "companyId": m["companyId"],
                        "section": m["section"]
                    })
                    
            if not retrieved_chunks:
                # Genuine "nothing relevant" — don't degrade to keyword search
                company = COMPANIES_DATA.get(company_id, {})
                company_name = company.get("name", "the selected source")
                return {
                    "answer": (
                        f"### No Relevant Filings Found\n\n"
                        f"The vector search completed successfully but found **no filings or documents** "
                        f"relevant to your query *\"{query}\"* for **{company_name}**.\n\n"
                        f"**Suggestions:**\n"
                        f"- Try rephrasing your question with different keywords.\n"
                        f"- Upload additional documents that may contain the information you're looking for.\n"
                        f"- Broaden your query scope (e.g., ask about general risks instead of a specific metric)."
                    ),
                    "citations": []
                }
                
            # 5. Formulate prompt context
            context_text = "\n\n".join([
                f"[Document: {chunk['source']} | Section: {chunk['section'] or 'N/A'}]\n{chunk['text']}"
                for chunk in retrieved_chunks
            ])
            
            system_prompt = (
                "You are an expert financial analyst performing due diligence.\n"
                "Analyze the provided document extracts and answer the user's question.\n"
                "Your response should be professional, data-driven, and highlight any financial, legal, or operational risks.\n"
                "You MUST cite your sources directly inside the text using bracketed format, matching the exact source and section name from the document headers, e.g. [Company Name - Section Name].\n"
                "If the retrieved documents do not contain the answer, politely state that the information is not present in the current filings.\n"
                "Only use facts directly mentioned in the text. Do not make up information."
            )
            
            full_prompt = f"{system_prompt}\n\n=== RETRIEVED DOCS ===\n{context_text}\n\n=== USER QUESTION ===\n{query}\n\n=== YOUR DETAILED RESPONSE ==="
            
            answer_text = await call_gemini_api(active_api_key, full_prompt)
            return {
                "answer": answer_text,
                "citations": retrieved_chunks
            }
        except Exception as error:
            print("Vector database query failed, falling back to keyword search:", error)
            retrieved_chunks = run_keyword_search_fallback(company_id, query)
            fallback = generate_simulated_response(company_id, query, retrieved_chunks)
            fallback["answer"] = f"> [!WARNING]\n> **Vector RAG Error**: {str(error)}. Falling back to local/simulated keyword analysis.\n\n" + fallback["answer"]
            return fallback
    else:
        # Offline mode / Fallback keyword search
        retrieved_chunks = run_keyword_search_fallback(company_id, query)
        return generate_simulated_response(company_id, query, retrieved_chunks)
