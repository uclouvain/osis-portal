from django.utils import translation
from django.utils.translation import ugettext as _

from base.tests.functional.models.base_model import FunctionalTestCase
from performance.tests.functional.model import StudentWithPerformanceMixin


class PerformanceAsAStudentTestCase(FunctionalTestCase, StudentWithPerformanceMixin):

    def setUp(self):
        super(PerformanceAsAStudentTestCase, self).setUp()
        self.student_without_perfs = self.create_student()
        self.student_with_perfs = self.create_student_with_performances()

    def test_access_performance_page(self):
        """
        As a student I can access my exam marks page
        """
        self.login(self.student_without_perfs.person.user.username)
        self._got_to_perfomance_page()
        self.check_page_title(self.config.get('PERFORMANCE').get('PAGE_TITLE'))

    def test_user_without_performances(self):
        """
        As a student
         - Without any performance results
           * I should see a message "No results yet"
        """
        self.login(self.student_without_perfs.person.user.username)
        self._got_to_perfomance_page()
        translation.activate('en')
        string = _('dont_have_the_score_yet')
        self.check_page_contains_string(string)

    def _got_to_perfomance_page(self):
        self.openUrlByName('dashboard')
        self.click_element_by_id(self.config.get('PERFORMANCE').get('FROM_DASH_LINK'))
