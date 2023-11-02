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
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import formset_factory
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import base.models as mdl
from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.cohort_view_decorators import redirect_if_subscription_not_allowed
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations
from internship.forms.form_offer_preference import OfferPreferenceFormSet, OfferPreferenceForm
from internship.services.internship import InternshipAPIService


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
@redirect_if_subscription_not_allowed
def view_internship_selection(request, cohort_id, internship_id=None):
    cohort = InternshipAPIService.get_cohort_detail(cohort_name=cohort_id, person=request.user.person)
    internships = InternshipAPIService.get_internships_by_cohort(cohort_name=cohort_id, person=request.user.person)

    if not InternshipAPIService.is_cohort_open_for_selection(cohort_name=cohort_id, person=request.user.person):
        return layout.render(request, "internship_selection_closed.html", {'cohort': cohort})

    if request.POST:
        internship_id = request.POST['current_internship']
    elif not internship_id:
        internship_id = internships[0].uuid

    current_internship = next(internship for internship in internships if internship.uuid == internship_id)

    specialties = InternshipAPIService.get_selectable_specialties(cohort_name=cohort_id, person=request.user.person)
    student = mdl.student.find_by_user(request.user)
    saved_choices = []

    # transform to SimpleNamespace to have free-form internship objects
    internships = [SimpleNamespace(**internship._data_store) for internship in internships]

    student_choices = InternshipAPIService.get_student_choices(
        person=request.user.person, cohort_name=cohort_id
    ).results

    all_selectable_offers = InternshipAPIService.get_internship_offers(
        person=request.user.person, cohort_name=cohort_id, selectable=True
    ).results

    all_first_choices = InternshipAPIService.get_number_first_choice_by_organization(
        person=request.user.person, cohort_name=cohort_id,
    ).results

    for internship in internships:
        internship.internship_choices = [choice for choice in student_choices if choice.internship == internship.name]
        specialty = _get_chosen_specialty(internship, request)
        internship.chosen_specialty = specialty.to_dict() if specialty else None
        selectable_offers = [
            offer for offer in all_selectable_offers if specialty and offer.speciality.uuid == specialty.uuid
        ]
        internship.formset = _handle_formset_to_save(
            request, all_selectable_offers, selectable_offers, student, internship, specialty, saved_choices
        )
        first_choices_by_organization = get_first_choices_by_organization(all_first_choices, specialty)
        internship.offers_forms = zip_offers_formset_and_first_choices(
            internship.formset, selectable_offers, first_choices_by_organization
        )
    if saved_choices:
        messages.add_message(
            request,
            messages.SUCCESS,
            _build_choices_saved_success_message(saved_choices)
        )
        return HttpResponseRedirect("{}#{}".format(request.path_info, current_internship.uuid))

    return layout.render(
        request,
        "internship_selection.html",
        {
            "internships": internships,
            "current_internship": current_internship,
            "all_specialities": specialties,
            "cohort": cohort,
            "student": student,
        }
    )


def _get_chosen_specialty(internship, request):
    specialty = internship.speciality
    if internship.internship_choices:
        specialty = internship.internship_choices[0].specialty
    specialty = _get_post_chosen_specialty(internship, request, specialty)
    return specialty


def _get_post_chosen_specialty(internship, request, specialty):
    if '{}-speciality_id'.format(internship.name) in request.POST:
        specialty_id = request.POST['{}-speciality_id'.format(internship.name)] or None
        if not internship.speciality and specialty_id:
            specialty = InternshipAPIService.get_specialty(specialty_uuid=specialty_id, person=request.user.person)
    return specialty


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
@redirect_if_subscription_not_allowed
def get_selective_internship_preferences(request, cohort_id):
    internship = InternshipAPIService.get_internship(
        internship_uuid=request.GET.get('internship'), person=request.user.person
    )

    if not request.GET.get('specialty'):
        return HttpResponseNotFound(reason="No specialty provided")

    specialty = InternshipAPIService.get_specialty(
        specialty_uuid=request.GET.get('specialty'), person=request.user.person
    )

    internship_choices = InternshipAPIService.get_internship_student_choices(
        person=request.user.person, internship_uuid=internship.uuid
    )

    all_selectable_offers = InternshipAPIService.get_internship_offers(
        person=request.user.person, cohort_name=cohort_id, selectable=True
    ).results

    selectable_offers = [offer for offer in all_selectable_offers if offer.speciality.uuid == specialty.uuid]

    all_first_choices = InternshipAPIService.get_number_first_choice_by_organization(
        person=request.user.person, cohort_name=cohort_id,
    ).results

    formset = _handle_formset_to_save(
        request, all_selectable_offers, selectable_offers, None, internship, specialty, []
    )
    first_choices_by_organization = get_first_choices_by_organization(all_first_choices, specialty)
    offers_forms = zip_offers_formset_and_first_choices(formset, selectable_offers, first_choices_by_organization)

    return render(
        request,
        "fragment/internship_preferences.html",
        {
            "internship": internship,
            "formset": formset,
            "offers_forms": offers_forms,
            "internship_choices": internship_choices
        }
    )


