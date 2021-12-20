from django.conf import settings
from .models import Category


def categories(request):
    return {'category_list': Category.objects.select_related('image').all()}


def analitics(request):
    return {'GOOGLE_ANALYTICS_IDD': settings.GOOGLE_ANALYTICS_IDD}
