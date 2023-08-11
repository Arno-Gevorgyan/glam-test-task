from typing import TypeVar

import strawberry


T = TypeVar('T')


@strawberry.input
class UserInput:
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


@strawberry.input
class UserRegisterInput:
    email: str
    first_name: str
    last_name: str
    password: str


@strawberry.type
class UserType:
    id: str
    email: str
    first_name: str | None
    last_name: str | None
    full_name: str | None

    @strawberry.field
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.replace('None', '').strip()


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.type
class LoginSuccessType:
    user: UserType
    access_token: str
    refresh_token: str


# Password Types


@strawberry.input
class ChangePasswordInput:
    current_password: str
    password: str


# Other Types


@strawberry.type
class Message:
    message: str


@strawberry.input
class ConfirmEmailInput:
    token: str
