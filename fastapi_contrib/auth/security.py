from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from fastapi_contrib.core.config import CONFIG

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    print(f"{plain_password=} {hashed_password=}")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta) -> str:
    expires_delta = expires_delta
    expire_at = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire_at, "sub": str(subject)}
    return jwt.encode(
        to_encode,
        CONFIG.JWT_SECRET_KEY,
        algorithm=CONFIG.JWT_ALGORITHM,
    )
