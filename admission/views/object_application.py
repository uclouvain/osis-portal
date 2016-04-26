from admission import models as mdl


class Object_application:

    def __init__(self):
        print('intit')
        self.rdb_diploma_sec = True
        self.academic_year = mdl.academic_year.find_by_id(3)
        print('academic_year:',self.academic_year.year)
        self.rdb_belgian_foreign = True
        self.rdb_belgian_community = "FRENCH"
        self.rdb_school_belgian_community = "FRENCH"
        self.rdb_education_transition_type="GENERAL_TRANSITION"
        #self.rdb_education_transition_type=None
        self.rdb_education_technic_type=None
        self.other_education_type=None
        self.rdb_daes=True
        self.repeated_grade = True
        self.re_orientation = False
        self.result = 74
        self.admission_application = False


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


