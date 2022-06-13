##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from attestation.views import download as attestation_main
from attestation.views.administration import Administration, AdministrationSelectStudent, \
    AdministrationViewStudentAttestation
from attestation.views.home import Home

urlpatterns = [

    url(r'^$', Home.as_view(), name='attestation_home'),
    url(r'^administration/attestations/$', Administration.as_view(),
        name='attestation_administration'),
    url(r'^administration/select_student/$', AdministrationSelectStudent.as_view(),
        name='attestation_admin_select_student'),
    url(r'^administration/attestations/(?P<registration_id>[0-9]+)/$',
        AdministrationViewStudentAttestation.as_view(), name='attestation_admin_view'),
    url(r'^administration/attestations/(?P<global_id>[0-9]+)/(?P<academic_year>[0-9]+)/(?P<attestation_type>.+)/$',
        attestation_main.download_student_attestation, name='attestation_admin_download'),
    url(r'^attestations/(?P<academic_year>[0-9]+)/(?P<attestation_type>.+)/$', attestation_main.download_attestation,
        name='download_attestation'
        ),

]
