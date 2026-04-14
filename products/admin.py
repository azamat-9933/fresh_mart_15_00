from django.contrib import admin

from .models import Category, Product, ProductImage, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'order', 'products_count')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active', 'parent')

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Товаров'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'stock', 'is_active', 'is_featured', 'is_new')
    list_editable = ('price', 'stock', 'is_active', 'is_featured', 'is_new')
    list_filter = ('category', 'is_active', 'is_featured', 'is_new', 'unit')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')
