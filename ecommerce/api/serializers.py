from products.models import Product, Category


# converts Product into JSON format
def serialize_product_as_json(product):
    return {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'category': product.category.id,
        'description': product.description,
        'price': str(product.price),
        'created': product.created.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-7] + 'Z',
        'featured': product.featured,
    }
