##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from types import SimpleNamespace

from django.test import SimpleTestCase

from base.utils.api_utils import api_paginated_response, gather_all_api_paginated_results


class SDKUtilsTestCase(SimpleTestCase):

    def test_decorator_should_return_an_api_paginated_response(self):
        def get_api_response(*args, **kwargs):
            attrs = {'results': [], 'count': 0, 'extra': 'extra'}
            return SimpleNamespace(attribute_map=attrs, **attrs)

        paginated_response = api_paginated_response(get_api_response)()
        self.assertEqual(paginated_response.results, [])
        self.assertEqual(paginated_response.count, 0)
        self.assertEqual(paginated_response.get_extra('extra'), 'extra')

    def test_decorator_should_call_api_multiple_times_and_return_gathered_paginated_results(self):
        def get_api_response(*args, **kwargs):
            attrs = {'results': [SimpleNamespace() for _ in range(5)], 'count': 10}
            get_api_response.counter += 1
            return SimpleNamespace(attribute_map=attrs, **attrs)

        get_api_response.counter = 0
        paginated_response = gather_all_api_paginated_results(get_api_response)()
        self.assertEqual(get_api_response.counter, 2)
        self.assertEqual(len(paginated_response.results), paginated_response.count)
