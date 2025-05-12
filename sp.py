import os
import django
import random
# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbotselling.settings')  # Replace with your project's settings module
django.setup()
from main_site.models import *

edges_data = [
    (1, 2, 4.5),
    (1, 3, 2.0),
    (2, 4, 3.0),
    (2, 5, 2.5),
    (3, 6, 6.0),
    (4, 7, 5.5),
    (5, 7, 1.5),
    (6, 8, 2.2),
    (7, 9, 3.8),
    (8, 9, 4.0),
    (9, 10, 2.7),
    (10, 11, 3.3),
    # ... bạn có thể thêm tuỳ ý
]

# Tạo các Edge
edges = [
    Edge(start_id=u, end_id=v, distance=d)
    for u, v, d in edges_data
]
Edge.objects.bulk_create(edges)