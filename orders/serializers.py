from rest_framework import serializers
from products.serializers import ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price', 'added_at')
        read_only_fields = ('id', 'added_at')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'updated_at')

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'total_price')


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grand_total = serializers.ReadOnlyField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'status_display', 'payment_method', 'is_paid',
                  'total_price', 'delivery_price', 'grand_total', 'items_count', 'created_at')

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grand_total = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'status_display', 'payment_method', 'is_paid',
                  'delivery_address', 'deliver_phone', 'delivery_name', 'comment',
                  'total_price', 'delivery_price', 'grand_total', 'items', 'created_at', 'updated_at')

class CreateOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    delivery_phone = serializers.CharField(max_length=20)
    delivery_name = serializers.CharField(max_length=100)
    payment_method = serializers.ChoiceField(choices=['cash', 'card', 'online'], default='cash')
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        user = self.context['request'].user
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise serializers.ValidationError('Корзина пуста')

        for item in cart.items.select_related('product').all():
            if item.product.stock < item.quantity:
                raise serializers.ValidationError(
                    f'Недостаточно товара "{item.product.name}" на складе. Доступно: {item.product.stock}'
                )

        data['cart'] = cart
        return data
