# Generated by Django 5.0.6 on 2024-08-21 23:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_lease'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lease',
            name='created_at',
        ),
    ]