from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    
    url(r'^$', 'rideshare.views.home'),
    url(r'^login/', 'rideshare.views.login_user'),
    url(r'^main/', 'rideshare.views.main'),
    url(r'^mobile/rewards', 'rideshare.views.rewards'),
    url(r'^mobile/do_create', 'rideshare.views.mobile_do_create'),
    url(r'^mobile/create_trip', 'rideshare.views.mobile_create'),
    url(r'^mobile/similar_trips', 'rideshare.views.mobile_create_similar'),
    url(r'^mobile/find_trips/search', 'rideshare.views.mobile_perform_search'),
    url(r'^mobile/find_trips', 'rideshare.views.mobile_find'),
    url(r'^mobile/my_trips', 'rideshare.views.mobile_my_trips'),
    url(r'^mobile/', 'rideshare.views.mobile_home'),
    url(r'^trip/search', 'rideshare.views.search'),
    url(r'^trip$', 'rideshare.views.create_trip'),
    url(r'^trip/(?P<trip_id>\d+)/apply', 'rideshare.views.apply_to_trip'),
    url(r'^trip/(?P<trip_id>\d+)/(?P<verb>[a-z]+)/(?P<user_id>\d+)', 'rideshare.views.update_pending'),


    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('registration.urls')),

    # Examples:
    # url(r'^$', 'rideshare.views.home', name='home'),
    # url(r'^rideshare/', include('rideshare.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += staticfiles_urlpatterns()
