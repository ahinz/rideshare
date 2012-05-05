from django.contrib.gis.db import models
from django.contrib.auth.models import User

class Trip(models.Model):
    start = models.PointField()
    end = models.PointField()

    time = models.DateTimeField()

    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now=True)

    objects = models.GeoManager()

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
    
