from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ArticleType(str, Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"


class LeadingPrice(str, Enum):
    NET = "NET"
    GROSS = "GROSS"


class ArticlePrice(BaseModel):
    netPrice: Optional[float] = None
    grossPrice: Optional[float] = None
    leadingPrice: Optional[LeadingPrice] = None
    currency: Optional[str] = None
    taxRate: Optional[float] = None


class ArticleReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    createdDate: datetime
    updatedDate: datetime
    version: int
    archived: Optional[bool] = None


class ArticleWritable(BaseModel):
    title: str
    type: ArticleType
    articleNumber: Optional[str] = None
    gtin: Optional[str] = None
    note: Optional[str] = None
    unitName: str
    description: Optional[str] = None
    price: Optional[ArticlePrice] = None
    version: Optional[int] = None


class Article(ArticleReadOnly, ArticleWritable):
    pass
