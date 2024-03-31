from typing import Optional

from pydantic import BaseModel, AnyUrl, Field

from src.emulations.types import GraphicalTypes


class Emulation(BaseModel):
    terminal: Optional[AnyUrl] = Field(default=None)
    graphical: Optional[AnyUrl] = Field(default=None)
    graphical_type: Optional[GraphicalTypes] = Field(alias="graphicalType", default=None)
    emulation_id: str = Field(alias="emulationId")

    class Config:
        populate_by_name = True

