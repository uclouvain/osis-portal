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
import uuid
from random import randint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from admission import models as mdl
from reference import models as reference_mdl
from admission.forms import NewAccountForm, AccountForm, NewPasswordForm
from admission.utils import send_mail


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
                                         'applications' : applications })


def home_error(request, message,form):
    form_new = NewAccountForm()
    number1 = randint(1, 20)
    number2 = randint(1, 20)
    number3 = randint(1, 20)
    sum = number1 + number2
    while number3 > sum:
        number3 = randint(1, 20)
    return render(request, "home.html", {'number1':  number1,
                                         'number2':  number2,
                                         'number3':  number3,
                                         'form_new': form_new,
                                         'form':     form,
                                         'message': message})


def new_user(request):
    """
    To create a new user for the admission
    :param request:
    :return:
    """
    form_new = NewAccountForm(data=request.POST)
    number1 = request.POST['number1']
    number2 = request.POST['number2']
    number3 = request.POST['number3']

    validation = True
    if form_new.is_valid():
        try:
            result = int(number1) + int(number2) - int(number3)
        except:
            result = None

        if str(result) != form_new['verification'].value():
            validation = False
            form_new.errors['verification'] = "Résultat du calcul incorrect"
    else:
        validation = False
    email = form_new['email_new'].value()

    user = User.objects.filter(email=email)
    if user:
        form_new.errors['email_new_confirm'] = "Il existe déjà un compte pour cette adresse email %s" % email
        validation = False

    if validation:
        user = User.objects.create_user(form_new['email_new'].value(),
                                        form_new['email_new'].value(),
                                        form_new['password_new'].value())
        user.is_staff = False
        user.is_superuser = False
        user.is_active = False
        user.first_name = form_new['first_name_new'].value()
        user.last_name = form_new['last_name_new'].value()
        user.save()
        applicant = mdl.applicant.Applicant()
        applicant.user=user
        applicant.save()
        # send an activation email
        send_mail.send_mail_activation(request, str(applicant.activation_code), form_new['email_new'].value())
        user_id = user.id
        return HttpResponseRedirect(reverse('account_confirm',  args=(user_id,)))
    else:


        extra_context = {}
        extra_context['form_new'] = form_new
        number1 = randint(1, 20)
        extra_context['number1'] = number1
        number2 = randint(1, 20)
        extra_context['number2'] = number2
        sum = number1 + number2
        number3 = randint(1, 20)
        while number3 > sum:
            number3 = randint(1, 20)
        extra_context['number3'] = number3
        return login(request,  extra_context=extra_context)

def activation_mail(request, user_id):
    """
    To re-send an activation email
    :param request:
    :param user_id:
    :return:
    """
    if request.method == "POST":
        user = User.objects.get(pk=user_id)
        applicant = mdl.applicant.find_by_user(user)
        if applicant:
            send_mail.send_mail_activation(request, str(applicant.activation_code), user.email)
            return HttpResponseRedirect(reverse('admission'))
        else:
            return HttpResponseRedirect(reverse('admission'))
    return HttpResponseRedirect(reverse('admission'))


def activation(request, activation_code):
    applicant = mdl.applicant.find_by_activation_code(activation_code)
    if applicant:
        user = User.objects.get(pk=applicant.user.id)
        if applicant and user:
            user.is_active = True
            user.save()
            # to avoid a double activation
            applicant.activation_code = None
            applicant.save()
            return render(request, "confirmed_account.html", {'user': user})
        else:
            return render(request, "activation_failed.html")
    else:
        return render(request, "activation_failed.html")


def new_password_request(request):
    form = AccountForm()
    return render(request, "new_password.html",{'form':form})


def new_password(request):
    form = AccountForm(data=request.POST)
    email = form['email'].value()

    try:
        user = User.objects.get(username=email)
        if user:
            applicant = mdl.applicant.find_by_user(user)
            if not user.is_active:
                message = "Votre compte n\'a pas encore été activé"
                return render(request, "new_password.html", {'message': message, 'form':form})
            else:
                applicant.activation_code = uuid.uuid4()
                applicant.save()
                send_mail.new_password(request, str(applicant.activation_code), user.email)
                return HttpResponseRedirect(reverse('new_password_info'))
        else:
            message = "L'adresse email encodée ne correspond à aucun utilisateur"
            return render(request, "new_password.html", {'message': message, 'form':form})
    except:
        message = "L'adresse email encodée ne correspond à aucun utilisateur"
        return render(request, "new_password.html", {'message': message,'form':form })


def new_password_form(request, code):
    form = NewPasswordForm()
    applicant = mdl.applicant.find_by_activation_code(code)
    if applicant:
        return render(request, "new_password_form.html",{'form':   form,
                                                         'applicant_id': applicant.id})
    else:
        return render(request, "new_password_form.html",{'form':   form,
                                                         'applicant_id': None})


