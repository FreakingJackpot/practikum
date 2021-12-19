from django.views.generic import ListView, DetailView, TemplateView
from django.http import HttpResponseRedirect

from .models import Category, Product, AttributeValue
from .forms import RequestForm


class IndexTemplateView(TemplateView):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        sales = Product.objects.prefetch_related('image').filter(discount_price__gt=0, active=True)[:9]
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales_categories = Category.objects.select_related('sale_image').filter(product__discount_price__gt=0,
                                                                                product__active=True)
        context['sales_categories'] = sales_categories
        return context


class ProductListView(ListView):
    ordering = 'name'
    template_name = 'catalog/list.html'

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])

        queryset = Product.objects.filter(category=self.category, active=True).order_by(self.ordering)
        if self.request.GET.get('sale'):
            queryset = queryset.filter(discount_price__gt=0)

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

        values = AttributeValue.objects.select_related('attribute').filter(product=product, value__isnull=False)

        sales_categories = Category.objects.select_related('sale_image').filter(product__discount_price__gt=0,
                                                                                product__active=True)

        return self.render_to_response({'product': product, 'values': values, 'sales_categories': sales_categories})


def process_request_form(request):
    if request.method == 'POST':
        redirect_url = request.POST.get('next')

        data = {'phone': request.POST.get('phone'), 'name': request.POST.get('name'),
                'comment': request.POST.get('comment')}
        form_data = RequestForm(data)

        if form_data.is_valid():
            form_data.save()
            redirect_url = request.POST.get('next')
            return HttpResponseRedirect(redirect_url)

        return HttpResponseRedirect(redirect_url)
