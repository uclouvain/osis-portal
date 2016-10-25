##############################################################################
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
##############################################################################
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from admission import models as mdl
from admission.views import demande_validation
from admission.forms import SociologicalSurveyForm
from admission.models.sociological_survey import SociologicalSurvey
from admission.views import attachments, accounting


def update(request, application_id=None):
    """
    Sociological survey of an applicant.
    """
    applicant = mdl.applicant.find_by_user(request.user)
    next_tab = 5
    if request.method == "POST":
        sociological_form = SociologicalSurveyForm(request.POST)
        if sociological_form.is_valid():
            save_sociological_form(sociological_form, request.user)
            next_tab = request.POST.get('next_tab', 'next')
            return redirect_to_next_tab(next_tab)
    else:
        try:    # Prefill the form if the user already filled it.
            u = SociologicalSurvey.objects.get(applicant=applicant)
            sociological_form = SociologicalSurveyForm(instance=u)
        except ObjectDoesNotExist:
            sociological_form = SociologicalSurveyForm()

    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)

    data = {
        'tab_active': next_tab,
        'application': application,
        'applications': mdl.application.find_by_user(request.user),
        'sociological_form': sociological_form
    }
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def save_sociological_form(sociological_form, user):
    """
    Save a sociological form.
    The form must have passed the is_valid check.
    :param sociological_form: a form of type SociologicalForm
    :param user: the current user
    :return:
    """
    applicant = mdl.applicant.find_by_user(user)
    number_brothers_sisters = sociological_form.cleaned_data['number_brothers_sisters']
    father_is_deceased = sociological_form.cleaned_data['father_is_deceased']
    father_education = sociological_form.cleaned_data['father_education']
    father_profession = sociological_form.cleaned_data['father_profession']
    mother_is_deceased = sociological_form.cleaned_data['mother_is_deceased']
    mother_education = sociological_form.cleaned_data['mother_education']
    mother_profession = sociological_form.cleaned_data['mother_profession']
    student_professional_activity = sociological_form.cleaned_data['student_professional_activity']
    student_profession = sociological_form.cleaned_data['student_profession']
    conjoint_professional_activity = sociological_form.cleaned_data['conjoint_professional_activity']
    conjoint_profession = sociological_form.cleaned_data['conjoint_profession']
    paternal_grandfather_profession = sociological_form.cleaned_data['paternal_grandfather_profession']
    maternal_grandfather_profession = sociological_form.cleaned_data['maternal_grandfather_profession']

    sociological_survey = SociologicalSurvey(applicant=applicant,
                                             number_brothers_sisters=number_brothers_sisters,
                                             father_is_deceased=father_is_deceased, father_education=father_education,
                                             father_profession=father_profession, mother_is_deceased=mother_is_deceased,
                                             mother_education=mother_education, mother_profession=mother_profession,
                                             student_professional_activity=student_professional_activity,
                                             student_profession=student_profession,
                                             conjoint_professional_activity=conjoint_professional_activity,
                                             conjoint_profession=conjoint_profession,
                                             paternal_grandfather_profession=paternal_grandfather_profession,
                                             maternal_grandfather_profession=maternal_grandfather_profession)
    sociological_survey.save()  # Will update or create depending if a record exist with the same applicant


def redirect_to_next_tab(next_tab):
    """
    Redirect to the next or previous page.
    The next page is the "attachments" one and
    the previous is the "accounting" one.
    :param next_tab: a string equals to previous or next
    :return: redirect to another page
    """
    if next_tab == "previous":
        return redirect(accounting.accounting_update)
    return redirect(attachments.update)

