# Generated by Django 3.2.8 on 2021-12-19 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20211209_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='url',
        ),
    ]
