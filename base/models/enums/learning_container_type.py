##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import ugettext_lazy as _

COURSE = "COURSE"
INTERNSHIP = "INTERNSHIP"
DISSERTATION = "DISSERTATION"
OTHER_COLLECTIVE = "OTHER_COLLECTIVE"
OTHER_INDIVIDUAL = "OTHER_INDIVIDUAL"
MASTER_THESIS = "MASTER_THESIS"
EXTERNAL = "EXTERNAL"

CONTAINER_TYPE = (
    (COURSE, _("Course")),
    (INTERNSHIP, _("Internship")),
    (DISSERTATION, _("Dissertation")),
    (OTHER_COLLECTIVE, _("Other collective")),
    (OTHER_INDIVIDUAL, _("Other individual")),
    (MASTER_THESIS, _("Thesis")),
    (EXTERNAL, _("External")),
)

IN_CHARGE_TYPES = [COURSE, INTERNSHIP, DISSERTATION]
