from django.db import models

# Create your models here.
class Address(models.Model):
    country = models.CharField(max_length=100, default='Việt Nam')
    province = models.CharField(max_length=100, default='Thành phố Hồ Chí Minh')
    district = models.CharField(max_length=100, default='1')
    ward = models.CharField(max_length=100, default='Bến Nghé')
    street = models.CharField(max_length=100, default='Nguyễn Huệ')
    def __str__(self):
        return f'{self.street} Street, {self.ward} Ward, {self.district} District, {self.province} Province, {self.country}'
    def get_full_address(self):
        return self.__str__()
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=50)
    balance = models.IntegerField(default=0)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    address_number = models.CharField(max_length=255, default='1')
    phone = models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username
    def get_full_address(self):
        return f'{self.address_number} {self.address.__str__()}'
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = (
        ('available','available'),
        ('sold','sold'),
        ('hide','Hide')
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)   
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Sold')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    def is_hide(self):
        return self.status == 'hide'
    def get_different_categories(self):
        return Category.objects.exclude(id=self.category.id).distinct()
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.user:
            return f'Order {self.id} of {self.user.username}'
        return f'Order {self.id}'

class Order_Product(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    review = models.TextField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    current_location = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    def get_status(self):
        if self.product.seller.address == self.current_location:
            return 'Waiting for delivery'
        elif self.current_location == self.order.user.address:
            return 'Arrived'
        else:
            return 'On the way'
    def __str__(self):
        return f'Order {self.order.id} - Product {self.product.name}'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.user and self.product:
            return f'Cart {self.id} of {self.user.username} - {self.product.name}'
        return f'Cart #{self.id}'

class FavoriteList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.user:
            return f'Favorite {self.id} of {self.user.username}'
        return f'Favorite #{self.id}'

class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    def __str__(self):
        if self.product:
            return f'Image of {self.product.name} #{self.id}'
        return f'Image Link #{self.id}'