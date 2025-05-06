import os
import sys
# trỏ về thư mục chứa settings.py của Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbotselling.settings")

import django
django.setup()
# actions/actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from main_site.models import Product  # import Django ORM models

class ActionSearchProduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product")
        # Tra cứu DB Django
        results = Product.objects.filter(name__icontains=product_name)[:5]
        if results:
            msg = "Mình tìm thấy các sản phẩm:\n"
            for p in results:
                msg += f"- {p.name}: {p.get_formatted_price()}\n"
        else:
            msg = "Xin lỗi, mình chưa tìm thấy sản phẩm phù hợp."
        dispatcher.utter_message(text=msg)
        return []

class ActionRecommendGift(Action):
    def name(self) -> Text:
        return "action_recommend_gift"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        occasion = tracker.get_slot("occasion")
        # Ví dụ đơn giản: lọc category theo occasion
        suggestions = Product.objects.filter(category__name__icontains=occasion)[:5]
        if suggestions:
            msg = f"Gợi ý quà cho dịp {occasion}:\n"
            for p in suggestions:
                msg += f"- {p.name} ({p.get_formatted_price()})\n"
        else:
            msg = "Mình chưa có gợi ý phù hợp, bạn thử dịp khác nhé."
        dispatcher.utter_message(text=msg)
        return []
