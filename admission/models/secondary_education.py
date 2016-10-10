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
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from reference.enums.education_institution_national_comunity import NATIONAL_COMMUNITY_TYPES


class SecondaryEducationAdmin(admin.ModelAdmin):
    list_display = ('person', 'national')


class SecondaryEducation(models.Model):
    RESULT_TYPE = (('LOW', 'Moins de 65%'),
                   ('MIDDLE', 'entre 65% et 75%'),
                   ('HIGH', 'plus de 75%'))

    INTERNATIONAL_DIPLOMA_TYPE = (('NATIONAL', 'Baccalauréat national (ou diplôme d\'état, ...)'),
                                  ('EUROPEAN', 'Baccalauréat européen (Schola Europea)'),
                                  ('INTERNATIONAL', 'Baccalauréat international(IBO)'))

    EQUIVALENCE_TYPE = (('YES', _('Yes')),
                        ('NO', _('No')),
                        ('DEMANDED', _('Demanded')))

    LOCAL_LANGUAGE_EXAM_RESULT_TYPE = (('SUCCEED', _('succeeded')),
                                       ('FAILED', _('failed')),
                                       ('ENROLLMENT_IN_PROGRESS', _('demanded_result')))

    person = models.OneToOneField('Applicant')
    diploma = models.BooleanField(default=False)
    academic_year = models.IntegerField(blank=True, null=True)
    national = models.NullBooleanField(default=True)
    national_community = models.CharField(max_length=20, choices=NATIONAL_COMMUNITY_TYPES, blank=True, null=True)
    national_institution = models.ForeignKey('reference.EducationInstitution', blank=True, null=True)
    education_type = models.ForeignKey('reference.EducationType', blank=True, null=True)
    dipl_acc_high_educ = models.NullBooleanField(default=False)  # Local qualification diploma to get access to higher
                                                                 #  education studies (DAES)
    path_repetition = models.NullBooleanField(default=False)
    path_reorientation = models.NullBooleanField(default=False)
    result = models.CharField(max_length=20, choices=RESULT_TYPE, blank=True, null=True)
    international_diploma = models.CharField(max_length=20, choices=INTERNATIONAL_DIPLOMA_TYPE, blank=True, null=True)
    international_diploma_country = models.ForeignKey('reference.Country', blank=True, null=True)
    international_diploma_language = models.ForeignKey('reference.Language', blank=True, null=True)
    international_equivalence = models.CharField(max_length=20, choices=EQUIVALENCE_TYPE, blank=True, null=True)


def find_by_person(an_applicant):
    return SecondaryEducation.objects.filter(person=an_applicant).first()
