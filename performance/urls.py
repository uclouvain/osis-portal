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

from performance.views import main

urlpatterns = [
    url(r'^$', main.view_performance_home, name='performance_home'),
    url(r'^result/(?P<pk>[0-9]+)/$',
        main.display_result_for_specific_student_performance, name='performance_student_result'),
    url(
        r'^result/(?P<acronym>[0-9A-Za-z_ ]+)/(?P<academic_year>[0-9]{4})/$',
        main.display_results_by_acronym_and_year,
        name='performance_student_by_acronym_and_year'
    ),
    url(r'^administration/select_student/$', main.select_student, name='performance_administration'),
    url(r'^administration/student_programs/(?P<registration_id>[0-9]+)/$', main.visualize_student_programs,
        name='performance_student_programs_admin'),
    url(r'^administration/student_result/(?P<pk>[0-9]+)/$',
        main.visualize_student_result, name='performance_student_result_admin'),
]
