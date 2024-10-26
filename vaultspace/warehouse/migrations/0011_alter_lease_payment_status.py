# Generated by Django 5.0.6 on 2024-10-12 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0010_lease_lessor_signature_lease_tenant_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lease',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Rejected', 'Rejected'), ('Expired', 'Expired')], default='Pending', max_length=10),
        ),
    ]