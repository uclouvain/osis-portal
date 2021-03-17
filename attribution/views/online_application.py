##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from attribution.business import attribution
from attribution.business import tutor_application
from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from attribution.forms.application import ApplicationForm, VacantAttributionFilterForm
from attribution.utils import permission
from attribution.utils import tutor_application_epc
from attribution.views.decorators.authorization import user_is_tutor_or_super_user
from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_year_subtypes
from base.models.enums import learning_component_year_type
from base.models.learning_unit_year import LearningUnitYear
from base.templatetags.academic_year_display import display_as_academic_year
from base.views import layout


logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def outside_period(request):
    calendar = ApplicationCoursesRemoteCalendar()
    if calendar.get_opened_academic_events():
        return HttpResponseRedirect(reverse('applications_overview'))

    previous_academic_event = calendar.get_previous_academic_event()
    if previous_academic_event:
        messages.add_message(
            request,
            messages.WARNING,
            _('The period of online application for courses %(year)s opened on %(start_date)s to %(end_date)s') % {
                'year': display_as_academic_year(previous_academic_event.authorized_target_year),
                'start_date': previous_academic_event.start_date.strftime('%d/%m/%Y'),
                'end_date': previous_academic_event.end_date.strftime('%d/%m/%Y')
                if previous_academic_event.end_date else ''
            }
        )

    next_academic_event = calendar.get_next_academic_event()
    if next_academic_event:
        messages.add_message(
            request,
            messages.WARNING,
            _('The period of online application for courses %(year)s will open on %(start_date)s to %(end_date)s') % {
                'year': display_as_academic_year(next_academic_event.authorized_target_year),
                'start_date': next_academic_event.start_date.strftime('%d/%m/%Y'),
                'end_date': next_academic_event.end_date.strftime('%d/%m/%Y') if next_academic_event.end_date else ''
            }
        )
    return layout.render(request, "attribution_access_denied.html", {})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
@require_http_methods(["GET", "POST"])
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
@require_http_methods(["GET"])
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def overview(request, global_id=None):
    tutor = mdl_base.tutor.find_by_user(request.user) if not global_id else \
        mdl_base.tutor.find_by_person_global_id(global_id)

    application_courses_calendars_opened = ApplicationCoursesRemoteCalendar().get_opened_academic_events()
    if not application_courses_calendars_opened:
        return redirect('outside_applications_period')
    elif len(application_courses_calendars_opened) > 1:
        logger.warning("Multiple application courses calendars opened at same time")

    application_course_calendar = application_courses_calendars_opened[0]
    application_academic_year = AcademicYear.objects.get(year=application_course_calendar.authorized_target_year)

    # Applications for current application academic year
    applications = tutor_application.get_application_list(
        global_id=tutor.person.global_id,
        academic_year=application_academic_year
    )

    # Attributions for next year
    attributions = attribution.get_attribution_list(
        global_id=tutor.person.global_id,
        academic_year=application_academic_year
    )
    volume_total_attributions = attribution.get_volumes_total(attributions)

    # Attribution which will be expire the year previous of application academic year
    previous_academic_year = application_academic_year.past()
    attributions_about_to_expired = attribution.get_attribution_list_about_to_expire(
        global_id=tutor.person.global_id,
        academic_year=previous_academic_year
    )

    for attrib in attributions:
        attrib['teachers'] = attribution.get_teachers(attrib['acronym'], application_academic_year.year)

    for an_attribution in attributions:
        attribution.update_learning_unit_volume(an_attribution, application_academic_year)
    if attributions_about_to_expired:
        for an_attribution in attributions_about_to_expired:
            attribution.update_learning_unit_volume(an_attribution, application_academic_year)
    return layout.render(request, "attribution_overview.html", {
        'a_tutor': tutor,
        'attributions': attributions,
        'previous_academic_year': previous_academic_year,
        'attributions_about_to_expire': attributions_about_to_expired,
        'application_academic_year': application_academic_year,
        'applications': applications,
        'tot_lecturing': volume_total_attributions.get(learning_component_year_type.LECTURING),
        'tot_practical': volume_total_attributions.get(learning_component_year_type.PRACTICAL_EXERCISES),
        'application_course_calendar': application_course_calendar,
        'catalog_url': settings.ATTRIBUTION_CONFIG.get('CATALOG_URL'),
        'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
    })


@login_required
@require_http_methods(["GET"])
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def search_vacant_attribution(request):
    tutor = mdl_base.tutor.find_by_user(request.user)
    attributions_vacant = None
    form = VacantAttributionFilterForm(data=request.GET)
    if request.GET and form.is_valid():
        attributions_vacant = _get_attributions_vacant(form, tutor)

    return layout.render(request, "attribution_vacant_list.html", {
        'a_tutor': tutor,
        'attributions_vacant': attributions_vacant,
        'search_form': form,
        'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
    })


