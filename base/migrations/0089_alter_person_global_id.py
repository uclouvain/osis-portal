# Generated by Django 3.2.20 on 2023-09-04 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0088_delete_learningcontainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='global_id',
            field=models.CharField(blank=True, db_index=True, max_length=10, null=True),
        ),
    ]
