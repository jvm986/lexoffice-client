from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel

from lexoffice_client.sales_voucher_common import (
    LineItem,
    PaymentConditions,
    SalesVoucherAddress,
    ShippingConditions,
    TaxConditions,
    TotalPrice,
)


class RecurringTemplate(BaseModel):
    id: UUID
    organizationId: UUID
    createdDate: datetime
    updatedDate: datetime
    version: int
    archived: Optional[bool] = None
    language: Optional[str] = None
    address: Optional[SalesVoucherAddress] = None
    lineItems: Optional[List[LineItem]] = None
    totalPrice: Optional[TotalPrice] = None
    taxConditions: Optional[TaxConditions] = None
    paymentConditions: Optional[PaymentConditions] = None
    shippingConditions: Optional[ShippingConditions] = None
    title: Optional[str] = None
    introduction: Optional[str] = None
    remark: Optional[str] = None
    printLayoutId: Optional[UUID] = None
    nextExecutionDate: Optional[datetime] = None
    executionInterval: Optional[str] = None
    lastExecutionDate: Optional[datetime] = None
    executionStatus: Optional[str] = None
