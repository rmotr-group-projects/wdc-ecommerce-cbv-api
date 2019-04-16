import json
from products.models import Category, Product
from api.serializers import serialize_product_as_json

from django.views.generic import View
from django.http import HttpResponse, JsonResponse

# complete the View below with all REST functionality



class ProductView(View):

    def get(self, *args, **kwargs):
        #Return the request object formatted into JSON
        id_passed = kwargs.get('prod_id')
        if id_passed:
            product = Product.objects.get(id=self.kwargs['prod_id'])
            if product:
                json_product = serialize_product_as_json(product)
                return JsonResponse(json_product)
            else:
                return JsonResponse({"success": False, "msg": "Could not find product with id: {}".format(product)}, status=404)
        #Return all objects formatted into JSON
        else:
            products = Product.objects.all()
            product_list = [serialize_product_as_json(product) for product in products]
            return JsonResponse(product_list,safe=False)

    def post(self, *args, **kwargs):
        #try to get json payload
        try:
            payload = json.loads(self.request.body)
        except ValueError:
            return JsonResponse(
                {"success": False, "msg": "Provide a valid JSON payload"},  
                status=400)
        try:
            category_id = payload.get('category',None)
            category = Category.objects.get(id=category_id)

        except Category.DoesNotExist:
            return JsonResponse(
                {"success": False, "msg": "Could not find category with id: {}".format(category)},
                status=404)
        try:
            product = Product.objects.create(
                category=category,
                name=payload['name'],
                sku=payload['sku'],
                description=payload['description'],
                price=payload['price'],
                featured = payload.get('featured',False)
            )

        except (ValueError, KeyError):
            return JsonResponse(
                {"success": False, "msg": "Provided info isn't valid, please fill in all details"},
                status=400)
        product.save()
        ret_prod = serialize_product_as_json(product)
        return JsonResponse(ret_prod, status=201)


    def delete(self, *args, **kwargs):
        product_id = kwargs.get('prod_id')
        product = Product.objects.get(id=product_id)
        if product:
            product.delete()
            data = {"success": True}
            return JsonResponse(data,status=204)
        else:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        return JsonResponse({'msg': 'Invalid HTTP method', 'success': False}, status=400)

    def patch(self, *args, **kwargs):
        product = Product.objects.get(id=self.kwargs['prod_id'])
        if product:
            #get input payload
            try:
                payload = json.loads(self.request.body)
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provide a valid JSON payload"},  
                    status=400)
            for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
                if field in payload:

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
        else:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
    def put(self, *args, **kwargs):
        product = Product.objects.get(id=self.kwargs['prod_id'])
        if product:
            #get input payload
            try:
                payload = json.loads(self.request.body)
            except ValueError:
                return JsonResponse(
                    {"success": False, "msg": "Provide a valid JSON payload"},  
                    status=400)

            for field in ['name', 'category', 'sku', 'description', 'price', 'featured']:
                if not field in payload:
                    return JsonResponse({   "success": False, "msg": "Missing field"},
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
                except ValueError:
                    return JsonResponse(
                    {"success": False, "msg": "Provided payload is not valid"},
                    status=400)
                product.save()
                data = serialize_product_as_json(product)
            return JsonResponse(data)

            
        else:
            return JsonResponse(
                {"success": False, "msg": "Could not find product with id: {}".format(product_id)},
                status=404)
        return JsonResponse({'msg': 'Invalid HTTP method', 'success': False}, status=400)
