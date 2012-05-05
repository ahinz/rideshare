from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
import datetime

from django.contrib.auth import authenticate, login

def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('auth.html',
                              {'state':state, 
                               'username': username,
                               'next': '/main'},
                              context_instance=RequestContext(request))

def home(request):
    return render_to_response("index.html",
                              {},
                              context_instance=RequestContext(request))