def set_new_password(request):
    applicant_id = request.POST['applicant_id']
    applicant = mdl.applicant.find_by_id(applicant_id)
    form = NewPasswordForm(data=request.POST)
    if form.is_valid():
        if applicant:
            if applicant.user:
                user = applicant.user
                user.set_password(form['password_new'].value())
                user.save()
            applicant.activation_code=None
            applicant.save()
            return render(request, "new_password_confirmed.html")
    else:
        return render(request, "new_password_form.html",{'form':   form,
                                                         'applicant_id': applicant_id})


def account_confirm(request,user_id):
    return render(request, "confirm_account.html", {'user':user_id})


def new_password_info(request):
    return render(request, "new_password_info.html")


def offer_selection(request):
    offers = None
    application = mdl.application.find_by_user(request.user)
    return render(request, "offer_selection.html",
                          {"gradetypes":  reference_mdl.grade_type.find_all(),
                           "domains":     mdl.domain.find_all(),
                           "offers":      offers,
                           "offer":       None,
                           "application": application})


def refresh_offer_selection(request):
    offer_type=None
    if request.POST.get('bachelor_type'):
        offer_type = request.POST['bachelor_type']
    if request.POST.get('master_type'):
        offer_type = request.POST['master_type']
    if request.POST.get('doctorate_type'):
        offer_type = request.POST['doctorate_type']

    domain_id = request.POST.get('domain')
    domain = get_object_or_404(mdl.domain.Domain, pk=domain_id)
    offers = mdl.offer_year.find_by_domain_grade(domain, offer_type)
    grade = get_object_or_404(reference_mdl.grade_type.GradeType, pk=offer_type)
    return render(request, "offer_selection.html",
                          {"gradetypes":  reference_mdl.grade_type.find_all(),
                           "domains":     mdl.domain.find_all(),
                           "offers":      offers,
                           "offer_type":  grade,
                           "domain":      domain})


def _get_offer_type(request):
    offer_type=None

    if request.POST.get('bachelor_type'):
        offer_type = request.POST['bachelor_type']
    if request.POST.get('master_type'):
        offer_type = request.POST['master_type']
    if request.POST.get('doctorate_type'):
        offer_type = request.POST['doctorate_type']
    if offer_type:
        return get_object_or_404(reference_mdl.grade_type.GradeType, pk=offer_type)
    return None


def _get_domain(request):
    domain_id = request.POST.get('domain')
    domain = None
    if domain_id:
        domain = get_object_or_404(mdl.domain.Domain, pk=domain_id)
    return domain


def save_offer_selection(request):

    if request.method=='POST' and 'save_down' in request.POST:
        offer_year = None

        offer_year_id = request.POST.get('offer_year_id')

        application_id = request.POST.get('application_id')
        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
        else:
            application = mdl.application.Application()
            applicant = mdl.applicant.find_by_user(request.user)
            application.applicant = applicant

        if offer_year_id:
            offer_year = mdl.offer_year.find_by_id(offer_year_id)

        application.offer_year = offer_year
        application.save()

    return render(request, "offer_selection.html",
                          {"gradetypes":  reference_mdl.grade_type.find_all(),
                           "domains":     mdl.domain.find_all(),
                           "offers":      None,
                           "offer_type":  None,
                           "domain":      mdl})


def selection_offer(request, offer_id):
    offer_year = get_object_or_404(mdl.offer_year.OfferYear, pk=offer_id)
    grade = _get_offer_type(request)
    domain = _get_domain(request)


    return render(request, "offer_selection.html",
                          {"gradetypes":  reference_mdl.grade_type.find_all(),
                           "domains":     mdl.domain.find_all(),
                           "offers":      None,
                           "offer":       offer_year,
                           "offer_type":  grade,
                           "domain":      domain})


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                          {"offers":      None,
                           "offer":       application.offer_year,
                           "application": application})


def osis_login(request, *args, **kwargs):
    extra_context = {}
    extra_context['form_new'] = NewAccountForm()
    number1 = randint(1, 20)
    extra_context['number1'] = number1
    number2 = randint(1, 20)
    extra_context['number2'] = number2
    sum = number1 + number2
    number3 = randint(1, 20)
    while number3 > sum:
        number3 = randint(1, 20)
    extra_context['number3'] = number3
    return login(request, *args, extra_context=extra_context, **kwargs)


def osis_login_error(request, *args, **kwargs):
    extra_context = {}
    form_new = NewAccountForm()
    form_new.errors['email_new_confirm'] = "Il existe déjà un compte pour cette adresse email"
    extra_context['form_new'] = form_new
    number1 = randint(1, 20)
    extra_context['number1'] = number1
    number2 = randint(1, 20)
    extra_context['number2'] = number2
    sum = number1 + number2
    number3 = randint(1, 20)
    while number3 > sum:
        number3 = randint(1, 20)
    extra_context['number3'] = number3
    return login(request, *args, extra_context=extra_context, **kwargs)
