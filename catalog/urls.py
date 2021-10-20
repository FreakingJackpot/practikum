from django.urls import path
from .views import get_category_list, ProductListView

urlpatterns = [
    path('', get_category_list, name='catalog'),
    path('<slug:slug>/', get_category_list, name='sub-catalog'),
    path('product_list/<slug:slug>/', ProductListView.as_view(), name='product_list'),
]
