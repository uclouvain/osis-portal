# Generated by Django 2.2.13 on 2021-10-25 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0084_auto_20210930_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='language',
            field=models.CharField(choices=[('fr-be', 'French'), ('en', 'English')], default='fr-be', max_length=30),
        ),
    ]
