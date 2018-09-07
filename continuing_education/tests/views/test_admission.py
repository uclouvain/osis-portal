##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime
import factory

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from continuing_education.forms.admission import AdmissionForm
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.forms.test_admission_form import convert_dates, convert_countries, convert_offer, \
    convert_faculty


class ViewStudentAdmissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        self.client.force_login(self.user)
        self.admission = AdmissionFactory()

    def test_admission_detail(self):
        url = reverse('admission_detail', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admission_detail.html')

    def test_admission_detail_not_found(self):
        response = self.client.get(reverse('admission_detail', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_admission_new(self):
        url = reverse('admission_new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_admission_new_save(self):
        admission = AdmissionFactory()
        admission_dict = admission.__dict__
        convert_dates(admission_dict)
        response = self.client.post(reverse('admission_new'), data=admission_dict)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('continuing_education'))

    def test_admission_save_with_error(self):
        admission = AdmissionFactory()
        admission_dict = admission.__dict__
        convert_dates(admission_dict)
        admission_dict["birth_date"] = "no valid date"
        response = self.client.post(reverse('admission_new'), data=admission_dict)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_admission_edit_not_found(self):
        response = self.client.get(reverse('admission_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_edit_get_admission_found(self):
        url = reverse('admission_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_edit_post_admission_found(self):
        admission = AdmissionFactory().__dict__
        convert_dates(admission)
        convert_countries(admission)
        convert_offer(admission)
        convert_faculty(admission)
        url = reverse('admission_edit', args=[self.admission.id])
        form = AdmissionForm(admission)
        form.is_valid()
        response = self.client.post(url, data=form.cleaned_data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]))
        self.admission.refresh_from_db()

        # verifying that fields are correctly updated
        for key in form.cleaned_data.keys():
            field_value = self.admission.__getattribute__(key)
            if type(field_value) is datetime.date:
                field_value = field_value.strftime('%Y-%m-%d')
            self.assertEqual(field_value, admission[key])

