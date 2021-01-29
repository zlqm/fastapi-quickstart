import sqlalchemy
from databases import Database
from fastapi import FastAPI

from fastapi_contrib.core.config import CONFIG
from fastapi_contrib.core.utils import Proxy

metadata = sqlalchemy.MetaData()


async def connect_database(app: FastAPI) -> None:
    proxy = Proxy()
    for name, uri in CONFIG.DATABASES.items():
        proxy[name] = Database(uri)
        await proxy[name].connect()
    app.state.databases = proxy
    app.state.database = proxy["DEFAULT"]


async def disconnect_database(app: FastAPI) -> None:
    for name, database in app.state.items():
        await database.disconnect()
    app.state.database = None
