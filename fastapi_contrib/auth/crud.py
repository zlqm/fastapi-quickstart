from typing import Optional

from databases import Database

from fastapi_contrib.auth import models, schemas, security
from fastapi_contrib.core.crud import CRUDBase
from fastapi_contrib.core.utils import random_string


class CRUDUser(CRUDBase):
    async def get_by_email(
        self, db: Database, email: str
    ) -> Optional[schemas.UserInDB]:
        query = self.table.select().where(self.table.c.email == email)
        record = await db.fetch_one(query=query)
        if record:
            record = schemas.UserInDB(**record)
        return record

    async def authenticate(
        self,
        db: Database,
        email: str,
        password: str,
    ) -> Optional[schemas.UserInDB]:
        user = await self.get_by_email(db, email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    async def create(
        self, db: Database, *, obj_in: schemas.UserCreate
    ) -> schemas.UserInDB:
        data = dict(
            id=random_string(),
            email=obj_in.email,
            hashed_password=security.get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_superuser=obj_in.is_superuser,
        )
        query = self.table.insert().values(**data)
        latest_record_id = await db.execute(query)
        data["id"] = latest_record_id
        return schemas.UserInDB(**data)

    async def update(
        self, db: Database, *, db_obj: schemas.UserInDB, obj_in: schemas.UserUpdate
    ) -> schemas.UserInDB:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = security.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)


user = CRUDUser(models.User, schemas.UserInDB)
