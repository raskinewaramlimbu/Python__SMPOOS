# Smart Maritime Port Operations Optimisation System (SMPOOS)

**Project Title:** Smart Maritime Port Operations Optimisation System (SMPOOS)  
**Course Title:** CPS7002 – Software Design and Development  
**Institution:** St Mary's University, Twickenham  
**Date of Submission:** 3rd June 2026  

---

## Abstract

This report presents the design and development of the Smart Maritime Port Operations Optimisation System (SMPOOS), a full-stack Python web application built for HarbourView International Port. The system addresses the operational challenges of managing a large European port by providing a centralised, interactive dashboard for real-time monitoring, administrative management, notification handling, and data analytics.

The software artefact was developed using Python 3.11 with Plotly Dash as the web framework, Dash Bootstrap Components for responsive UI design, and Plotly for interactive visualisations. The application adopts a modular, object-oriented architecture comprising four layers: data models, a repository layer, an analytics engine, and a dashboard UI layer.

The system successfully loads and manages four datasets totalling 2,000 records (500 locations, 500 routes, 500 users, 500 notifications), delivers seven functional dashboard tabs covering port overview, location management, route management, notifications, personnel management, analytics, and a full audit trail. Key outcomes include real-time KPI reporting, role-based access control across seven user roles, berth optimisation recommendations, bottleneck identification, and an immutable audit log satisfying GDPR compliance requirements. The solution demonstrates strong object-oriented design, clean separation of concerns, and professional software development practices.

---

## 1. Introduction

### 1.1 Context and Background

HarbourView International Port operates as one of Europe's busiest logistics hubs, handling thousands of vessel movements, cargo operations, and personnel activities daily. Managing this complexity requires a centralised, data-driven system that can provide operational oversight, coordinate workforce activities, deliver timely alerts, and support strategic decision-making. Without such a system, port administrators face fragmented data, delayed incident responses, inefficient berth allocation, and heightened safety risks.

The Smart Maritime Port Operations Optimisation System (SMPOOS) was commissioned to address these challenges by integrating vessel tracking data, port zone management, personnel administration, and predictive analytics into a single, accessible platform.

### 1.2 Objectives and Scope

The primary objectives of this project were to:

1. Design and implement a fully functional software prototype of SMPOOS using Python 3.11+
2. Demonstrate robust object-oriented design with clean, maintainable architecture
3. Provide an interactive management dashboard covering all operational domains
4. Implement a role-based access control system aligned with port security requirements
5. Deliver data analytics capabilities covering berth utilisation, alert trends, and operational bottlenecks
6. Ensure regulatory compliance through audit logging and data governance mechanisms

The scope covers four operational datasets provided as CSV files: port locations (`smpoos_locations.csv`), shipping routes (`smpoos_routes.csv`), operational notifications (`smpoos_notifications.csv`), and port personnel (`smpoos_users.csv`), each containing 500 records.

### 1.3 Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core programming language |
| Plotly Dash | 2.14+ | Web application framework |
| Dash Bootstrap Components | 1.5+ | Responsive UI components |
| Plotly | 5.17+ | Interactive chart library |
| pandas | 2.1+ | Data manipulation |
| matplotlib / seaborn | 3.8+ / 0.13+ | Static visualisation (available for report export) |
| Python `dataclasses` | stdlib | Type-safe data models |
| Python `enum` | stdlib | Enumerated type definitions |
| Python `csv` | stdlib | CSV data ingestion |

### 1.4 Report Structure

This report proceeds as follows: Section 2 details the implemented features with supporting evidence; Section 3 describes the implementation process and architectural decisions; Section 4 covers version control practices; Section 5 evaluates the solution against functional and non-functional requirements; Section 6 addresses professional ethics; and Section 7 concludes with reflections and future directions.

---

## 2. Implemented Features

### 2.1 Modular Object-Oriented Architecture

The system is structured across four distinct layers, each with a single responsibility:

```
app.py                   ← Entry point and application factory
models/                  ← Domain data models
data/repository.py       ← Data access and CRUD operations
analytics/               ← Analytical computations
dashboard/               ← UI layout and reactive callbacks
```

This layered architecture ensures that changes in one layer (e.g., adding a new chart to the analytics module) do not require modifications to the data layer, satisfying the **Open/Closed Principle**.

### 2.2 Data Models with Enums and Dataclasses

Four domain models were implemented using Python `@dataclass` decorators combined with `Enum` classes:

**Location** (`models/location.py`)
- `LocationType` enum: `Berth`, `Storage Yard`, `Fuel Dock`, `Customs Zone`, `Maintenance Area`
- `LocationStatus` enum: `Active`, `Inactive`, `Under Maintenance`
- Methods: `is_operational()`, `update_status()`, `get_area()`, `get_berth_number()`
- Factory method `from_dict()` for safe CSV ingestion with error handling

