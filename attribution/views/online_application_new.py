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
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from attribution.business import attribution
from attribution.business import tutor_application
from attribution.forms.application import ApplicationForm, VacantAttributionFilterForm
from attribution.utils import permission
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
    return overview(request, global_id)


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def overview(request, global_id=None):
    tutor = mdl_base.tutor.find_by_user(request.user) if not global_id else \
                 mdl_base.tutor.find_by_person_global_id(global_id)

    # Current Attributions
    attributions = attribution.get_attribution_list(global_id=tutor.person.global_id)
    attributions = attribution.append_team_and_volume_declared_vacant(attributions)
    attributions = attribution.append_start_and_end_academic_year(attributions)
    volume_total_attributions = attribution.get_volumes_total(attributions)
    # Applications For Next Year
    application_year = tutor_application.get_application_year()
    applications = tutor_application.get_application_list(global_id=tutor.person.global_id)

    return layout.render(request, "attribution_applications.html", {
        'a_tutor': tutor,
        'attributions': attributions,
        'application_year': application_year,
        'applications': applications,
        'tot_lecturing': volume_total_attributions.get(learning_component_year_type.LECTURING),
        'tot_practical': volume_total_attributions.get(learning_component_year_type.PRACTICAL_EXERCISES)
    })


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def attribution_expired_overview(request):
    tutor = mdl_base.tutor.find_by_user(request.user)
    attributions_expired = attribution.get_attribution_list(global_id=tutor.person.global_id)
    search_form = VacantAttributionFilterForm()

    return layout.render(request, "attribution_application_form.html", {
        'a_tutor': tutor,
        'attributions': attributions_expired,
        'search_form': search_form
    })


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def search_vacant_attribution(request):
    form = VacantAttributionFilterForm(data=request.GET)
    if form.is_valid():
        tutor = mdl_base.tutor.find_by_user(request.user)
        application_academic_year = mdl_base.academic_year.current_academic_year() #tutor_application.get_application_year()
        attributions_vacant = tutor_application.get_attributions_vacant_for_application(
            global_id=tutor.person.global_id,
            acronym_filter=form.cleaned_data['learning_container_acronym'],
            academic_year=application_academic_year
        )

        return layout.render(request, "attribution_vacant.html", {
            'a_tutor': tutor,
            'attributions_vacant': attributions_vacant,
            'search_form': form
        })
    return redirect('tutor_application_create')


@login_required
#@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def create_application(request, learning_container_year_id):
    tutor = mdl_base.tutor.find_by_user(request.user)
    global_id = tutor.person.global_id
    learning_container_year = mdl_base.learning_container_year.find_by_id(learning_container_year_id)

    if request.method == 'POST':
        form = ApplicationForm(learning_container_year=learning_container_year,
                               global_id=global_id,
                               data=request.POST)
        if form.is_valid():
            application_to_add = form.cleaned_data
            tutor_application.create_application(global_id, application_to_add)
            return redirect('learning_unit_applications')
    else:
        form = ApplicationForm(learning_container_year=learning_container_year,
                               global_id=tutor.person.global_id)

    return layout.render(request, "application_form.html", {
        'a_tutor': tutor,
        'form': form,
        'learning_container_year': learning_container_year
    })


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def delete_application(request, application_id):
    tutor = mdl_base.tutor.find_by_user(request.user)
    tutor_application.delete(global_id=tutor.person.global_id, application_id=application_id)
    return redirect('learning_unit_applications')



