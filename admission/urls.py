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
from django.conf.urls import url
from admission.views import application, common, identification, offer, level, question, option, country, curriculum, \
    education_institution, language, domain, secondary_education, accounting, upload_file
from django.contrib.auth.views import logout


urlpatterns = [
    url(r'^$', common.home, name='home'),
    url(r'^admission/$', common.home, name='admission'),

    url(r'^admission/new_password_request/$', identification.new_password_request, name='new_password_request'),
    url(r'^admission/new_password/$', identification.new_password, name='new_password'),
    url(r'^admission/new_password_form/([0-9a-z-]+)/$', identification.new_password_form, name='new_password_form'),
    url(r'^admission/set_new_password/$', identification.set_new_password, name='set_new_password'),
    url(r'^admission/user/new/$', identification.new_user, name='new_user'),
    url(r'^admission/user/([0-9]+)/mail/activation/$', identification.activation_mail, name='activation_mail'),
    url(r'^admission/user/([0-9a-z-]+)/activation/$', identification.activation, name='activation'),
    url(r'^admission/user/new/confirm/([0-9]+)/$', identification.account_confirm, name="account_confirm"),
    url(r'^admission/new_password/info/$', identification.new_password_info, name='new_password_info'),
    url(r'^admission/application/([0-9]+)/$', application.application_update, name='application_update'),
    url(r'^admission/application/diploma/save/$', secondary_education.diploma_save, name='diploma'),
    url(r'^admission/curriculum/save/$', curriculum.save, name='curriculum'),
    url(r'^admission/curriculum/update/$', curriculum.update, name='curriculum_update'),
    url(r'^admission/application/diploma/update/$', secondary_education.diploma_update, name='diploma_update'),
    url(r'^admission/offer/$', offer.offer_selection, name='offer_selection'),
    url(r'^admission/offer/save/$', application.save_application_offer, name='save_offer_selection'),
    url(r'^admission/offer/application/([0-9]+)/$', offer.selection_offer, name='selection_offer'),
    url(r'^admission/application/read/([0-9]+)/$', application.application_view, name='application_view'),

    url(r'^country/$', country.find_by_id_json),

    url(r'^levels/$', level.find_by_type),

    url(r'^login/$', identification.login_admission, name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^offers/$', offer.search),
    url(r'^offer/$', offer.find_by_id),

    url(r'^options/$', option.find_by_offer),

    url(r'^profile/$', common.profile, name='profile'),
    url(r'^profile_confirmed/$', application.profile_confirmed, name='profile_confirmed'),

    url(r'^questions/$', question.find_by_offer),

    url(r'^cities/$', education_institution.find_by_country),
    url(r'^universities/$', education_institution.find_by_city),
    url(r'^langue_recognized/$', language.is_recognized),
    url(r'^highnonuniversity/$', education_institution.find_national_by_city_type),

    url(r'^high_countries/$', education_institution.find_countries_by_type_adhoc),
    url(r'^high_cities/$', education_institution.find_by_country_type_adhoc),
    url(r'^high_institutions/$', education_institution.find_high_institution_by_city),
    url(r'^countries/$', education_institution.find_countries),
    url(r'^errors_update/$', curriculum.errors_update),
    url(r'^subdomains/$', domain.find_subdomains),
    url(r'^highnonuniversity_cities/$', education_institution.find_cities_by_country_type_adhoc),
    url(r'^institution_cities/$', education_institution.find_cities_by_type),
    url(r'^institution_postal_codes/$', education_institution.find_postal_codes_by_type),
    url(r'^institutions/$', education_institution.find_institution_by_city_postal_code_type),

    url(r'^admission/application/accounting/$', accounting.accounting, name='accounting'),
    url(r'^admission/application/accounting/update/$', accounting.accounting_update, name='accounting_update'),

    url(r'^upload/$', upload_file.upload_file, name='new_file'),
    url(r'^upload/download/(?P<pk>[0-9]+)$', upload_file.download, name='download'),

]
