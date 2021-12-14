# noinspection PyUnresolvedReferences
class ServiceGetMixin:
    async def get(self) -> list | dict:
        if self.obj_id:
            obj = await self.database.get(self.model_name, {self.id_key: self.obj_id})
            return self._append_id_object(obj)
        else:
            obj = await self.database.get_all(self.model_name)
            return self._append_id_to_list(obj)


# noinspection PyUnresolvedReferences
class ServiceCreateMixin:
    async def create(self, params: dict) -> dict:
        obj = await self.database.create(self.model_name, params)

        return self._append_id_object(obj)


# noinspection PyUnresolvedReferences
class ServiceUpdateMixin:
    async def update(self, params: dict) -> dict:
        filters = {self.id_key: self.obj_id}
        del params["id"]
        obj = await self.database.update(self.model_name, filters, params)
        return self._append_id_object(obj)


# noinspection PyUnresolvedReferences
class ServiceRemoveMixin:
    async def remove(self) -> bool:
        filters = {self.id_key: self.obj_id}
        anw = await self.database.delete(self.model_name, filters)
        return anw


class ServiceCRUDMixin(
    ServiceCreateMixin,
    ServiceGetMixin,
    ServiceUpdateMixin,
    ServiceRemoveMixin
):
    ...