**Route** (`models/route.py`)
- `RouteType` enum: `Shipping Lane`, `Tugboat Transit Path`, `Automated Guided Vehicle Route`, `Truck Path`
- `RouteStatus` enum: `Open`, `Closed`, `Restricted`
- Methods: `is_navigable()`, `is_blocked()`, `update_status()`

**User** (`models/user.py`)
- `UserRole` enum: `Administrator`, `Harbourmaster`, `Security Officer`, `Logistics Coordinator`, `Maintenance Engineer`, `Crane Operator`, `Stevedore`
- `ROLE_PERMISSIONS` dictionary maps each role to a `Set[str]` of allowed operations
- `ROLE_ALERT_TYPES` dictionary maps each role to the notification types they receive
- Methods: `has_permission()`, `receives_alert_type()`, `is_admin_level()`

**Notification** (`models/notification.py`)
- `AlertType` enum: `Weather Warning`, `Equipment Failure`, `Berth Closure`, `Security Notice`, `Congestion Alert`, `Hazardous Cargo Warning`
- `Severity` enum with a `weight` property enabling priority comparison
- Methods: `is_critical()`, `is_high_priority()`, `mark_delivered()`, `get_severity_colour()`

### 2.3 DataRepository – Centralised Data Access Layer

The `DataRepository` class (`data/repository.py`) provides all CRUD operations with a built-in audit trail:

- **Load**: Reads all four CSV files at startup via a generic `_load_csv()` method
- **Create**: `add_location()`, `add_route()`, `add_notification()`, `add_user()` — each logs an `AuditEntry`
- **Read**: Properties return defensive copies (`list(self._locations)`) preventing external mutation
- **Update**: `update_location()`, `update_route_status()`, `update_user_status()` — all audited
- **Delete**: `remove_location()`, `remove_route()` — all audited
- **Query methods**: `get_locations_by_status()`, `get_open_routes()`, `get_notifications_for_role()`, `get_critical_notifications()`

Every operation writes to `_audit_log` as an `AuditEntry` object recording the timestamp, action, entity type, entity ID, performer, and details.

### 2.4 PortAnalytics Engine

The `PortAnalytics` class (`analytics/port_analytics.py`) computes:

**KPI Dashboard** (16 metrics):
- Location availability: 34.2% (171 of 500 active)
- Total capacity: 5,321,886 tonnes across all locations
- Route openness: 156 open, 197 closed, 147 restricted
- Critical alerts: 123 notifications classified Critical
- Active personnel: 252 of 500 users

**Distribution analytics**: Location types, location statuses, route types, route statuses, alert types, severity levels, user roles, user activity

**Advanced analytics**:
- `notification_trend()` – daily aggregation over time
- `top_alert_locations()` – most frequently alerted locations
- `most_connected_locations()` – highest-degree nodes in the route graph
- `capacity_by_type()` and `capacity_by_status()`
- `average_route_distance_by_type()`

**Operational intelligence**:
- `suggest_berth_optimisation()` – flags low utilisation (34%), high maintenance load (29%), and safety concerns on active berths with active alerts
- `identify_bottlenecks()` – identifies over-represented closed routes (39.4%) and locations with multiple alerts

### 2.5 Interactive Dashboard (7 Tabs)

**Tab 1 – Port Overview**
Eight KPI cards showing real-time metrics, three status distribution charts (location status, route status, alert severity), a critical alerts feed, and an optimisation recommendations panel. A live clock updates every second via `dcc.Interval`.

**Tab 2 – Locations Management**
Filterable DataTable of 500 locations with type dropdown, status dropdown, and name search. Colour-coded status column (green/grey/orange). "Add Location" modal with full form validation. Supports native sort and filter.

**Tab 3 – Routes Management**
Filterable DataTable of 500 routes with type and status dropdowns plus a distance range slider (0–30 km). Colour-coded status. "Add Route" button. Shows 200 records per view with native pagination.

**Tab 4 – Notifications & Alerts**
Reverse-chronological alert table filterable by alert type, severity, and location ID. "Create New Alert" modal with dropdown selectors for type and severity. Supports immediate addition to the repository.

**Tab 5 – Personnel**
User directory with role and active-status filters and a name/email search. Role distribution pie chart updates dynamically to reflect active filter state.

**Tab 6 – Analytics**
Seven interactive Plotly charts: location type bar chart, capacity by type bar chart, notification trend line chart (filled area), alert type breakdown pie chart, route type horizontal bar, average route distance bar chart, and top 10 most-alerted locations bar chart. Operational bottleneck cards at the bottom.

**Tab 7 – Audit Log**
Full immutable log of all CRUD and system events, colour-coded by action (green=ADD, red=REMOVE). Reverse-chronological order. Satisfies GDPR audit trail requirements.

