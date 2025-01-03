# Generated by Django 5.0.6 on 2024-10-09 09:25

import warehouse.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0009_alter_warehouse_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='lease',
            name='lessor_signature',
            field=models.ImageField(blank=True, null=True, upload_to=warehouse.models.upload_signature_path),
        ),
        migrations.AddField(
            model_name='lease',
            name='tenant_signature',
            field=models.ImageField(blank=True, null=True, upload_to=warehouse.models.upload_signature_path),
        ),
    ]
