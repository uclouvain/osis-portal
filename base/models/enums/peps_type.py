from django.utils.translation import gettext_lazy as _
from base.models.utils.utils import ChoiceEnum


# FIX ME: Use Enum provided by OpenAPI Component instead of this one
class PepsTypes(ChoiceEnum):
    NOT_DEFINED = _('Not defined')
    DISABILITY = _('DDI')
    SPORT = _('Sport')
    ARTIST = _('Artist')
    ENTREPRENEUR = _('Entrepreneur')
    ARRANGEMENT_JURY = _('Educational facilities accepted by Jury')
