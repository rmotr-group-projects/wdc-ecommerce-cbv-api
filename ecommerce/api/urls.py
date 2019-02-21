from django.contrib import admin
from django.urls import path, include

from api import views


app_name = 'api'

urlpatterns = [
    path('products/', views.ProductView.as_view(), name='all_products'),
    path('products/<int:product_id>/', views.ProductView.as_view(), name='all_products'),
    path('abc/', views.abc, name='abc'),
]
