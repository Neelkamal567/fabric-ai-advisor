/**
 * FabricAI — Frontend Application Logic
 * Handles tab switching, form submission, chatbot, and API interactions.
 */

const API_BASE = window.location.origin;

// ---- State ----
let chatHistory = [];
let isLoading = false;
let currentRecommendations = [];

// ---- Global Chart Settings ----
Chart.defaults.color = "rgba(255, 255, 255, 0.7)";
Chart.defaults.font.family = "'Inter', sans-serif";

// ---- DOM Elements ----
const navPills = document.querySelectorAll('.nav-pill');
const tabPanels = document.querySelectorAll('.tab-panel');
const recommendForm = document.getElementById('recommend-form');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const emptyState = document.getElementById('empty-state');
const resultsContainer = document.getElementById('results-container');
const fabricCards = document.getElementById('fabric-cards');
const explanationCard = document.getElementById('explanation-card');
const explanationText = document.getElementById('explanation-text');
const resultsQuery = document.getElementById('results-query');
const submitBtn = document.getElementById('recommend-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const suggestionChips = document.querySelectorAll('.chip');
const voiceBtn = document.getElementById('voice-btn');

// New DOM Elements
const btnCompare = document.getElementById('btn-compare');
const comparisonView = document.getElementById('comparison-view');
const comparisonContainer = document.getElementById('comparison-container');
const closeCompareBtn = document.getElementById('close-compare-btn');
const modalOverlay = document.getElementById('fabric-modal');
const modalClose = document.getElementById('modal-close');
const modalBody = document.getElementById('modal-body');
const themeToggle = document.getElementById('theme-toggle');

// ---- Initialize ----
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadOptions();
    initTabSwitching();
    initRecommendForm();
    initChat();
    initVoice();
    initExtraTools();
    initTheme();
});

// ---- Theme Logic ----
function initTheme() {
    const savedTheme = localStorage.getItem('fabricTheme') || 'dark';
    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        themeToggle.textContent = '☀️';
        Chart.defaults.color = "rgba(0, 0, 0, 0.7)";
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'light') {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('fabricTheme', 'dark');
            themeToggle.textContent = '🌙';
            Chart.defaults.color = "rgba(255, 255, 255, 0.7)";
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('fabricTheme', 'light');
            themeToggle.textContent = '☀️';
            Chart.defaults.color = "rgba(0, 0, 0, 0.7)";
        }
        
        // Force redraw of any specific logic if needed
        // but charts will catch it on next render.
    });
}

// ---- Health Check & Options ----
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        statusDot.classList.add('online');
        const parts = [];
        if (data.model_loaded) parts.push('ML');
        if (data.dataset_loaded) parts.push('Data');
        if (data.gemini_available) parts.push('Gemini');
        statusText.textContent = parts.length ? `${parts.join(' + ')} Active` : 'Online';
    } catch {
        statusDot.classList.remove('online');
        statusText.textContent = 'Connecting...';
        setTimeout(checkHealth, 3000);
    }
}

async function loadOptions() {
    try {
        const res = await fetch(`${API_BASE}/api/options`);
        const data = await res.json();
        populateSelect('weather-select', data.weathers);
        populateSelect('festival-select', data.festivals);
        populateSelect('purpose-select', data.purposes);
    } catch (err) {
        populateSelect('weather-select', ['summer', 'winter', 'rainy', 'humid', 'autumn']);
        populateSelect('festival-select', ['None', 'Wedding', 'Diwali', 'Eid', 'Christmas', 'Holi', 'Office Event', 'Interview']);
        populateSelect('purpose-select', ['Daily Wear', 'Office', 'Sports', 'Travel', 'Party', 'Formal', 'Ethnic Wear']);
    }
}

function populateSelect(selectId, options) {
    const select = document.getElementById(selectId);
    if (!select) return;
    const placeholder = select.options[0];
    select.innerHTML = '';
    select.appendChild(placeholder);
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = formatLabel(opt);
        select.appendChild(option);
    });
}

function formatLabel(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

// ---- Tab Switching ----
function initTabSwitching() {
    navPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const tab = pill.dataset.tab;
            navPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `panel-${tab}`) panel.classList.add('active');
            });
            if (tab === 'chat') setTimeout(() => chatInput.focus(), 300);
        });
    });
}

