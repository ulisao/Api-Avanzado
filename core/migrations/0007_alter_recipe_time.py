# Generated by Django 4.1 on 2022-08-27 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_recipe_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='time',
            field=models.IntegerField(),
        ),
    ]
