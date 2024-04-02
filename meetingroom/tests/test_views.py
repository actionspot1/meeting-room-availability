import pytest
from django.test import Client
from django.urls import reverse
from core.views import index

client = Client()


def test_index_view():
    response = client.get(reverse("index"))
    assert response.status_code == 200
    assert "is_available" in response.context


def test_book_reservation_view():
    response = client.get(reverse("book_reservation"))
    assert response.status_code == 200
