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
from django.utils.translation import gettext as _

APD_NUMBER = 15
MIN_APDS = 5
MAX_APDS = 8

APDS = ['apd_{}'.format(index) for index in range(1, APD_NUMBER + 1)]

COMMENTS_FIELDS = [
    ('intermediary_evaluation', _("Intermediary evaluation (optional)")),
    ('good_perf_ex', _("Good performance examples")),
    ('impr_areas', _("Improvement areas")),
    ('suggestions', _("Suggested learning methods"))
]
DEFAULT_PERIODS = 'all'
AVAILABLE_GRADES = ['A', 'B', 'C', 'D']

APDS_DESCRIPTIONS = {
    "1": _("Take a history (anamnesis)"),
    "2": _("Conduct clinical examination"),
    "3": _("Appreciate medical emergency"),
    "4": _("Establish a diagnosis"),
    "5": _("Complement patient record"),
    "6": _("Oral presentation of a clinical situation"),
    "7": _("Select diagnostic tests"),
    "8": _("Write medical prescriptions"),
    "9": _("Perform technical procedures"),
    "10": _("Formulate clinical questions"),
    "11": _("Communicate (broad sense)"),
    "12": _("Work as a team"),
    "13": _("Make/receive transmission report"),
    "14": _("Obtain informed consent"),
    "15": _("Contribute to quality of care and patient safety"),
}
