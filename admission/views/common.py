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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from admission import models as mdl
from admission.forms import ApplicantForm
from reference import models as mdl_ref
from admission.views import demande_validation, assimilation_criteria as assimilation_criteria_view
from admission.views import tabs
from osis_common import models as mdl_osis_common
from admission.models.enums import document_type
from osis_common.forms import UploadDocumentFileForm


@login_required(login_url=settings.ADMISSION_LOGIN_URL)
def home(request):
    applicant = mdl.applicant.find_by_user(request.user)

    if applicant and applicant.gender:
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
            tab_status = tabs.init(request)
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
                'picture': get_picture_id(request.user),
                'id_document': get_id_document(request.user),
                'person_legal_address': person_legal_address,
                'person_contact_address': person_contact_address,
                'assimilationCriteria': assimilation_criteria,
                'applicant_assimilation_criteria': applicant_assimilation_criteria,
                'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
                'assimilation_documents_existing': get_assimilation_documents_existing(request.user)})

    else:
        return profile(request)


def profile(request, application_id=None, message_success=None):
    tab_status = tabs.init(request)
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
            # person_legal_address.country = None
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
                person_contact_address.country = country
            else:
                person_contact_address.country = None
            same_addresses = False
        else:
            # Question que faire si true, mais qu'une adresse de contact existe déjà
            person_contact_address = None
            same_addresses = True

        if request.POST['phone_mobile']:
            applicant.phone_mobile = request.POST['phone_mobile']
        if request.POST['phone']:
            applicant.phone = request.POST['phone']
        if request.POST['additional_email']:
            applicant.additional_email = request.POST['additional_email']

        if request.POST['previous_enrollment'] == "true":
            if request.POST['registration_id']:
                applicant.registration_id = request.POST['registration_id']
            if request.POST['last_academic_year']:
                applicant.last_academic_year = request.POST['last_academic_year']
            previous_enrollment = True
        else:
            applicant.registration_id = None
            applicant.last_academic_year = None
            previous_enrollment = False

        for key in request.POST:
            if key[0:22] == "assimilation_criteria_":
                if request.POST[key] == "true":
                    criteria_id = key[22:]
                    # Delete other previous criteria encoded
                    criterias = mdl.applicant_assimilation_criteria.find_by_applicant(applicant)
                    for c in criterias:
                        if c.criteria.id != int(criteria_id):
                            c.delete()
                    #
                    criteria = mdl_ref.assimilation_criteria.find_by_id(criteria_id)
                    if criteria:
                        applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.search(applicant,
                                                                                                     criteria)
                        if not applicant_assimilation_criteria:
                            applicant_assimilation_criteria = \
                                mdl.applicant_assimilation_criteria.ApplicantAssimilationCriteria()
                            applicant_assimilation_criteria.criteria = criteria
                            applicant_assimilation_criteria.applicant = applicant
                            applicant_assimilation_criteria.save()
        documents_upload(request)

        message_success = None

        if person_contact_address:
            person_contact_address.save()
        person_legal_address.save()
        applicant.user.save()
        request.user = applicant.user  # Otherwise it was not refreshed while going back to home page
        applicant.save()

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

    assimilation_criteria = mdl_ref.assimilation_criteria.find_criteria()
    applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_by_applicant(applicant.id)
    application = None
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        tab_status = tabs.init(request)
    # validated are not ready yet, to be achieved in another issue - Leila
    person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
    person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')

    document_formset = UploadDocumentFileForm()
    return render(request, "admission_home.html", {
        'applicant': applicant,
        'applicant_form': applicant_form,
        'countries': countries,
        'assimilationCriteria': assimilation_criteria,
        'applicant_assimilation_criteria': applicant_assimilation_criteria,
        'person_legal_address': person_legal_address,
        'person_contact_address': person_contact_address,
        'same_addresses': same_addresses,
        'previous_enrollment': previous_enrollment,
        'institution': institution_name,
        "message_success": message_success,
        'tab_active': 0,
        'validated_profil': demande_validation.validate_profil(applicant, request.user),
        'validated_diploma': demande_validation.validate_diploma(application),
        'validated_curriculum': demande_validation.validate_curriculum(application),
        'validated_application': demande_validation.validate_application(application),
        'validated_accounting': demande_validation.validate_accounting(),
        'validated_sociological': demande_validation.validate_sociological(),
        'validated_attachments': demande_validation.validate_attachments(),
        'validated_submission': demande_validation.validate_submission(),
        'application': application,
        'tab_profile': tab_status['tab_profile'],
        'tab_applications': tab_status['tab_applications'],
        'tab_diploma': tab_status['tab_diploma'],
        'tab_curriculum': tab_status['tab_curriculum'],
        'tab_accounting': tab_status['tab_accounting'],
        'tab_sociological': tab_status['tab_sociological'],
        'tab_attachments': tab_status['tab_attachments'],
        'tab_submission': tab_status['tab_submission'],
        'applications': mdl.application.find_by_user(request.user),
        'picture': get_picture_id(request.user),
        'id_document': get_id_document(request.user),
        'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
        'assimilation_documents_existing': get_assimilation_documents_existing(request.user),
        'document_formset': document_formset})


