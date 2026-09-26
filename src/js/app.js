import { companiesData, fetchCompanies } from './data.js';
import { executeRAGQuery } from './rag.js';
import { renderFinancialCharts, destroyCharts } from './charts.js';

// Application State
const state = {
  currentCompanyId: 'acme',
  currentTab: 'chat',
  customDocuments: [], // Array of { id, name, content, companyId, size, type }
  apiKey: localStorage.getItem('gemini_api_key') || '',
  serverHasApiKey: false, // Tracks if server has key configured via .env
  chatHistories: {
    acme: [],
    solaris: [],
    biohealth: [],
    custom: []
  }
};

// DOM Elements Cache
const elements = {
  companySelect: document.getElementById('company-select-dropdown'),
  companyBadge: document.getElementById('active-company-badge'),
  companyName: document.getElementById('active-company-name'),
  apiStatusDot: document.getElementById('api-status-dot'),
  apiStatusText: document.getElementById('api-status-text'),
  
  // Sidebar Tabs
  tabs: {
    dashboard: document.getElementById('nav-tab-dashboard'),
    risks: document.getElementById('nav-tab-risks'),
    chat: document.getElementById('nav-tab-chat'),
    documents: document.getElementById('nav-tab-documents')
  },
  panels: {
    dashboard: document.getElementById('panel-dashboard'),
    risks: document.getElementById('panel-risks'),
    chat: document.getElementById('panel-chat'),
    documents: document.getElementById('panel-documents')
  },

  // Dashboard Tab Elements
  dashboardIndustry: document.getElementById('dashboard-company-industry'),
  dashboardSummary: document.getElementById('dashboard-company-summary'),
  
  // Risks Tab Elements
  riskCountCritical: document.getElementById('risk-count-critical'),
  riskCountHigh: document.getElementById('risk-count-high'),
  riskCountMedium: document.getElementById('risk-count-medium'),
  riskTableBody: document.getElementById('risk-table-body'),

  // Chat Tab Elements
  chatHistory: document.getElementById('chat-history-container'),
  chatSuggestions: document.getElementById('chat-suggestions-container'),
  chatInput: document.getElementById('chat-user-input'),
  chatSendBtn: document.getElementById('chat-send-button'),

  // Documents Tab Elements
  dragDropZone: document.getElementById('drag-drop-zone'),
  fileInput: document.getElementById('hidden-file-input'),
  documentList: document.getElementById('document-library-list'),

  // Drawer Elements
  drawerOverlay: document.getElementById('citation-drawer-overlay'),
  drawerClose: document.getElementById('citation-drawer-close'),
  drawerCompany: document.getElementById('drawer-company-name'),
  drawerSection: document.getElementById('citation-drawer-section'),
  drawerBody: document.getElementById('citation-drawer-body'),

  // Settings Modal Elements
  settingsBtn: document.getElementById('settings-btn-sidebar'),
  modalOverlay: document.getElementById('settings-modal-overlay'),
  modalClose: document.getElementById('settings-modal-close'),
  apiKeyInput: document.getElementById('gemini-api-key-input'),
  settingsCancel: document.getElementById('settings-cancel-btn'),
  settingsSave: document.getElementById('settings-save-btn')
};

// Initial welcome messages for chatbot
const WELCOME_MESSAGES = {
  acme: "Hi! I am your AI Due Diligence Copilot for **Acme SaaS Corporation**. I have ingested their complete 2025 10-K filings. Ask me about their high **AWS dependency**, their pending **Sentinel patent lawsuit**, or their **$120M debt wall maturity**.",
  solaris: "Hi! I am your AI Due Diligence Copilot for **Solaris Energy Partners**. I have fully parsed their utility-scale portfolio reports. Ask me about the **18-month grid interconnection backlog**, **federal tax credits dependency**, or their **high debt leverage**.",
  biohealth: "Hi! I am your AI Due Diligence Copilot for **BioHealth Labs Inc.** I've indexed their clinical trials and patent reports. Ask me about **CardioVax Phase III side effects**, their **14-month cash burn runway**, or their **2028 patent expirations**.",
  custom: "Welcome! This is your **Custom RAG Knowledge Index**. Please upload documents (.pdf or .txt) in the **Document Manager** tab first, then ask me questions about their contents here."
};

