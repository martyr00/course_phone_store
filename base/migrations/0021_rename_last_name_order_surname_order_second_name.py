# Generated by Django 5.0.4 on 2024-05-28 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_remove_order_full_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='surname',
        ),
        migrations.AddField(
            model_name='order',
            name='second_name',
            field=models.CharField(blank=True, null=True),
        ),
    ]