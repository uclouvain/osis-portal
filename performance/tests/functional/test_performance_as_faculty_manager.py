from base.tests.functional.models.user_type import FacAdministratorMixin, StudentMixin
from osis_common.tests.functional.models.model import FunctionalTestCase
from osis_common.tests.functional.models.report import can_be_reported
from performance.models import student_performance
from performance.tests.functional.models.model import StudentWithPerformanceMixin


class FacultyAdministratorsPerformanceTestCase(FunctionalTestCase, FacAdministratorMixin, StudentWithPerformanceMixin, StudentMixin):
    """
    Performance application testing as a Faculty Administrator
    """

    def setUp(self):
        super(FacultyAdministratorsPerformanceTestCase, self).setUp()
        self.student_with_valid_perfs = self.create_student_with_performances()
        self.faculty_administrator = self.create_fac_admin()
        self.student_with_no_valid_perfs = self.create_student()

    @classmethod
    def setUpClass(cls):
        super(FacultyAdministratorsPerformanceTestCase, cls).setUpClass()
        cls.perf_config = cls.config.get('PERFORMANCE')

    @can_be_reported
    def test_got_to_exam_marks_admin_page(self):
        """
        As a Faculty Administrator
        When i go to the "Faculty Administration" page
        If i click on the "Exam Marks faculty administration" link
        - I should be able to access the "ExamMarks faculty administration" page
        """
        self.login(self.faculty_administrator.user.username)
        self.__got_to_performance_administration_page()
        self.check_page_title('Exam Marks Faculty Administration')

    @can_be_reported
    def test_search_student_with_valid_results(self):
        """
        As a Faculty Administrator
        When i go to the "Exam Marks Faculty Administration" page
        With the registration id of a student with valid exam marks
        - I should be able to search for his exam marks
        - I should see the programs list of the student i looked for
        """
        self.login(self.faculty_administrator.user.username)
        self.__got_to_performance_administration_page()
        self.__search_student_programs(self.student_with_valid_perfs.registration_id)
        self.check_page_title(self.perf_config.get('PAGE_TITLE'))
        perfs = student_performance.search(registration_id=self.student_with_valid_perfs.registration_id)
        perf_lnk_pattern = self.perf_config.get('EXAM_MARK_LINKS_PATTERN')
        self.check_page_contains_ids([perf_lnk_pattern.format(p.pk) for p in perfs])

    @can_be_reported
    def test_search_student_with_no_valid_results(self):
        """
        As a Faculty Administrator
        When i go to the "Exam Marks Faculty Administration" page
        With the registration id of a student with no valid exam marks
        - I should be able to search for his exam marks
        - I should see a 'No exam marks available yet' message
        """
        self.login(self.faculty_administrator.user.username)
        self.__got_to_performance_administration_page()
        self.__search_student_programs(self.student_with_no_valid_perfs.registration_id)
        self.check_page_contains_string(self.get_localized_message('dont_have_the_score_yet',
                                                                   self.faculty_administrator.language))

    @can_be_reported
    def test_search_student_no_valid_registration_id(self):
        """
        As a Faculty Administrator
        When i go to the "Exam Marks Faculty Administration" page
        With an non valid registration id
        - I should be able to search for his exam marks
        - I should see a 'No student with this registration id' message
        """
        self.login(self.faculty_administrator.user.username)
        self.__got_to_performance_administration_page()
        self.__search_student_programs(-1)
        self.check_page_contains_string(self.get_localized_message('no_student_with_this_registration_id',
                                                                   self.faculty_administrator.language))

    @can_be_reported
    def test_look_at_student_results(self):
        """
        As a Faculty Administrator
        If I click on a program acronym from the results of the search page
        - I should see the exam marks of the student for this program
        """
        self.login(self.faculty_administrator.user.username)
        self.__got_to_performance_administration_page()
        self.__search_student_programs(self.student_with_valid_perfs.registration_id)
        self.click_element_by_id(self.__get_first_program_link_id(self.student_with_valid_perfs))
        self.check_page_title(self.config.get('PERFORMANCE').get('EXAM_MARK').get('PAGE_TITLE'))

    def __search_student_programs(self, registration_id):
        self.fill_element_by_id('registration_id', registration_id)
        self.click_element_by_id('btn_search_perfs')

    def __got_to_performance_administration_page(self):
        self.open_url_by_name('faculty_administration')
        self.click_element_by_id('lnk_performance_administration')

    def __get_first_program_link_id(self, student):
        perfs = student_performance.search(registration_id=student.registration_id)
        perf_lnk_pattern = self.perf_config.get('EXAM_MARK_LINKS_PATTERN')
        return perf_lnk_pattern.format(perfs[0].pk)
