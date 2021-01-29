from sqlalchemy import Boolean, Column, String, Table

from fastapi_contrib.core.db import metadata
from fastapi_contrib.core.utils import random_string

User = Table(
    "user",
    metadata,
    Column("id", String(32), primary_key=True, default=random_string),
    Column("full_name", String(255), index=True),
    Column("email", String(255), unique=True, index=True, nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("is_active", Boolean, default=True),
    Column("is_superuser", Boolean, default=False),
)
