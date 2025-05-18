import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            hash TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()

def hash_url(url: str):
    return hashlib.sha256(url.encode()).hexdigest()

def add_product(title, url):
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    url_hash = hash_url(url)

    cursor.execute("SELECT id FROM products WHERE hash = ?", (url_hash,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute("INSERT INTO products (title, url, hash) VALUES (?, ?, ?)", (title, url, url_hash))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def insert_price(product_id, price):
    import sqlite3
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()

    cursor.execute("SELECT price FROM prices WHERE product_id = ? ORDER BY date DESC LIMIT 1", (product_id,))
    last = cursor.fetchone()

    print(f"[DEBUG] DB'deki son fiyat: {last[0] if last else 'YOK'} - Yeni fiyat: {price}")

    if last and last[0] == price:
        print(f"[SKIP] Fiyat zaten aynı ({price}), kayıt yapılmadı.")
        conn.close()
        return False

    cursor.execute("INSERT INTO prices (product_id, price) VALUES (?, ?)", (product_id, price))
    conn.commit()
    conn.close()
    print(f"[DB] Yeni fiyat kaydedildi: {price}")
    return True



def get_all_products():
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_price_history(product_id):
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, price FROM prices WHERE product_id = ? ORDER BY date", (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_last_two_prices(product_id):
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM prices WHERE product_id = ? ORDER BY date DESC LIMIT 2", (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows] if len(rows) == 2 else None

def get_last_price_entry(product_id):
    import sqlite3
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM prices WHERE product_id = ? ORDER BY date DESC LIMIT 1", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None