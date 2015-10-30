from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Offer(models.Model):
    num_offer   = models.BigIntegerField()
    acronym     = models.CharField(max_length = 5,blank = False, null = False)
    cycle       = models.DecimalField(max_digits = 1, decimal_places = 0, blank = True, null = True)
    level       = models.DecimalField(max_digits = 1, decimal_places = 0, blank = True, null = True)
    offer_type  = models.CharField(max_length = 2, blank = True, null = True)
    orientation = models.CharField(max_length = 2, blank = True, null = True)

    def __str__(self):
        return self.acronym.upper() + " " + str(self.cycle) + " " + str(self.level) + " " + self.offer_type + " " + self.orientation


class OfferYear(models.Model):
    title = models.CharField(max_length = 240, blank = True, null = True)
    offer = models.ForeignKey(Offer)

    def __str__(self):
        return self.title


class Student(models.Model):
    name                = models.CharField(max_length = 40, blank = False, null = False)
    first_name1         = models.CharField(max_length = 20, blank = False, null = False)
    registration_number = models.CharField(max_length = 10, blank = True, null = True)

    def offer_enrollments(self):
        return OfferEnrollment.objects.filter(student=self)
    def learning_unit_enrollments(self):
        return LearningUnitEnrollment.objects.filter(student=self)
    def __str__(self):
        return self.name + ' ' + self.first_name1


class AcademicYear(models.Model):
    year = models.IntegerField(validators=[
                                        MaxValueValidator(3000),
                                        MinValueValidator(1967)
                                    ]
                                 )
    def __str__(self):
        return str(self.year)


class OfferEnrollment(models.Model):
    REGISTRATION_STATE_CHOICES = (
        ('UNKNOWN','Unknown'),
        ('ERROR','Error'),
        ('CYCLE','Cycle')
    )

    offer_year         = models.ForeignKey(OfferYear)
    student            = models.ForeignKey(Student)
    academic_year      = models.ForeignKey(AcademicYear, null = True)
    registration_state = models.CharField(max_length = 10, blank = True, null = True,choices = REGISTRATION_STATE_CHOICES, default = 'UNKNOWN')

    def __str__(self):
        return self.registration_state


# class Tutor(models.Model):
# class Exam(models.Model):
# class ExamEnrollment(models.Model):

class LearningUnit(models.Model):
    acronym     = models.CharField(max_length = 5,blank = False, null = False)
    number      = models.DecimalField(max_digits = 11, decimal_places = 0, blank = True, null = True)
    title       = models.CharField(max_length = 210, blank = True, null = True)

    def __str__(self):
        return self.acronym.upper() + " " + str(self.number)


class LearningUnitYear(models.Model):
    EXAM_REGISTRATION_STATE_CHOICES = (
        ('REGISTERED', 'Registered'),
        ('MODIFIED_TEST', 'Modified test'),
        ('DELAY','Delay'),
        ('SECOND_REGISTRATION','Second registration'),
        ('SATISFYING','Satisfying'),
        ('NOT_SATISFYING','Not Satisfying'),
        ('CREDITS_DELAY','Credits delay'),
        ('EXEMPTION', 'Exemption'),
        ('JANUARY_SCORE_DELAY','January score delay'),
        ('Q_94', 'Q_94'),
        ('C_94', 'C_94'),
        ('N_94', 'N_94'),
        ('K_94', 'K_94'),
        ('TEST', 'TEST'),
        ('EXTERNAL', 'External'),
        ('INCOMPLETE','Incomplete'),
        ('*','Star'),
        ('ALL','All'),
        ('UNKNOWN','Unknown')
    )
    CREDIT_TYPE_CHOICES = (
        ('CREDIT','Credit'),
        ('DELAY','Delay'),
        ('EXEMPTION','Exemption'),
        ('Q_94','Credit before Bologne'),
        ('C_94','Delay before Bologne'),
        ('MODIFIED_TEST','Modified test'),
        ('POSTPONED','Postponed'),
        ('UNKNOWN','Unknown')
    )

    academicYear   = models.ForeignKey(AcademicYear)
    learning_unit  = models.ForeignKey(LearningUnit)
    score_1        = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    exam_state_1   = models.CharField(max_length = 10, blank = True, null = True,choices = EXAM_REGISTRATION_STATE_CHOICES, default = 'UNKNOWN')
    score_2        = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    exam_state_2   = models.CharField(max_length = 10, blank = True, null = True,choices = EXAM_REGISTRATION_STATE_CHOICES, default = 'UNKNOWN')
    score_3        = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    exam_state_3   = models.CharField(max_length = 10, blank = True, null = True,choices = EXAM_REGISTRATION_STATE_CHOICES, default = 'UNKNOWN')
    weight         = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    credit_type    = models.CharField(max_length = 10, blank = True, null = True,choices = CREDIT_TYPE_CHOICES, default = 'UNKNOWN')

    def __str__(self):
        return str(self.academicYear.year) + " " + self.learning_unit.acronym   + str(self.learning_unit.number)

class LearningUnitEnrollment(models.Model):
    student            = models.ForeignKey(Student)
    learning_unit_year = models.ForeignKey(LearningUnitYear)

    def __str__(self):
        return self.student.name + " " + str(self.learning_unit_year.academicYear)
# class Structure(models.Model):
# class Attribution(models.Model):


class Configuration(models.Model):
    key  = models.CharField(max_length = 50, blank = False, null = False)
    value = models.CharField(max_length = 255, blank = False, null = False)

    def __str__(self):
        return self.key