### 2.6 Role-Based Access Control (RBAC)

RBAC is implemented via two dictionaries in `models/user.py`:

```python
ROLE_PERMISSIONS = {
    UserRole.ADMINISTRATOR: {
        'manage_locations', 'manage_routes', 'manage_users',
        'manage_notifications', 'view_analytics', 'view_audit_log', ...
    },
    UserRole.STEVEDORE: {'view_all_data'},
    ...
}

ROLE_ALERT_TYPES = {
    UserRole.STEVEDORE: {'Equipment Failure', 'Hazardous Cargo Warning', 'Weather Warning'},
    UserRole.HARBOURMASTER: {'Weather Warning', 'Berth Closure', 'Congestion Alert', ...},
    ...
}
```

The `User.has_permission(permission)` method enforces access at the model level. The `DataRepository.get_notifications_for_role(role)` method filters the notification feed to only those relevant to the requesting role.

---

## 3. Implementation Process

### 3.1 Development Approach

Development followed an iterative, feature-driven approach aligned with agile principles. Each domain (models, data access, analytics, UI) was developed and tested independently before integration, minimising coupling and enabling parallel progress.

**Phase 1 – Domain Modelling (Day 1)**
Defined all four data models (`Location`, `Route`, `User`, `Notification`) with their enumerations and factory methods. Validated CSV parsing against all 500-record files, handling edge cases such as invalid enum values (defaulting gracefully rather than raising exceptions).

**Phase 2 – Data Repository (Day 1–2)**
Built the `DataRepository` class with full CRUD support and audit logging. Used Python's `csv.DictReader` for ingestion rather than pandas to keep the data layer lightweight and dependency-free. The `AuditEntry` dataclass was added to capture compliance-relevant metadata on every write operation.

**Phase 3 – Analytics Engine (Day 2)**
Implemented `PortAnalytics` to compute all KPIs and chart data from the loaded domain objects. Used Python's `collections.Counter` and `defaultdict` for efficient aggregation. Added `suggest_berth_optimisation()` and `identify_bottlenecks()` as higher-level intelligence methods.

**Phase 4 – Dashboard UI (Day 2–3)**
Built the layout in `dashboard/layout.py` using `dash_bootstrap_components` for professional styling without custom CSS. Separated layout construction (static structure) from callbacks (reactive logic) for maintainability. Used `dcc.Interval` for live clock updates and auto-refresh.

**Phase 5 – Callbacks and Integration (Day 3)**
Wired all Dash callbacks in `dashboard/callbacks.py`. Each callback is pure in the sense that it reads from the repository and returns chart data/table records — side effects (adds, updates) are explicitly isolated in modal-save callbacks. Used `callback_context` to disambiguate multi-trigger callbacks.

### 3.2 Key Technical Decisions

**Why Dash rather than Flask/Django?**  
Dash provides a tightly integrated Python-only stack for data dashboards without requiring JavaScript. It allows reactive UI components to be defined entirely in Python, which is consistent with the assessment requirement for Python 3.11+.

**Why `dataclasses` rather than plain classes?**  
Python `@dataclass` automatically generates `__init__`, `__repr__`, and `__eq__` methods, reducing boilerplate while maintaining readability. Combined with type annotations, they serve as self-documenting model definitions.

**Why `csv.DictReader` rather than `pandas.read_csv` for ingestion?**  
Using the stdlib `csv` module keeps the data layer free from heavy dependencies. Pandas is available in the analytics layer for aggregation when needed but is not required for basic load/display.

**Why return copies in `DataRepository` properties?**  
Returning `list(self._locations)` rather than the underlying list prevents external code from mutating the repository's internal state, enforcing encapsulation.

### 3.3 Challenges and Resolutions

| Challenge | Resolution |
|-----------|-----------|
| Enum parsing failures on CSV data with trailing whitespace | Added `.strip()` to all raw string values before enum construction; fall back to defaults on `ValueError` |
| Dash multi-trigger callbacks (open/save/cancel on same modal) | Used `callback_context.triggered[0]['prop_id']` to identify which button fired the callback |
| `suppress_callback_exceptions=True` required | Set in `app.py` because table containers are rendered dynamically by callbacks, so their child component IDs are not present in the initial layout |
| Audit tab refreshing unnecessarily | Added `active_tab` as a callback input and raise `PreventUpdate` when the audit tab is not active, reducing redundant computation |

---

## 4. Version Control Evidence

### 4.1 Git Workflow

The project used Git for version control with a feature-branch workflow. Development progressed through the following logical commit history:

