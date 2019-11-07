import factory.fuzzy
import pendulum


def fn_publication_start_date(cohort):
    return pendulum.today().start_of('month')._datetime


def fn_subscription_start_date(cohort):
    return pendulum.instance(cohort.publication_start_date).subtract(months=1)._datetime


def fn_subscription_end_date(cohort):
    return pendulum.instance(cohort.subscription_start_date).add(months=2)._datetime


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'internship.Cohort'

    name = factory.Sequence(lambda n: 'Cohort %d' % (n,))
    description = factory.fuzzy.FuzzyText()

    publication_start_date = factory.LazyAttribute(fn_publication_start_date)
    subscription_start_date = factory.LazyAttribute(fn_subscription_start_date)
    subscription_end_date = factory.LazyAttribute(fn_subscription_end_date)
