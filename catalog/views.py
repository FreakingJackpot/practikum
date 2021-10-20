from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import Category, Product, AttributeValue


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/categories.html'


class ProductListView(ListView):
    ordering = 'id'
    paginate_by = 10
    template_name = 'catalog/product_list.html'

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        leafnodes = self.category.get_leafnodes()

        if leafnodes:
            queryset = Product.objects.filter(category__in=leafnodes)
        else:
            queryset = Product.objects.filter(category=self.category)

        queryset = queryset.order_by(self.ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductDetailView(DetailView):
    template_name = 'catalog/product_detail.html'

    def get(self, request, *args, **kwargs):
        product = Product.objects.select_related('category').get(slug=kwargs['slug'])
        values = AttributeValue.objects.select_related('attribute').filter(product=product)
        return self.render_to_response({'product': product, 'values': values})
