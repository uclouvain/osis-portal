from django.contrib import admin

from .models import Offer
from .models import OfferEnrollment
from .models import Student
from .models import OfferYear
from .models import AcademicYear
from .models import LearningUnit
from .models import LearningUnitYear
from .models import LearningUnitEnrollment
from .models import Configuration

admin.site.register(Offer)
admin.site.register(OfferEnrollment)
admin.site.register(Student)
admin.site.register(OfferYear)
admin.site.register(AcademicYear)
admin.site.register(LearningUnit)
admin.site.register(LearningUnitYear)
admin.site.register(LearningUnitEnrollment)
admin.site.register(Configuration)
