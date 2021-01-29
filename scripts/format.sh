#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place fastapi_contrib --exclude=__init__.py
black fastapi_contrib
isort --recursive --apply fastapi_contrib
