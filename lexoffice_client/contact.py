from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, model_validator


class Address(BaseModel):
    supplement: Optional[str] = None
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    countryCode: str


class Addresses(BaseModel):
    billing: Optional[List[Address]] = None
    shipping: Optional[List[Address]] = None


class CompanyContactPerson(BaseModel):
    salutation: Optional[str] = None
    firstName: Optional[str] = None
    lastName: str
    primary: Optional[bool] = None
    emailAddress: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None


class Company(BaseModel):
    allowTaxFreeInvoices: Optional[bool] = None
    name: str
    taxNumber: Optional[str] = None
    vatRegistrationId: Optional[str] = None
    contactPersons: Optional[List[CompanyContactPerson]] = None


class Person(BaseModel):
    salutation: Optional[str] = None
    firstName: Optional[str] = None
    lastName: str


class Role(BaseModel):
    number: Optional[int] = None


class Roles(BaseModel):
    customer: Optional[Role] = None
    vendor: Optional[Role] = None


class EmailAddresses(BaseModel):
    business: Optional[List[str]] = None
    office: Optional[List[str]] = None
    private: Optional[List[str]] = None
    other: Optional[List[str]] = None


class PhoneNumbers(BaseModel):
    business: Optional[List[str]] = None
    office: Optional[List[str]] = None
    mobile: Optional[List[str]] = None
    private: Optional[List[str]] = None
    fax: Optional[List[str]] = None
    other: Optional[List[str]] = None


class ContactXRechnung(BaseModel):
    buyerReference: Optional[str] = None
    vendorNumberAtCustomer: Optional[str] = None


class ContactReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    version: Optional[int] = None
    archived: bool


class ContactWritable(BaseModel):
    version: Optional[int] = None
    roles: Roles
    company: Optional[Company] = None
    person: Optional[Person] = None
    addresses: Optional[Addresses] = None
    note: Optional[str] = None
    emailAddresses: Optional[EmailAddresses] = None
    phoneNumbers: Optional[PhoneNumbers] = None
    xRechnung: Optional[ContactXRechnung] = None

    @model_validator(mode="after")
    def check_model(self) -> "ContactWritable":
        if bool(self.company) == bool(self.person):
            raise ValueError("Exactly one of 'company' or 'person' must be set.")
        return self


class Contact(ContactReadOnly, ContactWritable):
    pass
