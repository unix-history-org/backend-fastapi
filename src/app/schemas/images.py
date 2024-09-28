from typing import List, Annotated

from pydantic import BaseModel, HttpUrl, AfterValidator

HttpUrlString = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]


class Images(BaseModel):
    url: HttpUrlString


ImagesMulti = Images | List[Images]
