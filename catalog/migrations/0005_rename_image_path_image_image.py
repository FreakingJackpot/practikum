# Generated by Django 3.2.8 on 2021-12-19 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_remove_image_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='image_path',
            new_name='image',
        ),
    ]
