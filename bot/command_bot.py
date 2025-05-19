# ─────── Telegram Bot Komutları ───────
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from scraper.trendyol import get_trendyol_data
from db.database import (
    add_product,
    init_db,
    insert_price,
    get_all_products,
    get_last_price_entry,
    get_price_history,
)
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

# Flask kısmı → sahte port için
import threading
from flask import Flask

# Telegram bot token
TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"  

# ─────── Komutlar ───────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Trendyol ürünlerini takip etmek için /yardım yaz.")

async def yardım(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📋 *Komutlar:*\n"
        "/ekle <url> - Yeni ürün ekle\n"
        "/fiyatlar - Tüm ürünleri listele\n"
        "/grafik <id> - Fiyat grafiğini gönderir\n"
        "/yardım - Yardım menüsü"
    )
    await update.message.reply_markdown(msg)

async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Lütfen bir Trendyol linki gir: `/ekle <url>`", parse_mode="Markdown")
        return

    url = context.args[0]
    try:
        data = get_trendyol_data(url)
        title = data["title"]
        price = data["price"]
        product_id = add_product(title, url)
        insert_price(product_id, price)

        await update.message.reply_text(
            f"✅ Ürün eklendi: *{title}*\n💸 İlk Fiyat: `{price}`\n(ID: {product_id})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ürün eklenemedi: {str(e)}")

async def fiyatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()
    if not products:
        await update.message.reply_text("Henüz hiç ürün yok.")
        return

    msg = "📦 *Takip Edilen Ürünler:*\n"
    for prod in products:
        last_price = get_last_price_entry(prod[0]) or "?"
        msg += f"🔹 ID: `{prod[0]}`\n📄 {prod[1]}\n💸 Fiyat: `{last_price}`\n\n"

    await update.message.reply_markdown(msg)

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Kullanım: `/grafik <id>`", parse_mode="Markdown")
        return

    try:
        product_id = int(context.args[0])
        history = get_price_history(product_id)

        if not history or len(history) < 2:
            await update.message.reply_text("⚠️ Bu ürün için yeterli fiyat verisi yok.")
            return

        dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in history]
        prices = [int(row[1].replace(" TL", "").replace("₺", "").replace(".", "").replace(",", "")) for row in history]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, prices, marker='o', linewidth=2)
        plt.title(f"Ürün #{product_id} Fiyat Geçmişi")
        plt.xlabel("Tarih")
        plt.ylabel("Fiyat (₺)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await update.message.reply_photo(photo=buf)

    except ValueError:
        await update.message.reply_text("❌ Geçersiz ID girdin.")
    except Exception as e:
        await update.message.reply_text(f"❌ Grafik oluşturulamadı: {str(e)}")

# ─────── Uygulama Başlatıcı ───────

def run_bot():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardım", yardım))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("fiyatlar", fiyatlar))
    app.add_handler(CommandHandler("grafik", grafik))

    print("🚀 Telegram komut sistemi başlatıldı.")

    async def set_commands():
        await app.bot.set_my_commands([
            BotCommand("start", "Botu başlat"),
            BotCommand("yardım", "Komut listesini göster"),
            BotCommand("ekle", "Ürün ekle"),
            BotCommand("fiyatlar", "Ürünleri listele"),
            BotCommand("grafik", "Fiyat grafiği göster")
        ])

    import asyncio
    asyncio.run(set_commands())
    app.run_polling()

# ─────── Flask (sahte port açıcı) ───────

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot çalışıyor."

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# ─────── Ana Giriş ───────

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