// Suggestion Prompts by company
const SUGGESTION_PROMPTS = {
  acme: [
    "What are the details of the Sentinel lawsuit?",
    "When does Acme's debt mature and what is the rate?",
    "Show me the operating loss for FY 2025."
  ],
  solaris: [
    "What is the grid interconnection backlog?",
    "How dependent is Solaris on tax credits?",
    "What is their debt-to-equity ratio?"
  ],
  biohealth: [
    "What were the safety signals in Phase III trials?",
    "How long is BioHealth's cash runway?",
    "Which patents expire in 2028?"
  ],
  custom: [
    "Summarize the key risks in my uploaded file.",
    "List the financial metrics found in the document."
  ]
};

/* ==========================================================================
   STATE MANAGERS & SYNCHRONIZERS
   ========================================================================== */

async function initApp() {
  // Load company profiles & filings from Python FastAPI backend
  await fetchCompanies();
  
  // Check if backend has Gemini API key configured
  try {
    const res = await fetch('/api/status');
    if (res.ok) {
      const statusData = await res.json();
      state.serverHasApiKey = statusData.hasApiKey;
    }
  } catch (err) {
    console.warn("Could not fetch backend status:", err);
  }
  
  updateAPIIndicator();
  setupEventListeners();
  
  // Set initial screen
  switchCompany(state.currentCompanyId);
  switchTab(state.currentTab);
}

// Update the top-right header API Status
function updateAPIIndicator() {
  const isLive = (state.apiKey && state.apiKey.trim() !== '') || state.serverHasApiKey;
  if (isLive) {
    elements.apiStatusDot.classList.add('active');
    elements.apiStatusText.textContent = "Gemini Live RAG Enabled";
  } else {
    elements.apiStatusDot.classList.remove('active');
    elements.apiStatusText.textContent = "Gemini Offline Mode";
  }
}

// Swiping tabs
function switchTab(tabId) {
  state.currentTab = tabId;
  
  // Update nav item highlights
  Object.keys(elements.tabs).forEach(id => {
    if (id === tabId) {
      elements.tabs[id].classList.add('active');
      elements.panels[id].classList.add('active');
    } else {
      elements.tabs[id].classList.remove('active');
      elements.panels[id].classList.remove('active');
    }
  });

  // Action adjustments per tab
  if (tabId === 'dashboard') {
    renderActiveDashboard();
  }
}

// Switch Active Target Company
function switchCompany(companyId) {
  state.currentCompanyId = companyId;
  const company = companiesData[companyId];

  if (company) {
    elements.companyBadge.textContent = company.ticker;
    elements.companyBadge.style.display = 'inline-block';
    elements.companyName.textContent = company.name;
  } else {
    // Custom uploads scope
    elements.companyBadge.style.display = 'none';
    elements.companyName.textContent = "Custom Document Repository";
  }

  // Sync panels
  if (state.currentTab === 'dashboard') {
    renderActiveDashboard();
  }
  renderActiveRisks();
  renderActiveChatHistory();
  renderActiveDocumentsList();
}

/* ==========================================================================
   RENDER METHODS FOR VARIOUS TABS
   ========================================================================== */

