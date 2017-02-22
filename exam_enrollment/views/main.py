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
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from base.views import layout
from base.models import student, offer_enrollment, academic_year, offer_year
from frontoffice.queue import queue_listener
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import response
from exam_enrollment.forms.exam_enrollment_form import ExamEnrollmentForm
from django.forms import formset_factory
from osis_common.queue import queue_sender
from django.conf import settings


@login_required
@permission_required('base.is_student', raise_exception=True)
def choose_offer(request):
    stud = student.find_by_user(request.user)
    student_programs = None
    if stud:
        student_programs = [enrol.offer_year for enrol in list(offer_enrollment.find_by_student(stud))]
    return layout.render(request, 'offer_choice.html', {'programs': student_programs,
                                                        'student': stud})


@login_required
@permission_required('base.is_student', raise_exception=True)
def exam_enrollment_form(request, offer_year_id):
    stud = student.find_by_user(request.user)
    off_year = offer_year.find_by_id(offer_year_id)
    # ExamEnrollmentFormSet = formset_factory(ExamEnrollmentForm, extra=0)
    if request.method == 'POST':
        # formset = ExamEnrollmentFormSet(request.POST, request.FILES)
        # if formset.is_valid():
        #     for f in formset:
        #         print(str(f.cleaned_data))
        #         print('ici')
        #     pass

        data_to_submit = {
            'registration_id': stud.registration_id,
            'offer_year_acronym': off_year.acronym,
            'year': off_year.academic_year.year,
            'exam_enrollments': _build_enrollments_by_learning_unit(request)
        }
        queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'),
                                  data_to_submit)
        messages.add_message(request, messages.SUCCESS, _('exam_enrollment_form_submitted'))
        return response.HttpResponseRedirect(reverse('dashboard_home'))
    else:
        data = None
        if stud:
            data = _fetch_json(stud.registration_id, off_year.acronym, off_year.academic_year.year)
            if not data:
                messages.add_message(request, messages.WARNING, _('outside_exam_enrollment_period'))
                return response.HttpResponseRedirect(reverse('dashboard_home'))
            # test = ExamEnrollmentForm()
            # formset = ExamEnrollmentFormSet(initial=data.get('exam_enrollments'))
            # test = ExamEnrollmentFormSet(**data)
            return layout.render(request, 'exam_enrollment_form.html', {'exam_enrollments': data.get('exam_enrollments'),
                                                                        'student': stud,
                                                                        'current_number_session': data.get('current_number_session'),
                                                                        'academic_year': academic_year.current_academic_year(),
                                                                        'program': offer_year.find_by_id(offer_year_id)})


def _build_enrollments_by_learning_unit(request):
    current_number_session = request.POST['current_number_session']
    # "etat_to_inscr_current_session"
    enrollments_by_learn_unit = []
    is_enrolled_by_acronym = [{"acronym": _extract_acronym(html_tag_id), "is_enrolled": True if value == "on" else False} for html_tag_id, value in request.POST.items()
                              if "chckbox_exam_enrol_sess{}_".format(current_number_session) in html_tag_id]
    etat_to_inscr_by_acronym = {_extract_acronym(html_tag_id): etat_to_inscr for html_tag_id, etat_to_inscr in request.POST.items()
                                if "etat_to_inscr_current_session_" in html_tag_id}
    # append_etat_to_inscr_value = lambda x: x.update({"etat_to_inscr": etat_to_inscr_by_acronym[x.get('acronym')]})
    for is_enrol_by_acronym in is_enrolled_by_acronym:
        acronym = is_enrol_by_acronym.get('acronym')
        is_enrol_by_acronym['etat_to_inscr'] = etat_to_inscr_by_acronym[acronym]
        enrollments_by_learn_unit.append(is_enrol_by_acronym)
    return enrollments_by_learn_unit
    # liste = [_append_etat_to_inscr_item(is_enrol_by_acronym, etat_to_inscr_by_acronym) for is_enrol_by_acronym in is_enrolled_by_acronym]
    # return liste

    # for key, value in request.POST.items():
    #     enrol_by_learn_unit = {}
    #     if "chckbox_exam_enrol_sess{}_".format(current_number_session) in key:
    #         enrol_by_learn_unit["acronym"] = key.split("_")[-1]
    #         enrol_by_learn_unit["is_enrolled"] = value
    #
    # return [{"acronym": key.split("_")[-1], "is_enrolled": value} for key, value in request.POST.items()
    #         if "chckbox_exam_enrol_sess{}_".format(current_number_session) in key]


def _append_etat_to_inscr_item(a_dict, etat_to_inscr_by_acronym):
    a_dict['etat_to_inscr'] = etat_to_inscr_by_acronym(a_dict.get('acronym'))
    return a_dict

def _extract_acronym(html_tag_id):
    return html_tag_id.split("_")[-1]


def _extract(big_dict, keys_to_extract):
    return {k: big_dict[k] for k in big_dict.keys() & keys_to_extract}


def _fetch_json(registration_id, offer_year_acronym, year):
    # return load_json_file("exam_enrollment/tests/ressources/exam_enrollment_form_example.json")
    exam_enrol_client = queue_listener.ExamEnrollmentClient()
    message = _generate_message(registration_id, offer_year_acronym, year)
    json_data = exam_enrol_client.call(message)
    if json_data:
        json_data = json_data.decode("utf-8")
        return json.loads(json_data)
    return json_data

def load_json_file(path):
    json_data = open(path)
    data1 = json.load(json_data) # deserialises it
    return data1


def _generate_message(registration_id, offer_year_acronym, year):
    message = {
        'registration_id': registration_id,
        'offer_year_acronym': offer_year_acronym,
        'year': year,
    }
    return json.dumps(message)
