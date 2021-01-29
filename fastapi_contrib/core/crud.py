from typing import Any, Dict, List, Optional, TypeVar, Union

from databases import Database
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Table, delete, update

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase:
    def __init__(self, table: Table, model: ModelType):
        self.table = table
        self.model = model

    async def get(self, db: Database, id: Any) -> Optional[Dict[str, Any]]:
        query = self.table.select().where(self.table.c.id == id)
        record = await db.fetch_one(query=query)
        if record:
            record = self.model(**record)
        return record

    async def get_multi(
        self, db: Database, *, offset: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = self.table.select().offset(offset).limit(limit)
        items = await db.fetch_all(query)
        return [self.model(**item) for item in items]

    async def create(
        self,
        db: Database,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        ins = self.table.insert().values(**obj_in_data)
        last_record_id = await db.execute(ins)
        obj_in_data["id"] = last_record_id
        return self.model(**obj_in_data)

    async def update(
        self,
        db: Database,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        "id" in update_data and update_data.pop("id")
        for field in db_obj:
            if field not in update_data:
                update_data.pop(field)
        if not update_data:
            return db_obj
        query = update(self.table).where(self.table.id == db_obj.id)
        query = query.values(**update_data)
        await db.execute(query)
        return await self.get(db, db_obj.id)

    async def remove(self, db: Database, id: Any) -> ModelType:
        obj = await self.get(db, id)
        query = delete(self.table).where(self.table.id == id)
        await db.execute(query)
        return obj
