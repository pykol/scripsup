scripsup - Inscription dématérialisée en CPGE interfacé avec Parcoursup
=======================================================================

Ce programme est distribué sous licence GNU Affero GPL version 3.

Pour démarrer :

```sh
virtualenv -p python3 scripsup_venv
source scripsup_venv/bin/activate

git clone https://github.com/pykol/scripsup.git
cd scripsup

pip intall -r requirements.txt
./manage.py migrate
./manage.py loaddata communes.json pays.json professions.json etablissements.json
./manage.py createsuperuser
```

Avec le compte super-utilisateur :

- aller dans l'interface d'administration,
- sélectionner l'établissement d'accueil dont il faut gérer les
  inscriptions,
- cocher la case « Inscriptions » et sauvegarder,
- créer les formations gérées par le serveur d'inscription,
- créer un compte utilisateur pour Parcoursup, avec le rôle Parcoursup.
  L'identifiant et le mot de passe peuvent être choisis au hasard. Il
  faut simplement ensuite les indiquer à Parcoursup (onglet
  Admissions/Interface synchrone) pour que la plateforme les utilise
  pour envoyer ses messages. Il faut créer un InscrireUser et un
  ParcoursupUser associé,
- le ParcoursupUser possède également deux champs à renseigner pour
  pouvoir communiquer depuis le serveur d'inscription vers Parcoursup.
  Les identifiants à renseigner sont fixés par Parcoursup et communiqués
  dans l'interface de gestion.

Il y a donc deux couples identifiant/mot de passe pour les
communications avec Parcoursup : un couple choisi par Parcoursup pour
les messages que nous lui envoyons, et un couple choisi par nous pour
les messages que Parcoursup nous envoie.

Il est possible de simuler l'envoi par Parcoursup d'un candidat de
test :

```sh
curl -H 'Content-type: application/json' \
     -d @inscrire/tools/candidat_test.json \
     http://127.0.0.1:8000/parcoursup/admissionCandidat
```

Le code Parcoursup de la formation est le code 8842. Ce code doit
correspondre au code indiqué pour une des formations plus haut. Les
données JSON s'identifient avec l'identifiant 42 et le mot de passe
secretsecret.

L'envoi d'un candidat de test génère l'envoi d'un e-mail d'activation au
candidat à l'adresse contenue dans les données JSON.
