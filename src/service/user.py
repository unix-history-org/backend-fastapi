from typing import Optional

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.service.base import BaseService
from src.service.mixins import ServiceCRUDMixin
import src.service.token
from src.cryptography.cryptography import Crypto


class UserService(ServiceCRUDMixin, BaseService):
    def __init__(self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = 'user'
        self.user = None
        self.user_login = None
        self.password = None
        self.hash_password = None

    async def _set_user_info(self, params):
        self.user_login = params.get('login')
        self.user = await self.database.get(self.model_name, filters={"login": self.user_login})
        self.password = params.get('password')
        self.hash_password = Crypto.full_passwd(self.password)
        self.token = Crypto.gen_token_for_auth(self.user_login)
        self.is_admin = params.get('is_admin') or False

    async def _create_token(self):
        await src.service.token.TokenService(database=self.database).create(
            {
                'token': self.token,
                'user_id': self.user['_id']
            }
        )

    async def register(self, params):
        await self._set_user_info(params)
        if self.user is None:
            ret = await self.database.create(self.model_name, {
                "login": self.user_login,
                "password": self.hash_password,
                "is_admin": self.is_admin
            })
            self.user = ret
        else:
            return {
                "detail": "User exist"
            }, ""
        await self._create_token()
        del ret['password']
        return self._append_id_object(ret), self.token

    async def login(self, params):
        await self._set_user_info(params)
        if self.user is not None:
            if Crypto.is_correct_password(self.user['password'], self.password):
                await self._create_token()
            else:
                return {
                           "detail": "Wrong password"
                       }, ""
        else:
            return {
                       "detail": "User doesn't exist"
                   }, ""
        ret = self.user
        del ret['password']
        return self._append_id_object(ret), self.token

    async def logout(self, token):
        return await src.service.token.TokenService(database=self.database).remove(token)

    async def set_admin(self):
        return await self.update({"is_admin": True})

    async def unset_admin(self):
        return await self.update({"is_admin": False})
