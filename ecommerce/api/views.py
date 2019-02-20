import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

from django.utils.decorators import method_decorator # for method_decorator
from django.views.decorators.csrf import csrf_exempt # for csrf_exempt


# complete the View below with all REST functionality

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    
    def _get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None 
    
    def get(self, *args, **kwargs):
        product_id = kwargs.get('product_id') #get the id if it exists
        
        if product_id: # if the product ID exists, do this...
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
        

        #### Note to self: REVIEW CODE BELOW ####
        
    def post(self, *args, **kwargs):
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)

        # tries to find category in the JSON payload, if it doesn't exist it defaults to None
        category_id = payload.get('category', None)
        
    
        #CODE BELOW is getting the object by it's ID in the database (an int)

        #we're just assiging it to that Category model
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "msg": "Could not find category with id: {}".format(category_id)},
                status=404)

        try:
            product = Product.objects.create(
                name=payload['name'],
                category=category,
                sku=payload['sku'],
                description=payload['description'],
                price=payload['price'],
            )
        except (ValueError, KeyError):
            return JsonResponse(
                {"success": False, "msg": "Provided payload is not valid"},
                status=400)
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=201, safe=False)

# CODE FROM MODELS.PY
# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     sku = models.CharField(max_length=8)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     description = models.CharField(max_length=1000, blank=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     created = models.DateTimeField(auto_now_add=True)
#     featured = models.BooleanField(default=False)
    
    
    
    def delete(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        if not product_id:
            return JsonResponse(
                {'msg': 'Invalid HTTP method', 'success': False},
                status=400)
        product = self._get_object(product_id)
        if not product:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        product.delete()
        data = {"success": True}
        return JsonResponse(data, status=204, safe=False)

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
                        {"success": False, "msg": "Could not find payload with id: {}".format(payload['category'])},
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
        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if not product:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(product, payload, partial=True)

    def put(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if not product:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(product, payload, partial=False)