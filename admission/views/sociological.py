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
from admission.forms import SociologicalSurveyForm
from admission.models.sociological_survey import SociologicalSurvey
from admission.views import navigation

CHECKED_STATUS = 'on'


def update(request, application_id=None):
    """
    Sociological survey of an applicant.
    :param request
    :param application_id
    """
    applicant = mdl.applicant.find_by_user(request.user)
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)

    next_tab = navigation.SOCIOLOGICAL_SURVEY_TAB
    sociological_survey = None
    if request.method == "POST":
        save_sociological_form(request)

        sociological_survey = SociologicalSurvey.objects.get(applicant=applicant)
        sociological_form = SociologicalSurveyForm(instance=sociological_survey)
        sociological_form.is_valid()

        following_tab = navigation.get_following_tab(request, 'sociological', application)
        if following_tab:
            return following_tab
    else:
        try:    # Prefill the form if the user already filled it.
            sociological_survey = SociologicalSurvey.objects.get(applicant=applicant)
            sociological_form = SociologicalSurveyForm(instance=sociological_survey)
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
        'sociological_form': sociological_form,
        'professions': mdl.profession.find_by_adoc(False),
        'sociological_survey': sociological_survey
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def save_sociological_form(request):
    """
    Save a sociological form.
    The form must have passed the is_valid check.
    :param request
    :return:
    """
    user = request.user
    applicant = mdl.applicant.find_by_user(user)
    if request.POST.get('number_brothers_sisters') and request.POST.get('number_brothers_sisters').isnumeric():
        number_brothers_sisters = int(request.POST.get('number_brothers_sisters'))
    else:
        number_brothers_sisters = 0
    father_is_deceased = get_boolean_status(request.POST.get('father_is_deceased'))

    if request.POST.get('father_education') is None \
            or (request.POST.get('father_education').startswith('-') or request.POST.get('father_education') == ''):
        father_education = None
    else:
        father_education = request.POST.get('father_education')
    father_profession = get_profession(request.POST.get('father_profession'),
                                       request.POST.get('father_profession_other_name'))
    mother_is_deceased = get_boolean_status(request.POST.get('mother_is_deceased'))
    if request.POST.get('father_education') is None \
            or (request.POST.get('mother_education').startswith('-') or request.POST.get('mother_education') == ''):
        mother_education = None
    else:
        mother_education = request.POST.get('mother_education')
    mother_profession = get_profession(request.POST.get('mother_profession'),
                                       request.POST.get('mother_profession_other_name'))
    if request.POST.get('student_professional_activity') != '-':
        student_professional_activity = request.POST.get('student_professional_activity')
    else:
        student_professional_activity = None
    student_profession = get_profession(request.POST.get('student_profession'),
                                        request.POST.get('student_profession_other_name'))
    if request.POST.get('conjoint_professional_activity') != '-':
        conjoint_professional_activity = request.POST.get('conjoint_professional_activity')
    else:
        conjoint_professional_activity = None
    conjoint_profession = get_profession(request.POST.get('conjoint_profession'),
                                         request.POST.get('conjoint_profession_other_name'))
    paternal_grandfather_profession = get_profession(request.POST.get('paternal_grandfather_profession'),
                                                     request.POST.get('paternal_grandfather_profession_other_name'))
    maternal_grandfather_profession = get_profession(request.POST.get('maternal_grandfather_profession'),
                                                     request.POST.get('maternal_grandfather_profession_other_name'))

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


def get_other_profession(field):
    if field:
        existing_profession = mdl.profession.find_by_name(field)
        if existing_profession:
            return existing_profession
        else:
            new_profession = mdl.profession.Profession()
            new_profession.adhoc = True
            new_profession.name = field
            new_profession.save()
            return new_profession
    return None


def get_profession(known_profession_id, other):
    if known_profession_id and known_profession_id != '-' and known_profession_id.isnumeric():
        return mdl.profession.find_by_id(int(known_profession_id))
    else:
        return get_other_profession(other)


def get_boolean_status(field_value):
    if field_value and field_value == CHECKED_STATUS:
        return True
    else:
        return False
