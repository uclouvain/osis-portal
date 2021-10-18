from collections import defaultdict
from typing import Optional, Dict, List, Set

from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned

from base.models.enums import offer_enrollment_state
from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService


def check_if_person_is_student(person: Person) -> bool:
    """
    Check if the person object has at least on student object linked
    """
    return Student.objects.filter(person=person).exists()


def _discriminate_student(students: List[Student]) -> Optional[Student]:
    """
    Discriminate between several student objects that belong to the same person.
    Offer enrollments with valid state enrollment are checked.
    If the most recent enrollment year has only one student, this student is returned.
    If there are more than one student for the most recent offer enrollment year, an exception is raised.
    """

    student_offer_enrollments = _get_student_offer_enrollments(students)
    if student_offer_enrollments:
        max_year = max(student_offer_enrollments.keys())
        if len(student_offer_enrollments.get(max_year)) > 1:
            raise MultipleObjectsReturned
        return student_offer_enrollments.get(max_year).pop()
    return None


def _get_student_offer_enrollments(students: List[Student]) -> Dict[Set]:
    student_offer_enrollments = defaultdict(set)
    for stud in students:
        offer_enrolls = OfferEnrollmentService.get_enrollments_list(
            person=stud.person,
            registration_id=str(stud.registration_id),
            enrollment_state=list(offer_enrollment_state.VALID_ENROLLMENT_STATES)
        ).results
        for offer in offer_enrolls:
            student_offer_enrollments[offer.year].add(stud)
    return student_offer_enrollments


def find_by_user_and_discriminate(a_user: User) -> Optional[Student]:
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
    return _discriminate_student(students)
