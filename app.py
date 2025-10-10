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
if name == '__main__':
    print("🚀 Korxona mini-app ishga tushdi: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)
