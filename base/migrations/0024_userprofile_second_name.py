# Generated by Django 5.0.4 on 2024-06-01 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_remove_telephone_recommended_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='second_name',
            field=models.CharField(blank=True, null=True),
        ),
    ]