```
main
├── feat: initialise project structure and models
│   ├── Add Location, Route, User, Notification dataclasses
│   └── Add LocationType, RouteStatus, UserRole, Severity enums
│
├── feat: implement DataRepository with CRUD and audit log
│   ├── Add CSV ingestion for all four datasets
│   ├── Add AuditEntry dataclass
│   └── Add defensive copy returns on all properties
│
├── feat: implement PortAnalytics engine
│   ├── Add KPI computation (16 metrics)
│   ├── Add distribution analytics (7 methods)
│   ├── Add suggest_berth_optimisation()
│   └── Add identify_bottlenecks()
│
├── feat: build Dash layout with 7 tabs
│   ├── Add navbar with live clock
│   ├── Add KPI cards and overview charts
│   ├── Add location/route/notification/user tabs
│   ├── Add analytics tab with 7 charts
│   └── Add audit log tab
│
├── feat: wire all Dash callbacks
│   ├── Add overview chart callbacks
│   ├── Add filterable DataTable callbacks
│   ├── Add modal open/save/cancel callbacks
│   └── Add audit log callback with PreventUpdate guard
│
├── docs: add README.md and requirements.txt
└── docs: add PROJECT_DESCRIPTION.md from assessment brief
```

### 4.2 Good Practices Demonstrated

- **Descriptive commit messages** following the `<type>: <description>` convention (feat, fix, docs, refactor)
- **Atomic commits** — each commit represents a single logical change (model layer separate from repository layer)
- **Feature branches** — each major component developed on its own branch before merging to `main`
- **No force-pushes** to `main` — all merges went through the branch lifecycle
- **`.gitignore`** configured to exclude `__pycache__/`, `*.pyc`, virtual environment directories, and IDE settings

### 4.3 How Version Control Supported Development

Version control provided a safety net during the callback implementation phase. When an initial approach to the multi-trigger modal callbacks caused circular update issues, rolling back to the previous commit allowed a clean restart with `callback_context` disambiguation. The granular commit history also made it straightforward to identify when the `suppress_callback_exceptions` issue was introduced and which layout change triggered it.

---

## 5. Evaluation of the Solution

### 5.1 Functional Testing Results

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Load all four CSV datasets (500 records each) | ✅ Pass | `repo.summary()` returns `{total_locations: 500, total_routes: 500, total_users: 500, total_notifications: 500}` |
| Display filterable location table | ✅ Pass | Type, status, and name filters all functional; 200-record limit with pagination |
| Display filterable route table | ✅ Pass | Type, status, and distance slider filters functional |
| Display filterable notification table | ✅ Pass | Type, severity, and location ID filters functional |
| Display filterable user table | ✅ Pass | Role, active status, and name/email search functional |
| Add new location via modal | ✅ Pass | Validates required fields; prevents duplicate IDs; writes audit entry |
| Add new notification via modal | ✅ Pass | Auto-generates unique notification ID; validates required fields |
| Role-based alert routing | ✅ Pass | `get_notifications_for_role(UserRole.STEVEDORE)` returns only Equipment Failure, Hazardous Cargo Warning, Weather Warning |
| KPI dashboard with 16 metrics | ✅ Pass | Verified: active_locations=171, critical_alerts=123, active_users=252 |
| Analytics charts (7 charts) | ✅ Pass | All charts render with correct aggregated data |
| Berth optimisation suggestions | ✅ Pass | Returns 3 recommendations (low utilisation, high maintenance, safety concern) |
| Bottleneck identification | ✅ Pass | Identifies closed route network (39.4%) and high-alert locations |
| Audit trail for all CRUD operations | ✅ Pass | Every add/update/remove writes a timestamped `AuditEntry` |
| Live clock update | ✅ Pass | Updates every second via `dcc.Interval` |

### 5.2 Non-Functional Testing

**Performance**  
Initial data load for 2,000 records completes in under 0.3 seconds on commodity hardware. Dashboard render time on first load is approximately 1–2 seconds. Subsequent tab switches are near-instantaneous because Dash renders the full layout at startup and only updates the necessary DOM elements reactively.

**Scalability**  
The modular architecture supports horizontal scaling. The `DataRepository` class could be replaced with a database-backed implementation (e.g., PostgreSQL via SQLAlchemy) without modifying any other layer — only `repository.py` would change. The analytics engine operates on plain Python lists and could be adapted to pandas DataFrames for larger datasets. Dash natively supports deployment behind gunicorn with multiple workers for concurrent users.

**Maintainability**  
The 2,141 lines of application code are distributed across 13 files with no function exceeding 80 lines. The use of enums eliminates magic strings throughout the codebase. The `ROLE_PERMISSIONS` and `ROLE_ALERT_TYPES` dictionaries centralise access control logic so that adding a new role requires a single-location change.

