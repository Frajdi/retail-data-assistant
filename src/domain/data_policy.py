from dataclasses import dataclass
from enum import Enum


class ExposurePolicy(str, Enum):
    ALLOW = "allow"
    MASK = "mask"
    DROP = "drop"


@dataclass(frozen=True)
class FieldPolicy:
    exposure: ExposurePolicy


FIELD_POLICIES: dict[str, FieldPolicy] = {
    "users.first_name": FieldPolicy(ExposurePolicy.MASK),
    "users.last_name": FieldPolicy(ExposurePolicy.MASK),
    "users.email": FieldPolicy(ExposurePolicy.MASK),

    "users.street_address": FieldPolicy(ExposurePolicy.DROP),
    "users.latitude": FieldPolicy(ExposurePolicy.DROP),
    "users.longitude": FieldPolicy(ExposurePolicy.DROP),

    "users.state": FieldPolicy(ExposurePolicy.ALLOW),
    "users.city": FieldPolicy(ExposurePolicy.ALLOW),
    "users.country": FieldPolicy(ExposurePolicy.ALLOW),
}