// ---- Recommend Form ----
function initRecommendForm() {
    recommendForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (isLoading) return;
        const weather = document.getElementById('weather-select').value;
        const festival = document.getElementById('festival-select').value;
        const purpose = document.getElementById('purpose-select').value;

        if (!weather || !festival || !purpose) {
            shakeElement(submitBtn);
            return;
        }
        await getRecommendations(weather, festival, purpose);
    });
}

async function getRecommendations(weather, festival, purpose) {
    isLoading = true;
    submitBtn.classList.add('loading');

    try {
        const res = await fetch(`${API_BASE}/api/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ weather, festival, purpose, top_n: 5 }),
        });
        const data = await res.json();
        if (data.success && data.recommendations.length > 0) {
            currentRecommendations = data.recommendations;
            renderRecommendations(data.recommendations, data.query, data.explanation);
        } else {
            showError('No recommendations found. Try different criteria.');
        }
    } catch (err) {
        showError('Failed to get recommendations. Please try again.');
    } finally {
        isLoading = false;
        submitBtn.classList.remove('loading');
    }
}

// ---- UI Extractor ---
function getCurrentUIState() {
    return {
        weather: document.getElementById('weather-select').value,
        festival: document.getElementById('festival-select').value,
        purpose: document.getElementById('purpose-select').value
    };
}

// ---- Rendering Recommendations ----
function renderRecommendations(recommendations, query, explanation) {
    emptyState.style.display = 'none';
    resultsContainer.style.display = 'block';
    btnCompare.style.display = 'none';
    comparisonView.style.display = 'none';
    resultsQuery.textContent = `For ${formatLabel(query.weather)} weather • ${query.festival} occasion • ${query.purpose}`;
    fabricCards.innerHTML = '';

    recommendations.forEach((rec, index) => {
        const rankClass = index === 0 ? 'rank-1' : index === 1 ? 'rank-2' : index === 2 ? 'rank-3' : 'rank-default';
        
        const card = document.createElement('div');
        card.className = 'fabric-card';
        card.innerHTML = `
            <div class="fabric-card-header">
                <span class="fabric-name">${rec.fabric_type}</span>
                <span class="fabric-rank ${rankClass}">#${index + 1}</span>
            </div>
            
            <div class="fabric-card-inner-flex">
                <div class="fabric-image-container" onclick="openFabricModal(${index})">
                    <img src="${rec.image_url || '/static/css/placeholder.png'}" alt="${rec.fabric_type}">
                </div>
                
                <div class="fabric-content-area">
                    <div class="fabric-tags" style="margin-bottom:10px;">
                        <span class="fabric-tag tag-cost">💰 ${rec.cost_category}</span>
                        <span class="fabric-tag tag-weight">⚖️ ${rec.weight}</span>
                        ${rec.moisture_wicking === 'Yes' ? '<span class="fabric-tag tag-wicking">💧 Wicking</span>' : ''}
                        <span class="fabric-tag tag-score">⭐ Score: ${rec.combined_score || rec.suitability_score}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">
                        <strong>Why this fabric:</strong> ${rec.why_this_fabric || 'matches your criteria.'}
                    </div>
                </div>
                
                <div class="radar-chart-container">
                    <canvas id="chart-${index}"></canvas>
                </div>
            </div>

            <div class="card-actions-row">
                <label class="compare-checkbox-label">
                    <input type="checkbox" class="compare-cb" value="${index}">
                    Compare
                </label>
            </div>
        `;
        fabricCards.appendChild(card);
        drawRadarChart(`chart-${index}`, rec);
    });

    // Checkbox listener
    document.querySelectorAll('.compare-cb').forEach(cb => {
        cb.addEventListener('change', updateCompareButton);
    });

    if (explanation) {
        explanationCard.style.display = 'block';
        explanationText.innerHTML = explanation.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    } else {
        explanationCard.style.display = 'none';
    }
}

function drawRadarChart(canvasId, rec) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Comfort', 'Durability', 'Breathable', 'Sustainable'],
            datasets: [{
                label: 'Score',
                data: [rec.comfort_level, rec.durability, rec.breathability, rec.sustainability_score],
                backgroundColor: 'rgba(167, 139, 250, 0.2)',
                borderColor: 'rgba(167, 139, 250, 0.8)',
                pointBackgroundColor: 'rgba(6, 182, 212, 1)',
                borderWidth: 1.5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { font: { size: 9 }, color: '#9ca3af' },
                    ticks: { display: false, min: 0, max: 10 }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updateCompareButton() {
    const checked = document.querySelectorAll('.compare-cb:checked');
    btnCompare.style.display = checked.length > 1 ? 'block' : 'none';
}

function showError(message) {
    emptyState.style.display = 'none';
    resultsContainer.style.display = 'block';
    fabricCards.innerHTML = `<div class="glass-card" style="padding: 32px; text-align: center;"><p style="color: var(--accent-tertiary);">${message}</p></div>`;
    explanationCard.style.display = 'none';
}

function shakeElement(el) {
    el.style.animation = 'none';
    el.offsetHeight; 
    el.style.animation = 'shake 0.4s ease';
}

// ---- Analytics & Tools (Compare, Modal) ----
function initExtraTools() {
    // Compare
    btnCompare.addEventListener('click', () => {
        const checked = Array.from(document.querySelectorAll('.compare-cb:checked')).map(cb => parseInt(cb.value));
        const selected = checked.map(i => currentRecommendations[i]);
        
        let html = '<table class="compare-table"><thead><tr><th>Property</th>';
        selected.forEach(s => html += `<th>${s.fabric_type}</th>`);
        html += '</tr></thead><tbody>';
        
        const props = [
            { key: 'comfort_level', label: 'Comfort (1-10)' },
            { key: 'durability', label: 'Durability (1-10)' },
            { key: 'breathability', label: 'Breathability (1-10)' },
            { key: 'sustainability_score', label: 'Sustainability (1-10)' },
            { key: 'cost_category', label: 'Cost' },
            { key: 'weight', label: 'Weight' }
        ];

        props.forEach(p => {
            html += `<tr><td><strong>${p.label}</strong></td>`;
            // Find max for highlighting numeric
            let maxV = -1;
            if(p.label.includes('(1-10)')) {
                maxV = Math.max(...selected.map(s => s[p.key]));
            }
            selected.forEach(s => {
                const val = s[p.key];
                const highlight = (val === maxV) ? 'class="compare-highlight"' : '';
                html += `<td ${highlight}>${val}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        comparisonContainer.innerHTML = html;
        comparisonView.style.display = 'block';
    });

    closeCompareBtn.addEventListener('click', () => comparisonView.style.display = 'none');
    modalClose.addEventListener('click', () => modalOverlay.classList.remove('active'));
    modalOverlay.addEventListener('click', (e) => { if(e.target === modalOverlay) modalOverlay.classList.remove('active'); });
}

