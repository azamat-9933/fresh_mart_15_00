from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product, Review, Wishlist
from .serializers import (CategorySerializer, ProductListSerializer,
                          ProductDetailSerializer,
                          ReviewSerializer, WishlistSerializer)

from drf_spectacular.utils import extend_schema

@extend_schema(tags=['products'])
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Category.objects.filter(is_active=True, parent=None).prefetch_related('children', 'products')
    pagination_class = None


@extend_schema(tags=['products'])
class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Category.objects.filter(is_active=True)
    lookup_field = 'slug'


@extend_schema(tags=['products'])
class ProductViewSet(viewsets.ReadOnlyModelViewSet):  # products  # product/(id)  #  product/(slug)
    permission_classes = (permissions.AllowAny,)
    search_fields = ('name', 'description', 'category__name')
    ordering_fields = ('price', 'created_at', 'name')
    ordering = ('-created_at',)

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_object(self):
        if self.kwargs.get(self.lookup_field, '').isdigit():
            return super().get_object()
        self.lookup_field = 'slug'
        return super().get_object()


    @extend_schema(tags=['products'])
    @action(detail=False, methods=['get'])  # products/featured/
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['products'])
    @action(detail=False, methods=['get'])  # products/new_arrivals/
    def new_arrivals(self, request):
        qs = self.get_queryset().filter(is_new=True)
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['products'])
    @action(detail=False, methods=['get'])  # products/new_arrivals/
    def on_sale(self, request):
        qs = self.get_queryset().filter(old_price__isnull=False)
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)


@extend_schema(tags=['reviews'])
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        product = generics.get_object_or_404(Product, pk=self.kwargs['product_pk'])
        serializer.save(user=self.request.user, product=product)


@extend_schema(tags=['reviews'])
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

@extend_schema(tags=['wishlist'])
class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # ← фикс: AnonymousUser при генерации схемы
        if getattr(self, 'swagger_fake_view', False):
            return Wishlist.objects.none()
        return Wishlist.objects.filter(
            user=self.request.user
        ).select_related('product', 'product__category')

@extend_schema(tags=['wishlist'])
class WishlistDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer  # ← добавили, было пусто
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)



