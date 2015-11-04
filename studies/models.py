from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class AcademicYear(models.Model):
    year       = models.IntegerField()
    start_date = models.DateField()
    end_date   = models.DateField()

    def __str__(self):
        return u'%d - %d' % (self.year, self.year + 1)


class Offer(models.Model):
    title   = models.CharField(max_length = 240, blank = False, null = False)
    acronym = models.CharField(max_length = 10, blank = True, null = True)

    def __str__(self):
        return self.title


class OfferYear(models.Model):
    offer         = models.ForeignKey(Offer)
    academic_year = models.ForeignKey(AcademicYear)

    def __str__(self):
        return u'%s (%d)' % (self.offer.title, self.academic_year.year)


class Student(models.Model):
    first_name = models.CharField(max_length = 50, blank = False, null = False)
    last_name  = models.CharField(max_length = 50, blank = False, null = False)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class OfferEnrollment(models.Model):
    offer_year = models.ForeignKey(OfferYear)
    student    = models.ForeignKey(Student)

    def __str__(self):
        return u'%s' % (self.offer_year.academic_year)


class Tutor(models.Model):
    first_name = models.CharField(max_length = 50, blank = False, null = False)
    last_name  = models.CharField(max_length = 50, blank = False, null = False)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Structure(models.Model):
    name = models.CharField(max_length = 100, blank = False, null = False)


class LearningUnit(models.Model):
    title       = models.CharField(max_length = 210, blank = True, null = True)
    acronym     = models.CharField(max_length = 10, blank = True, null = True)
    description = models.TextField(blank = True, null = True)

    def __str__(self):
        return self.title


class LearningUnitYear(models.Model):
    academic_year = models.ForeignKey(AcademicYear)
    learning_unit = models.ForeignKey(LearningUnit)
    credits = models.DecimalField(max_digits=2, decimal_places=0, blank = True, null = True)

    def __str__(self):
        return u'%s %s' % (self.academic_year, self.learning_unit.acronym)


class LearningUnitEnrollment(models.Model):
    student            = models.ForeignKey(Student)
    learning_unit_year = models.ForeignKey(LearningUnitYear)

    def __str__(self):
        return u'%s - %s' % (self.student, self.learning_unit_year)


class Exam(models.Model):
    learning_unit_year = models.ForeignKey(LearningUnitYear)
    start_date         = models.DateField()
    end_date           = models.DateField()

    @property
    def session(self):
        return self.start_date.strftime("%B");

    def __str__(self):
        return u'%s - %s' % (self.start_date, self.end_date)


class ExamEnrollment(models.Model):
    exam                     = models.ForeignKey(Exam)
    learning_unit_enrollment = models.ForeignKey(LearningUnitEnrollment)
    score                    = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)


class ExamEnrollmentHistory(models.Model):
    exam_enrollment = models.ForeignKey(ExamEnrollment)
    change_date     = models.DateTimeField()


class Attribution(models.Model):
    tutor         = models.ForeignKey(Tutor)
    learning_unit = models.ForeignKey(LearningUnit)
    start_date    = models.DateField()
    end_date      = models.DateField()


class Configuration(models.Model):
    key   = models.CharField(max_length = 50, blank = False, null = False)
    value = models.CharField(max_length = 255, blank = True, null = True)

    def __str__(self):
        return self.key
