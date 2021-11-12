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
import urllib
from typing import List, Dict

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from assessments.services.assessments import AssessmentsService
from attribution.services.attribution import AttributionService
from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.models.academic_year import AcademicYear
from base.models.person import Person
from base.views import layout
from learning_unit.services.learning_unit import LearningUnitService

NO_DATA_VALUE = "-"
LEARNING_UNIT_ACRONYM_ID = "learning_unit_acronym_"
logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.can_access_attribution', raise_exception=True)
def students_list(request):
    current_session_dict = AssessmentsService.get_current_session(request.user.person)
    if current_session_dict:
        data = get_learning_units(request, current_session_dict)
    else:
        data = _get_warning_concerning_sessions(request.user.person)
    return render(request, "list/students_exam.html", data)


def get_learning_units(request, current_session_dict: Dict):
    a_user = request.user
    a_person = mdl_base.person.find_by_user(a_user)
    learning_units = []
    if a_person:
        tutor = mdl_base.tutor.find_by_person(a_person)
        if tutor:
            learning_units = __get_learning_unit_year_attributed(request, a_person, current_session_dict.year)
    return {
        'person': a_person,
        'my_learning_units': learning_units,
        'current_session': current_session_dict
    }


def __get_learning_unit_year_attributed(request, person: Person, year: int) -> List[Dict]:
    learning_units_by_person = []
    attributions = AttributionService.get_attributions_list(
        year, person,
        with_effective_class_repartition=True
    )
    if attributions:
        learning_unit_codes = {attribution.code for attribution in attributions}
        score_responsible_list = AssessmentsService.get_score_responsible_list(
            learning_unit_codes=list(learning_unit_codes),
            year=year,
            person=person)
        learning_units = LearningUnitService.get_learning_units(
            learning_unit_codes=list(learning_unit_codes),
            year=year,
            person=person
        )

        if isinstance(learning_units, List):
            for learning_unit in learning_units:
                ue_acronym = learning_unit.get('acronym', '')
                learning_unit.update(
                    {
                        'score_responsible': _get_score_responsible(score_responsible_list, ue_acronym),
                        'effective_class_detail': _get_all_effective_class_repartition(
                            attributions,
                            ue_acronym,
                            score_responsible_list
                        ),
                    }
                )
                learning_units_by_person.append({'acronym': ue_acronym, 'learning_unit': learning_unit})
        else:
            messages.add_message(
                request,
                messages.ERROR,
                learning_units.error if learning_units.error else _('Unexpected error')
            )
    return learning_units_by_person


def build_learning_units_string(
        academic_yr: int,
        acronym: str,
        learning_unit_years_in: List,
        user_learning_units_assigned: List[str],
        person: Person
) -> List:
    learning_unit_years = learning_unit_years_in
    learning_units = LearningUnitService.get_learning_units(
        learning_unit_codes=[acronym],
        year=academic_yr,
        person=person
    )

    if learning_units:
        ue_acronym = learning_units[0].get('acronym')
        if ue_acronym in user_learning_units_assigned:
            if learning_unit_years is None:
                learning_unit_years = "{0}".format(ue_acronym)
            else:
                learning_unit_years = "{0},{1}".format(user_learning_units_assigned, ue_acronym)

    return learning_unit_years


def get_anac_parameter(current_academic_year: AcademicYear):
    return str(current_academic_year.year) if current_academic_year else NO_DATA_VALUE


