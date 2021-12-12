from typing import List

from pydantic import BaseModel, HttpUrl

from src.app.schemas.mixins import IDModelMixin


class Images(BaseModel):
    url: HttpUrl


class ImagesResponse(Images, IDModelMixin):
    ...


ImagesMulti = ImagesResponse | List[ImagesResponse]
