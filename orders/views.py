from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (CartSerializer, AddToCartSerializer, CartItemSerializer,
                          OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer)
# ======================================================================================================

@extend_schema(tags=['cart'])
class CartView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

@extend_schema(tags=['cart'])
class CartAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'error': f'Доступно только {product.stock} единиц'},
                            status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        if item.quantity > product.stock:
            item.quantity = product.stock

        item.save()

        return Response({
            'message': 'Товар добавлен в корзину',
            'cart': CartSerializer(cart).data
        })

@extend_schema(tags=['cart'])
class CartItemUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        quantity = request.data.get('quantity', item.quantity)
        if int(quantity) < 1:
            item.delete()
            return Response({'message': 'Товар удалён из корзины'})

        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)


@extend_schema(tags=['cart'])
class CartClearView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Корзина очищена'})


@extend_schema(tags=['orders'])
class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


@extend_schema(tags=['orders'])
class OrderCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cart = data['cart']

        # Calculate total
        total = sum(item.total_price for item in cart.items.all())
        delivery_price = 0 if total >= 100000 else 15000  # free delivery over 100k

        order = Order.objects.create(
            user=request.user,
            delivery_address=data['delivery_address'],
            delivery_phone=data['delivery_phone'],
            delivery_name=data['delivery_name'],
            payment_method=data['payment_method'],
            comment=data.get('comment', ''),
            total_price=total,
            delivery_price=delivery_price,
        )


        # Create order items and reduce stock
        for cart_item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
            )
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Clear cart
        cart.delete()

        return Response({
            'message': 'Заказ успешно оформлен!',
            'order': OrderDetailSerializer(order).data
        }, status=status.HTTP_201_CREATED)



@extend_schema(tags=['orders'])
class OrderDetailView(generics.RetrieveAPIView):
    """Детали заказа"""
    serializer_class = OrderDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

class OrderCancelView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ('pending', 'confirmed'):
            return Response({'error': 'Невозможно отменить заказ на данном этапе'}, status=status.HTTP_400_BAD_REQUEST)

        # Restore stock
        with transaction.atomic():
            for item in order.items.select_related('product').all():
                item.product.stock += item.quantity
                item.product.save()
            order.status = 'cancelled'
            order.save()

        return Response({'message': 'Заказ отменён', 'order': OrderDetailSerializer(order).data})










