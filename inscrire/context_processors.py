import os
from django.conf import settings
BASE_DIR = settings.BASE_DIR

def avertissement_maintenance(request):
    try:
        with open(os.path.join(BASE_DIR, 'scripsup/avertissement_maintenance.txt'), encoding = 'utf-8', newline = '') as f:
            avertissement = f.read().strip()
    except FileNotFoundError:
        avertissement = ""
    return {'avertissement_maintenance': avertissement}
