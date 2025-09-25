import sqlite3

# Baza nomi
DB_NAME = "data.db"

# Baza yaratish
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# 🔹 Foydalanuvchilar jadvali
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# 🔹 Mahsulotlar jadvali
c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image TEXT
)
""")

# 🔹 Buyurtmalar jadvali (keyinchalik kerak bo‘ladi)
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    total_price REAL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# 🔑 Super admin qo‘shamiz (agar mavjud bo‘lmasa)
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)",
          ("superadmin", "emaktab", "super_admin"))

conn.commit()
conn.close()

print("✅ Database yaratildi va superadmin qo‘shildi!")