@login_required
@permission_required('base.can_access_attribution', raise_exception=True)
@require_POST
def list_build(request):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    anac = get_anac_parameter(current_academic_year)
    current_session_dict = AssessmentsService.get_current_session(request.user.person)
    learning_unit_acronyms = _get_learning_unit_acronyms(
        get_learning_units(request, current_session_dict).get('my_learning_units', []))
    codes = get_codes_parameter_list(request, current_academic_year, learning_unit_acronyms)
    list_exam_enrollments_xls = fetch_student_exam_enrollment(str(anac), codes)
    if list_exam_enrollments_xls:
        return _make_xls_list(list_exam_enrollments_xls)
    else:
        current_session_dict = AssessmentsService.get_current_session(request.user.person)
        data = get_learning_units(request, current_session_dict)
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
@permission_required('base.can_access_attribution', raise_exception=True)
def lists_of_students_exams_enrollments(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            data = get_learning_units_by_person(request, global_id)
            return render(request, "admin/students_exam_list.html", data)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/students_list.html", {"form": form})


def get_learning_units_by_person(request, global_id: str) -> Dict:
    a_person = mdl_base.person.find_by_global_id(global_id)
    learning_units = []
    current_session_dict = {}
    if a_person:
        current_session_dict = AssessmentsService.get_current_session(a_person)
        tutor = mdl_base.tutor.find_by_person(a_person)
        if tutor and current_session_dict:
            learning_units = __get_learning_unit_year_attributed(
                request,
                a_person,
                current_session_dict.year
            )

    return {
        'person': a_person,
        'learning_units': learning_units,
        'current_session': current_session_dict
    }


@login_required
@permission_required('base.can_access_attribution', raise_exception=True)
@require_POST
def list_build_by_person(request, global_id: str):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    anac = get_anac_parameter(current_academic_year)
    person = mdl_base.person.find_by_global_id(global_id)
    data = get_learning_units_by_person(request, person.global_id)
    user_learning_units_assigned = data.get('learning_units', [])
    learning_unit_acronyms = _get_learning_unit_acronyms(user_learning_units_assigned)
    codes = get_codes_parameter_list(request, current_academic_year, learning_unit_acronyms)
    list_exam_enrollments_xls = fetch_student_exam_enrollment(str(anac), codes)
    if list_exam_enrollments_xls:
        return _make_xls_list(list_exam_enrollments_xls)
    else:
        data.update({'msg_error': _('No data found')})
        return render(request, "admin/students_exam_list.html", data)


def get_codes_parameter_list(request, current_academic_year: AcademicYear, learning_unit_acronyms: List[str]):
    academic_yr = current_academic_year.year if current_academic_year else None
    learning_unit_years = None

    for key, value in request.POST.items():
        if key.startswith(LEARNING_UNIT_ACRONYM_ID):
            acronym = key.replace(LEARNING_UNIT_ACRONYM_ID, '')
            learning_unit_years = build_learning_units_string(academic_yr, acronym, learning_unit_years,
                                                              learning_unit_acronyms, request.user.person)
    if learning_unit_years:
        return learning_unit_years
    return NO_DATA_VALUE


def _get_all_effective_class_repartition(attributions: List, ue_acronym: str, score_responsible_list: List) -> List:
    classes = [
        _class for attr in attributions for _class in attr.effective_class_repartition if attr.code == ue_acronym
    ]

    list_of_unique_dicts_effective_class_repartition = {x['code']: x for x in classes}.values()
    sorted_list_of_unique_dicts_effective_class_repartition = sorted(
        list_of_unique_dicts_effective_class_repartition,
        key=lambda d: d['code']
    )

    effective_class_detail = []
    for effective_class in sorted_list_of_unique_dicts_effective_class_repartition:
        score_responsible = _get_score_responsible(score_responsible_list, effective_class.code)

        effective_class_detail.append(
            {
                'effective_class_repartition': effective_class,
                'score_responsible': score_responsible
            }
        )

    return effective_class_detail


def _get_score_responsible(score_responsibles: List, lu_acronym: str) -> str:
    if score_responsibles:
        return next(
            (pers.get('full_name') for pers in score_responsibles if pers.get('learning_unit_acronym') == lu_acronym),
            ''
        )
    return ''


def _get_learning_unit_acronyms(user_learning_units_assigned: List[Dict]) -> List[str]:
    learning_unit_acronyms = set()
    for learning_unit in user_learning_units_assigned:
        learning_unit_acronyms.add(learning_unit.get('acronym'))
    return list(learning_unit_acronyms)


def _get_warning_concerning_sessions(a_person: Person) -> Dict:
    date_format = str(_('date_format'))

    previous_session_dict = AssessmentsService.get_previous_session(a_person)
    str_date = previous_session_dict.get('end_date').strftime(date_format)
    previous_session_msg = \
        _("The period of scores' encoding for %(month_session)s session is closed since %(str_date)s") \
        % {
            'month_session': previous_session_dict.get('month_session_name').lower(),
            'str_date': str_date
        }

    next_session_dict = AssessmentsService.get_next_session(a_person)
    str_date = next_session_dict.get('start_date').strftime(date_format)
    next_session_msg = \
        _("The period of scores' encoding for %(month_session)s session will be open %(str_date)s. "
          "The 'Lists of students enrolled to my exams' will be available at that date") \
        % {
            'month_session': next_session_dict.get('month_session_name').lower(),
            'str_date': str_date
        }
    return {'messages_error': {previous_session_msg, next_session_msg}}
