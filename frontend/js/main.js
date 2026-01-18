Telegram.WebApp.ready();
const apiBase = '/api';  // Backend URL

// API chaqiruv
async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${apiBase}${endpoint}`, {
        method,
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
}

// Sahifa o'zgartirish
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(page).style.display = 'block';
}
