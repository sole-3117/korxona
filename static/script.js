// script.js
// Korxona mini app frontend logic
// Configure backend URL here (or set via environment when building)
const BACKEND_URL = (function(){
  // Replace with your backend URL or keep as placeholder (the user should edit after deploy)
  return localStorage.getItem('BACKEND_URL') || prompt('Enter BACKEND_URL (e.g. https://your-backend.onrender.com):', 'https://your-backend.onrender.com');
})();

if(!BACKEND_URL){
  alert('BACKEND_URL kerak. Admin bilan bog\'laning.');
}

// --- state
let APP = { version: '0.2.2025', products: [], users: {}, changeHistory: [] };
let CURRENT_USER = null;

// --- dom refs
const views = {
  login: document.getElementById('view-login'),
  search: document.getElementById('view-search'),
  add: document.getElementById('view-add'),
  profile: document.getElementById('view-profile')
};
const navSearch = document.getElementById('nav-search');
const navAdd = document.getElementById('nav-add');
const navProfile = document.getElementById('nav-profile');

const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const searchImagePlaceholder = document.getElementById('search-image-placeholder');

const addName = document.getElementById('add-name');
const addPrice = document.getElementById('add-price');
const addImage = document.getElementById('add-image');
const addNote = document.getElementById('add-note');

const loginLogin = document.getElementById('login-login');
const loginPass = document.getElementById('login-pass');
const btnLogin = document.getElementById('btn-login');
const btnDemo = document.getElementById('btn-demo');

const profileUsername = document.getElementById('profile-username');
const currentUserBadge = document.getElementById('currentUser');
const btnLogout = document.getElementById('btn-logout');

const btnAdd = document.getElementById('btn-add');
const btnClearForm = document.getElementById('btn-clear-form');

const btnExport = document.getElementById('btn-export');
const btnImport = document.getElementById('btn-import');
const adminControls = document.getElementById('admin-controls');
const btnAddAdmin = document.getElementById('btn-add-admin');
const btnPromoteAdmin = document.getElementById('btn-promote-admin');
const newAdminLogin = document.getElementById('new-admin-login');
const newAdminPass = document.getElementById('new-admin-pass');
const changeHistoryEl = document.getElementById('change-history');

const themeToggle = document.getElementById('theme-toggle');

// navigation
navSearch.addEventListener('click', ()=> showView('search'));
navAdd.addEventListener('click', ()=> showView('add'));
navProfile.addEventListener('click', ()=> showView('profile'));

function showView(name){
  Object.values(views).forEach(v => v.classList.remove('active'));
  views[name].classList.add('active');
  [navSearch, navAdd, navProfile].forEach(b => b.classList.remove('active'));
  if(name==='search') navSearch.classList.add('active');
  if(name==='add') navAdd.classList.add('active');
  if(name==='profile') navProfile.classList.add('active');
}

