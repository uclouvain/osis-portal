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
from datetime import datetime
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from admission import models as mdl
from admission.forms.applicant import ApplicantForm
from reference import models as mdl_ref
from admission.views import demande_validation, assimilation_criteria as assimilation_criteria_view, navigation, \
    upload_file
from osis_common import models as mdl_osis_common
from admission.models.enums import document_type
from osis_common.forms import UploadDocumentFileForm
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from reference.enums import assimilation_criteria as assimilation_criteria_enum

RADIO_NAME_ASSIMILATION_CRITERIA = "assimilation_criteria_"


@login_required(login_url=settings.ADMISSION_LOGIN_URL)
def home(request):
    applicant = mdl.applicant.find_by_user(request.user)
    same_addresses = True
    person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
    if person_contact_address:
        same_addresses = False
    if applicant:
        if applicant.language:
            user_language = applicant.language
            translation.activate(user_language)
            request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        applications = mdl.application.find_by_user(request.user)
        person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
        person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
        if applications:
            applicant_form = ApplicantForm()

            return render(request, "applications.html", {'applications': applications,
                                                         'applicant': applicant,
                                                         'applicant_form': applicant_form,
                                                         'person_legal_address': person_legal_address,
                                                         'person_contact_address': person_contact_address,
                                                         "tab_active": -1})
        else:
            assimilation_criteria = assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES
            applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_by_applicant(applicant.id)
            return render(request, "admission_home.html", {
                'applications': applications,
                'applicant': applicant,
                'tab_active': navigation.PROFILE_TAB,
                'first': True,
                'countries': mdl_ref.country.find_all(),
                'main_status': 0,
                'picture': get_picture_id(request.user),
                'id_document': get_id_document(request.user),
                'person_legal_address': person_legal_address,
                'person_contact_address': person_contact_address,
                'assimilation_criteria': assimilation_criteria,
                'applicant_assimilation_criteria': applicant_assimilation_criteria,
                'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
                'assimilation_documents_existing': get_assimilation_documents_existing(request.user),
                'same_addresses': same_addresses})

    else:
        return profile(request)


