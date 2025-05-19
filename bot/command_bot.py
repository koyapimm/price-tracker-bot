from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from db.database import init_db, add_product, get_all_products

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hoş geldin! Komutlar için /yardim yazabilirsin.")

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Botu başlatır"
        "/yardim - Yardım menüsü"
        "/ekle <url> - Ürün ekler"
        "/fiyatlar - Eklenen ürünleri listeler"
    )

async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Lütfen bir ürün URL'si gir.")
        return

    url = context.args[0]
    title = "Ürün Başlığı"  # Dummy
    product_id = add_product(title, url)
    await update.message.reply_text(f"✅ Ürün eklendi. ID: {product_id}")

async def fiyatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()
    if not products:
        await update.message.reply_text("Henüz ürün eklenmemiş.")
        return

    text = "".join([f"{p[0]} - {p[1]}" for p in products])
    await update.message.reply_text(text)

async def run():
    print("🔥 Başlatılıyor...")
    print("⚙️ run_bot fonksiyonu başlatıldı.")
    print(f"🔑 TOKEN (ilk 10 karakter): {TOKEN[:10] if TOKEN else 'YOK'}")

    if not TOKEN:
        print("❌ [HATA] TOKEN environment değişkeni alınamadı!")
        return

    init_db()
    print("📦 DB başlatıldı.")

    app = ApplicationBuilder().token(TOKEN).build()
    print("✅ ApplicationBuilder tamam.")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("fiyatlar", fiyatlar))

    print("🔧 Komutlar eklendi.")

    await app.initialize()
    print("🔧 initialize tamamlandı.")

    await app.start()
    print("✅ Telegram bot çalışıyor.")

    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
