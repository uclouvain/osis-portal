from typing import Optional

from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned

from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService, OfferEnrollmentBusinessException
from frontoffice.settings.osis_sdk.utils import MultipleApiBusinessException


def check_if_person_is_student(person: Person) -> bool:
    """
    Check if the person object has at least on student object linked
    """
    return Student.objects.filter(person=person).exists()


def _discriminate_student(students, person: Person) -> Optional[Student]:
    """
    Discriminate between several student objects that belong to the same person.
    It's done by OSIS API
    If there are more than one student for the most recent offer enrollment year, a DoubleNOMA status_code is sent by
    OSIS and an exception is raised.
    """

    try:
        student_offer_enrollments = OfferEnrollmentService.get_enrollments_list(
            person=person,
            global_id=str(person.global_id),
        ).results
        if student_offer_enrollments:
            registration_id = student_offer_enrollments[0].student_registration_id
            return students.get(registration_id=registration_id)
        return None
    except MultipleApiBusinessException as e:
        for i in e.exceptions:
            if i.status_code == OfferEnrollmentBusinessException.DoubleNOMA.value:
                raise MultipleObjectsReturned


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
    return _discriminate_student(students, person)
