# Generated by Django 2.2.13 on 2021-06-15 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0072_delete_learningcomponentyear'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutor',
            options={'permissions': (('can_access_attribution_application', 'Can access attribution application'), ('can_access_attribution', 'Can access attribution'))},
        ),
    ]