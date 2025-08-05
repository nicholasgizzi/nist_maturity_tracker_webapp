# app/services/ldap_auth.py
from ldap3 import Server, Connection, SIMPLE
from flask import current_app

class LDAPAuthError(Exception): pass
class LDAPAuth:
    @staticmethod
    def authenticate(username, password):
        cfg   = current_app.config
        user_dn = username if "@" in username else f"{username}@{cfg['LDAP_DOMAIN']}"
        srv     = Server(cfg['LDAP_SERVER'])
        with Connection(srv, user=user_dn, password=password,
                        authentication=SIMPLE, receive_timeout=5) as conn:
            if not conn.bind():
                raise LDAPAuthError("Invalid credentials")
            conn.search(
              search_base  = cfg["LDAP_SEARCH_BASE"],
              search_filter= f"(&(objectClass=user)(sAMAccountName={username}))",
              attributes   = ["memberOf"]
            )
            groups = (conn.entries and conn.entries[0].memberOf.values) or []
            if not any(
                dn.lower().startswith(f"cn={cfg['LDAP_GROUP'].lower()},")
                for dn in groups
            ):
                raise LDAPAuthError("User is not in required group.")
        return True