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
from django.shortcuts import get_object_or_404, render, redirect
from django.http import *
from osis_common.forms import UploadDocumentFileForm
from osis_common.models.document_file import DocumentFile


def upload_file(request):
    documents = DocumentFile.objects.filter(user=request.user).filter(document_type="admission")
    if request.method == "POST":
        form = UploadDocumentFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.size = file.file.size
            file.file_name = request.FILES['file'].name
            file_type = form.cleaned_data["file"]
            content_type = file_type.content_type
            file.content_type = content_type
            file.save()
            return redirect('new_file')
        else:
            return render(request, 'new_file.html', {'form': form,
                                                     'content_type_choices': DocumentFile.CONTENT_TYPE_CHOICES,
                                                     'description_choices': DocumentFile.DESCRIPTION_CHOICES,
                                                     'documents': documents})
    else:
        form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                               'document_type': "admission",
                                               'user': request.user})
        return render(request, 'new_file.html', {'form': form,
                                                 'content_type_choices': DocumentFile.CONTENT_TYPE_CHOICES,
                                                 'description_choices': DocumentFile.DESCRIPTION_CHOICES,
                                                 'documents': documents})


def download(request, pk):
    document = get_object_or_404(DocumentFile, pk=pk)
    filename = document.file_name
    response = HttpResponse(document.file, content_type=document.content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response
