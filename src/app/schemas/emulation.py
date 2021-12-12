from typing import Optional

from pydantic import BaseModel, AnyUrl


class Emulation(BaseModel):
    terminal: Optional[AnyUrl]
    graphical: Optional[AnyUrl]
