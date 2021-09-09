# Generated by Django 2.2.13 on 2021-08-30 08:28

from django.db import migrations, models


def edit_gender_values(apps, schema_editor):
    Person = apps.get_model('base', 'Person')
    persons_to_update = []
    for person in Person.objects.all():
        if person.gender == 'M':
            person.gender = 'H'
            persons_to_update.append(person)

    Person.objects.bulk_update(persons_to_update, ['gender'], batch_size=1000)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0073_auto_20210615_1557'),
    ]

    operations = [
        migrations.RunPython(edit_gender_values),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(blank=True, choices=[('F', 'Female'), ('H', 'Male'), ('X', 'Other')], default='',
                                   max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='external_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='global_id',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='middle_name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone_mobile',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]