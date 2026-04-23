from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from products.serializers import ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()  # ← было ReadOnlyField

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price', 'added_at')
        read_only_fields = ('id', 'added_at')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()  # ← было ReadOnlyField
    total_price = serializers.SerializerMethodField()  # ← было ReadOnlyField

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'updated_at')

    @extend_schema_field(serializers.IntegerField())
    def get_total_items(self, obj):
        return obj.total_items

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()  # ← было ReadOnlyField

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price',
                  'quantity', 'total_price')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grand_total = serializers.SerializerMethodField()    # ← было ReadOnlyField
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'status_display', 'payment_met',
                  'is_paid', 'total_price', 'delivery_price',
                  'grand_total', 'items_count', 'created_at')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_grand_total(self, obj):
        return obj.grand_total

    @extend_schema_field(serializers.IntegerField())
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grand_total = serializers.SerializerMethodField()  # ← было ReadOnlyField

    class Meta:
        model = Order
        fields = ('id', 'status', 'status_display', 'payment_met',
                  'is_paid', 'delivery_address', 'delivery_phone',
                  'delivery_name', 'comment', 'total_price',
                  'delivery_price', 'grand_total', 'items',
                  'created_at', 'updated_at')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_grand_total(self, obj):
        return obj.grand_total


class CreateOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    delivery_phone = serializers.CharField(max_length=20)
    delivery_name = serializers.CharField(max_length=100)
    payment_method = serializers.ChoiceField(
        choices=['cash', 'card', 'online'], default='cash'
    )
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        user = self.context['request'].user
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise serializers.ValidationError('Корзина пуста')
        for item in cart.items.select_related('product').all():
            if item.product.stock < item.quantity:
                raise serializers.ValidationError(
                    f'Недостаточно "{item.product.name}". '
                    f'Доступно: {item.product.stock}'
                )
        data['cart'] = cart
        return data