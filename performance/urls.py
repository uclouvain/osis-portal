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
from django.conf.urls import url
from performance.views import main

urlpatterns = [
    url(r'^$', main.home, name='performance_home'),

    url(r'^administration/$', main.performance_administration, name='performance_administration'),
    url(r'^administration/select_student/$', main.select_student, name='performance_select_student'),

    url(r'^result/(?P<offer_year_id>[0-9]+)/$',
        main.result_by_year_and_program, name='performance_result'),
    url(r'^student_programs/(?P<registration_id>[0-9]+)/$', main.student_programs, name='performance_student_programs'),
    url(r'^student_result/(?P<registration_id>[0-9]+)/(?P<offer_year_id>[0-9]+)/$',
        main.student_result, name='performance_student_result'),
]

