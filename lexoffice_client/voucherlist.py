from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class VoucherlistItem(BaseModel):
    id: UUID
    voucherType: Optional[str] = None
    voucherStatus: Optional[str] = None
    voucherNumber: Optional[str] = None
    voucherDate: Optional[datetime] = None
    contactId: Optional[UUID] = None
    contactName: Optional[str] = None
    totalAmount: Optional[float] = None
    openAmount: Optional[float] = None
    currency: Optional[str] = None
    archived: Optional[bool] = None
    dueDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None
