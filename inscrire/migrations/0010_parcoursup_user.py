# Generated by Django 2.2.12 on 2020-05-24 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscrire', '0009_parcoursup_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parcoursupuser',
            name='password',
        ),
        migrations.AddField(
            model_name='parcoursupuser',
            name='user',
            field=models.OneToOneField(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inscrireuser',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'direction'), (2, 'secrétariat'), (3, 'professeur'), (4, 'vie scolaire'), (5, 'intendance'), (6, 'étudiant'), (7, 'Parcoursup')], verbose_name='rôle'),
        ),
    ]
