# Standard library imports
from typing import List, Any
from datetime import datetime, timedelta

# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession

# SQLAlchemy imports
from sqlalchemy import select

# Project-specific imports
from settings import get_settings
from messages import ErrorMessage
from db.models._users import UserModel
from gql.base.types import MessageType, RefreshTokenInput
from gql.exceptions import FoundError, GQLError, ValidationError
from services.validators import validate_user_data, validate_password
from utils.auth import decode_token, get_password_hash, verify_password, create_access_token
from gql.users.types import UserInput, UserType, LoginInput, LoginSuccessType, ChangePasswordInput, UserRegisterInput


# Queries functions ##


async def get(session: AsyncSession, email: str = None,
              user_id: int = None) -> UserModel:
    """ Getting user by email or id """
    if email:
        query = select(UserModel).where(UserModel.email == email)
    else:
        query = select(UserModel).where(UserModel.id == int(user_id))
    result = await session.execute(query)
    return result.scalars().first()


async def get_users(session: AsyncSession) -> List[UserType]:
    """ Getting list of users """

    query = select(UserModel)
    result = await session.execute(query)
    return result.scalars().unique().all()


# Mutations functions ##


async def register_user(data: UserRegisterInput, session: AsyncSession) -> MessageType:
    """Creating User by email and password"""

    user_data = data.__dict__
    password = user_data.pop('password')
    email = user_data.get('email')

    # Validate data
    await validate_user_data(session, email, password)

    # Create instance for User
    user = UserModel(**user_data)
    user.hashed_password = get_password_hash(password)
    session.add(user)
    await session.commit()
    return MessageType(message='User was created')


async def update(data: UserInput, session: AsyncSession,
                 user: UserModel) -> UserType:
    """ Updating user """

    data_dict = data.__dict__
    try:
        for arg in data_dict:
            if data_dict[arg] is not None:
                user.__setattr__(arg, data_dict[arg])
    except Exception as e:
        raise ValidationError('Email already exists')
    user.updated_at = datetime.utcnow()
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: UserModel) -> MessageType:
    """ Deleting user """

    await session.delete(user)
    await session.commit()
    return MessageType(message=f'User was deleted: {user.email}')


async def login(data: LoginInput, session: AsyncSession) -> LoginSuccessType:
    """ User authentication """

    user = await get(session, data.email.lower())
    if not user:
        raise ValidationError(ErrorMessage.USER_NOT_EXISTS)
    if not verify_password(data.password, user.hashed_password):
        raise ValidationError(ErrorMessage.INCORRECT_PASSWORD)
    return await create_tokens(user)


async def refresh_token(data: RefreshTokenInput,
                        session: AsyncSession) -> LoginSuccessType:
    """ Getting new access and refresh tokens """

    user_id = decode_token(data.refresh_token)
    user = await get(session, user_id=int(user_id))
    if user is None:
        raise FoundError(ErrorMessage.USER_NOT_EXISTS)
    return await create_tokens(user)


async def login_admin(data: LoginInput, session: AsyncSession) -> str:
    """ User authentication: admin panel """

    user = await get(session, email=data.email)
    if not user:
        raise FoundError(ErrorMessage.USER_NOT_EXISTS)
    if not verify_password(data.password, user.hashed_password):
        raise ValidationError(ErrorMessage.INCORRECT_PASSWORD)
    errors = {}
    if not user.is_superuser:
        errors.update(ErrorMessage.USER_NOT_ADMIN)
    if errors:
        raise GQLError(errors)
    return create_access_token(
        data={'token_type': 'access', 'user_id': user.id},
        expires_delta=timedelta(
            minutes=get_settings().access_token_expire_minutes
        )
    )


async def get_current_user(token: str, session: AsyncSession) -> UserType:
    """ Getting current user by token """

    user_id = decode_token(token)
    user = await get(session, user_id=int(user_id))
    if user is None:
        raise FoundError(ErrorMessage.USER_NOT_EXISTS)
    return user


async def create_tokens(user: UserModel) -> LoginSuccessType:

    access_token = create_access_token(
        data={'token_type': 'access', 'user_id': user.id},
        expires_delta=timedelta(
            minutes=get_settings().access_token_expire_minutes
        )
    )
    user_refresh_token = create_access_token(
        data={'token_type': 'refresh', 'user_id': user.id},
        expires_delta=timedelta(days=get_settings().refresh_token_expire_days)
    )
    return LoginSuccessType(user=user, access_token=access_token, refresh_token=user_refresh_token)


async def change_password(user: UserModel, data: ChangePasswordInput, session: AsyncSession) -> MessageType:
    """ Change user password  """
    current_password = data.current_password
    if not verify_password(current_password, user.hashed_password):
        raise ValidationError(ErrorMessage.CURRENT_PASSWORD)
    elif current_password == data.password:
        raise ValidationError({'password': 'You cannot change your password to an existing one.'})

    new_password = data.password
    password = validate_password(new_password)
    user.hashed_password = get_password_hash(password)
    await session.commit()
    await session.refresh(user)
    return MessageType(message='Password changed successfully')

