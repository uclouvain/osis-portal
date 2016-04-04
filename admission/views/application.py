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
from admission import models as mdl
from reference.models import Country
from django.shortcuts import render

from admission.forms import PersonForm, PersonLegalAddressForm, PersonContactAddressForm,PersonAddressMatchingForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from datetime import datetime


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                           {"offers":      None,
                            "offer":       application.offer_year,
                            "application": application})


def profile(request):
    if request.method == 'POST':
        print('profile post')
        person = mdl.person.find_by_user(request.user)
        person_legal_address = mdl.personAddress.find_by_person_type(person,'LEGAL')
        if person_legal_address is None:
            person_legal_address = mdl.personAddress.PersonAddress()
            person_legal_address.person = person


        if request.POST['last_name']:
            person.user.last_name = request.POST['last_name']
        if request.POST['first_name']:
            person.user.first_name = request.POST['first_name']
        if request.POST['middle_name']:
            person.middle_name = request.POST['middle_name']
        if request.POST['birth_date']:
            person.birth_date = datetime.strptime(request.POST['birth_date'], '%d/%m/%Y')
        if request.POST['birth_place']:
            person.birth_place = request.POST['birth_place']
        if request.POST['birth_country']:
            birth_country_id = request.POST['birth_country']
            birth_country = Country.find_by_id(birth_country_id)
            person.birth_country = birth_country
        if request.POST['gender']:
            person.gender = request.POST['gender']
        if request.POST['civil_status']:
            person.civil_status = request.POST['civil_status']
        if request.POST['number_children']:
            person.number_children = request.POST['number_children']
        if request.POST['spouse_name']:
            person.spouse_name = request.POST['spouse_name']
        if request.POST['nationality']:
            country_id = request.POST['nationality']
            country = Country.find_by_id(country_id)
            person.nationality = country

        if request.POST['national_id']:
            person.national_id = request.POST['national_id']
        if request.POST['id_card_number']:
            person.id_card_number = request.POST['id_card_number']
        if request.POST['passport_number']:
            person.passport_number = request.POST['passport_number']

        if request.POST['legal_adr_street']:
            person_legal_address.street = request.POST['legal_adr_street']
        if request.POST['legal_adr_number']:
            person_legal_address.number = request.POST['legal_adr_number']
        if request.POST['legal_adr_complement']:
            person_legal_address.complement = request.POST['legal_adr_complement']
        if request.POST['legal_adr_postal_code']:
            person_legal_address.postal_code = request.POST['legal_adr_postal_code']
        if request.POST['legal_adr_city']:
            person_legal_address.city = request.POST['legal_adr_city']
        if request.POST['legal_adr_country']:
            country_id = request.POST['legal_adr_country']
            country = Country.find_by_id(country_id)
            person_legal_address.country = country

        if request.POST['contact_adr_street']== "on":
            pass
        else:
            person_contact_address = mdl.personAddress.find_by_person_type(person,'CONTACT')
            if person_contact_address is None:
                person_contact_address = mdl.personAddress.PersonAddress()
                person_contact_address.person = person

            if request.POST['contact_adr_street']:
                person_contact_address.street = request.POST['contact_adr_street']
            if request.POST['contact_adr_number']:
                person_contact_address.number = request.POST['contact_adr_number']
            if request.POST['contact_adr_complement']:
                person_contact_address.complement = request.POST['contact_adr_complement']
            if request.POST['contact_adr_postal_code']:
                person_contact_address.postal_code = request.POST['contact_adr_postal_code']
            if request.POST['contact_adr_city']:
                person_contact_address.city = request.POST['contact_adr_city']
            if request.POST['contact_adr_country']:
                country_id = request.POST['contact_adr_country']
                country = Country.find_by_id(country_id)
                person_contact_address.country = country
            person_contact_address.save()

        if request.POST['phone_mobile']:
            person.phone_mobile = request.POST['phone_mobile']
        if request.POST['phone']:
            person.phone = request.POST['phone']
        if request.POST['additional_email']:
            person.additional_email = request.POST['additional_email']

        if request.POST['register_number']:
            person.register_number = request.POST['register_number']
        if request.POST['ucl_last_year']:
            person.ucl_last_year = request.POST['ucl_last_year']
        person.save()

        person_legal_address.save()
        return HttpResponseRedirect(reverse('profile_confirmed')) # TMP - FOR TESTING PURPOSE


    else:
        print('profile init')
        person = mdl.person.find_by_user(request.user)
        person_legal_address = mdl.personAddress.find_by_person_type(person,'LEGAL')
        person_contact_address = mdl.personAddress.find_by_person_type(person,'CONTACT')

        person_addressMatching_form = PersonAddressMatchingForm()

    countries = Country.find_countries()
    return render(request, "profile.html", dict(person=person,
                                                person_addressMatching_form = person_addressMatching_form,
                                                countries=countries,
                                                person_legal_address=person_legal_address,
                                                person_contact_address=person_contact_address))

def profile_confirmed(request):
    return render(request, "profile_confirmed.html")