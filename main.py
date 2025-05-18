from scraper.trendyol import get_trendyol_data
from db.database import init_db, insert_price, add_product

def run():
    init_db()
    url = input("Enter the URL of the product: ").strip()
    data = get_trendyol_data(url)
    print(data)

    print("Product Title:", data['title'])
    print("Product Price:", data['price'])

    product_id = add_product(data['title'], url)
    insert_price(product_id, data['price'])

    print("Product added to the database.")

if __name__ == "__main__":
    run()