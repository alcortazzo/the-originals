from contextlib import suppress
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, field_validator


# class TaskValidator(BaseModel):
#     uuid: str
#     name: str
#     description: str | None
#     status: str
#     priority: int
#     created_at: datetime
#     last_updated: datetime

#     class Config:
#         orm_mode = True


# class VenueValidator(BaseModel):
#     venue_id: int
#     venue_name: str
#     city: str
#     state: str
#     country: str
#     org_id: int | None = None  # TODO Find where we can get this data point
#     org_name: str | None = None  # TODO Find where we can get this data point
#     url: str

#     # class Config:
#     #     orm_mode = True


# class EventValidator(BaseModel):
#     performance_id: int
#     performance_name: str | None
#     performance_date: datetime | None
#     venue_id: int | None
#     price_min: Decimal | None
#     price_max: Decimal | None
#     availability: Literal["InStock", "SoldOut", "FutureOnSale", "NotOnSale"] | None
#     url: str | None
#     has_manifest: bool | None
#     has_location: bool | None
#     has_section: bool | None
#     has_price_level: bool | None
#     has_best: bool | None
#     inventory_last_updated: datetime | None
#     seatmap_url: str | None
#     alternate_manifest: bool | None
#     has_captcha: bool | None

#     @field_validator("price_min", "price_max", mode="before")
#     def parse_decimal(cls, value) -> Decimal | None:
#         if value is None:
#             return None

#         return Decimal(str(value))

#     @field_validator("performance_date", mode="before")
#     def parse_date(cls, value) -> datetime | None:
#         if value is None:
#             return None

#         with suppress(Exception):
#             return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
#         with suppress(Exception):
#             return datetime.strptime(value, "%B %d, %Y %I:%M %p")
