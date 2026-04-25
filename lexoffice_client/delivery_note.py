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
    TaxConditions,
)


class DeliveryNoteReadOnly(BaseModel):
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


class DeliveryNoteWritable(BaseModel):
    version: Optional[int] = None
    archived: Optional[bool] = None
    language: Optional[str] = None
    voucherDate: Optional[Union[str, date, datetime]] = None
    address: Optional[SalesVoucherAddress] = None
    lineItems: Optional[List[LineItem]] = None
    taxConditions: Optional[TaxConditions] = None
    deliveryTerms: Optional[str] = None
    shippingConditions: Optional[ShippingConditions] = None
    title: Optional[str] = None
    introduction: Optional[str] = None
    remark: Optional[str] = None
    printLayoutId: Optional[UUID] = None


class DeliveryNote(DeliveryNoteReadOnly, DeliveryNoteWritable):
    pass
