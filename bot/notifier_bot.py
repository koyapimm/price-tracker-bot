from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime
from db.database import get_price_history
import matplotlib.pyplot as plt
import os

TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"
CHAT_ID = 2144798452

bot = Bot(token=TOKEN)

async def send_price_alert_and_graph(product_title, new_price, direction, change_percent, product_id):
    try:
        msg = f"*{product_title}*\n"
        msg += f"Yeni Fiyat: `{new_price}`\n"
        if direction == "down":
            msg += f"⬇️ Fiyat düştü! %{change_percent:.2f}"
        elif direction == "up":
            msg += f"⬆️ Fiyat yükseldi! %{change_percent:.2f}"
        else:
            msg += f"ℹ️ Fiyat değişti ama yön algılanamadı."

        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

        if direction in ["down", "up"]:
            data = get_price_history(product_id)
            if len(data) < 2:
                return

            dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in data]
            prices = [int(row[1].replace(" TL", "").replace("₺", "").replace(".", "").replace(",", "").strip()) for row in data]

            plt.figure()
            plt.plot(dates, prices, marker='o')
            plt.title(f"{product_title} Fiyat Değişimi")
            plt.xlabel("Tarih")
            plt.ylabel("Fiyat (₺)")
            plt.xticks(rotation=45)
            plt.tight_layout()

            os.makedirs("graphs", exist_ok=True)
            file_path = f"graphs/{product_id}.png"
            plt.savefig(file_path)
            plt.close()

            with open(file_path, "rb") as f:
                await bot.send_photo(chat_id=CHAT_ID, photo=f)

            os.remove(file_path)

    except TelegramError as e:
        print(f"[Telegram Error] {e}")
