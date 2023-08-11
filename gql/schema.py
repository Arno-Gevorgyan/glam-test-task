# Strawberry import
from strawberry.tools import merge_types

from gql.instagram.queries import InstagramQuery
# GQL - Queries
from gql.users.queries import UserQuery

# GQL - Mutations
from gql.users.mutations import UserMutation


Query = merge_types(
    name='Query',
    types=(
        UserQuery,
        InstagramQuery,
    ),
)

Mutation = merge_types(
    name="Mutation",
    types=(
        UserMutation,
    ),
)
