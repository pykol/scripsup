# Generated by Django 2.2.13 on 2020-06-20 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0025_auto_20200619_2243'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='email_pieces_justificatives',
            field=models.EmailField(blank=True, default='', help_text='Adresse à laquelle le candidat doit envoyer les pièces justificatives', max_length=254, verbose_name='adresse e-mail pièces justificatives'),
        ),
        migrations.AddField(
            model_name='formation',
            name='email_pieces_justificatives',
            field=models.EmailField(blank=True, default='', help_text='Adresse spécifique à cette formation à laquelle le candidat doit envoyer les pièces justificatives', max_length=254, verbose_name='adresse e-mail pièces justificatives'),
        ),
        migrations.AddField(
            model_name='piecejustificative',
            name='descriptif',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='piecejustificative',
            name='email_specifique',
            field=models.EmailField(default='', help_text='Adresse spécifique à laquelle le candidat doit envoyer cette pièce justificative', max_length=254, verbose_name='adresse e-mail pour cette pièce'),
        ),
        migrations.AlterField(
            model_name='piecejustificative',
            name='etablissement',
            field=models.ForeignKey(blank=True, default=None, help_text='Ne pas renseigner si la pièce est spécifique à une formation', null=True, on_delete=django.db.models.deletion.CASCADE, to='inscrire.Etablissement'),
        ),
        migrations.AlterField(
            model_name='piecejustificative',
            name='formation',
            field=models.ForeignKey(blank=True, default=None, help_text='Renseigner si la pièce est spécifique à cette formation', null=True, on_delete=django.db.models.deletion.CASCADE, to='inscrire.Formation'),
        ),
        migrations.AlterField(
            model_name='piecejustificative',
            name='modalite',
            field=models.PositiveSmallIntegerField(choices=[(1, 'obligatoire'), (2, 'facultative')], default=1, verbose_name='modalité'),
        ),
    ]
