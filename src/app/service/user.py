from typing import Optional, Tuple

from app.core.db.base_layer import AbstractDatabaseLayer
from app.service.base import BaseService
from app.service.mixins import ServiceCRUDMixin
from cryptography.cryptography import Crypto


class UserService(ServiceCRUDMixin, BaseService):
    def __init__(
        self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer
    ) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = "user"
        self._user = None
        self._user_login = None
        self._password = None
        self._hash_password = None
        self._token = None
        self._is_admin = None

    async def _set_user_info(self, params: dict) -> None:
        self._user_login = params.get("login")
        self._user = await self.database.get(
            self.model_name, filters={"login": self._user_login}
        )
        self._password = params.get("password")
        self._hash_password = Crypto.full_passwd(self._password)
        self._token = Crypto.gen_token_for_auth(self._user_login)
        self._is_admin = params.get("is_admin", False)

    async def _create_token(self):
        await TokenService(database=self.database).create(
            {"token": self._token, "user_id": self._user["id"]}
        )

    async def _prepare_data_to_send(self):
        del self._user["password"]

    async def create(
        self, params: Optional[dict] = None
    ) -> Tuple[Optional[dict], Optional[str], Optional[dict]]:
        await self._set_user_info(params)
        if self._user is not None:
            return None, None, {"detail": "User exists"}

        self._user = await self.database.create(
            self.model_name,
            {
                "login": self._user_login,
                "password": self._hash_password,
                "is_admin": self._is_admin,
            },
        )

        await self._create_token()
        await self._prepare_data_to_send()

        return self._user, self._token, None

    async def login(
        self, params: Optional[dict] = None
    ) -> Tuple[Optional[dict], Optional[str], Optional[dict]]:
        await self._set_user_info(params)
        if self._user is None:
            return None, None, {"detail": "User doesn't exist"}

        if not Crypto.is_correct_password(self._user["password"], self._password):
            return None, None, {"detail": "Wrong password"}

        await self._create_token()
        await self._prepare_data_to_send()

        return self._user, self._token, None

    async def logout(self, token: str) -> bool:
        return await TokenService(database=self.database).remove(token)

    async def set_admin(self, is_admin=True) -> dict:
        return await self.update({"is_admin": is_admin})


class TokenService(ServiceCRUDMixin, BaseService):
    def __init__(
        self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer
    ) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = "token"
        self.token = None

    async def remove(  # pylint: disable=W1113,W0221
        self, token: str = None, *args, **kwargs
    ) -> bool:
        token = await self.database.get(self.model_name, filters={"token": token})
        if token is not None:
            self.obj_id = token["id"]
            return await super().remove()
        return False

    async def check_token(self, token: str) -> bool:
        self.token = await self.database.get(self.model_name, filters={"token": token})
        return self.token is not None

    async def check_token_and_check_permission(self, token: str) -> bool:
        valid_token = await self.check_token(token)
        if not valid_token:
            return False
        user = await UserService(self.token["user_id"], database=self.database).get()
        if user is None:
            return False
        return user["is_admin"]
