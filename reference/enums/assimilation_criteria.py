from django.utils.translation import ugettext_lazy as _

CRITERIA_1 = "CRITERIA_1"
CRITERIA_2 = "CRITERIA_2"
CRITERIA_3 = "CRITERIA_3"
CRITERIA_4 = "CRITERIA_4"
CRITERIA_5 = "CRITERIA_5"
CRITERIA_6 = "CRITERIA_6"
CRITERIA_7 = "CRITERIA_7"

ASSIMILATION_CRITERIA_CHOICES = (
    (CRITERIA_1, _(CRITERIA_1)),
    (CRITERIA_2, _(CRITERIA_2)),
    (CRITERIA_3, _(CRITERIA_3)),
    (CRITERIA_4, _(CRITERIA_4)),
    (CRITERIA_5, _(CRITERIA_5)),
    (CRITERIA_6, _(CRITERIA_6)),
    (CRITERIA_7, _(CRITERIA_7)),
)


def find(criteria):
    for elt in ASSIMILATION_CRITERIA_CHOICES:
        if elt[0] == criteria:
            return elt
    return None
