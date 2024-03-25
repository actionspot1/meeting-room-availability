from django.urls import path

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("book-reservation", book_reservation, name="book_reservation"),
]
