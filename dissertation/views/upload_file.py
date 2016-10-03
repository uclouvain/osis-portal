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
from django.contrib.auth.decorators import login_required
from django.http import *
from dissertation import models as mdl
from osis_common import models as mdl_osis_common


@login_required
def download(request, pk):
    dissertation_document = mdl.dissertation_document_file.find_by_id(pk)
    document = mdl_osis_common.document_file.find_by_id(dissertation_document.document_file.id)
    filename = document.file_name
    response = HttpResponse(document.file, content_type=document.content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


def save_uploaded_file(request):
    data = request.POST
    if request.method == 'POST':
        if request.POST.get('dissertation_id'):
            dissertation = mdl.dissertation.find_by_id(request.POST['dissertation_id'])
        file_selected = request.FILES['file']
        file = file_selected
        file_name = file_selected.name
        content_type = file_selected.content_type
        size = file_selected.size
        description = data['description']
        storage_duration = 0
        documents = mdl.dissertation_document_file.search(dissertation, description)
        for document in documents:
            old_document = mdl_osis_common.document_file.find_by_id(document.document_file.id)
            old_document.delete()
            document.delete()
        new_document = mdl_osis_common.document_file.DocumentFile(file_name=file_name,
                                                                  file=file,
                                                                  description=description,
                                                                  storage_duration=storage_duration,
                                                                  application_name='dissertation',
                                                                  content_type=content_type,
                                                                  size=size,
                                                                  user=request.user)
        new_document.save()
        dissertation_file = mdl.dissertation_document_file.DissertationDocumentFile()
        dissertation_file.dissertation = dissertation
        dissertation_file.document_file = new_document
        dissertation_file.save()
    return HttpResponse('')

