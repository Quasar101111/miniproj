# Generated by Django 5.0.7 on 2024-08-06 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_profile_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('tenant_id', models.AutoField(primary_key=True, serialize=False)),
                ('tenant_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('contact_number', models.CharField(max_length=50)),
                ('photo', models.ImageField(upload_to='tenant_photos/')),
                ('identity_proof', models.FileField(blank=True, null=True, upload_to='tenant_id/')),
                ('state', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
            ],
        ),
    ]