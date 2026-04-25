from datetime import date, datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

from lexoffice_client.sales_voucher_common import (
    Files,
    LineItem,
    RelatedVoucher,
    SalesVoucherAddress,
    SalesVoucherStatus,
    ShippingConditions,
    TaxAmount,
    TaxConditions,
    TotalPrice,
)


class CreditNoteReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    createdDate: datetime
    updatedDate: datetime
    version: int
    voucherStatus: Optional[SalesVoucherStatus] = None
    voucherNumber: Optional[str] = None
    voucherDate: Optional[Union[str, date, datetime]] = None
    relatedVouchers: Optional[List[RelatedVoucher]] = None
    files: Optional[Files] = None


class CreditNoteWritable(BaseModel):
    version: Optional[int] = None
    archived: Optional[bool] = None
    language: Optional[str] = None
    voucherDate: Optional[Union[str, date, datetime]] = None
    address: Optional[SalesVoucherAddress] = None
    lineItems: Optional[List[LineItem]] = None
    totalPrice: Optional[TotalPrice] = None
    taxAmounts: Optional[List[TaxAmount]] = None
    taxConditions: Optional[TaxConditions] = None
    shippingConditions: Optional[ShippingConditions] = None
    title: Optional[str] = None
    introduction: Optional[str] = None
    remark: Optional[str] = None
    printLayoutId: Optional[UUID] = None


class CreditNote(CreditNoteReadOnly, CreditNoteWritable):
    pass
