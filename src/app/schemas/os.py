from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from src.app.schemas.base import MongoID
from src.app.schemas.images import Images
from src.app.schemas.mixins import IDModelMixin
from src.emulations.types import EmuType


class OS(BaseModel):
    name: str
    version: str
    vendor: str
    short_description: str = Field(alias="shortDescription")
    full_description: str = Field(alias="fullDescription")
    terminal_enable: bool = Field(alias="terminalEnable")
    graphics_enable: bool = Field(alias="graphicsEnable")
    photos: Optional[List[Images]] = Field(default=None)
    main_photo: Optional[HttpUrl] = Field(alias="mainPhoto", default=None)
    parent_id: Optional[List[MongoID]] = Field(alias="parentId", default=None)
    child_id: Optional[List[MongoID]] = Field(alias="childId", default=None)
    is_free: bool = Field(alias="isFree")
    can_downloaded_raw: bool = Field(alias="canDownloadedRaw")
    os_username: str = Field(alias="osUsername", default="uh")
    os_password: str = Field(alias="osPassword", default="uh")
    os_root_password: str = Field(alias="osRootPassword", default="uh")

    class Config:  # pylint: disable=R0903
        populate_by_name = True


class OSDatabase(OS):
    start_config: Optional[str] = Field(alias="startConfig", default=None)
    stop_config: Optional[str] = Field(alias="stopConfig", default=None)
    template_disk_path: Optional[str] = Field(alias="templateDiskPath", default=None)
    emulation_type: Optional[EmuType] = Field(alias="emulationType", default=None)
    lifetime: Optional[int] = Field(default=60 * 15)

    class Config:  # pylint: disable=R0903
        populate_by_name = True


class OSResponse(OS, IDModelMixin):
    ...


class OSAdmin(OSDatabase, IDModelMixin):
    ...


class OSAdminPatch(OSDatabase, IDModelMixin):
    id: Optional[MongoID] = Field(default=None)
    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    short_description: Optional[str] = Field(alias="shortDescription", default=None)
    full_description: Optional[str] = Field(alias="fullDescription", default=None)
    terminal_enable: Optional[bool] = Field(alias="terminalEnable", default=None)
    graphics_enable: Optional[bool] = Field(alias="graphicsEnable", default=None)
    is_free: Optional[bool] = Field(alias="isFree", default=None)
    can_downloaded_raw: Optional[bool] = Field(alias="canDownloadedRaw", default=None)


OSMulti = OSResponse | List[OSResponse]
OSAdminMulti = OSAdmin | List[OSAdmin]
