# CPS7002 – Software Design and Development
## Assessment Brief: Smart Maritime Port Operations Optimisation System (SMPOOS)

**Module Code:** CPS7002  
**Module Title:** Software Design and Development  
**Module Convenor:** Elisabetta Canetta  
**Assessment Weight:** 60%  
**Submission Deadline:** 3rd June 2026  

---

## Introduction

HarbourView International Port, one of the busiest logistics hubs in Europe, is planning to implement a **Smart Maritime Port Operations Optimisation System (SMPOOS)** to enhance operational efficiency, reduce vessel turnaround time, and improve safety in port environments.

The envisioned system integrates:

- **Vessel tracking** using AIS (Automatic Identification System) data
- **Predictive analytics** for berth allocation and congestion forecasting
- **Environmental sensors** for weather, tide, and air-quality monitoring
- **Location-based notifications** for hazards, delays, or workflow changes sent to dock workers and port administrators
- **An interactive management dashboard** accessible across devices, showing operational KPIs, predictive insights, and automated alerts

---

## System Requirements

### Non-Functional Requirements

The system must be:
- **Scalable** – to support large and growing vessel traffic
- **Maintainable** – allowing updates as port operations evolve
- **Secure** – due to the sensitivity of maritime logistics data

### Data Sources

The system integrates with the following CSV datasets:

| File | Description |
|------|-------------|
| `smpoos_locations.csv` | Port zones: Berths, Storage Yards, Fuel Docks, Customs Zones, Maintenance Areas |
| `smpoos_routes.csv` | Shipping lanes and internal transit paths |
| `smpoos_notifications.csv` | Port alerts and notifications |
| `smpoos_users.csv` | Port personnel with roles |

#### smpoos_locations.csv columns:
- `location_id` – Unique identifier
- `name` – Berth number + Area letter
- `type` – Berth, Storage Yard, Fuel Dock, Customs Zone, Maintenance Area
- `status` – Active, Inactive, Under Maintenance
- `capacity_tonnes` – Capacity in tonnes

#### smpoos_routes.csv columns:
- `route_id` – Unique identifier
- `start_location` / `end_location` – Location IDs
- `route_type` – Shipping Lane, Tugboat Transit Path, AGV Route, Truck Path
- `distance_km` – Distance in kilometres
- `status` – Open, Closed, Restricted

#### smpoos_notifications.csv columns:
- `notification_id` – Unique identifier
- `alert_type` – Weather Warning, Equipment Failure, Berth Closure, Security Notice, Congestion Alert, Hazardous Cargo Warning
- `location_id` – Associated location
- `severity` – Low, Medium, High, Critical
- `message` – Alert message text
- `timestamp` – Date/time of alert

#### smpoos_users.csv columns:
- `user_id` – Unique identifier
- `name` – User name
- `role` – Harbourmaster, Stevedore, Crane Operator, Administrator, Security Officer, Logistics Coordinator, Maintenance Engineer
- `email` – Contact email
- `active` – Yes/No

---

## Functional Requirements

### (a) SMPOOS Management

**Administrative Capabilities** – Admin users must be able to:
- Add, update, and remove port zones, berth areas, internal transport routes, and operational notifications via a secure interface
- Modify vessel paths, loading/unloading routes, or restricted areas in real time
- Use **Role-Based Access Control (RBAC)** to ensure only authorised personnel can modify operational data

**Operational Changes** – The system should support:
- Immediate reconfiguration of vessel and vehicle routes during temporary disruptions
- Automated recalculation of berth allocation based on new conditions

### (b) Real-Time Monitoring and Alerts/Notifications

**Operational Monitoring** must include:
- Vessel movements and estimated times of arrival/departure
- Berth occupancy
- Cargo-handling activity
- Environmental updates (wind speed, tide levels, visibility)
- System health and event logs

**Notification Engine** – Alerts delivered based on:
- **Location** (e.g., hazard near Berth 12)
- **Role** (e.g., stevedores receive safety alerts, harbourmasters receive congestion warnings)
- **Operational context** (delays, equipment faults, weather hazards, workflow changes)

**Notification Delivery** via:
- In-system notifications
- Email

**Admin Controls** – Admins can:
- Configure notification rules and thresholds
- Review a full audit trail of alerts including timestamps, severity, and delivery status

### (c) Regulatory Compliance

