document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const telegramId = Telegram.WebApp.initDataUnsafe.user ? Telegram.WebApp.initDataUnsafe.user.id : 0;
    
    try {
        const data = { username, password, telegram_id: telegramId };
        const res = await apiCall('/auth/login', 'POST', data);
        localStorage.setItem('token', res.access_token);
        showPage('dashboard');  // Dashboard sahifasiga o'tish
    } catch (err) {
        document.getElementById('error').textContent = 'Xato: ' + err.message;
    }
});

// Auto-logout (30 daqiqa)
setTimeout(() => { localStorage.removeItem('token'); showPage('login'); }, 1800000);
