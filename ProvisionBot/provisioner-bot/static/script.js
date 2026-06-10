let chatHistory = [];
let allRequests = [];

document.addEventListener('DOMContentLoaded', () => {
  // Load initial states
  checkMockMode();
  loadStats();

  // Route-specific loader
  if (window.location.pathname === '/requests') {
    loadRequests();
    // 30 seconds auto-refresh
    setInterval(loadRequests, 30000);

    // Search and filter listeners
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');

    if (searchInput) searchInput.addEventListener('input', filterRequests);
    if (statusFilter) statusFilter.addEventListener('change', filterRequests);
  }

  // Provision Form Submits
  const form = document.getElementById('provision-form');
  if (form) {
    form.addEventListener('submit', submitForm);
  }

  // Chat Panel Toggle
  const chatToggle = document.getElementById('chat-toggle');
  const chatClose = document.getElementById('chat-close');
  const chatPanel = document.getElementById('chat-panel');

  if (chatToggle && chatPanel) {
    chatToggle.addEventListener('click', () => toggleChat(true));
  }
  if (chatClose && chatPanel) {
    chatClose.addEventListener('click', () => toggleChat(false));
  }

  // Chat Submit
  const chatForm = document.getElementById('chat-input-form');
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('chat-input');
      const msg = input.value.trim();
      if (msg) {
        sendMessage(msg);
        input.value = '';
      }
    });
  }

  // Suggestion Chips
  const chipBtns = document.querySelectorAll('.chip-btn');
  chipBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.getAttribute('data-msg');
      if (msg) {
        sendMessage(msg);
      }
    });
  });

  // Render initial greeting in bot panel
  const chatMessages = document.getElementById('chat-messages');
  if (chatMessages && chatMessages.children.length === 0) {
    addBubble("Hello 👋 I am Provisioner AI. How can I help you today?", "bot");
  }
});

// Check if running in mock mode and display banner
function checkMockMode() {
  fetch('/api/status')
    .then(res => res.json())
    .then(data => {
      const banner = document.getElementById('mock-banner');
      if (banner && data.mock_mode) {
        banner.style.display = 'block';
      }
    })
    .catch(err => console.error('Error checking mock mode:', err));
}

// Fetch stats and update counters
function loadStats() {
  fetch('/api/requests')
    .then(res => res.json())
    .then(data => {
      const total = data.length;
      const approved = data.filter(r => r.status === 'approved').length;
      const pending = data.filter(r => r.status === 'pending').length;
      const prs = data.filter(r => r.pr_link && !r.pr_link.includes('mock')).length;

      const totalEl = document.getElementById('total-requests');
      const approvedEl = document.getElementById('approved-count');
      const pendingEl = document.getElementById('pending-count');
      const prEl = document.getElementById('pr-count');

      if (totalEl) totalEl.innerText = total;
      if (approvedEl) approvedEl.innerText = approved;
      if (pendingEl) pendingEl.innerText = pending;
      if (prEl) prEl.innerText = prs;
    })
    .catch(err => console.error('Error loading stats:', err));
}

// Fetch and load requests into tracker table
function loadRequests() {
  fetch('/api/requests')
    .then(res => res.json())
    .then(data => {
      allRequests = data;
      renderTable(data);
    })
    .catch(err => {
      console.error('Error loading requests:', err);
      const tbody = document.getElementById('requests-table-body');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error loading requests.</td></tr>';
      }
    });
}

// Render request rows
function renderTable(requests) {
  const tbody = document.getElementById('requests-table-body');
  if (!tbody) return;

  if (requests.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No requests found.</td></tr>';
    return;
  }

  tbody.innerHTML = requests.map(r => {
    let badgeClass = 'bg-pending';
    if (r.status === 'approved') badgeClass = 'bg-approved';
    if (r.status === 'rejected') badgeClass = 'bg-rejected';

    const dateStr = new Date(r.created_at).toLocaleString();

    return `
      <tr>
        <th scope="row">#${r.id}</th>
        <td>${escapeHtml(r.requester)}</td>
        <td><code class="text-info">${escapeHtml(r.env_type)}</code></td>
        <td><code>${escapeHtml(r.env_name)}</code></td>
        <td><span class="badge ${badgeClass}">${escapeHtml(r.status)}</span></td>
        <td>
          <a href="${r.pr_link}" target="_blank" class="btn btn-sm btn-outline-info">
            PR Link &nearr;
          </a>
        </td>
        <td class="text-white-50">${dateStr}</td>
      </tr>
    `;
  }).join('');
}

