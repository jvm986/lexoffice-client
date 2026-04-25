from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class PaymentItem(BaseModel):
    paymentItemType: Optional[str] = None
    postingDate: Optional[datetime] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


class Payment(BaseModel):
    openAmount: Optional[float] = None
    currency: Optional[str] = None
    paymentStatus: Optional[str] = None
    voucherId: Optional[UUID] = None
    voucherType: Optional[str] = None
    voucherStatus: Optional[str] = None
    paidDate: Optional[datetime] = None
    paymentItems: Optional[List[PaymentItem]] = None