def get_first_choices_by_organization(all_first_choices, specialty):
    list_number_choices = [
        choice for choice in all_first_choices if specialty and choice.specialty_uuid == specialty.uuid
    ]
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["reference"]] = \
            number_first_choices["count"]
    return dict_number_choices_by_organization


def zip_offers_formset_and_first_choices(formset, internships_offers, number_choices_by_organization):
    zipped_data = None
    if internships_offers:
        zipped_data = []
        for offer, form in zip(internships_offers, formset):
            zipped_data.append((offer, form, number_choices_by_organization.get(offer.organization.reference, 0)))
    return zipped_data


def _handle_formset_to_save(
        request, all_selectable_offers, selectable_offers, student, internship, speciality, saved_choices
):
    offer_preference_formset = _build_offer_preference_formset(
        request.user.person, internship, all_selectable_offers, selectable_offers, speciality
    )
    formset = offer_preference_formset(prefix=internship.name)
    if request.method == 'POST':
        data = _filter_internship_form_data(request.POST, internship)
        if data:
            formset = offer_preference_formset(prefix=internship.name, data=data)
            if formset.is_valid():
                _save_preferences(formset, internship, speciality, student, all_selectable_offers)
                saved_choices.append(internship)
            else:
                _show_error_message(formset, internship, request)
        else:
            _handle_empty_formset(internship, speciality, student)
    return formset


def _build_offer_preference_formset(person, internship, all_selectable_offers, selectable_offers, speciality):
    selectable_offers_count = len(selectable_offers)
    if not internship.speciality:
        selectable_offers = [
            offer for offer in all_selectable_offers if speciality and offer.speciality.uuid == speciality.uuid
        ]
        selectable_offers_count = len(selectable_offers)
    offer_preference_formset = formset_factory(
        OfferPreferenceForm,
        formset=OfferPreferenceFormSet,
        extra=selectable_offers_count,
        min_num=selectable_offers_count,
        max_num=selectable_offers_count,
        validate_min=True,
        validate_max=True
    )
    return offer_preference_formset


def _show_error_message(formset, internship, request):
    messages.add_message(
        request,
        messages.ERROR,
        _build_error_message(formset.non_form_errors(), internship)
    )


def _save_preferences(formset, internship, speciality, student, all_selectable_offers):
    InternshipAPIService.delete_internship_choices(person=student.person, internship_uuid=internship.uuid)
    _save_student_choices(formset, student, internship, speciality, all_selectable_offers)


def _handle_empty_formset(internship, speciality, student):
    internship.chosen_specialty = None


def _build_error_message(errors, current_internship):
    error_message = _('Choices for %(internship)s have not been saved due to errors:') % {
        'internship': current_internship.name
    }
    error_message += "<ul>"
    for error in errors:
        error_message += "<li>{}</li>".format(error)
    error_message += "</ul>"
    return mark_safe(error_message)


def _build_choices_saved_success_message(saved_choices):
    success_message = _('Choices have been successfully saved for: ')
    success_message += ", ".join([internship.name for internship in saved_choices])
    return mark_safe(success_message)


def _save_student_choices(formset, student, internship, speciality, all_selectable_offers):
    for form in formset:
        _save_student_choice(form, student, internship, speciality, all_selectable_offers)


def _save_student_choice(form, student, internship, speciality, all_selectable_offers):
    if form.cleaned_data:
        offer_uuid = form.cleaned_data["offer"]
        preference_value = int(form.cleaned_data["preference"])
        offer = next(offer for offer in all_selectable_offers if offer.uuid == str(offer_uuid))
        if has_been_selected(preference_value) and is_correct_speciality(offer, speciality):
            InternshipAPIService.save_internship_choice(
                person=student.person,
                cohort_name=offer.cohort,
                internship_uuid=internship.uuid,
                organization_uuid=offer.organization.uuid,
                specialty_uuid=speciality.uuid,
                choice=preference_value,
            )


def _filter_internship_form_data(data, internship):
    return {key: value for (key, value) in data.items() if internship.name in key
            if internship.name in key and 'speciality_id' not in key}


def has_been_selected(preference_value):
    return bool(preference_value)


def is_correct_speciality(offer, speciality):
    return offer.speciality.uuid == speciality.uuid
