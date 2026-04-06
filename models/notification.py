from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


class AlertType(Enum):
    WEATHER_WARNING = "Weather Warning"
    EQUIPMENT_FAILURE = "Equipment Failure"
    BERTH_CLOSURE = "Berth Closure"
    SECURITY_NOTICE = "Security Notice"
    CONGESTION_ALERT = "Congestion Alert"
    HAZARDOUS_CARGO_WARNING = "Hazardous Cargo Warning"


class Severity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    @property
    def weight(self) -> int:
        return {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}[self.value]


@dataclass
class Notification:
    notification_id: str
    alert_type: AlertType
    location_id: str
    severity: Severity
    message: str
    timestamp: datetime
    delivered: bool = False
    delivery_channels: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'Notification':
        raw_type = data.get('alert_type', '').strip()
        raw_severity = data.get('severity', '').strip()
        raw_ts = data.get('timestamp', '')

        try:
            a_type = AlertType(raw_type)
        except ValueError:
            a_type = AlertType.SECURITY_NOTICE

        try:
            severity = Severity(raw_severity)
        except ValueError:
            severity = Severity.LOW

        if isinstance(raw_ts, str):
            try:
                ts = datetime.fromisoformat(raw_ts)
            except ValueError:
                ts = datetime.now()
        elif isinstance(raw_ts, datetime):
            ts = raw_ts
        else:
            ts = datetime.now()

        return cls(
            notification_id=data['notification_id'].strip(),
            alert_type=a_type,
            location_id=data.get('location_id', '').strip(),
            severity=severity,
            message=data.get('message', '').strip(),
            timestamp=ts,
        )

    def to_dict(self) -> dict:
        return {
            'notification_id': self.notification_id,
            'alert_type': self.alert_type.value,
            'location_id': self.location_id,
            'severity': self.severity.value,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def is_critical(self) -> bool:
        return self.severity == Severity.CRITICAL

    def is_high_priority(self) -> bool:
        return self.severity.weight >= 3

    def mark_delivered(self, channel: str = 'in-system') -> None:
        self.delivered = True
        if channel not in self.delivery_channels:
            self.delivery_channels.append(channel)

    def get_severity_colour(self) -> str:
        colours = {
            Severity.LOW: 'success',
            Severity.MEDIUM: 'warning',
            Severity.HIGH: 'danger',
            Severity.CRITICAL: 'dark',
        }
        return colours.get(self.severity, 'secondary')

    def __str__(self) -> str:
        return (
            f"Notification({self.notification_id}, {self.alert_type.value}, "
            f"{self.severity.value}, {self.timestamp.strftime('%Y-%m-%d %H:%M')})"
        )
