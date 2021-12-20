from typing import List, Optional

from pydantic import BaseModel

from src.app.schemas.base import MongoID
from src.app.schemas.images import Images
from src.app.schemas.mixins import IDModelMixin
from src.emulations.types import EmuType


class OS(BaseModel):
    name: str
    version: str
    vendor: str
    full_description: str
    terminal_enable: bool
    graphics_enable: bool
    photos: Optional[List[Images]]
    parent_id: Optional[List[MongoID]]
    child_id: Optional[List[MongoID]]
    is_free: bool
    can_downloaded_raw: bool


class OSDatabase(OS):
    start_config: Optional[str]
    stop_config: Optional[str]
    template_disk_path: Optional[str]
    emulation_type: Optional[EmuType]


class OSResponse(OS, IDModelMixin):
    ...


class OSAdmin(OSDatabase, IDModelMixin):
    ...


OSMulti = OSResponse | List[OSResponse]
OSAdminMulti = OSAdmin | List[OSAdmin]
