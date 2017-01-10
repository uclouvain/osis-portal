##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from attribution import models as mdl_attribution


def create_application_charge(data):
    application_charge = mdl_attribution.application_charge.ApplicationCharge()
    if 'tutor_application' in data:
        application_charge.tutor_application = data['tutor_application']
    if 'learning_unit_component' in data:
        application_charge.learning_unit_component = data['learning_unit_component']
    if 'allocation_charge' in data:
        application_charge.allocation_charge = data['allocation_charge']
    application_charge.save()
    return application_charge
