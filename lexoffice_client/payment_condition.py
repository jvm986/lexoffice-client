from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class PaymentDiscountCondition(BaseModel):
    discountPercentage: Optional[float] = None
    discountRange: Optional[int] = None


class PaymentCondition(BaseModel):
    id: UUID
    organizationId: Optional[UUID] = None
    paymentTermLabel: Optional[str] = None
    paymentTermLabelTemplate: Optional[str] = None
    paymentTermDuration: Optional[int] = None
    paymentDiscountConditions: Optional[List[PaymentDiscountCondition]] = None
