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
from admission import models as mdl
from reference import models as mdl_ref
from datetime import datetime
from admission.forms import PersonForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import translation


@login_required
def home(request):
    person = mdl.person.find_by_user(request.user)

    if person and person.gender:
        if person.language:
            user_language = person.language
            translation.activate(user_language)
            request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        applications = mdl.application.find_by_user(request.user)
        return render(request, "home.html", {'applications': applications})
    else:
        return profile(request)


def profile(request):
    if request.method == 'POST':
        person_form = PersonForm(data=request.POST)

        person = mdl.person.find_by_user(request.user)
        person_legal_address = mdl.person_address.find_by_person_type(person, 'LEGAL')

        if person_legal_address is None:
            person_legal_address = mdl.person_address.PersonAddress()
            person_legal_address.person = person
            person_legal_address.type = 'LEGAL'

        if request.POST['last_name']:
            person.user.last_name = request.POST['last_name']
        else:
            person.user.last_name = None
        if request.POST['first_name']:
            person.user.first_name = request.POST['first_name']
        else:
            person.user.first_name = None
        if request.POST['middle_name']:
            person.middle_name = request.POST['middle_name']
        else:
            person.middle_name = None
        if request.POST['birth_date']:
            try:
                person.birth_date = datetime.strptime(request.POST['birth_date'], '%d/%m/%Y')
            except ValueError:
                person.birth_date = None
                person_form.errors['birth_date'] = "La date encodée('%s') semble incorrecte " % request.POST[
                    'birth_date']
        else:
            person.birth_date = None
        if request.POST['birth_place']:
            person.birth_place = request.POST['birth_place']
        else:
            person.birth_place = None
        if request.POST['birth_country']:
            birth_country_id = request.POST['birth_country']
            birth_country = mdl_ref.country.find_by_id(birth_country_id)
            person.birth_country = birth_country
        else:
            person.birth_country = None
        if request.POST.get('gender'):
            person.gender = request.POST['gender']
        else:
            person.gender = None
        if request.POST['civil_status']:
            person.civil_status = request.POST['civil_status']
        else:
            person.civil_status = None
        if request.POST['number_children']:
            person.number_children = request.POST['number_children']
        else:
            person.number_children = None
        if request.POST['spouse_name']:
            person.spouse_name = request.POST['spouse_name']
        else:
            person.spouse_name = None
        if request.POST['nationality']:
            country_id = request.POST['nationality']
            country = mdl_ref.country.find_by_id(country_id)
            person.nationality = country
        else:
            person.nationality = None
        if request.POST['national_id']:
            person.national_id = request.POST['national_id']
        else:
            person.national_id = None
        if request.POST['id_card_number']:
            person.id_card_number = request.POST['id_card_number']
        else:
            person.id_card_number = None
        if request.POST['passport_number']:
            person.passport_number = request.POST['passport_number']
        else:
            person.passport_number = None
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
        if request.POST['legal_adr_country']:
            country_id = request.POST['legal_adr_country']
            country = mdl_ref.country.find_by_id(country_id)
            person_legal_address.country = country
        else:
            person_legal_address.country = None
        if request.POST['same_contact_legal_addr'] == "false":
            person_contact_address = mdl.person_address.find_by_person_type(person, 'CONTACT')
            if person_contact_address is None:
                person_contact_address = mdl.person_address.PersonAddress()
                person_contact_address.person = person
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
            person.phone_mobile = request.POST['phone_mobile']
        if request.POST['phone']:
            person.phone = request.POST['phone']
        if request.POST['additional_email']:
            person.additional_email = request.POST['additional_email']

        if request.POST['previous_enrollment'] == "true":
            if request.POST['register_number']:
                person.register_number = request.POST['register_number']
            if request.POST['ucl_last_year']:
                person.ucl_last_year = request.POST['ucl_last_year']
            previous_enrollment = True
        else:
            person.register_number = None
            person.ucl_last_year = None
            previous_enrollment = False

        for key in request.POST:
            if key[0:22] == "assimilation_criteria_":
                if request.POST[key] == "true":
                    criteria_id = key[22:]
                    criteria = mdl.assimilation_criteria.find_by_id(criteria_id)
                    if criteria:
                        person_assimilation_criteria = mdl.person_assimilation_criteria.PersonAssimilationCriteria()
                        person_assimilation_criteria.criteria = criteria
                        person_assimilation_criteria.person = person
                        if person_form.is_valid():
                            person_assimilation_criteria.save()

        if person_form.is_valid():
            if person_contact_address:
                person_contact_address.save()
            person_legal_address.save()
            person.save()
            return home(request)

    else:
        person = mdl.person.find_by_user(request.user)
        person_form = PersonForm()
        if person:
            person_legal_address = mdl.person_address.find_by_person_type(person, 'LEGAL')
            person_contact_address = mdl.person_address.find_by_person_type(person, 'CONTACT')
            same_addresses = True
            if person_contact_address:
                same_addresses = False

            previous_enrollment = False
            if person.register_number or person.ucl_last_year:
                previous_enrollment = True
        else:
            return HttpResponseRedirect('/admission/logout/?next=/admission')

    countries = mdl_ref.country.find_all()
    props = mdl.properties.find_by_key('INSTITUTION')
    if props:
        institution_name = props.value
    else:
        institution_name = None

    assimilation_criteria = mdl.assimilation_criteria.find_criteria()
    person_assimilation_criteria = mdl.person_assimilation_criteria.find_by_person(person.id)

    return render(request, "profile.html", {'person': person,
                                            'person_form': person_form,
                                            'countries': countries,
                                            'assimilationCriteria': assimilation_criteria,
                                            'personAssimilationCriteria': person_assimilation_criteria,
                                            'person_legal_address': person_legal_address,
                                            'person_contact_address': person_contact_address,
                                            'same_addresses': same_addresses,
                                            'previous_enrollment': previous_enrollment,
                                            'institution': institution_name})
