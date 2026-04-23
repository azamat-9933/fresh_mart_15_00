from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_met', 'is_paid',
                    'grand_total', 'created_at')
    list_editable = ('status', 'is_paid')
    list_filter = ('status', 'payment_met', 'is_paid')
    search_fields = ('user__username', 'delivery_name',
                     'delivery_phone')
    inlines = [OrderItemInline]
    readonly_fields = ('total_price', 'delivery_price',
                       'created_at', 'updated_at')
