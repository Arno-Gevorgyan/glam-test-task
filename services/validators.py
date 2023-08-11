# Standard library imports
import re


# Third-party imports
from starlette.exceptions import HTTPException
from email_validator import validate_email

# Project-specific imports
from messages import ErrorMessage
from gql.exceptions import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


def validate_password_server(value):
    # need this for admin and if password is wrong rise exception

    password_regex = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')
    if not re.match(password_regex, value):
        raise HTTPException(status_code=400,
                            detail="Invalid password format. "
                                   "Your password must be at least 8 characters long and "
                                   "include at least one uppercase letter, one lowercase letter,"
                                   " one number, and one special character.")
    return value


def validate_password(value):
    # need this for website and if password is wrong return message
    password_regex = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$')
    if not re.match(password_regex, value):
        raise ValidationError(ErrorMessage.PASSWORD_ERROR)

    return value


async def validate_user_data(session: AsyncSession,
                             email: str = None,
                             password: str = None,
                             ) -> None:
    from services.users import get
    """ Validation for user with same conditions """
    if email and await get(session=session, email=email):
        raise ValidationError(ErrorMessage.USER_EXISTS_EMAIL)
    try:
        validate_email(email)
    except Exception as e:
        raise ValidationError({"email": str(e)}) from e
    validate_password(password)
