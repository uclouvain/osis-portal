import factory.fuzzy
from django.utils.translation import gettext_lazy as _

from base.tests.factories.person import PersonFactory
from internship.tests.factories.cohort import CohortFactory

TYPE_CHOICE = (('SPECIALIST', _('Specialist')),
               ('GENERALIST', _('Generalist')))


class InternshipStudentInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.InternshipStudentInformation'

    person = factory.SubFactory(PersonFactory)
    cohort = factory.SubFactory(CohortFactory)
    location = factory.Faker('address')
    postal_code = 1348
    city = factory.Faker('city')
    country = factory.Faker('country')
    email = factory.Faker('email')
    phone_mobile = factory.Faker('phone_number')
    contest = factory.fuzzy.FuzzyChoice(TYPE_CHOICE)

