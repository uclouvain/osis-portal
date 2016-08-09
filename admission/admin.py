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
from django.contrib import admin

from admission.models import *

admin.site.register(academic_year.AcademicYear,
                    academic_year.AcademicYearAdmin)

admin.site.register(admission_exam_type.AdmissionExamType,
                    admission_exam_type.AdmissionExamTypeAdmin)

admin.site.register(answer.Answer,
                    answer.AnswerAdmin)

admin.site.register(applicant.Applicant,
                    applicant.ApplicantAdmin)

admin.site.register(applicant_assimilation_criteria.ApplicantAssimilationCriteria,
                    applicant_assimilation_criteria.ApplicantAssimilationCriteriaAdmin)

admin.site.register(application.Application,
                    application.ApplicationAdmin)

admin.site.register(application_assimilation_criteria.ApplicationAssimilationCriteria,
                    application_assimilation_criteria.ApplicationAssimilationCriteriaAdmin)

admin.site.register(curriculum.Curriculum,
                    curriculum.CurriculumAdmin)

admin.site.register(form.Form,
                    form.FormAdmin)

admin.site.register(offer_year.OfferYear,
                    offer_year.OfferYearAdmin)

admin.site.register(option.Option,
                    option.OptionAdmin)

admin.site.register(person_address.PersonAddress,
                    person_address.PersonAddressAdmin)

admin.site.register(properties.Properties,
                    properties.PropertiesAdmin)

admin.site.register(question.Question,
                    question.QuestionAdmin)

admin.site.register(secondary_education.SecondaryEducation,
                    secondary_education.SecondaryEducationAdmin)

admin.site.register(secondary_education_exam.SecondaryEducationExam,
                    secondary_education_exam.SecondaryEducationExamAdmin)
