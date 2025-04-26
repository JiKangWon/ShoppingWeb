from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('country', 'province', 'district', 'ward', 'street')
    search_fields = ('country', 'province', 'district', 'ward', 'street')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'balance', 'address', 'address_number', 'phone', 'created_at')
    search_fields = ('username', 'name', 'address__country', 'address__province', 'address__district', 'address__ward', 'address__street')
    list_filter = ('balance',)
    ordering = ('-created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'description', 'price', 'category', 'quantity', 'status', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('status', 'category')
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)

@admin.register(Order_Product)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('order', 'product')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user', 'product')

@admin.register(FavoriteList)
class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user', 'product')

@admin.register(Product_Image)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id','product')
    search_fields = ('product__name',)
    list_filter = ('product',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'request', 'response')