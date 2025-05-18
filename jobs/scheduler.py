import sys
import os
import asyncio
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper.trendyol import get_trendyol_data
from db.database import get_all_products, insert_price, get_last_two_prices
from bot.notifier_bot import send_price_alert_and_graph

def clean_price(price_str):
    return int(
        price_str.replace(" TL", "")
                 .replace("₺", "")
                 .replace(".", "")
                 .replace(",", "")
                 .strip()
    )

async def track_all_products():
    print(f"⏰ [{datetime.now().strftime('%H:%M')}] Fiyatlar kontrol ediliyor...\n")
    products = get_all_products()

    for product in products:
        prod_id, title, url, _ = product
        try:
            data = get_trendyol_data(url)
            new_price = data["price"]
            success = insert_price(prod_id, new_price)
            if not success:
                continue

            old_price = get_last_two_prices(prod_id)
            if old_price and len(old_price) == 2:
                current_price = clean_price(old_price[0])
                prev_price = clean_price(old_price[1])

                print(f"[KONTROL] {title} → {prev_price} → {current_price}")
                if current_price != prev_price:
                    change_percent = abs((current_price - prev_price) / prev_price) * 100
                    direction = "down" if current_price < prev_price else "up"
                    await send_price_alert_and_graph(
                        product_title=title,
                        new_price=new_price,
                        direction=direction,
                        change_percent=change_percent,
                        product_id=prod_id
                    )
        except Exception as e:
            print(f"[HATA] {title}: {e}")

if __name__ == "__main__":
    asyncio.run(track_all_products())
