from time import sleep

from base.tests.functional.models.model import FunctionalTestCase
from performance.models import student_performance
from performance.tests.functional.models.model import StudentWithPerformanceMixin


class PerformanceAsAStudentTestCase(FunctionalTestCase, StudentWithPerformanceMixin):

    def setUp(self):
        super(PerformanceAsAStudentTestCase, self).setUp()
        self.student_without_perfs = self.create_student()
        self.student_with_valid_perfs = self.create_student_with_valid_performances()

    @classmethod
    def setUpClass(cls):
        super(PerformanceAsAStudentTestCase, cls).setUpClass()
        cls.perf_config = cls.config.get('PERFORMANCE')

    def test_access_performance_page(self):
        """
        As a student I can access my exam marks page
        """
        self.login(self.student_without_perfs.person.user.username)
        self._got_to_perfomance_page()
        self.check_page_title(self.perf_config.get('PAGE_TITLE'))

    def test_student_without_performances(self):
        """
        As a student
         Without any performance results
          When i go to to "my exam marks page"
           - I should see a message "No results yet"
        """
        self.login(self.student_without_perfs.person.user.username)
        self._got_to_perfomance_page()
        string = self.get_localized_message('dont_have_the_score_yet', self.student_without_perfs.person.language)
        self.check_page_contains_string(string)

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
        self._got_to_perfomance_page()
        string = self.get_localized_message('performance_results_general_legal_announcement',
                                            self.student_with_valid_perfs.person.language)
        self.check_page_contains_string(string)
        perfs = student_performance.search(registration_id=self.student_with_valid_perfs.registration_id)
        perf_lnk_pattern = self.perf_config.get('EXAM_MARK_LINKS_PATTERN')
        self.check_page_contains_ids([perf_lnk_pattern.format(p.pk) for p in perfs])
        self.click_element_by_id(perf_lnk_pattern.format(perfs[0].pk))
        self.check_page_title(self.config.get('PERFORMANCE').get('EXAM_MARK').get('PAGE_TITLE'))
        self._check_common_messages(self.student_with_valid_perfs.person.language)

    def _check_common_messages(self, language):
        self.check_page_contains_string(self.get_localized_message('performance_result_note_legal_announcement', language))
        self.check_page_contains_string(self.get_localized_message('text_mean_exprimed_for_20', language))
        self.check_page_contains_string(self.get_localized_message('legend', language))
        self.check_page_contains_string(self.get_localized_message('cycle_advancement_explanations', language))
        self.check_page_contains_ids(['paragraph_mention_explanation'])

    def _got_to_perfomance_page(self):
        self.openUrlByName('home')
        self.click_element_by_id(self.config.get('PERFORMANCE').get('FROM_DASH_LINK'))
