from typing import Any

from strawberry.types import Info
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.permission import BasePermission

from settings import get_settings
from messages import ErrorMessage
from gql.exceptions import GQLError
from services.users import get_current_user


class IsAuthenticated(BasePermission):

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request: Request | WebSocket = info.context['request']
        if 'Authorization' in request.headers:
            authorization = request.headers['Authorization'].split()
            if authorization[0] != get_settings().jwt_header:
                raise GQLError(ErrorMessage.WRONG_TOKEN_HEADER)
            info.context['user'] = await get_current_user(
                authorization[1],
                info.context['session'],
            )
            return True
        raise GQLError(ErrorMessage.AUTH_NEEDED)
