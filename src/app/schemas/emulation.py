from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.emulations.types import GraphicalTypes


class Emulation(BaseModel):
    terminal: Optional[str] = Field(default=None)
    graphical: Optional[str] = Field(default=None)
    graphical_type: Optional[GraphicalTypes] = Field(
        alias="graphicalType", default=None
    )
    emulation_id: UUID = Field(alias="emulationId")

    class Config:  # pylint: disable=R0903
        populate_by_name = True
