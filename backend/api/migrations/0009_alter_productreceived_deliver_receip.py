# Generated by Django 5.1.1 on 2025-01-26 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_package_status_of_processing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productreceived',
            name='deliver_receip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivered_products', to='api.deliverreceip'),
        ),
    ]
