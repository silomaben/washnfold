# Generated by Django 4.2.7 on 2023-12-12 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='loyalty_points',
            field=models.FloatField(default=0.0),
        ),
    ]