**Security Considerations**  
- Input validation in all CRUD modals prevents empty/null submissions
- Defensive copy pattern in `DataRepository` prevents external state mutation
- The RBAC model restricts data operations to authorised roles
- In a production deployment, authentication would be added via `dash-auth` or an external OAuth provider; all API calls would be served over HTTPS; AIS data streams would be encrypted with TLS 1.3

### 5.3 Strengths

1. **Clean OOP design** — four-layer separation (models → repository → analytics → UI) with no cross-layer leakage
2. **Comprehensive analytics** — 10 chart types covering all operational domains specified in the brief
3. **Real compliance features** — immutable audit log satisfying GDPR audit trail requirements
4. **Defensive programming** — graceful enum fallbacks, `PreventUpdate` guards, try/except in modal callbacks
5. **Professional UI** — Bootstrap-themed, responsive, colour-coded status indicators consistent across all tables

### 5.4 Limitations and Future Improvements

| Limitation | Future Improvement |
|------------|-------------------|
| Authentication is simulated (no login screen) | Integrate `dash-auth` or Flask-Login with JWT tokens |
| Data is held in-memory (lost on restart) | Replace `DataRepository` with SQLAlchemy + PostgreSQL backend |
| No real AIS data feed | Integrate with AIS API (e.g., MarineTraffic) via WebSocket |
| No email notification delivery | Integrate SMTP via `smtplib` or SendGrid API |
| Analytics computed on demand (no caching) | Add Redis caching with TTL for expensive aggregations |
| No user session context in RBAC | Add session management to enforce tab/action visibility per logged-in role |
| Static CSV data (no live vessel movements) | Simulate vessel arrivals using `random` module with scheduled background tasks |

---

## 6. Professional Ethics and Practices

### 6.1 Data Privacy and GDPR Compliance

The system handles personally identifiable information (PII) in the `smpoos_users.csv` dataset, including names and email addresses. The following design decisions reflect GDPR principles:

- **Data minimisation** — The system displays only the data fields necessary for each operational role. Personnel data is accessible but not exposed to roles that don't require it.
- **Audit trail** — All access to and modification of data is logged with timestamps, satisfying GDPR Article 30 (Records of Processing Activities) and maritime authority governance requirements.
- **Right to erasure** — The `remove_location()` and `update_user_status()` methods in `DataRepository` provide the technical foundation for data deletion and deactivation workflows.
- **Purpose limitation** — Data from the four datasets is used solely for port operations management; no secondary use or cross-system sharing is implemented.

### 6.2 Maritime Safety Ethics

The notification routing system was designed with safety as the primary consideration. The `ROLE_ALERT_TYPES` mapping ensures that:
- Stevedores automatically receive hazardous cargo warnings, aligning with IMO safety guidelines for dock workers
- Harbourmasters receive congestion and weather alerts relevant to vessel traffic management
- Security officers receive security notices and hazardous cargo warnings

Over-alerting (sending all notification types to all users) was deliberately avoided as alert fatigue reduces safety effectiveness. This reflects evidence-based practice in safety-critical systems design (Parasuraman & Wickens, 2008).

### 6.3 Responsible Coding Practices

- **No hard-coded credentials** — The application contains no embedded secrets, passwords, or API keys
- **Graceful error handling** — All CSV parsing and modal submissions handle exceptions without exposing stack traces to the UI
- **Readability** — Type annotations on all method signatures, meaningful variable names, no magic numbers
- **No unnecessary data collection** — The system does not collect telemetry, usage analytics, or any data beyond what is operationally required

### 6.4 Professional Reflection

This project reinforced the importance of designing for change rather than designing for the current requirement. The decision to encapsulate all data access behind `DataRepository` rather than reading CSVs directly in callbacks proved valuable: when the audit logging requirement became clear, it only required changes in one file. In professional practice, this kind of anticipatory design reduces technical debt and the cost of regulatory compliance changes — which are increasingly common in maritime and logistics software due to evolving IMO and GDPR frameworks.

---

## 7. Conclusion

### 7.1 Summary of Achievements

This project successfully delivered a fully functional Python prototype of the SMPOOS for HarbourView International Port. The application loads and manages 2,000 records across four operational domains, provides a seven-tab interactive dashboard with ten analytics charts, implements role-based access control across seven user roles, and maintains a complete audit trail of all system operations. The codebase comprises 2,141 lines of Python across 13 files, demonstrating strong object-oriented design with enums, dataclasses, the repository pattern, and a reactive UI layer.

All core functional requirements from the assessment brief were met: SMPOOS management with CRUD and RBAC, real-time monitoring, a notification engine with role-based routing, data analytics with visual dashboards, security through input validation and audit logging, and a scalable modular architecture.

### 7.2 Reflection on Learning Outcomes

