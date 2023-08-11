from db.models._users import UserModel
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin.authentication import AuthenticationBackend

from db.session import engine
from settings import get_settings
from gql.users.types import LoginInput
from services.users import login_admin, get_current_user


class AuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form['username'], form['password']
        data = LoginInput(email=username, password=password)
        try:
            async with AsyncSession(engine) as session:
                result = await login_admin(data, session)
                request.session.update(
                    {'token': f'{get_settings().jwt_header} {result}'}
                )
                return True
        except Exception as e:
            print(e)
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get('token')
        if not token:
            return False
        try:
            async with AsyncSession(engine) as session:
                result = await get_current_user(token.split()[-1], session)
            if isinstance(result, UserModel):
                request.session.update({'user': {
                    'id': result.id,
                    'is_active': result.is_active,
                    'is_superuser': result.is_superuser,
                }})
                return True
        except Exception as e:
            print(e)
        return False
