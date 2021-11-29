from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField()
    image = models.OneToOneField('Image', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'categories'
        ordering = ('id',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_list', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            value = self.title
            self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class Image(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', null=True, blank=True)
    image_path = models.ImageField(upload_to='images/', verbose_name='Изображение')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар', null=True,
                                related_name='image', blank=True)
    url = models.CharField(max_length=300, null=True, blank=True, default=f'{settings.MEDIA_URL}images/{image_path}', )

    class Meta:
        db_table = 'images'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.url = f'{settings.MEDIA_URL}images/{self.image_path}'
        super(Image, self).save(*args, **kwargs)


class Color(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    hex = models.CharField(max_length=20, null=True)
    preview = models.OneToOneField(Image, verbose_name='Изображение', on_delete=models.CASCADE, related_name='color')

    class Meta:
        db_table = 'colors'
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=300, verbose_name='Название')
    phone = models.PositiveBigIntegerField(null=True, verbose_name='Номер телефона',
                                           validators=[MinValueValidator(70000000000),
                                                       MaxValueValidator(89999999999)], blank=True)
    location = models.TextField()


class Product(models.Model):
    vendor_code = models.CharField(max_length=100, verbose_name='Артикул')
    name = models.CharField(max_length=300, verbose_name='Название')
    manufacturer = models.ForeignKey(Manufacturer, verbose_name='Производитель', null=True, related_name='product',
                                     on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    color = models.ManyToManyField(Color, verbose_name='Цвет', null=True, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    discount_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.vendor_code}, {self.name}'

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


class Attribute(models.Model):
    name = models.CharField(max_length=300, verbose_name='Название')

    class Meta:
        db_table = 'attributes'
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name='Аттрибут', related_name='value')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='prod_attr_value')
    value = models.TextField()

    class Meta:
        db_table = 'attribute_values'
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибутов'

    def __str__(self):
        return f'{self.attribute.name} : {self.product.vendor_code}'
