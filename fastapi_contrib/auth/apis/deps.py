from databases import Database
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from fastapi_contrib.auth import crud, schemas
from fastapi_contrib.core.apis.deps import get_db
from fastapi_contrib.core.config import CONFIG

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=CONFIG.JWT_TOKEN_URL)


async def get_current_user(
    db: Database = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> schemas.UserInDB:
    try:
        payload = jwt.decode(
            token, CONFIG.JWT_SECRET_KEY, algorithms=[CONFIG.JWT_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not found"
        )
    return user


async def get_current_active_user(
    current_user: schemas.UserInDB = Depends(get_current_user),
) -> schemas.UserInDB:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_active_superuser(
    current_active_user: schemas.UserInDB = Depends(get_current_active_user),
) -> schemas.UserInDB:
    if not current_active_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_active_user
