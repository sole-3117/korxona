from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3, os, json, datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "database.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # foydalanuvchilar
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('admin','superadmin'))
    )''')
    # mahsulotlar
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT,
        note TEXT,
        updated_at TEXT,
        updated_by TEXT
    )''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = {"id": user[0], "username": user[1], "role": user[3]}
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Login yoki parol noto‘g‘ri")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id DESC")
    products = c.fetchall()
    conn.close()
    return render_template("index.html", products=products, user=session["user"])

@app.route("/add", methods=["GET","POST"])
def add_product():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        note = request.form["note"]
        image = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename:
                filepath = os.path.join("static/uploads", file.filename)
                file.save(filepath)
                image = filepath

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO products (name,price,image,note,updated_at,updated_by) VALUES (?,?,?,?,?,?)",
                  (name, price, image, note, datetime.datetime.now().isoformat(), session["user"]["username"]))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return render_template("add.html")

@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name,updated_at,updated_by FROM products ORDER BY updated_at DESC")
    history = c.fetchall()
    conn.close()
    return render_template("history.html", history=history)

@app.route("/export")
def export():
    if "user" not in session or session["user"]["role"] != "superadmin":
        return "Ruxsat yo‘q"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    data = c.fetchall()
    conn.close()
    with open("export.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    return send_file("export.json", as_attachment=True)

@app.route("/import", methods=["POST"])
def import_data():
    if "user" not in session or session["user"]["role"] != "superadmin":
        return "Ruxsat yo‘q"
    file = request.files["file"]
    if file:
        data = json.load(file)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for row in data:
            c.execute("INSERT INTO products (id,name,price,image,note,updated_at,updated_by) VALUES (?,?,?,?,?,?,?)", row)
        conn.commit()
        conn.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    os.makedirs("static/uploads", exist_ok=True)
    init_db()
    app.run(host="0.0.0.0", port=5000)