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
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase


def test_paths(routes_to_test):
    for route in routes_to_test:
        path = route["url_path"]
        pattern = route["pattern_name"]
        params = route.get('args')
        kwparams = route.get("kwargs")

        if kwparams:
            yield reverse(pattern, args=params, kwargs=kwparams), path
        else:
            yield reverse(pattern, args=params), path

        yield resolve(path).url_name, pattern


class UrlsTestCase(TestCase):
    def test_url(self):
        routes_to_test = [
            dict(
                url_path='/continuing_education/',
                pattern_name='continuing_education',
            ),
            dict(
                url_path="/continuing_education/admission_new/",
                pattern_name='admission_new',
            ),
            dict(
                url_path="/continuing_education/admission_edit/1",
                pattern_name='admission_edit',
                kwargs={'admission_id': 1}
            ),
            dict(
                url_path="/continuing_education/admission_detail/1",
                pattern_name='admission_detail',
                kwargs={'admission_id': 1}
            ),
            dict(
                url_path="/continuing_education/registration_edit/1",
                pattern_name='registration_edit',
                kwargs={'admission_id': 1}
            ),
            dict(
                url_path="/continuing_education/registration_detail/1",
                pattern_name='registration_detail',
                kwargs={'admission_id': 1}
            ),
        ]

        for url_name, pattern in test_paths(routes_to_test):
            self.assertEqual(url_name, pattern)
