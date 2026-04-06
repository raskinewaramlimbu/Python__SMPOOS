from enum import Enum
from dataclasses import dataclass


class RouteType(Enum):
    SHIPPING_LANE = "Shipping Lane"
    TUGBOAT_PATH = "Tugboat Transit Path"
    AGV_ROUTE = "Automated Guided Vehicle Route"
    TRUCK_PATH = "Truck Path"


class RouteStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    RESTRICTED = "Restricted"


@dataclass
class Route:
    route_id: str
    start_location: str
    end_location: str
    route_type: RouteType
    distance_km: float
    status: RouteStatus

    @classmethod
    def from_dict(cls, data: dict) -> 'Route':
        raw_type = data.get('route_type', '').strip()
        raw_status = data.get('status', '').strip()

        try:
            r_type = RouteType(raw_type)
        except ValueError:
            r_type = RouteType.SHIPPING_LANE

        try:
            r_status = RouteStatus(raw_status)
        except ValueError:
            r_status = RouteStatus.CLOSED

        return cls(
            route_id=data['route_id'].strip(),
            start_location=data['start_location'].strip(),
            end_location=data['end_location'].strip(),
            route_type=r_type,
            distance_km=float(data.get('distance_km', 0.0)),
            status=r_status,
        )

    def to_dict(self) -> dict:
        return {
            'route_id': self.route_id,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'route_type': self.route_type.value,
            'distance_km': self.distance_km,
            'status': self.status.value,
        }

    def is_navigable(self) -> bool:
        return self.status == RouteStatus.OPEN

    def is_blocked(self) -> bool:
        return self.status == RouteStatus.CLOSED

    def update_status(self, new_status: RouteStatus) -> None:
        self.status = new_status

    def __str__(self) -> str:
        return (
            f"Route({self.route_id}, {self.start_location} → {self.end_location}, "
            f"{self.route_type.value}, {self.distance_km}km, {self.status.value})"
        )
