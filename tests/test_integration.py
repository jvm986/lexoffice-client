"""
Integration tests against the live Lexware API.

Usage:
    LEXOFFICE_API_KEY=your_key python3 tests/test_integration.py
    LEXOFFICE_API_KEY=your_key python3 tests/test_integration.py --write

By default, only read-only endpoints are tested. Pass --write to also test
create/update/delete operations (creates real data in your account).

Cleanup: articles and event subscriptions are deleted after each test.
Contacts and finalized vouchers cannot be deleted via the API.
"""

import os
import sys
import time
import unittest
from uuid import UUID

from lexoffice_client import (
    LexofficeClient,
    Article,
    ArticleWritable,
    ArticleType,
    Contact,
    ContactWritable,
    Country,
    CreateResponse,
    CreditNote,
    CreditNoteWritable,
    DeliveryNote,
    DeliveryNoteWritable,
    Dunning,
    DunningWritable,
    EventSubscription,
    EventSubscriptionWritable,
    EventType,
    Invoice,
    InvoiceWritable,
    LineItem,
    OrderConfirmation,
    OrderConfirmationWritable,
    PaginatedResponse,
    PaymentCondition,
    Person,
    PostingCategoryReadOnly,
    PrintLayout,
    Profile,
    Quotation,
    QuotationWritable,
    Role,
    Roles,
    SalesVoucherAddress,
    SalesTaxType,
    TaxConditions,
    UnitPrice,
)

API_KEY = os.environ.get("LEXOFFICE_API_KEY")
WRITE_MODE = "--write" in sys.argv


def skip_without_key(cls):
    if not API_KEY:
        return unittest.skip("LEXOFFICE_API_KEY not set")(cls)
    return cls


def skip_without_write(cls):
    if not WRITE_MODE:
        return unittest.skip("pass --write to run write tests")(cls)
    return skip_without_key(cls)


def _cleanup(client: LexofficeClient, resource_type: str, resource_id: UUID) -> None:
    """Best-effort cleanup of a created resource."""
    try:
        time.sleep(0.6)
        if resource_type == "article":
            client.delete_article(resource_id)
        elif resource_type == "event_subscription":
            client.delete_event_subscription(resource_id)
        else:
            return
        print(f"  [cleanup] Deleted {resource_type}: {resource_id}")
    except Exception as e:
        print(f"  [cleanup] Failed to delete {resource_type} {resource_id}: {e}")


@skip_without_key
class TestReadOnlyEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_ping(self):
        self.client.ping()

    def test_retrieve_profile(self):
        profile = self.client.retrieve_profile()
        self.assertIsInstance(profile, Profile)
        self.assertIsInstance(profile.organizationId, UUID)
        print(f"  Profile: org={profile.organizationId}, company={profile.companyName}")

    def test_list_countries(self):
        countries = self.client.list_countries()
        self.assertIsInstance(countries, list)
        self.assertTrue(len(countries) > 0)
        self.assertIsInstance(countries[0], Country)
        de = next((c for c in countries if c.countryCode == "DE"), None)
        self.assertIsNotNone(de)
        print(f"  Countries: {len(countries)} total")

    def test_retrieve_posting_categories(self):
        categories = self.client.retrieve_posting_categories_list()
        self.assertIsInstance(categories, list)
        self.assertTrue(len(categories) > 0)
        self.assertIsInstance(categories[0], PostingCategoryReadOnly)
        print(f"  Posting categories: {len(categories)} total")

    def test_list_payment_conditions(self):
        conditions = self.client.list_payment_conditions()
        self.assertIsInstance(conditions, list)
        for pc in conditions:
            self.assertIsInstance(pc, PaymentCondition)
        print(f"  Payment conditions: {len(conditions)} total")

    def test_list_print_layouts(self):
        layouts = self.client.list_print_layouts()
        self.assertIsInstance(layouts, list)
        for pl in layouts:
            self.assertIsInstance(pl, PrintLayout)
        print(f"  Print layouts: {len(layouts)} total")

    def test_filter_contacts(self):
        result = self.client.filter_contacts(page=0)
        self.assertIsInstance(result, PaginatedResponse)
        self.assertIsInstance(result.totalElements, int)
        for contact in result.content:
            self.assertIsInstance(contact, Contact)
        print(f"  Contacts: {result.totalElements} total, page has {result.numberOfElements}")

    def test_filter_articles(self):
        result = self.client.filter_articles(page=0)
        self.assertIsInstance(result, PaginatedResponse)
        for article in result.content:
            self.assertIsInstance(article, Article)
        print(f"  Articles: {result.totalElements} total")

    def test_filter_voucherlist(self):
        result = self.client.filter_voucherlist(
            voucher_type="invoice", voucher_status="open", page=0
        )
        self.assertIsInstance(result, PaginatedResponse)
        print(f"  Voucherlist: {result.totalElements} total")

    def test_list_recurring_templates(self):
        result = self.client.list_recurring_templates(page=0)
        self.assertIsInstance(result, PaginatedResponse)
        print(f"  Recurring templates: {result.totalElements} total")


