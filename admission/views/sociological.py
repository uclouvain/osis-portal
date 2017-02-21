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
from admission import models as mdl
from admission.views import demande_validation
from admission.forms.sociological_survey import SociologicalSurveyForm
from admission.models import sociological_survey as sociological_survey_mdl
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
    sociological_survey = sociological_survey_mdl.find_by_applicant(applicant)
    if request.method == "POST":
        sociological_form = SociologicalSurveyForm(request.POST)
        if sociological_form.is_valid():
            sociological_form.save(applicant=applicant)
            sociological_survey = sociological_survey_mdl.find_by_applicant(applicant)
            following_tab = navigation.get_following_tab(request, 'sociological', application)
            if following_tab:
                return following_tab
            else:
                sociological_form = SociologicalSurveyForm(instance=sociological_survey)
    elif sociological_survey:
        sociological_form = SociologicalSurveyForm(instance=sociological_survey)
    else:
        sociological_form = SociologicalSurveyForm()

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


