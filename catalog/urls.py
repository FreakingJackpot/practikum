from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),
    path('<slug:slug>/', ProductListView.as_view(), name='product_list'),
    path('product_detail/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

]
