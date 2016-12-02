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
from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import component_type
from django.conf import settings

MAIL_TO = 'mailto:'
STUDENT_LIST_EMAIL_END = '@listes-student.uclouvain.be'

ADE_URL_PART1 = '/direct/index.jsp?displayConfName=WEB&showTree=false&showOptions=false&weeks=0&login=enseignant&password=prof&projectId='
ADE_URL_PART2 = '&code='
ADE_PROJET_NUMBER = '21'


def get_person(a_user):
    return mdl_base.person.find_by_user(a_user)


def get_title_uppercase(learning_unit_year):
    if learning_unit_year and learning_unit_year.title:
        return learning_unit_year.title.upper()
    return ''


def get_attribution_allocation_charge(a_tutor, a_learning_unit_year, a_component_type):
    attribution_list = mdl_attribution.attribution.search(a_tutor, a_learning_unit_year)
    tot_allocation_charge = 0
    for an_attribution in attribution_list:
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year,
                                                                              a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
            for attribution_charge in attribution_charges:
                if attribution_charge:
                    tot_allocation_charge += attribution_charge.allocation_charge

    return tot_allocation_charge

def sum_learning_unit_year_duration(a_learning_unit_year):
    tot_duration = 0
    for learning_unit_component in mdl_base.learning_unit_component.search(a_learning_unit_year):
        if learning_unit_component.duration:
            tot_duration += learning_unit_component.duration
    return tot_duration

def sum_learning_unit_year_allocation_charge(a_tutor, a_learning_unit_year):
    return get_attribution_allocation_charge(a_tutor, a_learning_unit_year, None)


def calculate_format_percentage_allocation_charge(a_tutor, a_learning_unit_year):
    a_learning_unit_year_duration = sum_learning_unit_year_duration(a_learning_unit_year)
    if a_learning_unit_year_duration > 0:
        percentage = sum_learning_unit_year_allocation_charge(a_tutor, a_learning_unit_year) * 100 / a_learning_unit_year_duration
        return "%0.2f" % (percentage,)
    return None

def get_email_students(an_acronym):
    if an_acronym and len(an_acronym.strip()) > 0:
        return "{0}{1}{2}".format(MAIL_TO, an_acronym.lower(),STUDENT_LIST_EMAIL_END)
    return None

def get_schedule_url(an_acronym):
    if an_acronym and len(an_acronym.strip()) > 0:
        return "{0}{1}{2}{3}{4}".format(settings.ADE_MAIN_URL,
                                        ADE_URL_PART1,
                                        ADE_PROJET_NUMBER,
                                        ADE_URL_PART2,
                                        an_acronym.lower())
    return None

class TeachingLoadAttributionRepresentation:

    def __init__(self):
        self.acronym = ""
        self.title = ""
        self.lecturing_allocation_charge = ""
        self.practice_allocation_charge = ""
        self.percentage_allocation_charge = ""
        self.url_schedule = ""
        self.url_students_list_email = ""
        self.function=""
