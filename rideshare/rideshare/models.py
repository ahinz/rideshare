from django.db.models import signals
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django_facebook.models import FacebookProfileModel

def create_userprofile(sender, **kwargs):
    created = kwargs['created'] # object created or just saved?

    if created:
        UserProfile.objects.create(user=kwargs['instance'])

signals.post_save.connect(create_userprofile, sender=User)

class UserProfile(FacebookProfileModel):
    user = models.OneToOneField(User)

    def post_facebook_registration(self, request):
        from django_facebook.utils import next_redirect
        default_url = "/main"
        response = next_redirect(request, default=default_url,
                                 next_key='register_next')
        response.set_cookie('fresh_registration', self.user_id)

        return response

class Trip(models.Model):
    start = models.PointField()
    start_readable = models.TextField(default='', blank=True)
    end = models.PointField()
    end_readable = models.TextField(default='', blank=True)
    time = models.DateTimeField()
    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        start_readable = self.start_readable
        end_readable = self.end_readable
        if len(start_readable) > 35:
            start_readable = '%s...' % start_readable[:32]
        if len(end_readable) > 35:
            end_readable = '%s...' % end_readable[:32]
        return '%s to %s' % (start_readable,
                             end_readable)

    def pending(self):
        return Rider.objects.filter(trip=self,status=RiderStatus.PENDING)

    def rejected(self):
        return Rider.objects.filter(trip=self,status=RiderStatus.REJECTED)

    def going(self):
        return Rider.objects.filter(trip=self,status=RiderStatus.ACCEPTED)

    def num_going(self):
        return len(self.going())

    def formatted_date(self):
        return self.time.strftime("%a %m/%d/%y")

    def distance(self):
        from math import radians, cos, sin, asin, sqrt
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [self.start.x, self.start.y, self.end.x, self.end.y])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        mi = km * 0.621371192

        return mi

    def distancef(self):
        return "%0f" % self.distance()

    def passenger_count(self):
        return len(Rider.objects.filter(trip=self)) - 1

    def points_for_user(self, user):
        # Check if driver
        #TODO: Don't use len() use count()...
        if len(Rider.objects.filter(user=user,trip=self,role=RiderRole.DRIVER)) > 0:
            return int(self.distance()) * self.passenger_count()
        else:
            return int(self.distance())


class RiderRole:
    PASSENGER = "PASSENGER"
    DRIVER = "DRIVER"

class RiderStatus:
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"
    PENDING = "Pending"

class Rider(models.Model):
    role_choice = ((RiderRole.PASSENGER,RiderRole.PASSENGER),(RiderRole.DRIVER,RiderRole.DRIVER))
    status_choice = ((RiderStatus.REJECTED,RiderStatus.REJECTED),
                     (RiderStatus.ACCEPTED,RiderStatus.ACCEPTED),
                     (RiderStatus.PENDING,RiderStatus.PENDING))

    trip = models.ForeignKey(Trip)
    user = models.ForeignKey(User)

    role = models.CharField(max_length=50, choices=role_choice)
    status = models.CharField(max_length=50, choices=status_choice)
    
