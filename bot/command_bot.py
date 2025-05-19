from dotenv import load_dotenv
load_dotenv()

import os
TOKEN = os.getenv("TOKEN")
import sys
import asyncio
from flask import Flask
from threading import Thread

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from scraper.trendyol import get_trendyol_data
from db.database import (
    init_db,
    add_product,
    insert_price,
    get_all_products,
    get_last_price_entry,
    get_price_history,
)

# === Flask server (Render için port açma)
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "✅ Bot aktif. Render port görüyor."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# === Telegram Bot ===
TOKEN = os.getenv("TOKEN")  # Environment variable olarak ayarlanmalı!

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hoş geldin! /yardim komutunu kullanabilirsin.")

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Başlat\n"
        "/yardim - Yardım menüsü\n"
        "/ekle <url> - Ürün ekle\n"
        "/fiyatlar - Listele\n"
        "/grafik <id> - Fiyat grafiği"
    )

async def run_bot():
    print("⚙️ Telegram bot başlatılıyor...")
    init_db()

    if not TOKEN:
        print("❌ TOKEN çevre değişkeni olarak alınamadı.")
    else:
        print(f"🎯 TOKEN yüklendi: {TOKEN[:8]}... (gizlendi)")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))

    await app.bot.set_my_commands([
        BotCommand("start", "Botu başlat"),
        BotCommand("yardim", "Yardım menüsü"),
    ])

    await app.initialize()
    print("🔧 initialize tamamlandı.")

    await app.start()
    print("✅ Telegram bot çalışıyor.")
    await asyncio.Event().wait()

# === Giriş Noktası ===
if __name__ == "__main__":
    # Flask'ı ayrı thread'de başlat
    Thread(target=run_flask).start()

    # Telegram botu çalıştır
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"[BOT HATASI]: {e}")
