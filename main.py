import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template_string, request, redirect, url_for,
    flash, session, send_from_directory, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json

# --- Konfiguratsiya ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "change_this_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(BASE_DIR, "app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB limit

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --- Modelar ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="admin")  # 'super_admin' yoki 'admin'

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    info = db.Column(db.Text, default="")
    image = db.Column(db.String(300), default="")  # filename
    created_by = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(150))
    action = db.Column(db.String(100))  # Qo'shdi / O'zgartirdi / O'chirdi / Import / Export
    details = db.Column(db.Text)  # eski -> yangi yoki item json

# --- Login loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Role decorator ---
def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role_name:
                flash("Sizda bu amalni bajarish huquqi yo'q.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# --- Yordamchi funktsiyalar ---
def save_log(user, action, details):
    l = Log(user=user, action=action, details=details)
    db.session.add(l)
    db.session.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"png","jpg","jpeg","gif"}

# --- Initial DB yaratish va default super admin ---
@app.before_first_request
def init_db():
    db.create_all()
    # default super admin agar yo'q bo'lsa
    if not User.query.filter_by(role='super_admin').first():
        u = User(username="emaktab", role="super_admin")
        u.set_password("emaktab")  # iltimos, darhol o'zgartiring!
        db.session.add(u)
        db.session.commit()
        print("Default super_admin yaratildi: emaktab / emaktab")

# --- Shablon (oddiy, bitta fayl ichida) ---
BASE_HTML = """
<!doctype html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <title>Shop Admin v0.1.2025</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; margin:0; padding:0; }
    .top { padding:10px; background: #f5f5f5; display:flex; justify-content:space-between; align-items:center; }
    .dark .top { background:#222; color:#eee; }
    .content { padding:20px; }
    .card { border:1px solid #ddd; padding:10px; margin:10px 0; border-radius:6px; background:#fff; }
    .dark .card { background:#2b2b2b; border-color:#444; color:#eee; }
    .grid { display:flex; gap:10px; flex-wrap:wrap; }
    .product { width:240px; border:1px solid #ccc; padding:8px; border-radius:6px; text-align:center; background:#fff; }
    .dark .product { background:#333; border-color:#444; color:#eee; }
    .imgframe { width:200px; height:140px; border:1px dashed #aaa; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; background:#fafafa; }
    .dark .imgframe { background:#1f1f1f; border-color:#444; }
    .menu { display:flex; gap:8px; }
    a { text-decoration:none; color:inherit; }
    .btn { padding:6px 10px; border-radius:4px; border:1px solid #888; background:#eee; cursor:pointer; display:inline-block; }
    .dark .btn { background:#444; color:#eee; border-color:#666; }
    form.inline { display:flex; gap:6px; }
    table { width:100%; border-collapse:collapse; }
    th,td { border:1px solid #ddd; padding:6px; }
    .small { font-size:12px; color:#666; }
  </style>
</head>
<body class="{{ 'dark' if dark else '' }}">
  <div class="top">
    <div>
      <strong>Shop Admin v0.1.2025</strong>
      {% if current_user.is_authenticated %}
        — {{ current_user.username }} ({{ current_user.role }})
      {% endif %}
    </div>
    <div class="menu">
      <a href="{{ url_for('index') }}" class="btn">🔍 Qidiruv</a>
      <a href="{{ url_for('add_product') }}" class="btn">➕ Mahsulot qo'shish</a>
      <a href="{{ url_for('logs') }}" class="btn">📜 Tarix</a>
      <a href="{{ url_for('profile') }}" class="btn">👤 Profil</a>
      {% if current_user.is_authenticated and current_user.role == 'super_admin' %}
        <a href="{{ url_for('users') }}" class="btn">👥 Adminlar</a>
        <a href="{{ url_for('export_json') }}" class="btn">⬇️ Export (JSON)</a>
        <a href="{{ url_for('import_json') }}" class="btn">⬆️ Import (JSON)</a>
      {% endif %}
      {% if current_user.is_authenticated %}
        <a href="{{ url_for('logout') }}" class="btn">Chiqish</a>
      {% else %}
        <a href="{{ url_for('login') }}" class="btn">Kirish</a>
      {% endif %}
      <a href="{{ url_for('toggle_theme') }}" class="btn">{{ 'Light' if dark else 'Dark' }}</a>
    </div>
  </div>

  <div class="content">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="card"><strong>{{ cat }}:</strong> {{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {{ body|safe }}
  </div>
</body>
</html>
"""

