# Generated by Django 3.2.8 on 2021-12-05 17:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Атрибут',
                'verbose_name_plural': 'Атрибуты',
                'db_table': 'attributes',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('slug', models.SlugField()),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'db_table': 'categories',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('hex', models.CharField(max_length=20, null=True)),
            ],
            options={
                'verbose_name': 'Цвет',
                'verbose_name_plural': 'Цвета',
                'db_table': 'colors',
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Название')),
                ('phone', models.PositiveBigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(70000000000), django.core.validators.MaxValueValidator(89999999999)], verbose_name='Номер телефона')),
                ('location', models.TextField()),
            ],
            options={
                'verbose_name': 'Производитель',
                'verbose_name_plural': 'Производители',
                'db_table': 'manufacturers',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=200, verbose_name='Фамилия')),
                ('father_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Отчество')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Итоговая цена')),
                ('phone', models.PositiveBigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(70000000000), django.core.validators.MaxValueValidator(89999999999)], verbose_name='Номер телефона')),
                ('comment', models.TextField()),
                ('status', models.CharField(choices=[('UNCOMPLETED', 'Необработан'), ('IN PROGRESS', 'В обработке'), ('PRODUCTION', 'Изготовление'), ('TRANSPORT', 'Транспортировка'), ('COMPLETED', 'Завершен'), ('REFUSAL', 'Отказ')], default='UNCOMPLETED', max_length=50, verbose_name='Статус заказа')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.PositiveBigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(70000000000), django.core.validators.MaxValueValidator(89999999999)], verbose_name='Номер телефона')),
                ('name', models.CharField(max_length=300, verbose_name='Имя')),
                ('comment', models.TextField(verbose_name='Комментарий')),
                ('status', models.CharField(choices=[('UNCOMPLETED', 'Необработан'), ('IN PROGRESS', 'В обработке'), ('COMPLETED', 'Завершен')], default='UNCOMPLETED', max_length=100, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Запрос',
                'verbose_name_plural': 'Запросы',
                'db_table': 'requests',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_code', models.CharField(max_length=100, unique=True, verbose_name='Артикул')),
                ('name', models.CharField(max_length=300, verbose_name='Название')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Цена')),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Цена со скидкой')),
                ('active', models.BooleanField(default=True, verbose_name='Активность товара')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='catalog.category', verbose_name='Категория')),
                ('color', models.ManyToManyField(blank=True, to='catalog.Color', verbose_name='Цвет')),
                ('manufacturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='catalog.manufacturer', verbose_name='Производитель')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'db_table': 'products',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Название')),
                ('image_path', models.FileField(upload_to='images/', verbose_name='Изображение')),
                ('url', models.CharField(blank=True, default='/media/images/<django.db.models.fields.files.FileField>', max_length=300, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image', to='catalog.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
                'db_table': 'images',
            },
        ),
        migrations.AddField(
            model_name='color',
            name='preview',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='color', to='catalog.image', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.image'),
        ),
        migrations.AddField(
            model_name='category',
            name='sale_image',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_sale_img', to='catalog.image'),
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='value', to='catalog.attribute', verbose_name='Атрибут')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prod_attr_value', to='catalog.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Значение атрибута',
                'verbose_name_plural': 'Значения атрибутов',
                'db_table': 'attribute_values',
            },
        ),
    ]
