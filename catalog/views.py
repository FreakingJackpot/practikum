from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from .models import Category, Product


def get_category_list(request, slug=None):
    if slug:
        categories = Category.objects.filter(parent__slug=slug)
    else:
        categories = Category.objects.filter(parent=None)

    if not categories.exists():
        return redirect(reverse('product_list', kwargs={'slug': slug}))

    return render(request, 'catalog/categories.html', {'categories': categories})


class ProductListView(ListView):
    template_name = 'catalog/product_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        queryset = Product.objects.filter(category__slug=slug)
        return queryset
