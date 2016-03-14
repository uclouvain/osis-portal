import uuid
from uuid import UUID
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class PersonAdmin(admin.ModelAdmin):
    list_display = ('activation_code', 'user')


class Person(models.Model):
    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    user            = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)


def find_by_user(user):
    try:
        person = Person.objects.get(user=user)
    except:
        return None
    return person


def find_by_activation_code(activation_code):
    if validate_uuid4(activation_code):
        try:
            return Person.objects.filter(activation_code=activation_code).first()
        except:
            return None
    else:
        return None


def validate_uuid4(uuid_string):
    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False


    return True


def find_by_id(id):
    try:
        return Person.objects.get(pk=id)
    except:
        return None