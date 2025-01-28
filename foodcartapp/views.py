
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.response import Response

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    try:
        order_data = request.data
        if 'products' not in order_data or not order_data['products']:
            return Response({'error': 'Обязательное поле products отсутствует или пусто'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(order_data['products'], list):
            return Response({'error': 'products должен быть списком'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            firstname=order_data.get('firstname'),
            lastname=order_data.get('lastname'),
            phonenumber=order_data.get('phonenumber'),
            address=order_data.get('address'),
        )

        for product_item in order_data['products']:
            if 'product' not in product_item or 'quantity' not in product_item:
                raise ValidationError('Каждый продукт должен содержать product и quantity')
            product = get_object_or_404(Product, id=product_item['product'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_item['quantity']
            )
        return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


