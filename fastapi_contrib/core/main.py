from functools import partial

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .config import CONFIG
from .db import connect_database, disconnect_database


def get_application():
    app = FastAPI(
        title=CONFIG.PROJECT_NAME,
    )
    if CONFIG.get("CORS_ORIGINS"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in CONFIG.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_event_handler("startup", partial(connect_database, app))
    app.add_event_handler("shutdown", partial(disconnect_database, app))
    return app
