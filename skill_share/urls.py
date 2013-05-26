from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from skill_share import settings

urlpatterns = patterns('main.views',
    url(r'^$', 'home'),
    url(r'^profile/(?P<uid>\d+)/$', 'profile_view'),
    url(r'^search$', 'search_view'),
    url(r'^edit$', 'edit_view'),
    url(r'^service/(?P<sid>\d+)/$', 'service_view'),
    url(r'^login/$', 'login_view'),
    url(r'^logout/$', 'logout_view'),
    url(r'^register/$', 'register_view'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('', (r'^static/(?P.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),)
