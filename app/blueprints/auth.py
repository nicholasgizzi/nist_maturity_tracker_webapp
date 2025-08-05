from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_user, logout_user, login_required
from ldap3 import Server, Connection, SIMPLE

auth_bp = Blueprint('auth', __name__)

class LDAPUser:
    """Minimal User object for Flask-Login."""
    def __init__(self, username):
        self.id = username  # flask-login uses `id` attribute

    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return self.id

from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    # We don’t have user rows in DB; just re-create from session id
    return LDAPUser(user_id)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        raw    = request.form['username'].strip()
        pw     = request.form['password']
        # Dev credentials bypass
        dev_username = current_app.config.get('DEV_USERNAME')
        dev_password = current_app.config.get('DEV_PASSWORD')
        if dev_username and dev_password and raw == dev_username and pw == dev_password:
            login_user(LDAPUser(raw))
            return redirect(url_for('dashboard.dashboard'))
        domain = current_app.config.get('LDAP_DOMAIN')
        server = current_app.config.get('LDAP_SERVER')
        search_base    = current_app.config.get('LDAP_SEARCH_BASE')
        required_group = current_app.config.get('LDAP_GROUP')

        # Ensure LDAP settings are complete
        if not all([domain, server, search_base, required_group]):
            abort(500, description="LDAP configuration is incomplete.")

        # build UPN if user didn’t include domain
        user = raw if '@' in raw else f"{raw}@{domain}"

        srv = Server(server)
        with Connection(srv,
                        user=user,
                        password=pw,
                        authentication=SIMPLE,
                        receive_timeout=5) as conn:
            if not conn.bind():
                flash('Invalid credentials', 'danger')
                return redirect(url_for('auth.login'))

            # fetch groups
            conn.search(
                search_base=search_base,
                search_filter=f'(&(objectClass=user)(sAMAccountName={raw}))',
                attributes=['memberOf']
            )
            groups = conn.entries[0].memberOf.values if conn.entries else []

            # ensure membership
            required_cn = required_group.lower()
            allowed = any(
                dn.split(',',1)[0].split('=',1)[1].lower() == required_cn
                for dn in groups
            )
            if not allowed:
                flash('You are not authorized to view this site.', 'warning')
                return redirect(url_for('auth.login'))

        # success!
        login_user(LDAPUser(raw))
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')
