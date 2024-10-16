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
from django.urls import path

from dashboard.views.faculty_administration import FacultyAdministration
from dashboard.views.home import Home
from dashboard.views.student.my_personal_information import MyPersonalInformationAdmin, MyPersonalInformation

urlpatterns = [
    path('', Home.as_view(), name='dashboard_home'),
    path('faculty_administration/', FacultyAdministration.as_view(), name='faculty_administration'),
    path('faculty_administration/student/data/select_student/', MyPersonalInformationAdmin.as_view(),
        name='student_id_data_administration'),
    path('student/data/', MyPersonalInformation.as_view(), name='student_id_data_home'),
]
