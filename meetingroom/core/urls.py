from django.urls import path

from .views import index, book_reservation, reschedule

urlpatterns = [
    path("", index, name="index"),
    path("book-reservation", book_reservation, name="book_reservation"),
    path("reschedule", reschedule, name="reschedule"),
]
