"""
How to raise several fields errors?
Use empty errors dict and `update()` method.
"""
import strawberry
from enum import Enum
from graphql import GraphQLError


@strawberry.enum
class ExceptionEnum(Enum):
    """ Exception statuses which are used in the GraphQLError extensions """

    TOKEN_EXPIRED = 'TOKEN_EXPIRED'
    UNPROCESSABLE_ENTITY = 'UNPROCESSABLE_ENTITY'
    RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND'


class GQLError(GraphQLError):
    message: str = 'Common error'
    code: str = ExceptionEnum.UNPROCESSABLE_ENTITY.value

    def __init__(self, explain=None, *args, **kwargs):
        extensions = {
            'code': self.code,
            'explain': explain or {}
        }
        super().__init__(self.message, extensions=extensions, *args, **kwargs)


class ValidationError(GQLError):
    message: str = 'Invalid data'
    code: str = ExceptionEnum.UNPROCESSABLE_ENTITY.value


class AuthenticationError(GQLError):
    message: str = 'Expired token'
    code: str = ExceptionEnum.TOKEN_EXPIRED.value


class FoundError(GQLError):
    message: str = 'Data couldn\'t be found'
    code: str = ExceptionEnum.RESOURCE_NOT_FOUND.value