def profile(request, application_id=None, message_success=None):
    message_info = None
    application = None
    assimilation_case = False

    if application_id:
        application = mdl.application.find_by_id(application_id)
    if request.method == 'POST':
        applicant_form = ApplicantForm(data=request.POST)
        applicant = mdl.applicant.find_by_user(request.user)
        person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')

        if person_legal_address is None:
            person_legal_address = mdl.person_address.PersonAddress()
            person_legal_address.person = applicant
            person_legal_address.type = 'LEGAL'

        if request.POST['last_name']:
            applicant.user.last_name = request.POST['last_name']
        else:
            applicant.user.last_name = None
        if request.POST['first_name']:
            applicant.user.first_name = request.POST['first_name']
        else:
            applicant.user.first_name = None
        if request.POST['middle_name']:
            applicant.middle_name = request.POST['middle_name']
        else:
            applicant.middle_name = None
        if request.POST['birth_date']:
            try:
                applicant.birth_date = datetime.strptime(request.POST['birth_date'], '%d/%m/%Y')
            except ValueError:
                applicant.birth_date = None
                applicant_form.errors['birth_date'] = "La date encodée('%s') semble incorrecte " % request.POST[
                    'birth_date']
        else:
            applicant.birth_date = None
        if request.POST['birth_place']:
            applicant.birth_place = request.POST['birth_place']
        else:
            applicant.birth_place = None
        if request.POST.get('birth_country'):
            birth_country_id = request.POST['birth_country']
            if birth_country_id and int(birth_country_id) >= 0:
                birth_country = mdl_ref.country.find_by_id(birth_country_id)
            else:
                birth_country = None
            applicant.birth_country = birth_country
        else:
            applicant.birth_country = None
        if request.POST.get('gender'):
            applicant.gender = request.POST['gender']
        else:
            applicant.gender = None
        if request.POST['civil_status']:
            applicant.civil_status = request.POST['civil_status']
        else:
            applicant.civil_status = None
        if request.POST['number_children']:
            applicant.number_children = request.POST['number_children']
        else:
            applicant.number_children = None
        if request.POST['spouse_name']:
            applicant.spouse_name = request.POST['spouse_name']
        else:
            applicant.spouse_name = None
        if request.POST.get('nationality') and not request.POST.get('nationality') == "-1":
            country_id = request.POST['nationality']
            if country_id and int(country_id) >= 0:
                country = mdl_ref.country.find_by_id(country_id)
            else:
                country = None
            if country:
                if not country.european_union:
                    assimilation_case = True
            applicant.nationality = country
        else:
            applicant.nationality = None
        if request.POST['national_id']:
            applicant.national_id = request.POST['national_id']
        else:
            applicant.national_id = None
        if request.POST['id_card_number']:
            applicant.id_card_number = request.POST['id_card_number']
        else:
            applicant.id_card_number = None
        if request.POST['passport_number']:
            applicant.passport_number = request.POST['passport_number']
        else:
            applicant.passport_number = None
        if request.POST['legal_adr_street']:
            person_legal_address.street = request.POST['legal_adr_street']
        else:
            person_legal_address.street = ''
        if request.POST['legal_adr_number']:
            person_legal_address.number = request.POST['legal_adr_number']
        else:
            person_legal_address.number = ''
        if request.POST['legal_adr_complement']:
            person_legal_address.complement = request.POST['legal_adr_complement']
        else:
            person_legal_address.complement = None
        if request.POST['legal_adr_postal_code']:
            person_legal_address.postal_code = request.POST['legal_adr_postal_code']
        else:
            person_legal_address.postal_code = ''
        if request.POST['legal_adr_city']:
            person_legal_address.city = request.POST['legal_adr_city']
        else:
            person_legal_address.city = ''

        if request.POST.get('legal_adr_country') and not request.POST.get('legal_adr_country') == "-1":
            country_id = request.POST['legal_adr_country']
            country = None
            if country_id and int(country_id) >= 0:
                country = mdl_ref.country.find_by_id(country_id)
            person_legal_address.country = country
        else:
            applicant_form.errors['legal_adr_country'] = _('mandatory_field')

        if request.POST.get('same_contact_legal_addr') == "false":
            person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
            if person_contact_address is None:
                person_contact_address = mdl.person_address.PersonAddress()
                person_contact_address.person = applicant
                person_contact_address.type = 'CONTACT'

            if request.POST['contact_adr_street']:
                person_contact_address.street = request.POST['contact_adr_street']
            else:
                person_contact_address.street = None
            if request.POST['contact_adr_number']:
                person_contact_address.number = request.POST['contact_adr_number']
            else:
                person_contact_address.number = None
            if request.POST['contact_adr_complement']:
                person_contact_address.complement = request.POST['contact_adr_complement']
            else:
                person_contact_address.complement = None
            if request.POST['contact_adr_postal_code']:
                person_contact_address.postal_code = request.POST['contact_adr_postal_code']
            else:
                person_contact_address.postal_code = None
            if request.POST['contact_adr_city']:
                person_contact_address.city = request.POST['contact_adr_city']
            else:
                person_contact_address.city = None
            if request.POST['contact_adr_country']:
                country_id = request.POST['contact_adr_country']
                country = None
                if country_id and int(country_id) >= 0:
                    country = mdl_ref.country.find_by_id(country_id)
                if country:
                    person_contact_address.country = country
            else:
                person_contact_address.country = None
            same_addresses = False
            person_contact_address.save()
        else:
            same_addresses = True
            person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
            if person_contact_address:
                person_contact_address.delete()
                person_contact_address = None

        if request.POST['phone_mobile']:
            applicant.phone_mobile = request.POST['phone_mobile']
        if request.POST['phone']:
            applicant.phone = request.POST['phone']
        else:
            applicant.phone = None

        if request.POST['previous_enrollment'] == "true":
            if request.POST['registration_id']:
                applicant.registration_id = request.POST['registration_id']
            else:
                applicant.registration_id = None
            if request.POST['last_academic_year']:
                applicant.last_academic_year = request.POST['last_academic_year']
            else:
                applicant.last_academic_year = None
            previous_enrollment = True
        else:
            applicant.registration_id = None
            applicant.last_academic_year = None
            previous_enrollment = False
        if assimilation_case:
            # verify if it exists one record per criteria
            default_criteria_list = assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES
            for criteria in default_criteria_list:
                crit = criteria[0]
                existing_crit = mdl.applicant_assimilation_criteria.find_first(applicant, crit)
                if existing_crit is None:
                    applicant_assimilation_criteria = \
                        mdl.applicant_assimilation_criteria.ApplicantAssimilationCriteria()
                    applicant_assimilation_criteria.criteria = crit
                    applicant_assimilation_criteria.applicant = applicant
                    applicant_assimilation_criteria.additional_criteria = None
                    applicant_assimilation_criteria.selected = None
                    applicant_assimilation_criteria.save()
                if application:
                    application_assimilation_criteria = mdl.application_assimilation_criteria.find_first(application,
                                                                                                         crit)
                    if application_assimilation_criteria is None:
                        application_assimilation_criteria = \
                            mdl.application_assimilation_criteria.ApplicationAssimilationCriteria()
                        application_assimilation_criteria.criteria = crit
                        application_assimilation_criteria.application = application
                        application_assimilation_criteria.additional_criteria = None
                        application_assimilation_criteria.selected = None
                        application_assimilation_criteria.save()

            for key in request.POST:
                if key[0:len(RADIO_NAME_ASSIMILATION_CRITERIA)] == RADIO_NAME_ASSIMILATION_CRITERIA:
                    criteria_id = key[len(RADIO_NAME_ASSIMILATION_CRITERIA):]
                    criteria_ref = assimilation_criteria_enum.find(criteria_id)
                    criteria = criteria_ref[0]
                    applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_first(applicant,
                                                                                                     criteria)
                    if applicant_assimilation_criteria is None:
                        applicant_assimilation_criteria = mdl.applicant_assimilation_criteria\
                            .ApplicantAssimilationCriteria()
                        applicant_assimilation_criteria.criteria = criteria
                        applicant_assimilation_criteria.applicant = applicant
                    if request.POST[key] == "true":
                        if criteria:
                            assimilation_basic_documents = assimilation_criteria_view.\
                                find_list_assimilation_basic_documents()
                            list_document_type_needed = assimilation_criteria_view.\
                                get_list_documents_descriptions(criteria)
                            list_document_type_needed.append(document_type.ID_CARD)

                            if criteria == assimilation_criteria_enum.CRITERIA_5:
                                if request.POST.get("criteria_5") == assimilation_criteria_enum.CRITERIA_1:
                                    list_document_type_needed.extend([document_type.RESIDENT_LONG_DURATION,
                                                                      document_type.ID_FOREIGN_UNLIMITED])
                                if request.POST.get("criteria_5") == assimilation_criteria_enum.CRITERIA_2:
                                    list_document_type_needed.extend([
                                        document_type.ATTACHMENT_26,
                                        document_type.REFUGEE_CARD,
                                        document_type.FAMILY_COMPOSITION,
                                        document_type.BIRTH_CERTIFICATE,
                                        document_type.REFUGEE_CARD,
                                        document_type.RESIDENT_CERTIFICATE,
                                        document_type.FOREIGN_INSCRIPTION_CERTIFICATE,
                                        document_type.SUBSIDIARY_PROTECTION_DECISION,
                                        document_type.RESIDENCE_PERMIT,
                                        document_type.STATELESS_CERTIFICATE])
                                if request.POST.get("criteria_5") == assimilation_criteria_enum.CRITERIA_3:
                                    list_document_type_needed.extend([document_type.FAMILY_COMPOSITION,
                                                                      document_type.PAYCHECK_1,
                                                                      document_type.PAYCHECK_2,
                                                                      document_type.PAYCHECK_3,
                                                                      document_type.PAYCHECK_4,
                                                                      document_type.PAYCHECK_5,
                                                                      document_type.PAYCHECK_6,
                                                                      document_type.RESIDENT_CERTIFICATE,
                                                                      document_type.ID_CARD])
                                if request.POST.get("criteria_5") == assimilation_criteria_enum.CRITERIA_4:
                                    list_document_type_needed.extend([document_type.CPAS])

                            for basic_doc_description in assimilation_basic_documents:
                                if basic_doc_description not in list_document_type_needed:
                                    app_doc_files = mdl.applicant_document_file.\
                                        find_by_applicant_and_description(applicant, basic_doc_description)
                                    for app_doc_file in app_doc_files:
                                        # delete unnecessary documents
                                        app_doc_file.document_file.delete()

                            applicant_assimilation_criteria.additional_criteria = \
                                define_additional_criteria(request.POST.get("criteria_5"))
                            applicant_assimilation_criteria.selected = True
                            applicant_assimilation_criteria.save()

                            # Update/create application_assimilation_criteria
                            if application:
                                application_assimilation_criteria = mdl.application_assimilation_criteria.\
                                    find_first(application, criteria)
                                application_assimilation_criteria.criteria = criteria
                                if applicant_assimilation_criteria.additional_criteria:
                                    application_assimilation_criteria.additional_criteria = \
                                        applicant_assimilation_criteria.additional_criteria
                                application_assimilation_criteria.selected = True
                                application_assimilation_criteria.save()

                    if request.POST[key] == "false":
                        applicant_assimilation_criteria.selected = False
                        applicant_assimilation_criteria.save()
                        # Update/create application_assimilation_criteria
                        if application:
                            application_assimilation_criteria = mdl.application_assimilation_criteria.\
                                find_first(application, criteria)
                            application_assimilation_criteria.criteria = criteria
                            if applicant_assimilation_criteria.additional_criteria:
                                application_assimilation_criteria.additional_criteria = \
                                    applicant_assimilation_criteria.additional_criteria
                            application_assimilation_criteria.selected = False
                            application_assimilation_criteria.save()

        else:
            # cleanup the database if needed
            delete_previous_criteria(applicant, application)
        message_success = None

        if person_contact_address:
            person_contact_address.save()
        person_legal_address.save()
        applicant.user.save()
        if application:
            application.application_type = mdl.application.define_application_type(application.coverage_access_degree,
                                                                                   request.user)
            application.save()
        request.user = applicant.user  # Otherwise it was not refreshed while going back to home page
        applicant.save()
        message_info = _('msg_info_saved')

        following_tab = navigation.get_following_tab(request, 'profile', application)
        if following_tab:
            return following_tab
    else:
        applicant = mdl.applicant.find_by_user(request.user)
        applicant_form = ApplicantForm()
        if applicant:
            person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
            same_addresses = True
            if person_contact_address:
                same_addresses = False

            previous_enrollment = False
            if applicant.registration_id or applicant.last_academic_year:
                previous_enrollment = True
        else:
            return HttpResponseRedirect('/admission/logout')

    countries = mdl_ref.country.find_all()
    props = mdl.properties.find_by_key('INSTITUTION')
    if props:
        institution_name = props.value
    else:
        institution_name = None

    assimilation_criteria = assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES
    applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_by_applicant(applicant.id)

    # validated are not ready yet, to be achieved in another issue - Leila
    person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
    person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')

    document_formset = UploadDocumentFileForm()
    data = {
        'applicant': applicant,
        'applicant_form': applicant_form,
        'countries': countries,
        'assimilation_criteria': assimilation_criteria,
        'applicant_assimilation_criteria': applicant_assimilation_criteria,
        'person_legal_address': person_legal_address,
        'person_contact_address': person_contact_address,
        'same_addresses': same_addresses,
        'previous_enrollment': previous_enrollment,
        'institution': institution_name,
        'message_success': message_success,
        'tab_active': navigation.PROFILE_TAB,
        'application': application,
        'applications': mdl.application.find_by_user(request.user),
        'picture': get_picture_id(request.user),
        'id_document': get_id_document(request.user),
        'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
        'assimilation_documents_existing': get_assimilation_documents_existing(request.user),
        'document_formset': document_formset,
        'message_info': message_info}
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


