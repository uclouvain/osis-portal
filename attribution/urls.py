##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from attribution.views import online_application_new
from attribution.views import tutor_charge, online_application, list
from django.views.i18n import javascript_catalog


js_info_dict = {
    'packages': ('attribution', )
}

urlpatterns = [

    url(r'^$', tutor_charge.home, name='attribution_home'),
    url(r'^charge/([0-9]+)/([0-9a-z-]+)/$', tutor_charge.by_year, name='attributions_by_year'),

    url(r'^students/(?P<a_learning_unit_year>[0-9]+)/(?P<a_tutor>[0-9]+)/$', tutor_charge.show_students,
        name='attribution_students'),

    url(r'^applications/', include([
        url(r'^$', online_application_new.overview, name='learning_unit_applications'),
        url(r'^outside_period/$', online_application.outside_period, name='outside_applications_period'),
        url(r'^search_vacant$', online_application_new.search_vacant_attribution, name='vacant_learning_unit_search'),
        url(r'^send_summary$', online_application_new.send_mail_applications_summary,
            name='email_tutor_application_confirmation'),
        url(r'^renew/$', online_application_new.renew_applications, name='renew_applications'),
        url(r'^(?P<learning_container_year_id>[0-9a-z-]+)/', include([
            url(r'^edit/$', online_application_new.create_or_update_application,
                name='create_or_update_tutor_application'),
            url(r'^delete/$', online_application_new.delete_application,
                name='delete_tutor_application'),
        ]))
    ])),

    url(r'^administration/', include([
        url(r'^charge/([0-9]+)/([0-9a-z-]+)/$', tutor_charge.by_year_admin, name='attributions_by_year_admin'),
        url(r'^students/(?P<a_learning_unit_year>[0-9]+)/(?P<a_tutor>[0-9]+)/$', tutor_charge.show_students_admin,
            name='attribution_students_admin'),
        url(r'^attributions/$', tutor_charge.attribution_administration, name='attribution_administration'),
        url(r'^select_tutor/$', tutor_charge.select_tutor_attributions,
            name='attribution_admin_select_tutor'),
        url(r'^visualize_tutor/([0-9a-z-]+)/$', tutor_charge.visualize_tutor_attributions,
            name='attribution_admin_visualize_tutor'),
        url(r'^students_list/$', list.students_list_admin, name='students_list_admin'),
        url(r'^students_list/([0-9a-z-]+)/xls', list.list_build_by_person, name='students_list_admin_create'),

        url(r'^applications/', include([
            url(r'^$', online_application_new.administration_applications,
                name='attribution_applications'),
            url(r'^(?P<global_id>[0-9a-z-]+)/$', online_application_new.visualize_tutor_applications,
                name="visualize_tutor_applications")
        ])),
    ])),
    url(r'^list/students$', list.students_list, name='students_list'),
    url(r'^list/students/xls', list.list_build, name='students_list_create'),

    url(r'^jsi18n/', javascript_catalog, js_info_dict),
]