@skip_without_write
class TestContactCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_contact_lifecycle(self):
        created = self.client.create_contact(
            ContactWritable(
                roles=Roles(customer=Role()),
                person=Person(lastName="IntegrationTest"),
            )
        )
        self.assertIsInstance(created, CreateResponse)
        self.assertIsInstance(created.id, UUID)
        print(f"  Created contact: {created.id}")

        time.sleep(0.6)
        contact = self.client.retrieve_contact(created.id)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.person.lastName, "IntegrationTest")

        time.sleep(0.6)
        updated = self.client.update_contact(
            created.id,
            ContactWritable(
                version=created.version,
                roles=Roles(customer=Role()),
                person=Person(firstName="Updated", lastName="IntegrationTest"),
            ),
        )
        self.assertIsInstance(updated, CreateResponse)
        self.assertEqual(updated.version, created.version + 1)
        print(f"  Updated contact: version {created.version} -> {updated.version}")


@skip_without_write
class TestArticleCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_article_lifecycle(self):
        from lexoffice_client import ArticlePrice, LeadingPrice

        created = self.client.create_article(
            ArticleWritable(
                title="Integration Test Widget",
                type=ArticleType.SERVICE,
                unitName="hour",
                price=ArticlePrice(
                    netPrice=100.00,
                    grossPrice=119.00,
                    leadingPrice=LeadingPrice.NET,
                    currency="EUR",
                    taxRate=19,
                ),
            )
        )
        self.assertIsInstance(created, CreateResponse)
        self.addCleanup(_cleanup, self.client, "article", created.id)
        print(f"  Created article: {created.id}")

        time.sleep(0.6)
        article = self.client.retrieve_article(created.id)
        self.assertEqual(article.title, "Integration Test Widget")
        self.assertEqual(article.type, ArticleType.SERVICE)

        time.sleep(0.6)
        updated = self.client.update_article(
            created.id,
            ArticleWritable(
                title="Updated Integration Test Widget",
                type=ArticleType.SERVICE,
                unitName="hour",
                version=created.version,
                price=ArticlePrice(
                    netPrice=200.00,
                    grossPrice=238.00,
                    leadingPrice=LeadingPrice.NET,
                    currency="EUR",
                    taxRate=19,
                ),
            ),
        )
        self.assertGreater(updated.version, created.version)
        print(f"  Updated article: version {created.version} -> {updated.version}")


