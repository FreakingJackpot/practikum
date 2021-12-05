from .models import Category


def categories(request):
    return {'category_list': Category.objects.select_related('image').all()}


