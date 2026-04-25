from datetime import date, datetime
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel

from lexoffice_client.sales_voucher_common import (
    Files,
    LineItem,
    PaymentConditions,
    RelatedVoucher,
    SalesVoucherAddress,
    SalesVoucherStatus,
    ShippingConditions,
    TaxAmount,
    TaxConditions,
    TotalPrice,
)


class DownPaymentInvoice(BaseModel):
    id: UUID
    organizationId: UUID
    createdDate: datetime
    updatedDate: datetime
    version: int
    archived: Optional[bool] = None
    language: Optional[str] = None
    voucherStatus: Optional[SalesVoucherStatus] = None
    voucherNumber: Optional[str] = None
    voucherDate: Optional[Union[str, date, datetime]] = None
    dueDate: Optional[Union[str, date, datetime]] = None
    address: Optional[SalesVoucherAddress] = None
    lineItems: Optional[List[LineItem]] = None
    totalPrice: Optional[TotalPrice] = None
    taxAmounts: Optional[List[TaxAmount]] = None
    taxConditions: Optional[TaxConditions] = None
    paymentConditions: Optional[PaymentConditions] = None
    shippingConditions: Optional[ShippingConditions] = None
    relatedVouchers: Optional[List[RelatedVoucher]] = None
    title: Optional[str] = None
    introduction: Optional[str] = None
    remark: Optional[str] = None
    printLayoutId: Optional[UUID] = None
    files: Optional[Files] = None
