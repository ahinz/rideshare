from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from omgeo import Geocoder
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

_geocoder = None # Cache geocoder
def geocode(address):
    """Given an address, returns lat/lon tuple or None if 
    the address cannot be geocoded."""
    if _geocoder is None:
        _geocoder = Geocoder()
    candidates = _geocoder.geocode(address)
    if len(candidates) < 1:
        return None
    top_result = candidates[0]
    return (top_result.x, top_result.y)


@login_required
def create_trip(request):
    from_lng,from_lat = geocode(request.POST['from'])
    top_lng,top_lat = geocode(request.POST['to'])

    time = "%s %s" % (request.POST['date'], request.POST['time'])

    trip = Trip.objects.create(start=Point(from_lng, from_lat),end=Point(top_lng,top_lat),created_by=request.user,time=time)

    Rider.objects.create(trip=trip, user=request.user, role=RiderRole.DRIVER, status=RiderStatus.ACCEPTED)
    
    return redirect("/main")

@login_required
def update_pending(request, trip_id, verb, user_id):
    trip = Trip.objects.get(pk=trip_id)

    if trip.created_by.pk is request.user.pk:
        rideruser = User.objects.get(pk=user_id)
        rider = Rider.objects.get(trip=trip,user=rideruser)

        if verb == "approve":
            rider.status = RiderStatus.ACCEPTED
        else:
            rider.status = RiderStatus.REJECTED

        rider.save()

        return redirect('/main')
    else:
        raise Exception("Invalid user (%s=%s)" % (trip.created_by.pk,request.user.pk))
    

@login_required
def main(request):
    mytrips = Trip.objects.filter(created_by=request.user)

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
    
    
