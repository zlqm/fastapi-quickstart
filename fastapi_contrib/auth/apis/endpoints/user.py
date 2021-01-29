from typing import Any, List

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
    current_active_user: schemas.UserInDB = Depends(deps.get_current_active_user)
) -> schemas.User:
    return current_active_user


@router.post("/me")
async def update_user_me(
    user_in: schemas.UserUpdate,
    db: Database = Depends(schemas.User),
    current_user: schemas.UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/", response_model=schemas.User)
async def read_users(
    *,
    db: Database = Depends(get_db),
    offset: int = 0,
    limit: int = 100,
    current_user: schemas.UserInDB = Depends(deps.get_current_active_superuser)
) -> List[schemas.User]:
    users = await crud.user.get_multi(db, offset=offset, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    db: Database = Depends(get_db),
    current_user: schemas.UserInDB = Depends(deps.get_current_active_superuser),
) -> Any:
    user = await crud.user.get_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists in the system",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user
