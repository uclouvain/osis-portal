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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################


def change_contact_address(contact_address_required):
    """
    Change the value of the applicant contact address.
    If the contact address is ot required, the function remove all information about the applicant contact adress.
    :param contact_address_required: True if the contact address and the residence address of the applicant are different.
                                     False if the applicant has only one address.
    """
    # To implement
    if not contact_address_required:
        # remove all info about the contact address
        # To implement
        pass


def change_already_registered_in_ucl(already_registered):
    """
    Change the value of the field 'registration_id' and 'last_academic_year' of the Applicant.
    :param already_registered: True if the applicant was already registered in the UCL university in the past.
    """