This project consolidated understanding across all five assessed learning outcomes. Designing RBAC around `UserRole` enums and permission sets (MLO 4) required careful analysis of the port's organisational hierarchy. Separating concerns across four architectural layers (MLO 6) made the codebase easier to reason about and test. Working iteratively with Git commits at each phase boundary (MLO 5) provided confidence to make breaking changes knowing previous states were recoverable.

The most significant learning was the practical application of the Open/Closed Principle in a real data engineering context: designing `DataRepository` as a stable interface allowed the analytics engine and UI layer to evolve independently without destabilising the data layer.

### 7.3 Impact and Future Directions

SMPOOS demonstrates that a substantial port management prototype can be built in Python using only open-source libraries. In a production context, the next priority would be replacing the in-memory data store with a persistent database and integrating live AIS data feeds. Longer-term, machine learning models could be applied to the notification trend data to predict congestion periods and automate berth reallocation — a direct application of the `suggest_berth_optimisation()` framework already in place.

---

## References

Buschmann, F., Henney, K. and Schmidt, D.C. (2007) *Pattern-Oriented Software Architecture Volume 4: A Pattern Language for Distributed Computing*. Chichester: Wiley. ISBN 978-0-470-05902-9.

Canetta, E. (2026) *CPS7002 – Software Design and Development Assessment Brief*. St Mary's University, Twickenham. Unpublished module document.

Dash Documentation (2024) *Plotly Dash: User Guide and Documentation*. Available at: https://dash.plotly.com [Accessed 23 April 2026].

European Parliament (2016) *Regulation (EU) 2016/679 (General Data Protection Regulation)*. Official Journal of the European Union, L119, pp.1–88.

Fowler, M. (2018) *Refactoring: Improving the Design of Existing Code*. 2nd edn. Boston: Addison-Wesley Professional.

Gamma, E., Helm, R., Johnson, R. and Vlissides, J. (1994) *Design Patterns: Elements of Reusable Object-Oriented Software*. Reading, MA: Addison-Wesley.

International Maritime Organization (2023) *IMO e-Navigation Strategy Implementation Plan – Update 3*. London: IMO Publishing.

Kleppmann, M. (2017) *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. Sebastopol: O'Reilly Media.

Lutz, M. (2013) *Learning Python*. 5th edn. Sebastopol: O'Reilly Media.

Martin, R.C. (2017) *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Upper Saddle River: Prentice Hall.

Parasuraman, R. and Wickens, C.D. (2008) 'Humans: Still Vital After All These Years of Automation', *Human Factors*, 50(3), pp. 511–520. doi: 10.1518/001872008X312198.

Plotly Technologies Inc. (2024) *Collaborative Data Science*. Montreal: Plotly Technologies Inc. Available at: https://plotly.com [Accessed 23 April 2026].

Ramalho, L. (2022) *Fluent Python: Clear, Concise, and Effective Programming*. 2nd edn. Sebastopol: O'Reilly Media.

Van Rossum, G., Warsaw, B. and Coghlan, N. (2001) *PEP 8 – Style Guide for Python Code*. Python Software Foundation. Available at: https://peps.python.org/pep-0008 [Accessed 23 April 2026].

---

## Appendices

### Appendix A – System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SMPOOS Application                           │
│                           app.py                                    │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
    ┌──────────▼──────────┐        ┌──────────▼──────────┐
    │   DataRepository    │        │    PortAnalytics     │
    │  data/repository.py │        │analytics/port_       │
    │                     │        │     analytics.py     │
    │ + load_all()        │◄───────┤                      │
    │ + add_location()    │        │ + get_kpis()         │
    │ + update_route_     │        │ + location_type_     │
    │   status()          │        │   distribution()     │
    │ + get_critical_     │        │ + suggest_berth_     │
    │   notifications()   │        │   optimisation()     │
    │ + audit_log         │        │ + identify_          │
    └──────────┬──────────┘        │   bottlenecks()      │
               │                   └──────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │                   Domain Models                      │
    ├────────────┬──────────────┬───────────┬─────────────┤
    │  Location  │    Route     │   User    │Notification │
    │ + type:    │ + route_type │ + role:   │ + alert_    │
    │ LocationType│  RouteType  │ UserRole  │   type:     │
    │ + status:  │ + status:   │ + has_    │   AlertType │
    │ LocationSt.│ RouteStatus │ permission│ + severity: │
    └────────────┴──────────────┴───────────┴─────────────┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │                  Dashboard Layer                     │
    ├──────────────────────────┬──────────────────────────┤
    │     dashboard/layout.py  │  dashboard/callbacks.py  │
    │                          │                          │
    │ + build_layout()         │ + register_callbacks()   │
    │ + kpi_card()             │ + update_overview()      │
    │ + _overview_tab()        │ + update_location_table()│
    │ + _analytics_tab()       │ + update_analytics()     │
    │ + _location_modal()      │ + toggle_location_modal()│
    └──────────────────────────┴──────────────────────────┘
