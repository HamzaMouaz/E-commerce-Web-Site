# Generated by Django 5.1 on 2024-08-23 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyApp', '0005_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='sales',
            field=models.IntegerField(default=0),
        ),
    ]
