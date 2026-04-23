from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Category, Product, ProductImage, Review, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'description',
                  'parent', 'children', 'products_count')

    @extend_schema_field(serializers.ListField())   # ← тип для Swagger
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(
                obj.children.filter(is_active=True), many=True
            ).data
        return []

    @extend_schema_field(serializers.IntegerField())  # ← тип для Swagger
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt', 'order')


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'user', 'user_name', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'user', 'user_name', 'created_at')

    @extend_schema_field(serializers.CharField())  # ← тип для Swagger
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.SerializerMethodField()  # ← было ReadOnlyField
    in_stock = serializers.SerializerMethodField()          # ← было ReadOnlyField
    avg_rating = serializers.SerializerMethodField()        # ← было ReadOnlyField
    reviews_count = serializers.SerializerMethodField()     # ← было ReadOnlyField

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'category_name',
                  'price', 'old_price', 'discount_percent', 'image',
                  'unit', 'in_stock', 'stock', 'is_featured', 'is_new',
                  'avg_rating', 'reviews_count')

    @extend_schema_field(serializers.IntegerField())
    def get_discount_percent(self, obj):
        return obj.discount_percent

    @extend_schema_field(serializers.BooleanField())
    def get_in_stock(self, obj):
        return obj.in_stock

    @extend_schema_field(serializers.FloatField())
    def get_avg_rating(self, obj):
        return obj.avg_rating

    @extend_schema_field(serializers.IntegerField())
    def get_reviews_count(self, obj):
        return obj.reviews_count


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    discount_percent = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'description',
                  'price', 'old_price', 'discount_percent', 'image',
                  'images', 'unit', 'in_stock', 'stock', 'is_featured',
                  'is_new', 'avg_rating', 'reviews_count', 'reviews',
                  'created_at', 'updated_at')

    @extend_schema_field(serializers.IntegerField())
    def get_discount_percent(self, obj):
        return obj.discount_percent

    @extend_schema_field(serializers.BooleanField())
    def get_in_stock(self, obj):
        return obj.in_stock

    @extend_schema_field(serializers.FloatField())
    def get_avg_rating(self, obj):
        return obj.avg_rating

    @extend_schema_field(serializers.IntegerField())
    def get_reviews_count(self, obj):
        return obj.reviews_count


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ('id', 'product', 'product_id', 'added_at')
        read_only_fields = ('id', 'added_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)