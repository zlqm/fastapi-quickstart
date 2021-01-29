from datetime import timedelta
from typing import Any

from databases import Database
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_contrib.auth import crud, schemas, security
from fastapi_contrib.auth.apis import deps
from fastapi_contrib.core.apis.deps import get_db
from fastapi_contrib.core.config import CONFIG

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    db: Database = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = await crud.user.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User"
        )
    access_token_expires = timedelta(minutes=CONFIG["JWT_EXPIRE_MINUTES"])
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=schemas.User)
async def test_token(
    current_user: schemas.UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    return current_user
