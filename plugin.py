# inventree_takealot/plugin.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .api import TakeALot_API, Custom_Inventree_API

class Takealot_Integration(UrlsMixin, NavigationMixin, SettingsMixin, InvenTreePlugin):
    NAME = "TakeALot Integrator"
    SLUG = "takealotintegrator"
    TITLE = "TakeALot Integrator"
    DESCRIPTION = "Provides features that work with takealot"
    VERSION = "1.0.0"
    AUTHOR = "Kelvin Wei"
    MIN_VERSION = "0.17.8"
    NAVIGATION_TAB_NAME = "Integration_TAL"
    NAVIGATION_TAB_ICON = "fas fa-plug"
    NAVIGATION = [
        {
            "name": "View Stock Days Cover",
            "link": "plugin:takealotintegrator:interface",
            "icon": "fas fa-shipping-fast",
        }
    ]
    SETTINGS = {
        "TAKEALOT_API_KEY": {
            "name": "TakeALot API Key",
            "description": "TakeALot API key for intergrating with takealot api",
            "default": "",
            "validator":"string",
            "required": True,
            "hidden": True,
        },
        "TAKEALOT_API_ENDPOINT": {
            "name": "TakeALot EndPoint URL",
            "description": "TakeALot URL to access the api",
            "default": "",
            "validator":"string",
            "required": True,
        },
    }

    def __init__(self):
        super().__init__()

        self.context = {}
        self.takealot_api = TakeALot_API(self.get_setting("TAKEALOT_API_KEY"), self.get_setting("TAKEALOT_BASE_URL"))
        self.inventree_api = Custom_Inventree_API()

    def setup_urls(self):
        """Define custom URL endpoints for this plugin's views."""
        return [
            path("", login_required(self.interface), name="interface"),
        ]

    # --- End Provided Functions ---
    def fetch_takealot_data(self, request):
        product_list = self.takealot_api.get_stock_cover()
        sales_data = self.takealot_api.get_sales_data(days=100)
        filtered = TakeALot_API.prepare_sdc_data(product_list, sales_data)

        result = []
        for sku, sdc_total, stock_cover, sales_count in filtered:
            part = self.inventree_api.match_part(sku)
            product_image = part.image_url
            product_name = part.nam
            # Map warehouse ids to names using the warehouse_mappings list.
            warehouses = []
            for wh_id in stock_cover:
                # Look up warehouse name from the mappings list; if not found, default to the id.
                warehouse_name = self.takealot_api.warehouse_mappings[wh_id]
                warehouses.append({
                    "warehouse_id": wh_id,
                    "warehouse_name": warehouse_name,
                    "sdc": stock_cover[wh_id]
                })
            result.append({
                "sku": sku,
                "product_name": product_name,
                "product_image": product_image,
                "sdc_total": sdc_total,
                "sales_count": sales_count,
                "warehouses": warehouses
            })

        return JsonResponse({"data": result})