// static/script.js 
const API_PREFIX = ""; // same origin
// DOM refs
const loginView = document.getElementById('loginView');
const appView = document.getElementById('appView');
const btnLogin = document.getElementById('btnLogin');
const loginUser = document.getElementById('loginUser');
const loginPass = document.getElementById('loginPass');
const userBadge = document.getElementById('userBadge');

const navSearch = document.getElementById('navSearch');
const navAdd = document.getElementById('navAdd');
const navProfile = document.getElementById('navProfile');

const viewSearch = document.getElementById('view-search');
const viewAdd = document.getElementById('view-add');
const viewProfile = document.getElementById('view-profile');

const productList = document.getElementById('productList');
const searchInput = document.getElementById('searchInput');
const productPreview = document.getElementById('productPreview');

const addName = document.getElementById('addName');
const addPrice = document.getElementById('addPrice');
const addNote = document.getElementById('addNote');
const addImage = document.getElementById('addImage');
const btnAdd = document.getElementById('btnAdd');
const btnClear = document.getElementById('btnClear');

const newAdminLogin = document.getElementById('newAdminLogin');
const newAdminPass = document.getElementById('newAdminPass');
const btnAddAdmin = document.getElementById('btnAddAdmin');
const btnPromote = document.getElementById('btnPromote');
const superControls = document.getElementById('superControls');

const btnExport = document.getElementById('btnExport');
const importFile = document.getElementById('importFile');
const changeHistory = document.getElementById('changeHistory');

const themeToggle = document.getElementById('themeToggle');

let state = { token: null, username: null, role: null, products: [] };

// theme
(function(){
  const t = localStorage.getItem('theme') || 'dark';
  if(t==='dark') document.body.classList.add('dark'), themeToggle.textContent='🌙';
  else document.body.classList.remove('dark'), themeToggle.textContent='☀️';
})();
themeToggle.addEventListener('click', ()=>{
  document.body.classList.toggle('dark');
  const is = document.body.classList.contains('dark') ? 'dark' : 'light';
  localStorage.setItem('theme', is);
  themeToggle.textContent = is==='dark' ? '🌙' : '☀️';
});

// check token
(function init(){
  const t = localStorage.getItem('korxona_token');
  if(t) {
    state.token = t;
    fetchProfileAndInit();
  } else {
    showLogin();
  }
})();

btnLogin.addEventListener('click', async ()=>{
  const u = loginUser.value.trim();
  const p = loginPass.value.trim();
  if(!u||!p) return alert('Login va parol kiriting');
  const form = new FormData();
  form.append('username', u);
  form.append('password', p);
  const res = await fetch(`${API_PREFIX}/api/login`, { method:'POST', body: form });
  if(!res.ok) return alert('Login yoki parol xato');
  const j = await res.json();
  state.token = j.access_token;
  state.username = j.username;
  state.role = j.role;
  localStorage.setItem('korxona_token', state.token);
  showApp();
  loadProducts();
  renderProfile();
});

function authFetch(url, opts={}){
  opts.headers = opts.headers || {};
  if(state.token) opts.headers['Authorization'] = 'Bearer ' + state.token;
  return fetch(url, opts);
}

function showLogin(){ loginView.classList.add('active'); appView.classList.remove('active'); }
function showApp(){ loginView.classList.remove('active'); appView.classList.add('active'); }

navSearch.addEventListener('click', ()=> { switchSub('search'); loadProducts(); });
navAdd.addEventListener('click', ()=> { switchSub('add'); });
navProfile.addEventListener('click', ()=> { switchSub('profile'); renderProfile(); });

function switchSub(name){
  document.querySelectorAll('.subview').forEach(s=>s.classList.remove('active'));
  if(name==='search') viewSearch.classList.add('active');
  if(name==='add') viewAdd.classList.add('active');
  if(name==='profile') viewProfile.classList.add('active');
  [navSearch, navAdd, navProfile].forEach(b=>b.classList.remove('active'));
  if(name==='search') navSearch.classList.add('active');
  if(name==='add') navAdd.classList.add('active');
  if(name==='profile') navProfile.classList.add('active');
}

// load products
async function loadProducts(){
  const res = await fetch('/api/products');
  if(!res.ok) return alert('Server error');
  const arr = await res.json();
  state.products = arr;
  renderProducts(arr);
}

function renderProducts(arr){
  productList.innerHTML = '';
  if(!arr.length) return productList.innerHTML = '<div class="card">Mahsulot topilmadi</div>';
  arr.forEach(p=>{
    const el = document.createElement('div'); el.className='item';
    el.innerHTML = `
      <div class="thumb">${p.image ? `<img src="${p.image}" style="width:100%;height:100%;object-fit:cover;border-radius:8px" />` : 'Rasm'}</div>
      <div class="meta"><div class="title">${escapeHtml(p.name)}</div><div class="price">${p.price || '—'}</div><div class="note">${escapeHtml(p.note||'')}</div></div>
      <div class="actions"></div>
    `;
    const actions = el.querySelector('.actions');
    const openBtn = document.createElement('button'); openBtn.textContent='Ochish';
    openBtn.addEventListener('click', ()=> { productPreview(p); });
    actions.appendChild(openBtn);
    if(state.role === 'super' || state.role === 'admin'){
      const editBtn = document.createElement('button'); editBtn.textContent='Tahrirlash'; editBtn.className='ghost';
      editBtn.addEventListener('click', ()=> editProductPrompt(p));
      actions.appendChild(editBtn);
    }
    if(state.role === 'super'){
      const delBtn = document.createElement('button'); delBtn.textContent='Oʻchirish'; delBtn.className='ghost';
      delBtn.addEventListener('click', ()=> deleteProduct(p.id));
      actions.appendChild(delBtn);
    }
    productList.appendChild(el);
  });
}

