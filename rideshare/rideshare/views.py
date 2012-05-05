from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.gis.geos import Point

from rideshare.models import Trip, Rider, RiderRole, RiderStatus

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

@login_required
def main(request):
    mytrips = Trip.objects.filter(rider__user=request.user)

    trips_going_on = Trip.objects.filter(rider__user=request.user).exclude(created_by=request.user)

    return render_to_response("main.html",
                              { "mytrips" : mytrips,
                                "trips_going_on" : trips_going_on },
                              context_instance=RequestContext(request))                              

@login_required
def apply_to_trip(request, trip_id):
    trip = Trip.objects.get(pk=trip_id)
    Rider.objects.create(trip=trip, user=request.user, role=RiderRole.PASSENGER, status=RiderStatus.PENDING)

    return redirect('/main')

@login_required
def search(request):
    lat = request.REQUEST['lat']
    lng = request.REQUEST['lng']
    rad = request.REQUEST['radius']

    pnt = Point(float(lng), float(lat))

    trips = Trip.objects.filter(start__distance_lte=(pnt,float(rad)))

    return render_to_response("search.html",
                              { "trips" : trips },
                              context_instance=RequestContext(request))                              
    
    
