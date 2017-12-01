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

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook


STATUS_COL_WIDTH = 10
NOTE_COL_WIDTH = 10


def students_list_build_by_learning_unit(student_list, a_learning_unit_year):
    xls = _make_xls_list(student_list)
    filename = 'student_list_{}_{}.xlsx'.format(a_learning_unit_year.acronym, a_learning_unit_year.academic_year.year)
    response = HttpResponse(xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
    return response


def _make_xls_list(student_list):
    workbook = Workbook()
    worksheet1 = workbook.active
    worksheet1.title = "Students"
    worksheet1.append([str(_('program')),
                       str(_('activity')),
                       str(_('email')),
                       str(_('student')),
                       str(_('registration_id')),
                       str(_('status')),
                       str(_('january')),
                       str(_('status')),
                       str(_('june')),
                       str(_('status')),
                       str(_('september'))
                       ])

    for student in student_list:
        worksheet1.append([student.get('program'),
                           student.get('acronym'),
                           student.get('email'),
                           student.get('name'),
                           student.get('registration_id'),
                           student.get('january_status'),
                           student.get('january_note'),
                           student.get('june_status'),
                           student.get('june_note'),
                           student.get('september_status'),
                           student.get('september_note')
                           ])

    _columns_resizing(worksheet1)

    return save_virtual_workbook(workbook)


def _columns_resizing(ws):
    """
    Definition of the columns sizes
    """
    col_program = ws.column_dimensions['A']
    col_program.width = 18
    col_acronym = ws.column_dimensions['B']
    col_acronym.width = 15
    col_mail = ws.column_dimensions['C']
    col_mail.width = 40
    col_name = ws.column_dimensions['D']
    col_name.width = 30
    col_registration_id = ws.column_dimensions['E']
    col_registration_id.width = 15
    col_january_status = ws.column_dimensions['F']
    col_january_status.width = STATUS_COL_WIDTH
    col_january_note = ws.column_dimensions['G']
    col_january_note.width = NOTE_COL_WIDTH
    col_june_status = ws.column_dimensions['H']
    col_june_status.width = STATUS_COL_WIDTH
    col_june_note = ws.column_dimensions['I']
    col_june_note.width = NOTE_COL_WIDTH
    col_september_status = ws.column_dimensions['J']
    col_september_status.width = STATUS_COL_WIDTH
    col_september_note = ws.column_dimensions['K']
    col_september_note.width = NOTE_COL_WIDTH