@login_required
@require_http_methods(["POST"])
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def renew_applications(request):
    tutor = mdl_base.tutor.find_by_user(request.user)
    global_id = tutor.person.global_id
    application_courses_years_opened = ApplicationCoursesRemoteCalendar().get_target_years_opened()
    application_academic_year = AcademicYear.objects.get(year=application_courses_years_opened[0])

    post_data = dict(request.POST.lists())
    learning_container_year_acronyms = [param.split("_")[-1] for param, value in post_data.items() \
                                        if "learning_container_year_" in param]
    attributions_about_to_expired = attribution.get_attribution_list_about_to_expire(
        global_id=global_id,
        academic_year=application_academic_year.past()
    )
    attribution_to_renew_list = [attrib for attrib in attributions_about_to_expired
                                 if attrib.get('acronym') in learning_container_year_acronyms and \
                                 attrib.get('is_renewable', False)]
    if not attribution_to_renew_list:
        messages.add_message(request, messages.ERROR, _('No attribution renewed'))
        return redirect('applications_overview')

    l_containers_years = mdl_base.learning_container_year.search(id=[
        attrib.get('attribution_vacant', {}).get('learning_container_year_id')
        for attrib in attribution_to_renew_list
    ])

    for attri_to_renew in attribution_to_renew_list:
        learning_container_year = next((l_containers_year for l_containers_year in l_containers_years if
                                        l_containers_year.acronym == attri_to_renew.get('acronym')), None)

        application_data = {
            'charge_lecturing_asked': attri_to_renew.get(learning_component_year_type.LECTURING),
            'charge_practical_asked': attri_to_renew.get(learning_component_year_type.PRACTICAL_EXERCISES),
        }
        form = ApplicationForm(learning_container_year=learning_container_year,
                               data=application_data)
        if form.is_valid():
            application = form.cleaned_data
            try:
                tutor_application.create_or_update_application(global_id, application)
                tutor_application.set_pending_flag(global_id, application, tutor_application_epc.UPDATE_OPERATION)
                # Send signal to EPC
                tutor_application_epc.send_message(tutor_application_epc.UPDATE_OPERATION,
                                                   global_id,
                                                   application)
            except Exception as e:
                error_msg = "{}: {}".format(learning_container_year.acronym, e.args[0])
                messages.add_message(request, messages.ERROR, error_msg)
    return redirect('applications_overview')


@login_required
@require_http_methods(["GET", "POST"])
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def create_or_update_application(request, learning_container_year_id):
    tutor = mdl_base.tutor.find_by_user(request.user)
    global_id = tutor.person.global_id
    learning_unit_year = LearningUnitYear.objects.get(
        learning_container_year__id=learning_container_year_id,
        subtype=learning_unit_year_subtypes.FULL
    )
    learning_container_year = learning_unit_year.learning_container_year
    can_be_saved = True

    if request.method == 'POST':
        form = ApplicationForm(learning_container_year=learning_container_year,
                               data=request.POST)
        if form.is_valid():
            application = form.cleaned_data
            try:
                tutor_application.create_or_update_application(global_id, application)
                tutor_application.set_pending_flag(global_id, application, tutor_application_epc.UPDATE_OPERATION)
                # Send message to EPC
                tutor_application_epc.send_message(tutor_application_epc.UPDATE_OPERATION,
                                                   global_id,
                                                   application)
            except Exception as e:
                error_msg = e.args[0]
                messages.add_message(request, messages.ERROR, error_msg)
            return redirect('applications_overview')
    else:
        inital_data = tutor_application.get_application(global_id, learning_container_year)
        can_be_saved = tutor_application.can_be_updated(inital_data) if inital_data else True
        form = ApplicationForm(
            initial=inital_data,
            learning_container_year=learning_container_year,
        )

    return layout.render(request, "application_form.html", {
        'a_tutor': tutor,
        'form': form,
        'learning_container_year': learning_container_year,
        'learning_unit_year': learning_unit_year,
        'can_be_saved': can_be_saved,
        'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
    })


@login_required
@require_http_methods(["POST"])
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def delete_application(request, learning_container_year_id):
    tutor = mdl_base.tutor.find_by_user(request.user)
    global_id = tutor.person.global_id
    learning_container_year = mdl_base.learning_container_year.find_by_id(learning_container_year_id)

    application_to_delete = tutor_application.get_application(global_id, learning_container_year)
    if application_to_delete:
        try:
            # Delete with FLAG Pending
            tutor_application.set_pending_flag(global_id, application_to_delete,
                                               tutor_application_epc.DELETE_OPERATION)
            # Send signal to EPC
            tutor_application_epc.send_message(tutor_application_epc.DELETE_OPERATION,
                                               global_id,
                                               application_to_delete)
        except Exception as e:
            error_msg = e.args[0]
            messages.add_message(request, messages.ERROR, error_msg)
        return redirect('applications_overview')
    raise Http404


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@require_http_methods(["POST"])
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
def send_mail_applications_summary(request):
    tutor = mdl_base.tutor.find_by_user(request.user)
    global_id = tutor.person.global_id
    error_msg = tutor_application.send_mail_applications_summary(global_id)
    if error_msg:
        messages.add_message(request, messages.ERROR, _(error_msg))
    else:
        messages.add_message(request, messages.INFO, _('An email with your applications have been sent'))
    return redirect('applications_overview')


def _get_attributions_vacant(form, tutor):
    application_courses_years_opened = ApplicationCoursesRemoteCalendar().get_target_years_opened()
    application_academic_year = AcademicYear.objects.get(year=application_courses_years_opened[0])
    attributions_vacant = attribution.get_attribution_vacant_list(
        acronym_filter=form.cleaned_data['learning_container_acronym'],
        academic_year=application_academic_year,
        faculty=form.cleaned_data['faculty'],
    )
    attributions_vacant = tutor_application.mark_attribution_already_applied(
        attributions_vacant,
        tutor.person.global_id,
        application_academic_year
    )
    if attributions_vacant:
        for an_attribution in attributions_vacant:
            attribution.update_learning_unit_volume(an_attribution, application_academic_year)
    for attrib in attributions_vacant:
        attrib['teachers'] = attribution.get_teachers(attrib['acronym'],
                                                      application_academic_year.year)
    return attributions_vacant
