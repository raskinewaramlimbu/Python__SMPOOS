import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

from models.location import Location, LocationStatus, LocationType
from models.route import Route, RouteStatus, RouteType
from models.user import User, UserRole
from models.notification import Notification, AlertType, Severity


class AuditEntry:
    def __init__(self, action: str, entity_type: str, entity_id: str,
                 performed_by: str, details: str = ''):
        self.timestamp = datetime.now()
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.performed_by = performed_by
        self.details = details

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'performed_by': self.performed_by,
            'details': self.details,
        }


class DataRepository:
    def __init__(self, data_dir: str = '.'):
        self.data_dir = data_dir
        self._locations: List[Location] = []
        self._routes: List[Route] = []
        self._users: List[User] = []
        self._notifications: List[Notification] = []
        self._audit_log: List[AuditEntry] = []

    def load_all(self) -> None:
        self._locations = self._load_csv(
            'smpoos_locations.csv', Location.from_dict
        )
        self._routes = self._load_csv(
            'smpoos_routes.csv', Route.from_dict
        )
        self._users = self._load_csv(
            'smpoos_users.csv', User.from_dict
        )
        self._notifications = self._load_csv(
            'smpoos_notifications.csv', Notification.from_dict
        )
        self._audit('SYSTEM', 'SYSTEM', 'ALL', 'system', 'Initial data load completed')

    def _load_csv(self, filename: str, factory) -> list:
        path = os.path.join(self.data_dir, filename)
        records = []
        try:
            with open(path, newline='', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        records.append(factory(row))
                    except Exception:
                        pass
        except FileNotFoundError:
            pass
        return records

    def _audit(self, action: str, entity_type: str, entity_id: str,
               performed_by: str, details: str = '') -> None:
        self._audit_log.append(
            AuditEntry(action, entity_type, entity_id, performed_by, details)
        )

    # ── Locations ──────────────────────────────────────────────────────────────

    @property
    def locations(self) -> List[Location]:
        return list(self._locations)

    def get_location(self, location_id: str) -> Optional[Location]:
        for loc in self._locations:
            if loc.location_id == location_id:
                return loc
        return None

    def add_location(self, location: Location, performed_by: str = 'admin') -> bool:
        if self.get_location(location.location_id):
            return False
        self._locations.append(location)
        self._audit('ADD', 'LOCATION', location.location_id, performed_by,
                    f"Added {location.name}")
        return True

    def update_location(self, location_id: str, updates: Dict[str, Any],
                        performed_by: str = 'admin') -> bool:
        loc = self.get_location(location_id)
        if not loc:
            return False
        for key, value in updates.items():
            if hasattr(loc, key):
                setattr(loc, key, value)
        self._audit('UPDATE', 'LOCATION', location_id, performed_by,
                    f"Updated fields: {list(updates.keys())}")
        return True

    def remove_location(self, location_id: str, performed_by: str = 'admin') -> bool:
        loc = self.get_location(location_id)
        if not loc:
            return False
        self._locations.remove(loc)
        self._audit('REMOVE', 'LOCATION', location_id, performed_by,
                    f"Removed {loc.name}")
        return True

    def get_locations_by_status(self, status: LocationStatus) -> List[Location]:
        return [l for l in self._locations if l.status == status]

    def get_locations_by_type(self, loc_type: LocationType) -> List[Location]:
        return [l for l in self._locations if l.type == loc_type]

    # ── Routes ─────────────────────────────────────────────────────────────────

    @property
    def routes(self) -> List[Route]:
        return list(self._routes)

    def get_route(self, route_id: str) -> Optional[Route]:
        for r in self._routes:
            if r.route_id == route_id:
                return r
        return None

    def add_route(self, route: Route, performed_by: str = 'admin') -> bool:
        if self.get_route(route.route_id):
            return False
        self._routes.append(route)
        self._audit('ADD', 'ROUTE', route.route_id, performed_by)
        return True

    def update_route_status(self, route_id: str, new_status: RouteStatus,
                            performed_by: str = 'admin') -> bool:
        route = self.get_route(route_id)
        if not route:
            return False
        old_status = route.status
        route.update_status(new_status)
        self._audit('UPDATE', 'ROUTE', route_id, performed_by,
                    f"Status: {old_status.value} → {new_status.value}")
        return True

    def remove_route(self, route_id: str, performed_by: str = 'admin') -> bool:
        route = self.get_route(route_id)
        if not route:
            return False
        self._routes.remove(route)
        self._audit('REMOVE', 'ROUTE', route_id, performed_by)
        return True

    def get_open_routes(self) -> List[Route]:
        return [r for r in self._routes if r.is_navigable()]

    # ── Users ──────────────────────────────────────────────────────────────────

    @property
    def users(self) -> List[User]:
        return list(self._users)

    def get_user(self, user_id: str) -> Optional[User]:
        for u in self._users:
            if u.user_id == user_id:
                return u
        return None

    def add_user(self, user: User, performed_by: str = 'admin') -> bool:
        if self.get_user(user.user_id):
            return False
        self._users.append(user)
        self._audit('ADD', 'USER', user.user_id, performed_by,
                    f"Added {user.name} as {user.role.value}")
        return True

    def update_user_status(self, user_id: str, active: bool,
                           performed_by: str = 'admin') -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        user.active = active
        action = 'ACTIVATE' if active else 'DEACTIVATE'
        self._audit(action, 'USER', user_id, performed_by)
        return True

    def get_users_by_role(self, role: UserRole) -> List[User]:
        return [u for u in self._users if u.role == role]

    def get_active_users(self) -> List[User]:
        return [u for u in self._users if u.active]

    # ── Notifications ──────────────────────────────────────────────────────────

    @property
    def notifications(self) -> List[Notification]:
        return list(self._notifications)

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        for n in self._notifications:
            if n.notification_id == notification_id:
                return n
        return None

    def add_notification(self, notification: Notification,
                         performed_by: str = 'system') -> bool:
        self._notifications.append(notification)
        self._audit('ADD', 'NOTIFICATION', notification.notification_id, performed_by,
                    f"{notification.alert_type.value} – {notification.severity.value}")
        return True

    def get_notifications_by_severity(self, severity: Severity) -> List[Notification]:
        return [n for n in self._notifications if n.severity == severity]

    def get_notifications_by_location(self, location_id: str) -> List[Notification]:
        return [n for n in self._notifications if n.location_id == location_id]

    def get_critical_notifications(self) -> List[Notification]:
        return [n for n in self._notifications if n.is_critical()]

    def get_high_priority_notifications(self) -> List[Notification]:
        return [n for n in self._notifications if n.is_high_priority()]

    def get_notifications_for_role(self, role: UserRole) -> List[Notification]:
        from models.user import ROLE_ALERT_TYPES
        allowed = ROLE_ALERT_TYPES.get(role, set())
        return [n for n in self._notifications
                if n.alert_type.value in allowed]

    # ── Audit Log ──────────────────────────────────────────────────────────────

    @property
    def audit_log(self) -> List[AuditEntry]:
        return list(self._audit_log)

    def get_audit_log_dicts(self) -> List[dict]:
        return [e.to_dict() for e in reversed(self._audit_log)]

    # ── Summary ────────────────────────────────────────────────────────────────

    def summary(self) -> dict:
        return {
            'total_locations': len(self._locations),
            'total_routes': len(self._routes),
            'total_users': len(self._users),
            'total_notifications': len(self._notifications),
            'audit_entries': len(self._audit_log),
        }
