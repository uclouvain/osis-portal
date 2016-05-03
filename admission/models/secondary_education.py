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
from admission.models import form


class SecondaryEducationAdmin(admin.ModelAdmin):
    list_display = ('person', 'national')
    fieldsets = ((None, {'fields': ('person', 'national')}),)


class SecondaryEducation(models.Model):
    NATIONAL_COMMUNITY_TYPES = (
        ('FRENCH', 'Communauté française de Belgique'),
        ('GERMAN', 'Communauté germanophone'),
        ('DUTCH', 'Communauté flamande'),
        )

    RESULT_TYPE = (('LOW', 'Moins de 65%'),
                   ('MIDDLE', 'entre 65% et 75%'),
                   ('HIGH', 'plus de 75%'))

    INTERNATIONAL_DIPLOMA_TYPE =(('NATIONAL', 'Baccalauréat national (ou diplôme d\'état, ...)'),
                                 ('EUROPEAN', 'Baccalauréat européen (Schola Europea)'),
                                 ('INTERNATIONAL', 'Baccalauréat international(IBO)'))

    EQUIVALENCE_TYPE =(('YES', _('Yes')),
                       ('NO', _('No')),
                       ('DEMANDED', _('Demanded')))

    person = models.OneToOneField('Person')
    secondary_education_diploma = models.BooleanField(default=False)
    academic_year = models.ForeignKey('AcademicYear', blank=True, null=True)
    national = models.NullBooleanField(default=True)
    national_community = models.CharField(max_length=20, choices=NATIONAL_COMMUNITY_TYPES, blank=True, null=True)
    national_institution = models.ForeignKey('reference.EducationInstitution', blank=True, null=True)
    education_type = models.ForeignKey('reference.EducationType', blank=True, null=True)
    daes = models.NullBooleanField(default=False)
    path_repetition = models.NullBooleanField(default=False)
    path_reorientation = models.NullBooleanField(default=False)
    result = models.CharField(max_length=20, choices=RESULT_TYPE,blank=True, null=True)
    international_diploma = models.CharField(max_length=20, choices=INTERNATIONAL_DIPLOMA_TYPE,blank=True, null=True)
    international_diploma_country = models.ForeignKey('reference.Country',blank=True, null=True)
    international_diploma_language = models.ForeignKey('reference.Language',blank=True, null=True)
    international_equivalence = models.CharField(max_length=20, choices=EQUIVALENCE_TYPE,blank=True, null=True)
    admission_exam = models.NullBooleanField(default=False)
    admission_exam_date = models.DateField(blank=True, null=True)
    admission_exam_institution = models.CharField(max_length=100,blank=True, null=True)
    admission_exam_type = models.ForeignKey('reference.AdmissionExamType',blank=True, null=True)
    admission_exam_result = models.CharField(max_length=20, choices=RESULT_TYPE, blank=True, null=True)
    professional_exam = models.NullBooleanField(default=False)
    professional_exam_date = models.DateField(blank=True, null=True)
    professional_exam_institution = models.CharField(max_length=100,blank=True, null=True)
    professional_exam_result = models.CharField(max_length=20, choices=RESULT_TYPE,blank=True, null=True)
    local_language_exam = models.NullBooleanField(default=False)
    local_language_exam_date = models.DateField(blank=True, null=True)
    local_language_exam_institution = models.CharField(max_length=100,blank=True, null=True)
    local_language_exam_result = models.CharField(max_length=25, choices=RESULT_TYPE, blank=True, null=True)


    @property
    def path(self):
        if self.academic_year.year < 1994:
            return True
        return False

    @property
    def daes_possible(self):
        if self.national_community == 'FRENCH' and self.academic_year.year < 1994:
            return True
        if self.national_community == 'DUTCH' and self.academic_year.year < 1992:
            return True
        return False


def find_by_person(a_person):
    return SecondaryEducation.objects.filter(person=a_person).first()