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
from django.shortcuts import render, get_object_or_404

from admission.forms import PersonForm

from datetime import datetime
from admission.views import common


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                           {"offers":      None,
                            "offer":       application.offer_year,
                            "application": application})


def profile(request):

    if request.method == 'POST':
        person_form = PersonForm(data=request.POST)

        person = mdl.person.find_by_user(request.user)
        person_legal_address = mdl.person_address.find_by_person_type(person,'LEGAL')

        if person_legal_address is None:
            person_legal_address = mdl.person_address.PersonAddress()
            person_legal_address.person = person
            person_legal_address.type='LEGAL'

        if request.POST['last_name']:
            person.user.last_name = request.POST['last_name']
        if request.POST['first_name']:
            person.user.first_name = request.POST['first_name']
        if request.POST['middle_name']:
            person.middle_name = request.POST['middle_name']
        if request.POST['birth_date']:
            try:
                person.birth_date = datetime.strptime(request.POST['birth_date'], '%d/%m/%Y')
            except:
                person.birth_date = None
                person_form.errors['birth_date'] = "La date encodée('%s') semble incorrecte " % request.POST['birth_date']

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

        if request.POST['same_contact_legal_addr'] == "false":
            person_contact_address = mdl.person_address.find_by_person_type(person,'CONTACT')
            if person_contact_address is None:
                person_contact_address = mdl.person_address.PersonAddress()
                person_contact_address.person = person
                person_contact_address.type='CONTACT'

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
            previous_enrollment=True
        else:
            person.register_number = None
            person.ucl_last_year = None
            previous_enrollment=False

        if person_form.is_valid():
            if person_contact_address:
                person_contact_address.save()
            person_legal_address.save()
            person.save()

            return common.home(request)

    else:
        person = mdl.person.find_by_user(request.user)
        person_legal_address = mdl.person_address.find_by_person_type(person,'LEGAL')
        person_contact_address = mdl.person_address.find_by_person_type(person,'CONTACT')
        same_addresses = True
        if person_contact_address:
            same_addresses=False
        person_form = PersonForm()

        previous_enrollment = False
        if person.register_number or person.ucl_last_year:
            previous_enrollment = True

    countries = Country.find_countries()
    return render(request, "profile.html", dict(person=person,
                                                person_form=person_form,
                                                countries=countries,
                                                person_legal_address=person_legal_address,
                                                person_contact_address=person_contact_address,
                                                same_addresses=same_addresses,
                                                previous_enrollment=previous_enrollment))


def profile_confirmed(request):
    return render(request, "profile_confirmed.html")


def save_application_offer(request):
    if request.method == 'POST' and 'save' in request.POST:
        offer_year = None
        offer_year_id = request.POST.get('offer_year_id')

        application_id = request.POST.get('application_id')
        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
        else:
            application = mdl.application.Application()
            person_application = mdl.person.find_by_user(request.user)
            application.person = person_application

        if offer_year_id:
            offer_year = mdl.offer_year.find_by_id(offer_year_id)
            if offer_year.grade_type:
                if offer_year.grade_type.grade == 'DOCTORATE':
                    application.doctorate = True
                else:
                    application.doctorate = False

        application.offer_year = offer_year
        application.save()
        # answer_question_
        for key, value in request.POST.items():
            if "txt_answer_question_" in key:
                answer = mdl.answer.Answer()
                answer.application = application
                answer.value = value
                # as it's txt_answer we know that it's there is only one option available,
                # (SHORT_INPUT_TEXT, LONG_INPUT_TEXT)
                option_id = key.replace("txt_answer_question_", "")
                answer.option = mdl.option.find_by_id(int(option_id))
                answer.save()
            else:
                if "txt_answer_radio_chck_optid_" in key:

                    # RADIO_BUTTON
                    if "on" == value:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option_id = key.replace("txt_answer_radio_chck_optid_", "")
                        option = mdl.option.find_by_id(int(option_id))
                        answer.option = option
                        answer.value = option.value
                        answer.save()
                else:
                    if "slt_question_" in key:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option = mdl.option.find_by_id(value)
                        answer.option = option
                        answer.value = option.value
                        answer.save()

        return render(request, "diploma.html", {"application": application})


def application_view(request, application_id):
    application = mdl.application.find_by_id(application_id)
    answers = mdl.answer.find_by_application(application_id)
    return render(request, "application.html",
                           {"application": application,
                            "answers": answers})
