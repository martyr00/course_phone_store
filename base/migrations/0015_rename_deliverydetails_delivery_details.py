# Generated by Django 5.0.4 on 2024-05-26 05:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_order_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DeliveryDetails',
            new_name='delivery_details',
        ),
    ]
