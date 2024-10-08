# Generated by Django 5.0.7 on 2024-08-03 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0006_profile_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('warehouse_id', models.AutoField(primary_key=True, serialize=False)),
                ('area', models.CharField(max_length=50)),
                ('ownership_documents', models.CharField(max_length=50)),
                ('facilities', models.CharField(max_length=255)),
                ('photo', models.CharField(max_length=60)),
                ('year_built', models.DateField()),
                ('landmarks', models.CharField(blank=True, max_length=255, null=True)),
                ('rental_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('terms_cond', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.location')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.lessor')),
            ],
        ),
    ]
