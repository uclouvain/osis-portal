import factory
import factory.fuzzy
import pendulum

from internship.tests.factories.cohort import CohortFactory

class InternshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Internship'
        database = 'default'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    length_in_periods = 1
    cohort = CohortFactory()
    speciality = None
