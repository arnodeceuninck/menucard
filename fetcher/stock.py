import os
import requests
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Grocy API credentials
GROCY_URL = os.getenv("GROCY_URL")
GROCY_API_KEY = os.getenv("GROCY_API_KEY")

# API Endpoints
STOCK_URL = f"{GROCY_URL}/api/stock"
PRODUCT_GROUPS_URL = f"{GROCY_URL}/api/objects/product_groups"
PRODUCTS_URL = f"{GROCY_URL}/api/objects/products"
LOCATIONS_URL = f"{GROCY_URL}/api/objects/locations"
PRODUCT_STOCK_LOCATIONS_URL = f"{GROCY_URL}/api/stock/products/{{}}/locations"

# Define headers
headers = {
    'GROCY-API-KEY': GROCY_API_KEY
}

# Define the correct order of categories
ORDER = [
    "Frisdranken",
    "Siropen",
    "Vruchtensappen",
    "Overige alcoholvrije dranken",
    "Bieren",
    "Ciders en lichte dranken",
    "Rode Wijnen",
    "Jenevers",
    "Vodka's",
    "Gins",
    "Likeuren en zoete dranken",
    "Overige sterke dranken",
    "Chips"
]

# Fetch stock data from Grocy API
def fetch_stock_data():
    response = requests.get(STOCK_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Failed to retrieve stock. Status code: {response.status_code}")

# Fetch product groups from Grocy API
def fetch_product_groups():
    response = requests.get(PRODUCT_GROUPS_URL, headers=headers)
    if response.status_code == 200:
        product_groups = response.json()
        return {group['id']: group['name'] for group in product_groups}
    else:
        raise RuntimeError(f"Failed to retrieve product groups. Status code: {response.status_code}")

# Fetch location mapping (id → name)
def fetch_locations():
    response = requests.get(LOCATIONS_URL, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to retrieve locations. Status code: {response.status_code}")

    locations = response.json()
    return {loc['id']: loc['name'] for loc in locations}

# Fetch product locations for each product
def fetch_fridge_items():
    fridge_items = set()
    products_response = requests.get(PRODUCTS_URL, headers=headers)
    
    if products_response.status_code != 200:
        raise RuntimeError(f"Failed to retrieve products. Status code: {products_response.status_code}")
    
    products = products_response.json()

    # Fetch locations where each product is stored
    for product in products:
        product_id = product['id']
        locations_response = requests.get(PRODUCT_STOCK_LOCATIONS_URL.format(product_id), headers=headers)
        
        if locations_response.status_code != 200:
            print(f"Warning: Failed to get locations for product {product['name']}")
            continue

        locations = locations_response.json()

        # Check if the product is in the fridge
        for loc in locations:
            if loc['location_id'] and loc['location_name'] == "Fridge":
                fridge_items.add(product['name'])
                break  # No need to check further locations for this product

    return fridge_items

# Organize stock by category, adding ❄️ for fridge items
def organize_stock_by_category(stock_data, product_groups, fridge_items):
    categories = {}

    for item in stock_data:
        product_name = item['product']['name']
        product_group_id = item['product'].get('product_group_id')
        amount = item['amount']

        if amount == 0:
            continue

        # Add ❄️ if stored in fridge
        display_name = f"{product_name} ❄️" if product_name in fridge_items else product_name

        # Get category name or default to "Unknown"
        category = product_groups.get(product_group_id, "Unknown")

        if category not in ORDER:
            raise ValueError(f"Unexpected category '{category}' found. Update ORDER list if needed.")

        if category not in categories:
            categories[category] = []
        categories[category].append(display_name)

    return categories

# Write the organized data to a YAML file
def write_to_yaml(data):
    yaml_file_path = "_data/menu_auto.yml"

    # Sort categories based on ORDER list
    sorted_data = [{"name": category, "items": data[category]} for category in ORDER if category in data]

    with open(yaml_file_path, 'w', encoding="utf-8") as yaml_file:
        yaml.dump(sorted_data, yaml_file, default_flow_style=False, allow_unicode=True)

    print(f"Data has been written to {yaml_file_path}")

# Main function
def main():
    stock_data = fetch_stock_data()
    product_groups = fetch_product_groups()
    locations = fetch_locations()  # Get location ID → name mapping
    fridge_items = fetch_fridge_items()  # Identify fridge items

    organized_data = organize_stock_by_category(stock_data, product_groups, fridge_items)
    write_to_yaml(organized_data)

if __name__ == "__main__":
    main()
