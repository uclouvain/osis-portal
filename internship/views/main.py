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
import internship.models as mdl_internship
from internship.forms import form_select_speciality


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_home(request):

    return layout.render(request, "internship_home.html")


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_selection(request):
    NUMBER_NON_MANDATORY_INTERNSHIPS = 6
    specialities = mdl_internship.internship_speciality.InternshipSpeciality.objects.all()
    internships_offers = mdl_internship.internship_offer.InternshipOffer.objects.all()

    speciality_form = form_select_speciality.SpecialityForm()

    return layout.render(request, "internship_selection.html",
                         {"number_non_mandatory_internships": range(1, NUMBER_NON_MANDATORY_INTERNSHIPS + 1),
                          "specialities": specialities,
                          "speciality_form": speciality_form,
                          "internships_offers": internships_offers})