# --- Routes (index, auth, CRUD, logs, users, export/import) ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/toggle_theme')
def toggle_theme():
    session['dark'] = not session.get('dark', False)
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_vars():
    return dict(current_user=current_user, dark=session.get('dark', False))

@app.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    products = []
    if q:
        products = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) | (Product.info.ilike(f"%{q}%"))
        ).order_by(Product.id.desc()).all()
    else:
        products = Product.query.order_by(Product.id.desc()).limit(30).all()
    cards = ""
    for p in products:
        img_html = ""
        if p.image:
            img_html = f'<img src="{url_for("uploaded_file", filename=p.image)}" style="max-width:200px; max-height:140px;">'
        else:
            img_html = '<div class="imgframe">Rasm yo‘q</div>'
        cards += f"""
        <div class="product card">
          {img_html}
          <strong>{p.name}</strong><br>
          <span class="small">{p.price} so‘m</span><br>
          <div class="small">{p.info or ''}</div>
          <div style="margin-top:6px;">
            <a class="btn" href="{url_for('edit_product', pid=p.id)}">✏️ O'zgartirish</a>
            {% if current_user.role == 'super_admin' or current_user.role == 'admin' %}
              <a class="btn" href="{url_for('delete_product', pid=p.id)}" onclick="return confirm('O\\'chirasizmi?')">🗑️ O'chirish</a>
            {% endif %}
          </div>
        </div>
        """
    body = f"""
    <form method="get" class="inline" action="{url_for('index')}">
      <input name="q" placeholder="Qidirish..." style="padding:6px; width:60%;" value="{q}">
      <button class="btn" type="submit">🔍</button>
    </form>
    <div class="grid">{cards or '<div class="card">Mahsulot topilmadi.</div>'}</div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and u.check_password(request.form['password']):
            login_user(u)
            flash("Tizimga muvaffaqiyatli kirdingiz.", "OK")
            return redirect(url_for('index'))
        flash("Login yoki parol xato.", "Xato")
    body = """
    <div class="card">
      <form method="post">
        <div><label>Username</label><br><input name="username"></div>
        <div><label>Parol</label><br><input name="password" type="password"></div>
        <div style="margin-top:8px;"><button class="btn" type="submit">Kirish</button></div>
      </form>
      <div class="small" style="margin-top:8px;">Default super admin: emaktab / emaktab (darhol parolni o'zgartiring)</div>
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Siz tizimdan chiqdingiz.", "OK")
    return redirect(url_for('login'))

@app.route('/add', methods=['GET','POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        price = request.form.get('price','0').strip()
        info = request.form.get('info','').strip()
        if not name:
            flash("Nomi kiriting", "Xato")
            return redirect(url_for('add_product'))
        try:
            price_val = float(price)
        except:
            flash("Narxni to'g'ri kiriting", "Xato")
            return redirect(url_for('add_product'))
        filename = ""
        file = request.files.get('image')
        if file and file.filename != "":
            if allowed_file(file.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Rasm formati ruxsat etilmagan", "Xato")
                return redirect(url_for('add_product'))
        p = Product(name=name, price=price_val, info=info, image=filename, created_by=current_user.username)
        db.session.add(p)
        db.session.commit()
        save_log(current_user.username, "Qo'shdi", json.dumps({
            "id": p.id, "name": p.name, "price": p.price, "info": p.info
        }, ensure_ascii=False))
        flash("Mahsulot qo'shildi", "OK")
        return redirect(url_for('index'))

    body = f"""
    <div class="card">
      <h3>➕ Mahsulot qo'shish</h3>
      <form method="post" enctype="multipart/form-data">
        <div><label>1-qism (majburiy)</label></div>
        <div><input name="name" placeholder="Nomi" required></div>
        <div><input name="price" placeholder="Narxi" required></div>
        <hr>
        <div><label>2-qism (ixtiyoriy)</label></div>
        <div><input type="file" name="image" accept="image/*"></div>
        <div><textarea name="info" placeholder="Eslatma yoki ma'lumot"></textarea></div>
        <div style="margin-top:8px;"><button class="btn" type="submit">Saqlash</button></div>
      </form>
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/edit/<int:pid>', methods=['GET','POST'])
@login_required
def edit_product(pid):
    p = Product.query.get_or_404(pid)
    if request.method == 'POST':
        old = {"name": p.name, "price": p.price, "info": p.info}
        name = request.form.get('name','').strip()
        price = request.form.get('price','0').strip()
        info = request.form.get('info','').strip()
        if not name:
            flash("Nomi kerak", "Xato")
            return redirect(url_for('edit_product', pid=pid))
        try:
            price_val = float(price)
        except:
            flash("Narxni to'g'ri kiriting", "Xato")
            return redirect(url_for('edit_product', pid=pid))
        file = request.files.get('image')
        filename = p.image
        if file and file.filename != "":
            if allowed_file(file.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Rasm formati ruxsat etilmagan", "Xato")
                return redirect(url_for('edit_product', pid=pid))
        p.name = name
        p.price = price_val
        p.info = info
        p.image = filename
        p.updated_at = datetime.utcnow()
        db.session.commit()
        save_log(current_user.username, "O'zgartirdi", json.dumps({
            "id": p.id, "old": old, "new": {"name": p.name, "price": p.price, "info": p.info}
        }, ensure_ascii=False))
        flash("Mahsulot yangilandi", "OK")
        return redirect(url_for('index'))
    body = f"""
    <div class="card">
      <h3>✏️ Mahsulotni tahrirlash</h3>
      <form method="post" enctype="multipart/form-data">
        <div><input name="name" value="{p.name}" required></div>
        <div><input name="price" value="{p.price}" required></div>
        <div><input type="file" name="image" accept="image/*"></div>
        <div><textarea name="info">{p.info or ''}</textarea></div>
        <div style="margin-top:8px;"><button class="btn" type="submit">Yangilash</button></div>
      </form>
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/delete/<int:pid>')
@login_required
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    save_log(current_user.username, "O'chirdi", json.dumps({"id": pid, "name": p.name}, ensure_ascii=False))
    flash("Mahsulot o'chirildi", "OK")
    return redirect(url_for('index'))

@app.route('/logs')
@login_required
def logs():
    q_user = request.args.get('user','').strip()
    q_action = request.args.get('action','').strip()
    query = Log.query.order_by(Log.time.desc())
    if q_user:
        query = query.filter(Log.user.ilike(f"%{q_user}%"))
    if q_action:
        query = query.filter(Log.action.ilike(f"%{q_action}%"))
    rows = query.limit(500).all()
    rows_html = "<table><tr><th>Vaqt</th><th>Foydalanuvchi</th><th>Amal</th><th>Detal</th></tr>"
    for r in rows:
        rows_html += f"<tr><td>{r.time}</td><td>{r.user}</td><td>{r.action}</td><td><pre style='white-space:pre-wrap'>{r.details}</pre></td></tr>"
    rows_html += "</table>"
    body = f"""
    <div class="card"><h3>📜 O'zgarishlar tarixi</h3>
      <form method="get" action="{url_for('logs')}">
        <input name="user" placeholder="Foydalanuvchi" value="{q_user}">
        <input name="action" placeholder="Amal" value="{q_action}">
        <button class="btn" type="submit">Filtrlash</button>
      </form>
      {rows_html}
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/users', methods=['GET','POST'])
@login_required
@role_required('super_admin')
def users():
    if request.method == 'POST':
        uname = request.form.get('username','').strip()
        pwd = request.form.get('password','').strip()
        role = request.form.get('role','admin').strip()
        if not uname or not pwd:
            flash("Username va parol kerak", "Xato")
            return redirect(url_for('users'))
        if User.query.filter_by(username=uname).first():
            flash("Bu username mavjud", "Xato")
            return redirect(url_for('users'))
        u = User(username=uname, role=role)
        u.set_password(pwd)
        db.session.add(u)
        db.session.commit()
        save_log(current_user.username, "Yangi admin yaratdi", f"{uname} as {role}")
        flash("Admin yaratildi", "OK")
        return redirect(url_for('users'))
    allu = User.query.all()
    rows = "<table><tr><th>Username</th><th>Role</th><th>Actions</th></tr>"
    for u in allu:
        rows += f"<tr><td>{u.username}</td><td>{u.role}</td><td>"
        if u.username != current_user.username:
            rows += f'<a class="btn" href="{url_for("delete_user", uid=u.id)}" onclick="return confirm(\'O\\'chirasizmi?\')">O\\'chirish</a>'
        rows += "</td></tr>"
    rows += "</table>"
    body = f"""
    <div class="card">
      <h3>👥 Adminlarni boshqarish</h3>
      <form method="post">
        <div><input name="username" placeholder="username" required></div>
        <div><input name="password" placeholder="parol" required></div>
        <div>
          <select name="role">
            <option value="admin">admin</option>
            <option value="super_admin">super_admin</option>
          </select>
        </div>
        <div style="margin-top:6px;"><button class="btn" type="submit">Yaratish</button></div>
      </form>
      <hr>
      {rows}
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/delete_user/<int:uid>')
@login_required
@role_required('super_admin')
def delete_user(uid):
    u = User.query.get_or_404(uid)
    if u.username == current_user.username:
        flash("O'zingizni o'chira olmaysiz", "Xato")
        return redirect(url_for('users'))
    db.session.delete(u)
    db.session.commit()
    save_log(current_user.username, "Admin o'chirdi", u.username)
    flash("Admin o'chirildi", "OK")
    return redirect(url_for('users'))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        newp = request.form.get('newpass','').strip()
        if not newp:
            flash("Yangi parol kiriting", "Xato")
            return redirect(url_for('profile'))
        current_user.set_password(newp)
        db.session.commit()
        save_log(current_user.username, "Parol o'zgartirdi", "")
        flash("Parol o'zgardi", "OK")
        return redirect(url_for('index'))
    body = f"""
    <div class="card">
      <h3>👤 Profil</h3>
      <div>Username: <strong>{current_user.username}</strong></div>
      <div>Role: <strong>{current_user.role}</strong></div>
      <hr>
      <form method="post">
        <div><input name="newpass" placeholder="Yangi parol" required></div>
        <div style="margin-top:6px;"><button class="btn" type="submit">Parolni o'zgartirish</button></div>
      </form>
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route('/export')
@login_required
@role_required('super_admin')
def export_json():
    products = Product.query.all()
    logs = Log.query.all()
    users = User.query.all()
    data = {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "info": p.info,
                "image": p.image,
                "created_by": p.created_by,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in products
        ],
        "logs": [
            {
                "id": l.id,
                "time": l.time.isoformat(),
                "user": l.user,
                "action": l.action,
                "details": l.details
            } for l in logs
        ],
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role
            } for u in users
        ]
    }
    save_log(current_user.username, "Export", "Export JSON performed")
    return jsonify(data)

@app.route('/import', methods=['GET','POST'])
@login_required
@role_required('super_admin')
def import_json():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash("Fayl kiriting", "Xato")
            return redirect(url_for('import_json'))
        try:
            data = json.load(f)
        except Exception as e:
            flash("Faylni o'qib bo'lmadi: " + str(e), "Xato")
            return redirect(url_for('import_json'))
        # Import products (note: we won't delete existing, we'll add or update by id if exists)
        count = 0
        for pr in data.get('products', []):
            pid = pr.get('id')
            existing = Product.query.filter_by(id=pid).first() if pid else None
            if existing:
                existing.name = pr.get('name', existing.name)
                existing.price = pr.get('price', existing.price)
                existing.info = pr.get('info', existing.info)
                existing.image = pr.get('image', existing.image)
            else:
                newp = Product(
                    name=pr.get('name',''),
                    price=pr.get('price') or 0.0,
                    info=pr.get('info',''),
                    image=pr.get('image',''),
                    created_by=pr.get('created_by') or current_user.username
                )
                db.session.add(newp)
            count += 1
        # Import users (only create if not exists)
        for us in data.get('users', []):
            if not User.query.filter_by(username=us.get('username')).first():
                nu = User(username=us.get('username'), role=us.get('role','admin'))
                nu.set_password("changeme")  # super admin should reset passwords
                db.session.add(nu)
        db.session.commit()
        save_log(current_user.username, "Import", f"Imported {count} products")
        flash(f"Import yakunlandi: {count} item", "OK")
        return redirect(url_for('index'))

    body = """
    <div class="card">
      <h3>⬆️ JSON Import (super admin)</h3>
      <form method="post" enctype="multipart/form-data">
        <div><input type="file" name="file" accept="application/json" required></div>
        <div style="margin-top:6px;"><button class="btn" type="submit">Import</button></div>
      </form>
      <div class="small">Eslatma: import qilinganda mavjud bo‘lgan idlar bo‘yicha yangilanadi, yangi idlar qo‘shiladi.</div>
    </div>
    """
    return render_template_string(BASE_HTML, body=body)

if __name__ == "__main__":
    # For local testing
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))