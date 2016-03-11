from django.shortcuts import render
from django.contrib.auth.models import User
from admission.forms import AccountForm

def home(request):
    form = AccountForm()

    return render(request, "home.html",{'number1': 19,
                                        'number2': 14,
                                        'number3': 11,
                                        'form':form})


def new_user(request):
    form = AccountForm(data=request.POST)
    # first_name = request.POST['first_name_new']
    # last_name = request.POST['last_name_new']
    # email = request.POST['email_new']
    # email_confirm = request.POST['email_new_confirm']
    # password = request.POST['password_new']
    # password_confirm = request.POST['password_new_confirm']
    # verification = request.POST['verification']
    number1 = request.POST['number1']
    number2 = request.POST['number2']
    number3 = request.POST['number3']
    #Validation
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

    if validation:
        user = User.objects.create_user(form['last_name_new'].value(), form['email_new'].value(), form['password_new'].value())
        user.is_staff = False
        user.is_superuser = False
        user.is_active = False
        user.first_name = form['first_name_new'].value()
        user.last_name = form['last_name_new'].value()
        user.save()
        return render(request, "confirm_account.html")
    else:
        return render(request, "home.html",
                          {'number1':     19,
                           'number2':     14,
                           'number3':     11,
                           'form' :       form})

def activation_mail(request):
     return render(request, "home.html",{'number1': 19,
                                        'number2': 14,
                                        'number3': 11})