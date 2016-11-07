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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

import admission.tests.data_for_tests as data_model
from admission.views import accounting
from reference.enums import education_institution_national_comunity
from django.http import HttpRequest


class AccountingTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@localhost', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(self.user)
        self.application = data_model.create_application(self.applicant)

    def test_populate_an_existing_application(self):
        my_request = self.factory.get("", {'study_grant':              'true',
                                           'study_grant_number':       '152',
                                           'deduction_children':       'true',
                                           'scholarship':              'true',
                                           'scholarship_organization': 'Entreprise 1',
                                           'sport_membership':         'true',
                                           'culture_membership':       'true',
                                           'solidarity_membership':    'true',
                                           'bank_account_iban':        'true',
                                           'bank_account_bic':         'true',
                                           'bank_account_name':        'Mister T'}
)

        try:
            accounting.populate_save_application(my_request, self.application.id)
        except Exception:
            self.fail("delete_existing_application_documents raised ExceptionType unexpectedly!")

    def test_populate_an_existing_application_without_offer_year(self):
        request = HttpRequest()
        request.user = self.user

        try:
            accounting.populate_save_application(request, None)
        except Exception:
            self.fail("delete_existing_application_documents raised ExceptionType unexpectedly!")

    def test_populate_application_with_study_grant(self):
        my_request = self.factory.post("", {'study_grant':        'true',
                                            'study_grant_number': '152'})

        application = accounting.populate_save_application(my_request, self.application.id)
        self.assertTrue(application.study_grant_number and application.study_grant)

    def test_populate_application_without_study_grant(self):
        my_request = self.factory.post("", {'study_grant':        'false',
                                            'study_grant_number': '152'})

        application = accounting.populate_save_application(my_request, self.application.id)
        self.assertTrue(application.study_grant is False and application.study_grant_number is None)

    def test_populate_application_with_deduction_children(self):
        my_request = self.factory.post("", {'study_grant':        'false',
                                            'study_grant_number': None,
                                            'deduction_children': 'true'})

        application = accounting.populate_save_application(my_request, self.application.id)
        self.assertTrue(application.deduction_children and application.study_grant is False)

    def test_debts_check_true(self):
        current_academic_year = data_model.create_academic_year_current()
        current_year = current_academic_year.year
        previous_academic_yr = data_model.create_academic_year_by_year(current_year-1)
        education_institution = data_model.create_education_institution()
        data_model.create_curriculum({'applicant':            self.applicant,
                                      'academic_year':        previous_academic_yr.year,
                                      'path_type':            'LOCAL_UNIVERSITY',
                                      'national_education':   education_institution_national_comunity.FRENCH,
                                      'national_institution': education_institution})
        self.assertTrue(accounting.debts_check(self.application))

    def test_debts_check_false(self):
        self.assertFalse(accounting.debts_check(self.application))

        data_model.create_curriculum({'applicant': self.applicant,
                                      'academic_year': None,
                                      'path_type': 'LOCAL_UNIVERSITY',
                                      'national_education':  education_institution_national_comunity.GERMAN,
                                      'national_institution': None})
        self.assertFalse(accounting.debts_check(self.application))

    def test_reduction_possible_true(self):
        self.assertTrue(accounting.reduction_possible(self.application))

    def test_reduction_possible_false(self):
        an_offer_year_reduction_impossible = data_model.create_offer_year_by_acronym('SPO2Z')
        an_application_reduction_impossible = data_model.create_application(self.applicant)
        an_application_reduction_impossible.offer_year = an_offer_year_reduction_impossible
        an_application_reduction_impossible.save()
        self.assertFalse(accounting.reduction_possible(an_application_reduction_impossible))

    def test_third_cycle_true(self):
        an_offer_year_third_cycle = data_model.create_offer_year_by_acronym('SPO2MC')
        an_application_third_cycle = data_model.create_application(self.applicant)
        an_application_third_cycle.offer_year = an_offer_year_third_cycle
        an_application_third_cycle.save()
        self.assertTrue(accounting.third_cycle(an_application_third_cycle))

    def test_third_cycle_false(self):
        an_offer_year_no_third_cycle = data_model.create_offer_year_by_acronym('SPO11BA')
        an_application_no_third_cycle = data_model.create_application(self.applicant)
        an_application_no_third_cycle.offer_year = an_offer_year_no_third_cycle
        an_application_no_third_cycle.save()
        self.assertFalse(accounting.third_cycle(an_application_no_third_cycle))

