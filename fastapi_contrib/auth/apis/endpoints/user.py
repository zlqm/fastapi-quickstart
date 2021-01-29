from typing import Any

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_contrib.auth import crud, schemas
from fastapi_contrib.auth.apis import deps
from fastapi_contrib.core.apis.deps import get_db

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    *,
    db: Database = Depends(get_db),
    current_active_user: schemas.UserInDB = Depends(
        deps.get_current_active_user)
) -> schemas.User:
    return current_active_user


@router.put("/me")
async def update_user_me(
    user_in: schemas.UserUpdate,
    db: Database = Depends(get_db),
    current_user: schemas.UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/")
async def read_users(
    *,
    db: Database = Depends(get_db),
    offset: int = 0,
    limit: int = 100,
    current_user: schemas.UserInDB = Depends(deps.get_current_active_superuser)
) -> Any:
    users = await crud.user.get_multi(db, offset=offset, limit=limit)
    users = [schemas.User(**user.dict()) for user in users]
    total = await crud.user.count(db)
    return {'total': total, 'items': users}


@router.post("/", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    db: Database = Depends(get_db),
    current_user: schemas.UserInDB = Depends(
        deps.get_current_active_superuser),
) -> Any:
    user = await crud.user.get_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists in the system",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return user
