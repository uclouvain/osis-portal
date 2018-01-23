# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from base.views import layout
from internship.forms.form_search_hospital import SearchHospitalForm
from internship import models as mdl_internship
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_hospitals_list(request, cohort_id):
    cities = mdl_internship.organization.get_all_cities()
    name = ""
    city = ""
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)

    if request.method == 'POST':
        form = SearchHospitalForm(cities, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city = form.cleaned_data['city']
    else:
        form = SearchHospitalForm(cities)

    hospitals = mdl_internship.organization.search(cohort, name, city)

    return layout.render(request, "hospitals.html", {'search_form': form,
                                                     'hospitals': hospitals,
                                                     'cohort': cohort,
                                                     'name': name,
                                                     'city': city})
