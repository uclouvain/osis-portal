# Generated by Django 2.2.13 on 2021-06-22 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0009_auto_20190723_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='decree',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='parent',
        ),
        migrations.DeleteModel(
            name='GradeType',
        ),
        migrations.DeleteModel(
            name='Decree',
        ),
        migrations.DeleteModel(
            name='Domain',
        ),
    ]