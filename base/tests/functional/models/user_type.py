"""
Methods used yo create users for tests
All the environment for a student could be created
"""
from django.contrib.auth.models import Permission, Group

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory


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


