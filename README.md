# SMPOOS – Smart Maritime Port Operations Optimisation System

**CPS7002 – Software Design and Development | Assessment 1**  
St Mary's University, Twickenham | 2025–2026

---

## Overview

SMPOOS is a web-based management dashboard for HarbourView International Port, built as a Python/Dash application. It provides real-time port operations monitoring, alert management, data analytics, and administrative CRUD capabilities for locations, routes, users, and notifications.

---

## Features

| Module | Capability |
|--------|-----------|
| **Port Overview** | KPI cards, status distribution charts, critical alert feed, berth optimisation recommendations |
| **Locations** | Filterable table (500 locations), add new locations via modal, status colour-coding, capacity metrics |
| **Routes** | Filterable route table (500 routes), distance slider filter, status management, route type analytics |
| **Notifications** | Full alert log, filter by type/severity/location, create new alerts via modal |
| **Personnel** | User directory (500 users), role-based filtering, role distribution pie chart |
| **Analytics** | Location type distribution, capacity by type, notification trends over time, alert breakdown, route analysis, top alert locations, bottleneck identification |
| **Audit Log** | Full immutable log of all CRUD operations with timestamps, entity IDs, and actors |

---

## Technical Architecture

```
smpoos/
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── models/
│   ├── location.py          # Location dataclass + LocationType/Status enums
│   ├── route.py             # Route dataclass + RouteType/Status enums
│   ├── user.py              # User dataclass + UserRole enum + RBAC
│   └── notification.py      # Notification dataclass + AlertType/Severity enums
├── data/
│   └── repository.py        # DataRepository – CRUD + audit logging
├── analytics/
│   └── port_analytics.py    # PortAnalytics – KPIs, charts data, optimisation
└── dashboard/
    ├── layout.py             # Dash UI layout (tabs, modals, KPI cards)
    └── callbacks.py          # Dash reactive callbacks
```

### OOP Design Principles Applied

- **Encapsulation** – All data access goes through `DataRepository`; direct list mutation is prevented by returning copies via `@property`.
- **Data Classes** – `Location`, `Route`, `User`, `Notification` use Python `dataclasses` for clean, type-safe models.
- **Enums** – `LocationType`, `LocationStatus`, `RouteType`, `RouteStatus`, `UserRole`, `AlertType`, `Severity` ensure valid-value enforcement throughout.
- **Single Responsibility** – Models handle data representation; `DataRepository` handles persistence/CRUD; `PortAnalytics` handles computation; `dashboard/` handles UI.
- **RBAC** – `ROLE_PERMISSIONS` dict in `models/user.py` maps each `UserRole` to a set of allowed operations. `ROLE_ALERT_TYPES` defines which alert types each role receives.

---

## Prerequisites

- Python 3.11+
- pip

---

## Installation

```bash
# 1. Clone or unzip the project
cd raskin/

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirement.txt

# 4. Run the application
python app.py                  # Or from dropdown run current file

```

Then open **http://127.0.0.1:8050** in your browser.

---

## Data Sources

Place the following CSV files in the project root (already included):

| File | Records | Description |
|------|---------|-------------|
| `smpoos_locations.csv` | 500 | Port zones (berths, storage yards, fuel docks, etc.) |
| `smpoos_routes.csv` | 500 | Shipping lanes and internal transit paths |
| `smpoos_notifications.csv` | 500+ | Port alerts and notifications |
| `smpoos_users.csv` | 500 | Port personnel with roles |

---

## Role-Based Access Control

| Role | Permissions |
|------|------------|
| Administrator | Full access – manage locations, routes, users, notifications, view analytics & audit log |
| Harbourmaster | Manage locations, routes, notifications; view analytics & audit log |
| Security Officer | View all data; manage notifications; configure alerts |
| Logistics Coordinator | View all data; view analytics |
| Maintenance Engineer | Manage locations; view all data |
| Crane Operator | View all data |
| Stevedore | View all data |

---

## Compliance

- **GDPR** – Audit log records all data access and modifications with timestamps and actor IDs. User data is scoped by role.
- **Maritime Safety** – Notification engine delivers alerts to relevant roles (e.g., stevedores receive hazardous cargo warnings; harbourmasters receive congestion alerts).
- **Audit Trail** – Every CRUD operation is recorded in an immutable audit log accessible from the dashboard.

---

## Module Dependencies

```
dash ─────────────────── Web framework for interactive dashboards
dash-bootstrap-components ── Bootstrap-themed UI components
plotly ───────────────── Interactive charts (bar, pie, line, scatter)
pandas ───────────────── Data manipulation (used in analytics)
matplotlib / seaborn ──── Static chart generation (available for report export)
```

---

## Author

Student assessment submission – CPS7002, St Mary's University Twickenham  
Academic Year 2025–2026
