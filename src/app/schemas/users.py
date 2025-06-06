from typing import List

from pydantic import BaseModel, Field

from app.schemas.mixins import IDModelMixin


class User(BaseModel):
    login: str


class UserCreation(User):
    password: str


class UserDB(UserCreation):
    is_admin: bool = Field(alias="isAdmin", default=False)

    class Config:  # pylint: disable=R0903
        populate_by_name = True


class UserResponse(User, IDModelMixin):
    ...


class UserAdminResponse(User, IDModelMixin):
    is_admin: bool = Field(alias="isAdmin", default=False)

    class Config:  # pylint: disable=R0903
        populate_by_name = True


UserMulti = UserResponse | List[UserResponse]
