# Generated by Django 2.2.13 on 2020-06-14 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0019_selectfiches'),
    ]

    operations = [
        migrations.AddField(
            model_name='pays',
            name='num_insee',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]