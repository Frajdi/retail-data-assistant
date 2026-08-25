from typing import Any
from pydantic import BaseModel

from src.domain.errors import QueryErrorType


class QuerySuccess(BaseModel):
    data: list[dict[str, Any]]

class QueryFailure(BaseModel):
    error_type: QueryErrorType
    error_message: str
