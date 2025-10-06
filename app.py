from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
import sqlite3, os, json, datetime

app = Flask(__name__)
app.secret_key = 'korxona_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_NAME = 'korxona.db'

# --- Dastlabki bazani yaratish ---
def init_db():
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        # Foydalanuvchilar jadvali
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            password TEXT,
            role TEXT
        )''')
        # Mahsulotlar jadvali
        cur.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            image TEXT,
            note TEXT
        )''')
        # Tarix jadvali
        cur.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            action TEXT,
            time TEXT
        )''')
        # Superadmin mavjudligini tekshirish
        cur.execute("SELECT * FROM users WHERE login='superadmin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
                        ('superadmin', 'emaktab', 'superadmin'))
            print("✅ Superadmin yaratildi (login: superadmin, parol: emaktab)")
        con.commit()

init_db()

# --- Foydalanuvchini tekshirish ---
def check_user(login, password):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE login=? AND password=?", (login, password))
        return cur.fetchone()

# --- Harakat tarixini yozish ---
def add_history(user, action):
    try:
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO history (user, action, time) VALUES (?, ?, ?)",
                        (user, action, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            con.commit()
    except Exception as e:
        print("❌ Tarix yozishda xato:", e)

# --- Asosiy sahifa ---
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# --- Login sahifasi ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = check_user(login, password)
        if user:
            session['user'] = {'login': user[1], 'role': user[3]}
            add_history(user[1], "Tizimga kirdi")
            flash("Xush kelibsiz!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login yoki parol xato!", "danger")
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    if 'user' in session:
        add_history(session['user']['login'], "Tizimdan chiqdi")
        session.pop('user', None)
    return redirect(url_for('login'))

# --- Dashboard (asosiy sahifa) ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
    return render_template('dashboard.html', products=products, user=session['user'])

# --- Mahsulot qo‘shish ---
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        note = request.form['note']
        image = request.files.get('image')
        filename = None
        if image and image.filename:
            filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + image.filename
            image.save(os.path.join(UPLOAD_FOLDER, filename))
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO products (name, price, image, note) VALUES (?, ?, ?, ?)",
                        (name, price, filename, note))
            con.commit()
        add_history(session['user']['login'], f"Mahsulot qo‘shdi: {name}")
        flash("✅ Mahsulot muvaffaqiyatli qo‘shildi!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add.html', user=session['user'])

# --- Tarix sahifasi ---
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM history ORDER BY id DESC")
        records = cur.fetchall()
    return render_template('history.html', records=records, user=session['user'])

# --- Export (faqat superadmin) ---
@app.route('/export')
def export_data():
    if 'user' not in session or session['user']['role'] != 'superadmin':
        flash("❌ Faqat superadmin bu bo‘limdan foydalana oladi!", "danger")
        return redirect(url_for('dashboard'))
    with sqlite3.connect(DB_NAME) as con:
        data = {}
        for table in ['users', 'products', 'history']:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {table}")
            data[table] = cur.fetchall()
    filename = 'export.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    add_history(session['user']['login'], "Ma’lumotlar eksport qilindi")
    return send_file(filename, as_attachment=True)

# --- Import (faqat superadmin) ---
@app.route('/import', methods=['POST'])
def import_data():
    if 'user' not in session or session['user']['role'] != 'superadmin':
        flash("❌ Ruxsat yo‘q!", "danger")
        return redirect(url_for('dashboard'))
    file = request.files['file']
    data = json.load(file)
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        for table, rows in data.items():
            for row in rows:
                if table == 'users':
                    cur.execute("INSERT OR IGNORE INTO users (id, login, password, role) VALUES (?, ?, ?, ?)", row)
                elif table == 'products':
                    cur.execute("INSERT INTO products (id, name, price, image, note) VALUES (?, ?, ?, ?, ?)", row)
                elif table == 'history':
                    cur.execute("INSERT INTO history (id, user, action, time) VALUES (?, ?, ?, ?)", row)
        con.commit()
    add_history(session['user']['login'], "Ma’lumotlar import qilindi")
    flash("✅ Ma’lumotlar import qilindi!", "success")
    return redirect(url_for('dashboard'))

# --- Flaskni ishga tushirish ---
if __name__ == '__main__':
    print("🚀 Korxona mini-app ishga tushdi: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)