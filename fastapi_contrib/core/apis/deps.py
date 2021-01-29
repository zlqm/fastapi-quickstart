from databases import Database
from fastapi import Request


def get_db(request: Request) -> Database:
    name = "DEFAULT"
    return request.app.state.databases[name]
