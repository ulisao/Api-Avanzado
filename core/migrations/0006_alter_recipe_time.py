# Generated by Django 4.1 on 2022-08-27 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_ingredient_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='time',
            field=models.CharField(max_length=3),
        ),
    ]
