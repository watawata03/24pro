# Generated by Django 5.1.1 on 2024-10-08 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0002_category_alter_product_id_alter_product_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='popularity',
            field=models.IntegerField(default=0),
        ),
    ]