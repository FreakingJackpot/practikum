from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

from catalog.views import IndexTemplateView, AboutTemplateView, DeliveryTemplateView, ContactTemplateView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', IndexTemplateView.as_view(), name='index'),
                  path('about/', AboutTemplateView.as_view(), name='about'),
                  path('delivery/', DeliveryTemplateView.as_view(), name='delivery'),
                  path('contact/', ContactTemplateView.as_view(), name='contact'),
                  path('catalog/', include('catalog.urls')),
                  path('__debug__/', include(debug_toolbar.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
