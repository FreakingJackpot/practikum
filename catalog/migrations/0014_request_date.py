# Generated by Django 3.2.8 on 2022-01-08 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_auto_20220106_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
