# AD / LDAP settings for this local instance only

# LDAP server URL
LDAP_SERVER      = "ldap://<your_ldap_server>"

# AD domain (for NTLM bind)
LDAP_DOMAIN      = "YOURDOMAIN.COM"

# Base DN to search for user objects
LDAP_SEARCH_BASE = "DC=domain,DC=com"

# AD group whose members may log in
LDAP_GROUP       = "webapp_group"
