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
from couchbase.bucket import Bucket, NotFoundError
from django.conf import settings

# Helper functions to interact (connection, fetch, upsert) with the CouchBase bucket containing
# student academic results.


def connect_db():
    """
    Connect to the bucket "bucket_name" located on the server at address "COUCHBASE_CONNECTION_STRING"
    :return: the bucket
    """
    bucket_name = "student_results"
    if settings.COUCHBASE_PASSWORD:
        cb = Bucket(settings.COUCHBASE_CONNECTION_STRING+bucket_name, password=settings.COUCHBASE_PASSWORD)
    else:
        cb = Bucket(settings.COUCHBASE_CONNECTION_STRING+bucket_name)
    return cb

cb = connect_db()


def fetch_document(document_id):
    """
    Fetch the document having id (key) "document_id" from the bucket "cb".
    :param document_id: The key of the document
    :return: the document if exists, None if not.
    """
    try:
        return cb.get(document_id)
    except NotFoundError:
        return None


def insert_or_update_document(key, data):
    """
    Insert a new document if the key passed in parameter doesn't exist in CouchDB.
    :param key: The key of the document
    :param data: The document (JSON) to insert/update in Couchbase
    """
    cb.set(key, data)
