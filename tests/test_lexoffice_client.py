from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4

import httpx

from lexoffice_client.client import LexofficeClient
from lexoffice_client.common import CreateResponse
from lexoffice_client.contact import Contact, ContactWritable, Person, Role, Roles
from lexoffice_client.voucher import (
    TaxType,
    Voucher,
    VoucherItem,
    VoucherStatus,
    VoucherType,
    VoucherWritable,
)
from lexoffice_client.article import Article, ArticleType, ArticleWritable
from lexoffice_client.country import Country
from lexoffice_client.credit_note import CreditNote, CreditNoteWritable
from lexoffice_client.delivery_note import DeliveryNote, DeliveryNoteWritable
from lexoffice_client.down_payment_invoice import DownPaymentInvoice
from lexoffice_client.dunning import Dunning, DunningWritable
from lexoffice_client.event_subscription import (
    EventSubscription,
    EventSubscriptionWritable,
    EventType,
)
from lexoffice_client.invoice import Invoice, InvoiceWritable
from lexoffice_client.order_confirmation import OrderConfirmation, OrderConfirmationWritable
from lexoffice_client.payment import Payment
from lexoffice_client.payment_condition import PaymentCondition
from lexoffice_client.posting_category import PostingCategoryReadOnly
from lexoffice_client.print_layout import PrintLayout
from lexoffice_client.profile import Profile
from lexoffice_client.quotation import Quotation, QuotationWritable
from lexoffice_client.recurring_template import RecurringTemplate
from lexoffice_client.sales_voucher_common import (
    LineItem,
    SalesVoucherAddress,
    SalesVoucherStatus,
    TaxConditions,
    SalesTaxType,
)
from lexoffice_client.voucherlist import VoucherlistItem

ORGANIZATION_ID = uuid4()
CONTACT_ID = uuid4()
VOUCHER_ID = uuid4()
CATEGORY_ID = uuid4()
ARTICLE_ID = uuid4()
INVOICE_ID = uuid4()
SUBSCRIPTION_ID = uuid4()
FILE_ID = uuid4()

NOW = datetime.now()


def make_paginated_response(content: list, page: int = 0, total_pages: int = 1) -> dict:
    return {
        "content": content,
        "first": page == 0,
        "last": page == total_pages - 1,
        "number": page,
        "size": 25,
        "numberOfElements": len(content),
        "totalElements": len(content),
        "totalPages": total_pages,
        "sort": [],
    }


def make_create_response(resource_id, uri_prefix):
    return {
        "id": str(resource_id),
        "resourceUri": f"/{uri_prefix}/{resource_id}",
        "createdDate": NOW.isoformat(),
        "updatedDate": NOW.isoformat(),
        "version": 1,
    }


