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

# === Flask Uygulaması ===
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bot aktif 👋"

# === Telegram Bot Token ===
TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"  

# === Komut Fonksiyonları ===
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

async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Lütfen bir Trendyol ürün linki gir: /ekle <url>")
        return

    url = context.args[0]
    try:
        data = get_trendyol_data(url)
        title = data["title"]
        price = data["price"]
        product_id = add_product(title, url)
        insert_price(product_id, price)

        await update.message.reply_text(
            f"✅ Ürün eklendi:\n🛒 {title}\n💸 {price}\n🆔 ID: {product_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ürün eklenemedi: {str(e)}")

async def fiyatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()
    if not products:
        await update.message.reply_text("Henüz hiç ürün yok.")
        return

    msg = ""
    for prod in products:
        price = get_last_price_entry(prod[0]) or "?"
        msg += f"🆔 {prod[0]}\n📄 {prod[1]}\n💸 {price}\n\n"

    await update.message.reply_text(msg.strip())

# === Botu Asenkron Olarak Başlat ===
async def run_bot():
    print("⚙️ Telegram bot başlatılıyor...")
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("fiyatlar", fiyatlar))

    await app.bot.set_my_commands([
        BotCommand("start", "Botu başlat"),
        BotCommand("yardim", "Komutları göster"),
        BotCommand("ekle", "Ürün ekle"),
        BotCommand("fiyatlar", "Ürünleri listele")
    ])

    await app.initialize()
    await app.start()
    print("✅ Telegram bot çalışıyor.")
    await asyncio.Event().wait()  # sonsuza kadar çalış

# === Ana Giriş Noktası ===
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    flask_app.run(host="0.0.0.0", port=10000)
