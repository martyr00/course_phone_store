# Generated by Django 5.0.4 on 2024-05-30 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_views'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telephone',
            name='recommended_price',
        ),
    ]
