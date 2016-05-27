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
from django import template
from admission import models as mdl
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def message_error(a, **kwargs):
    if a is None or len(a) == 0:
        return ''

    year = kwargs['year']
    elt_name = kwargs['param']
    key = '%s_%s' % (elt_name, year)

    ch = a.get(str(key))
    if ch:
        return mark_safe('<br>%s<br>' % ch)
    else:
        return ''


@register.assignment_tag
def pnl_national_education__message_error(a, **kwargs):

    if a is None or len(a) == 0:
        return False
    keys = ['path_type', 'national_education', 'national_institution_french', 'national_institution_dutch', 'domain',
            'subdomain', 'grade_type', 'diploma', 'diploma_title', 'result_national', 'credits_enrolled',
            'credits_obtained', 'high_non_university_name']
    year = kwargs['year']
    for elt_name in keys:
        key = '%s_%s' % (elt_name, year)
        for k, v in a.items():
            if k.startswith(key):
                print('erreur national', key)
                return True
    return False


@register.assignment_tag
def pnl_foreign_education_message_error(a, **kwargs):
    if a is None or len(a) == 0:
        return False
    keys = ['path_type', 'foreign_institution_country', 'foreign_institution', 'foreign_institution_city', 'domain_foreign',
            'subdomain_foreign', 'grade_type_foreign', 'diploma_foreign']
    year = kwargs['year']
    for elt_name in keys:
        key = '%s_%s' % (elt_name, year)
        for k, v in a.items():
            if k.startswith(key):
                print('erreur foreign : ', key)
                return True
    return False


@register.assignment_tag
def pnl_other_message_error(a, **kwargs):
    print('pnl_other_message_error')

    if a is None or len(a) == 0:
        return False
    keys = ['activity_type', 'activity', 'activity_place']
    year = kwargs['year']
    for elt_name in keys:
        key = '%s_%s' % (elt_name, year)
        for k, v in a.items():
            if k.startswith(key):
                print('erreur Other', key)
                return True
    return False
