import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

# complete the View below with all REST functionality

class ProductView(View):

    def _get_object(self, product_id):
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

        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        
        category = payload['category']
        try:
            cat_obj = Category.objects.get(id=category)
        except:
            return JsonResponse(
                {"response":"Not a valid category"}, status=400
            )

        new_product = Product.objects.create(
            name = payload['name'],
            sku = payload['sku'],
            description = payload['description'],
            price = payload['price'],
            category = cat_obj
        )

        data = serialize_product_as_json(new_product)

        return JsonResponse(data,status=201)

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

    def _check_name_and_update(self,product):
        product_fields = ['id','name','sku','category','description','price']
        payload = json.loads(self.request.body)
        fields_update = []
        for key in payload.keys():
            if key in product_fields:
                fields_update.append(key)
                continue
            else:
                return JsonResponse({"success": False, "msg": "Provide a valid JSON payload"},status=400)

        for field in fields_update:
            try:
                setattr(product,field,payload[field])
            except:
                return JsonResponse({"success": False, "msg": "Provide a valid JSON payload"},status=400)
        
        product.save()
        data = serialize_product_as_json(product)
        return data

    def patch(self, *args, **kwargs):
        prod = self._get_object(kwargs['product_id'])
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        
        data = self._check_name_and_update(prod)
        return JsonResponse(data,status=200)
        

    def put(self, *args, **kwargs):
        
        if kwargs != {}:
            try:
                prod = Product.objects.get(id=kwargs['product_id'])
                
            except:
                pass        
        
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},
                status=400)
        
        category = payload['category']
        try:
            cat_obj = Category.objects.get(id=category)
            
        except:
            return JsonResponse(
                {"response":"Not a valid category"}, status=400
            )
    
        try:   
            prod.name = payload['name']
            prod.sku = payload['sku']
            prod.description = payload['description']
            prod.price = payload['price']
            prod.category = Category.objects.get(id=category)
            prod.featured = payload['featured']
            prod.save()

            return JsonResponse(serialize_product_as_json(prod), status=200)
        except:
            return JsonResponse(
                {"response":"An error has occured"}, status=400
            )
        
        
        return JsonResponse({},status=400,safe=False)
