from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class CreateResponse(BaseModel):
    id: UUID
    resourceUri: str
    createdDate: datetime
    updatedDate: datetime
    version: int


class PaginatedResponse(BaseModel, Generic[T]):
    content: List[T]
    first: bool
    last: bool
    number: int
    size: int
    numberOfElements: int
    totalElements: int
    totalPages: int
    sort: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_response(cls, data: dict, item_type: Type[T]) -> "PaginatedResponse[T]":
        data["content"] = [item_type.model_validate(item) for item in data.get("content", [])]
        return cls.model_validate(data)
