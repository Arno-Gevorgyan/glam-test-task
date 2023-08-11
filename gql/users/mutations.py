import strawberry
from strawberry.types import Info

from gql.permissions import IsAuthenticated
from services.users import delete_user, update, login, refresh_token, change_password, register_user

from gql.base.types import MessageType, RefreshTokenInput
from .types import LoginInput, LoginSuccessType, UserInput, UserType, ChangePasswordInput, UserRegisterInput


@strawberry.type
class UserMutation:
    @strawberry.mutation(
        description='User register',
    )
    async def user_register(self, info: Info, data: UserRegisterInput) -> MessageType:
        return await register_user(data, info.context['session'])

    @strawberry.mutation(description='Login')
    async def login(self, info: Info,
                    data: LoginInput) -> LoginSuccessType:
        return await login(data, info.context['session'])

    @strawberry.mutation(
        description='User updating',
        permission_classes=[IsAuthenticated],
    )
    async def user_update(self, info: Info, data: UserInput) -> UserType:
        return await update(data, info.context['session'], info.context['user'])

    @strawberry.mutation(
        description='User deleting',
        permission_classes=[IsAuthenticated],
    )
    async def user_delete(self, info: Info) -> MessageType:
        return await delete_user(info.context['session'], info.context['user'])

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def change_password(self, info: Info, data: ChangePasswordInput) -> MessageType:
        return await change_password(info.context['user'], data, info.context['session'])

    @strawberry.mutation(description='Refreshing of tokens')
    async def token_refresh(self, info: Info,
                            data: RefreshTokenInput) -> LoginSuccessType:
        return await refresh_token(data, info.context['session'])
