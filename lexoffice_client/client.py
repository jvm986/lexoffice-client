from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

import httpx

from lexoffice_client.article import Article, ArticleWritable
from lexoffice_client.common import CreateResponse, PaginatedResponse
from lexoffice_client.contact import Contact, ContactWritable
from lexoffice_client.country import Country
from lexoffice_client.credit_note import CreditNote, CreditNoteWritable
from lexoffice_client.delivery_note import DeliveryNote, DeliveryNoteWritable
from lexoffice_client.down_payment_invoice import DownPaymentInvoice
from lexoffice_client.dunning import Dunning, DunningWritable
from lexoffice_client.event_subscription import (
    EventSubscription,
    EventSubscriptionWritable,
)
from lexoffice_client.file import File, Type as FileType
from lexoffice_client.invoice import Invoice, InvoiceWritable
from lexoffice_client.order_confirmation import (
    OrderConfirmation,
    OrderConfirmationWritable,
)
from lexoffice_client.payment import Payment
from lexoffice_client.payment_condition import PaymentCondition
from lexoffice_client.posting_category import PostingCategoryReadOnly
from lexoffice_client.print_layout import PrintLayout
from lexoffice_client.profile import Profile
from lexoffice_client.quotation import Quotation, QuotationWritable
from lexoffice_client.recurring_template import RecurringTemplate
from lexoffice_client.voucher import Voucher, VoucherWritable
from lexoffice_client.voucherlist import VoucherlistItem


