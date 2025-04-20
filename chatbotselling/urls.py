"""
URL configuration for chatbotselling project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from main_site import views

urlpatterns = [
    # ! ADMIN
    path('admin/', admin.site.urls),
    # ! ACCOUNT:
    path('', views.get_login, name='get_login'),
    path('register/', views.get_register, name='get_register'),
    path('setting/<int:user_id>/', views.get_setting, name='get_setting'),
    # ! CUSTOMER:
    path('customer/home/<int:user_id>/', views.get_home_customer, name='get_home_customer'),
    # ! SELLER:
    path('seller/home/<int:user_id>/', views.get_home_seller, name='get_home_seller'),
    path('seller/product/add/<int:user_id>/', views.get_add_product, name='get_add_product'),
    path('seller/product/list/<int:user_id>/', views.get_product_list, name='get_product_list'),
    path('seller/product/history/<int:user_id>/<int:month>/<int:year>/', views.get_selling_history, name='get_selling_history'),
    path('seller/product/revenue/<int:user_id>/<int:month>/<int:year>/', views.get_revenue, name='get_revenue'),
    path('seller/product/view/<int:product_id>/', views.get_product_view, name='get_product_view'),
    path('seller/product/edit/<int:product_id>/', views.get_product_edit, name='get_product_edit'),
    path('update_quantity/<int:product_id>/<int:change>/', views.inc_quantity, name='inc_quantity'),
    path('update_quantity/<int:product_id>/-<int:change>/', views.dec_quantity, name='dec_quantity'), 
    path('hide_product/<int:product_id>/', views.hide_product, name='hide_product'),
    path('delete_product_image/<int:product_image_id>/', views.delete_product_image, name='delete_product_image'),
    # ! TEST
    path('test/', views.get_test, name='get_test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
