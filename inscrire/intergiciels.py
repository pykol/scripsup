import os
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

def en_travaux(get_response):
    def middleware(request):
        try:
            with open(os.path.join(settings.BASE_DIR, 'scripsup/en_travaux.txt'), encoding = 'utf-8', newline = '') as f:
                en_travaux = f.read().strip()
        except FileNotFoundError:
            en_travaux = "Site en cours de configuration"
        if en_travaux:
            try:
                with open(os.path.join(settings.BASE_DIR, 'scripsup/maintenance_mode_ip.txt'), encoding = 'utf-8', newline = '') as f:
                    IPs = [line.strip() for line in f.readlines()]
            except FileNotFoundError:
                return HttpResponse(en_travaux)
            IP = request.META.get('REMOTE_ADDR')
            if not IP in IPs :
                return HttpResponse(en_travaux)
        response = get_response(request)
        return response
    return middleware
