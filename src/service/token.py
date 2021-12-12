from typing import Optional

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.service.base import BaseService
from src.service.mixins import ServiceCRUDMixin
import src.service.user


class TokenService(ServiceCRUDMixin, BaseService):
    def __init__(self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = 'token'
        self.token = None

    async def remove(self, token=None) -> bool:
        token = await self.database.get(self.model_name, filters={"token": token})
        if token is not None:
            self.obj_id = token['_id']
            return await super().remove()
        return False

    async def check_token(self, token: str) -> bool:
        token = await self.database.get(self.model_name, filters={"token": token})
        self.token = token
        return token is not None

    async def check_token_and_check_permission(self, token: str) -> bool:
        valid_token = await self.check_token(token)
        if not valid_token:
            return False
        user = await src.service.user.UserService(self.token['user_id'], database=self.database).get()
        return user['is_admin']

