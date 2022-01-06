from django.views.generic import ListView, DetailView, TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from practikum.settings import SENDGRID_API_KEY, SENDGRID_MAIL_FROM

from .models import Category, Product, AttributeValue, Settings
from .forms import RequestForm


class IndexTemplateView(TemplateView):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.extra_context is not None:
            context.update(self.extra_context)

        context['sales'] = Product.get_sales_for_sales_bar()

        return context


class AboutTemplateView(TemplateView):
    template_name = 'catalog/about.html'


class DeliveryTemplateView(TemplateView):
    template_name = 'catalog/delivery.html'


class ContactTemplateView(TemplateView):
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales_categories = Category.get_sales_categories()
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

        values = product.get_attributes_values()

        sales_categories = Category.get_sales_categories()

        return self.render_to_response({'product': product, 'values': values, 'sales_categories': sales_categories})


def process_request_form(request):
    redirect_url = request.POST.get('next')
    if request.method == 'POST':

        data = {'phone': request.POST.get('phone'), 'name': request.POST.get('name'),
                'comment': request.POST.get('comment')}
        form_data = RequestForm(data)

        if form_data.is_valid():
            request_obj = form_data.save()

            setting = Settings.objects.get(key='request_emails')
            emails = setting.value.split(',')

            content = request.build_absolute_uri(reverse('admin:catalog_request_change', args=(request_obj.id,)))

            message = Mail(from_email=SENDGRID_MAIL_FROM, to_emails=emails, subject='Новая заявка',
                           html_content=content)

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        return HttpResponseRedirect(redirect_url)

    return HttpResponseRedirect(redirect_url)
