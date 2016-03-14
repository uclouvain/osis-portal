from django.shortcuts import render
from django.contrib.auth.models import User
from admission.forms import AccountForm
from admission.utils import send_mail
from random import randint
from admission import models as mdl


def home(request):
    form = AccountForm()
    number1 = randint(1,20)
    number2 = randint(1,20)
    number3 = randint(1,20)
    return render(request, "home.html",{'number1': number1,
                                        'number2': number2,
                                        'number3': number3,
                                        'form':    form})


def new_user(request):
    """
    To create a new user for the admission
    :param request:
    :return:
    """
    form = AccountForm(data=request.POST)
    number1 = request.POST['number1']
    number2 = request.POST['number2']
    number3 = request.POST['number3']

    validation = True
    if form.is_valid():
        try:
            result = int(number1) + int(number2) - int(number3)
        except:
            result = None

        if str(result) != form['verification'].value():
            validation = False
            form.errors['verification'] = "Résultat du calcul incorrect"
    else:
        validation = False
    email = form['email_new'].value()

    user = User.objects.filter(email= email)
    if user:
        form.errors['email_new_confirm'] = "Il existe déjà un compte pour cette adresse email"
        validation = False

    if validation:
        user = User.objects.create_user(form['email_new'].value(), form['email_new'].value(), form['password_new'].value())
        user.is_staff = False
        user.is_superuser = False
        user.is_active = False
        user.first_name = form['first_name_new'].value()
        user.last_name = form['last_name_new'].value()
        user.save()
        person = mdl.person.Person()
        person.user=user
        person.save()
        #send an activation email
        send_mail.send_mail_activation(request, str(person.activation_code), form['email_new'].value())
        return render(request, "confirm_account.html",{'user_id': user.id})
    else:
        number1 = randint(1, 20)
        number2 = randint(1, 20)
        number3 = randint(1, 20)
        return render(request, "home.html",
                          {'number1':     number1,
                           'number2':     number2,
                           'number3':     number3,
                           'form':        form})


def activation_mail(request, user_id):
    """
    To re-send an activation email
    :param request:
    :param user_id:
    :return:
    """
    user = User.objects.get(pk=user_id)
    person = mdl.person.find_by_user(user)
    if person:
        send_mail.send_mail_activation(request, str(person.activation_code), user.email)
        return home(request)
    else:
        return home(request)


def activation(request, activation_code):
    person = mdl.person.find_by_activation_code(activation_code)
    if person:
        user = User.objects.get(pk=person.user.id)
        if person and user:
            user.is_active = True
            user.save()
            person.activation_code = None #to avoid a dubble activation
            person.save()
            return render(request, "confirmed_account.html",{'user': user})
        else:
            return render(request, "activation_failed.html")
    else:
        return render(request, "activation_failed.html")