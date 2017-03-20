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
import json

from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _

from base.forms.base_forms import RegistrationIdForm
from base.models import student as student_mdl, person as person_mdl
from attestation.queues import student_attestation_status, student_attestation
from base.views import layout
from dashboard.views import main as dash_main_view


@login_required
@permission_required('base.is_student', raise_exception=True)
def home(request):
    try:
        student = student_mdl.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    if student:
        json_message = _make_registration_json_message(student.registration_id)
        attestation_statuses_json_dict = student_attestation_status.fetch_json_attestation_statuses(json_message)
    else:
        attestation_statuses_json_dict = None
    data = _make_attestation_data(attestation_statuses_json_dict, student)
    return layout.render(request, "attestation_home.html", data)


@login_required
@permission_required('base.is_student', raise_exception=True)
def download_attestation(request, academic_year, attestation_type):
    try:
        student = student_mdl.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    attestation_pdf = student_attestation.fetch_student_attestation(student.person.global_id,
                                                                    academic_year,
                                                                    attestation_type)
    if attestation_pdf:
        return _make_pdf_attestation(attestation_pdf, attestation_type)
    else:
        messages.add_message(request, messages.ERROR, _('error_fetching_attestation'))
        return home(request)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def attestation_administration(request):
    return layout.render(request, 'admin/attestation_administration.html')


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def visualize_student_attestations(request, registration_id):
    student = student_mdl.find_by_registration_id(registration_id)
    json_message = _make_registration_json_message(student.registration_id)
    attestation_statuses_json_dict = student_attestation_status.fetch_json_attestation_statuses(json_message)
    data = _make_attestation_data(attestation_statuses_json_dict, student)
    return layout.render(request, "attestation_home.html", data)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def download_student_attestation(request, global_id, academic_year, attestation_type):
    attestation_pdf = student_attestation.fetch_student_attestation(global_id,
                                                                    academic_year,
                                                                    attestation_type)
    if attestation_pdf:
        return _make_pdf_attestation(attestation_pdf, attestation_type)
    else:
        person = person_mdl.find_by_global_id(global_id)
        student = student_mdl.find_by_person(person)
        messages.add_message(request, messages.ERROR, _('error_fetching_attestation'))
        return visualize_student_attestations(request, student.registration_id)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_student_attestations(request):
    if request.method == "POST":
        form = RegistrationIdForm(request.POST)
        if form.is_valid():
            registration_id = form.cleaned_data['registration_id']
            return visualize_student_attestations(request, registration_id)
    else:
        form = RegistrationIdForm()
    return layout.render(request, "admin/attestation_administration.html", {"form": form})


def _make_registration_json_message(registration_id):
    json_message = None
    if registration_id:
        message = {'registration_id': registration_id}
        json_message = json.dumps(message)
    return json_message


def _make_anac_for_template(year):
    formated_academic_year = None
    if year:
        formated_academic_year = '{} - {}'.format(year, year+1)
    return formated_academic_year


def _make_attestation_data(attestation_statuses_json_dict, student):
    if attestation_statuses_json_dict:
        attestation_statuses = attestation_statuses_json_dict.get('attestationStatuses')
        academic_year = attestation_statuses_json_dict.get('academicYear')
        formated_academic_year = _make_anac_for_template(academic_year)
        attestation_available = attestation_statuses_json_dict.get('available')
    else:
        attestation_statuses = None
        academic_year = None
        formated_academic_year = None
        attestation_available = None

    return {'attestation_statuses': attestation_statuses,
            'academic_year': academic_year,
            'formated_academic_year': formated_academic_year,
            'available': attestation_available,
            'student': student}


def _make_pdf_attestation(attestation_pdf, attestation_type):
    filename = "%s.pdf" % _(attestation_type)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    response.write(attestation_pdf)
    return response