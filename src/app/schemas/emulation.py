from typing import Optional

from pydantic import BaseModel, AnyUrl

from src.emulations.types import GraphicalTypes


class Emulation(BaseModel):
    terminal: Optional[AnyUrl]
    graphical: Optional[AnyUrl]
    graphical_type: Optional[GraphicalTypes]
