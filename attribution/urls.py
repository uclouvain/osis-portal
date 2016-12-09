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
from django.conf.urls import url
from attribution.views import teaching_load, online_application

urlpatterns = [
    url(r'^$', teaching_load.home, name='home'),
    url(r'^attribution/$', teaching_load.by_year, name='attribution'),
    url(r'^load/([0-9]+)/$', teaching_load.by_year, name='attributions_by_year'),
    url(r'^students/([0-9]+)/$', teaching_load.show_students, name='students'),
    url(r'^attribution/attribution_applications/$', online_application.home, name='attribution_applications'),
    url(r'^attribution/delete_application/([0-9]+)/$', online_application.delete, name='delete_tutor_application'),
    url(r'^attribution/new_application/$', online_application.attribution_application_form, name='tutor_application_create'),
    url(r'^attribution/search/$', online_application.search, name='vacant_learning_unit_search'),
    url(r'^attribution/renew/$', online_application.renew, name='renew'),



]
