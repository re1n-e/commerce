# Generated by Django 5.0.2 on 2024-04-12 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='listing',
            name='Active',
            field=models.BooleanField(default=True),
        ),
    ]