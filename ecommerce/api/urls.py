from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    path('products/', views.ProductView.as_view()),
    path('products/<int:id>', views.ProductView.as_view())
]
