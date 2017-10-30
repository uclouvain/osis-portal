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
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect

from attribution.business import attribution_list
from attribution.business import tutor_application_list
from attribution.views.decorators.authorization import user_is_tutor_or_super_user
from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.models.enums import learning_component_year_type
from base.views import layout


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def administration_applications(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return redirect('visualize_tutor_applications', global_id=global_id)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/applications_administration.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
@user_is_tutor_or_super_user
def visualize_tutor_applications(request, global_id):
    return home(request, global_id)


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def home(request, global_id=None):
    tutor = mdl_base.tutor.find_by_user(request.user) if not global_id else \
                 mdl_base.tutor.find_by_person_global_id(global_id)

    # Current Attributions
    attributions = attribution_list.get_attribution_list(global_id=tutor.person.global_id)
    attributions = attribution_list.append_team_and_volume_declared_vacant(attributions)
    attributions = attribution_list.append_start_and_end_academic_year(attributions)
    volume_total_attributions = attribution_list.get_volumes_total(attributions)
    # Applications For Next Year
    application_year = tutor_application_list.get_application_year()
    applications = tutor_application_list.get_application_list(global_id=tutor.person.global_id)

    return layout.render(request, "attribution_applications.html", {
        'a_tutor': tutor,
        'attributions': attributions,
        'application_year': application_year,
        'applications': None, #applications,
        'tot_lecturing': volume_total_attributions.get(learning_component_year_type.LECTURING),
        'tot_practical': volume_total_attributions.get(learning_component_year_type.PRACTICAL_EXERCISES)
    })

