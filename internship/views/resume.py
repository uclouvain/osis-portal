# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from base.views import layout
from internship.models import internship_student_information as mdl_student_information
from internship.models import internship_student_affectation_stat as mdl_student_affectation
from internship.models import organization_address as mdl_organization_address
from internship.models import internship_choice as mdl_internship_choice
from internship.forms import form_internship_student_information
from base.models import student as mdl_student


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_student_resume(request):
    student = mdl_student.find_by_user(request.user)
    student_information = mdl_student_information.find_by_user(request.user)
    student_affectations = mdl_student_affectation.search(student=student)
    student_affectations_with_address = \
        [(affectation, mdl_organization_address.get_by_organization(affectation.organization)) for affectation in
         student_affectations]
    student_choices = mdl_internship_choice.search(student=student).order_by('internship_choice', 'choice')
    return layout.render(request, "student_resume.html", {"student": student,
                                                          "student_information": student_information,
                                                          "student_affectations_with_address":
                                                              student_affectations_with_address,
                                                          "student_choices": student_choices,
                                                          "internships": range(1, 7)})


@login_required
@permission_required('base.is_student', raise_exception=True)
def edit_student_information(request):
    form = form_internship_student_information.InternshipStudentInformationForm()
    return layout.render(request, "student_edit_information.html", {"form": form})