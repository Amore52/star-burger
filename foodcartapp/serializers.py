from rest_framework import serializers
from .models import Order, OrderItem, Product
import re

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    def validate_phonenumber(self, value):
        phone_regex = re.compile(r'^\+79[0-9]{9}$')
        if not phone_regex.match(value):
            raise serializers.ValidationError('Введен некорректный номер телефона')
        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product_item in products_data:
            product = product_item['product']
            quantity = product_item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        return order
