from pathlib import Path

import strawberry
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from services.users import login
from admin import init_admin_page
from settings import get_settings
from admin.base import CustomAdmin
from gql.schema import Mutation, Query
from gql.users.types import LoginInput
from gql.auth_backend import AuthBackend
from db.session import engine, get_async_session


# App's config


async def get_context(
    session: AsyncSession = Depends(get_async_session),
):
    return {
        'session': session,
    }

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)

graphql_app = GraphQLRouter(schema, context_getter=get_context)


def create_app() -> FastAPI:
    app = FastAPI()

    app.mount(
        '/static',
        StaticFiles(directory=Path(__file__).parent.absolute() / 'templates'),
        name='static',
    )

    app.include_router(graphql_app, prefix='/graphql')

    app.add_middleware(CORSMiddleware, allow_headers=["*"],
                       allow_origins=["*"], allow_methods=["*"])

    app.add_middleware(SessionMiddleware, secret_key=get_settings().jwt_secret)
    return app


app = create_app()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

auth_backend = AuthBackend(secret_key=get_settings().jwt_secret)
admin_app = CustomAdmin(app, engine, authentication_backend=auth_backend)
init_admin_page(admin_app)

# FastAPI endpoints

templates = Jinja2Templates(directory='templates')


@app.get('/', include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})


@app.get('/info')
async def info():
    """ Getting app info """

    settings = get_settings()
    return {
        'app_name': settings.app_name,
        'admin_email': settings.admin_email
    }


@app.post('/token')
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """ Getting tokens after email and password validation """

    cred = LoginInput(email=form_data.username, password=form_data.password)
    try:
        data = await login(cred, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': f'{get_settings().jwt_header}'},
        ) from e
    return {'access_token': data.access_token,
            'refresh_token': data.refresh_token,
            'token_type': f'{get_settings().jwt_header}'}
