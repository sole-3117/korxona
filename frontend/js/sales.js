// Mahsulotlar yuklash
async function loadProducts(query = '') {
    const products = await apiCall(`/sales/products?search=${query}`);
    const list = document.getElementById('productList');
    list.innerHTML = products.map(p => `
        <div class="card">
            <h3>${p.name}</h3>
            <p>Narx: ${p.price} so'm</p>
            <p>Ombor: ${p.stock}</p>
            <button onclick="addToCart(${p.id})">Qo'shish</button>
        </div>
    `).join('');
}

// Savatcha
let cart = [];
function addToCart(productId) {
    // Miqdor +/-
    cart.push({ id: productId, qty: 1 });
    updateCart();
}

function updateCart() {
    const cartEl = document.querySelector('.cart');
    cartEl.innerHTML = cart.map(item => `<div>${item.id} - ${item.qty}</div>`).join('') + 
        `<button onclick="checkout()">To'lash</button>`;
    cartEl.style.display = 'block';
}

async function checkout() {
    // Chegirma, to'lov turi kiritish
    const discount = prompt('Chegirma (foiz yoki summa):') || 0;
    const payment = prompt('To\'lov: naqd/karta/aralash');
    const saleData = { items: cart, discount, payment_type: payment };
    const sale = await apiCall('/sales', 'POST', saleData);
    // Chek yuborish
    await apiCall(`/receipts/${sale.id}/send`);
    cart = [];
    updateCart();
    alert('Sotuv muvaffaqiyatli!');
}
