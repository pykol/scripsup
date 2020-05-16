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
./manage.py loaddata communes.json pays.json professions.json
./manage.py createsuperuser
```
