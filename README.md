# gainz

This is a [backend test](https://docs.google.com/document/d/1qKMGyYrd1r8fVHdTd-x9_naIc_H29VrLtl9JZAOk6PI/edit) for Gainz AI company. The aim is to build a chat interface with OpenAI's realtime streaming API with FastAPI framework. The detail is as follows:
* this is the work of Touchchai (https://www.linkedin.com/in/heartnetkung/)
* the project is bootstraped using [fastapi_template](https://github.com/s3rius/FastAPI-template)
* no database is used as we can mostly rely on OpenAI's API as the source of truth
  * that is, if the server restart the data is gone
* use pydantic for schema
* front-end is built using plain HTML and jQuery
* the dependency management is Poetry
  * dependencies are listed in `pyproject.toml` file
* this project relies heavily on websocket and thus should be handled properly in production
* according to this OpenAI's missing [feature on listing threads](https://community.openai.com/t/list-of-threads-is-missing-from-the-api/484510), we resort to simple implementation just for illustration purpose.

## Quick Commands

To run the project use this set of commands:

```bash
poetry install
poetry run python -m gainz
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## Project structure

```bash
├── services
│   ├── jwt_auth.py # handling jwt encrypt/decrypt and utilities
│   └── openai.py # initialize and configure openai API
├── settings.py # list environment variables
├── static # html static files
│   ├── chat.html # chatroom interface
│   ├── chats.html # managing and joining chatrooms
│   └── index.html # login page
└── web
    ├── api
    │   ├── auth
    │   │   └── views.py # authentication routes
    │   ├── router.py # route listing
    │   └── thread
    │       ├── schema.py # schema for interfacing with OpenAI's API and the client
    │       ├── views.py # chat-related routes
    │       └── websocket.py # websocket routes
    └── application.py # FastAPI initialization
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. 

All environment variables should start with "GAINZ_" prefix.

For example if you see in your "gainz/settings.py" a variable named like
`random_parameter`, you should provide the "GAINZ_RANDOM_PARAMETER" 
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `gainz.settings.Settings.Config`.

An example of .env file:
```bash
GAINZ_RELOAD="True"
GAINZ_PORT="8000"
GAINZ_ENVIRONMENT="dev"
GAINZ_AUTH_JWT_SECRET="..."
GAINZ_OPENAI_KEY="..."
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* ruff (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.

```bash
pytest -vv .
```