// theme
(function initTheme(){
  const t = localStorage.getItem('theme') || 'dark';
  if(t==='dark') document.body.classList.add('dark');
  themeToggle.textContent = (t==='dark') ? '🌙' : '☀️';
})();
themeToggle.addEventListener('click', ()=>{
  document.body.classList.toggle('dark');
  const isDark = document.body.classList.contains('dark');
  themeToggle.textContent = isDark ? '🌙' : '☀️';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// util
function genId(){ return 'p_' + Date.now() + '_' + Math.floor(Math.random()*1000) }
function escapeHtml(s=''){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// load data from backend
async function loadFromBackend(){
  try{
    const r = await fetch(`${BACKEND_URL}/api/data`);
    if(!r.ok) throw new Error('server error');
    APP = await r.json();
    renderProducts(APP.products || []);
    renderHistory();
  }catch(e){
    console.warn('Backend load failed, using localStorage fallback', e);
    // fallback to localStorage
    const raw = localStorage.getItem('korxona_demo');
    if(raw) APP = JSON.parse(raw);
    renderProducts(APP.products || []);
    renderHistory();
  }
}
loadFromBackend();

// render
function renderProducts(list){
  searchResults.innerHTML = '';
  if(!list || !list.length){
    searchResults.innerHTML = `<div class="card small">Mahsulot topilmadi</div>`;
    return;
  }
  list.forEach(p=>{
    const el = document.createElement('div');
    el.className='item';
    el.innerHTML = `
      <div class="thumb">${p.image ? `<img src="${p.image}" style="width:100%;height:100%;object-fit:cover;border-radius:8px" />` : 'Rasm'}</div>
      <div class="meta">
        <div class="title">${escapeHtml(p.name)}</div>
        <div class="price">${p.price ? (escapeHtml(p.price) + ' so\'m') : '—'}</div>
        <div class="note">${escapeHtml(p.note || '')}</div>
      </div>
      <div class="actions">
        <button class="open-btn">Ochish</button>
        ${ (CURRENT_USER && CURRENT_USER.role === 'super') ? '<button class="delete-btn ghost">Oʻchirish</button>' : '' }
      </div>
    `;
    // attach
    el.querySelector('.open-btn').addEventListener('click', ()=> viewProduct(p.id));
    const delBtn = el.querySelector('.delete-btn');
    if(delBtn){
      delBtn.addEventListener('click', ()=> deleteProduct(p.id));
    }
    searchResults.appendChild(el);
  });
}

// search
searchInput.addEventListener('input', e=>{
  const q = (e.target.value || '').toLowerCase().trim();
  const filtered = (APP.products||[]).filter(p => p.name.toLowerCase().includes(q));
  renderProducts(filtered);
});

// view product
function viewProduct(id){
  const p = (APP.products||[]).find(x=>x.id===id);
  if(!p) return alert('Mahsulot topilmadi');
  if(p.image) searchImagePlaceholder.innerHTML = `<img src="${p.image}" style="max-width:100%;max-height:150px;object-fit:cover" />`;
  else searchImagePlaceholder.innerHTML = 'Rasm yoʻq';
  searchInput.value = p.name;
  renderProducts([p]);
  showView('search');
  // If current user can edit, show edit form modal (simple prompt for demo)
  if(CURRENT_USER && (CURRENT_USER.role === 'super' || CURRENT_USER.role === 'admin')){
    const doEdit = confirm('Mahsulotni tahrirlashni xohlaysizmi?');
    if(doEdit){
      const newName = prompt('Yangi nom', p.name) || p.name;
      const newPrice = prompt('Yangi narx (soʻm)', p.price || '') || p.price;
      const newNote = prompt('Yangi eslatma', p.note || '') || p.note;
      p.name = newName; p.price = newPrice; p.note = newNote;
      APP.changeHistory = APP.changeHistory || [];
      APP.changeHistory.push({at: Date.now(), by: CURRENT_USER.user, action: `edit product ${p.id}`});
      saveToBackend();
      renderProducts(APP.products);
    }
  }
}

// delete (super only)
function deleteProduct(id){
  if(!(CURRENT_USER && CURRENT_USER.role === 'super')) return alert('Faqat super admin o\'chirishi mumkin');
  if(!confirm('Haqiqatan o\'chirmoqchimisiz?')) return;
  APP.products = (APP.products||[]).filter(p=>p.id!==id);
  APP.changeHistory = APP.changeHistory || [];
  APP.changeHistory.push({at: Date.now(), by: CURRENT_USER.user, action: `delete product ${id}`});
  saveToBackend();
  renderProducts(APP.products);
}

// add product
btnAdd.addEventListener('click', async ()=>{
  if(!(CURRENT_USER && (CURRENT_USER.role==='admin' || CURRENT_USER.role==='super'))){
    return alert('Mahsulot qo\'shish uchun kirish kerak');
  }
  const name = (addName.value||'').trim();
  const price = (addPrice.value||'').trim();
  if(!name || !price) return alert('Nomi va narxi majburiy');
  const note = addNote.value || '';
  let imageData = null;
  const file = addImage.files && addImage.files[0];
  if(file){
    imageData = await readFileAsDataURL(file);
  }
  const p = { id: genId(), name, price, note, image: imageData, createdAt: Date.now() };
  APP.products = APP.products || [];
  APP.products.unshift(p);
  APP.changeHistory = APP.changeHistory || [];
  APP.changeHistory.push({at: Date.now(), by: CURRENT_USER.user, action: `add product ${p.id}`});
  saveToBackend();
  renderProducts(APP.products);
  clearAddForm();
  alert('Mahsulot qo\'shildi');
});
btnClearForm.addEventListener('click', clearAddForm);
function clearAddForm(){ addName.value=''; addPrice.value=''; addNote.value=''; addImage.value=''; }

// read file to base64
function readFileAsDataURL(file){
  return new Promise((res, rej)=>{
    const fr = new FileReader();
    fr.onload = ()=> res(fr.result);
    fr.onerror = rej;
    fr.readAsDataURL(file);
  });
}

// login logic (local check via backend users)
btnLogin.addEventListener('click', async ()=>{
  const user = (loginLogin.value||'').trim();
  const pass = (loginPass.value||'').trim();
  if(!user || !pass) return alert('Login va parol kiriting');
  // check against APP.users
  try{
    // reload latest users from backend
    const r = await fetch(`${BACKEND_URL}/api/data`);
    const d = await r.json();
    const users = d.users || {};
    if(!users[user]) return alert('Bunday foydalanuvchi yo\'q');
    if(users[user].password !== pass) return alert('Parol xato');
    CURRENT_USER = { user, role: users[user].role || 'admin' };
    APP = d; // sync
    APP.changeHistory = APP.changeHistory || [];
    APP.changeHistory.push({at: Date.now(), by: user, action: 'login'});
    // notify server to save history via merge
    await saveToBackend(true);
    updateProfileUI();
    showView('search');
  }catch(e){
    alert('Kirishda xatolik: ' + e.message);
  }
});

// demo local login (for quick start in dev)
btnDemo.addEventListener('click', ()=>{
  // create demo superadmin in local APP
  APP.users = APP.users || {};
  APP.users['superadmin'] = APP.users['superadmin'] || {password: 'superpass', role: 'super'};
  CURRENT_USER = { user: 'superadmin', role: 'super' };
  updateProfileUI();
  showView('search');
  renderProducts(APP.products||[]);
});

// logout
btnLogout.addEventListener('click', ()=>{
  CURRENT_USER = null;
  updateProfileUI();
  showView('login');
});

// update UI
function updateProfileUI(){
  if(CURRENT_USER){
    profileUsername.textContent = `${CURRENT_USER.user} (${CURRENT_USER.role})`;
    currentUserBadge.textContent = CURRENT_USER.user;
    if(CURRENT_USER.role === 'super'){
      adminControls.classList.remove('hidden');
    } else {
      adminControls.classList.add('hidden');
    }
  } else {
    profileUsername.textContent = 'Kirish yo\'q';
    currentUserBadge.textContent = 'Kirish yo\'q';
    adminControls.classList.add('hidden');
  }
}

// export: call backend /api/export?chat_id=...
btnExport.addEventListener('click', async ()=>{
  if(!CURRENT_USER) return alert('Kirish qiling');
  // Ask user to provide their Telegram chat_id so backend can send via bot
  const chatId = prompt('Telegram chat ID ni kiriting (bot sizga fayl yuborishi uchun). Agar bilmasangiz, botga /start yuboring va chat IDni admindan oling.', '');
  if(!chatId) return alert('chat_id kerak');
  try{
    const r = await fetch(`${BACKEND_URL}/api/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ }) // endpoint accepts optional chat_id via query, we send as query param below
    });
    // If backend sendFile to telegram is desired, call endpoint with ?chat_id=
    const r2 = await fetch(`${BACKEND_URL}/api/export?chat_id=${encodeURIComponent(chatId)}`, { method: 'POST' });
    const res = await r2.json();
    if(res.sent_to_chat){
      alert('Fayl bot orqali yuborildi. Telegramni tekshiring.');
    } else {
      alert('Fayl yaratildi: ' + (res.file || 'unknown') + '\nAgar kerak bo\'lsa admindan so\'rang.');
    }
  }catch(e){
    alert('Export xatolik: ' + e);
  }
});

// import: instruct user to send exported .json to bot as document
btnImport.addEventListener('click', ()=>{
  alert("Import qilish uchun: eksport qilingan .json faylni Telegram botga yuboring. Bot faylni qabul qilib backendga import qiladi.");
});

// admin add
btnAddAdmin.addEventListener('click', async ()=>{
  if(!(CURRENT_USER && CURRENT_USER.role === 'super')) return alert('Faqat super admin');
  const login = (newAdminLogin.value||'').trim();
  const pass = (newAdminPass.value||'').trim();
  if(!login || !pass) return alert('Login va parol kiriting');
  // Add user via merge: fetch data, modify users and post back via /api/data
  try{
    const r = await fetch(`${BACKEND_URL}/api/data`);
    const d = await r.json();
    d.users = d.users || {};
    d.users[login] = {password: pass, role: 'admin'};
    // call POST /api/data with merge
    d.mode = 'merge';
    const rep = await fetch(`${BACKEND_URL}/api/data`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(d)
    });
    if(rep.ok){
      alert('Admin qo\'shildi');
      await loadFromBackend();
    } else alert('Xatolik admin qo\'shishda');
  }catch(e){
    alert('Xatolik: ' + e);
  }
});

// promote admin -> super
btnPromoteAdmin.addEventListener('click', async ()=>{
  if(!(CURRENT_USER && CURRENT_USER.role === 'super')) return alert('Faqat super admin');
  const login = prompt('Qaysi adminni superga oshirmoqchisiz? (login kiriting)');
  if(!login) return;
  try{
    const r = await fetch(`${BACKEND_URL}/api/data`);
    const d = await r.json();
    if(!d.users || !d.users[login]) return alert('Bunday foydalanuvchi yo\'q');
    d.users[login].role = 'super';
    d.mode = 'merge';
    const rep = await fetch(`${BACKEND_URL}/api/data`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(d)
    });
    if(rep.ok){
      alert('Muvaffaqiyatli oshirildi');
      await loadFromBackend();
    } else alert('Xatolik');
  }catch(e){
    alert('Xatolik: ' + e);
  }
});

// render history
function renderHistory(){
  const list = (APP.changeHistory || []).slice().reverse();
  changeHistoryEl.innerHTML = '';
  if(!list.length){ changeHistoryEl.innerHTML = '<div class="small">Hozircha o\'zgarishlar yo\'q</div>'; return; }
  list.forEach(h=>{
    const date = new Date(h.at || Date.now()).toLocaleString();
    const div = document.createElement('div');
    div.innerHTML = `<div style="padding:6px;border-bottom:1px dashed #eee"><strong>${escapeHtml(h.by)}</strong> — ${escapeHtml(h.action)} <div class="small">${date}</div></div>`;
    changeHistoryEl.appendChild(div);
  });
}

// save to backend (mode merge)
async function saveToBackend(skipReload=false){
  try{
    const payload = JSON.parse(JSON.stringify(APP));
    payload.mode = 'merge';
    const r = await fetch(`${BACKEND_URL}/api/data`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if(!r.ok) throw new Error('save failed');
    if(!skipReload) await loadFromBackend();
    localStorage.setItem('korxona_demo', JSON.stringify(APP));
  }catch(e){
    console.warn('Save failed, saving local only', e);
    localStorage.setItem('korxona_demo', JSON.stringify(APP));
  }
}

// initial UI
updateProfileUI();
showView('login');
