from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns('',
    url(r'^app/', include('app.urls')),
    url(r'^admin/', include(admin.site.urls)), 
    
)
