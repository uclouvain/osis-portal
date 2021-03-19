from collections import defaultdict

from django.core.exceptions import MultipleObjectsReturned

from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.models.person import Person
from base.models.student import Student


def check_if_person_is_student(person):
    """
    Check if the person object has at least on student object linked
    """
    return Student.objects.filter(person=person).exists()


def _discriminate_student(students):
    """
    Discriminate between several student objects that belong to the same person.
    Offer enrollments with valid state enrollment are checked.
    If the most recent enrollment year has only one student, this student is returned.
    If there are more than one student for the most recent offer enrollment year, an exception is raised.
    """
    student_offer_enrollments = defaultdict(set)
    offers_enrollments = list(OfferEnrollment.objects.filter(
        student__in=students,
        enrollment_state__in=offer_enrollment_state.VALID_ENROLLMENT_STATES))

    for offer_enrollment in offers_enrollments:
        year = offer_enrollment.education_group_year.academic_year.year
        student_offer_enrollments[year].add(offer_enrollment.student)

    if student_offer_enrollments:
        max_year = max(student_offer_enrollments.keys())
        if len(student_offer_enrollments.get(max_year)) > 1:
            raise MultipleObjectsReturned
        else:
            return student_offer_enrollments.get(max_year).pop()
    else:
        return None


def find_by_user_and_discriminate(a_user):
    """
    Try to find unique Student by user.
    If there is multiple student, offer enrollments are checked to find the valid Student.
    """
    person = Person.objects.get(user=a_user)
    students = Student.objects.filter(person=person)
    count_students = len(students)
    if count_students < 1:
        return None
    elif count_students == 1:
        return students[0]
    else:
        return _discriminate_student(students)
