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
from django.contrib.auth.models import User
from admission import models as mdl
from base import models as mdl_base
from reference import models as mdl_reference
from osis_common import models as mdl_osis_common
from reference.enums import assimilation_criteria as assimilation_criteria_enum


def create_user():
    a_user = User.objects.create_user('testo', password='testopw')
    a_user.save()
    return a_user


def create_applicant_by_user(user):
    an_applicant = mdl.applicant.Applicant(user=user)
    an_applicant.save()
    return an_applicant


def create_applicant():
    an_applicant = mdl.applicant.Applicant(user=create_user())
    an_applicant.save()
    return an_applicant


def create_secondary_education():
    a_secondary_education = mdl.secondary_education.SecondaryEducation(person=create_applicant())
    a_secondary_education.save()
    return a_secondary_education


def create_secondary_education_exam(secondary_education, a_type):
        an_admission_exam = mdl.secondary_education_exam.SecondaryEducationExam(
            secondary_education=secondary_education,
            type=a_type)
        an_admission_exam.save()
        return an_admission_exam


def create_secondary_education_with_exams():
    secondary_education = create_secondary_education()
    create_secondary_education_exam(secondary_education, 'ADMISSION')
    create_secondary_education_exam(secondary_education, 'PROFESSIONAL')
    create_secondary_education_exam(secondary_education, 'LANGUAGE')
    return secondary_education


def create_application(an_applicant):
    an_application = mdl.application.Application(applicant=an_applicant,
                                                 offer_year=create_offer_year(),
                                                 application_type='ADMISSION')
    an_application.save()
    return an_application


def create_offer_year():
    an_offer_year = mdl_base.offer_year.OfferYear()
    an_offer_year.academic_year = create_academic_year()
    an_offer_year.acronym = "VETE11BA"
    an_offer_year.title = "Première année de bachelier en médecine vétérinaire"
    an_offer_year.save()
    return an_offer_year


def create_academic_year():
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = 2016
    an_academic_year.save()
    return an_academic_year


def create_grade_type(a_name, an_institutional_grade_type):
    a_grade_type = mdl_reference.grade_type.GradeType(name=a_name, institutional_grade_type=an_institutional_grade_type)
    a_grade_type.save()
    return a_grade_type


def create_document_file(update_by, description=None):
    a_document_file = mdl_osis_common.document_file.DocumentFile(description=description)
    a_document_file.file_name = "test.jpg"
    a_document_file.storage_duration = 1
    a_document_file.update_by = update_by
    a_document_file.save()
    return a_document_file


def create_application_document_file(an_application, update_by, description=None):
    a_document_file = create_document_file(update_by, description)
    an_application_document_file = mdl.application_document_file.ApplicationDocumentFile()
    an_application_document_file.application = an_application
    an_application_document_file.document_file = a_document_file
    an_application_document_file.save()
    return an_application_document_file


def create_profession(a_name, an_adhoc):
    return mdl.profession.Profession(name=a_name, adhoc=an_adhoc)


def create_applicant_assimilation_criteria(an_applicant):
    return mdl.applicant_assimilation_criteria.ApplicantAssimilationCriteria(
        applicant=an_applicant,
        criteria=assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES[0][0],
        additional_criteria=None,
        selected=False)
