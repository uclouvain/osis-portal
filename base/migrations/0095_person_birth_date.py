# Generated by Django 3.2.20 on 2023-11-06 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0094_alter_person_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]