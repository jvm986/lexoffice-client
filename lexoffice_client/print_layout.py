from uuid import UUID
from pydantic import BaseModel


class PrintLayout(BaseModel):
    id: UUID
    name: str
    default: bool
