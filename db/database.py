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

def get_all_products():
    conn = sqlite3.connect("price_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows
