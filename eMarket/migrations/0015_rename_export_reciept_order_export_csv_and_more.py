# Generated by Django 4.1.6 on 2023-02-22 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eMarket', '0014_order_export_reciept'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='export_reciept',
            new_name='export_csv',
        ),
        migrations.AddField(
            model_name='order',
            name='export_excel',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='export_pdf',
            field=models.BooleanField(default=False),
        ),
    ]