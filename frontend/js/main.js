let currentUser = {};
Telegram.WebApp.ready();
const API_BASE = '/api';  // Backend URL

async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    const options = {
        method,
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    };
    if (data) options.body = JSON.stringify(data);
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Xato yuz berdi');
    }
    return response.json();
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(pageId)?.style.display = 'block';
    if (pageId === 'sales') loadProducts();
}

async function logout() {
    localStorage.removeItem('token');
    window.location.href = '/static/index.html';
}

// Auto-logout 30 daqiqa
setTimeout(logout, 1800000);

// Dashboard yuklash
if (localStorage.getItem('token')) {
    try {
        currentUser = await apiCall('/auth/me');
        showPage('dashboard');
    } catch (err) {
        localStorage.removeItem('token');
    }
}
