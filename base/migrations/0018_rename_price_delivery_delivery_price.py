# Generated by Django 5.0.4 on 2024-05-28 02:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_alter_delivery_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='price',
            new_name='delivery_price',
        ),
    ]
