# Generated by Django 5.1.2 on 2024-10-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveBigIntegerField(blank=True, choices=[(1, 'Restaurant'), (2, 'Customer')], null=True),
        ),
    ]
