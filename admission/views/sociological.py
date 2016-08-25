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
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from admission import models as mdl
from admission.views import demande_validation
from admission.views import tabs
from admission.forms import SociologicalSurveyForm
from admission.models.sociological_survey import SociologicalSurvey


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
            next_tab = request.POST.get('next_tab', 5) #TODO check value

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

    tab_status = tabs.init(request)
    return render(request, "admission_home.html",
                  {'tab_active':             next_tab,
                   'application':            application,
                   'validated_profil':       demande_validation.validate_profil(applicant),
                   'validated_diploma':      demande_validation.validate_diploma(application),
                   'validated_curriculum':   demande_validation.validate_curriculum(application),
                   'validated_application':  demande_validation.validate_application(application),
                   'validated_accounting':   demande_validation.validate_accounting(),
                   'validated_sociological': demande_validation.validate_sociological(),
                   'validated_attachments':  demande_validation.validate_attachments(),
                   'validated_submission':   demande_validation.validate_submission(),
                   'tab_profile': tab_status['tab_profile'],
                   'tab_applications': tab_status['tab_applications'],
                   'tab_diploma': tab_status['tab_diploma'],
                   'tab_curriculum': tab_status['tab_curriculum'],
                   'tab_accounting': tab_status['tab_accounting'],
                   'tab_sociological': tab_status['tab_sociological'],
                   'tab_attachments': tab_status['tab_attachments'],
                   'tab_submission': tab_status['tab_submission'],
                   'applications': mdl.application.find_by_user(request.user),
                   'sociological_form': sociological_form})


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