class TestPing(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_ping(self, mock_get: MagicMock):
        mock_get.return_value = MagicMock(status_code=200, is_success=True)
        self.client.ping()
        mock_get.assert_called_once_with("/ping")


class TestProfile(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_retrieve_profile(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "organizationId": str(ORGANIZATION_ID),
            "organizationName": "Test Org",
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_profile()
        mock_get.assert_called_once_with("/profile")
        self.assertIsInstance(result, Profile)
        self.assertEqual(result.organizationId, ORGANIZATION_ID)


class TestContacts(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_contact(self, mock_post: MagicMock):
        contact = ContactWritable(
            roles=Roles(customer=Role()), person=Person(lastName="Test")
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(CONTACT_ID, "contacts")
        mock_post.return_value = mock_response
        result = self.client.create_contact(contact)
        mock_post.assert_called_once()
        self.assertEqual(result.id, CONTACT_ID)

    @patch("httpx.Client.get")
    def test_retrieve_contact(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        contact = Contact(
            id=CONTACT_ID,
            organizationId=ORGANIZATION_ID,
            roles=Roles(customer=Role()),
            person=Person(lastName="Test"),
            archived=False,
        )
        mock_response.json.return_value = contact.model_dump(mode="json")
        mock_get.return_value = mock_response
        result = self.client.retrieve_contact(CONTACT_ID)
        mock_get.assert_called_once_with(f"/contacts/{CONTACT_ID}")
        self.assertEqual(result.id, CONTACT_ID)

    @patch("httpx.Client.put")
    def test_update_contact(self, mock_put: MagicMock):
        contact = ContactWritable(
            version=1,
            roles=Roles(customer=Role()),
            person=Person(lastName="Updated"),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(CONTACT_ID, "contacts")
        mock_put.return_value = mock_response
        result = self.client.update_contact(CONTACT_ID, contact)
        mock_put.assert_called_once()
        self.assertEqual(result.id, CONTACT_ID)

    @patch("httpx.Client.get")
    def test_filter_contacts(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([])
        mock_get.return_value = mock_response
        result = self.client.filter_contacts(email="test@example.com")
        mock_get.assert_called_once()
        self.assertEqual(len(result.content), 0)
        self.assertTrue(result.first)


class TestArticles(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_article(self, mock_post: MagicMock):
        article = ArticleWritable(title="Widget", type=ArticleType.PRODUCT, unitName="piece")
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(ARTICLE_ID, "articles")
        mock_post.return_value = mock_response
        result = self.client.create_article(article)
        mock_post.assert_called_once()
        self.assertEqual(result.id, ARTICLE_ID)

    @patch("httpx.Client.get")
    def test_retrieve_article(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(ARTICLE_ID),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
            "title": "Widget",
            "type": "PRODUCT",
            "unitName": "piece",
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_article(ARTICLE_ID)
        mock_get.assert_called_once_with(f"/articles/{ARTICLE_ID}")
        self.assertEqual(result.title, "Widget")

    @patch("httpx.Client.put")
    def test_update_article(self, mock_put: MagicMock):
        article = ArticleWritable(title="Updated Widget", type=ArticleType.PRODUCT, unitName="piece", version=1)
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(ARTICLE_ID, "articles")
        mock_put.return_value = mock_response
        result = self.client.update_article(ARTICLE_ID, article)
        mock_put.assert_called_once()
        self.assertEqual(result.id, ARTICLE_ID)

    @patch("httpx.Client.delete")
    def test_delete_article(self, mock_delete: MagicMock):
        mock_delete.return_value = MagicMock(is_success=True, status_code=204)
        self.client.delete_article(ARTICLE_ID)
        mock_delete.assert_called_once_with(f"/articles/{ARTICLE_ID}")

    @patch("httpx.Client.get")
    def test_filter_articles(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([])
        mock_get.return_value = mock_response
        result = self.client.filter_articles(type="PRODUCT")
        mock_get.assert_called_once()
        self.assertEqual(len(result.content), 0)


class TestCountries(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_list_countries(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = [
            {"countryCode": "DE", "countryNameDE": "Deutschland", "countryNameEN": "Germany", "taxClassification": "de"},
        ]
        mock_get.return_value = mock_response
        result = self.client.list_countries()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].countryCode, "DE")


class TestInvoices(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_invoice(self, mock_post: MagicMock):
        invoice = InvoiceWritable(
            address=SalesVoucherAddress(name="Test Customer"),
            lineItems=[LineItem(type="custom", name="Service", quantity=1)],
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(INVOICE_ID, "invoices")
        mock_post.return_value = mock_response
        result = self.client.create_invoice(invoice)
        mock_post.assert_called_once()
        self.assertEqual(result.id, INVOICE_ID)

    @patch("httpx.Client.post")
    def test_create_invoice_finalized(self, mock_post: MagicMock):
        invoice = InvoiceWritable(
            address=SalesVoucherAddress(name="Test Customer"),
            lineItems=[LineItem(type="custom", name="Service", quantity=1)],
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(INVOICE_ID, "invoices")
        mock_post.return_value = mock_response
        result = self.client.create_invoice(invoice, finalize=True)
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs.get("params"), {"finalize": "true"})

    @patch("httpx.Client.get")
    def test_retrieve_invoice(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(INVOICE_ID),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
            "voucherStatus": "draft",
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_invoice(INVOICE_ID)
        self.assertIsInstance(result, Invoice)
        self.assertEqual(result.id, INVOICE_ID)

    @patch("httpx.Client.get")
    def test_download_invoice_file(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True, content=b"%PDF-1.4 test")
        mock_get.return_value = mock_response
        result = self.client.download_invoice_file(INVOICE_ID)
        self.assertEqual(result, b"%PDF-1.4 test")
        call_kwargs = mock_get.call_args
        self.assertEqual(call_kwargs.kwargs.get("headers"), {"Accept": "application/pdf"})


class TestCreditNotes(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_credit_note(self, mock_post: MagicMock):
        credit_note = CreditNoteWritable(
            address=SalesVoucherAddress(name="Test"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(uuid4(), "credit-notes")
        mock_post.return_value = mock_response
        result = self.client.create_credit_note(credit_note)
        self.assertIsInstance(result, CreateResponse)

    @patch("httpx.Client.get")
    def test_retrieve_credit_note(self, mock_get: MagicMock):
        cn_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(cn_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_credit_note(cn_id)
        self.assertIsInstance(result, CreditNote)


class TestDeliveryNotes(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_delivery_note(self, mock_post: MagicMock):
        delivery_note = DeliveryNoteWritable(
            address=SalesVoucherAddress(name="Test"),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(uuid4(), "delivery-notes")
        mock_post.return_value = mock_response
        result = self.client.create_delivery_note(delivery_note)
        self.assertIsInstance(result, CreateResponse)

    @patch("httpx.Client.get")
    def test_retrieve_delivery_note(self, mock_get: MagicMock):
        dn_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(dn_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_delivery_note(dn_id)
        self.assertIsInstance(result, DeliveryNote)


class TestDownPaymentInvoices(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_retrieve_down_payment_invoice(self, mock_get: MagicMock):
        dpi_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(dpi_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_down_payment_invoice(dpi_id)
        self.assertIsInstance(result, DownPaymentInvoice)

    @patch("httpx.Client.get")
    def test_download_down_payment_invoice_file(self, mock_get: MagicMock):
        dpi_id = uuid4()
        mock_response = MagicMock(is_success=True, content=b"%PDF")
        mock_get.return_value = mock_response
        result = self.client.download_down_payment_invoice_file(dpi_id)
        self.assertEqual(result, b"%PDF")


class TestDunnings(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_dunning(self, mock_post: MagicMock):
        dunning = DunningWritable(
            address=SalesVoucherAddress(name="Test"),
            taxConditions=TaxConditions(taxType=SalesTaxType.GROSS),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(uuid4(), "dunnings")
        mock_post.return_value = mock_response
        result = self.client.create_dunning(dunning)
        self.assertIsInstance(result, CreateResponse)

    @patch("httpx.Client.get")
    def test_retrieve_dunning(self, mock_get: MagicMock):
        d_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(d_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_dunning(d_id)
        self.assertIsInstance(result, Dunning)


class TestOrderConfirmations(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_order_confirmation(self, mock_post: MagicMock):
        oc = OrderConfirmationWritable(
            address=SalesVoucherAddress(name="Test"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(uuid4(), "order-confirmations")
        mock_post.return_value = mock_response
        result = self.client.create_order_confirmation(oc)
        self.assertIsInstance(result, CreateResponse)

    @patch("httpx.Client.get")
    def test_retrieve_order_confirmation(self, mock_get: MagicMock):
        oc_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(oc_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_order_confirmation(oc_id)
        self.assertIsInstance(result, OrderConfirmation)


class TestQuotations(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_quotation(self, mock_post: MagicMock):
        quotation = QuotationWritable(
            address=SalesVoucherAddress(name="Test"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(uuid4(), "quotations")
        mock_post.return_value = mock_response
        result = self.client.create_quotation(quotation)
        self.assertIsInstance(result, CreateResponse)

    @patch("httpx.Client.get")
    def test_retrieve_quotation(self, mock_get: MagicMock):
        q_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(q_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_quotation(q_id)
        self.assertIsInstance(result, Quotation)


class TestEventSubscriptions(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_event_subscription(self, mock_post: MagicMock):
        sub = EventSubscriptionWritable(
            eventType=EventType.INVOICE_CREATED,
            callbackUrl="https://example.com/webhook",
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(SUBSCRIPTION_ID, "event-subscriptions")
        mock_post.return_value = mock_response
        result = self.client.create_event_subscription(sub)
        self.assertEqual(result.id, SUBSCRIPTION_ID)

    @patch("httpx.Client.get")
    def test_retrieve_event_subscription(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "subscriptionId": str(SUBSCRIPTION_ID),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "eventType": "invoice.created",
            "callbackUrl": "https://example.com/webhook",
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_event_subscription(SUBSCRIPTION_ID)
        self.assertIsInstance(result, EventSubscription)
        self.assertEqual(result.eventType, EventType.INVOICE_CREATED)

    @patch("httpx.Client.get")
    def test_list_event_subscriptions(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = [
            {
                "subscriptionId": str(SUBSCRIPTION_ID),
                "organizationId": str(ORGANIZATION_ID),
                "createdDate": NOW.isoformat(),
                "eventType": "invoice.created",
                "callbackUrl": "https://example.com/webhook",
            }
        ]
        mock_get.return_value = mock_response
        result = self.client.list_event_subscriptions()
        self.assertEqual(len(result), 1)

    @patch("httpx.Client.delete")
    def test_delete_event_subscription(self, mock_delete: MagicMock):
        mock_delete.return_value = MagicMock(is_success=True, status_code=204)
        self.client.delete_event_subscription(SUBSCRIPTION_ID)
        mock_delete.assert_called_once_with(f"/event-subscriptions/{SUBSCRIPTION_ID}")


class TestVouchers(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.post")
    def test_create_voucher(self, mock_post: MagicMock):
        voucher = VoucherWritable(
            type=VoucherType.SALES_INVOICE,
            voucherStatus=VoucherStatus.UNCHECKED,
            totalGrossAmount=119.0,
            totalTaxAmount=19.0,
            taxType=TaxType.GROSS,
            useCollectiveContact=True,
            voucherItems=[
                VoucherItem(
                    amount=100.0,
                    taxAmount=19.0,
                    taxRatePercent=19.0,
                    categoryId=CATEGORY_ID,
                )
            ],
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(VOUCHER_ID, "vouchers")
        mock_post.return_value = mock_response
        result = self.client.create_voucher(voucher)
        mock_post.assert_called_once()
        self.assertEqual(result.id, VOUCHER_ID)

    @patch("httpx.Client.get")
    def test_retrieve_voucher(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        voucher = Voucher(
            id=VOUCHER_ID,
            organizationId=VOUCHER_ID,
            createdDate=NOW,
            updatedDate=NOW,
            type=VoucherType.SALES_INVOICE,
            voucherStatus=VoucherStatus.UNCHECKED,
            totalGrossAmount=119.0,
            totalTaxAmount=19.0,
            taxType=TaxType.GROSS,
            useCollectiveContact=True,
            voucherItems=[
                VoucherItem(
                    amount=100.0,
                    taxAmount=19.0,
                    taxRatePercent=19.0,
                    categoryId=CATEGORY_ID,
                )
            ],
        )
        mock_response.json.return_value = voucher.model_dump(mode="json")
        mock_get.return_value = mock_response
        result = self.client.retrieve_voucher(VOUCHER_ID)
        mock_get.assert_called_once_with(f"/vouchers/{VOUCHER_ID}")
        self.assertEqual(result.id, VOUCHER_ID)

    @patch("httpx.Client.put")
    def test_update_voucher(self, mock_put: MagicMock):
        voucher = VoucherWritable(
            type=VoucherType.SALES_INVOICE,
            voucherStatus=VoucherStatus.UNCHECKED,
            totalGrossAmount=119.0,
            totalTaxAmount=19.0,
            taxType=TaxType.GROSS,
            useCollectiveContact=True,
            voucherItems=[
                VoucherItem(
                    amount=100.0,
                    taxAmount=19.0,
                    taxRatePercent=19.0,
                    categoryId=CATEGORY_ID,
                )
            ],
            version=1,
        )
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_create_response(VOUCHER_ID, "vouchers")
        mock_put.return_value = mock_response
        result = self.client.update_voucher(VOUCHER_ID, voucher)
        mock_put.assert_called_once()
        self.assertEqual(result.id, VOUCHER_ID)

    @patch("httpx.Client.get")
    def test_filter_vouchers(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([])
        mock_get.return_value = mock_response
        result = self.client.filter_vouchers(voucher_status="open")
        mock_get.assert_called_once()
        self.assertEqual(len(result.content), 0)


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_download_file(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True, content=b"file-content")
        mock_get.return_value = mock_response
        result = self.client.download_file(FILE_ID)
        self.assertEqual(result, b"file-content")


class TestPostingCategories(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_retrieve_posting_categories(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = [
            {
                "id": str(CATEGORY_ID),
                "name": "Revenue",
                "type": "income",
                "contactRequired": False,
                "splitAllowed": True,
                "groupName": "Income",
            }
        ]
        mock_get.return_value = mock_response
        result = self.client.retrieve_posting_categories_list()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], PostingCategoryReadOnly)


class TestPaymentConditions(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_list_payment_conditions(self, mock_get: MagicMock):
        pc_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = [
            {"id": str(pc_id), "paymentTermLabel": "Net 30", "paymentTermDuration": 30}
        ]
        mock_get.return_value = mock_response
        result = self.client.list_payment_conditions()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], PaymentCondition)


class TestPrintLayouts(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_list_print_layouts(self, mock_get: MagicMock):
        pl_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = [
            {"id": str(pl_id), "name": "Default", "default": True}
        ]
        mock_get.return_value = mock_response
        result = self.client.list_print_layouts()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].default)


class TestVoucherlist(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_filter_voucherlist(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([
            {
                "id": str(INVOICE_ID),
                "voucherType": "invoice",
                "voucherStatus": "open",
                "voucherNumber": "INV-001",
            }
        ])
        mock_get.return_value = mock_response
        result = self.client.filter_voucherlist(voucher_type="invoice", voucher_status="open")
        self.assertEqual(len(result.content), 1)
        self.assertIsInstance(result.content[0], VoucherlistItem)


class TestPayments(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_list_payments(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([])
        mock_get.return_value = mock_response
        result = self.client.list_payments()
        self.assertEqual(len(result.content), 0)


class TestRecurringTemplates(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_retrieve_recurring_template(self, mock_get: MagicMock):
        t_id = uuid4()
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = {
            "id": str(t_id),
            "organizationId": str(ORGANIZATION_ID),
            "createdDate": NOW.isoformat(),
            "updatedDate": NOW.isoformat(),
            "version": 1,
        }
        mock_get.return_value = mock_response
        result = self.client.retrieve_recurring_template(t_id)
        self.assertIsInstance(result, RecurringTemplate)

    @patch("httpx.Client.get")
    def test_list_recurring_templates(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=True)
        mock_response.json.return_value = make_paginated_response([])
        mock_get.return_value = mock_response
        result = self.client.list_recurring_templates()
        self.assertEqual(len(result.content), 0)


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = LexofficeClient(access_token="test_token")

    @patch("httpx.Client.get")
    def test_error_raises_http_status_error(self, mock_get: MagicMock):
        mock_response = MagicMock(is_success=False, status_code=404, text="Not Found")
        mock_response.request = MagicMock()
        mock_get.return_value = mock_response
        with self.assertRaises(httpx.HTTPStatusError):
            self.client.retrieve_contact(uuid4())

    @patch("httpx.Client.post")
    def test_post_error_raises_http_status_error(self, mock_post: MagicMock):
        mock_response = MagicMock(is_success=False, status_code=400, text="Bad Request")
        mock_response.request = MagicMock()
        mock_post.return_value = mock_response
        contact = ContactWritable(
            roles=Roles(customer=Role()), person=Person(lastName="Test")
        )
        with self.assertRaises(httpx.HTTPStatusError):
            self.client.create_contact(contact)


if __name__ == "__main__":
    unittest.main()
