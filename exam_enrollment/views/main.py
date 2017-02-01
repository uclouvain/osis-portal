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
from django.contrib.auth.decorators import login_required
from base.views import layout
from base.models import student, offer_enrollment, academic_year, offer_year


@login_required
def choose_offer(request):
    stud = student.find_by_user(request.user)
    student_programs = None
    if stud:
        student_programs = [enrol.offer_year for enrol in list(offer_enrollment.find_by_student(stud))]
    return layout.render(request, 'offer_choice.html', {'programs': student_programs,
                                                        'student': stud})


def _fetch_exam_enrollment_form(registration_id):
    import json
    import os
    script_dir = os.path.dirname(__file__)
    rel_path = "exam_enrollment_form_example.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    json_data = open(abs_file_path)
    data1 = json.load(json_data) # deserialises it
    # data2 = json.dumps(json_data) # json formatted string
    return data1


@login_required
def exam_enrollment_form(request, offer_year_id):
    stud = student.find_by_user(request.user)
    data = None
    if stud:
        data = _fetch_exam_enrollment_form(stud.registration_id)
    return layout.render(request, 'exam_enrollment_form.html', {'exam_enrollments': data.get('exam_enrollments'),
                                                                'student': stud,
                                                                'current_number_session': data.get('current_number_session'),
                                                                'academic_year': academic_year.current_academic_year(),
                                                                'program': offer_year.find_by_id(offer_year_id),
                                                                'legend': data.get('legend')})
