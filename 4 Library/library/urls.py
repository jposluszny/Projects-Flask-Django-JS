from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("registration", views.registration_view, name="registration"),
    path("user", views.user_view, name="user"),
    path("logout", views.logout_view, name="logout"),
    path("search", views.search_view, name = "search"),
    path("borrow", views.borrow_view, name = "borrow"),

    path("history", views.history_view, name = "history"),
    path("<i_isbn>", views.book_view, name = "book"),


]