@login_required(login_url=settings.ADMISSION_LOGIN_URL)
def home_retour(request):
    applications = mdl.application.find_by_user(request.user)
    return render(request, "admission_home.html", {'applications': applications, 'message_info': _('msg_info_saved')})


def get_picture_id(user):
    applicant = mdl.applicant.find_by_user(user)
    app_doc_file = mdl.applicant_document_file.find_last_by_applicant_and_description(
        applicant, document_type.ID_PICTURE)
    if app_doc_file:
        return ''.join(('/admission', app_doc_file.document_file.file.url))

    return None


def get_id_document(user):
    applicant = mdl.applicant.find_by_user(user)
    app_doc_file = mdl.applicant_document_file.find_last_by_applicant_and_description(applicant, document_type.ID_CARD)
    if app_doc_file:
        return ''.join(('/admission', app_doc_file.document_file.file.url))
    return None


def get_document_assimilation(user, description):
    applicant = mdl.applicant.find_by_user(user)
    app_doc_file = mdl.applicant_document_file.find_last_by_applicant_and_description(applicant, description)
    if app_doc_file:
        return ''.join(('/admission', app_doc_file.document_file.file.url))
    return None


def get_assimilation_documents_existing(user):
    applicant = mdl.applicant.find_by_user(user)
    assimilation_basic_documents = assimilation_criteria_view.find_list_assimilation_basic_documents()
    docs = []
    for document_type_description in assimilation_basic_documents:
        app_doc_files = mdl.applicant_document_file\
            .find_by_applicant_and_description(applicant, document_type_description)
        if app_doc_files:
            document_files = []
            for app_doc_file in app_doc_files:
                document_files.append(app_doc_file.document_file)
            docs.extend(document_files)

    return docs


