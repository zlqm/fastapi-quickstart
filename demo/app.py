from fastapi import APIRouter
import sqlalchemy

from fastapi_contrib.core.config import CONFIG
from fastapi_contrib.core.db import metadata
from fastapi_contrib.core.main import get_application
from fastapi_contrib.auth.apis import login, user

CONFIG['PROJECT_NAME'] = 'demo_app'


def create_application():
    app = get_application()
    api_router = APIRouter()
    api_router.include_router(login.router, prefix='/login', tags=['login'])
    api_router.include_router(user.router, prefix='/user', tags=['user'])
    app.include_router(api_router, prefix='/api/v1')
    return app


app = create_application()


def script_create_tables():
    engine = sqlalchemy.create_engine(CONFIG.DATABASES.DEFAULT)
    metadata.create_all(engine)


async def create_test_user():
    import databases
    db = databases.Database(CONFIG.DATABASES.DEFAULT)
    await db.connect()
    from fastapi_contrib.auth import crud, schemas
    user = schemas.UserCreate(email='test@test.com', password='123456')
    await crud.user.create(db, obj_in=user)
    await db.disconnect()


if __name__ == '__main__':
    script_create_tables()
    import asyncio
    asyncio.run(create_test_user())
