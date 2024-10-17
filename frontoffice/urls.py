##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2024 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import include, path, re_path

from base.views import common, administration

packages = ("attribution",)

urlpatterns = (
    re_path(r'^' + settings.ADMIN_URL, include([
        path('data/', administration.data, name='data'),
        path('data/maintenance', administration.data_maintenance, name='data_maintenance'),
    ])),
    path('', include('base.urls')),
    path('login/', common.login, name='login'),
    path('logout/', common.log_out, name='logout'),
    path('logged_out/', common.logged_out, name='logged_out'),
    re_path(r'^' + settings.ADMIN_URL, admin.site.urls),
    path('403/', common.access_denied, name="error_403"),
    path('hijack/', include('hijack.urls', namespace='hijack')),
)

if 'dashboard' in settings.INSTALLED_APPS:
    urlpatterns += (path('dashboard/', include('dashboard.urls')),)
if 'performance' in settings.INSTALLED_APPS:
    urlpatterns += (path('exammarks/', include('performance.urls')),)
if 'dissertation' in settings.INSTALLED_APPS:
    urlpatterns += (path('dissertation/', include('dissertation.urls')),)
if 'attribution' in settings.INSTALLED_APPS:
    urlpatterns += (path('attribution/', include('attribution.urls')),)
if 'internship' in settings.INSTALLED_APPS:
    urlpatterns += (path('internship/', include('internship.urls')),)
if 'exam_enrollment' in settings.INSTALLED_APPS:
    urlpatterns += (path('exam_enrollment/', include('exam_enrollment.urls')),)
if 'attestation' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (path('attestation/', include('attestation.urls')),)
if 'assessments' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (path('assessments/', include('assessments.urls')),)
if 'continuing_education' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (path('continuing_education/', include('continuing_education.urls')),)
if 'admission' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (path('admission/', include('admission.urls')),)
if 'osis_notification' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + (path('osis_notification/', include('osis_notification.urls')),)
if 'inscription_aux_cours' in settings.INSTALLED_APPS:
    urlpatterns += (path('inscription_aux_cours/', include('inscription_aux_cours.urls')),)
if 'learning_unit' in settings.INSTALLED_APPS:
    urlpatterns += (path('learning_unit/', include('learning_unit.urls')),)
if 'inscription_evaluation' in settings.INSTALLED_APPS:
    urlpatterns += (path('inscription_evaluation/', include('inscription_evaluation.urls')),)

handler404 = 'base.views.common.page_not_found'
handler403 = 'base.views.common.access_denied'
handler500 = 'base.views.common.server_error'

admin.site.site_header = 'Osis-studies'
admin.site.site_title = 'Osis-studies'
admin.site.index_title = 'Louvain'

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

if settings.DEBUG and 'silk' in settings.INSTALLED_APPS:
    urlpatterns += (path('silk/', include('silk.urls', namespace='silk')),)
