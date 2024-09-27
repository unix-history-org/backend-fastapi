from typing import Optional

from app.core.db.base_layer import AbstractDatabaseLayer
from app.service.base import BaseService
from app.service.mixins import ServiceCRUDMixin


class OSService(ServiceCRUDMixin, BaseService):
    def __init__(
        self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer
    ) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = "os"
