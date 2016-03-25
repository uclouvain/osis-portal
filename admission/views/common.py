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
from admission.forms import NewAccountForm, AccountForm
from random import randint
from admission import models as mdl
from django.shortcuts import render


@login_required
def home(request):
    form_new = NewAccountForm()
    form = AccountForm()
    number1 = randint(1, 20)
    number2 = randint(1, 20)
    number3 = randint(1, 20)
    sum = number1 + number2
    while number3 > sum:
        number3 = randint(1, 20)

    applications = mdl.application.find_by_user(request.user)

    return render(request, "home.html", {'number1':  number1,
                                         'number2':  number2,
                                         'number3':  number3,
                                         'form_new': form_new,
                                         'form':     form,
                                         'applications': applications})
