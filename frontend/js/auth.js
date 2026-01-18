document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const telegramId = Telegram.WebApp.initDataUnsafe?.user?.id || 123456789;  // Test uchun

    try {
        const res = await apiCall('/auth/login', 'POST', { username, password, telegram_id: telegramId });
        localStorage.setItem('token', res.access_token);
        currentUser = { role: res.role };
        window.location.href = '/static/dashboard.html';
    } catch (err) {
        document.getElementById('error').textContent = err.message;
    }
});
