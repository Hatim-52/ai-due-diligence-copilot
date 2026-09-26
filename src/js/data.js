// Dynamic companiesData cache that is populated from the FastAPI backend
export const companiesData = {};

/**
 * Fetches company profiles and filings from the Python FastAPI server.
 * Populates companiesData dynamically.
 */
export async function fetchCompanies() {
  try {
    const response = await fetch('/api/companies');
    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }
    const data = await response.json();
    
    // Clean existing keys to prevent stale data
    Object.keys(companiesData).forEach(key => delete companiesData[key]);
    
    // Populate with backend data
    Object.assign(companiesData, data);
    return true;
  } catch (error) {
    console.error("Failed to load company filings from FastAPI backend:", error);
    return false;
  }
}
