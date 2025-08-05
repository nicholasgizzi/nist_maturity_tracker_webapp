# nist_tracker_webapp

A Flask application for tracking cybersecurity maturity scores by mapping tools to NIST CSF categories and functions.

## Features

- LDAP authentication for production environments  
- Dev-mode credential bypass for local development  
- Database migrations with Flask-Migrate  
- Seed script to populate NIST CSF reference data  

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