Must comply with:
- **GDPR** and similar regulatory frameworks
- **Maritime safety regulations** (e.g., IMO data handling guidelines)
- **Port authority governance requirements**

Must also:
- Include user consent mechanisms for personal/workforce data monitoring
- Support data access, portability, and deletion requests
- Maintain audit logs for all administrative actions, data modifications, and system access

### (d) Data Analytics and Reporting

Collect and analyse:
- Most used berths or port zones
- Common vessel routes or internal transport paths
- Peak congestion times
- Equipment utilisation rates
- Environmental trends (tidal patterns, wind delays)

Must also:
- Provide visual analytics dashboards for port managers and planners
- Enable custom report generation, filtered by date, vessel type, cargo type, or port area
- Use analytics to suggest berth allocation optimisations and identify operational bottlenecks

### (e) Security and Privacy

Must include:
- Secure authentication
- Encryption of sensitive data (in transit and at rest)
- Access control policies aligned with port security protocols
- Regular vulnerability scans, security audits, and patching

### (f) Management Dashboard

A responsive administrative dashboard providing:

**Key Widgets:**
- Port status overview (berth occupancy, vessel queue, environmental conditions)
- Vessel and vehicle activity
- Notifications and alerts panel
- Data analytics summaries (performance KPIs, congestion heatmaps)

**Customisation:**
- Custom dashboard layouts based on user roles
- Interactive map overlays (berth layout, shipping lanes, restricted zones)
- Filters, drill-downs, and historical playback of vessel movements

### (g) Scalability

To ensure long-term viability:
- Use a modular, layered architecture
- Support increased vessel data volume, more sensors, and more concurrent users
- Implement load balancing for AIS data processing and analytics services
- Use caching and stream-processing optimisations to maintain performance as port traffic grows

---

## Technical Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| IDE | VSCode / PyCharm / Jupyter Notebook |
| UI Framework | Plotly Dash + Dash Bootstrap Components |
| Data Processing | pandas, csv |
| Visualisation | plotly, matplotlib, seaborn |
| Data Models | Python dataclasses + enums |
| Version Control | Git / GitHub |
| Diagrams | Draw.io or equivalent |
| Report | Microsoft Word → PDF |

---

## Assessment Criteria

| Grade Band | Technical Competence | Problem Solving | Communication |
|------------|---------------------|-----------------|---------------|
| 80–100 Distinction | Exceptional proficiency; robust, secure, scalable | Outstanding problem-solving; real-time updates, advanced analytics | Highly articulate report; strong justification, diagrams, ethical reflection |
| 70–79 Distinction | Advanced technical skills; well-executed, mostly complete | Advanced strategies; clear logic and rationale | Clear and professional; well-organised with good evidence |
| 60–69 Merit | Good technical understanding; most features functional | Competent with reasonable decisions | Clear and informative; appropriate structure |
| 50–59 Pass | Basic competence; functional but may have flaws | Problem-solving evident but lacks sophistication | Communicates key ideas; structure may be weak |

---

## Submission Requirements

- **PDF Report** (3000 words): submitted separately, not in the zip file
- **Zip file** containing the software artefact + README.md
- Submit via Moodle by **3rd June 2026**

### Report Structure

1. **Title Page** – Project title, course title, submission date
2. **Abstract** (150–200 words)
3. **Introduction** (300–400 words) – Context, objectives, technologies, report structure
4. **Implemented Features** (500–600 words) – Feature descriptions with justification, diagrams
5. **Implementation Process** (400–500 words) – Step-by-step breakdown, tools, challenges
6. **Version Control Evidence** (300–400 words) – Git usage, commits, branches
7. **Evaluation of the Solution** (500–600 words) – Testing, performance, strengths/limitations
8. **Professional Ethics and Practices** (200–300 words)
9. **Conclusion** (200–300 words)
10. **References** – Minimum 12 sources, Harvard referencing style
11. **Appendices** – Additional diagrams, version control logs, full code

---

## Learning Outcomes Assessed

- **MLO 2** – Evaluate agile project management principles, risk management, team coordination, and ethical considerations
- **MLO 4** – Create, design, and test software systems meeting functional and non-functional requirements
- **MLO 5** – Employ Git for source code version control with branching, merging, and conflict resolution
- **MLO 6** – Develop and test software using an IDE with OOP best practices
- **MLO 7** – Demonstrate self-directed learning, reflection on professional development and ethical considerations