// 1. Dashboard Renderer
function renderActiveDashboard() {
  const company = companiesData[state.currentCompanyId];
  
  // Reset previous charts
  destroyCharts();

  if (!company) {
    // Custom doc mode layout (no charts)
    elements.dashboardIndustry.textContent = "MULTIPLE SECTORS";
    elements.dashboardSummary.innerHTML = `
      <div style="text-align: center; padding: 40px 20px;">
        <h3 style="margin-bottom: 12px; color: var(--accent-cyan);">Custom Document Dashboard</h3>
        <p style="color: var(--text-secondary); max-width: 500px; margin: 0 auto; line-height: 1.6;">
          Financial visualizations are deactivated for custom documents. 
          Please navigate to the <strong>AI Chat Copilot</strong> to query your documents, or 
          <strong>Document Manager</strong> to upload and index more files.
        </p>
      </div>
    `;
    return;
  }

  // Normal company rendering
  elements.dashboardIndustry.textContent = company.industry;
  elements.dashboardSummary.textContent = company.summary;
  
  // Render Chart.js
  setTimeout(() => {
    renderFinancialCharts('revenue-chart-canvas', 'leverage-chart-canvas', company);
  }, 100);
}

// 2. Risks Renderer
function renderActiveRisks() {
  const company = companiesData[state.currentCompanyId];
  elements.riskTableBody.innerHTML = '';

  if (!company) {
    // Custom documents risks overview
    elements.riskCountCritical.textContent = '-';
    elements.riskCountHigh.textContent = '-';
    elements.riskCountMedium.textContent = '-';
    
    // Check if custom documents have risks
    elements.riskTableBody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 40px;">
          Risk categories are only pre-parsed for standard portfolio companies.<br>
          Use the <strong>AI Chat Copilot</strong> to extract risks from custom uploaded files dynamically.
        </td>
      </tr>
    `;
    return;
  }

  // Pre-load company risk counters
  const critical = company.risks.filter(r => r.severity === 'CRITICAL').length;
  const high = company.risks.filter(r => r.severity === 'HIGH').length;
  const medium = company.risks.filter(r => r.severity === 'MEDIUM').length;

  elements.riskCountCritical.textContent = critical;
  elements.riskCountHigh.textContent = high;
  elements.riskCountMedium.textContent = medium;

  // Build risk table rows
  company.risks.forEach(risk => {
    const row = document.createElement('tr');
    row.className = 'risk-row';
    row.innerHTML = `
      <td><span class="severity-badge ${risk.severity}">${risk.severity}</span></td>
      <td style="color: var(--text-secondary); font-weight: 500;">${risk.category}</td>
      <td>
        <div class="risk-title">${risk.title}</div>
        <div class="risk-desc">${risk.description}</div>
      </td>
      <td>
        <button class="risk-source-btn" data-source-ref="${risk.sourceRef}" data-risk-title="${risk.title}">
          <svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
          View Source
        </button>
      </td>
    `;
    elements.riskTableBody.appendChild(row);
  });

  // Attach table events
  elements.riskTableBody.querySelectorAll('.risk-source-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const sourceRef = btn.getAttribute('data-source-ref');
      const title = btn.getAttribute('data-risk-title');
      openCitationDrawerFromRisk(company.id, sourceRef, title);
    });
  });
}

// 3. Chat History Renderer
function renderActiveChatHistory() {
  const companyId = state.currentCompanyId;
  const history = state.chatHistories[companyId];

  // Clear Chat DOM
  elements.chatHistory.innerHTML = '';

  if (history.length === 0) {
    // Insert welcome message
    appendChatBubble('assistant', WELCOME_MESSAGES[companyId]);
  } else {
    // Re-render past conversations
    history.forEach(msg => {
      appendChatBubble(msg.sender, msg.text, msg.citations);
    });
  }

  // Populate prompt suggestions
  elements.chatSuggestions.innerHTML = '';
  const prompts = SUGGESTION_PROMPTS[companyId] || [];
  prompts.forEach(promptText => {
    const chip = document.createElement('button');
    chip.className = 'suggestion-chip';
    chip.textContent = promptText;
    chip.addEventListener('click', () => {
      elements.chatInput.value = promptText;
      handleSendMessage();
    });
    elements.chatSuggestions.appendChild(chip);
  });

  // Scroll to bottom
  elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

// 4. Document Manager Renderer
function renderActiveDocumentsList() {
  elements.documentList.innerHTML = '';

  const companyId = state.currentCompanyId;
  
  // Render default files if this is a pre-loaded company
  const company = companiesData[companyId];
  if (company) {
    company.filings.forEach(filing => {
      const fileItem = document.createElement('div');
      fileItem.className = 'file-item';
      fileItem.innerHTML = `
        <div class="file-info">
          <div class="file-icon">
            <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
          </div>
          <div>
            <div class="file-name">${company.name} - ${filing.section}</div>
            <div class="file-size">Built-in Portfolo Doc • ${filing.content.length} chars</div>
          </div>
        </div>
        <span class="indexing-badge">Indexed</span>
      `;
      elements.documentList.appendChild(fileItem);
    });
  }

  // Render matching custom uploaded files
  const filteredCustoms = state.customDocuments.filter(d => 
    companyId === 'custom' || d.companyId === companyId
  );

  filteredCustoms.forEach(doc => {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
      <div class="file-info">
        <div class="file-icon" style="color: var(--accent-violet);">
          <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
        </div>
        <div>
          <div class="file-name">${doc.name}</div>
          <div class="file-size">${formatBytes(doc.size)} • Custom PDF/TXT</div>
        </div>
      </div>
      <span class="indexing-badge" style="border-color: rgba(127, 0, 255, 0.2); background: rgba(127, 0, 255, 0.08); color: #c084fc;">Indexed</span>
    `;
    elements.documentList.appendChild(fileItem);
  });

  if (elements.documentList.children.length === 0) {
    elements.documentList.innerHTML = `
      <div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 0.85rem;">
        No files indexed for this repository yet. Drag & Drop a file on the left to add one!
      </div>
    `;
  }
}