def documents_upload(request):
    assimilation_uploads = assimilation_criteria_view.find_list_assimilation_basic_documents()
    applicant = mdl.applicant.find_by_user(request.user)
    prerequisites_uploads = [document_type.NATIONAL_DIPLOMA_RECTO,
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
    application = None

    if request.POST.get('application_id'):
        application_id = request.POST['application_id']
        application = mdl.application.find_by_id(application_id)
    for key in request.POST:
        if key[0:26] == "uploaded_file_description_":
            if request.POST[key]:
                file_description = key[26:]
                if request.POST["uploaded_file_name_"+file_description]:
                    fn = request.POST["uploaded_file_name_"+file_description]
                    file = request.FILES["uploaded_file_"+file_description]
                    if file_description in prerequisites_uploads:
                        app_doc_files = mdl.applicant_document_file\
                            .find_by_applicant_and_description(applicant, file_description)
                        for app_doc_file in app_doc_files:
                            app_doc_file.document_file.delete()

                    if file_description == document_type.ID_PICTURE \
                        or file_description == document_type.ID_CARD \
                        or file_description in prerequisites_uploads \
                            or file_description in assimilation_uploads:
                        # Delete older file with the same description
                        app_doc_files = mdl.applicant_document_file\
                            .find_by_applicant_and_description(applicant, file_description)
                        for app_doc_file in app_doc_files:
                            app_doc_file.document_file.delete()

                        storage_duration = 0
                        content_type = file.content_type
                        size = file.size

                        doc_file = mdl_osis_common.document_file.DocumentFile(file_name=fn,
                                                                              file=file,
                                                                              description=file_description,
                                                                              storage_duration=storage_duration,
                                                                              application_name='admission',
                                                                              content_type=content_type,
                                                                              size=size,
                                                                              update_by=request.user.username)
                        doc_file.save()
                        applicant_document_file = mdl.applicant_document_file\
                                                     .ApplicantDocumentFile(applicant=applicant, document_file=doc_file)
                        applicant_document_file.save()
                        if file_description in prerequisites_uploads:
                            adm_doc_file = mdl.application_document_file.ApplicationDocumentFile()
                            adm_doc_file.application = application
                            adm_doc_file.document_file = doc_file
                            adm_doc_file.save()


def define_additional_criteria(criteria5):
    if criteria5:
        criteria_ref = assimilation_criteria_enum.find(criteria5)
        if criteria_ref:
            return criteria_ref[0]

    return None


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl_osis_common.document_file.DocumentFile
        fields = ('file', 'file_name', 'content_type')


def get_picture(request):
    applicant = mdl.applicant.find_by_user(request.user)
    description = request.GET['description']
    app_doc_files = mdl.applicant_document_file.find_by_applicant_and_description(applicant, description)
    if app_doc_files:
        serializer = DocumentFileSerializer(app_doc_files[0].document_file)
        return JSONResponse(serializer.data)
    return None


def delete_previous_criteria(applicant, application):
    criteria_list = mdl.applicant_assimilation_criteria.find_by_applicant(applicant)
    for c in criteria_list:
        c.delete()
    if application:
        criteria_list = mdl.application_assimilation_criteria.find_by_application(application)
        for c in criteria_list:
            c.delete()
    for description in assimilation_criteria_view.find_list_only_assimilation_documents():
        upload_file.delete_existing_applicant_documents(applicant, description)


def is_local_language_exam_needed(application):
    if application and application.offer_year.grade_type:
        return application.offer_year.grade_type.language_exam_required
    return False
