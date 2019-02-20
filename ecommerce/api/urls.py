from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    # write your URL rules here
    path('products/<int:product_id>', views.ProductView.as_view()), # Question: break this down
    path('products/', views.ProductView.as_view() ),
]


# path is URL routing syntax

# /api/products/

# /api/products/<product_id>

# https://docs.djangoproject.com/en/2.1/topics/http/urls/

# views.ProductView.as_view -->  views is views.py, ProductView is the class, 

# https://ccbv.co.uk/

# https://docs.djangoproject.com/en/2.1/topics/class-based-views/

# subclassing generic views

# https://docs.djangoproject.com/en/2.1/topics/class-based-views/
# over HTTP using the views as an API