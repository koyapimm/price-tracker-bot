# ─────── Telegram Bot Komutları ───────
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from flask import Flask
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

from threading import Thread

# === Flask Uygulaması ===
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bot aktif 👋"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# === Telegram Bot Token ===
TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"  

# === Komutlar ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! /yardim yazarak komutları görebilirsin.")

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Botu başlat\n"
        "/yardim - Komutları göster\n"
        "/ekle <url> - Ürün ekle\n"
        "/fiyatlar - Ürünleri listele\n"
        "/grafik <id> - Fiyat grafiği gönder"
    )

async def run_bot():
    print("⚙️ Telegram bot başlatılıyor...")
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))

    await app.bot.set_my_commands([
        BotCommand("start", "Botu başlat"),
        BotCommand("yardim", "Komutları göster"),
    ])

    await app.initialize()
    await app.start()
    print("✅ Telegram bot çalışıyor.")
    await asyncio.Event().wait()

# === Ana giriş ===
if __name__ == "__main__":
    Thread(target=run_flask).start()

    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"[HATA]: {e}")
