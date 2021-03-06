# Generated by Django 2.2.12 on 2020-05-11 15:57

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import inscrire.models.fiches
import inscrire.models.fields
import localflavor.generic.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscrireUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='adresse e-mail')),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'direction'), (2, 'secrétariat'), (3, 'professeur'), (4, 'vie scolaire'), (5, 'intendance'), (6, 'étudiant')], verbose_name='rôle')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Candidat',
            fields=[
                ('genre', models.PositiveSmallIntegerField(choices=[(1, 'homme'), (2, 'femme')])),
                ('last_name', models.CharField(max_length=100, verbose_name='nom')),
                ('first_name', models.CharField(max_length=100, verbose_name='prénom')),
                ('telephone', models.CharField(blank=True, default='', max_length=20, verbose_name='téléphone')),
                ('telephone_mobile', models.CharField(blank=True, default='', max_length=20, verbose_name='téléphone mobile')),
                ('adresse', models.TextField(blank=True, default='(Inconnue)')),
                ('dossier_parcoursup', models.IntegerField(primary_key=True, serialize=False, verbose_name='numéro Parcoursup')),
                ('date_naissance', models.DateField(blank=True, null=True, verbose_name='date de naissance')),
                ('ine', models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name="INE (numéro d'étudiant)")),
                ('bac_date', models.DateField(blank=True, null=True)),
                ('bac_serie', models.CharField(blank=True, max_length=8, null=True)),
                ('bac_mention', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'passable'), (1, 'assez bien'), (2, 'bien'), (3, 'très bien')], null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Commune',
            fields=[
                ('code_insee', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('nom_clair', models.CharField(max_length=200)),
                ('nom_riche', models.CharField(max_length=200)),
                ('libelle', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Etablissement',
            fields=[
                ('numero_uai', inscrire.models.fields.Lettre23Field(length=8, primary_key=True, serialize=False, unique=True, verbose_name='UAI')),
                ('nom', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, verbose_name='adresse e-mail')),
            ],
        ),
        migrations.CreateModel(
            name='Fiche',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valide', models.BooleanField(default=False)),
                ('etat', models.PositiveSmallIntegerField(choices=[(1, 'fiche à compléter'), (2, 'fiche confirmée'), (3, 'validée par le gestionnaire'), (4, 'annulée')], default=1, verbose_name='état')),
                ('candidat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Candidat')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_inscrire.fiche_set+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('code_parcoursup', models.SmallIntegerField(unique=True)),
                ('groupe_parcoursup', models.SmallIntegerField()),
                ('slug', models.SlugField(unique=True)),
                ('code_mef', models.CharField(max_length=11)),
                ('etablissement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Etablissement')),
            ],
        ),
        migrations.CreateModel(
            name='MefMatiere',
            fields=[
                ('code', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('code_gestion', models.CharField(max_length=10)),
                ('libelle_court', models.CharField(max_length=100)),
                ('libelle_long', models.CharField(max_length=100)),
                ('libelle_edition', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ParcoursupMessageEnvoyeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Pays',
            fields=[
                ('code_iso2', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('code_iso3', models.CharField(max_length=3, unique=True)),
                ('num_iso', models.PositiveSmallIntegerField(unique=True)),
                ('libelle', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('code', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('libelle_court', models.CharField(max_length=200)),
                ('libelle_long', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FicheBourse',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('boursier', models.BooleanField(default=False)),
                ('echelon', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='échelon')),
                ('enfants_charge', models.PositiveSmallIntegerField(default=1, verbose_name="nombre d'enfants à charge (y compris l'étudiant)")),
                ('enfants_secondaire', models.PositiveSmallIntegerField(default=0, verbose_name="nombre d'enfants en lycée ou en collège")),
                ('enfants_etablissement', models.PositiveSmallIntegerField(default=1, verbose_name="nombre d'enfants dans l'établissement")),
                ('attribution_bourse', models.FileField(blank=True, null=True, upload_to=inscrire.models.fiches.FicheBourse._attribution_bourse_upload_to, verbose_name="copie de l'attestation conditionnelle de bourse")),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheCesure',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheHebergement',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('regime', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'externe'), (1, 'demi-pensionnaire'), (2, 'interne externé'), (3, 'interne')], null=True, verbose_name='régime')),
                ('iban', localflavor.generic.models.IBANField(blank=True, include_countries=('FR',), max_length=34, null=True, use_nordea_extensions=False)),
                ('bic', localflavor.generic.models.BICField(blank=True, max_length=11, null=True)),
                ('titulaire_compte', models.CharField(blank=True, default='', max_length=200)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheInternat',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('message', models.TextField(blank=True, default='', verbose_name='demandes particulières')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheReglement',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('signature_reglement', models.DateTimeField(blank=True, null=True, verbose_name='signature du règlement intérieur')),
                ('autorisation_parents_eleves', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='Voeu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('etat', models.PositiveSmallIntegerField(choices=[(0, "en liste d'attente"), (1, 'accepté avec autres vœux en attente'), (2, 'accepté définitivement'), (3, 'refusé par le candidat')])),
                ('internat', models.BooleanField()),
                ('cesure', models.BooleanField()),
                ('candidat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Candidat')),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Formation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResponsableLegal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.PositiveSmallIntegerField(choices=[(1, 'homme'), (2, 'femme')])),
                ('last_name', models.CharField(max_length=100, verbose_name='nom')),
                ('first_name', models.CharField(max_length=100, verbose_name='prénom')),
                ('telephone', models.CharField(blank=True, default='', max_length=20, verbose_name='téléphone')),
                ('telephone_mobile', models.CharField(blank=True, default='', max_length=20, verbose_name='téléphone mobile')),
                ('adresse', models.TextField(blank=True, default='(Inconnue)')),
                ('candidat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responsables', to='inscrire.Candidat')),
                ('profession', models.ForeignKey(default=99, on_delete=django.db.models.deletion.SET_DEFAULT, to='inscrire.Profession')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MefOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modalite', models.PositiveSmallIntegerField(choices=[(1, 'obligatoire'), (2, 'facultative')], verbose_name='modalité')),
                ('rang', models.PositiveSmallIntegerField()),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Formation')),
                ('matiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.MefMatiere')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueVoeu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('etat', models.PositiveSmallIntegerField(choices=[(0, "en liste d'attente"), (1, 'accepté avec autres vœux en attente'), (2, 'accepté définitivement'), (3, 'refusé par le candidat')])),
                ('date', models.DateTimeField()),
                ('voeu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Voeu')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CandidatActionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, default='')),
                ('date', models.DateTimeField()),
                ('candidat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Candidat')),
            ],
        ),
        migrations.AddField(
            model_name='candidat',
            name='commune_naissance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inscrire.Commune'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='nationalite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidats_nationalite', to='inscrire.Pays'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='pays_naissance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidats_naissance', to='inscrire.Pays'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ParcoursupUser',
            fields=[
                ('etablissement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='inscrire.Etablissement')),
                ('adresse_api', models.URLField(max_length=300)),
                ('remontee_username', models.CharField(max_length=50)),
                ('remontee_password', models.CharField(max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParcoursupMessageRecuLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('ip_source', models.GenericIPAddressField()),
                ('endpoint', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=200)),
                ('succes', models.BooleanField()),
                ('payload', models.BinaryField(blank=True, default=b'', null=True, verbose_name='données reçues')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inscrire.ParcoursupUser')),
            ],
        ),
        migrations.CreateModel(
            name='FicheScolariteAnterieure',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('classe_terminale', models.CharField(blank=True, default='', max_length=20, verbose_name='classe de terminale suivie')),
                ('specialite_terminale', models.CharField(blank=True, default='', max_length=100, verbose_name='spécialité en terminale')),
                ('autre_formation', models.CharField(blank=True, default='', max_length=200, verbose_name='autre formation')),
                ('etablissement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inscrire.Etablissement')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheScolarite',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.Formation')),
                ('options', models.ManyToManyField(to='inscrire.MefOption')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='FicheIdentite',
            fields=[
                ('fiche_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inscrire.Fiche')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=inscrire.models.fiches.FicheIdentite._photo_upload_to)),
                ('piece_identite', models.FileField(blank=True, null=True, upload_to=inscrire.models.fiches.FicheIdentite._piece_identite_upload_to)),
                ('commune_naissance_etranger', models.CharField(blank=True, default='', max_length=200)),
                ('commune_naissance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inscrire.Commune')),
                ('pays_naissance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inscrire.Pays')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('inscrire.fiche',),
        ),
        migrations.CreateModel(
            name='BulletinScolaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classe', models.PositiveSmallIntegerField(choices=[(1, 'bulletin de première'), (2, 'bulletin de terminale')])),
                ('bulletin', models.FileField(upload_to=inscrire.models.fiches.BulletinScolaire._bulletin_upload_to)),
                ('fiche_scolarite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscrire.FicheScolariteAnterieure')),
            ],
        ),
    ]