function productPreview(p){
  if(p.image) productPreview.innerHTML = `<img src="${p.image}" style="max-width:100%;max-height:150px;object-fit:cover" />`;
  else productPreview.innerHTML = 'Rasm yoʻq';
  searchInput.value = p.name;
  switchSub('search');
}

// add product
btnAdd.addEventListener('click', async ()=>{
  if(!state.token) return alert('Kiring');
  const name = addName.value.trim(); const price = addPrice.value.trim();
  if(!name || !price) return alert('Nomi va narx majburiy');
  const fd = new FormData();
  fd.append('name', name); fd.append('price', price);
  fd.append('note', addNote.value || '');
  if(addImage.files && addImage.files[0]) fd.append('image', addImage.files[0]);
  fd.append('token', state.token);
  const res = await fetch('/api/products', { method:'POST', body: fd });
  if(!res.ok) return alert('Xato qoʻshishda');
  alert('Mahsulot qoʻshildi');
  addName.value=''; addPrice.value=''; addNote.value=''; addImage.value='';
  loadProducts();
  switchSub('search');
});

function escapeHtml(s=''){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

async function editProductPrompt(p){
  const name = prompt('Yangi nom', p.name); if(name===null) return;
  const price = prompt('Yangi narx', p.price||''); if(price===null) return;
  const note = prompt('Yangi eslatma', p.note||''); if(note===null) return;
  const fd = new FormData();
  fd.append('name', name); fd.append('price', price); fd.append('note', note); fd.append('token', state.token);
  const res = await fetch(`/api/products/${p.id}`, { method:'PUT', body: fd });
  if(!res.ok) return alert('Xato tahrirlashda');
  alert('Tahrirlandi'); loadProducts();
}

async function deleteProduct(id){
  if(!confirm('Haqiqatan oʻchirasizmi?')) return;
  const fd = new FormData(); fd.append('token', state.token);
  const res = await fetch(`/api/products/${id}`, { method:'DELETE', body: fd });
  if(!res.ok) return alert('Xato o\'chirishda');
  alert('Oʻchirildi'); loadProducts();
}

// profile
async function fetchProfileAndInit(){
  const token = localStorage.getItem('korxona_token');
  state.token = token;
  const res = await fetch(`/api/profile?token=${encodeURIComponent(token)}`);
  if(!res.ok){ localStorage.removeItem('korxona_token'); showLogin(); return; }
  const j = await res.json();
  state.username = j.username; state.role = j.role;
  userBadge.textContent = `${state.username} (${state.role})`;
  showApp(); loadProducts();
  renderProfile();
}

function renderProfile(){
  document.getElementById('profileInfo').innerHTML = `<div>Foydalanuvchi: <strong>${state.username}</strong></div><div>Rol: ${state.role}</div>`;
  if(state.role==='super') superControls.classList.remove('hidden'); else superControls.classList.add('hidden');
}

// admin controls
btnAddAdmin.addEventListener('click', async ()=>{
  if(!state.token) return alert('Kiring');
  const login = newAdminLogin.value.trim(), pass = newAdminPass.value.trim();
  if(!login||!pass) return alert('Ikkalasini kiriting');
  const fd = new FormData(); fd.append('username', login); fd.append('password', pass); fd.append('token', state.token);
  const res = await fetch('/api/add_admin', { method:'POST', body: fd });
  if(!res.ok) return alert('Xato admin qo\'shishda');
  alert('Admin qo\'shildi'); newAdminLogin.value=''; newAdminPass.value=''; loadProducts();
});

btnPromote.addEventListener('click', async ()=>{
  const u = prompt('Qaysi adminni superga oshirmoqchisiz (login)'); if(!u) return;
  const fd = new FormData(); fd.append('username', u); fd.append('token', state.token);
  const res = await fetch('/api/promote', { method:'POST', body: fd });
  if(!res.ok) return alert('Xato prom'); alert('Muvaffaqiyat'); loadProducts();
});

// export/import
btnExport.addEventListener('click', async ()=>{
  if(!state.token) return alert('Kiring');
  const res = await fetch(`/api/export?token=${encodeURIComponent(state.token)}`);
  if(!res.ok) return alert('Export xato');
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = `korxona_export_${Date.now()}.json`; a.click();
  URL.revokeObjectURL(url);
});

importFile.addEventListener('change', async ()=>{
  if(!state.token) return alert('Kiring');
  const f = importFile.files[0]; if(!f) return;
  const fd = new FormData(); fd.append('file', f); fd.append('token', state.token);
  const res = await fetch('/api/import', { method:'POST', body: fd });
  if(!res.ok) return alert('Import xato');
  alert('Import qilindi'); loadProducts();
});

// history load
async function loadHistory(){
  if(state.role!=='super') return;
  const res = await fetch(`/api/history?token=${encodeURIComponent(state.token)}`);
  if(!res.ok) return;
  const arr = await res.json();
  changeHistory.innerHTML = arr.map(h=>`<div><strong>${escapeHtml(h.user)}</strong> — ${escapeHtml(h.action)} <div class="small">${escapeHtml(h.ts)}</div></div>`).join('');
}
setInterval(()=>{ if(state.role==='super') loadHistory(); }, 5000);
//salol