// Filter requests locally
function filterRequests() {
  const searchVal = document.getElementById('search-input').value.toLowerCase();
  const statusVal = document.getElementById('status-filter').value;

  const filtered = allRequests.filter(r => {
    const matchesSearch = r.requester.toLowerCase().includes(searchVal) || r.env_type.toLowerCase().includes(searchVal);
    const matchesStatus = statusVal === 'all' || r.status === statusVal;
    return matchesSearch && matchesStatus;
  });

  renderTable(filtered);
}

// Submit the provisioning form
function submitForm(e) {
  e.preventDefault();
  
  const submitBtn = document.getElementById('submit-btn');
  const spinner = document.getElementById('submit-spinner');
  const alertDiv = document.getElementById('form-alert');

  // Set loading states
  if (submitBtn) submitBtn.disabled = true;
  if (spinner) spinner.classList.remove('d-none');
  if (alertDiv) {
    alertDiv.className = 'alert d-none';
    alertDiv.innerText = '';
  }

  const requester = document.getElementById('requesterName').value.trim();
  const env_type = document.getElementById('envType').value;
  const env_name = document.getElementById('envName').value;
  const details = document.getElementById('requestDetails').value.trim();

  const payload = { requester, env_type, env_name, details };

  fetch('/api/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(err => { throw new Error(err.reason || 'Validation or processing failed') });
    }
    return res.json();
  })
  .then(data => {
    if (alertDiv) {
      alertDiv.className = 'alert alert-success';
      alertDiv.innerHTML = `<strong>Success!</strong> Request approved. <a href="${data.pr_link}" target="_blank" class="alert-link">View Pull Request</a>`;
      alertDiv.classList.remove('d-none');
    }
    document.getElementById('provision-form').reset();
    loadStats();
  })
  .catch(err => {
    if (alertDiv) {
      alertDiv.className = 'alert alert-danger';
      alertDiv.innerText = `Error: ${err.message}`;
      alertDiv.classList.remove('d-none');
    }
  })
  .finally(() => {
    if (submitBtn) submitBtn.disabled = false;
    if (spinner) spinner.classList.add('d-none');
  });
}

// Toggle floating chat drawer
function toggleChat(isOpen) {
  const chatPanel = document.getElementById('chat-panel');
  if (!chatPanel) return;

  if (isOpen) {
    chatPanel.style.display = 'flex';
    // Small timeout to allow display change before transition
    setTimeout(() => {
      chatPanel.classList.add('active');
    }, 10);
  } else {
    chatPanel.classList.remove('active');
    setTimeout(() => {
      chatPanel.style.display = 'none';
    }, 400); // match CSS transition duration
  }
}

// Send user message to chat bot
function sendMessage(text) {
  addBubble(text, 'user');
  showTyping();

  const payload = {
    message: text,
    history: chatHistory
  };

  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    hideTyping();
    addBubble(data.reply, 'bot');
    chatHistory.push({ role: 'user', content: text });
    chatHistory.push({ role: 'assistant', content: data.reply });
  })
  .catch(err => {
    console.error('Chat error:', err);
    hideTyping();
    addBubble('Sorry, I encountered an error. Please try again.', 'bot');
  });
}

// Append bubble to chat viewport
function addBubble(text, sender) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `message-bubble ${sender}`;
  bubble.innerText = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// Show animated typing dots
function showTyping() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  // Check if indicator already exists
  if (document.getElementById('typing-indicator')) return;

  const typing = document.createElement('div');
  typing.id = 'typing-indicator';
  typing.className = 'typing-indicator';
  typing.innerHTML = `
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
  `;
  container.appendChild(typing);
  container.scrollTop = container.scrollHeight;
}

// Hide typing indicator
function hideTyping() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) {
    indicator.remove();
  }
}

// Helper to escape HTML tags
function escapeHtml(str) {
  if (!str) return '';
  return str.toString()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
