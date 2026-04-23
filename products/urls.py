from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryListView, CategoryDetailView, ProductViewSet,
                    ReviewCreateView, ReviewDetailView, WishlistView, WishlistDeleteView)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('products/<int:product_pk>/reviews/', ReviewCreateView.as_view(), name='review_create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', WishlistDeleteView.as_view(), name='wishlist_delete'),
]