let cart = [];

async function loadProducts(query = '') {
    try {
        const products = await apiCall(`/sales/products?search=${encodeURIComponent(query)}`);
        const list = document.getElementById('productList');
        list.innerHTML = products.map(p => `
            <div class="card">
                <h3>${p.name}</h3>
                <p>Narx: ${p.price} so'm</p>
                <p>Ombor: ${p.stock}</p>
                <button onclick="addToCart(${p.id}, '${p.name}', ${p.price})">+ Qo'shish</button>
            </div>
        `).join('');
    } catch (err) {
        alert(err.message);
    }
}

function addToCart(id, name, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ id, name, price, qty: 1 });
    }
    updateCart();
}

function updateCart() {
    const cartEl = document.getElementById('cart');
    const itemsEl = document.getElementById('cartItems');
    itemsEl.innerHTML = cart.map(item => `
        <div>${item.name} x${item.qty} = ${(item.price * item.qty).toFixed(0)} so'm 
            <button onclick="changeQty(${cart.indexOf(item)}, -1)">-</button>
            <button onclick="changeQty(${cart.indexOf(item)}, 1)">+</button>
        </div>
    `).join('');
    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    itemsEl.innerHTML += `<p>Jami: ${total} so'm</p>`;
    cartEl.style.display = cart.length ? 'block' : 'none';
}

function changeQty(index, delta) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) cart.splice(index, 1);
    updateCart();
}

async function checkout() {
    if (!cart.length) return alert('Savatcha bo\'sh');
    const discountStr = document.getElementById('discount').value;
    const discount = parseFloat(discountStr) || 0;
    const payment = document.getElementById('payment').value;
    const items = cart.map(item => ({ product_id: item.id, quantity: item.qty, price: item.price }));
    try {
        const sale = await apiCall('/sales/create', 'POST', { items, discount_amount: discount, payment_type: payment });
        // Chek yuborish
        await apiCall(`/receipts/${sale.id}/generate`);  // Backend'da implement qiling
        alert('Sotuv muvaffaqiyatli! Chek Telegram\'ga yuborildi.');
        cart = [];
        updateCart();
        loadProducts();
    } catch (err) {
        alert(err.message);
    }
}
