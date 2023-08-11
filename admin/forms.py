# Third-party imports
from wtforms.validators import Length
from wtforms import StringField, Form, EmailField

# Project-specific imports
from utils.auth import get_password_hash
from services.validators import validate_password_server


class UserForm(Form):
    """
        Custom new password.
    """
    new_password = StringField(validators=[Length(min=8, max=50)], render_kw={"class": "form-control"})
    hashed_password = StringField(render_kw={"class": "form-control", 'readonly': True})

    def validate(self, extra_validators=None):
        if new_password := self.data.get('new_password', None):
            validate_password_server(new_password)

            self.hashed_password.data = get_password_hash(new_password)
        elif self.data.get('hashed_password', None):
            self.__delitem__('new_password')
        return super().validate(extra_validators)


class UserEmailForm(Form):
    """
        Custom email field for User and hide in edit page.
    """

    user_email = EmailField(validators=[Length(max=320)],
                            render_kw={"class": "form-control"})
