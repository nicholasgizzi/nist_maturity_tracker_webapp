from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
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
        domain = current_app.config.get('LDAP_DOMAIN')
        server = current_app.config.get('LDAP_SERVER')

        # build UPN if user didn’t include domain
        user = raw if '@' in raw else f"{raw}@{domain}"

        # bind to LDAP
        srv  = Server(server)
        conn = Connection(srv,
                          user=user,
                          password=pw,
                          authentication=SIMPLE,
                          receive_timeout=5)
        if not conn.bind():
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))

        # fetch the memberOf values
        conn.search(
          search_base=current_app.config['LDAP_SEARCH_BASE'],
          search_filter=f'(&(objectClass=user)(sAMAccountName={raw}))',
          attributes=['memberOf']
        )
        groups = conn.entries[0].memberOf.values if conn.entries else []

        # check if any DN’s CN matches your LDAP_GROUP
        required_cn = current_app.config['LDAP_GROUP'].lower()
        allowed = False
        for dn in groups:
            # each dn looks like "CN=prism_webapp,OU=Groups,DC=aamp,DC=com"
            cn_part = dn.split(',', 1)[0]        # "CN=prism_webapp"
            cn_val  = cn_part.split('=', 1)[1]   # "prism_webapp"
            if cn_val.lower() == required_cn:
                allowed = True
                break

        if not allowed:
            flash('You are not authorized to view this site.', 'warning')
            return redirect(url_for('auth.login'))

        # success!
        login_user(LDAPUser(raw))
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')
