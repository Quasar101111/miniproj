# Generated by Django 5.0.6 on 2025-01-13 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0013_warehousereview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehousereview',
            name='rating',
            field=models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]),
        ),
    ]
