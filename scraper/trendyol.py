import requests
from bs4 import BeautifulSoup

def get_trendyol_data(url: str):
    """
    Fetches product data from a Trendyol product page.
    
    Args:
        url (str): The URL of the Trendyol product page.
        
    Returns:
        dict: A dictionary containing the product title and price.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    price = soup.find("span", class_="prc-dsc").text.strip()
    title = soup.find("h1", class_="pr-new-br").text.strip()
    
    return {
        "title": title,
        "price": price
    }


