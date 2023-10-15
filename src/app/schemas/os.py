from typing import List, Optional

from pydantic import BaseModel, Field

from src.app.schemas.base import MongoID
from src.app.schemas.images import Images
from src.app.schemas.mixins import IDModelMixin
from src.emulations.types import EmuType


class OS(BaseModel):
    name: str
    version: str
    vendor: str
    full_description: str = Field(alias="fullDescription")
    terminal_enable: bool = Field(alias="terminalEnable")
    graphics_enable: bool = Field(alias="graphicsEnable")
    photos: Optional[List[Images]]
    parent_id: Optional[List[MongoID]] = Field(alias="parentId")
    child_id: Optional[List[MongoID]] = Field(alias="childId")
    is_free: bool = Field(alias="isFree")
    can_downloaded_raw: bool = Field(alias="canDownloadedRaw")


class OSDatabase(OS):
    start_config: Optional[str] = Field(alias="startConfig")
    stop_config: Optional[str] = Field(alias="stopConfig")
    template_disk_path: Optional[str] = Field(alias="templateDiskPath")
    emulation_type: Optional[EmuType] = Field(alias="emulationType")


class OSResponse(OS, IDModelMixin):
    ...


class OSAdmin(OSDatabase, IDModelMixin):
    ...


OSMulti = OSResponse | List[OSResponse]
OSAdminMulti = OSAdmin | List[OSAdmin]
