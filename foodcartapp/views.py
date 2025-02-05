import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.response import Response

from .models import Product, Order, OrderItem
from .serializers import OrderSerializer


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


@api_view(['POST'])
def register_order(request):
    try:
        registered_order = request.data
        required_keys = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
        phone_regex = re.compile(r'^\+79[0-9]{9}$')
        empty_keys = [key for key in required_keys if key not in registered_order or not registered_order[key]]
        if empty_keys:
            return Response(f'error: {empty_keys}: поле не может быть пустым', status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(registered_order['products'], list):
            return Response({'error': 'products: Ожидался list со значениями, но был получен "str".'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not phone_regex.match(registered_order['phonenumber']):
            return Response({'error': 'phonenumber: Введен некорректный номер телефона'},
                            status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            firstname=registered_order.get('firstname'),
            lastname=registered_order.get('lastname'),
            phonenumber=registered_order.get('phonenumber'),
            address=registered_order.get('address'),
        )

        for product_item in registered_order['products']:
            if 'product' not in product_item or 'quantity' not in product_item:
                raise ValidationError('Каждый продукт должен содержать product и quantity')
            product = get_object_or_404(Product, id=product_item['product'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product_item['quantity'],
                price=product.price
            )
        serializer = OrderSerializer(order)
        redirect_url = 'http://127.0.0.1:8000/manager/orders/'
        response_data = {
            'message': 'Заказ успешно создан',
            'order': serializer.data,
            'redirect_url': redirect_url
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers={
            'Location': redirect_url
        })

    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


