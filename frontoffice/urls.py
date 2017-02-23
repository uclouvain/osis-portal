##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from base.views import common


js_info_dict = {
    'domain': 'djangojs',
    'packages': ('admission',),
}


urlpatterns = (
    url(r'^'+settings.ADMIN_URL, admin.site.urls),
    url(r'', include('base.urls')),
    url(r'^login/$', common.login, name='login'),
    url(r'^logout/$', common.log_out, name='logout'),
    url(r'^logged_out/$', common.logged_out, name='logged_out'),
    url(r'^403/$', common.access_denied, name="error_403"),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='javascript-catalog'),
)


if 'admission' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^admission/', include('admission.urls')), )
if 'dashboard' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^dashboard/', include('dashboard.urls')), )
if 'catalog' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^catalog/', include('catalog.urls')), )
if 'performance' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^performance/', include('performance.urls')), )
if 'dissertation' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^dissertation/', include('dissertation.urls')),)
if 'attribution' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^attribution/', include('attribution.urls')), )
if 'internship' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^internship/', include('internship.urls')), )
if 'exam_enrollment' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^exam_enrollment/', include('exam_enrollment.urls')), )
if 'attestation' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (url(r'^attestation/', include('attestation.urls')), )

handler404 = 'base.views.common.page_not_found'
handler403 = 'base.views.common.access_denied'
handler500 = 'base.views.common.server_error'

admin.site.site_header = 'Osis-studies'
admin.site.site_title = 'Osis-studies'
admin.site.index_title = 'Louvain'
