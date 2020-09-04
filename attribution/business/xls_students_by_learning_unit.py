##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles.borders import Border, Side, BORDER_MEDIUM
from openpyxl.styles import Color
from openpyxl.styles import Style
from attribution.business.student_specific_profile import get_type_peps

COLUMN_REGISTRATION_ID_NO = 5
STATUS_COL_WIDTH = 10
NOTE_COL_WIDTH = 10
OPENPYXL_STRING_FORMAT = '@'
BORDER_LEFT = Border(
        left=Side(border_style=BORDER_MEDIUM,
                  color=Color('FF000000'),
                  ),
    )
FIRST_COL_PEPS = 'L'


def get_xls(student_list, a_learning_unit_year):
    xls = _make_xls_list(student_list)
    filename = '{}_{}_{}.xlsx'.format(_('student_list'),
                                      a_learning_unit_year.acronym,
                                      a_learning_unit_year.academic_year.year)
    response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
    return response


def _make_xls_list(student_list):
    workbook = Workbook()
    worksheet1 = workbook.active
    worksheet1.title = _("Students")
    columns_header = [
        _('Program'),
        _('Learning unit'),
        _('Email'),
        _('Student'),
        _('Registration id'),
        _('State'),
        _('January'),
        _('State'),
        _('June'),
        _('State'),
        _('September'),
        _('Type of specific profile'),
        _('Extra time (33% generally)'),
        _('Large print'),
        _('Specific room of examination'),
        _('Other educational facilities'),
        _('Educational tutor'),
    ]
    worksheet1.append(col for col in columns_header)
    for student in student_list:
        line_content = [
            student.get('program'),
            student.get('acronym'), student.get('email'),
            student.get('name'),
            student.get('registration_id'),
            student.get('january_status'),
            student.get('january_note'),
            student.get('june_status'),
            student.get('june_note'),
            student.get('september_status'),
            student.get('september_note'),
        ]

        student_specific_profile = student.get('student_specific_profile')

        if student_specific_profile:
            line_content.extend([
                get_type_peps(student_specific_profile),
                str(_('Yes')) if student_specific_profile.arrangement_additional_time else '-',
                str(_('Yes')) if student_specific_profile.arrangement_appropriate_copy else '-',
                str(_('Yes')) if student_specific_profile.arrangement_specific_locale else '-',
                str(_('Yes')) if student_specific_profile.arrangement_other else '-',
                str(student_specific_profile.guide) if student_specific_profile.guide else '-',
                ])
        else:
            line_content.extend(["-", "-", "-", "-", "-", "-"])
        worksheet1.append(line_content)

    _columns_resizing(worksheet1)
    _columns_registration_id_to_text(worksheet1)
    _set_peps_border(worksheet1, len(student_list)+1)
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
    col_type_of_specific_profile = ws.column_dimensions['L']
    col_type_of_specific_profile.width = 20
    col_extra_time = ws.column_dimensions['M']
    col_extra_time.width = 25
    col_large_print = ws.column_dimensions['N']
    col_large_print.width = 15
    col_specific_room_of_examination = ws.column_dimensions['O']
    col_specific_room_of_examination.width = 25
    col_other_educational_facilities = ws.column_dimensions['P']
    col_other_educational_facilities.width = 25
    col_educational_tutor = ws.column_dimensions['Q']
    col_educational_tutor.width = 30


def _columns_registration_id_to_text(ws):
    """
    Necessary, otherwise the registration_id is considered as a number and set with a quote while looking at the
    input line
    """
    for row in ws.iter_rows():
        for cell in row:
            if cell.col_idx == COLUMN_REGISTRATION_ID_NO:
                cell.number_format = OPENPYXL_STRING_FORMAT


def _set_peps_border(ws, last_row_number):
    """
    Set border at the left of the first peps column
    """
    for cpt in range(1, last_row_number + 1):
        cell = ws["{}{}".format(FIRST_COL_PEPS, cpt)]
        _update_border_for_first_peps_column(cell)


def _update_border_for_first_peps_column(cell):
    c = cell.style if cell.has_style else Style()

    c.border = BORDER_LEFT
    cell.style = c
