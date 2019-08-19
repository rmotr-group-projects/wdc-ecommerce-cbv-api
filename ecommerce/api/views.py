import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# complete the View below with all REST functionality

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(View):
    def _get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        #product_id may not come in the kwargs
        if product_id:
            product = self._get_object(product_id)
            # got a product_id but we dont know what it is
            if not product:
                return JsonResponse(
                    {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                    status=404)
            # got a product_id that we matched to a product. We put into json format with the serializer
            data = serialize_product_as_json(product)
        # we did not get a kwargs key for 'product_id'. we just got a GET request. 
        # we are going to send back all the products that we have in a list of json objects.
        else:
            # list
            qs = Product.objects.all()
            #       using the serializer for each product in our db.
            data = [serialize_product_as_json(product) for product in qs]
        return JsonResponse(data, status=200, safe=False)



        
# POST methods are supposed to create a new product.
    def post(self, *args, **kwargs):
        # create
        if 'product_id' in kwargs:
            return JsonResponse(
                {"success": False, "msg": "Invalid HTTP method"},
                status=400)

        try:
            payload = json.loads(self.request.body.decode('utf-8'))
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        # THIS BLOCK might need to be implemented to include a Category?
        # when creating a new procuct we need to know the category id to link it to an 
        # existing category. If we don't get a category id we return an error message. 
        category_id = payload.get('category_id', None)
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "msg": "Could not find category with id: {}".format(category_id)},
                status=404)
        # THIS BLOCK
        try:
            product = Product.objects.create(
                name=payload['name'],
                sku=payload['sku'],
                category=category,
                description=payload['description'],
                price=payload['price'])
        except (ValueError, KeyError):
            return JsonResponse(
                {"success": False, "msg": "Provided payload is not valid"},
                status=400)
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=201, safe=False)


    

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
        return JsonResponse(data, status=200, safe=False)

    # need a helper function

    def _update(self, product, payload, partial=False):
        for field in ['name', 'sku', 'category_id', 'description', 'price']:
            if not field in payload:
                if partial:
                    continue
                return JsonResponse(
                    {"success": False, "msg": "Missing field in full update"},
                    status=400)
            # category
            if field == 'category_id':
                category_id = payload.get('category_id', None)
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "msg": "Could not find category with id: {}".format(category_id)},
                        status=404)

                
            try:       #product is an instance of product set within the function#
                setattr(product, field, payload[field])
                product.save()
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provided payload is not valid"},
                    status=400)
        data = serialize_product_as_json(product)
        return JsonResponse(data, status=200, safe=False)
    

        
    # partial update 
    def patch(self, *args, **kwargs):

        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if not product:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        try:
            payload = json.loads(self.request.body.decode('utf-8'))
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(product, payload, partial=True)


    # full update
    def put(self, *args, **kwargs):

        product_id = kwargs.get('product_id')
        product = self._get_object(product_id)
        if not product:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        try:
            payload = json.loads(self.request.body.decode('utf-8'))
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        return self._update(product, payload, partial=False)
        
