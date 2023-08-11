import strawberry


@strawberry.input
class IDInput:
    id: int


@strawberry.type
class MessageType:
    message: str


@strawberry.input
class RefreshTokenInput:
    refresh_token: str
