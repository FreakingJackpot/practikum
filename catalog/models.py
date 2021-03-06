from django.db import models
from django.urls import reverse
from pytils.translit import slugify

REQUESTS_CHOICES = (
    ('UNCOMPLETED', 'Необработан'),
    ('IN PROGRESS', 'В обработке'),
    ('COMPLETED', 'Завершен'),
)

ORDER_STATUS_CHOICES = (
    ('UNCOMPLETED', 'Необработан'),
    ('IN PROGRESS', 'В обработке'),
    ('PRODUCTION', 'Изготовление'),
    ('TRANSPORT', 'Транспортировка'),
    ('COMPLETED', 'Завершен'),
    ('REFUSAL', 'Отказ')
)


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField()
    image = models.OneToOneField('Image', on_delete=models.SET_NULL, null=True, blank=True)
    sale_image = models.OneToOneField('Image', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='category_sale_img')

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
            value = self.name
            self.slug = slugify(value)
        super().save(*args, **kwargs)

    @classmethod
    def get_sales_categories(cls):
        return cls.objects.select_related('sale_image').filter(product__discount_price__gt=0,
                                                               product__active=True,
                                                               sale_image__isnull=False)


class Image(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', null=True, blank=True)
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар', null=True,
                                related_name='image', blank=True)

    class Meta:
        db_table = 'images'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        if self.name:
            return self.name

        return self.image.name


class Color(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    preview = models.OneToOneField(Image, verbose_name='Изображение', on_delete=models.CASCADE, related_name='color',
                                   null=True, blank=True)

    class Meta:
        db_table = 'colors'
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=300, verbose_name='Название')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    location = models.TextField()

    class Meta:
        db_table = 'vendors'
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class Product(models.Model):
    vendor_code = models.CharField(max_length=100, verbose_name='Артикул', unique=True)
    name = models.CharField(max_length=300, verbose_name='Название')
    vendor = models.ForeignKey(Vendor, verbose_name='Производитель', null=True, related_name='product',
                               on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    color = models.ManyToManyField(Color, verbose_name='Цвет', blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    discount_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0, blank=True,
                                         verbose_name='Цена со скидкой')
    active = models.BooleanField(default=True, verbose_name='Активность товара')

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.vendor_code}, {self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.vendor_code)
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[str(self.slug)])

    def get_colors(self):
        colors = list(self.color.all())

        return '/'.join(color.name for color in colors)

    @classmethod
    def get_sales_for_sales_bar(cls):
        sales = cls.objects.prefetch_related('image').filter(discount_price__gt=0, active=True)[:9]

        paginated_sales = [] if sales else None
        page = -1

        for index, sale in enumerate(sales):
            if not index or index % 3 == 0:
                paginated_sales.append([])
                page += 1

            paginated_sales[page].append({'obj': sale, 'image': sale.image.first()})

        return paginated_sales

    def get_attributes_values(self):
        return AttributeValue.objects.select_related('attribute').filter(product=self, value__isnull=False)


class Attribute(models.Model):
    category = models.ManyToManyField(Category, related_name='attribute', verbose_name='Категория', blank=True)
    name = models.CharField(max_length=300, verbose_name='Название')

    class Meta:
        db_table = 'attributes'
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name='Атрибут', related_name='value')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='prod_attr_value')
    value = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'attribute_values'
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибутов'

    def __str__(self):
        return f'{self.attribute.name} : {self.product.vendor_code}'


class Request(models.Model):
    phone = models.CharField(max_length=20, null=True, verbose_name='Номер телефона', blank=True)
    name = models.CharField(max_length=300, verbose_name='Имя')
    comment = models.TextField(verbose_name='Комментарий')
    status = models.CharField(max_length=100, choices=REQUESTS_CHOICES, default='UNCOMPLETED', verbose_name='Статус')
    date = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Дата создания запроса')

    class Meta:
        db_table = 'requests'
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'


class Order(models.Model):
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Фамилия')
    father_name = models.CharField(max_length=200, verbose_name='Отчество', null=True, blank=True)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                      verbose_name="Итоговая цена")
    phone = models.CharField(max_length=20, null=True, verbose_name='Номер телефона', blank=True)
    address = models.TextField(verbose_name='Адрес доставки', null=True, blank=True)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.CharField(max_length=50, verbose_name='Статус заказа', choices=ORDER_STATUS_CHOICES,
                              default='UNCOMPLETED')
    products = models.ManyToManyField(Product, verbose_name='Заказанные продукты')
    date = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Settings(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()
