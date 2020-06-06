# Generated by Django 2.2.12 on 2020-06-06 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0013_detail_formations'),
    ]

    operations = [
        migrations.AddField(
            model_name='mefoption',
            name='inscriptions',
            field=models.BooleanField(default=True, help_text="Indique si l'option est présentée aux candidats afin qu'ils la choisissent lors de l'inscription."),
            preserve_default=False,
        ),
    ]
