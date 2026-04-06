from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class LocationType(Enum):
    BERTH = "Berth"
    STORAGE_YARD = "Storage Yard"
    FUEL_DOCK = "Fuel Dock"
    CUSTOMS_ZONE = "Customs Zone"
    MAINTENANCE_AREA = "Maintenance Area"


class LocationStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    UNDER_MAINTENANCE = "Under Maintenance"


@dataclass
class Location:
    location_id: str
    name: str
    type: LocationType
    status: LocationStatus
    capacity_tonnes: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        raw_type = data.get('type', '').strip()
        raw_status = data.get('status', '').strip()

        try:
            loc_type = LocationType(raw_type)
        except ValueError:
            loc_type = LocationType.BERTH

        try:
            loc_status = LocationStatus(raw_status)
        except ValueError:
            loc_status = LocationStatus.INACTIVE

        return cls(
            location_id=data['location_id'].strip(),
            name=data['name'].strip(),
            type=loc_type,
            status=loc_status,
            capacity_tonnes=int(data.get('capacity_tonnes', 0)),
        )

    def to_dict(self) -> dict:
        return {
            'location_id': self.location_id,
            'name': self.name,
            'type': self.type.value,
            'status': self.status.value,
            'capacity_tonnes': self.capacity_tonnes,
        }

    def is_operational(self) -> bool:
        return self.status == LocationStatus.ACTIVE

    def update_status(self, new_status: LocationStatus) -> None:
        self.status = new_status

    def get_area(self) -> Optional[str]:
        parts = self.name.split('Area ')
        if len(parts) == 2:
            return f"Area {parts[1].strip()}"
        return None

    def get_berth_number(self) -> Optional[int]:
        parts = self.name.split()
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except ValueError:
                return None
        return None

    def __str__(self) -> str:
        return f"Location({self.location_id}, {self.name}, {self.type.value}, {self.status.value})"
