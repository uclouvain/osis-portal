from django import forms
from django.utils.encoding import smart_str

class CommaWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        return super(CommaWidget, self).render(name, smart_str(value).replace('.', ','))


class CommaDecimalField(forms.DecimalField):
    """
    Extension to DecimalField that allows comma-separated Decimals to be entered and displayed
    """
    widget = CommaWidget

    def clean(self, value):
        value = smart_str(value).replace(',', '.')
        return super(CommaDecimalField, self).clean(value)