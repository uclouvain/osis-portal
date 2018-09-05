import datetime
import random

from base.tests.functional.models.user_type import StudentMixin
from performance.tests.factories.student_performance import StudentPerformanceFactory


class StudentWithPerformanceMixin(StudentMixin):

    def create_student_with_valid_performances(self, user=None, count_perfs=None):
        student = self.create_student(user)
        self._create_random_perfs(student, count_perfs)
        return student

    @staticmethod
    def _create_random_perfs(student, count_perf):
        academic_year = datetime.datetime.today().year
        if not count_perf:
            count_perf = random.randint(1, 10)
        for idx in range(count_perf):
            StudentPerformanceFactory(registration_id=student.registration_id,
                                      academic_year=academic_year-idx)


