from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
from omgeo import Geocoder
from omgeo.places import PlaceQuery
from rideshare.models import Trip, Rider, RiderRole, RiderStatus
import datetime
import json

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
    """Given an address, returns candidates."""
    pq = PlaceQuery(address)
    global _geocoder
    if _geocoder is None:
        _geocoder = Geocoder()
    return _geocoder.geocode(pq)


def get_top_result_from_address(address):
    """
    Given address, returns top result and raises
    error if it can't geocode.
    """
    candidates = geocode(address)
    if len(candidates) < 1:
        raise Exception("Could not geocode %s." % address)
    return candidates[0]


@login_required
def create_trip(request):
    start_match = get_top_result_from_address(request.POST['from'])
    end_match = get_top_result_from_address(request.POST['to'])
    m,d,y = request.POST['date'].split("/")
    time = "%s-%s-%s %s" % (y,m,d,request.POST['time'])
    trip = Trip.objects.create(start=Point(start_match.x, start_match.y),
                               start_readable=start_match.match_addr,
                               end=Point(end_match.x, end_match.y),
                               end_readable=end_match.match_addr,
                               created_by=request.user, time=time)
    Rider.objects.create(trip=trip, user=request.user,
                         role=RiderRole.DRIVER, status=RiderStatus.ACCEPTED)
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

        return redirect('/mobile/my_trips')
    else:
        raise Exception("Invalid user (%s=%s)" % (trip.created_by.pk,request.user.pk))

def do_search(startstr,endstr,time):
    start_match = get_top_result_from_address(startstr)
    end_match = get_top_result_from_address(endstr)

    start = Point(float(start_match.x), float(start_match.y))
    end = Point(float(end_match.x), float(end_match.y))

    print "Doing search from %s to %s" % (start,end)

    rad = 1000*60 # 100 km

    trips = Trip.objects.filter(start__distance_lte=(start,D(m=rad)),
                                end__distance_lte=(end,D(m=rad)))

    return trips
    
    
@login_required
def mobile_perform_search(request):
    m,d,y = request.REQUEST['date'].split("/")

    trips = do_search(
        request.REQUEST['start'],
        request.REQUEST['end'],
        "%s-%s-%s %s" % (y,m,d,request.REQUEST['time']))

    return render_to_response("search.mobile.html",
                              { "trips" : trips },
                              context_instance=RequestContext(request))                              


@login_required
def mobile_profile(request):
    rider_id = request.REQUEST.get("rid",None)
    try:
        rider = Rider.objects.get(pk=rider_id)
    except:
        rider = None
    template_data = dict(rider=rider)
    try:
        raw = rider.user.userprofile.raw_data
        raw = json.loads(raw)
        template_data = dict(template_data, dict(raw=raw))
        if 'image' in raw:
            template_data = dict(template_data, dict(photo=raw['image']))
    except:
        pass
    return render_to_response("profile.mobile.html",
                              template_data,
                              context_instance=RequestContext(request))                              
    
    
@login_required
def rewards(request):
    recent_trip =  Trip.objects.filter(time__lte=datetime.datetime.now())[0]

    pcount = recent_trip.passenger_count()
    if pcount > 1:
        psg = "passengers"
    else:
        psg = "passenger"
        

    return render_to_response("rewards.mobile.html",
                              { "recent_trip" : recent_trip,
                                "recent_trip_points" : recent_trip.points_for_user(request.user),
                                "recent_trip_psg" : pcount,
                                "recent_trip_s" : psg },
                              context_instance=RequestContext(request))                              
    


@login_required
def mobile_do_create(request):
    start_match = get_top_result_from_address(request.POST['start'])
    end_match = get_top_result_from_address(request.POST['end'])
    time = request.POST['datetime']

    trip = Trip.objects.create(start=Point(float(start_match.x), float(start_match.y)),
                               start_readable=start_match.match_addr,
                               end=Point(float(end_match.x), float(end_match.y)),
                               end_readable=end_match.match_addr,
                               created_by=request.user, time=time)
    Rider.objects.create(trip=trip, user=request.user,
                         role=RiderRole.DRIVER, status=RiderStatus.ACCEPTED)

    return redirect("/mobile/my_trips")


@login_required
def mobile_create(request):

    return render_to_response("create.mobile.html",
                              {},
                              context_instance=RequestContext(request))
@login_required
def mobile_create_similar(request):
    m,d,y = request.REQUEST['date'].split("/")

    datetime = "%s-%s-%s %s" % (y,m,d,request.REQUEST['time'])

    trips = do_search(
        request.REQUEST['start'],
        request.REQUEST['end'],
        datetime)[0:4]

    return render_to_response("search_similar.mobile.html",
                             { "trips" : trips,
                               "start" : request.REQUEST['start'],
                               "end"   : request.REQUEST['end'],
                               "datetime" : datetime },
                              context_instance=RequestContext(request))                              



@login_required
def mobile_find(request):

    return render_to_response("find.mobile.html",
                              {},
                              context_instance=RequestContext(request))

@login_required
def mobile_home(request):

    return render_to_response("home.mobile.html", 
                              {},
                              context_instance=RequestContext(request))

@login_required
def mobile_my_trips(request):
    # mytrips = Trip.objects.filter(created_by=request.user)
    upcoming_trips = Trip.objects.filter(rider__user=request.user,time__gte=datetime.datetime.now()).order_by("time") #.exclude(created_by=request.user)
    prev_trips = Trip.objects.filter(rider__user=request.user,time__lt=datetime.datetime.now()).order_by("-time") #.exclude(created_by=request.user)

    return render_to_response("mobile.html",
                              { "upcoming_trips" : upcoming_trips,
                                "prev_trips" : prev_trips },
                              context_instance=RequestContext(request))                              


@login_required
def main(request):
    mytrips = Trip.objects.filter(created_by=request.user)

    trips_going_on = Trip.objects.filter(rider__user=request.user)\
                                 .exclude(created_by=request.user)

    return render_to_response("main.html",
                              { "mytrips" : mytrips,
                                "trips_going_on" : trips_going_on },
                              context_instance=RequestContext(request))                              

@login_required
def apply_to_trip(request, trip_id):
    trip = Trip.objects.get(pk=trip_id)
    Rider.objects.create(trip=trip, user=request.user,
                         role=RiderRole.PASSENGER, status=RiderStatus.PENDING)

    return redirect('/mobile/my_trips')

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
    
    
