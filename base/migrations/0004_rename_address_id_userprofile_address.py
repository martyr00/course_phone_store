# Generated by Django 5.0.4 on 2024-05-14 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_telephone_id_telephoneimage_telephone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='address_id',
            new_name='address',
        ),
    ]
