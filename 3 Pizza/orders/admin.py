from django.contrib import admin
from .models import Dishes, Orders, Toppings
# Register your models here.

admin.site.register(Dishes)
admin.site.register(Orders)
admin.site.register(Toppings)
