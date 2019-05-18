import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse


class ProductView(View):
    
    def _get_object(self, prod_id):
        try:
            return Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            return None

    def get(self, *args, **kwargs):
        prod_id = kwargs.get('product_id')
        if prod_id:
            prod = self._get_object(prod_id)
            if not prod:
                return JsonResponse(
                    {"success": False, "msg": "Could not find a product with id: {}".format(prod_id)},
                    status=404)
            data = serialize_product_as_json(prod)
        else:
            all_prod = Product.objects.all()
            data = [serialize_product_as_json(prod) for prod in all_prod]
        return JsonResponse(data, status=200, safe=False)

    def post(self, *args, **kwargs):
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        
        category_id = payload.get('category', None)
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "msg": "Could not find category with id: {}".format(planet_id)},
                status=404)

        try:
            prod = Product.objects.create(
                name=payload['name'],
                sku=payload['sku'],
                category=category,
                description=payload['description'],
                price=payload['price'])
            
        except (ValueError, KeyError):
            return JsonResponse(
                {"success": False, "msg": "Provided payload is not valid"},
                status=400)
        data = serialize_product_as_json(prod)
        return JsonResponse(data, status=201, safe=False)

    def delete(self, *args, **kwargs):
        prod_id = kwargs.get('product_id')
        if not prod_id:
            return JsonResponse(
                {'msg': 'Invalid HTTP method', 'success': False},
                status=400)
        prod = self._get_object(prod_id)
        if not prod:
            return JsonResponse(
                {"success": False, "msg": "Could not find a product with id: {}".format(prod_id)},
                status=404)
        prod.delete()
        data = {"success": True}
        return JsonResponse(data, status=204, safe=False)

    def _update(self, product, payload, partial=False):
        for field in ['name', 'sku', 'category', 'description', 'price', 'featured']:
            if not field in payload:
                if partial:
                    continue
                return JsonResponse(
                    {"success": False, "msg": "Missing field in full update"},
                    status=400)
            
            if field == 'category':
                try:
                    payload['category'] = Category.objects.get(id=payload['category'])
                except Category.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "msg": "Could not find a product with id: {}".format(payload['category'])},
                        status=404)

            try:
                setattr(product, field, payload[field])
                product.save()
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provided payload is not valid"},
                    status=400)
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=200, safe=False)

    def patch(self, *args, **kwargs):
        prod_id = kwargs.get('product_id')
        prod = self._get_object(prod_id)
        if not prod:
            return JsonResponse(
                {"success": False, "msg": "Could not find a product with id: {}".format(prod_id)},
                status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(prod, payload, partial=True)

    def put(self, *args, **kwargs):
        prod_id = kwargs.get('product_id')
        prod = self._get_object(prod_id)
        if not prod:
            return JsonResponse(
                {"success": False, "msg": "Could not find a product with id: {}".format(prod_id)},
                status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(prod, payload, partial=False)
