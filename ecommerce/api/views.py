import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404

# complete the View below with all REST functionality

class ProductView(View):

    def get(self, *args, **kwargs):
        data = None

        product_id = kwargs.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            data = serialize_product_as_json(product)
        else:
            products = get_list_or_404(Product)
            data = [serialize_product_as_json(product) for product in products]

        return JsonResponse(data, status=200, safe=False)

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        category_id = data.get('category', None)
        category = get_object_or_404(Category, id=category_id)
        product = Product.objects.create(
            name=data.get('name'),
            sku=data.get('sku'),
            category=category,
            description=data.get('description'),
            price = data.get('price')
        )
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=201, safe=False)

    def delete(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        data = {"success": True}
        return JsonResponse(data, status=204, safe=False)

    def patch(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(self.request.body)

        for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
            if not field in data:
                continue

            if field == 'category':
                data['category'] = get_object_or_404(Category, id=data.get('category'))

            setattr(product, field, data[field])
            product.save()

        data = serialize_product_as_json(product)
        return JsonResponse(data, status=200, safe=False)

    def put(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(self.request.body)

        for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
            if not field in data:
                return JsonResponse({'success': False}, status=404)

            if field == 'category':
                data['category'] = get_object_or_404(Category, id=data.get('category'))

            setattr(product, field, data[field])
            product.save()

        data = serialize_product_as_json(product)
        return JsonResponse(data, status=200, safe=False)
