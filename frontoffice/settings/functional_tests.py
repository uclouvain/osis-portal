import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Functional Tests settings
FUNCT_TESTS_CONFIG = {
    'DEFAULT_WAITING_TIME': int(os.environ.get('FT_DEFAULT_WAITING_TIME', 15)),
    'BROWSER': os.environ.get('FT_BROWSER', 'FIREFOX'),
    'VIRTUAL_DISPLAY': os.environ.get('FT_VIRTUAL_DISPLAY', 'True').lower() == 'true',
    'DISPLAY_WIDTH': int(os.environ.get('FT_DISPLAY_WIDTH', 1920)),
    'DISPLAY_HEIGHT': int(os.environ.get('FT_DISPLAY_HEIGHT', 1080)),
    'GECKO_DRIVER': os.environ.get(
        'FT_GECKO_DRIVER',
        os.path.join(BASE_DIR, 'base/tests/functional/drivers/geckodriver')
    ),
    'TAKE_SCREENSHOTS': os.environ.get('FT_TAKE_SCREENSHOTS', 'False').lower() == 'true',
    'SCREENSHOTS_DIR': os.environ.get('FT_SCREENSHOT_DIR', os.path.join(BASE_DIR, 'base/tests/functional/screenshots')),
    'HTML_REPORTS': os.environ.get('FT_HTML_REPORTS', 'False').lower() == 'true',
    'HTML_REPORTS_DIR': os.environ.get(
        'FT_HTML_REPORTS_DIR',
        os.path.join(BASE_DIR, 'base/tests/functional/html_reports')
    ),
    'HTML_REPORTS_STATIC_DIR': os.environ.get(
        'FT_HTML_REPORTS_STATIC_DIR',
        os.path.join(BASE_DIR, 'base/tests/functional/html_reports/static')
    ),
    'DASHBOARD': {
        'PAGE_TITLE': 'Dashboard',
        'STUDENT_LINKS': ('lnk_performance', 'lnk_my_attestations', 'lnk_exam_enrollment_offer_choice'),
        'TUTOR_LINKS': ('lnk_score_encoding', 'lnk_my_teaching_charge', 'lnk_my_students_list', 'lnk_manage_courses'),
        'ADMIN_LINKS': ('bt_administrations', )
    },
    'PERFORMANCE': {
        'PAGE_TITLE': 'Exam Marks',
        'FROM_DASH_LINK': 'lnk_performance',
        'EXAM_MARK_LINKS_PATTERN': 'lnk_perf_{}',
        'EXAM_MARK': {
            'PAGE_TITLE': 'Exam Mark',
        },
        'FAC_ADMIN': {
            'PAGE_TITLE': 'Exam Marks Faculty Administration',
            'SEARCH_INPUT': 'registration_id',
            'SEARCH_BT': 'btn_search_perfs',
            'FROM_FAC_ADMIN_LINK': 'lnk_performance_administration'
        }
    },
    'ADMIN': {
        'FAC_ADMIN': {
            'PAGE_TITLE': 'Faculty Administration',
            'FROM_DASH_LINK_1': 'bt_administrations',
            'FROM_DASH_LINK_2': 'bt_faculty_administration',
            'ADMIN_LINKS': ('lnk_performance_administration', 'lnk_attestation_administration',
                            'lnk_attribution_administration', 'lnk_scores_sheets_admin',
                            'lnk_lists_of_students_exams_enrollments')
        },
        'DATA_ADMIN': {
            'PAGE_TITLE': 'Data Administration',
            'FROM_DASH_LINK_1': 'bt_administrations',
            'FROM_DASH_LINK_2': 'bt_data',
            'ADMIN_LINKS': ('lnk_data_management', )
        },
        'DATA_MANAGEMENT': {
            'PAGE_TITLE': 'Louvain | Osis-studies',
            'FROM_DATA_ADMIN_LNK': 'lnk_data_management'
        }
    },
    'CONTINUING_EDUCATION': {
        'PAGE_TITLE': 'Continuing Education'
    }
}
