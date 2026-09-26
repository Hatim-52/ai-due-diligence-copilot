/**
 * RAG Query Connector
 * Sends the query parameters to the FastAPI backend and retrieves the generated answer and citations.
 */
export async function executeRAGQuery(companyId, query, customDocs = [], apiKey = null) {
  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        companyId: companyId,
        query: query,
        apiKey: apiKey || null
      })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error connecting to RAG backend service:", error);
    throw new Error(`RAG backend error: ${error.message}`);
  }
}
