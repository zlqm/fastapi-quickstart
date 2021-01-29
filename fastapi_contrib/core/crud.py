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

    def _filter_by(self, _query=None, **kwargs):
        query = _query
        if query is None:
            query = self.table.select()
        for key, value in kwargs.items():
            query = query.where(getattr(self.table.c, key) == value)
        return query

    async def count(self, db: Database, **kwargs) -> int:
        query = self._filter_by(**kwargs).count()
        return await db.fetch_val(query=query)

    async def get(self, db: Database, **kwargs) -> Optional[Dict[str, Any]]:
        query = self._filter_by(**kwargs)
        record = await db.fetch_one(query=query)
        if record:
            record = self.model(**record)
        return record

    async def get_multi(self,
                        db: Database,
                        *,
                        offset: int = 0,
                        limit: int = 100,
                        **kwargs) -> List[ModelType]:
        query = self._filter_by(**kwargs)
        query = query.offset(offset).limit(limit)
        items = await db.fetch_all(query)
        return [self.model(**item) for item in items]

    async def create(
            self, db: Database, *, db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        ins = self.table.insert().values(**obj_in_data)
        last_record_id = await db.execute(ins)
        obj_in_data["id"] = last_record_id
        return self.model(**obj_in_data)

    async def update(
            self, db: Database, *, db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field, _ in db_obj:
            if field not in update_data and field in update_data:
                update_data.pop(field)
        if 'id' in update_data:
            update_data.pop('id')
        if not update_data:
            return db_obj
        query = update(self.table).where(self.table.c.id == db_obj.id)
        query = query.values(**update_data)
        await db.execute(query)
        return await self.get(db, db_obj.id)

    async def remove(self, db: Database, id: Any) -> ModelType:
        obj = await self.get(db, id)
        query = delete(self.table).where(self.table.id == id)
        await db.execute(query)
        return obj
