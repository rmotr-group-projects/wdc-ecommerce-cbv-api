import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# complete the View below with all REST functionality
def abc(request):
    # product = Product.objects.get(id=1)
    # json.loads()
    print(request)
    return HttpResponse('<h1>Hi</h1>')

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):

    def _get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        if kwargs:  # get a single product
            product = Product.objects.get(id=self.kwargs['product_id'])
            if product:
                serialized_product = serialize_product_as_json(product)
                return JsonResponse(serialized_product)
            else:
                return JsonResponse({"success": False, "msg": "Could not find product with id: {}".format(product)}, status=404)
        else:  # get all products, return as json list
            products = Product.objects.all()
            product_list = [serialize_product_as_json(product) for product in products]
            return JsonResponse(product_list, safe=False)

    @csrf_exempt
    def post(self, *args, **kwargs):
        try:
            payload = json.loads(self.request.body)  # get JSON from user, convert into python dict... request.body.decode('utf-8') not necessary here
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},      # if there is a missing value, return False
                status=400)

        category_id = payload.get('category', None)  # getting the payload['category'] value as int()

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "msg": "Could not find category with id: {}".format(category_id)},
                status=404)
        try:
            product = Product.objects.create(
                name=payload['name'],
                category=category,  # int
                sku=payload['sku'],
                description=payload['description'],
                price=payload['price'],
            )
        except (ValueError, KeyError):
            return JsonResponse(
                {"success": False, "msg": "Provided payload is not valid. Add proper number or character values"},
                status=400)
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=201, safe=False)

    @csrf_exempt
    def delete(self, *args, **kwargs):
        product_id = kwargs.get('product_id')   # if url pattern exists: /products/11/
        product = self._get_object(product_id)
        if product:
            product.delete()
            data = {"success": True}
            return JsonResponse(data, status=204, safe=False)
        else:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        return JsonResponse({'msg': 'Invalid HTTP method', 'success': False}, status=400)

    @csrf_exempt
    def _update(self, product, payload, partial=False):
        for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
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
                        {"success": False, "msg": "Could not find planet with id: {}".format(payload['category'])},
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

    @csrf_exempt
    def patch(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if product:
            try:
                payload = json.loads(self.request.body)   # get JSON as dictionary
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provide a valid JSON payload"},
                    status=400)
            return self._update(product, payload, partial=True)
        return JsonResponse({"success": False, "msg": "Could not find product with id: {}".format(product_id)}, status=404)

    @csrf_exempt
    def put(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if product:
            try:
                payload = json.loads(self.request.body)
            except ValueError:
                return JsonResponse({"success": False,
				    "msg": "Provide a valid JSON payload"},
				    status=400)
            return self._update(product, payload, partial=False)
        return JsonResponse({"success": False, "msg": "Could not find product with id: {}".format(product_id)}, status=404)
