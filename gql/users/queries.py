from typing import List

import strawberry
from strawberry.types import Info

from .types import UserType
from gql.permissions import IsAuthenticated
from services.users import get_users


@strawberry.type
class UserQuery:

    @strawberry.field(
        description='Getting list of users',
        permission_classes=[IsAuthenticated],
    )
    async def users_list(self, info: Info) -> List[UserType]:
        return await get_users(info.context['session'])

    @strawberry.field(
        description='Getting authenticated user',
        permission_classes=[IsAuthenticated],
    )
    async def me(self, info: Info) -> UserType:
        return info.context['user']
