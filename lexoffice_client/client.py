from typing import Optional, List, Dict, Union
from uuid import UUID
import httpx
from lexoffice_client.common import CreateResponse
from lexoffice_client.contact import Contact, ContactWritable
from lexoffice_client.voucher import Voucher, VoucherWritable

from urllib.parse import urlencode


class LexofficeClient:
    def __init__(
        self, access_token: str, base_url: str = "https://api.lexoffice.io/v1"
    ):
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            base_url=base_url,
            timeout=10,
        )

    def ping(self):
        """Ping Lexoffice API and test the connection."""
        response = self.client.get("/ping")
        response.raise_for_status()

    def create_contact(self, contact: ContactWritable) -> CreateResponse:
        """Create a new contact.

        :param contact: The contact to create.
        :return: The response from the Lexoffice API.
        """

        response = self.client.post(
            "/contacts", json=contact.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        return CreateResponse.model_validate(response.json())

    def retrieve_contact(self, contact_id: UUID) -> Contact:
        """Retrieve a contact by its ID.

        :param contact_id: The ID of the contact to retrieve.
        :return: The retrieved contact as a Contact object.
        """
        response = self.client.get(f"/contacts/{contact_id}")
        response.raise_for_status()
        return Contact.model_validate(response.json())

    def filter_contacts(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        number: Optional[int] = None,
        customer: Optional[bool] = None,
        vendor: Optional[bool] = None,
    ) -> List[Contact]:
        """Filter contacts by optional email, name, number, customer, and vendor.

        :param email: The email address to filter by (optional).
        :param name: The name to filter by (optional).
        :param number: The number of contacts to retrieve (optional).
        :param customer: Whether to filter by customer (optional).
        :param vendor: Whether to filter by vendor (optional).
        :return: A list of filtered contacts.
        """
        query_params: Dict[str, Union[str, None]] = {
            "email": email,
            "name": name,
            "number": str(number) if number is not None else None,
            "customer": str(customer).lower() if customer is not None else None,
            "vendor": str(vendor).lower() if vendor is not None else None,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        response = self.client.get(f"/contacts?{urlencode(query_params)}")
        response.raise_for_status()
        content = response.json().get("content")
        if content is None:
            raise ValueError("Invalid response format: 'content' key not found.")
        return [Contact.model_validate(contact) for contact in content]

    def create_voucher(self, voucher: VoucherWritable) -> CreateResponse:
        """Create a new voucher.

        :param voucher: The voucher to create.
        :return: The response from the Lexoffice API.
        """
        response = self.client.post(
            "/vouchers", json=voucher.model_dump(exclude_none=True, mode="json")
        )
        response.raise_for_status()
        return CreateResponse.model_validate(response.json())

    def retrieve_voucher(self, voucher_id: UUID) -> Voucher:
        """Retrieve a voucher by its ID.

        :param voucher_id: The ID of the voucher to retrieve.
        :return: The retrieved voucher as an Invoice object.
        """
        response = self.client.get(f"/vouchers/{voucher_id}")
        response.raise_for_status()
        return Voucher.model_validate(response.json())
