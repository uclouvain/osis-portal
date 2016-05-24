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

from couchbase import Couchbase
from pprint import pprint
import json


def couchbase_insert(json_datas):
    cb = Couchbase.connect(bucket='default')
    data = json.loads(json_datas.decode("utf-8"))
    key = "{0}-{1}".format(
        data['id'],
        data['name'].replace(' ', '_').lower()
    )
    print('inserting datas in couchDB...')
    cb.set(key, data)
    print('Done.')
    print('getting datas just inserted in couchDB...')
    result = cb.get(key)
    pprint(result.value, indent=4)
    print('Done.')
    print('deleting datas just inserted in couchDB...')
    cb.delete(key)
    print('Done.')
