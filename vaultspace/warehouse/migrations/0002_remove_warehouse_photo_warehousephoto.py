# Generated by Django 5.0.7 on 2024-08-03 18:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='photo',
        ),
        migrations.CreateModel(
            name='WarehousePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='warehouse_photos/')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='warehouse.warehouse')),
            ],
        ),
    ]
