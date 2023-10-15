from typing import List

from pydantic import BaseModel, Field

from src.app.schemas.mixins import IDModelMixin


class User(BaseModel):
    login: str


class UserCreation(User):
    password: str


class UserDB(UserCreation):
    is_admin: bool = Field(alias="isAdmin", default=False)

    class Config:
        allow_population_by_field_name = True


class UserResponse(User, IDModelMixin):
    ...


class UserAdminResponse(User, IDModelMixin):
    is_admin: bool = Field(alias="isAdmin", default=False)

    class Config:
        allow_population_by_field_name = True


UserMulti = UserResponse | List[UserResponse]
