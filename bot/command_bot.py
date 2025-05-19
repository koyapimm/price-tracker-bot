import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db.database import init_db, add_product, get_all_products

# === Flask app ===
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "✅ Bot aktif. Render port görüyor."

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render için gerekli
    flask_app.run(host="0.0.0.0", port=port)

# === Telegram Bot ===
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hoş geldin! Komutlar için /yardim yaz.")

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Başlat\n"
        "/yardim - Yardım menüsü\n"
        "/ekle <url> - Ürün ekle\n"
        "/fiyatlar - Listele\n"
        "/grafik <id> - Grafik göster"
    )

async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗️ Lütfen bir URL gir.")
        return

    url = context.args[0]
    title = f"Ürün Başlığı"  # Dummy
    product_id = add_product(title, url)
    await update.message.reply_text(f"✅ Ürün eklendi! ID: {product_id}")

async def fiyatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()
    if not products:
        await update.message.reply_text("Henüz ürün eklenmemiş.")
        return

    msg = "\n".join([f"{p[0]} - {p[1]}" for p in products])
    await update.message.reply_text(f"📦 Ürünler:\n{msg}")

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Grafik özelliği henüz eklenmedi.")

async def run_bot():
    print("⚙️ Bot başlatılıyor...")
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("fiyatlar", fiyatlar))
    app.add_handler(CommandHandler("grafik", grafik))

    await app.bot.set_my_commands([
        BotCommand("start", "Botu başlat"),
        BotCommand("yardim", "Yardım menüsü"),
        BotCommand("ekle", "Ürün ekle"),
        BotCommand("fiyatlar", "Fiyatları listele"),
        BotCommand("grafik", "Fiyat grafiği"),
    ])

    await app.initialize()
    await app.start()
    print("✅ Telegram bot çalışıyor.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("🔥 Başlatılıyor...")
    Thread(target=run_flask).start()
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"[BOT HATASI]: {e}")
        print("❌ Bot başlatılamadı.")