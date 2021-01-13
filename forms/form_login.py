from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class InternshipAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username_field.verbose_name = User.get_email_field_name()