window.openFabricModal = function(index) {
    const rec = currentRecommendations[index];
    let advHtml = rec.advantages ? rec.advantages.map(a => `<li>✔️ ${a}</li>`).join('') : '';
    let disHtml = rec.disadvantages ? rec.disadvantages.map(a => `<li>❌ ${a}</li>`).join('') : '';
    
    modalBody.innerHTML = `
        <h2 style="color:var(--accent-primary); margin-bottom: 20px; font-family:var(--font-heading)">${rec.fabric_type} Details</h2>
        <div style="display:flex; gap: 20px; margin-bottom:20px;">
            <img src="${rec.image_url}" style="width:150px; height:150px; border-radius:12px; object-fit:cover; border:1px solid var(--glass-border);">
            <div>
                <p><strong>Why this fabric?</strong><br> ${rec.why_this_fabric || 'A solid choice based on context.'}</p>
                <div style="margin-top:10px;">
                    <strong>Care Instructions:</strong><br>
                    <span style="color:var(--text-secondary); font-size:0.9rem;">${rec.care_instructions || 'Check label.'}</span>
                </div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; font-size:0.85rem;">
            <div style="background:rgba(52, 211, 153, 0.05); padding:15px; border-radius:8px;">
                <strong>Advantages</strong>
                <ul style="list-style:none; margin-top:8px;">${advHtml}</ul>
            </div>
            <div style="background:rgba(244, 114, 182, 0.05); padding:15px; border-radius:8px;">
                <strong>Disadvantages</strong>
                <ul style="list-style:none; margin-top:8px;">${disHtml}</ul>
            </div>
        </div>
    `;
    modalOverlay.classList.add('active');
}

