# Generated by Django 2.2.12 on 2020-05-27 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0010_parcoursup_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='commune',
            field=models.ForeignKey(default='75056', on_delete=django.db.models.deletion.PROTECT, to='inscrire.Commune'),
            preserve_default=False,
        ),
    ]
