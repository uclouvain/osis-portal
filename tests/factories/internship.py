import factory.fuzzy

from internship.tests.factories.cohort import CohortFactory


class InternshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Internship'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    length_in_periods = 1
    cohort = factory.SubFactory(CohortFactory)
    speciality = None