/* ==========================================================================
   CHAT INTERACTIONS & RENDERING
   ========================================================================== */

function appendChatBubble(sender, markdownText, citations = []) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${sender}`;

  // Time & Source Label
  const meta = document.createElement('div');
  meta.className = 'chat-meta';
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  meta.innerHTML = `<span>${sender === 'user' ? 'You' : 'DueDiligence AI'}</span> • <span>${time}</span>`;
  bubble.appendChild(meta);

  // Body Text
  const body = document.createElement('div');
  body.className = 'chat-body';
  // Parse markdown if Marked library is available, otherwise just format linebreaks
  if (window.marked && typeof window.marked.parse === 'function') {
    body.innerHTML = window.marked.parse(markdownText);
  } else {
    body.textContent = markdownText;
    body.style.whiteSpace = 'pre-line';
  }
  bubble.appendChild(body);

  // Add Citation badges if any
  if (sender === 'assistant' && citations && citations.length > 0) {
    const wrapper = document.createElement('div');
    wrapper.className = 'citations-wrapper';
    wrapper.innerHTML = `<div class="citations-title">Retrieved Sources</div>`;
    
    const badgesContainer = document.createElement('div');
    badgesContainer.className = 'citations-badges';
    
    // De-duplicate references by section/text
    const seen = new Set();
    citations.forEach((cit, idx) => {
      const key = cit.source + (cit.section || '');
      if (seen.has(key)) return;
      seen.add(key);

      const badge = document.createElement('button');
      badge.className = 'citation-badge';
      badge.textContent = `[${cit.section || cit.source}]`;
      badge.addEventListener('click', () => {
        openCitationDrawerDirect(cit);
      });
      badgesContainer.appendChild(badge);
    });

    wrapper.appendChild(badgesContainer);
    bubble.appendChild(wrapper);
  }

  elements.chatHistory.appendChild(bubble);
  elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

// Typing Indicator Manager
let typingIndicatorElement = null;
function showTypingIndicator() {
  if (typingIndicatorElement) return;

  typingIndicatorElement = document.createElement('div');
  typingIndicatorElement.className = 'chat-bubble assistant';
  typingIndicatorElement.style.padding = '8px 16px';
  typingIndicatorElement.innerHTML = `
    <div class="typing-indicator">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
  `;
  elements.chatHistory.appendChild(typingIndicatorElement);
  elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

function removeTypingIndicator() {
  if (typingIndicatorElement) {
    typingIndicatorElement.remove();
    typingIndicatorElement = null;
  }
}

// User triggers message send
async function handleSendMessage() {
  const query = elements.chatInput.value.trim();
  if (query === '') return;

  // Clear input
  elements.chatInput.value = '';
  
  const companyId = state.currentCompanyId;

  // 1. Add message to state & render
  state.chatHistories[companyId].push({ sender: 'user', text: query });
  appendChatBubble('user', query);

  // 2. Show typing
  showTypingIndicator();

  try {
    // 3. Execute query
    const result = await executeRAGQuery(companyId, query, state.customDocuments, state.apiKey);
    
    // 4. Save response to state & render
    state.chatHistories[companyId].push({ 
      sender: 'assistant', 
      text: result.answer, 
      citations: result.citations 
    });
    
    removeTypingIndicator();
    appendChatBubble('assistant', result.answer, result.citations);
  } catch (error) {
    removeTypingIndicator();
    appendChatBubble('assistant', `⚠️ Sorry, an error occurred while processing your request: ${error.message}`);
  }
}

/* ==========================================================================
   CITATION DRAWER LOGIC
   ========================================================================== */

// Citation opened from a search response badge
function openCitationDrawerDirect(citation) {
  elements.drawerCompany.textContent = citation.source;
  elements.drawerSection.textContent = citation.section || "General Extract";
  
  // Escape HTML and highlight matching phrases
  const text = citation.text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  elements.drawerBody.innerHTML = `<div class="highlighted-text">${text}</div>`;
  
  elements.drawerOverlay.classList.add('active');
}

// View Source clicked in the Risk Assessment table
function openCitationDrawerFromRisk(companyId, sourceRef, riskTitle) {
  const company = companiesData[companyId];
  if (!company) return;

  // Search filings for section name
  const filing = company.filings.find(f => sourceRef.includes(f.section) || f.section.includes(sourceRef.replace("Section: ", "")));
  
  elements.drawerCompany.textContent = company.name;
  elements.drawerSection.textContent = sourceRef;

  if (filing) {
    // Try to find the sentence related to the risk title
    const content = filing.content;
    const cleanTitle = riskTitle.replace(/\([^)]*\)/g, "").trim();
    const sentences = content.split(/[.!?]\s+/);
    
    // Match title keywords
    let matchedSentenceIndex = -1;
    const keywords = cleanTitle.toLowerCase().split(/\s+/).filter(w => w.length > 4);
    
    for (let i = 0; i < sentences.length; i++) {
      const sLower = sentences[i].toLowerCase();
      if (keywords.some(k => sLower.includes(k))) {
        matchedSentenceIndex = i;
        break;
      }
    }

    if (matchedSentenceIndex !== -1) {
      // Build a rich highlighted display of the section text
      let highlightedHTML = "";
      sentences.forEach((s, idx) => {
        if (idx === matchedSentenceIndex) {
          highlightedHTML += `<span class="highlighted-text">${s}.</span> `;
        } else {
          highlightedHTML += `${s}. `;
        }
      });
      elements.drawerBody.innerHTML = highlightedHTML;
    } else {
      elements.drawerBody.innerHTML = `<span class="highlighted-text">${content}</span>`;
    }
  } else {
    elements.drawerBody.innerHTML = `<div style="color: var(--text-muted);">Could not locate full source text for '${sourceRef}' details.</div>`;
  }

  elements.drawerOverlay.classList.add('active');
}

function closeCitationDrawer() {
  elements.drawerOverlay.classList.remove('active');
}

/* ==========================================================================
   SETTINGS MODAL LOGIC
   ========================================================================== */

function openSettingsModal() {
  elements.apiKeyInput.value = state.apiKey;
  elements.modalOverlay.classList.add('active');
}

function closeSettingsModal() {
  elements.modalOverlay.classList.remove('active');
}

function saveSettings() {
  const newKey = elements.apiKeyInput.value.trim();
  state.apiKey = newKey;
  
  if (newKey === '') {
    localStorage.removeItem('gemini_api_key');
  } else {
    localStorage.setItem('gemini_api_key', newKey);
  }

  updateAPIIndicator();
  closeSettingsModal();
}

/* ==========================================================================
   FILE UPLOAD PROCESSING
   ========================================================================== */

async function processFileUpload(file) {
  if (!file) return;

  // Show indexing feedback in document list
  const tempId = 'temp-' + Date.now();
  const loadingItem = document.createElement('div');
  loadingItem.className = 'file-item';
  loadingItem.id = tempId;
  loadingItem.innerHTML = `
    <div class="file-info">
      <div class="file-icon" style="color: var(--accent-cyan); animation: pulseGlow 1s infinite alternate;">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
      </div>
      <div>
        <div class="file-name">${file.name}</div>
        <div class="file-size">Extracting and indexing text on server...</div>
      </div>
    </div>
  `;
  elements.documentList.prepend(loadingItem);

  try {
    // Send file via multipart/form-data to the FastAPI server
    const formData = new FormData();
    formData.append('file', file);
    formData.append('companyId', state.currentCompanyId === 'custom' ? 'custom' : state.currentCompanyId);
    formData.append('apiKey', state.apiKey || '');

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP status ${response.status}`);
    }

    const docObj = await response.json();

    // Add metadata object returned by server to client state
    state.customDocuments.push(docObj);
    
    // Remove loading item
    const tempEl = document.getElementById(tempId);
    if (tempEl) tempEl.remove();
    
    // Update files panel
    renderActiveDocumentsList();

    // Visual feedback notification
    alert(`Successfully parsed and indexed: ${file.name}`);
  } catch (error) {
    console.error("File parsing error:", error);
    const tempEl = document.getElementById(tempId);
    if (tempEl) tempEl.remove();
    alert(`File upload failed: ${error.message}`);
  }
}

