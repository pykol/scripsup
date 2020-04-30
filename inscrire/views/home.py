from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

USER = get_user_model()

def deconnexion(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
	try:
		candidat = request.user.candidat
	except USER.candidat.RelatedObjectDoesNotExist:
		return render(request, "base.html")
	return redirect("/candidat")
