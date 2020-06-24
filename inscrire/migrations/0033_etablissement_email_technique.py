# Generated by Django 2.2 on 2020-06-24 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0032_auto_20200624_0824'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='email_technique',
            field=models.EmailField(blank=True, default='', help_text='Adresse à contacter en cas de problème technique', max_length=254, verbose_name='email à contacter en cas de problème technique'),
        ),
    ]
