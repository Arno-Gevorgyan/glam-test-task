from services.users import get
from gql.exceptions import ValidationError


async def check_email(session, email: str) -> None:
    """
    Check if user already have user with this email.
    """

    user = await get(session, email=email)
    if user:
        raise ValidationError({'email': f'User with email: {email} already exist.'})