class LexofficeClient:
    def __init__(
        self, access_token: str, base_url: str = "https://api.lexoffice.io/v1"
    ):
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            base_url=base_url,
            timeout=10,
        )

    def _check_response(self, response: httpx.Response, context: str) -> None:
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error {context}: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

    def _get_json(self, path: str, context: str) -> dict:
        response = self.client.get(path)
        self._check_response(response, context)
        return response.json()

    def _post_json(self, path: str, data: dict, context: str, params: Optional[Dict[str, str]] = None) -> dict:
        response = self.client.post(path, json=data, params=params)
        self._check_response(response, context)
        return response.json()

    def _put_json(self, path: str, data: dict, context: str) -> dict:
        response = self.client.put(path, json=data)
        self._check_response(response, context)
        return response.json()

    def _delete(self, path: str, context: str) -> None:
        response = self.client.delete(path)
        self._check_response(response, context)

    def _download(self, path: str, context: str, accept: str = "application/pdf") -> bytes:
        response = self.client.get(path, headers={"Accept": accept})
        self._check_response(response, context)
        return response.content

    def _get_paginated(
        self, path: str, params: Dict[str, Any], item_type: Type, context: str
    ) -> PaginatedResponse:
        query = {k: str(v) if not isinstance(v, str) else v for k, v in params.items() if v is not None}
        response = self.client.get(path, params=query)
        self._check_response(response, context)
        return PaginatedResponse.from_response(response.json(), item_type)

    # ── Ping ──

    def ping(self):
        response = self.client.get("/ping")
        self._check_response(response, "pinging Lexoffice API")

    # ── Profile ──

    def retrieve_profile(self) -> Profile:
        return Profile.model_validate(self._get_json("/profile", "retrieving profile"))

    # ── Contacts ──

    def create_contact(self, contact: ContactWritable) -> CreateResponse:
        data = self._post_json(
            "/contacts", contact.model_dump(exclude_none=True), "creating contact"
        )
        return CreateResponse.model_validate(data)

    def retrieve_contact(self, contact_id: UUID) -> Contact:
        return Contact.model_validate(
            self._get_json(f"/contacts/{contact_id}", "retrieving contact")
        )

    def update_contact(self, contact_id: UUID, contact: ContactWritable) -> CreateResponse:
        data = self._put_json(
            f"/contacts/{contact_id}",
            contact.model_dump(exclude_none=True),
            "updating contact",
        )
        return CreateResponse.model_validate(data)

    def filter_contacts(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        number: Optional[int] = None,
        customer: Optional[bool] = None,
        vendor: Optional[bool] = None,
        page: int = 0,
    ) -> PaginatedResponse[Contact]:
        params: Dict[str, Any] = {
            "email": email,
            "name": name,
            "number": number,
            "customer": str(customer).lower() if customer is not None else None,
            "vendor": str(vendor).lower() if vendor is not None else None,
            "page": page,
        }
        return self._get_paginated("/contacts", params, Contact, "filtering contacts")

    # ── Countries ──

    def list_countries(self) -> List[Country]:
        data = self._get_json("/countries", "listing countries")
        return [Country.model_validate(c) for c in data]

    # ── Articles ──

    def create_article(self, article: ArticleWritable) -> CreateResponse:
        data = self._post_json(
            "/articles", article.model_dump(exclude_none=True), "creating article"
        )
        return CreateResponse.model_validate(data)

    def retrieve_article(self, article_id: UUID) -> Article:
        return Article.model_validate(
            self._get_json(f"/articles/{article_id}", "retrieving article")
        )

    def update_article(self, article_id: UUID, article: ArticleWritable) -> CreateResponse:
        data = self._put_json(
            f"/articles/{article_id}",
            article.model_dump(exclude_none=True),
            "updating article",
        )
        return CreateResponse.model_validate(data)

    def delete_article(self, article_id: UUID) -> None:
        self._delete(f"/articles/{article_id}", "deleting article")

    def filter_articles(
        self,
        article_number: Optional[str] = None,
        gtin: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 0,
    ) -> PaginatedResponse[Article]:
        params: Dict[str, Any] = {
            "articleNumber": article_number,
            "gtin": gtin,
            "type": type,
            "page": page,
        }
        return self._get_paginated("/articles", params, Article, "filtering articles")

    # ── Invoices ──

    def create_invoice(
        self,
        invoice: InvoiceWritable,
        finalize: bool = False,
        preceding_sales_voucher_id: Optional[UUID] = None,
        closing_invoice: Optional[bool] = None,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        if preceding_sales_voucher_id:
            params["precedingSalesVoucherId"] = str(preceding_sales_voucher_id)
        if closing_invoice is not None:
            params["closingInvoice"] = str(closing_invoice).lower()
        data = self._post_json(
            "/invoices",
            invoice.model_dump(exclude_none=True, mode="json"),
            "creating invoice",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_invoice(self, invoice_id: UUID) -> Invoice:
        return Invoice.model_validate(
            self._get_json(f"/invoices/{invoice_id}", "retrieving invoice")
        )

    def update_invoice(self, invoice_id: UUID, invoice: InvoiceWritable) -> CreateResponse:
        data = self._put_json(
            f"/invoices/{invoice_id}",
            invoice.model_dump(exclude_none=True, mode="json"),
            "updating invoice",
        )
        return CreateResponse.model_validate(data)

    def download_invoice_file(self, invoice_id: UUID, accept: str = "application/pdf") -> bytes:
        return self._download(f"/invoices/{invoice_id}/file", "downloading invoice file", accept)

    # ── Credit Notes ──

    def create_credit_note(
        self,
        credit_note: CreditNoteWritable,
        finalize: bool = False,
        preceding_sales_voucher_id: Optional[UUID] = None,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        if preceding_sales_voucher_id:
            params["precedingSalesVoucherId"] = str(preceding_sales_voucher_id)
        data = self._post_json(
            "/credit-notes",
            credit_note.model_dump(exclude_none=True, mode="json"),
            "creating credit note",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_credit_note(self, credit_note_id: UUID) -> CreditNote:
        return CreditNote.model_validate(
            self._get_json(f"/credit-notes/{credit_note_id}", "retrieving credit note")
        )

    def download_credit_note_file(self, credit_note_id: UUID, accept: str = "application/pdf") -> bytes:
        return self._download(
            f"/credit-notes/{credit_note_id}/file", "downloading credit note file", accept
        )

    # ── Delivery Notes ──

    def create_delivery_note(
        self,
        delivery_note: DeliveryNoteWritable,
        finalize: bool = False,
        preceding_sales_voucher_id: Optional[UUID] = None,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        if preceding_sales_voucher_id:
            params["precedingSalesVoucherId"] = str(preceding_sales_voucher_id)
        data = self._post_json(
            "/delivery-notes",
            delivery_note.model_dump(exclude_none=True, mode="json"),
            "creating delivery note",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_delivery_note(self, delivery_note_id: UUID) -> DeliveryNote:
        return DeliveryNote.model_validate(
            self._get_json(f"/delivery-notes/{delivery_note_id}", "retrieving delivery note")
        )

    def download_delivery_note_file(self, delivery_note_id: UUID, accept: str = "application/pdf") -> bytes:
        return self._download(
            f"/delivery-notes/{delivery_note_id}/file", "downloading delivery note file", accept
        )

    # ── Down Payment Invoices ──

    def retrieve_down_payment_invoice(self, down_payment_invoice_id: UUID) -> DownPaymentInvoice:
        return DownPaymentInvoice.model_validate(
            self._get_json(
                f"/down-payment-invoices/{down_payment_invoice_id}",
                "retrieving down payment invoice",
            )
        )

    def download_down_payment_invoice_file(
        self, down_payment_invoice_id: UUID, accept: str = "application/pdf"
    ) -> bytes:
        return self._download(
            f"/down-payment-invoices/{down_payment_invoice_id}/file",
            "downloading down payment invoice file",
            accept,
        )

    # ── Dunnings ──

    def create_dunning(
        self,
        dunning: DunningWritable,
        finalize: bool = False,
        preceding_sales_voucher_id: Optional[UUID] = None,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        if preceding_sales_voucher_id:
            params["precedingSalesVoucherId"] = str(preceding_sales_voucher_id)
        data = self._post_json(
            "/dunnings",
            dunning.model_dump(exclude_none=True, mode="json"),
            "creating dunning",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_dunning(self, dunning_id: UUID) -> Dunning:
        return Dunning.model_validate(
            self._get_json(f"/dunnings/{dunning_id}", "retrieving dunning")
        )

    def download_dunning_file(self, dunning_id: UUID, accept: str = "application/pdf") -> bytes:
        return self._download(f"/dunnings/{dunning_id}/file", "downloading dunning file", accept)

    # ── Order Confirmations ──

    def create_order_confirmation(
        self,
        order_confirmation: OrderConfirmationWritable,
        finalize: bool = False,
        preceding_sales_voucher_id: Optional[UUID] = None,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        if preceding_sales_voucher_id:
            params["precedingSalesVoucherId"] = str(preceding_sales_voucher_id)
        data = self._post_json(
            "/order-confirmations",
            order_confirmation.model_dump(exclude_none=True, mode="json"),
            "creating order confirmation",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_order_confirmation(self, order_confirmation_id: UUID) -> OrderConfirmation:
        return OrderConfirmation.model_validate(
            self._get_json(
                f"/order-confirmations/{order_confirmation_id}",
                "retrieving order confirmation",
            )
        )

    def download_order_confirmation_file(
        self, order_confirmation_id: UUID, accept: str = "application/pdf"
    ) -> bytes:
        return self._download(
            f"/order-confirmations/{order_confirmation_id}/file",
            "downloading order confirmation file",
            accept,
        )

    # ── Quotations ──

    def create_quotation(
        self,
        quotation: QuotationWritable,
        finalize: bool = False,
    ) -> CreateResponse:
        params: Dict[str, str] = {}
        if finalize:
            params["finalize"] = "true"
        data = self._post_json(
            "/quotations",
            quotation.model_dump(exclude_none=True, mode="json"),
            "creating quotation",
            params=params or None,
        )
        return CreateResponse.model_validate(data)

    def retrieve_quotation(self, quotation_id: UUID) -> Quotation:
        return Quotation.model_validate(
            self._get_json(f"/quotations/{quotation_id}", "retrieving quotation")
        )

    def download_quotation_file(self, quotation_id: UUID, accept: str = "application/pdf") -> bytes:
        return self._download(
            f"/quotations/{quotation_id}/file", "downloading quotation file", accept
        )

    # ── Event Subscriptions ──

    def create_event_subscription(self, subscription: EventSubscriptionWritable) -> CreateResponse:
        data = self._post_json(
            "/event-subscriptions",
            subscription.model_dump(exclude_none=True),
            "creating event subscription",
        )
        return CreateResponse.model_validate(data)

    def retrieve_event_subscription(self, subscription_id: UUID) -> EventSubscription:
        return EventSubscription.model_validate(
            self._get_json(
                f"/event-subscriptions/{subscription_id}", "retrieving event subscription"
            )
        )

    def list_event_subscriptions(self) -> List[EventSubscription]:
        data = self._get_json("/event-subscriptions", "listing event subscriptions")
        content = data.get("content", data) if isinstance(data, dict) else data
        return [EventSubscription.model_validate(s) for s in content]

    def delete_event_subscription(self, subscription_id: UUID) -> None:
        self._delete(f"/event-subscriptions/{subscription_id}", "deleting event subscription")

    # ── Files ──

    def upload_file(self, file_path: Union[str, Path], upload_type: FileType = FileType.VOUCHER) -> File:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("File size exceeds the 5MB limit.")

        with open(file_path, "rb") as f:
            response = self.client.post(
                "/files",
                files={"file": f},
                data={"type": upload_type.value},
            )
        self._check_response(response, "uploading file")
        return File.model_validate(response.json())

    def download_file(self, file_id: UUID) -> bytes:
        return self._download(f"/files/{file_id}", "downloading file", accept="*/*")

    def upload_file_to_voucher(
        self,
        voucher_id: UUID,
        file_path: Union[str, Path],
        upload_type: FileType = FileType.VOUCHER,
    ) -> File:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("File size exceeds the 5MB limit.")

        with open(file_path, "rb") as f:
            response = self.client.post(
                f"/vouchers/{voucher_id}/files",
                files={"file": f},
                data={"type": upload_type.value},
            )
        self._check_response(response, "uploading file to voucher")
        return File.model_validate(response.json())

    # ── Vouchers (bookkeeping) ──

    def create_voucher(self, voucher: VoucherWritable) -> CreateResponse:
        data = self._post_json(
            "/vouchers",
            voucher.model_dump(exclude_none=True, mode="json"),
            "creating voucher",
        )
        return CreateResponse.model_validate(data)

    def retrieve_voucher(self, voucher_id: UUID) -> Voucher:
        return Voucher.model_validate(
            self._get_json(f"/vouchers/{voucher_id}", "retrieving voucher")
        )

    def update_voucher(self, voucher_id: UUID, voucher: VoucherWritable) -> CreateResponse:
        data = self._put_json(
            f"/vouchers/{voucher_id}",
            voucher.model_dump(exclude_none=True, mode="json"),
            "updating voucher",
        )
        return CreateResponse.model_validate(data)

    def filter_vouchers(
        self,
        voucher_number: Optional[str] = None,
        voucher_date_from: Optional[datetime] = None,
        voucher_date_to: Optional[datetime] = None,
        posting_category: Optional[str] = None,
        archived: Optional[bool] = None,
        voucher_status: Optional[str] = None,
        page: int = 0,
    ) -> PaginatedResponse[Voucher]:
        params: Dict[str, Any] = {
            "voucherNumber": voucher_number,
            "voucherDateFrom": voucher_date_from.isoformat() if voucher_date_from else None,
            "voucherDateTo": voucher_date_to.isoformat() if voucher_date_to else None,
            "postingCategory": posting_category,
            "archived": str(archived).lower() if archived is not None else None,
            "voucherStatus": voucher_status,
            "page": page,
        }
        return self._get_paginated("/vouchers", params, Voucher, "filtering vouchers")

    # ── Posting Categories ──

    def retrieve_posting_categories_list(self) -> List[PostingCategoryReadOnly]:
        data = self._get_json("/posting-categories", "retrieving posting categories")
        return [PostingCategoryReadOnly.model_validate(category) for category in data]

    # ── Payment Conditions ──

    def list_payment_conditions(self) -> List[PaymentCondition]:
        data = self._get_json("/payment-conditions", "listing payment conditions")
        return [PaymentCondition.model_validate(pc) for pc in data]

    # ── Print Layouts ──

    def list_print_layouts(self) -> List[PrintLayout]:
        data = self._get_json("/print-layouts", "listing print layouts")
        return [PrintLayout.model_validate(pl) for pl in data]

    # ── Voucherlist ──

    def filter_voucherlist(
        self,
        voucher_type: str,
        voucher_status: str,
        voucher_number: Optional[str] = None,
        voucher_date_from: Optional[datetime] = None,
        voucher_date_to: Optional[datetime] = None,
        contact_id: Optional[UUID] = None,
        archived: Optional[bool] = None,
        page: int = 0,
    ) -> PaginatedResponse[VoucherlistItem]:
        params: Dict[str, Any] = {
            "voucherType": voucher_type,
            "voucherStatus": voucher_status,
            "voucherNumber": voucher_number,
            "voucherDateFrom": voucher_date_from.isoformat() if voucher_date_from else None,
            "voucherDateTo": voucher_date_to.isoformat() if voucher_date_to else None,
            "contactId": str(contact_id) if contact_id else None,
            "archived": str(archived).lower() if archived is not None else None,
            "page": page,
        }
        return self._get_paginated("/voucherlist", params, VoucherlistItem, "filtering voucherlist")

    # ── Payments ──

    def list_payments(self, page: int = 0) -> PaginatedResponse[Payment]:
        params: Dict[str, Any] = {"page": page}
        return self._get_paginated("/payments", params, Payment, "listing payments")

    # ── Recurring Templates ──

    def retrieve_recurring_template(self, template_id: UUID) -> RecurringTemplate:
        return RecurringTemplate.model_validate(
            self._get_json(
                f"/recurring-templates/{template_id}", "retrieving recurring template"
            )
        )

    def list_recurring_templates(self, page: int = 0) -> PaginatedResponse[RecurringTemplate]:
        params: Dict[str, Any] = {"page": page}
        return self._get_paginated(
            "/recurring-templates", params, RecurringTemplate, "listing recurring templates"
        )
