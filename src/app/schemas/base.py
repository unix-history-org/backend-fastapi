from pydantic import StringConstraints
from typing_extensions import Annotated

MongoID = Annotated[str, "MongoID", StringConstraints(max_length=24, min_length=24)]
