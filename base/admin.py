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
from base.models import *
from django.contrib import admin

admin.site.register(academic_calendar.AcademicCalendar)

admin.site.register(academic_year.AcademicYear,
                    academic_year.AcademicYearAdmin)

admin.site.register(campus.Campus,
                    campus.CampusAdmin)

admin.site.register(learning_unit.LearningUnit,
                    learning_unit.LearningUnitAdmin)

admin.site.register(learning_unit_year.LearningUnitYear,
                    learning_unit_year.LearningUnitYearAdmin)

admin.site.register(learning_unit_component.LearningUnitComponent,
                    learning_unit_component.LearningUnitComponentAdmin)

admin.site.register(learning_unit_enrollment.LearningUnitEnrollment,
                    learning_unit_enrollment.LearningUnitEnrollmentAdmin)

admin.site.register(offer.Offer,
                    offer.OfferAdmin)

admin.site.register(offer_enrollment.OfferEnrollment,
                    offer_enrollment.OfferEnrollmentAdmin)

admin.site.register(external_offer.ExternalOffer,
                    external_offer.ExternalOfferAdmin)

admin.site.register(offer_year.OfferYear,
                    offer_year.OfferYearAdmin)

admin.site.register(offer_year_domain.OfferYearDomain,
                    offer_year_domain.OfferYearDomainAdmin)

admin.site.register(organization.Organization,
                    organization.OrganizationAdmin)

admin.site.register(person.Person,
                    person.PersonAdmin)

admin.site.register(student.Student,
                    student.StudentAdmin)

admin.site.register(tutor.Tutor,
                    tutor.TutorAdmin)
