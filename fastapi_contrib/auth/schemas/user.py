from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive vai API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to return via API
class User(UserInDBBase):
    pass


# Properties to store in DB
class UserInDB(UserInDBBase):
    hashed_password: str
