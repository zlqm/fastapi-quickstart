from fastapi_contrib.core.config import CONFIG

from . import models

CONFIG["JWT_EXPIRE_MINUTES"] = 60 * 24 * 3
CONFIG["JWT_ALGORITHM"] = "HS256"
CONFIG["JWT_SECRET_KEY"] = "to-be-changed"
CONFIG["JWT_TOKEN_URL"] = "/api/v1/login/access-token"