@skip_without_write
class TestInvoiceLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_create_draft_invoice(self):
        from lexoffice_client import ShippingConditions, ShippingType, TotalPrice

        invoice = InvoiceWritable(
            voucherDate="2026-04-25T00:00:00.000+02:00",
            address=SalesVoucherAddress(name="Integration Test Customer", countryCode="DE"),
            lineItems=[
                LineItem(
                    type="custom",
                    name="Test Service",
                    quantity=1,
                    unitName="hour",
                    unitPrice=UnitPrice(
                        currency="EUR",
                        netAmount=100.00,
                        taxRatePercentage=19,
                    ),
                )
            ],
            totalPrice=TotalPrice(currency="EUR"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
            shippingConditions=ShippingConditions(
                shippingDate="2026-04-25T00:00:00.000+02:00",
                shippingType=ShippingType.SERVICE,
            ),
        )
        created = self.client.create_invoice(invoice)
        self.assertIsInstance(created, CreateResponse)
        print(f"  Created draft invoice: {created.id}")

        time.sleep(0.6)
        retrieved = self.client.retrieve_invoice(created.id)
        self.assertIsInstance(retrieved, Invoice)
        self.assertEqual(retrieved.voucherStatus.value, "draft")
        print(f"  Retrieved invoice: status={retrieved.voucherStatus}, number={retrieved.voucherNumber}")

    def test_create_finalized_invoice(self):
        from lexoffice_client import ShippingConditions, ShippingType, TotalPrice

        invoice = InvoiceWritable(
            voucherDate="2026-04-25T00:00:00.000+02:00",
            address=SalesVoucherAddress(name="Integration Test Customer", countryCode="DE"),
            lineItems=[
                LineItem(
                    type="custom",
                    name="Test Service",
                    quantity=1,
                    unitName="hour",
                    unitPrice=UnitPrice(
                        currency="EUR",
                        netAmount=50.00,
                        taxRatePercentage=19,
                    ),
                )
            ],
            totalPrice=TotalPrice(currency="EUR"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
            shippingConditions=ShippingConditions(
                shippingDate="2026-04-25T00:00:00.000+02:00",
                shippingType=ShippingType.SERVICE,
            ),
        )
        created = self.client.create_invoice(invoice, finalize=True)
        self.assertIsInstance(created, CreateResponse)
        print(f"  Created finalized invoice: {created.id}")

        time.sleep(0.6)
        retrieved = self.client.retrieve_invoice(created.id)
        self.assertEqual(retrieved.voucherStatus.value, "open")

        time.sleep(0.6)
        pdf = self.client.download_invoice_file(created.id)
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(len(pdf) > 0)
        print(f"  Downloaded invoice PDF: {len(pdf)} bytes")


@skip_without_write
class TestQuotationLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_create_and_retrieve_quotation(self):
        from lexoffice_client import ShippingConditions, ShippingType, TotalPrice

        quotation = QuotationWritable(
            voucherDate="2026-04-25T00:00:00.000+02:00",
            expirationDate="2026-05-25T00:00:00.000+02:00",
            address=SalesVoucherAddress(name="Integration Test Customer", countryCode="DE"),
            lineItems=[
                LineItem(
                    type="custom",
                    name="Consulting",
                    quantity=10,
                    unitName="hour",
                    unitPrice=UnitPrice(
                        currency="EUR",
                        netAmount=150.00,
                        taxRatePercentage=19,
                    ),
                )
            ],
            totalPrice=TotalPrice(currency="EUR"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
            shippingConditions=ShippingConditions(
                shippingDate="2026-04-25T00:00:00.000+02:00",
                shippingType=ShippingType.SERVICE,
            ),
        )
        created = self.client.create_quotation(quotation, finalize=True)
        self.assertIsInstance(created, CreateResponse)
        print(f"  Created quotation: {created.id}")

        time.sleep(0.6)
        retrieved = self.client.retrieve_quotation(created.id)
        self.assertIsInstance(retrieved, Quotation)

        time.sleep(0.6)
        pdf = self.client.download_quotation_file(created.id)
        self.assertTrue(len(pdf) > 0)
        print(f"  Downloaded quotation PDF: {len(pdf)} bytes")


@skip_without_write
class TestDeliveryNoteLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_create_and_retrieve_delivery_note(self):
        from lexoffice_client import ShippingConditions, ShippingType

        dn = DeliveryNoteWritable(
            voucherDate="2026-04-25T00:00:00.000+02:00",
            address=SalesVoucherAddress(name="Integration Test Customer", countryCode="DE"),
            lineItems=[
                LineItem(
                    type="custom",
                    name="Widget",
                    quantity=5,
                    unitName="piece",
                )
            ],
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
            shippingConditions=ShippingConditions(
                shippingDate="2026-04-25T00:00:00.000+02:00",
                shippingType=ShippingType.DELIVERY,
            ),
        )
        created = self.client.create_delivery_note(dn, finalize=True)
        self.assertIsInstance(created, CreateResponse)
        print(f"  Created delivery note: {created.id}")

        time.sleep(0.6)
        retrieved = self.client.retrieve_delivery_note(created.id)
        self.assertIsInstance(retrieved, DeliveryNote)


@skip_without_write
class TestOrderConfirmationLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_create_and_retrieve_order_confirmation(self):
        from lexoffice_client import ShippingConditions, ShippingType, TotalPrice

        oc = OrderConfirmationWritable(
            voucherDate="2026-04-25T00:00:00.000+02:00",
            address=SalesVoucherAddress(name="Integration Test Customer", countryCode="DE"),
            lineItems=[
                LineItem(
                    type="custom",
                    name="Custom Work",
                    quantity=1,
                    unitName="piece",
                    unitPrice=UnitPrice(
                        currency="EUR",
                        netAmount=500.00,
                        taxRatePercentage=19,
                    ),
                )
            ],
            totalPrice=TotalPrice(currency="EUR"),
            taxConditions=TaxConditions(taxType=SalesTaxType.NET),
            shippingConditions=ShippingConditions(
                shippingDate="2026-04-25T00:00:00.000+02:00",
                shippingType=ShippingType.SERVICE,
            ),
        )
        created = self.client.create_order_confirmation(oc, finalize=True)
        self.assertIsInstance(created, CreateResponse)
        print(f"  Created order confirmation: {created.id}")

        time.sleep(0.6)
        retrieved = self.client.retrieve_order_confirmation(created.id)
        self.assertIsInstance(retrieved, OrderConfirmation)


@skip_without_write
class TestEventSubscriptionLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_subscription_lifecycle(self):
        existing = self.client.list_event_subscriptions()
        for sub in existing:
            if sub.eventType == EventType.INVOICE_CREATED:
                time.sleep(0.6)
                self.client.delete_event_subscription(sub.subscriptionId)

        time.sleep(0.6)
        created = self.client.create_event_subscription(
            EventSubscriptionWritable(
                eventType=EventType.INVOICE_CREATED,
                callbackUrl="https://example.com/test-webhook",
            )
        )
        self.assertIsInstance(created, CreateResponse)
        self.addCleanup(_cleanup, self.client, "event_subscription", created.id)
        print(f"  Created event subscription: {created.id}")

        time.sleep(0.6)
        subs = self.client.list_event_subscriptions()
        self.assertIsInstance(subs, list)
        found = any(s.subscriptionId == created.id for s in subs)
        self.assertTrue(found)
        print(f"  Listed subscriptions: {len(subs)} total")


@skip_without_write
class TestCleanupLeftovers(unittest.TestCase):
    """Sweep resources left behind by previous interrupted test runs."""

    @classmethod
    def setUpClass(cls):
        cls.client = LexofficeClient(access_token=API_KEY)

    def setUp(self):
        time.sleep(0.6)

    def test_z_cleanup_articles(self):
        """Delete articles matching 'Integration Test'."""
        result = self.client.filter_articles(page=0)
        deleted = 0
        for article in result.content:
            if article.title and "Integration Test" in article.title:
                time.sleep(0.6)
                try:
                    self.client.delete_article(article.id)
                    deleted += 1
                except Exception:
                    pass
        print(f"  Cleaned up {deleted} leftover test articles")

    def test_z_cleanup_event_subscriptions(self):
        """Delete event subscriptions with test callback URLs."""
        subs = self.client.list_event_subscriptions()
        deleted = 0
        for sub in subs:
            if sub.callbackUrl and "example.com/test-webhook" in sub.callbackUrl:
                time.sleep(0.6)
                try:
                    self.client.delete_event_subscription(sub.subscriptionId)
                    deleted += 1
                except Exception:
                    pass
        print(f"  Cleaned up {deleted} leftover test event subscriptions")


if __name__ == "__main__":
    # Remove --write from argv so unittest doesn't choke on it
    sys.argv = [a for a in sys.argv if a != "--write"]
    unittest.main(verbosity=2)
