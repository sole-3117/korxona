async function createExpense() {
    const type = document.getElementById('expenseType').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const note = document.getElementById('note').value;
    if (type === 'bayram_puli' && currentUser.role !== 'admin') {
        alert('Faqat admin bayram puli kiritishi mumkin');
        return;
    }
    try {
        await apiCall('/expenses/create', 'POST', { type, amount, note });
        alert('Xarajat qo\'shildi');
        // Forma tozalash
    } catch (err) {
        alert(err.message);
    }
}
