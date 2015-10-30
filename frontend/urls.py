from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'studies.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^studies/', include('studies.urls')),
    url(r'^admin/',   include(admin.site.urls)),
]
