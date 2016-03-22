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
from django.conf.urls import url, include
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^admission/$', views.home, name='admission'),

    url(r'^login/$', views.osis_login,  name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^admission/new_password_request/$', views.new_password_request, name='new_password_request'),
    url(r'^admission/new_password/$', views.new_password, name='new_password'),
    url(r'^admission/new_password_form/([0-9a-z-]+)/$', views.new_password_form, name='new_password_form'),
    url(r'^admission/set_new_password/$', views.set_new_password, name='set_new_password'),
    url(r'^admission/user/new/$', views.new_user, name='new_user'),
    url(r'^admission/user/([0-9]+)/mail/activation/$', views.activation_mail, name='activation_mail'),
    url(r'^admission/user/([0-9a-z-]+)/activation/$', views.activation, name='activation'),
    url(r'^admission/user/new/confirm/([0-9]+)/$', views.account_confirm, name="account_confirm"),
    url(r'^admission/new_password/info/$', views.new_password_info, name='new_password_info'),
    url(r'^admission/application/([0-9]+)/$', views.application_update, name='application_update'),

    url(r'^admission/offer/$', views.offer_selection, name='offer_selection'),
    url(r'^admission/offer/search/$', views.refresh_offer_selection, name='refresh_offer_selection'),
    url(r'^admission/offer/save/$', views.save_offer_selection, name='save_offer_selection'),
    url(r'^admission/offer/application/([0-9]+)/$', views.selection_offer, name='selection_offer'),



]