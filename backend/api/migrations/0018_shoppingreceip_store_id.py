# Generated by Django 5.1.1 on 2025-03-08 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_order_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingreceip',
            name='store_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
