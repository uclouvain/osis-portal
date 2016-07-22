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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from admission import models as mdl
from admission.forms import ApplicantForm
from reference import models as mdl_ref
from admission.views import demande_validation
from admission.views import tabs


@login_required
def home(request):
    applicant = mdl.applicant.find_by_user(request.user)

    if applicant and applicant.gender:
        if applicant.language:
            user_language = applicant.language
            translation.activate(user_language)
            request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        applications = mdl.application.find_by_user(request.user)
        if applications:
            applicant_form = ApplicantForm()
            person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
            person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
            return render(request, "applications.html", {'applications': applications,
                                                         'applicant': applicant,
                                                         'applicant_form': applicant_form,
                                                         'person_legal_address': person_legal_address,
                                                         'person_contact_address': person_contact_address,
                                                         "tab_active": -1})
        else:
            tab_status = tabs.init(request)
            return render(request, "home.html", {'applications': applications,
                                                 "tab_active": 0,
                                                 "first": True,
                                                 "countries": mdl_ref.country.find_all(),
                                                 'tab_profile': tab_status['tab_profile'],
                                                 'tab_applications': tab_status['tab_applications'],
                                                 'tab_diploma': tab_status['tab_diploma'],
                                                 'tab_curriculum': tab_status['tab_curriculum'],
                                                 'tab_accounting': tab_status['tab_accounting'],
                                                 'tab_sociological': tab_status['tab_sociological'],
                                                 'tab_attachments': tab_status['tab_attachments'],
                                                 'tab_submission': tab_status['tab_submission'],
                                                 'main_status': 0})

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
            birth_country = mdl_ref.country.find_by_id(birth_country_id)
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
        if request.POST.get('nationality'):
            country_id = request.POST['nationality']
            country = mdl_ref.country.find_by_id(country_id)
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
            person_legal_address.street = None
        if request.POST['legal_adr_number']:
            person_legal_address.number = request.POST['legal_adr_number']
        else:
            person_legal_address.number = None
        if request.POST['legal_adr_complement']:
            person_legal_address.complement = request.POST['legal_adr_complement']
        else:
            person_legal_address.complement = None
        if request.POST['legal_adr_postal_code']:
            person_legal_address.postal_code = request.POST['legal_adr_postal_code']
        else:
            person_legal_address.postal_code = None
        if request.POST['legal_adr_city']:
            person_legal_address.city = request.POST['legal_adr_city']
        else:
            person_legal_address.city = None
        if request.POST.get('legal_adr_country'):
            country_id = request.POST['legal_adr_country']
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
                    criteria = mdl_ref.assimilation_criteria.find_by_id(criteria_id)
                    if criteria:
                        person_assimilation_criteria = mdl.person_assimilation_criteria.PersonAssimilationCriteria()
                        person_assimilation_criteria.criteria = criteria
                        person_assimilation_criteria.person = applicant
                        if applicant_form.is_valid():
                            person_assimilation_criteria.save()

        message_success = 'ok'
        if applicant_form.is_valid():
            if person_contact_address:
                person_contact_address.save()
            person_legal_address.save()
            applicant.user.save()
            request.user = applicant.user  # Otherwise it was not refreshed while going back to home page
            applicant.save()
        else:
            message_success = None
    else:
        applicant = mdl.applicant.find_by_user(request.user)
        applicant_form = ApplicantForm()
        if applicant:
            person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
            person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
            same_addresses = True
            if person_contact_address:
                same_addresses = False

            previous_enrollment = False
            if applicant.registration_id or applicant.last_academic_year:
                previous_enrollment = True
        else:
            return HttpResponseRedirect('/admission/logout/?next=/admission')

    countries = mdl_ref.country.find_all()
    props = mdl.properties.find_by_key('INSTITUTION')
    if props:
        institution_name = props.value
    else:
        institution_name = None

    assimilation_criteria = mdl_ref.assimilation_criteria.find_criteria()
    person_assimilation_criteria = mdl.person_assimilation_criteria.find_by_person(applicant.id)
    application = None
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        tab_status = tabs.init(request)
    # validated are not ready yet, to be achieved in another issue - Leila
    return render(request, "home.html", {'applicant': applicant,
                                         'applicant_form': applicant_form,
                                         'countries': countries,
                                         'assimilationCriteria': assimilation_criteria,
                                         'personAssimilationCriteria': person_assimilation_criteria,
                                         'person_legal_address': person_legal_address,
                                         'person_contact_address': person_contact_address,
                                         'same_addresses': same_addresses,
                                         'previous_enrollment': previous_enrollment,
                                         'institution': institution_name,
                                         "message_success": message_success,
                                         'tab_active': 0,
                                         'validated_profil': demande_validation.validate_profil(applicant),
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
                                         'applications': mdl.application.find_by_user(request.user)})


@login_required
def home_retour(request):
    applications = mdl.application.find_by_user(request.user)
    return render(request, "home.html", {'applications': applications, 'message_info': _('msg_info_saved')})


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
