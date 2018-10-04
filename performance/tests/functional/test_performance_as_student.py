from osis_common.tests.functional.models.model import FunctionalTestCase
from osis_common.tests.functional.models.report import can_be_reported
from performance.models import student_performance
from performance.tests.functional.models.model import StudentWithPerformanceMixin


class CommonStudentPerformancesTestCase(FunctionalTestCase, StudentWithPerformanceMixin):

    def setUp(self):
        super(CommonStudentPerformancesTestCase, self).setUp()
        self.student_without_perfs = self.create_student()
        self.student_with_valid_perfs = self.create_student_with_performances()

    @classmethod
    def setUpClass(cls):
        super(CommonStudentPerformancesTestCase, cls).setUpClass()
        cls.perf_config = cls.config.get('PERFORMANCE')

    @can_be_reported
    def test_access_performance_page(self):
        """
        As a student I can access my exam marks page
        """
        self.login(self.student_without_perfs.person.user.username)
        self.__got_to_perfomance_page()
        self.check_page_title(self.perf_config.get('PAGE_TITLE'))

    @can_be_reported
    def test_student_without_performances(self):
        """
        As a student
         Without any performance results
          When i go to to "my exam marks page"
           - I should see a message "No results yet"
        """
        self.login(self.student_without_perfs.person.user.username)
        self.__got_to_perfomance_page()
        string = self.get_localized_message('dont_have_the_score_yet', self.student_without_perfs.person.language)
        self.check_page_contains_string(string)

    @can_be_reported
    def test_student_with_performances(self):
        """
        As a student
         With performances results
          When i go to to "my exam marks page"
           - I should see a legal announcement
           - I should see the list of my registered offer
          When i click on an offer in the previous list
           - I should see my exam marks for this offer
           - I should see all the common messages
        """
        self.login(self.student_with_valid_perfs.person.user.username)
        self.__got_to_perfomance_page()
        string = self.get_localized_message('performance_results_general_legal_announcement',
                                            self.student_with_valid_perfs.person.language)
        self.check_page_contains_string(string)
        perfs = student_performance.search(registration_id=self.student_with_valid_perfs.registration_id)
        perf_lnk_pattern = self.perf_config.get('EXAM_MARK_LINKS_PATTERN')
        self.check_page_contains_ids([perf_lnk_pattern.format(p.pk) for p in perfs])
        self.click_element_by_id(perf_lnk_pattern.format(perfs[0].pk))
        self.check_page_title(self.config.get('PERFORMANCE').get('EXAM_MARK').get('PAGE_TITLE'))
        self.__check_common_messages(self.student_with_valid_perfs.person.language)

    def __check_common_messages(self, language):
        self.check_page_contains_string(self.get_localized_message('performance_result_note_legal_announcement',
                                                                   language))
        self.check_page_contains_string(self.get_localized_message('text_mean_exprimed_for_20', language))
        self.check_page_contains_string(self.get_localized_message('legend', language))
        self.check_page_contains_string(self.get_localized_message('cycle_advancement_explanations', language))
        self.check_page_contains_ids(['paragraph_mention_explanation'])

    def __got_to_perfomance_page(self):
        self.open_url_by_name('home')
        self.click_element_by_id(self.config.get('PERFORMANCE').get('FROM_DASH_LINK'))


class SpecificExamMarksMessagesTestCase(FunctionalTestCase, StudentWithPerformanceMixin):

    @classmethod
    def setUpClass(cls):
        super(SpecificExamMarksMessagesTestCase, cls).setUpClass()
        cls.perf_config = cls.config.get('PERFORMANCE')

    @can_be_reported
    def test_authorized_results(self):
        """
        As a student
         If my results marks are authorized by my faculty
          When I got to "my marks for an offer" page
          - I should not see the "not authorized" message
        """
        student = self.create_student_with_performances(count_perfs=1)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        student_perf = student_performance.search(registration_id=student.registration_id)[0]
        message = self.get_localized_message('performance_result_note_not_autorized', student.person.language). \
            format(self.get_localized_message(student_perf.session_locked, student.person.language))
        self.check_page_not_contains_string(message)

    @can_be_reported
    def test_not_authorized_results(self):
        """
        As a student
         If my results marks are not authorized by my faculty
          When I got to "my marks for an offer" page
          - I should see the "not authorized" message
        """
        student = self.create_student_with_performances(count_perfs=1, authorized_results=False)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        student_perf = student_performance.search(registration_id=student.registration_id)[0]
        message = self.get_localized_message('performance_result_note_not_autorized', student.person.language).\
            format(self.get_localized_message(student_perf.session_locked, student.person.language))
        self.check_page_contains_string(message)

    @can_be_reported
    def test_courses_registration_not_validated(self):
        """
        As a student:
         If my course registration is not validated yet by my faculty
          When I got to "my marks for an offer" page
          - I should see a "course registration not validated yet" message
        """
        student = self.create_student_with_performances(count_perfs=1, course_registration_validated=False)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        self.check_page_contains_string(self.get_localized_message('courses_registration_not_validated',
                                                                   student.person.language))

    @can_be_reported
    def test_courses_registration_validated(self):
        """
        As a student:
         If my courses registration is validated by my faculty
          When I got to "my marks for an offer" page
          - I should see a "course registration validated" message
        """
        student = self.create_student_with_performances(count_perfs=1, course_registration_validated=True)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        self.check_page_contains_string(self.get_localized_message('courses_registration_validated',
                                                                       student.person.language))

    @can_be_reported
    def test_courses_registration_None(self):
        """
        As a student:
         If the courses registration state is not available
          When I got to "my marks for an offer" page
          - I should not see any message about courses registration validity
        """
        student = self.create_student_with_performances(count_perfs=1, course_registration_validated=None)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        self.check_page_not_contains_string(self.get_localized_message('courses_registration_validated',
                                                                       student.person.language))
        self.check_page_not_contains_string(self.get_localized_message('courses_registration_not_validated',
                                                                       student.person.language))

    @can_be_reported
    def test_outside_catalog_lu(self):
        """
        As a student
         If some of the learning units i'm registered to are outside of the catalog
          When I got to "my marks for an offer" page
          - I should see a "outside of catalog learning units" message
        """
        student = self.create_student_with_performances(count_perfs=1, learning_units_outside_catalog=True)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        self.check_page_contains_string(self.get_localized_message('learning_unitys_outside_catalog',
                                                                   student.person.language))

    @can_be_reported
    def test_inside_catalog_lu(self):
        """
        As a student
         If none of the learning units i'm registered to are outside of the catalog
          When I got to "my marks for an offer" page
          - I should not see a "outside of catalog learning units" message
        """
        student = self.create_student_with_performances(count_perfs=1, learning_units_outside_catalog=False)
        self.login(student.person.user.username)
        self.__go_to_first_exam_marks_page(student)
        self.check_page_not_contains_string(self.get_localized_message('learning_unitys_outside_catalog',
                                                                       student.person.language))

    def __go_to_first_exam_marks_page(self, student):
        perf = student_performance.search(registration_id=student.registration_id)[0]
        self.open_url_by_name('performance_student_result', {'pk': perf.pk})

