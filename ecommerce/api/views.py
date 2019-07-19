import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

# complete the View below with all REST functionality

class ProductView(View):

    def get(self, *args, **kwargs):
      
        if kwargs != {}:
            product = Product.objects.get(id=kwargs['id'])
            product = serialize_product_as_json(product)
            return JsonResponse(product,status=200)
        else:
            all_prods = Product.objects.all()
            all_prods = [serialize_product_as_json(item) for item in all_prods]
            return JsonResponse(all_prods,status=200,safe=False)


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
        if kwargs != {}:
            try:
                prod_id = kwargs['id']
                Product.objects.get(id=prod_id).delete()
                return JsonResponse(
                    {"Response":"Product Id # {} delete".format(prod_id)},
                    status=204
                )
                
            except:
                return JsonResponse(
                    {"Product Not Found":"Can't find matching Id"},
                     status=404,safe=False
                     )
        
        return JsonResponse({},status=400,safe=False)

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
                
        if kwargs != {}:
            try:
                prod = Product.objects.get(id=kwargs['id'])
                
            except:
                pass        
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
                prod = Product.objects.get(id=kwargs['id'])
                
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
        print(prod)
        try:   
            prod.name = payload['name']
            prod.sku = payload['sku']
            prod.description = payload['description']
            prod.price = payload['price']
            prod.category = Category.objects.get(id=category)
            prod.save()

            return JsonResponse(serialize_product_as_json(prod), status=200)
        except:
            return JsonResponse(
                {"response":"An error has occured"}, status=400
            )
        
        
        return JsonResponse({},status=400,safe=False)
