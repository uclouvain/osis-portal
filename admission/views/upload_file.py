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
from django.shortcuts import get_object_or_404, render, redirect

from admission import models as mdl
from admission import settings as adm_settings
from admission.models.enums import document_type
from admission.views import common, tabs, assimilation_criteria as assimilation_criteria_view
from osis_common import models as mdl_osis_common
from osis_common.forms import UploadDocumentFileForm
from reference import models as mdl_ref
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


@login_required
def upload_file(request):
    print('upload_file')
    description = None
    documents = mdl_osis_common.document_file.search(description=description, user=request.user)
    if request.method == "POST":
        application = None
        if request.POST['description']:
            description = request.POST['description']
        if request.POST['application_id']:
            application_id = request.POST['application_id']
            application = mdl.application.find_by_id(application_id)

        document_formset = UploadDocumentFileForm(request.POST, request.FILES)
        valide_form = True
        print(document_formset.errors['content_type'])

        if document_formset.validate() is None:
            curriculum_uploads = [document_type.NATIONAL_DIPLOMA_RECTO,
                                  document_type.NATIONAL_DIPLOMA_VERSO,
                                  document_type.INTERNATIONAL_DIPLOMA_RECTO,
                                  document_type.INTERNATIONAL_DIPLOMA_VERSO,
                                  document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO,
                                  document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO,
                                  document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO,
                                  document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO,
                                  document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO,
                                  document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO,
                                  document_type.EQUIVALENCE,
                                  document_type.ADMISSION_EXAM_CERTIFICATE,
                                  document_type.PROFESSIONAL_EXAM_CERTIFICATE]
            assimilation_uploads = assimilation_criteria_view.find_list_assimilation_basic_documents()

            if description in curriculum_uploads:
                documents = mdl.application_document_file.search(application, description)
                for document in documents:
                    document.delete()
            if description == document_type.ID_PICTURE \
                    or description == document_type.ID_CARD \
                    or description in curriculum_uploads \
                    or description in assimilation_uploads:
                # Delete older file with the same description
                documents = mdl_osis_common.document_file.search(user=request.user, description=description)
                for document in documents:
                    document.delete()

            save_document_from_form(document_formset, request)
            if description in curriculum_uploads:
                adm_doc_file = mdl.application_document_file.ApplicationDocumentFile()
                adm_doc_file.application = application
                adm_doc_file.document_file = file
                adm_doc_file.save()

            if (description == document_type.ID_PICTURE or description == document_type.ID_CARD) or \
                            description in assimilation_uploads:
                tab_status = tabs.init(request)
                applicant = mdl.applicant.find_by_user(request.user)
                applications = mdl.application.find_by_user(request.user)
                person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
                person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
                assimilation_criteria = mdl_ref.assimilation_criteria.find_criteria()
                applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_by_applicant(applicant.id)

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
                    'person_contact_address': person_contact_address,
                    'assimilationCriteria': assimilation_criteria,
                    'applicant_assimilation_criteria': applicant_assimilation_criteria,
                    'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
                    'assimilation_documents_existing': common.get_assimilation_documents_existing(request.user)})
            else:
                if description in curriculum_uploads:
                    return HttpResponseRedirect(reverse('diploma_update', args=(application.id,)))
                else:
                    return redirect('new_document')
        else:
            documents = mdl_osis_common.document_file.search(user=request.user, description=description)
            return render(request, 'new_document.html', {
                'form': document_formset,
                'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
                'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
                'description': description,
                'documents': documents})
    else:
        form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                               'document_type': "admission",
                                               'user': request.user})
        return render(request, 'new_document.html', {
            'form': form,
            'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
            'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
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

    description = request.POST['description']
    application_id = request.POST['application_id']
    if not application_id.isdigit():
        application_id = None

    documents = mdl_osis_common.document_file.search(user=request.user, description=description)
    form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                           'document_type': "admission",
                                           'user': request.user})
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = None
    return render(request, 'new_document.html', {
        'form': form,
        'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
        'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
        'description': description,
        'documents': documents,
        'application': application})


@login_required
def upload_document(request):
    documents = mdl_osis_common.document_file.search(user=request.user, description=None)

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
            if description == mdl.enums.document_type.DOCUMENT_TYPE_CHOICES[document_type.ID_PICTURE]:
                # return common.home(request)
                return HttpResponseRedirect(reverse('home', ))
            else:
                return render(request, 'new_document.html', {
                    'form': form,
                    'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
                    'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
                    'description': description,
                    'documents': documents})


@login_required
def delete(request, pk):
    document = get_object_or_404(mdl_osis_common.document_file.DocumentFile, pk=pk)
    if document:
        description = document.description
        document.delete()
        documents = mdl_osis_common.document_file.search(user=request.user, description=description)

        return render(request, 'new_document.html', {
            'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
            'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
            'description': description,
            'documents': documents})


def save_document_from_form(document, request):
    """
    Save a document (attachment) from a form.
    :param document: an UploadDocumentForm received from a POST request.
    :param user: the current user
    :return:
    """
    file_name = request.FILES['file'].name
    file = document.cleaned_data['file']
    description = document.cleaned_data['description']
    # Never trust a user. They could change the hidden input values.
    # Ex: user, document_type, storage_duration, etc.
    storage_duration = 0
    content_type = file.content_type
    size = file.size

    doc_file = mdl_osis_common.document_file.DocumentFile(file_name=file_name,
                                                          file=file,
                                                          description=description,
                                                          storage_duration=storage_duration,
                                                          application_name='admission',
                                                          content_type=content_type,
                                                          size=size,
                                                          user=request.user)
    doc_file.save()


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl_osis_common.document_file.DocumentFile
        fields = ('id', 'file_name', 'file')


def find_by_description(request):
    description = request.GET['description']
    documents = mdl_osis_common.document_file.search(request.user, description)
    last_documents=[]
    if documents:
        last_document = documents.reverse()[0]
        last_documents = [last_document]

    serializer = DocumentFileSerializer(last_documents, many=True)
    return JSONResponse(serializer.data)



