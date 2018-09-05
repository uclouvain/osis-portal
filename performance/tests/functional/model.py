from base.tests.functional.models.user_type import StudentMixin


class StudentWithPerformanceMixin(StudentMixin):

    def create_student_with_performances(self):
        student = self.create_student()

        return student

