# Giam Test Task

## Project's structure

```text
├── alembic ············· alembic's data, what were generated during init, but can be updated
│  ├── env.py
│  ├── README
│  ├── script.py.mako
│  └── versions ········· generated migrations by alembic
├── alembic.ini ········· alembic's config
├── createuser.py ······· script for adding new user
├── db
│  ├── models ··········· db's models
│  ├── base.py ·········· base config for db models
│  └── session.py ······· params for connection to db
├── gql ················· strawberry schemas (graphql part)
├── main.py ············· main code for starting app
├── messages.py ········· errors and success messages for responses
├── README.md ··········· you're here
├── requirements.txt
│── Dockerfile ······· Setup
│── docker-compose.yaml 
├── services
│  ├── users.py ········· users logic
│  └── instagram.py ····· selenium
├── settings.py ········· app settings
├── templates ··········· templates for pages
```

## Local deployment

## RUN PROJECT

```shell
docker compose up
```

## Documentation how get photos from instagram
open /graphql -> mutation -> userRegister  
open /graphql -> mutation -> login -> accesToken  
add in headers 
{
 "Authorization": "Bearer <accesToken>"
}

open /graphql -> query -> getPhotos -> username, max_count


## Alembic

**Create migration**:

```shell
alembic revision --autogenerate -m "Comment"
```

*Recommendation*: use '{000}_comment' format for comments.

**Migrate to last**:

```shell
alembic upgrade head
```

## Superuser User adding

Use `createuser.py` for adding  superuser in table.

/admin for admin page