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

    @staticmethod
    def create_group(group_name):
        return Group.objects.get_or_create(name=group_name)

    @staticmethod
    def add_permissions_to_group(group_name, *permissions_names):
        group = Group.objects.get(name=group_name)
        for permission_name in permissions_names:
            permission = Permission.objects.get(codename=permission_name)
            group.permissions.add(permission)


class StudentMixin(UserMixin):
    def create_students_group(self):
        group, created = self.create_group('students')
        self.add_permissions_to_group('students', 'is_student')
        return group

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
    def create_tutors_group(self):
        group, created = self.create_group('tutors')
        self.add_permissions_to_group('tutors', 'is_tutor')
        self.add_permissions_to_group('tutors', 'can_access_attribution')
        return group

    def create_tutor(self, user=None):
        """
        Create a tutor object with all related objects and permissions
        :param user: related user object , if none it will be created
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


class PhdMixin(StudentMixin, TutorMixin):
    def create_phd(self, user=None):
        """
        Create a phd person object with all related objects and permissions
        :param user: related user object , if none it will be created
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
        :param user: related user object , if none it will be created
        :return: The administrator
        """
        if user:
            person = PersonFactory(user=user)
        else:
            super_user = SuperUserFactory()
            person = PersonFactory(user=super_user)
        return person


class FacAdministratorMixin(UserMixin):
    def create_faculty_administrators_group(self):
        group, created = self.create_group('faculty_administrators')
        self.add_permissions_to_group('faculty_administrators', 'is_faculty_administrator')
        self.add_permissions_to_group('faculty_administrators', 'can_access_administration')
        return group

    def create_fac_admin(self, user=None):
        """
        Create a fac administrator person with all related objects and permissions
        :param user: related user object , if none it will be created
        :return: The fac administrator person
        """
        if user:
            person = PersonFactory(user=user)
        else:
            person = PersonFactory()
        faculty_admin_group = self.create_faculty_administrators_group()
        faculty_admin_group.user_set.add(person.user)
        return person
