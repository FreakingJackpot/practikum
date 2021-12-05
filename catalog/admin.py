from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect

from .models import Category, Product, AttributeValue, Attribute, Image, Manufacturer, Color, Request, Order
from .forms import ExcelImportForm
from .import_products_from_excel import ExcelProductImporter


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


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    exclude = ['url']


admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(Manufacturer)
admin.site.register(Color)
admin.site.register(Request)
admin.site.register(Order)
