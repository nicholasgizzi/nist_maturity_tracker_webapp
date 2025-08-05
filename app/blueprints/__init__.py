from flask import Flask, current_app, redirect, url_for
from flask_login import current_user, login_user
from app.blueprints.auth import auth_bp, LDAPUser

# factory in app/__init__.py
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)

app.register_blueprint(auth_bp, url_prefix='/auth')

# confirm nothing essential is missing
required = ["LDAP_DOMAIN","LDAP_SERVER","LDAP_SEARCH_BASE","LDAP_GROUP"]
missing  = [k for k in required if not app.config.get(k)]
if missing:
    raise RuntimeError(f"Missing LDAP config: {missing}")

@app.before_request
def auto_login_dev():
    """Auto-login a dev user when running in development mode."""
    # Only bypass in Flask debug mode
    if current_app.config.get('AUTH_DISABLED') and not current_user.is_authenticated:
        dev_username = current_app.config.get('DEV_USER', 'admin')
        user = LDAPUser(dev_username)
        login_user(user)
        return redirect(url_for('dashboard.dashboard'))