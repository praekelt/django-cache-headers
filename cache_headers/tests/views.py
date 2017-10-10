from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


def mylogin(request):
    # 1.11 request as first arg
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("yay")
    raise RuntimeError("Bad credentials")


def mylogout(request):
    logout(request)
    return HttpResponse("yay")
