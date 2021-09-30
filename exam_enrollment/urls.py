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
from django.urls import include

from exam_enrollment.views.check_form import CheckForm
from exam_enrollment.views.enrollment_form import ExamEnrollmentForm
from exam_enrollment.views.offer_choice import OfferChoice

urlpatterns = [
    url(r'^$', OfferChoice.as_view(), name='exam_enrollment_offer_choice'),
    url(r'^(?P<acronym>[0-9A-Za-z_ ]+)/(?P<academic_year>[0-9]{4})/', include([
        url(r'^form/$', ExamEnrollmentForm.as_view(), name='exam_enrollment_form'),
        url(r'^check/$', CheckForm.as_view(), name='check_exam_enrollment_form'),
    ]))
]
