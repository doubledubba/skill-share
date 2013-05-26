from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('main.views',
    url(r'^$', 'home'),
    url(r'^profile/(?P<uid>\d+)/$', 'profile_view'),
    url(r'^search$', 'search_view'),
    url(r'^edit$', 'edit_view'),
    url(r'^service/(?P<sid>\d+)/$', 'service_view'),

    url(r'^admin/', include(admin.site.urls)),
)
