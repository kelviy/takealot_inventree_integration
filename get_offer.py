from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from collections import Counter

def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    base_url = "https://seller-api.takealot.com/"

    product_list = fetch_and_sort_stock_cover(api_key, base_url)
    sales_data = fetch_sales_data(api_key, base_url, days=100)
    filtered= filter_product_list(product_list, sales_data)

    for i in filtered:
        print(f"SKU: {i[0]} with SDC: {i[1]}... has {i[3]} sales")
    

def filter_product_list(product_list, sales_data):
    # Count the number of sales per SKU
    sales_counter = Counter(sale["sku"] for sale in sales_data if "sku" in sale)

    # Filter product_list and include the number of matching sales
    filtered = [
        (product[0], product[1], product[2], sales_counter[product[0]])
        for product in product_list
        if product[1] > 0 and product[0] in sales_counter
    ]
    
    # Sort by product quantity (product[1])
    filtered.sort(key=lambda x: x[1])

    return filtered

def fetch_and_sort_stock_cover(api_key, base_url):
    end_point = "/v2/offers"
    headers = {"Authorization": f"Key {api_key}"}
    page_size = 1000
    page_num = 1

    product_list = []

    while True:
        params = {"page_size": page_size, "page_number": page_num}
        try:
            response = requests.get(f"{base_url.rstrip("/")}{end_point}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            break

        offers = data.get("offers", [])
        if not offers:
            break  # Exit loop if no more data

        for product in offers:
            stock_cover = product.get("stock_cover", {})
            if stock_cover:
                total_stock_cover = sum(sdc.get("stock_cover_days", 0) for sdc in stock_cover)
                product_list.append((product["sku"], total_stock_cover, stock_cover))

        if len(offers) < page_size:
            break  # Last page reached
        page_num += 1

    return product_list

def warehouse_id_mapping(api_key, base_url):
    end_point = "/v2/offers"
    headers = {"Authorization": f"Key {api_key}"}
    params = {"page_size": 1}

    try:
        response = requests.get(f"{base_url.rstrip("/")}{end_point}", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()["offers"][0]
    except Exception as e:
            print(f"Error {e}")
            return
    
    mappings = []

    for map in data.get("stock_at_takealot", []):
        mappings.append(map["warehouse"])

    return mappings


def fetch_sales_data(api_key, base_url, days = 30):
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    end_point = "/v2/sales/"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    
    # Format dates as required by the API
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    filters = f"start_date:{start_date_str};end_date:{end_date_str}"
    page_number = 1
    page_size = 100
    all_sales = []

    while True:
        
        full_url = f"{base_url.rstrip('/')}{end_point}?page_number={page_number}&page_size={page_size}&filters={filters}"
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        for sale in data.get("sales", []):
            extracted = {
                "sku": sale.get("sku"),
                "sale_status": sale.get("sale_status"),
                "order_date": sale.get("order_date"),
                "quantity": sale.get("quantity"),
                "customer_dc": sale.get("customer_dc")
            }
            all_sales.append(extracted)

        page_summary = data.get("page_summary", {})
        total = page_summary.get("total", 0)
        if page_number * page_size >= total:
            break
        page_number += 1

    return all_sales
    

if __name__ == "__main__":
    main()