@login_required(login_url=settings.ADMISSION_LOGIN_URL)
def home_retour(request):
    applications = mdl.application.find_by_user(request.user)
    return render(request, "admission_home.html", {'applications': applications, 'message_info': _('msg_info_saved')})


def extra_information(request, application):
    try:
        if application.offer_year:
            admission_exam_offer_yr = mdl.admission_exam_offer_year.find_by_offer_year(application.offer_year)
            if admission_exam_offer_yr:
                return True
        return False
    except:  # RelatedObjectDoesNotExist
        return False


def validated_extra(secondary_education, application):
    if secondary_education:
        try:
            if application.offer_year:
                admission_exam_offer_yr = mdl.admission_exam_offer_year.find_by_offer_year(application.offer_year)
                if secondary_education.admission_exam_type == admission_exam_offer_yr.admission_exam_type \
                        and secondary_education.admission_exam and secondary_education.admission_exam_date \
                        and secondary_education.admission_exam_institution \
                        and secondary_education.admission_exam_result:
                    return True
        except:
            return True

    return False


def get_picture_id(user):
    pictures = mdl_osis_common.document_file.search(user, document_type.ID_PICTURE)
    if pictures:
        picture = pictures.reverse()[0]
        return ''.join(('/admission', picture.file.url))

    return None


def get_id_document(user):
    pictures = mdl_osis_common.document_file.search(user, document_type.ID_CARD)
    if pictures:
        return ''.join(('/admission', pictures.reverse()[0].file.url))
    return None


def get_document_assimilation(user, description):
    pictures = mdl_osis_common.document_file.search(user, description)
    if pictures:
        return ''.join(('/admission', pictures.reverse()[0].file.url))
    return None


def get_assimilation_documents_existing(user):
    assimilation_basic_documents = assimilation_criteria_view.find_list_assimilation_basic_documents()
    docs = []
    for document_type_description in assimilation_basic_documents:
        pictures = mdl_osis_common.document_file.search(user, document_type_description)
        if pictures:
            docs.extend(pictures)

    return docs


def documents_upload(request):
    assimilation_uploads = assimilation_criteria_view.find_list_assimilation_basic_documents()
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
                        documents = mdl.application_document_file.search(application, file_description)
                        for document in documents:
                            document.delete()

                    if file_description == document_type.ID_PICTURE \
                        or file_description == document_type.ID_CARD \
                        or file_description in prerequisites_uploads \
                            or file_description in assimilation_uploads:
                        # Delete older file with the same description
                        documents = mdl_osis_common.document_file.search(user=request.user,
                                                                         description=file_description)
                        for document in documents:
                            document.delete()

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
                                                                              user=request.user)
                        doc_file.save()
                        if file_description in prerequisites_uploads:
                            adm_doc_file = mdl.application_document_file.ApplicationDocumentFile()
                            adm_doc_file.application = application
                            adm_doc_file.document_file = doc_file
                            adm_doc_file.save()
