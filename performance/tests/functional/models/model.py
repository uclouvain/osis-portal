import datetime
import random

from base.tests.functional.models.user_type import StudentMixin
from performance.tests.factories.student_performance import StudentPerformanceFactory


class StudentWithPerformanceMixin(StudentMixin):

    def create_student_with_performances(self,
                                         user=None,
                                         count_perfs=None,
                                         authorized_results=True,
                                         course_registration_validated=None,
                                         learning_units_outside_catalog=None,
                                         fetch_timed_out=False):

        student = self.create_student(user)
        self.__create_random_perfs(student,
                                   count_perfs,
                                   authorized_results,
                                   course_registration_validated,
                                   learning_units_outside_catalog,
                                   fetch_timed_out)
        return student

    @staticmethod
    def __create_random_perfs(student,
                              count_perf,
                              authorized_results,
                              course_registration_validated,
                              learning_units_outside_catalog,
                              fetch_timed_out):
        academic_year = datetime.datetime.today().year
        if not count_perf:
            count_perf = random.randint(1, 10)
        for idx in range(count_perf):
            StudentPerformanceFactory(registration_id=student.registration_id,
                                      academic_year=academic_year-idx,
                                      authorized=authorized_results,
                                      courses_registration_validated=course_registration_validated,
                                      learning_units_outside_catalog=learning_units_outside_catalog)


