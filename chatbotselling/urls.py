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
    path('account/password/change/<int:user_id>/', views.get_change_password, name='get_change_password'),
    path('account/information/<int:user_id>/', views.get_information, name="get_information"),
    # Todo: Viết các hàm trong view cho nhóm trang account
    # ! CUSTOMER:
    path('customer/home/<int:user_id>/', views.get_home_customer, name='get_home_customer'),
    path('customer/cart/<int:user_id>/', views.get_cart, name='get_cart'),
    path('customer/cart/payment/<int:user_id>/', views.get_payment, name='get_payment'),
    path('customer/favorite/<int:user_id>/', views.get_favorite_list, name='get_favorite_list'),
    path('customer/shop/view/<int:user_id>/<int:seller_id>/', views.get_shop, name='get_shop'),
    path('customer/history/<int:user_id>/', views.get_history, name='get_history'),
    path('customer/cart/payment/identification/<int:user_id>', views.get_identification, name='get_identification'),
    path('customer/product/view/<int:user_id>/<int:product_id>/', views.get_product_view_customer, name='get_product_view_customer'),
    path('get_product_home/<int:offset>/<int:user_id>/', views.get_more_product, name='get_more_product'),
    path('get_search_product/<str:search>/<int:offset>/<int:user_id>/', views.get_search_product, name='get_search_product'),
    path('get_product_home/<int:offset>/<int:user_id>/<int:seller_id>/', views.get_more_product, name='get_more_product'),
    path('get_search_product/<str:search>/<int:offset>/<int:user_id>/<int:seller_id>/', views.get_search_product, name='get_search_product'),
    path('add_to_cart/<int:user_id>/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('like/<int:user_id>/<int:product_id>/', views.like_product, name='like_product'),
    path('delete_cart/<int:user_id>/<int:product_id>/', views.delete_cart, name='delete_cart'),
    path('update_quantity/cart/<int:cart_id>/<int:change>/', views.inc_quantity_in_cart, name='inc_quantity_in_cart'),
    path('update_quantity/cart/<int:cart_id>/-<int:change>/', views.dec_quantity_in_cart, name='dec_quantity_in_cart'),
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
    # ! CHATBOT:
    path('chatbot/send-message/<int:user_id>/', views.send_message, name='send_message'),
    # ! FACE ID:
    path('face/append/<int:user_id>/', views.get_append_face_id, name='get_append_face_id'),
    path('face/identification/<int:user_id>/', views.get_face_identification, name='get_face_identification'),
    path('user_faces/<int:user_id>/', views.get_faces, name="get_faces"),
] 
# Serve media files (for User_Face ImageField)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve face_id_model directory from project root
urlpatterns += static('/face_id_model/', document_root=settings.BASE_DIR / 'face_id_model')