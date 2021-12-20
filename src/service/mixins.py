# noinspection PyUnresolvedReferences
class ServiceGetMixin:
    async def get(self) -> list | dict:
        if self.obj_id:
            obj = await self.database.get(self.model_name, {"id": self.obj_id})
            return obj
        else:
            obj = await self.database.get_all(self.model_name)
            return obj


# noinspection PyUnresolvedReferences
class ServiceCreateMixin:
    async def create(self, params: dict) -> dict:
        obj = await self.database.create(self.model_name, params)
        return obj


# noinspection PyUnresolvedReferences
class ServiceUpdateMixin:
    async def update(self, params: dict) -> dict:
        filters = {"id": self.obj_id}
        obj = await self.database.update(self.model_name, filters, params)
        return obj


# noinspection PyUnresolvedReferences
class ServiceRemoveMixin:
    async def remove(self) -> bool:
        filters = {"id": self.obj_id}
        return await self.database.delete(self.model_name, filters)


class ServiceCRUDMixin(
    ServiceCreateMixin, ServiceGetMixin, ServiceUpdateMixin, ServiceRemoveMixin
):
    ...
