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
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.forms.form_search_hospital import SearchHospitalForm
from internship.services.internship import InternshipAPIService


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_hospitals_list(request, cohort_id):
    organizations = InternshipAPIService.get_organizations(person=request.user.person, cohort_name=cohort_id).results
    cities = sorted({organization.city for organization in organizations if organization.city})

    name = ""
    city = ""
    cohort = InternshipAPIService.get_cohort_detail(cohort_name=cohort_id, person=request.user.person)

    if request.method == 'POST':
        form = SearchHospitalForm(cities, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city = form.cleaned_data['city']
    else:
        form = SearchHospitalForm(cities)

    hospitals = [organization for organization in organizations]

    if city:
        hospitals = [h for h in hospitals if h.city and city in h.city]

    if name:
        hospitals = [h for h in hospitals if h.name and name in h.name]

    return layout.render(request, "hospitals.html", {
        'search_form': form,
        'hospitals': hospitals,
        'cohort': cohort,
        'name': name,
        'city': city
    })
