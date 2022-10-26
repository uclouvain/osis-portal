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
from django.conf.urls import url, include

from internship.views import main, hospital, resume, selection, score_encoding, place_evaluation
from internship.views.master_delegates import manage_delegates, new_delegate, delete_delegate

urlpatterns = [
    url(r'^$', main.view_internship_role_selection, name="internship"),

    url(r'^student/', include([
        url(r'^$', main.view_cohort_selection, name="internship_cohort_selection"),
        url(r'^cohort/(?P<cohort_id>[0-9]+)/', include([
            url(r'^$', main.view_internship_student_home, name='internship_student_home'),
            url(r'^selection/', include([
                url(r'^$', selection.view_internship_selection, name='select_internship'),
                url(r'^ajax/selective_internship/$', selection.get_selective_internship_preferences,
                    name='selective_internship_preferences'),
            ])),
            url(r'^hospitals/$', hospital.view_hospitals_list, name='hospitals_list'),
            url(r'^resume/$', resume.view_student_resume, name='student_resume'),
            url(r'^place_evaluation/$', place_evaluation.view_place_evaluation, name='place_evaluation')
        ])),
    ])),

    url(r'^master/', include([
        url(r'^$', main.view_internship_master_home, name='internship_master_home'),
        url(r'manage_delegates/', include([
            url(r'^$', manage_delegates, name='internship_manage_delegates'),
            url(r'new/(?P<specialty_uuid>[0-9a-f-]+)/(?P<organization_uuid>[0-9a-f-]+)/$', new_delegate,
                name='internship_new_delegate'),
            url(r'delete/(?P<allocation_uuid>[0-9a-f-]+)/$', delete_delegate,
                name='internship_delete_delegate'),
        ])),
        url(r'^score_encoding/', include([
            url(r'^$', score_encoding.view_score_encoding, name="internship_score_encoding"),
            url(r'(?P<specialty_uuid>[0-9a-f-]+)/(?P<organization_uuid>[0-9a-f-]+)/', include([
                url(r'^$', score_encoding.view_score_encoding_sheet, name='internship_score_encoding_sheet'),
                url(r'^(?P<affectation_uuid>[0-9a-f-]+)/$',
                    score_encoding.view_score_encoding_form,
                    name="internship_score_encoding_form"),
            ])),
        ])),
    ])),

    url(r'^ajax/', include([
       url(r'^(?P<affectation_uuid>[0-9a-f-]+)/validate$',
        score_encoding.score_encoding_validate, name="internship_score_encoding_validate"),
    ]))
]
