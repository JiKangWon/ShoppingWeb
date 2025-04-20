from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Order_Product)
def create_attendance_records(sender, instance, created, **kwargs):
    if created:  # Only run when the Class_Student is created, not updated
        instance.current_location = instance.product.seller.address
        instance.save()