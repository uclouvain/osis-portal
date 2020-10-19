from base.models.student import Student


def check_if_person_is_student(person):
    """
    Check if the person object has one or more student objetc linked
    :param person:
    :return: True if the person has at least one student object
    """
    return Student.objects.filter(person=person).exists()
