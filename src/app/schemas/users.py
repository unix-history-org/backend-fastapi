from typing import List

from pydantic import BaseModel

from src.app.schemas.mixins import IDModelMixin


class User(BaseModel):
    login: str


class UserCreation(User):
    password: str


class UserDB(UserCreation):
    is_admin: bool = False


class UserResponse(User, IDModelMixin):
    ...


class UserAdminResponse(User, IDModelMixin):
    is_admin: bool = False


UserMulti = UserResponse | List[UserResponse]