// Utility to format bytes beautifully
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/* ==========================================================================
   EVENT LISTENERS INITIALIZERS
   ========================================================================== */

function setupEventListeners() {
  // Tab click listeners
  Object.keys(elements.tabs).forEach(tabId => {
    elements.tabs[tabId].addEventListener('click', () => switchTab(tabId));
  });

  // Company Select dropdown
  elements.companySelect.addEventListener('change', (e) => {
    switchCompany(e.target.value);
  });

  // Settings modals
  elements.settingsBtn.addEventListener('click', openSettingsModal);
  elements.modalClose.addEventListener('click', closeSettingsModal);
  elements.settingsCancel.addEventListener('click', closeSettingsModal);
  elements.settingsSave.addEventListener('click', saveSettings);
  elements.modalOverlay.addEventListener('click', (e) => {
    if (e.target === elements.modalOverlay) closeSettingsModal();
  });

  // Drawer overlays
  elements.drawerClose.addEventListener('click', closeCitationDrawer);
  elements.drawerOverlay.addEventListener('click', (e) => {
    if (e.target === elements.drawerOverlay) closeCitationDrawer();
  });

  // Chat send buttons
  elements.chatSendBtn.addEventListener('click', handleSendMessage);
  elements.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Drag and Drop files manager
  elements.dragDropZone.addEventListener('click', () => elements.fileInput.click());
  elements.fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    processFileUpload(file);
  });

  elements.dragDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.dragDropZone.style.borderColor = 'var(--accent-cyan)';
    elements.dragDropZone.style.background = 'rgba(0, 242, 254, 0.04)';
  });

  elements.dragDropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    elements.dragDropZone.style.borderColor = 'var(--border-color)';
    elements.dragDropZone.style.background = 'rgba(255, 255, 255, 0.01)';
  });

  elements.dragDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.dragDropZone.style.borderColor = 'var(--border-color)';
    elements.dragDropZone.style.background = 'rgba(255, 255, 255, 0.01)';
    const file = e.dataTransfer.files[0];
    processFileUpload(file);
  });
}

// Trigger initial start
window.addEventListener('DOMContentLoaded', initApp);
