#!/bin/env bash

# Migrate
alembic upgrade head

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --forwarded-allow-ips="*"