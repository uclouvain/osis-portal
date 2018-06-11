##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from django.template import Context, Template
from django.test import override_settings

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class UrlCatalogTagTests(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2015)
        self.learning_container_year = LearningContainerYearFactory(acronym='LBIR1200',
                                                                    academic_year=self.academic_year)
        self.learning_unit_year = LearningUnitYearFactory(acronym='LBIR1200',
                                                          academic_year=self.academic_year,
                                                          learning_container_year=self.learning_container_year)

    @override_settings(ATTRIBUTION_CONFIG={'CATALOG_URL': 'http://www.uclouvain.be/cours-{0}-{1}.html'})
    def test_url_catalogs(self):
        url_expected = "http://www.uclouvain.be/cours-2015-lbir1200.html"
        out = Template(
            "{% load urls_catalog %}"
            "{{ learning_container_year.id | get_url_learning_unit_year }}"
        ).render(Context({
            'learning_container_year': self.learning_container_year
        }))
        self.assertEqual(out, url_expected)