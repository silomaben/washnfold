# Generated by Django 4.2.7 on 2023-11-28 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_tranzaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
