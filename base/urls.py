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
from django.conf import settings
from django.conf.urls import url

from base.views import administration, my_osis
from base.views.autocomplete.country import CountryAutocomplete
from base.views.autocomplete.education_group_year import TrainingAutocomplete
from dashboard.views import main

urlpatterns = [
    url(r'^'+settings.ADMIN_URL+'data/$', administration.data, name='data'),
    url(r'^'+settings.ADMIN_URL+'data/maintenance$', administration.data_maintenance, name='data_maintenance'),
    url(r'^my_osis/profile/lang/([A-Za-z-]+)/$', my_osis.profile_lang, name='profile_lang'),
    url(r'^$', main.home, name='home'),
    url(
        r'^country-autocomplete/$',
        CountryAutocomplete.as_view(),
        name='country-autocomplete',
    ),
    url(
        r'^training-autocomplete/$',
        TrainingAutocomplete.as_view(),
        name='training-autocomplete',
    ),
]
