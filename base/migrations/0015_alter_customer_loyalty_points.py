# Generated by Django 4.2.7 on 2024-01-08 07:57

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_tranzaction_object_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='loyalty_points',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10),
        ),
    ]
