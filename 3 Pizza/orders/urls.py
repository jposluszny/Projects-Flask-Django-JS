from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registration", views.registration_view, name="registration"),
    path("cart", views.cart_view, name = "cart"),
    path("status", views.status_view, name="status"),
]
