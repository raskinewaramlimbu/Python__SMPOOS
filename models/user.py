from enum import Enum
from dataclasses import dataclass
from typing import Dict, Set


class UserRole(Enum):
    ADMINISTRATOR = "Administrator"
    HARBOURMASTER = "Harbourmaster"
    STEVEDORE = "Stevedore"
    CRANE_OPERATOR = "Crane Operator"
    SECURITY_OFFICER = "Security Officer"
    LOGISTICS_COORDINATOR = "Logistics Coordinator"
    MAINTENANCE_ENGINEER = "Maintenance Engineer"


ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.ADMINISTRATOR: {
        'manage_locations', 'manage_routes', 'manage_users',
        'manage_notifications', 'view_analytics', 'view_audit_log',
        'configure_alerts', 'view_all_data',
    },
    UserRole.HARBOURMASTER: {
        'manage_locations', 'manage_routes',
        'manage_notifications', 'view_analytics', 'view_audit_log',
        'configure_alerts', 'view_all_data',
    },
    UserRole.SECURITY_OFFICER: {
        'view_all_data', 'manage_notifications', 'configure_alerts',
    },
    UserRole.LOGISTICS_COORDINATOR: {
        'view_all_data', 'view_analytics',
    },
    UserRole.MAINTENANCE_ENGINEER: {
        'manage_locations', 'view_all_data',
    },
    UserRole.CRANE_OPERATOR: {
        'view_all_data',
    },
    UserRole.STEVEDORE: {
        'view_all_data',
    },
}

ROLE_ALERT_TYPES: Dict[UserRole, Set[str]] = {
    UserRole.ADMINISTRATOR: {
        'Weather Warning', 'Equipment Failure', 'Berth Closure',
        'Security Notice', 'Congestion Alert', 'Hazardous Cargo Warning',
    },
    UserRole.HARBOURMASTER: {
        'Weather Warning', 'Berth Closure', 'Congestion Alert',
        'Hazardous Cargo Warning', 'Security Notice',
    },
    UserRole.SECURITY_OFFICER: {
        'Security Notice', 'Hazardous Cargo Warning', 'Weather Warning',
    },
    UserRole.STEVEDORE: {
        'Equipment Failure', 'Hazardous Cargo Warning', 'Weather Warning',
    },
    UserRole.CRANE_OPERATOR: {
        'Equipment Failure', 'Weather Warning',
    },
    UserRole.LOGISTICS_COORDINATOR: {
        'Congestion Alert', 'Berth Closure', 'Weather Warning',
    },
    UserRole.MAINTENANCE_ENGINEER: {
        'Equipment Failure', 'Berth Closure',
    },
}


@dataclass
class User:
    user_id: str
    name: str
    role: UserRole
    email: str
    active: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        raw_role = data.get('role', '').strip()
        try:
            role = UserRole(raw_role)
        except ValueError:
            role = UserRole.STEVEDORE

        active_val = data.get('active', 'No').strip()
        active = active_val.lower() in ('yes', 'true', '1')

        return cls(
            user_id=data['user_id'].strip(),
            name=data['name'].strip(),
            role=role,
            email=data['email'].strip(),
            active=active,
        )

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role.value,
            'email': self.email,
            'active': 'Yes' if self.active else 'No',
        }

    def has_permission(self, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())

    def receives_alert_type(self, alert_type: str) -> bool:
        return alert_type in ROLE_ALERT_TYPES.get(self.role, set())

    def is_admin_level(self) -> bool:
        return self.role in (UserRole.ADMINISTRATOR, UserRole.HARBOURMASTER)

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User({self.user_id}, {self.name}, {self.role.value}, {status})"
