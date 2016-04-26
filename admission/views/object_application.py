from admission import models as mdl
from reference.models import Language
from django.utils import timezone


class Object_application:

    def __init__(self):
        #Belgian
        # self.rdb_diploma_sec = True
        # self.academic_year = mdl.academic_year.find_by_id(3)
        # self.rdb_belgian_foreign = True
        # self.rdb_belgian_community = "FRENCH"
        # self.rdb_school_belgian_community = "FRENCH"
        # self.rdb_education_transition_type="GENERAL_TRANSITION"
        # self.rdb_education_technic_type=None
        # self.other_education_type=None
        # self.rdb_daes=True
        # self.repeated_grade = True
        # self.re_orientation = False
        # self.result = 74
        # self.admission_application = False
        #foreign
        self.rdb_diploma_sec = True
        self.academic_year = mdl.academic_year.find_by_id(3)
        self.foreign_baccalaureate_diploma='EUROPEAN'
        self.foreign_baccalaureate_diploma=None

        self.rdb_belgian_foreign = False
        self.language_diploma = None
        self.other_language_diploma= Language.find_by_id(9)
        self.result = 74
        #exam admission
        self.rdb_diploma_sec = False
        self.admission_exam = True
        self.admission_exam_date = timezone.now()
        #prof experie
        self.rdb_diploma_sec = False
        self.admission_exam = False
        self.professional_experience = True

    def daes(self):
        print('ades', self.academic_year.year, " " , self.rdb_belgian_community)
        if (self.academic_year.year < 1994 and self.rdb_belgian_community == 'FRENCH') \
                or (self.academic_year.year < 1992 and self.rdb_belgian_community == 'DUTCH'):
            return True
        return False

    def doubble(self):
        if self.rdb_diploma_sec is True and self.academic_year.year < 1994:
            return True
        return False


