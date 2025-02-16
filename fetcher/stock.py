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

# Organize stock by category
def organize_stock_by_category(stock_data, product_groups):
    categories = {}

    for item in stock_data:
        product_name = item['product']['name']
        product_group_id = item['product'].get('product_group_id')
        
        # Get category name or default to "Unknown"
        category = product_groups.get(product_group_id, "Unknown")

        if category not in ORDER:
            raise ValueError(f"Unexpected category '{category}' found. Update ORDER list if needed.")

        if category not in categories:
            categories[category] = []
        categories[category].append(product_name)

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

    organized_data = organize_stock_by_category(stock_data, product_groups)
    write_to_yaml(organized_data)

if __name__ == "__main__":
    main()
