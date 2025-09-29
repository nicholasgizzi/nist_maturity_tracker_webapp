# NIST CSF Maturity Tracker

A Flask web application for tracking and managing cybersecurity maturity scores by mapping organizational systems and tools to NIST Cybersecurity Framework (CSF) categories and functions.

## Overview

This application helps organizations assess their cybersecurity posture against the NIST CSF by:
- Tracking systems and their cybersecurity tools
- Mapping systems to NIST CSF subcategories with maturity scores (0-5)
- Managing risks with severity/likelihood assessments
- Providing dashboard views of organizational security maturity
- Supporting compliance reporting and audit preparation

## Architecture

### Core Technologies
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: LDAP3 integration with Flask-Login
- **Migrations**: Flask-Migrate (Alembic)
- **Frontend**: Jinja2 templates with vanilla JavaScript

### Project Structure
```
nist_tracker_webapp/
├── app/
│   ├── __init__.py              # Flask app factory & NIST function definitions
│   ├── models.py                # SQLAlchemy data models
│   ├── blueprints/              # Feature modules
│   │   ├── auth.py              # Authentication & LDAP integration
│   │   ├── dashboard.py         # Main dashboard views
│   │   ├── systems.py           # System management
│   │   ├── mappings.py          # System-to-NIST mappings
│   │   ├── functions.py         # NIST function views
│   │   ├── priorities.py        # Priority management
│   │   ├── risks.py             # Risk register
│   │   └── ldap_auth.py         # LDAP utilities
│   ├── templates/               # Jinja2 HTML templates
│   └── static/                  # CSS/JS assets
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific config (not in git)
├── run.py                      # Application entry point
├── seed.py                     # Database seeding script
└── requirements.txt            # Python dependencies
```

### Data Models

**NIST Framework Structure:**
- `Category`: Top-level NIST categories (GV, ID, PR, DE, RS, RC)
- `Subcategory`: Specific NIST subcategories within each category

**Organizational Data:**
- `System`: Organizational systems/tools being tracked
- `SystemMapping`: Links systems to NIST subcategories with maturity scores
- `Review`: Historical review records for mappings

**Risk Management:**
- `Risk`: Risk register entries with severity/likelihood matrix
- Supports risk status tracking (Open, In Progress, Mitigated, Accepted)

### NIST CSF Implementation

The application implements the 6 core NIST functions:
- **GV** (Govern) - #F8F1C8
- **ID** (Identify) - #4DB2E6
- **PR** (Protect) - #C079D6
- **DE** (Detect) - #FDBE5A
- **RS** (Respond) - #D9241F
- **RC** (Recover) - #82CF6B

Each function contains categories and subcategories that can be mapped to organizational systems with maturity scores ranging from 0-5.

### Application Flow

```mermaid
graph TD
    A[Executive Dashboard] --> B[NIST CSF Functions]
    A --> C[Risk Register]
    A --> D[System Overview]

    B --> E[Govern - GV]
    B --> F[Identify - ID]
    B --> G[Protect - PR]
    B --> H[Detect - DE]
    B --> I[Respond - RS]
    B --> J[Recover - RC]

    E --> K[Categories & Subcategories]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K --> L[System Mappings]
    L --> M[Maturity Scores 0-5]

    C --> N[Risk Assessment]
    N --> O[Severity × Likelihood]
    O --> P[Risk Mitigation Plans]

    D --> Q[System Inventory]
    Q --> R[Security Tool Coverage]
    R --> S[Compliance Gaps]

    style A fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#f96,stroke:#333,stroke-width:2px
    style M fill:#9f9,stroke:#333,stroke-width:2px
    style P fill:#99f,stroke:#333,stroke-width:2px
```

### Data Architecture

