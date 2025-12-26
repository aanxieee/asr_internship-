"""
URL configuration for pricing app
"""

from django.urls import path
from .views import get_price_estimate


urlpatterns = [
    path('estimate/', get_price_estimate, name='calculate_estimate'),
]