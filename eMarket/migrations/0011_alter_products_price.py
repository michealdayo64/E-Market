# Generated by Django 4.1.6 on 2023-02-20 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eMarket', '0010_alter_products_discount_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
