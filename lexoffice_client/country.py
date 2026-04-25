from pydantic import BaseModel


class Country(BaseModel):
    countryCode: str
    countryNameDE: str
    countryNameEN: str
    taxClassification: str
