# Generated by Django 2.2 on 2020-06-24 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0031_auto_20200623_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='photo_hauteur',
            field=models.PositiveSmallIntegerField(default=45, help_text="Hauteur de la photo d'identité; seul le ratio hauteur/largeur est pris en compte."),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='photo_largeur',
            field=models.PositiveSmallIntegerField(default=35, help_text="Largeur de la photo d'identité; seul le ratio hauteur/largeur est pris en compte."),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='photo_size_max',
            field=models.PositiveSmallIntegerField(default=200, help_text="Poids maximal des photos d'identités en ko."),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='tolerance_ratio',
            field=models.PositiveSmallIntegerField(default=10, help_text='Pourcentage de tolérance sur le ratio hauteur/largeur.'),
        ),
    ]