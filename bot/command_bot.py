from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scraper.trendyol import get_trendyol_data
from db.database import add_product, init_db, get_last_price_entry, insert_price

from db.database import get_all_products, get_price_history
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"

# Komut: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Bu bot ile Trendyol ürünlerini takip edebilirsin.\nYardım için /yardim yaz.")

# Komut: /yardım
async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *Komutlar:*\n"
        "/ekle <link> - Yeni ürün ekle ve fiyatını takip etmeye başla\n"
        "/fiyatlar - Takip edilen ürünleri listele (yakında)\n"
        "/grafik <id> - Ürün fiyat geçmişi grafiği gönderir (yakında)\n"
        "/yardım - Bu listeyi gösterir"
    )
    await update.message.reply_markdown(text)

async def fiyatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()
    if not products:
        await update.message.reply_text("⚠️ Henüz hiç ürün eklenmemiş.")
        return

    msg = "📦 *Takip Edilen Ürünler:*\n"
    for prod in products:
        last_price = get_last_price_entry(prod[0]) or "?"
        msg += f"🔹 ID: `{prod[0]}`\n📄 {prod[1]}\n💸 Fiyat: `{last_price}`\n\n"
    await update.message.reply_markdown(msg)

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Lütfen bir ürün ID gir: `/grafik <id>`", parse_mode="Markdown")
        return

    try:
        product_id = int(context.args[0])
        history = get_price_history(product_id)

        if not history or len(history) < 2:
            await update.message.reply_text("⚠️ Bu ürün için yeterli fiyat geçmişi yok.")
            return

        # Grafik çizimi
        dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in history]
        prices = [int(row[1].replace(" TL", "").replace("₺", "").replace(".", "").replace(",", "")) for row in history]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, prices, marker='o', linewidth=2)
        plt.title(f"Ürün #{product_id} Fiyat Geçmişi")
        plt.xlabel("Tarih")
        plt.ylabel("Fiyat (₺)")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await update.message.reply_photo(photo=buf)

    except ValueError:
        await update.message.reply_text("❌ Geçersiz ID. Sayı girmen gerekiyor.")
    except Exception as e:
        await update.message.reply_text(f"❌ Grafik oluşturulamadı: {str(e)}")


# Komut: /ekle <trendyol-url>
async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Lütfen bir Trendyol ürün linki gir: `/ekle <link>`", parse_mode="Markdown")
        return

    url = context.args[0]
    try:
        data = get_trendyol_data(url)
        title = data["title"]
        price = data["price"]
        product_id = add_product(title, url)

        insert_price(product_id, price)  # ⬅️ ilk fiyatı kaydet

        await update.message.reply_text(
            f"✅ Ürün eklendi: *{title}*\n💸 İlk Fiyat: `{price}`\n(ID: {product_id})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ürün eklenemedi: {str(e)}")

# Ana uygulama
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("fiyatlar", fiyatlar))
    app.add_handler(CommandHandler("grafik", grafik))

    print("🚀 Telegram komut sistemi başlatıldı.")
    app.run_polling()

if __name__ == "__main__":
    main()
