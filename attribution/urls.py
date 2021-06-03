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
from django.conf.urls import url, include

import attribution.views.students_list
from attribution.views import online_application
from attribution.views import tutor_charge, list
from attribution.views.home import HomeAttribution
from attribution.views.tutor_charge import TutorChargeView, AdminTutorChargeView

js_info_dict = {
    'packages': ('attribution',)
}

urlpatterns = [

    url(r'^$', HomeAttribution.as_view(), name='attribution_home'),
    url(r'^charge/$', TutorChargeView.as_view(), name='tutor_charge'),
    url(r'^students/(?P<learning_unit_year_id>[0-9]+)/(?P<a_tutor>[0-9]+)/$',
        attribution.views.students_list.show_students,
        name='attribution_students'),
    url(r'^students/list/xls/(?P<learning_unit_year_id>[0-9]+)',
        attribution.views.students_list.students_list_build_by_learning_unit,
        name='produce_xls_students'),

    url(r'^applications/', include([
        url(r'^$', online_application.ApplicationOverviewView.as_view(), name='applications_overview'),
        url(r'^outside_period/$', online_application.outside_period, name='outside_applications_period'),
        url(
            r'^search_vacant_courses$',
            online_application.SearchVacantCoursesView.as_view(),
            name='search_vacant_courses'
        ),
        url(r'^send_summary$', online_application.send_mail_applications_summary,
            name='email_tutor_application_confirmation'),
        url(
            r'^(?P<vacant_course_code>[0-9A-Za-z-]+)/create$',
            online_application.CreateApplicationView.as_view(),
            name='create_application'
        ),
        url(
            r'^renew/$',
            online_application.RenewMultipleAttributionsAboutToExpireView.as_view(),
            name='renew_applications',
        ),
        url(r'^(?P<application_uuid>[0-9a-z-]+)/', include([
            url(r'^delete$', online_application.DeleteApplicationView.as_view(), name='delete_application'),
            url(r'^update$', online_application.UpdateApplicationView.as_view(), name='update_application'),
        ]))
    ])),

    url(r'^administration/', include([
        url(r'^charge/(?P<global_id>[0-9a-z-]+)/$', AdminTutorChargeView.as_view(), name='tutor_charge_admin'),
        url(r'^students/(?P<learning_unit_year_id>[0-9]+)/(?P<a_tutor>[0-9]+)/$',
            attribution.views.students_list.show_students_admin,
            name='attribution_students_admin'),
        url(r'^attributions/$', tutor_charge.attribution_administration, name='attribution_administration'),
        url(r'^select_tutor/$', tutor_charge.select_tutor_attributions,
            name='attribution_admin_select_tutor'),
        url(r'^students_list/$', list.lists_of_students_exams_enrollments, name='lists_of_students_exams_enrollments'),
        url(r'^students_list/([0-9a-z-]+)/xls', list.list_build_by_person,
            name='lists_of_students_exams_enrollments_create'),

        url(r'^applications/', include([
            url(r'^$', online_application.administration_applications,
                name='attribution_applications'),
            url(
                r'^(?P<global_id>[0-9]+)/$',
                online_application.ApplicationOverviewAdminView.as_view(),
                name="visualize_tutor_applications"
            )
        ])),
    ])),
    url(r'^list/students$', list.students_list, name='students_list'),
    url(r'^list/students/xls', list.list_build, name='students_list_create'),
]
