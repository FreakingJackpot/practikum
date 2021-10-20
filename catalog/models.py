from django.db import models
from django.urls import reverse
from djmoney.models.fields import MoneyField
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

ATTRIBUTE_TYPE_CHOICES = [
    ('ST', 'static'),
    ('RN', 'ranged'),
    ('BL', 'bool'),
]

ATTRIBUTE_VALUE_TYPE_CHOICES = [
    ('FL', 'float'),
    ('BL', 'bool'),
    ('INT', 'integer'),
    ('STR', 'string')
]


class Category(MPTTModel):
    name = models.CharField(max_length=200, verbose_name='Название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
    slug = models.SlugField()

    class Meta:
        ordering = ('id',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.title
            self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    vendor_code = models.CharField(max_length=50)
    name = models.CharField(max_length=300)
    category = TreeForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    price = MoneyField(max_digits=15, decimal_places=2, default_currency='RUB')
    description = models.TextField()
    stock = models.PositiveIntegerField()
    slug = models.SlugField(default=slugify(name, allow_unicode=True))

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.vendor_code}, {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.name
            self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.slug)])


class Attribute(models.Model):
    type = models.CharField(max_length=10, choices=ATTRIBUTE_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    category = models.ManyToManyField(Category, related_name='product_attribute')

    class Meta:
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ATTRIBUTE_VALUE_TYPE_CHOICES)
    label = models.CharField(max_length=40, null=True)
    value = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.value} {self.label}'