// ---- Chat & Voice ----
function initChat() {
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg || isLoading) return;
        sendChatMessage(msg);
    });

    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const msg = chip.dataset.msg;
            chatInput.value = msg;
            sendChatMessage(msg);
        });
    });

    clearChatBtn.addEventListener('click', () => {
        chatHistory = [];
        chatMessages.innerHTML = `
            <div class="message bot-message fade-in">
                <div class="message-avatar">🧵</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <p>👋 Chat cleared! How can I help you with fabric recommendations?</p>
                    </div>
                    <span class="message-time">${getTimeString()}</span>
                </div>
            </div>
        `;
    });
}

function initVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        voiceBtn.style.display = 'none';
        return;
    }
    
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    voiceBtn.addEventListener('click', () => {
        if (voiceBtn.classList.contains('recording')) {
            recognition.stop();
        } else {
            recognition.start();
            voiceBtn.classList.add('recording');
        }
    });

    recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        chatInput.value = transcript;
        sendChatMessage(transcript);
        voiceBtn.classList.remove('recording');
    };

    recognition.onerror = () => voiceBtn.classList.remove('recording');
    recognition.onend = () => voiceBtn.classList.remove('recording');
}

async function sendChatMessage(message) {
    appendMessage(message, 'user');
    chatInput.value = '';
    isLoading = true;
    const typingEl = showTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: chatHistory,
                ui_context: getCurrentUIState() // Dynamic context extraction
            }),
        });

        const data = await res.json();
        typingEl.remove();

        if (data.success) {
            appendMessage(data.reply, 'bot');
            chatHistory = data.history || chatHistory;
            if (data.recommendations && data.recommendations.length > 0) {
                appendRecommendationCards(data.recommendations);
            }
        } else {
            appendMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (err) {
        typingEl.remove();
        appendMessage('⚠️ Connection error. Please check if the server is running.', 'bot');
    } finally {
        isLoading = false;
    }
}

function appendMessage(content, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'} fade-in`;
    const avatar = sender === 'user' ? '👤' : '🧵';
    let htmlContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
    htmlContent = htmlContent.replace(/^(\d+\.)\s/gm, '<br>$1 ');

    msgDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble"><p>${htmlContent}</p></div>
            <span class="message-time">${getTimeString()}</span>
        </div>
    `;
    chatMessages.appendChild(msgDiv);
    scrollChatToBottom();
}

function appendRecommendationCards(recommendations) {
    const container = document.createElement('div');
    container.className = 'message bot-message fade-in';
    container.style.maxWidth = '100%';

    let cardsHtml = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">';
    recommendations.slice(0, 3).forEach((rec, i) => {
        cardsHtml += `
            <div style="flex: 1; min-width: 140px; padding: 12px; background: rgba(167,139,250,0.08); border-radius: 12px; border: 1px solid rgba(167,139,250,0.15);">
                <div style="font-weight: 700; color: var(--accent-primary); font-size: 0.9rem; margin-bottom: 6px;">#${i+1} ${rec.fabric_type}</div>
                <div style="font-size: 0.72rem; color: var(--text-secondary); line-height: 1.5;">
                    Comfort: ${rec.comfort_level}/10<br>
                    Cost: ${rec.cost_category}
                </div>
            </div>
        `;
    });
    cardsHtml += '</div>';

    container.innerHTML = `
        <div class="message-avatar">📊</div>
        <div class="message-content">
            <div class="message-bubble">
                <p><strong>Recommendation Results:</strong></p>
                ${cardsHtml}
            </div>
        </div>
    `;
    chatMessages.appendChild(container);
    scrollChatToBottom();
}

function showTypingIndicator() {
    const typing = document.createElement('div');
    typing.className = 'message bot-message fade-in';
    typing.id = 'typing-indicator';
    typing.innerHTML = `
        <div class="message-avatar">🧵</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
            </div>
        </div>
    `;
    chatMessages.appendChild(typing);
    scrollChatToBottom();
    return typing;
}

function scrollChatToBottom() {
    setTimeout(() => chatMessages.scrollTop = chatMessages.scrollHeight, 50);
}

function getTimeString() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
