"""
Methods used yo create users for tests
All the environment for a student could be created
"""
from django.contrib.auth.models import Permission, Group

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import SuperUserFactory


class UserMixin:

    def create_group(self, group_name):
        return Group.objects.get_or_create(name=group_name)

    def add_permissions_to_group(self, group_name, *permissions_names):
        group = Group.objects.get(name=group_name)
        for permission_name in permissions_names:
            permission = Permission.objects.get(codename=permission_name)
            group.permissions.add(permission)

    def create_students_group(self):
        group, created = self.create_group('students')
        self.add_permissions_to_group('students', 'is_student')
        return group

    def create_tutors_group(self):
        group, created = self.create_group('tutors')
        self.add_permissions_to_group('tutors', 'is_tutor')
        self.add_permissions_to_group('tutors', 'can_access_attribution')
        return group


class StudentMixin(UserMixin):

    def create_student(self, user=None):
        """
        Create a student object with all related objects and permissions
        :return: The student
        """
        if user:
            person = PersonFactory(user=user)
        else:
            person = PersonFactory()
        student = StudentFactory(person=person)
        students_group = self.create_students_group()
        students_group.user_set.add(person.user)
        return student


class TutorMixin(UserMixin):

    def create_tutor(self, user=None):
        """
        Create a tutor object with all related objects and permissions
        :param user: related user object , if non it will be created
        :return: The tutor
        """
        if user:
            person = PersonFactory(user=user)
        else:
            person = PersonFactory()
        tutor = TutorFactory(person=person)
        tutors_group = self.create_tutors_group()
        tutors_group.user_set.add(person.user)
        return tutor


class PhdMixin(UserMixin):

    def create_phd(self, user=None):
        """
        Create a phd person object with all related objects and permissions
        :param user: related user object , if non it will be created
        :return: The phd person
        """
        if user:
            person = PersonFactory(user=user)
        else:
            person = PersonFactory()
        TutorFactory(person=person)
        StudentFactory(person=person)
        tutors_group = self.create_tutors_group()
        tutors_group.user_set.add(person.user)
        student_group = self.create_students_group()
        student_group.user_set.add(person.user)
        return person


class AdministratorMixin(UserMixin):
    def create_admin(self, user=None):
        """
        Create an administrator person object with all related objects and permissions
        :param user: related user object , if non it will be created
        :return: The phd person
        """
        if user:
            person = PersonFactory(user=user)
        else:
            super_user = SuperUserFactory()
            person = PersonFactory(user=super_user)
        return person
