from django.contrib import admin
from .models import books
from .models import borrowings
# Register your models here.
admin.site.register(books)
admin.site.register(borrowings)
