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

import urllib

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.conf import settings

from base import models as mdl_base
from attribution import models as mdl_attribution

NO_DATA_VALUE = "-"
LEARNING_UNIT_ACRONYM_ID = "learning_unit_acronym_"


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def students_list(request):
    data = get_learning_units(request)
    return render(request, "list/students_exam.html", data)


def get_learning_units(request):
    a_person = mdl_base.person.find_by_user(request.user)
    learning_units = []
    if a_person:
        current_academic_year = mdl_base.academic_year.current_academic_year()
        tutor = mdl_base.tutor.find_by_person(a_person)
        attributions = mdl_attribution.attribution.find_by_tutor_year(tutor, current_academic_year)
        learning_units = []
        for a in attributions:
            if a.learning_unit_year not in learning_units:
                learning_units.append(a.learning_unit_year)
    data = {'person': a_person,
            'my_learning_units': learning_units}
    return data


def get_codes_parameter(request, academic_yr):
    learning_unit_years = None
    for key, value in request.POST.items():
        if key.startswith(LEARNING_UNIT_ACRONYM_ID):
            acronym = key.replace(LEARNING_UNIT_ACRONYM_ID, '')
            learning_units = mdl_base.learning_unit_year.find_by_acronym(acronym, academic_yr)
            if learning_units:
                if learning_unit_years is None:
                    learning_unit_years = "{0}".format(learning_units[0].acronym)
                else:
                    learning_unit_years = "{0},{1}".format(learning_unit_years, learning_units[0].acronym)

    if learning_unit_years:
        return learning_unit_years

    return NO_DATA_VALUE


def get_anac_parameter(current_academic_year):
    if current_academic_year:
        return str(current_academic_year.year)
    return NO_DATA_VALUE


def list_build(request):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    anac = get_anac_parameter(current_academic_year)
    codes = get_codes_parameter(request, current_academic_year)
    list_exam_enrollments_xls = fetch_student_exam_enrollment(str(anac), codes)
    if list_exam_enrollments_xls:
        return _make_xls_list(list_exam_enrollments_xls)
    else:
        data = get_learning_units(request)
        data.update({'msg_error': _('no_data')})
        return render(request, "list/students_exam.html", data)


def fetch_student_exam_enrollment(academic_year, codes):
    server_top_url = settings.LIST_CONFIG.get('SERVER_TO_FETCH_URL')
    document_base_path = server_top_url + settings.LIST_CONFIG.get('LIST_PATH')
    if document_base_path:
        try:
            document_url = document_base_path.format(anac=academic_year,
                                                     codes=codes)
            return _fetch_with_basic_auth(server_top_url, document_url)
        except Exception as e:
            pass
    return None


def _fetch_with_basic_auth(server_top_url, document_url):
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    username = settings.LIST_CONFIG.get('SERVER_TO_FETCH_USER')
    password = settings.LIST_CONFIG.get('SERVER_TO_FETCH_PASSWORD')
    password_mgr.add_password(None, server_top_url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    with opener.open(document_url) as response:
        return response.read()


def _make_xls_list(attestation_pdf):
    filename = "Liste_Insc_Exam.xls"
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    response.write(attestation_pdf)
    return response
