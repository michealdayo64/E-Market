# Generated by Django 2.2.7 on 2021-05-09 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eMarket', '0003_auto_20210509_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='photo',
            field=models.ImageField(blank=True, default=False, upload_to='media'),
        ),
    ]
