# Generated by Django 5.0.4 on 2024-05-19 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_rename_telephone_id_comment_telephone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='full_price',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