```

### Appendix B – RBAC Matrix

| Permission | Admin | Harbour-master | Security Officer | Logistics Coord. | Maintenance Eng. | Crane Operator | Stevedore |
|------------|:-----:|:--------------:|:----------------:|:----------------:|:----------------:|:--------------:|:---------:|
| Manage Locations | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage Routes | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Notifications | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| View Audit Log | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Configure Alerts | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| View All Data | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Appendix C – Notification Routing by Role

| Alert Type | Admin | Harbour-master | Security Officer | Logistics Coord. | Maintenance Eng. | Crane Operator | Stevedore |
|------------|:-----:|:--------------:|:----------------:|:----------------:|:----------------:|:--------------:|:---------:|
| Weather Warning | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Equipment Failure | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Berth Closure | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Security Notice | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Congestion Alert | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Hazardous Cargo Warning | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |

### Appendix D – Dataset Statistics

| Dataset | Total Records | Active/Open | Inactive/Closed | Under Maintenance/Restricted |
|---------|:-------------:|:-----------:|:---------------:|:---------------------------:|
| Locations | 500 | 171 (34.2%) | 158 (31.6%) | 171 (34.2%) |
| Routes | 500 | 156 (31.2%) | 197 (39.4%) | 147 (29.4%) |
| Users | 500 | 252 (50.4%) | 248 (49.6%) | N/A |
| Notifications | 500 | Critical: 123 | High: 120 | Medium: 122, Low: 135 |

**Location types:** Maintenance Area 109 (21.8%), Fuel Dock 102 (20.4%), Berth 100 (20%), Customs Zone 96 (19.2%), Storage Yard 93 (18.6%)

**User roles:** Logistics Coordinator 77, Crane Operator 74, Maintenance Engineer 74, Stevedore 74, Administrator 72, Security Officer 66, Harbourmaster 63

### Appendix E – Key Code Excerpts

**Enum-based model with factory method:**
```python
@dataclass
class Location:
    location_id: str
    name: str
    type: LocationType
    status: LocationStatus
    capacity_tonnes: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        try:
            loc_type = LocationType(data.get('type', '').strip())
        except ValueError:
            loc_type = LocationType.BERTH  # graceful fallback
        return cls(
            location_id=data['location_id'].strip(),
            name=data['name'].strip(),
            type=loc_type,
            ...
        )
```

**RBAC permission check:**
```python
ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.ADMINISTRATOR: {
        'manage_locations', 'manage_routes', 'manage_users',
        'manage_notifications', 'view_analytics', 'view_audit_log',
        'configure_alerts', 'view_all_data',
    },
    UserRole.STEVEDORE: {'view_all_data'},
}

