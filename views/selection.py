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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import formset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import base.models as mdl
import internship.models as mdl_int
from base.models.student import Student
from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.cohort_view_decorators import redirect_if_subscription_not_allowed
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations
from internship.forms.form_offer_preference import OfferPreferenceFormSet, OfferPreferenceForm
from internship.models.cohort import Cohort
from internship.models.internship import Internship
from internship.models.internship_speciality import InternshipSpeciality


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
@redirect_if_subscription_not_allowed
def view_internship_selection(request, cohort_id, internship_id=-1, speciality_id=-1):
    cohort = mdl_int.cohort.Cohort.objects.get(pk=cohort_id)
    internships = Internship.objects.filter(cohort=cohort).order_by("speciality__name", "name")

    if int(internship_id) < 1:
        internship_id = internships.first().id
    if request.POST:
        internship_id = request.POST['current_internship']
    if not mdl_int.internship_offer.cohort_open_for_selection(cohort):
        return layout.render(request, "internship_selection_closed.html", {'cohort': cohort})

    current_internship = internships.get(pk=internship_id)
    specialities = mdl_int.internship_speciality.find_selectables(cohort).order_by("name")
    student = mdl.student.find_by_user(request.user)
    saved_choices = []

    for internship in internships:
        internship.internship_choices = mdl_int.internship_choice.search(
            student=student, internship=internship, specialities=specialities
        )
        specialty = _get_chosen_specialty(internship, request)
        internship.chosen_specialty = specialty

        selectable_offers = mdl_int.internship_offer.find_selectable_by_speciality_and_cohort(specialty,
                                                                                              cohort)
        internship.formset = _handle_formset_to_save(request, selectable_offers, student, internship, specialty,
                                                     saved_choices)
        first_choices_by_organization = get_first_choices_by_organization(specialty, internship)
        internship.offers_forms = zip_offers_formset_and_first_choices(internship.formset, selectable_offers,
                                                                       first_choices_by_organization)
    if saved_choices:
        messages.add_message(
            request,
            messages.SUCCESS,
            _build_choices_saved_success_message(saved_choices)
        )

    return layout.render(
        request,
        "internship_selection.html",
        {
            "internships": internships,
            "current_internship": current_internship,
            "all_specialities": specialities,
            "cohort": cohort,
            "student": student,
        }
    )


def _get_chosen_specialty(internship, request):
    specialty = internship.speciality
    if internship.internship_choices.exists():
        specialty = internship.internship_choices.first().speciality
    specialty = _get_post_chosen_specialty(internship, request, specialty)
    return specialty


def _get_post_chosen_specialty(internship, request, specialty):
    if '{}-speciality_id'.format(internship) in request.POST:
        specialty_id = request.POST['{}-speciality_id'.format(internship)] or None
        if not internship.speciality and specialty_id:
            specialty = InternshipSpeciality.objects.get(pk=specialty_id)
    return specialty


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
@redirect_if_subscription_not_allowed
def get_selective_internship_preferences(request, cohort_id):
    cohort = Cohort.objects.get(pk=cohort_id)
    internship = Internship.objects.get(pk=request.GET.get('internship'))
    student = Student.objects.get(pk=request.GET.get('student'))
    if not request.GET.get('specialty'):
        return HttpResponseNotFound(reason="No specialty provided")
    specialty = InternshipSpeciality.objects.get(pk=request.GET.get('specialty'))

    internship_choices = mdl_int.internship_choice.search(
        student=student, internship=internship
    )

    selectable_offers = mdl_int.internship_offer.find_selectable_by_speciality_and_cohort(specialty, cohort)
    formset = _handle_formset_to_save(request, selectable_offers, student, internship, specialty, [])
    first_choices_by_organization = get_first_choices_by_organization(specialty, internship)
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


def get_first_choices_by_organization(speciality, internship):
    list_number_choices = mdl_int.internship_choice.get_number_first_choice_by_organization(speciality, internship)
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["organization"]] = \
            number_first_choices["organization__count"]
    return dict_number_choices_by_organization


def zip_offers_formset_and_first_choices(formset, internships_offers, number_choices_by_organization):
    zipped_data = None
    if internships_offers:
        zipped_data = []
        for offer, form in zip(internships_offers, formset):
            zipped_data.append((offer, form, number_choices_by_organization.get(offer.organization.id, 0)))
    return zipped_data


def _handle_formset_to_save(request, selectable_offers, student, internship, speciality, saved_choices):
    offer_preference_formset = _build_offer_preference_formset(internship, selectable_offers, speciality)
    formset = offer_preference_formset(prefix=internship)
    if request.method == 'POST':
        data = _filter_internship_form_data(request.POST, internship)
        if data:
            formset = offer_preference_formset(prefix=internship, data=data)
            if formset.is_valid():
                _save_preferences(formset, internship, speciality, student)
                saved_choices.append(internship)
            else:
                _show_error_message(formset, internship, request)
        else:
            _handle_empty_formset(internship, speciality, student)
    return formset


def _build_offer_preference_formset(internship, selectable_offers, speciality):
    if not internship.speciality:
        selectable_offers = mdl_int.internship_offer.find_selectable_by_speciality_and_cohort(
            speciality,
            internship.cohort
        )
    offer_preference_formset = formset_factory(
        OfferPreferenceForm,
        formset=OfferPreferenceFormSet,
        extra=len(selectable_offers),
        min_num=len(selectable_offers),
        max_num=len(selectable_offers),
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


def _save_preferences(formset, internship, speciality, student):
    _remove_previous_choices(student, internship, speciality)
    _save_student_choices(formset, student, internship, speciality)


def _handle_empty_formset(internship, speciality, student):
    internship.chosen_specialty = None
    _remove_previous_choices(student, internship, speciality)


def _build_error_message(errors, current_internship):
    error_message = _('Choices for %(internship)s have not been saved due to errors:') % {
        'internship': current_internship
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


def _remove_previous_choices(student, internship, speciality):
    if internship.speciality_id is not None:
        previous_choices = mdl_int.internship_choice.search(student=student, internship=internship,
                                                            speciality=speciality)
    else:
        previous_choices = mdl_int.internship_choice.search(student=student, internship=internship)
    if previous_choices:
        previous_choices.delete()


def _save_student_choices(formset, student, internship, speciality):
    for form in formset:
        _save_student_choice(form, student, internship, speciality)


def _save_student_choice(form, student, internship, speciality):
    if form.cleaned_data:
        offer_pk = form.cleaned_data["offer"]
        preference_value = int(form.cleaned_data["preference"])
        offer = mdl_int.internship_offer.find_by_pk(offer_pk)
        if has_been_selected(preference_value) and is_correct_speciality(offer, speciality):
            internship_choice = mdl_int.internship_choice.InternshipChoice(student=student,
                                                                           organization=offer.organization,
                                                                           speciality=speciality,
                                                                           choice=preference_value,
                                                                           internship=internship,
                                                                           priority=False)
            internship_choice.save()


def _filter_internship_form_data(data, internship):
    return {key: value for (key, value) in data.items() if internship.name in key and 'speciality_id' not in key}


def has_been_selected(preference_value):
    return bool(preference_value)


def is_correct_speciality(offer, speciality):
    return offer.speciality == speciality
