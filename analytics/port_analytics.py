from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any

from models.location import Location, LocationStatus, LocationType
from models.route import Route, RouteStatus, RouteType
from models.user import User, UserRole
from models.notification import Notification, AlertType, Severity


class PortAnalytics:
    def __init__(self, locations: List[Location], routes: List[Route],
                 users: List[User], notifications: List[Notification]):
        self.locations = locations
        self.routes = routes
        self.users = users
        self.notifications = notifications

    # ── KPIs ───────────────────────────────────────────────────────────────────

    def get_kpis(self) -> Dict[str, Any]:
        total_locs = len(self.locations)
        active_locs = sum(1 for l in self.locations
                          if l.status == LocationStatus.ACTIVE)
        total_capacity = sum(l.capacity_tonnes for l in self.locations)
        active_capacity = sum(l.capacity_tonnes for l in self.locations
                              if l.status == LocationStatus.ACTIVE)
        open_routes = sum(1 for r in self.routes
                          if r.status == RouteStatus.OPEN)
        critical_alerts = sum(1 for n in self.notifications if n.is_critical())
        high_priority = sum(1 for n in self.notifications if n.is_high_priority())
        active_users = sum(1 for u in self.users if u.active)

        return {
            'total_locations': total_locs,
            'active_locations': active_locs,
            'inactive_locations': sum(1 for l in self.locations
                                      if l.status == LocationStatus.INACTIVE),
            'under_maintenance': sum(1 for l in self.locations
                                     if l.status == LocationStatus.UNDER_MAINTENANCE),
            'location_availability_pct': (
                round(active_locs / total_locs * 100, 1) if total_locs else 0
            ),
            'total_capacity_tonnes': total_capacity,
            'active_capacity_tonnes': active_capacity,
            'total_routes': len(self.routes),
            'open_routes': open_routes,
            'closed_routes': sum(1 for r in self.routes
                                 if r.status == RouteStatus.CLOSED),
            'restricted_routes': sum(1 for r in self.routes
                                     if r.status == RouteStatus.RESTRICTED),
            'total_notifications': len(self.notifications),
            'critical_alerts': critical_alerts,
            'high_priority_alerts': high_priority,
            'total_users': len(self.users),
            'active_users': active_users,
        }

    # ── Location analytics ─────────────────────────────────────────────────────

    def location_type_distribution(self) -> Dict[str, int]:
        return dict(Counter(l.type.value for l in self.locations))

    def location_status_distribution(self) -> Dict[str, int]:
        return dict(Counter(l.status.value for l in self.locations))

    def location_area_distribution(self) -> Dict[str, int]:
        areas: Counter = Counter()
        for loc in self.locations:
            area = loc.get_area()
            if area:
                areas[area] += 1
        return dict(areas)

    def top_capacity_locations(self, n: int = 10) -> List[Location]:
        return sorted(self.locations,
                      key=lambda l: l.capacity_tonnes, reverse=True)[:n]

    def capacity_by_type(self) -> Dict[str, int]:
        totals: defaultdict = defaultdict(int)
        for loc in self.locations:
            totals[loc.type.value] += loc.capacity_tonnes
        return dict(totals)

    def capacity_by_status(self) -> Dict[str, int]:
        totals: defaultdict = defaultdict(int)
        for loc in self.locations:
            totals[loc.status.value] += loc.capacity_tonnes
        return dict(totals)

    # ── Route analytics ────────────────────────────────────────────────────────

    def route_type_distribution(self) -> Dict[str, int]:
        return dict(Counter(r.route_type.value for r in self.routes))

    def route_status_distribution(self) -> Dict[str, int]:
        return dict(Counter(r.status.value for r in self.routes))

    def average_route_distance_by_type(self) -> Dict[str, float]:
        distances: defaultdict = defaultdict(list)
        for r in self.routes:
            distances[r.route_type.value].append(r.distance_km)
        return {k: round(sum(v) / len(v), 2) for k, v in distances.items()}

    def most_connected_locations(self, n: int = 10) -> List[Tuple[str, int]]:
        counts: Counter = Counter()
        for r in self.routes:
            counts[r.start_location] += 1
            counts[r.end_location] += 1
        return counts.most_common(n)

    # ── Notification analytics ─────────────────────────────────────────────────

    def notification_type_distribution(self) -> Dict[str, int]:
        return dict(Counter(n.alert_type.value for n in self.notifications))

    def notification_severity_distribution(self) -> Dict[str, int]:
        return dict(Counter(n.severity.value for n in self.notifications))

    def notifications_by_location(self) -> Dict[str, int]:
        return dict(Counter(n.location_id for n in self.notifications))

    def top_alert_locations(self, n: int = 10) -> List[Tuple[str, int]]:
        counts = Counter(n.location_id for n in self.notifications)
        return counts.most_common(n)

    def notification_trend(self) -> Dict[str, int]:
        daily: Counter = Counter()
        for n in self.notifications:
            day = n.timestamp.strftime('%Y-%m-%d')
            daily[day] += 1
        return dict(sorted(daily.items()))

    def critical_notifications_by_type(self) -> Dict[str, int]:
        return dict(Counter(
            n.alert_type.value for n in self.notifications if n.is_critical()
        ))

    # ── User analytics ─────────────────────────────────────────────────────────

    def user_role_distribution(self) -> Dict[str, int]:
        return dict(Counter(u.role.value for u in self.users))

    def user_activity_distribution(self) -> Dict[str, int]:
        active = sum(1 for u in self.users if u.active)
        return {'Active': active, 'Inactive': len(self.users) - active}

    def users_per_role_activity(self) -> Dict[str, Dict[str, int]]:
        result: defaultdict = defaultdict(lambda: {'Active': 0, 'Inactive': 0})
        for u in self.users:
            key = 'Active' if u.active else 'Inactive'
            result[u.role.value][key] += 1
        return dict(result)

    # ── Berth allocation optimisation ──────────────────────────────────────────

    def suggest_berth_optimisation(self) -> List[Dict[str, Any]]:
        suggestions = []
        berths = [l for l in self.locations
                  if l.type == LocationType.BERTH]
        active_berths = [b for b in berths if b.status == LocationStatus.ACTIVE]

        if not berths:
            return suggestions

        utilisation = len(active_berths) / len(berths) * 100
        if utilisation < 50:
            suggestions.append({
                'type': 'LOW_UTILISATION',
                'message': f"Only {utilisation:.0f}% of berths are active. "
                           f"Consider reactivating {len(berths) - len(active_berths)} berths.",
                'priority': 'Medium',
            })

        maintenance_berths = [b for b in berths
                              if b.status == LocationStatus.UNDER_MAINTENANCE]
        if len(maintenance_berths) > len(berths) * 0.2:
            suggestions.append({
                'type': 'HIGH_MAINTENANCE',
                'message': f"{len(maintenance_berths)} berths under maintenance "
                           f"({len(maintenance_berths)/len(berths)*100:.0f}%). "
                           f"Review maintenance scheduling.",
                'priority': 'High',
            })

        alert_locations = {n.location_id for n in self.notifications
                           if n.is_high_priority()}
        overloaded = [b for b in active_berths
                      if b.location_id in alert_locations]
        if overloaded:
            suggestions.append({
                'type': 'SAFETY_CONCERN',
                'message': f"{len(overloaded)} active berths have high-priority alerts. "
                           f"Review safety procedures.",
                'priority': 'Critical',
            })

        return suggestions

    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        bottlenecks = []

        closed_routes_pct = (
            sum(1 for r in self.routes if r.status == RouteStatus.CLOSED)
            / len(self.routes) * 100
            if self.routes else 0
        )
        if closed_routes_pct > 30:
            bottlenecks.append({
                'area': 'Route Network',
                'issue': f"{closed_routes_pct:.0f}% of routes are closed",
                'impact': 'High – vessel and cargo movement severely limited',
            })

        top_alert_locs = self.top_alert_locations(5)
        for loc_id, count in top_alert_locs:
            if count >= 2:
                loc = next((l for l in self.locations
                            if l.location_id == loc_id), None)
                name = loc.name if loc else loc_id
                bottlenecks.append({
                    'area': f"Location {name}",
                    'issue': f"{count} alerts registered at this location",
                    'impact': 'Medium – operational disruption risk',
                })

        return bottlenecks
