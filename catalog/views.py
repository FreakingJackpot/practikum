from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Prefetch
from .models import Category, Product, AttributeValue, Image


class IndexTemplateView(TemplateView):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        sales = Product.objects.prefetch_related('image').filter(discount_price__gt=0)[:9]
        kwargs['sales'] = [[], ] if sales else None
        page = 0

        for index, sale in enumerate(sales):
            if index != 0 and index % 3 == 0:
                kwargs['sales'].append([])
                page += 1
            kwargs['sales'][page].append({'obj': sale, 'image': sale.image.first()})

        return kwargs


class AboutTemplateView(TemplateView):
    template_name = 'catalog/about.html'


class DeliveryTemplateView(TemplateView):
    template_name = 'catalog/delivery.html'


class ContactTemplateView(TemplateView):
    template_name = 'catalog/contacts.html'


class ProductListView(ListView):
    ordering = 'name'
    paginate_by = 10
    template_name = 'catalog/list.html'

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Product.objects.filter(category=self.category).order_by(self.ordering)
        print(queryset[0].image.all()[0].url)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductDetailView(DetailView):
    template_name = 'catalog/product_detail.html'

    def get(self, request, *args, **kwargs):
        product = Product.objects.prefetch_related('color__preview', 'image').select_related(
            'category', 'manufacturer').get(slug=kwargs['slug'])
        values = AttributeValue.objects.select_related('attribute').filter(product=product)

        return self.render_to_response({'product': product, 'values': values})
