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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

from admission import models as mdl
from admission.models.enums import document_type
from admission.views import assimilation_criteria as assimilation_criteria_view
from osis_common import models as mdl_osis_common
from osis_common.forms import UploadDocumentFileForm
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer


@login_required
def download(request, pk):
    document = get_object_or_404(mdl_osis_common.document_file.DocumentFile, pk=pk)
    filename = document.file_name
    response = HttpResponse(document.file, content_type=document.content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


@login_required
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
    applicant = mdl.applicant.find_by_user(request.user)
    if description:
        documents = [app_doc_file.document_file for app_doc_file in mdl.applicant_document_file.find_by_applicant_and_description(applicant, description)]
    else:
        documents = mdl.applicant_document_file.find_document_by_applicant(applicant)
    document_files = []
    if documents.exists():
        for document in documents:
            document_files.append(document.document_file)

    form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                           'document_type': "admission",
                                           'update_by': request.user.username})
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = None
    return render(request, 'new_document.html', {
        'form': form,
        'content_type_choices': mdl_osis_common.document_file.CONTENT_TYPE_CHOICES,
        'description_choices': mdl.enums.document_type.DOCUMENT_TYPE_CHOICES,
        'description': description,
        'documents': document_files,
        'application': application})


@login_required
def upload_document(request):
    applicant = mdl.applicant.find_by_user(request.user)
    documents = mdl.applicant_document_file.find_document_by_applicant(applicant)
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


def save_document_from_form(document, request):
    """
    Save a document (attachment) from a form.
    :param document: an UploadDocumentForm received from a POST request.
    :param request:
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
                                                          update_by=request.user.username)
    doc_file.save()
    applicant = mdl.applicant.find_by_user(request.user)
    applicant_document_file = mdl.applicant_document_file.ApplicantDocumentFile(applicant=applicant,
                                                                                document_file=doc_file)
    applicant_document_file.save()


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
    applicant = mdl.applicant.find_by_user(request.user)
    app_doc_file = mdl.applicant_document_file.find_last_by_applicant_and_description(applicant, description)
    last_documents = []
    if app_doc_file:
        last_documents = [app_doc_file.document_file]

    serializer = DocumentFileSerializer(last_documents, many=True)
    return JSONResponse(serializer.data)


def save_uploaded_file(request):
    if request.method == 'POST':
        if request.POST.get('application_id'):
            application = mdl.application.find_by_id(request.POST.get('application_id'))
            applicant = application.applicant
        else:
            application = None
            applicant = mdl.applicant.find_by_user(request.user)

        description = request.POST.get('description')

        prerequis_uploads = get_prerequis_document_types()
        assimilation_uploads = assimilation_criteria_view.find_list_assimilation_basic_documents()

        if description in prerequis_uploads or description in assimilation_uploads:
            delete_existing_application_documents(application, description)

        if description == document_type.ID_PICTURE \
                or description == document_type.ID_CARD:
            delete_existing_applicant_documents(applicant, description)

        doc_file = create_document_file(description, request)
        applicant_document_file = mdl.applicant_document_file.ApplicantDocumentFile(applicant=applicant,
                                                                                    document_file=doc_file)
        applicant_document_file.save()

        if description in prerequis_uploads:
            adm_doc_file = mdl.application_document_file.ApplicationDocumentFile()
            adm_doc_file.application = application
            adm_doc_file.document_file = doc_file
            adm_doc_file.save()
            if description == document_type.PROFESSIONAL_EXAM_CERTIFICATE:
                secondary_education = mdl.secondary_education.find_by_person(applicant)
                secondary_education_exam_type = 'PROFESSIONAL'
                if secondary_education is None:
                    secondary_education = mdl.secondary_education.SecondaryEducation()
                    secondary_education.person = applicant
                    secondary_education.save()

                secondary_education_exams = mdl.secondary_education_exam.search(None,
                                                                                secondary_education,
                                                                                secondary_education_exam_type)
                if not secondary_education_exams.exists():
                    secondary_education_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                    secondary_education_exam.secondary_education = secondary_education
                    secondary_education_exam.type = secondary_education_exam_type
                    secondary_education_exam.save()

    return HttpResponse('')


@login_required
def delete_document_file(request):
    pk = request.POST.get('document_file_id')
    if pk:
        document = get_object_or_404(mdl_osis_common.document_file.DocumentFile, pk=pk)
        if document:
            document.delete()
    else:
        description = request.POST.get('description')
        if description:
            applicant = mdl.applicant.find_by_user(request.user)
            app_doc_files = mdl.applicant_document_file.find_by_applicant_and_description(applicant, description)
            [app_doc_file.document_file.delete() for app_doc_file in app_doc_files]
    return HttpResponse('')


def find_by_description_application(request):
    description = request.GET['description']
    application = request.GET['application']

    application_document_files = mdl.application_document_file.find_document_by_application_description(application,
                                                                                                        description)
    documents = [application_document_file.document_file for application_document_file in
                 application_document_files]
    last_documents = []
    if documents:
        last_document = documents[-1]
        last_documents = [last_document]

    serializer = DocumentFileSerializer(last_documents, many=True)
    return JSONResponse(serializer.data)


def create_document_file(description, request):
    file_selected = request.FILES['file']
    doc_file = mdl_osis_common.document_file.DocumentFile(file_name=file_selected.name,
                                                          file=file_selected,
                                                          description=description,
                                                          storage_duration=0,
                                                          application_name='admission',
                                                          content_type=file_selected.content_type,
                                                          size=file_selected.size,
                                                          update_by=request.user.username)
    doc_file.save()
    return doc_file


def delete_existing_applicant_documents(applicant, description):
    # Delete older file with the same description
    applicant_document_files = mdl.applicant_document_file.find_by_applicant_and_description(applicant, description)
    [applicant_document_file.document_file.delete() for applicant_document_file in applicant_document_files]


def delete_existing_application_documents(application, description):
    application_document_files = mdl.application_document_file.search(application, description)
    [application_document_file.document_file.delete() for application_document_file in application_document_files]


def get_prerequis_document_types():
    return [document_type.NATIONAL_DIPLOMA_RECTO,
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
            document_type.PROFESSIONAL_EXAM_CERTIFICATE,
            document_type.LANGUAGE_EXAM_CERTIFICATE]
