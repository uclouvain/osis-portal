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
from exam_enrollment.views import exam_enrollment

urlpatterns = [
    url(r'^$', exam_enrollment.choose_offer, name='exam_enrollment_offer_choice'),
    url(r'^direct/$', exam_enrollment.choose_offer_direct, name='exam_enrollment_form_direct'),
    url(r'^([0-9]+)/form/$', exam_enrollment.exam_enrollment_form, name='exam_enrollment_form'),
    url(r'^check/$', exam_enrollment.check_exam_enrollment_form, name='check_exam_enrollment_form'),
]
