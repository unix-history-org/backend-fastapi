from typing import Optional

from pydantic import BaseModel, AnyUrl, Field

from src.emulations.types import GraphicalTypes


class Emulation(BaseModel):
    terminal: Optional[AnyUrl]
    graphical: Optional[AnyUrl]
    graphical_type: Optional[GraphicalTypes] = Field(alias="graphicalType")
