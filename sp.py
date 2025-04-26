import os
import django
import random
# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbotselling.settings')  # Replace with your project's settings module
django.setup()
from main_site.models import *

products = Product.objects.filter(seller__id=2)
for product in products:
    print(product.name)