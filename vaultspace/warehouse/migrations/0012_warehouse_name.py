# Generated by Django 5.0.6 on 2024-10-13 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0011_alter_lease_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
