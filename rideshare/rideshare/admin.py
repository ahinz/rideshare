from django.contrib.gis import admin
from django.contrib.contenttypes import generic

from rideshare.models import Trip, Rider, UserProfile

class TripAdmin(admin.GeoModelAdmin):
    pass

class RiderAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Trip, TripAdmin)
admin.site.register(Rider, RiderAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
