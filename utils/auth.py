from settings import get_settings
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt, ExpiredSignatureError, JWTError

from messages import ErrorMessage
from gql.exceptions import AuthenticationError, FoundError, GQLError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=3600000)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().jwt_secret,
                             algorithm=get_settings().algorithm)
    return encoded_jwt


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, get_settings().jwt_secret,
                             algorithms=[get_settings().algorithm])
        user_id: str = payload.get('user_id')
        token_type: str = payload.get('token_type')
        if user_id is None:
            raise FoundError(ErrorMessage.USER_NOT_EXISTS)
        if token_type != 'access':
            raise GQLError(ErrorMessage.WRONG_TOKEN)
    except ExpiredSignatureError:
        raise AuthenticationError()
    except JWTError:
        raise GQLError(ErrorMessage.INVALID_TOKEN)
    return user_id
