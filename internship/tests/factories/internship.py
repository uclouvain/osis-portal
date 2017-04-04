import factory
import factory.fuzzy
import pendulum

from internship.tests.factories.cohort import CohortFactory
from internship.tests.models.test_internship_speciality import create_speciality

class InternshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Internship'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    length_in_periods = 1
    cohort = CohortFactory()
    speciality = None
