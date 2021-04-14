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
import functools
import logging
import operator
import urllib
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from attribution.models.remote_attribution_service import RemoteAttributionService
from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views import layout

NO_DATA_VALUE = "-"
LEARNING_UNIT_ACRONYM_ID = "learning_unit_acronym_"
logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def students_list(request):
    data = get_learning_units(request.user)
    return render(request, "list/students_exam.html", data)


def get_learning_units(a_user):
    a_person = mdl_base.person.find_by_user(a_user)
    learning_units = []
    if a_person:
        current_academic_year = mdl_base.academic_year.current_academic_year()
        tutor = mdl_base.tutor.find_by_person(a_person)
        if current_academic_year and tutor:
            learning_units = __get_learning_unit_year_attributed(current_academic_year.year, a_person)
    return {'person': a_person, 'my_learning_units': learning_units}


def __get_learning_unit_year_attributed(year: int, person: Person) -> List:
    attributions = RemoteAttributionService.get_attributions_list(year, person)
    if attributions:
        filter_clause = functools.reduce(
            operator.or_,
            (
                (Q(acronym=attribution.code) & Q(academic_year__year=attribution.year))
                for attribution in attributions
            )
        )
        return list(LearningUnitYear.objects.filter(filter_clause))
    return []


def get_codes_parameter(request, academic_yr):
    learning_unit_years = None
    user_learning_units_assigned = get_learning_units(request.user).get('my_learning_units', [])
    for key, value in request.POST.items():
        if key.startswith(LEARNING_UNIT_ACRONYM_ID):
            acronym = key.replace(LEARNING_UNIT_ACRONYM_ID, '')
            learning_unit_years = build_learning_units_string(academic_yr, acronym, learning_unit_years,
                                                              user_learning_units_assigned)

    if learning_unit_years:
        return learning_unit_years

    return NO_DATA_VALUE


def build_learning_units_string(academic_yr, acronym, learning_unit_years_in, user_learning_units_assigned):
    learning_unit_years = learning_unit_years_in
    learning_units = mdl_base.learning_unit_year.find_by_acronym(acronym, academic_yr)
    if learning_units and learning_units[0] in user_learning_units_assigned:
        if learning_unit_years is None:
            learning_unit_years = "{0}".format(learning_units[0].acronym)
        else:
            learning_unit_years = "{0},{1}".format(learning_unit_years, learning_units[0].acronym)
    return learning_unit_years


def get_anac_parameter(current_academic_year):
    if current_academic_year:
        return str(current_academic_year.year)
    return NO_DATA_VALUE


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
@require_POST
def list_build(request):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    anac = get_anac_parameter(current_academic_year)
    codes = get_codes_parameter(request, current_academic_year)
    list_exam_enrollments_xls = fetch_student_exam_enrollment(str(anac), codes)
    if list_exam_enrollments_xls:
        return _make_xls_list(list_exam_enrollments_xls)
    else:
        data = get_learning_units(request.user)
        data.update({'msg_error': _('No data found')})
        return render(request, "list/students_exam.html", data)


def fetch_student_exam_enrollment(academic_year, codes):
    if codes == NO_DATA_VALUE or academic_year == NO_DATA_VALUE:
        return None
    server_top_url = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_URL')
    document_base_path = server_top_url + settings.ATTRIBUTION_CONFIG.get('ATTRIBUTION_PATH')
    if document_base_path:
        try:
            document_url = document_base_path.format(anac=academic_year, codes=codes)
            return _fetch_with_basic_auth(server_top_url, document_url)
        except Exception:
            logger.exception(
                "Error when fetching document (anac:{}, codes{}, url{})".format(academic_year, codes, document_url))
    return None


def _fetch_with_basic_auth(server_top_url, document_url):
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    username = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_USER')
    password = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_PASSWORD')
    password_mgr.add_password(None, server_top_url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    with opener.open(document_url) as response:
        return response.read()


def _make_xls_list(excel_list_student_enrolled):
    # xls extension because file received is xls
    filename = "Liste_Insc_Exam.xls"
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    response.write(excel_list_student_enrolled)
    return response


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def lists_of_students_exams_enrollments(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            data = get_learning_units_by_person(global_id)
            return render(request, "admin/students_exam_list.html", data)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/students_list.html", {"form": form})


def get_learning_units_by_person(global_id):
    a_person = mdl_base.person.find_by_global_id(global_id)
    learning_units = []
    if a_person:
        current_academic_year = mdl_base.academic_year.current_academic_year()
        tutor = mdl_base.tutor.find_by_person(a_person)
        if current_academic_year and tutor:
            learning_units = __get_learning_unit_year_attributed(current_academic_year.year, a_person)
    return {'person': a_person, 'learning_units': learning_units}


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
@require_POST
def list_build_by_person(request, global_id):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    anac = get_anac_parameter(current_academic_year)
    person = mdl_base.person.find_by_global_id(global_id)
    data = get_learning_units_by_person(person.global_id)
    codes = get_codes_parameter_list(request, current_academic_year, data)
    list_exam_enrollments_xls = fetch_student_exam_enrollment(str(anac), codes)
    if list_exam_enrollments_xls:
        return _make_xls_list(list_exam_enrollments_xls)
    else:
        data.update({'msg_error': _('No data found')})
        return render(request, "admin/students_exam_list.html", data)


def get_codes_parameter_list(request, academic_yr, data):
    learning_unit_years = None
    user_learning_units_assigned = data.get('learning_units', [])
    for key, value in request.POST.items():
        if key.startswith(LEARNING_UNIT_ACRONYM_ID):
            acronym = key.replace(LEARNING_UNIT_ACRONYM_ID, '')
            learning_unit_years = build_learning_units_string(academic_yr, acronym, learning_unit_years,
                                                              user_learning_units_assigned)
    if learning_unit_years:
        return learning_unit_years
    return NO_DATA_VALUE
