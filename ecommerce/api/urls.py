from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    # write your URL rules here
    path('products/', views.ProductView.as_view(), name='all_products'),
    path('products/<int:prod_id>/', views.ProductView.as_view(), name='one_product'),
]
