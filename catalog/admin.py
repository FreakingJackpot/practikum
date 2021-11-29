from django.contrib import admin

from .models import Category, Product, AttributeValue, Attribute, Image, Manufacturer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    exclude = ['url']


admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(Manufacturer)
