import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

class ProductView(View):
    def _get_object(self,product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None
    def get(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        if product_id:
            # detail
            product = self._get_object(product_id)
            if not product:
                return JsonResponse(
                    {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                    status=404)
            data = serialize_product_as_json(product)
        else:
            # list
            qs = Product.objects.all()
            data = [serialize_product_as_json(product) for product in qs]
        return JsonResponse(data, status=200, safe=False)
    
    def post(self, *args, **kwargs):
        if 'product_id' in kwargs:
           return JsonResponse({"success": False, "msg": "Product already exists"}, status=400)
        try:         
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse({"success": False, "msg":"Provide a valid JSON payload"}, status=400)
        
        data = serialize_product_as_json(payload)
        return JsonResponse(data, status=201, safe=False)
            
    def delete(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        if not product_id:
            return JsonResponse({"success": False, "msg": "invalid HTTP method"}, status = 400)
        product = self._get_object(product_id)
        if not product:
            return JsonResponse({success: False, "msg": "unable to find product with id {}".format(product_id)}, status = 404)
        product.delete()
        data = {"success":True}
        return JsonResponse(data, status=200, safe=False)
    
    def _update(self, product, payload, partial=False):
        for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
            if not field in payload:
                if partial:
                    continue
                return JsonResponse(
                    {"success": False, "msg": "Missing field in full update"},status=400)
            if field == 'category':
                try:
                    payload['category'] = Category.objects.get(id=payload['category'])
                except Category.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "msg": "Could not find planet with id: {}".format(payload['category'])}, status=404)
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
        product_id = kwargs.get('product_id')
        if not product_id:
            return JsonResponse({"success": False, "msg": "invalid HTTP method"}, status = 400)
        product = self._get_object(product_id)
        if not product:
            return JsonResponse({"success": False, "msg": "Product with id {} doesn't exist, bucko".format(product_id)}, status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse({"success":False, "msg": "Invalid JSON paylod there, chief"}, status = 400)
        return self._update(product, payload, partiel=True)
    
    def put(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        if not product_id:
            return JsonResponse({"success": False, "msg": "invalid HTTP method"}, status = 400)
        product = self._get_object(product_id)
        if not product:
            return JsonResponse({"success": False, "msg": "Product with id {} doesn't exist, bucko".format(product_id)}, status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse({"success":False, "msg": "Invalid JSON paylod there, chief"}, status = 400)
        return self._update(product, payload, partiel=True)
