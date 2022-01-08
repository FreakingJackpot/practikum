from tempfile import NamedTemporaryFile
from datetime import datetime

from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect

from .models import Category, Product, AttributeValue, Attribute, Image, Vendor, Color, Request, Order, Settings
from .forms import ExcelImportForm

from catalog.services.import_products_from_excel import ExcelProductImporter
from catalog.services.export_products import ExcelProductExporter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    change_list_template = "admin/product_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.import_excel),
            path('export-excel/', self.export_excel),
        ]
        return my_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES["excel_file"]
            error = ExcelProductImporter(excel_file).run()

            if error:
                self.message_user(request, error, level=messages.ERROR)
            else:
                self.message_user(request, "Excel файл успешно импортирован")
            return redirect("..")
        form = ExcelImportForm()
        payload = {"form": form}
        return render(request, 'admin/excel_form.html', payload)

    def export_excel(self, request):
        exporter = ExcelProductExporter()
        excel_file = exporter.run()

        with NamedTemporaryFile(prefix='mebel', suffix='xlsx') as tmp:
            excel_file.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mebel-%s.xlsx' % (
            datetime.strftime(datetime.now(), '%d-%m-%Y-%H-%M'))
        response['Cache-Control'] = 'no-cache,no-store,max-age=0,must-revalidate'
        response.content = stream

        return response

    def save_related(self, request, form, formsets, change):
        req_dict = vars(request)
        super().save_related(request, form, formsets, change)
        AttributeValue.objects.exclude(attribute__category__id__in=req_dict['_post']['category']).filter(
            product__vendor_code=req_dict['_post']['vendor_code']).delete()


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    exclude = ['url']


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        req_dict = vars(request)
        super().save_related(request, form, formsets, change)
        AttributeValue.objects.exclude(attribute__category__id__in=req_dict['_post']['category']).filter(
            attribute__name=req_dict['_post']['name']).delete()


admin.site.register(AttributeValue)
admin.site.register(Vendor)
admin.site.register(Color)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'date', 'status')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('phone', 'first_name', 'second_name', 'father_name', 'date', 'status')


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
