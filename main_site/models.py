from django.db import models

# Create your models here.
class User(models.Model):
    STATUS_CHOICES = (        
        ('customer','customer'),
        ('seller','seller'),
    )
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=30)
    balance = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=STATUS_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('electronics','Electronics'),
        ('clothing','Clothing'),
        ('books','Books'),
        ('toys','Toys'),
        ('home','Home'),
        ('health','Health'),
        ('sports','Sports'),
        ('automotive','Automotive'),
        ('other','Other'),
    )
    STATUS_CHOICES = (
        ('available','Available'),
        ('sold','Sold'),
        ('hide','Hide')
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=1)
    category = models.CharField(max_length=100, default='Other')    
    quantity = models.IntegerField(default=0)
    img_url = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Sold')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('preparing','Preparing'),
        ('pending','Pending'),
        ('completed','Completed'),
    )
    seller = models.ForeignKey(User, related_name='sales' , on_delete=models.CASCADE)
    buyer = models.ForeignKey(User,related_name='purchases', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Preparing')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Transaction {self.id}'
    def total(self):
        product_quantities = Product.objects.get(transaction=self)
        ans = 0
        for product_quantity in product_quantities:
            ans += product_quantity.product.price * product_quantity.quantity
        return ans

class Product_Quantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    def total(self):
        return self.product.price * self.quantity
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)