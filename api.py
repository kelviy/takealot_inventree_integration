# inventree_takealot/views.py
from django.http import JsonResponse
import requests
from datetime import datetime, timedelta
from collections import Counter
from part.models import Part

# --- Provided Functions (with slight modifications) ---

class TakeALot_API:
    def __init__(self, api_key : str, base_url : str):
        self.api_key = api_key
        self.base_url = base_url
        self.warehouse_mappings = {}
        self.init_warehouse_id_mapping()

    def get_stock_cover(self) -> list:
        end_point = "/v2/offers"
        headers = {"Authorization": f"Key {self.api_key}"}
        page_size = 1000
        page_num = 1

        product_list = []

        while True:
            params = {"page_size": page_size, "page_number": page_num}
            try:
                response = requests.get(f"{self.base_url.rstrip('/')}{end_point}", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Error fetching page {page_num}: {e}")
                break

            offers = data.get("offers", [])
            if not offers:
                break  # Exit loop if no more data

            for product in offers:
                stock_cover = product.get("stock_cover", [])
                if stock_cover:
                    total_stock_cover = product.get("total_stock_cover")
                    product_list.append((product["sku"], total_stock_cover, stock_cover))

            if len(offers) < page_size:
                break  # Last page reached
            page_num += 1

        return product_list


    def get_sales_data(self, days=30) -> list:
        headers = { "Authorization": f"Key {self.api_key}", "Content-Type": "application/json" }
        end_point = "/v2/sales/"
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        filters = f"start_date:{start_date_str};end_date:{end_date_str}"
        page_number = 1
        page_size = 100
        all_sales = []

        while True:
            full_url = f"{self.base_url.rstrip('/')}{end_point}?page_number={page_number}&page_size={page_size}&filters={filters}"
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

    @staticmethod
    def prepare_sdc_data(product_list, sales_data) -> list:
        # Count the number of sales per SKU
        sales_counter = Counter(sale["sku"] for sale in sales_data if "sku" in sale)

        filtered = [
            (product[0], product[1], product[2], sales_counter[product[0]])
            for product in product_list
            if product[1] > 0 and product[0] in sales_counter
        ]
        
        filtered.sort(key=lambda x: x[1])
        return filtered

    def init_warehouse_id_mapping(self) -> None:
        end_point = "/v2/offers"
        headers = {"Authorization": f"Key {self.api_key}"}
        params = {"page_size": 1}

        try:
            response = requests.get(f"{self.base_url.rstrip('/')}{end_point}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["offers"][0]
        except Exception as e:
            print(f"Error {e}")
            return
        
        mappings = {}
        for mapping in data.get("stock_at_takealot", []):
            # Expecting each mapping to be a dict with "warehouse" details.
            mappings.update({mapping["warehouse"]["warehouse_id"]:mapping["warehouse"]["name"]})
        self.warehouse_mappings = mappings


class Custom_Inventree_API:
    
    def match_parts(self, sku_list) -> list:
        parts = []
        for sku in sku_list:
            part = Part.objects.filter(IPN__iexact=sku).first()
            parts.append(part)

        return parts
    
    def match_part(self, sku) -> Part:
        return Part.objects.filter(IPN__iexact=sku).first()

