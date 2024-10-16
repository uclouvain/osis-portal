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
from django.urls import path, re_path

import osis_common.api.url_v1
from base.views import my_osis
from base.views.autocomplete.country import CountryAutocomplete
from base.views.autocomplete.education_group_year import TrainingAutocomplete
from dashboard.views.home import Home

urlpatterns = [
    re_path(r'^my_osis/profile/lang/([A-Za-z-]+)/$', my_osis.profile_lang, name='profile_lang'),
    path('', Home.as_view(), name='home'),
    # TODO :: to remove shibboleth
    path(
        'continuing_education/country-autocomplete/',
        CountryAutocomplete.as_view(),
        name='country-autocomplete',
    ),
    path(
        'training-autocomplete/',
        TrainingAutocomplete.as_view(),
        name='training-autocomplete',
    ),
    *osis_common.api.url_v1.urlpatterns
]
