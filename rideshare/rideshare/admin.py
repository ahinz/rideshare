from django.contrib.gis import admin
from django.contrib.contenttypes import generic

from rideshare.models import Trip, Rider

class TripAdmin(admin.GeoModelAdmin):
    pass

class RiderAdmin(admin.ModelAdmin):
    pass

admin.site.register(Trip, TripAdmin)
admin.site.register(Rider, RiderAdmin)
