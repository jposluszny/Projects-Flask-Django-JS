from django.db import models

status = (("pending", "pending"), ("borrowed", "borrowed"), ("returned", "returned"))

# Create your models here.
class books(models.Model):
    isbn = models.CharField(max_length=64)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    year = models.CharField(max_length=4)
    quantity = models.IntegerField()
    def __str__(self):
        return f'{self.title} by {self.author}'

class borrowings(models.Model):
    user = models.CharField(max_length=64, blank=True)
    book = models.ForeignKey(books, on_delete=models.CASCADE, related_name="borrowing", blank=True)
    borrowing_date = models.DateField(auto_now_add = True, blank=False)
    return_date = models.DateField(blank=False)
    status = models.CharField(max_length=64, choices=status, default='pending')
    def __str__(self):
        return f'{self.user}, {self.book}, {self.borrowing_date}, {self.return_date}'
