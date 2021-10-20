from django.contrib import admin
from django.urls import path, include, re_path
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    path('__debug__/', include(debug_toolbar.urls)),

]
