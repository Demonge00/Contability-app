# Generated by Django 5.1.1 on 2025-02-24 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_shop_taxes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='shop_taxes',
        ),
    ]
