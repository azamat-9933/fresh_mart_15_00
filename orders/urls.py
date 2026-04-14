from django.urls import path

from .views import (CartView, CartAddView, CartItemUpdateView, CartClearView,
                    OrderListView, OrderCreateView, OrderDetailView, OrderCancelView)

urlpatterns = [
    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='cart_add'),
    path('cart/items/<int:pk>/', CartItemUpdateView.as_view(), name='cart_item'),
    path('cart/clear/', CartClearView.as_view(), name='cart_clear'),
    # Orders
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
]
