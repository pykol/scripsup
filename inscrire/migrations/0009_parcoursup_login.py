# Generated by Django 2.2.12 on 2020-05-24 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0008_etab_inscription_help'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parcoursupuser',
            name='user',
        ),
        migrations.AddField(
            model_name='parcoursupuser',
            name='password',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcoursupuser',
            name='username',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
