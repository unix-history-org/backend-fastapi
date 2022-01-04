from typing import List

from pydantic import BaseModel, HttpUrl


class Images(BaseModel):
    url: HttpUrl


ImagesMulti = Images | List[Images]
