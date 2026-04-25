from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Profile(BaseModel):
    organizationId: UUID
    companyName: Optional[str] = None
    created: Optional[dict] = None
    connectionId: Optional[UUID] = None
    taxType: Optional[str] = None
    smallBusiness: Optional[bool] = None
    distanceSalesPrinciple: Optional[str] = None
    taxExempt: Optional[bool] = None
    defaultLanguage: Optional[str] = None
    defaultCurrency: Optional[str] = None
    contactEmail: Optional[str] = None