```mermaid
erDiagram
    CATEGORY ||--o{ SUBCATEGORY : contains
    SUBCATEGORY ||--o{ SYSTEM_MAPPING : "mapped to"
    SYSTEM ||--o{ SYSTEM_MAPPING : "assessed in"
    SYSTEM_MAPPING ||--o{ REVIEW : "reviewed via"
    RISK }o--|| RISK_STATUS : has

    CATEGORY {
        string code "GV, ID, PR, DE, RS, RC"
        string name
        text description
    }

    SUBCATEGORY {
        string code "e.g. ID.AM-1"
        string name
        text description
        enum priority "LOW, MEDIUM, HIGH"
    }

    SYSTEM {
        string name
        text description
        string owner
        datetime added_on
    }

    SYSTEM_MAPPING {
        int score "0-5 maturity score"
        datetime last_reviewed
        string reviewer
        text notes
    }

    RISK {
        string code
        text description
        int severity "1-5"
        int likelihood "1-5"
        string owner
        enum status "Open, In Progress, Mitigated, Accepted"
    }
```

## Features

- **System Management**: Track organizational cybersecurity systems and tools
- **NIST Mapping**: Map systems to specific NIST CSF subcategories
- **Maturity Scoring**: Score system implementations from 0-5 with review history
- **Risk Register**: Comprehensive risk management with severity/likelihood matrix
- **Dashboard Views**: Visual overview of organizational security posture
- **Priority Management**: Set and track priorities across NIST subcategories
- **LDAP Authentication**: Enterprise authentication with dev-mode bypass
- **Audit Trail**: Track changes and reviews over time  

---

## Prerequisites

- Python 3.10+  
- `git`  
- (Production) Access to your LDAP server  
- (Optional) PostgreSQL/MySQL or SQLite  

---

## Local Development Setup

1. **Clone**  
   ```bash
   git clone https://github.com/nicholasgizzi/nist_tracker_webapp.git
   cd nist_tracker_webapp
   ```

2. **Create & activate a venv**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy & edit config**  
   ```bash
   cp instance/config.example.py instance/config.py
   ```
   In `instance/config.py`, set:
   ```python
   # — Database (dev)
   SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'

   # — LDAP (placeholders; not used in dev bypass)
   LDAP_DOMAIN       = 'your.domain.com'
   LDAP_SERVER       = 'ldap://your-ldap-server'
   LDAP_SEARCH_BASE  = 'DC=your,DC=domain,DC=com'
   LDAP_GROUP        = 'your_group_cn'

   # — Dev-mode bypass
   AUTH_DISABLED     = True
   DEV_USERNAME      = 'admin'
   DEV_PASSWORD      = 'admin'
   ```

5. **Initialize the database**  
   ```bash
   export FLASK_ENV=development
   flask db upgrade
   python seed.py
   ```

6. **Run in dev mode**  
   ```bash
   flask run
   ```
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) and log in with your dev credentials (`admin`/`admin`).

---

## Production / LDAP Setup

1. **Adjust `instance/config.py`**  
   Remove or set the dev bypass to `False`:
   ```python
   AUTH_DISABLED = False
   ```
   Then configure your real production values:
   ```python
   # Database (e.g. Postgres)
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@db-host/dbname'

   # LDAP
   LDAP_DOMAIN       = 'prod.domain.com'
   LDAP_SERVER       = 'ldap://ldap.prod.domain.com'
   LDAP_SEARCH_BASE  = 'DC=prod,DC=domain,DC=com'
   LDAP_GROUP        = 'production_group_cn'

   # Flask session secret
   SECRET_KEY        = 'a-very-secret-key'
   ```

2. **Deploy**  
   - Clone or pull to your server, e.g. `/srv/nist_tracker_webapp`  
   - Copy your production `instance/config.py` (keep it out of Git)  
   - Create/activate the venv & install requirements  
   - Run migrations & seed:  
     ```bash
     flask db upgrade
     python seed.py
     ```  
   - Restart your WSGI process (Gunicorn/uWSGI) and web server (Nginx).

---

## Example Deploy Script

```bash
#!/usr/bin/env bash
set -e

cd /srv/nist_tracker_webapp
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
flask db upgrade
python seed.py
sudo systemctl restart nist-tracker.service
```

---

## Notes

- After **any** model change:  
  ```bash
  flask db migrate -m "Describe changes"
  flask db upgrade
  ```  
- To update seed data:  
  ```bash
  python seed.py
  ```  
- When cloning for dev: remember to copy `instance/config.example.py` → `instance/config.py` and fill in your dev values.
