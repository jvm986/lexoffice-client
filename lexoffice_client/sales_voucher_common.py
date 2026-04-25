from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel


class SalesVoucherStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    PAIDOFF = "paidoff"
    VOIDED = "voided"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class SalesTaxType(str, Enum):
    NET = "net"
    GROSS = "gross"
    VATFREE = "vatfree"
    INTRA_COMMUNITY_SUPPLY = "intraCommunitySupply"
    CONSTRUCTION_SERVICE_13B = "constructionService13b"
    EXTERNAL_SERVICE_13B = "externalService13b"
    THIRD_PARTY_COUNTRY_SERVICE = "thirdPartyCountryService"
    THIRD_PARTY_COUNTRY_DELIVERY = "thirdPartyCountryDelivery"
    PHOTOVOLTAIC_EQUIPMENT = "photovoltaicEquipment"


class SalesTaxSubType(str, Enum):
    DISTANCE_SALES = "distanceSales"
    ELECTRONIC_SERVICES = "electronicServices"


class ShippingType(str, Enum):
    SERVICE = "service"
    SERVICE_PERIOD = "serviceperiod"
    DELIVERY = "delivery"
    DELIVERY_PERIOD = "deliveryperiod"
    NONE = "none"


class LineItemType(str, Enum):
    CUSTOM = "custom"
    TEXT = "text"
    SERVICE = "service"
    MATERIAL = "material"


class ElectronicDocumentProfile(str, Enum):
    NONE = "NONE"
    EN16931 = "EN16931"
    XRECHNUNG = "XRECHNUNG"


class SalesVoucherAddress(BaseModel):
    contactId: Optional[UUID] = None
    name: Optional[str] = None
    supplement: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    countryCode: Optional[str] = None
    contactPerson: Optional[str] = None


class UnitPrice(BaseModel):
    currency: Optional[str] = None
    netAmount: Optional[float] = None
    grossAmount: Optional[float] = None
    taxRatePercentage: Optional[float] = None


class Discount(BaseModel):
    percentage: Optional[float] = None
    absolute: Optional[float] = None


class LineItem(BaseModel):
    id: Optional[UUID] = None
    type: Optional[LineItemType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unitName: Optional[str] = None
    unitPrice: Optional[UnitPrice] = None
    discountPercentage: Optional[float] = None
    lineItemAmount: Optional[float] = None
    subItems: Optional[List["LineItem"]] = None
    alternative: Optional[bool] = None
    optional: Optional[bool] = None


class TotalPrice(BaseModel):
    currency: Optional[str] = None
    totalNetAmount: Optional[float] = None
    totalGrossAmount: Optional[float] = None
    totalTaxAmount: Optional[float] = None
    totalDiscountAbsolute: Optional[float] = None
    totalDiscountPercentage: Optional[float] = None


class TaxAmount(BaseModel):
    taxRatePercentage: Optional[float] = None
    taxAmount: Optional[float] = None
    netAmount: Optional[float] = None


class TaxConditions(BaseModel):
    taxType: Optional[SalesTaxType] = None
    taxSubType: Optional[SalesTaxSubType] = None
    taxTypeNote: Optional[str] = None


class PaymentDiscountConditions(BaseModel):
    discountPercentage: Optional[float] = None
    discountRange: Optional[int] = None


class PaymentConditions(BaseModel):
    paymentTermLabel: Optional[str] = None
    paymentTermLabelTemplate: Optional[str] = None
    paymentTermDuration: Optional[int] = None
    paymentDiscountConditions: Optional[List[PaymentDiscountConditions]] = None


class ShippingConditions(BaseModel):
    shippingDate: Optional[Union[str, date, datetime]] = None
    shippingEndDate: Optional[Union[str, date, datetime]] = None
    shippingType: Optional[ShippingType] = None


class RelatedVoucher(BaseModel):
    id: Optional[UUID] = None
    voucherNumber: Optional[str] = None
    voucherType: Optional[str] = None


class XRechnung(BaseModel):
    buyerReference: Optional[str] = None
    vendorNumberAtCustomer: Optional[str] = None
    invoiceRecipientsEPartyId: Optional[str] = None


class Files(BaseModel):
    documentFileId: Optional[UUID] = None
