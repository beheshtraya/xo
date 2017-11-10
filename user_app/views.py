from django.contrib import auth
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User


def register(request):
    if not request.method == 'POST':
        return render(request, "register.html")

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']

    User.objects.create_user(username=username, email=email, password=password)

    user = auth.authenticate(username=username, email=email, password=password)
    auth.login(request, user)

    return HttpResponseRedirect('/')


def login(request):

    if request.method == 'GET':
        if 'next' in request.GET:
            next_url = request.GET['next']
        else:
            next_url = '/'
        return render(request, "login.html", {'next': next_url})

    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if not user:
        return HttpResponse('Invalid username or password')

    auth.login(request, user)

    return HttpResponseRedirect(request.POST['next'])


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
