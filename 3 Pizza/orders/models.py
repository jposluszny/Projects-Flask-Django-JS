from django.db import models

status = (("pending", "pending"), ("completed", "completed"))

# Create your models here.
class Dishes(models.Model):
    name = models.CharField(max_length=64)
    size = models.CharField(max_length=64)
    price = models.DecimalField( max_digits=10, decimal_places=2)
    toppings = models.IntegerField()
    def __str__(self):
        return f"{self.name} {self.size}"

class Orders(models.Model):
    date = user = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    order = models.TextField()
    order_price = models.DecimalField( max_digits=10, decimal_places=2)
    status = models.CharField(max_length=64, choices=status, default='pending')
    def __str__(self):
        return f"{self.date} {self.order} {self.order_price} $ "

class Toppings(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.name}"
