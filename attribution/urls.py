##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import include, path, re_path

from attribution.views import list
from attribution.views.home import HomeAttribution
from attribution.views.online_application.create import CreateApplicationView
from attribution.views.online_application.delete import DeleteApplicationView
from attribution.views.online_application.outside_period import OutsidePeriod
from attribution.views.online_application.overview import ApplicationOverviewView, ApplicationOverviewAdminView
from attribution.views.online_application.renew_multiple_application_about_to_expire import \
    RenewMultipleAttributionsAboutToExpireView
from attribution.views.online_application.search_vacant_courses import SearchVacantCoursesView
from attribution.views.online_application.select_tutor import SelectTutor
from attribution.views.online_application.send_summary import SendApplicationsSummaryView
from attribution.views.online_application.update import UpdateApplicationView
from attribution.views.select_tutor_for_attribution import SelectTutorForAttribution
from attribution.views.students_list import StudentsListView, AdminStudentsListView, StudentsListXlsView
from attribution.views.tutor_charge import TutorChargeView, AdminTutorChargeView

js_info_dict = {
    'packages': ('attribution',)
}

urlpatterns = [

    path('', HomeAttribution.as_view(), name='attribution_home'),
    path('charge/', TutorChargeView.as_view(), name='tutor_charge'),
    re_path(r'^students/(?P<learning_unit_acronym>[0-9A-Za-z-]+)/(?P<learning_unit_year>[0-9]+)/', include([
        path('', StudentsListView.as_view(), name='student_enrollments_by_learning_unit'),
        re_path(r'^(?P<class_code>[0-9A-Za-z-]{1})$', StudentsListView.as_view(),
                name='student_enrollments_by_learning_class'),
        path('xls', StudentsListXlsView.as_view(), name='produce_xls_students'),
        re_path(r'^(?P<class_code>[0-9A-Za-z-]{1})/xls$', StudentsListXlsView.as_view(),
                name='produce_xls_class_students')
    ])),
    path('applications/', include([
        path('', ApplicationOverviewView.as_view(), name='applications_overview'),
        path('outside_period/', OutsidePeriod.as_view(), name='outside_applications_period'),
        path('search_vacant_courses', SearchVacantCoursesView.as_view(), name='search_vacant_courses'),
        path('send_summary', SendApplicationsSummaryView.as_view(), name='email_tutor_application_confirmation'),
        re_path(
            r'^(?P<vacant_course_code>[0-9A-Za-z-]+)/create$',
            CreateApplicationView.as_view(),
            name='create_application'
        ),
        path(
            'renew/',
            RenewMultipleAttributionsAboutToExpireView.as_view(),
            name='renew_applications',
        ),
        re_path(r'^(?P<application_uuid>[0-9A-Za-z-]+)/', include([
            path('delete', DeleteApplicationView.as_view(), name='delete_application'),
            path('update', UpdateApplicationView.as_view(), name='update_application'),
        ]))
    ])),

    path('administration/', include([
        re_path(r'^charge/(?P<global_id>[0-9a-z-]+)/$', AdminTutorChargeView.as_view(), name='tutor_charge_admin'),
        re_path(r'^students/(?P<learning_unit_acronym>[0-9A-Za-z-]+)/(?P<learning_unit_year>[0-9]+)/$',
                AdminStudentsListView.as_view(), name='attribution_students_admin'),
        path('select_tutor/', SelectTutorForAttribution.as_view(), name='attribution_admin_select_tutor'),
        path('students_list/', list.lists_of_students_exams_enrollments, name='lists_of_students_exams_enrollments'),
        re_path(r'^students_list/([0-9a-z-]+)/xls', list.list_build_by_person,
                name='lists_of_students_exams_enrollments_create'),

        path('applications/', include([
            path('', SelectTutor.as_view(), name='attribution_applications'),
            path(
                '<int:global_id>/',
                ApplicationOverviewAdminView.as_view(),
                name="visualize_tutor_applications"
            )
        ])),
    ])),
    path('list/students', list.students_list, name='students_list'),
    re_path(r'^list/students/xls', list.list_build, name='students_list_create'),
]
