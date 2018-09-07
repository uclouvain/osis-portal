from datetime import datetime

from django.contrib.admin import ModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models.academic_year import current_academic_years
from base.models.enums import entity_type


class AdmissionAdmin(ModelAdmin):
    list_display = ('last_name', 'first_name','country','formation', 'program_code')

class Admission(models.Model):

    CONTINUING_EDUCATION_TYPE = 8

    GENDER_CHOICES = (
        ('F', _('female')),
        ('M', _('male')),
    )

    STATUS_CHOICES = (
        ('EMPLOYEE', _('employee')),
        ('SELF_EMPLOYED', _('self_employed')),
        ('JOB_SEEKER', _('job_seeker')),
        ('PUBLIC_SERVANT', _('public_servant')),
        ('OTHER', _('other')),
    )

    SECTOR_CHOICES = (
        ('PRIVATE', _('private')),
        ('PUBLIC', _('public')),
        ('ASSOCIATIVE', _('associative')),
        ('HEALTH', _('health')),
        ('OTHER', _('other')),
    )

    REGISTRATION_TITLE_CHOICES = (
        ('PRIVATE', _('private')),
        ('PROFESSIONAL', _('professional')),
    )

    MARITAL_STATUS_CHOICES = (
        ('SINGLE', _('single')),
        ('MARRIED', _('married')),
        ('WIDOWED', _('widowed')),
        ('DIVORCED', _('divorced')),
        ('SEPARATED', _('separated')),
        ('LEGAL_COHABITANT', _('legal_cohabitant')),
    )

    STATE_CHOICES = (
        ('accepted', _('accepted')),
        ('rejected', _('rejected')),
        ('waiting', _('waiting')),
    )

    #Identification
    first_name = models.CharField(max_length=50, blank=True, db_index=True)
    last_name = models.CharField(max_length=50, blank=True, db_index=True)
    birth_date = models.DateField(blank=True, default=datetime.now)
    birth_location =  models.CharField(max_length=255, blank=True)
    birth_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='birth_country')
    citizenship = models.ForeignKey('reference.Country', blank=True, null=True, related_name='citizenship')
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES, default='F')

    #Contact
    phone_mobile = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=255, blank=True)

    #Address
    location = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='address_country')

    #Education
    high_school_diploma = models.BooleanField(default=False)
    high_school_graduation_year = models.DateField(blank=True, default=datetime.now)
    last_degree_level = models.CharField(max_length=50, blank=True)
    last_degree_field = models.CharField(max_length=50, blank=True)
    last_degree_institution = models.CharField(max_length=50, blank=True)
    last_degree_graduation_year = models.DateField(blank=True, default=datetime.now)
    other_educational_background = models.TextField(blank=True)

    #Professional Background
    professional_status = models.CharField(max_length=50, blank=True, choices=STATUS_CHOICES)
    current_occupation = models.CharField(max_length=50, blank=True)
    current_employer = models.CharField(max_length=50, blank=True)
    activity_sector = models.CharField(max_length=50, blank=True, choices=SECTOR_CHOICES)
    past_professional_activities = models.TextField(blank=True)

    #Motivation
    motivation = models.TextField(blank=True)
    professional_impact = models.TextField(blank=True)

    #Formation
    formation = models.ForeignKey('base.OfferYear', blank=True, null=True)
    courses_formula = models.CharField(max_length=50, blank=True)
    program_code = models.CharField(max_length=50, blank=True)
    faculty = models.ForeignKey('base.EntityVersion', blank=True, null=True)
    formation_administrator = models.CharField(max_length=50, blank=True)

    #Awareness
    awareness_ucl_website = models.BooleanField(default=False)
    awareness_formation_website = models.BooleanField(default=False)
    awareness_press = models.BooleanField(default=False)
    awareness_facebook = models.BooleanField(default=False)
    awareness_linkedin = models.BooleanField(default=False)
    awareness_customized_mail = models.BooleanField(default=False)
    awareness_emailing = models.BooleanField(default=False)

    #State
    state = models.CharField(max_length=50, blank=True,  choices=STATE_CHOICES)

    #Billing
    registration_type = models.CharField(max_length=50, blank=True, choices=REGISTRATION_TITLE_CHOICES)
    use_address_for_billing = models.BooleanField(default=False)
    billing_location = models.CharField(max_length=255, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='billing_country')
    head_office_name = models.CharField(max_length=255, blank=True)
    company_number = models.CharField(max_length=255, blank=True)
    vat_number = models.CharField(max_length=255, blank=True)

    #Registration
    national_registry_number = models.CharField(max_length=255, blank=True)
    id_card_number = models.CharField(max_length=255, blank=True)
    passport_number = models.CharField(max_length=255, blank=True)
    marital_status = models.CharField(max_length=255, blank=True, choices=MARITAL_STATUS_CHOICES)
    spouse_name = models.CharField(max_length=255, blank=True)
    children_number = models.SmallIntegerField(blank=True, default=0)
    previous_ucl_registration = models.BooleanField(default=False)
    previous_noma = models.CharField(max_length=255, blank=True)

    #Post
    use_address_for_post = models.BooleanField(default=False)
    residence_location = models.CharField(max_length=255, blank=True)
    residence_postal_code = models.CharField(max_length=20, blank=True)
    residence_city = models.CharField(max_length=255, blank=True)
    residence_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='residence_country')
    residence_phone = models.CharField(max_length=30, blank=True)

    #Student Sheet
    registration_complete = models.BooleanField(default=False)
    noma = models.CharField(max_length=255, blank=True)
    payment_complete = models.BooleanField(default=False)
    formation_spreading = models.BooleanField(default=False)
    prior_experience_validation = models.BooleanField(default=False)
    assessment_presented = models.BooleanField(default=False)
    assessment_succeeded = models.BooleanField(default=False)
    #ajouter dates sessions cours suivies
    sessions = models.CharField(max_length=255, blank=True)

def find_by_id(a_id):
    try:
        return Admission.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return None

#à modifier lors du lien avec une table student
def find_by_student(first_name, last_name):
        return Admission.objects.filter(first_name=first_name, last_name=last_name)