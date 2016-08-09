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
from django.shortcuts import get_object_or_404, render, redirect
from django.http import *
from osis_common.forms import UploadDocumentFileForm
from osis_common import models as mdl_osis_common
from admission.views import common
from admission import settings as adm_settings
from admission.views import tabs
from admission import models as mdl
from reference import models as mdl_ref


@login_required
def upload_file(request):

    description = 'LETTER_MOTIVATION'
    documents = mdl_osis_common.document_file.search(document_type=adm_settings.DOCUMENT_TYPE, user=request.user)
    if request.method == "POST":

        if request.POST['description']:
            description = request.POST['description']

        form = UploadDocumentFileForm(request.POST, request.FILES)
        if form.is_valid():
            if description == 'ID_PICTURE' or description == 'ID_CARD':
                # Delete older file with the same description
                documents = mdl_osis_common.document_file.search(
                    document_type=None,
                    user=request.user,
                    description=description)
                for document in documents:
                    document.delete()

            file = form.save()
            file.size = file.file.size
            file.file_name = request.FILES['file'].name
            file_type = form.cleaned_data["file"]
            content_type = file_type.content_type
            file.content_type = content_type
            file.save()
            if description == 'ID_PICTURE' or description == 'ID_CARD':
                tab_status = tabs.init(request)
                applicant = mdl.applicant.find_by_user(request.user)
                applications = mdl.application.find_by_user(request.user)
                person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
                person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
                return render(request, "admission_home.html", {
                    'applications': applications,
                    'applicant': applicant,
                    'tab_active': 0,
                    'first': True,
                    'countries': mdl_ref.country.find_all(),
                    'tab_profile': tab_status['tab_profile'],
                    'tab_applications': tab_status['tab_applications'],
                    'tab_diploma': tab_status['tab_diploma'],
                    'tab_curriculum': tab_status['tab_curriculum'],
                    'tab_accounting': tab_status['tab_accounting'],
                    'tab_sociological': tab_status['tab_sociological'],
                    'tab_attachments': tab_status['tab_attachments'],
                    'tab_submission': tab_status['tab_submission'],
                    'main_status': 0,
                    'picture': common.get_picture_id(request.user),
                    'id_document': common.get_id_document(request.user),
                    'person_legal_address': person_legal_address,
                    'person_contact_address': person_contact_address})
            else:
                return redirect('new_document')
        else:
            return render(request, 'new_document.html', {
                'form': form,
                'content_type_choices': mdl_osis_commondocument_file.CONTENT_TYPE_CHOICES,
                'description_choices': mdl_osis_common.document_file.DESCRIPTION_CHOICES,
                'description': description,
                'documents': documents})
    else:
        form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                               'document_type': "admission",
                                               'user': request.user})
        return render(request, 'new_document.html', {
            'form': form,
            'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
            'description_choices': mdl_osis_common.document_file.DESCRIPTION_CHOICES,
            'description': description,
            'documents': documents})


@login_required
def download(request, pk):
    document = get_object_or_404(mdl_osis_common.document_file.DocumentFile, pk=pk)
    filename = document.file_name
    response = HttpResponse(document.file, content_type=document.content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


def upload_file_description(request):
    """
    To display the scree to upload id_picture
    :param request:
    :return:
    """
    documents = mdl_osis_common.document_file.search(document_type=None,
                                                     user=request.user,
                                                     description="ID_PICTURE")

    description = request.POST['description']
    form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                           'document_type': "admission",
                                           'user': request.user})
    return render(request, 'new_document.html', {
        'form': form,
        'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
        'description_choices': mdl_osis_common.document_file.DESCRIPTION_CHOICES,
        'description': description,
        'documents': documents})


@login_required
def upload_document(request):
    documents = mdl_osis_common.document_file.search(document_type=None, user=request.user, description=None)

    if request.method == "POST":
        description = None
        if request.POST['description']:
            description = request.POST['description']
        form = UploadDocumentFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.size = file.file.size
            file.file_name = request.FILES['file'].name
            file_type = form.cleaned_data["file"]
            content_type = file_type.content_type
            file.content_type = content_type
            file.save()
            return redirect('new_document')
        else:
            if description == mdl_osis_common.document_file.DESCRIPTION_CHOICES['ID_PICTURE']:
                return common.home(request)
            else:
                return render(request, 'new_document.html', {
                    'form': form,
                    'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
                    'description_choices': mdl_osis_common.document_file.DESCRIPTION_CHOICES,
                    'description': description,
                    'documents': documents})
