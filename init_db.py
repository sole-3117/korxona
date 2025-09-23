import sqlite3

# bazani ochamiz (agar bo'lmasa, yangisini yaratadi)
conn = sqlite3.connect("data.db")
c = conn.cursor()

# foydalanuvchilar jadvali
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# mahsulotlar jadvali
c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image TEXT
)
""")

# 🔑 Super adminni avtomatik qo‘shamiz
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)",
          ("superadmin", "02062008solejon", "super_admin"))

conn.commit()
conn.close()

print("✅ Database yaratildi va superadmin qo‘shildi!")
