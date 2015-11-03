from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Keep the patterns here in alphabetic order.
    url(r'^admin/',   include(admin.site.urls)),
    url(r'', include('studies.urls')),
]