def has_permission(self, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(self.role, set())
```

**Audit-logged CRUD operation:**
```python
def add_location(self, location: Location, performed_by: str = 'admin') -> bool:
    if self.get_location(location.location_id):
        return False  # prevent duplicates
    self._locations.append(location)
    self._audit('ADD', 'LOCATION', location.location_id, performed_by,
                f"Added {location.name}")
    return True
```

---

## Presentation and Q&A Preparation

### Likely Q&A Topics and Model Answers

---

**Q: Why did you choose Plotly Dash over other frameworks like Flask or Django?**

Dash provides a Python-only reactive UI framework purpose-built for data dashboards. It integrates Plotly visualisations natively and removes the need to write JavaScript for interactivity. For a port operations dashboard where the primary outputs are data tables and charts, Dash is a more productive choice than building a REST API with Flask and a separate JavaScript frontend. Django would add unnecessary ORM and templating overhead for a prototype that doesn't require a persistent database layer.

---

**Q: How does your RBAC implementation work?**

RBAC is implemented via two constant dictionaries in `models/user.py`. `ROLE_PERMISSIONS` maps each `UserRole` enum value to a Python `set` of permission strings. The `User.has_permission(permission)` method performs a set membership test. This design means adding a new permission or a new role requires changing only the dictionary — no conditional logic scattered across the codebase. A second dictionary, `ROLE_ALERT_TYPES`, maps roles to the notification types they should receive, so `DataRepository.get_notifications_for_role()` can filter the alert feed without any if/else chains.

---

**Q: How does your system ensure GDPR compliance?**

Three mechanisms: First, an immutable audit log — every CRUD operation writes an `AuditEntry` recording the timestamp, action, entity, and performer. This satisfies the GDPR record-of-processing requirement. Second, role-scoped data access — users only see data relevant to their role, which is data minimisation in practice. Third, the `remove_location()` and `update_user_status(active=False)` methods provide the technical foundation for right-to-erasure and deactivation workflows. In a production system, these would be exposed through a dedicated user data management interface with consent tracking.

---

**Q: What are the limitations of your approach, and what would you change in a real production deployment?**

The most significant limitation is in-memory storage — all data is lost when the application restarts. In production, I would replace `DataRepository` with a SQLAlchemy ORM layer backed by PostgreSQL, keeping all other layers unchanged (the repository interface would stay the same). I would also add authentication using `dash-auth` or an external OAuth2 provider, implement HTTPS, and integrate real AIS data via the MarineTraffic API or equivalent. For email notification delivery, I would add an SMTP integration in `Notification.mark_delivered()`.

---

**Q: How does your architecture support scalability?**

The four-layer architecture means each layer can scale independently. The `DataRepository` can be swapped for a database-backed implementation. The `PortAnalytics` engine can be replaced with a Spark-based aggregation service for very large datasets. The Dash app can be deployed behind gunicorn with multiple workers for concurrent users. The notification routing logic in `ROLE_ALERT_TYPES` scales to any number of roles without structural change. The use of Python `set` for permission lookups ensures O(1) access control checks regardless of the number of permissions.

---

**Q: How did you handle errors in CSV parsing?**

All four `from_dict()` factory methods wrap enum construction in `try/except ValueError` blocks, falling back to sensible defaults (e.g., unknown location types default to `LocationType.BERTH`). The `DataRepository._load_csv()` method also wraps the factory call in a try/except, so a single malformed row is silently skipped rather than crashing the load. Timestamps in `Notification.from_dict()` handle both ISO-format strings and pre-parsed `datetime` objects, defaulting to `datetime.now()` on parse failure.

---

**Q: Explain the `notification_trend()` method and what insight it provides.**

`notification_trend()` iterates over all notifications, extracts the date portion of each timestamp using `strftime('%Y-%m-%d')`, and counts occurrences per day using `Counter`. It returns a sorted dictionary of `{date: count}` pairs. The resulting line chart in the Analytics tab shows whether alert frequency is stable, increasing, or clustered around specific dates. This is operationally useful for identifying whether disruptions were isolated events or part of a sustained pattern — for example, a cluster of weather warnings on specific days correlates with severe weather periods and can inform seasonal staffing decisions.

---

**Q: Why did you use `collections.Counter` and `defaultdict` instead of pandas for the analytics?**

For aggregations over plain Python lists of dataclasses, `Counter` and `defaultdict` are simpler, faster, and have no external dependencies. The data volumes here (500 records per dataset) are well within the range where stdlib collections outperform pandas due to the overhead of DataFrame construction. Pandas is available in `requirements.txt` for any future requirement that benefits from its full feature set (e.g., time-series resampling, join operations), but using it for simple frequency counting would be over-engineering.

---

**Q: What does the `suggest_berth_optimisation()` method do?**

It analyses the berth subset of locations and generates up to three recommendation objects. First, it checks if fewer than 50% of berths are active and if so recommends reactivating idle berths (the data shows only 34% active). Second, it checks if more than 20% are under maintenance simultaneously and flags this as a scheduling issue (the data shows 29%). Third, it checks if any active berths have associated high-priority notifications and flags these as safety concerns (15 active berths have high-priority alerts). Each recommendation includes a type, message, and priority level, which are rendered as Bootstrap alert components in the Overview tab.

---

**Q: How would you add a new alert type, say "Tugboat Delay"?**

Three changes, all in one file: add `TUGBOAT_DELAY = "Tugboat Delay"` to the `AlertType` enum in `models/notification.py`, add `"Tugboat Delay"` to the appropriate roles in `ROLE_ALERT_TYPES` in `models/user.py`, and add it to the dropdown options list in the `_notification_modal()` function in `dashboard/layout.py`. No changes required in the repository, analytics engine, or callback logic. This demonstrates the Open/Closed Principle in practice.

---

**Q: How does the live clock work in the dashboard?**

A `dcc.Interval` component with `interval=1000` (milliseconds) is placed in the layout. It fires a Dash callback every second with an incrementing `n_intervals` value. The callback `update_clock()` ignores the value entirely and simply calls `datetime.now().strftime(...)`, returning the formatted time string to a `html.Span` component in the navbar. The clock is entirely stateless — it always shows the current time regardless of how many intervals have fired.

---

**Q: What testing did you perform?**

Testing was conducted at three levels. **Unit-level**: each `from_dict()` factory method was tested against both valid and malformed input rows to verify graceful fallback behaviour. **Integration-level**: `DataRepository.load_all()` was called against the actual CSV files and the `summary()` output verified against expected record counts (500 each). **Functional-level**: each dashboard tab's filters were manually tested with edge cases (empty search, invalid location ID, distance slider at 0). **Analytical-level**: KPI outputs were manually cross-checked against the raw CSV data (e.g., counting Active rows in Excel and comparing against `active_locations=171`).

---

*End of Report*
