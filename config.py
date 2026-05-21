import os

# --- Active Directory / LDAP Server Settings ---
AD_SERVER = "192.168.1.100"  # Active Directory Domain Controller IP or Hostname
AD_PORT = 636                # 389 for standard/StartTLS, 636 for LDAPS
AD_USE_SSL = True           # Set to True if using LDAPS (Port 636)

# --- Service Account (Bind User) Credentials ---
# This account must have delegated permissions to reset user passwords.
# Format: 'CN=Administrator,CN=Users,DC=lab,DC=local' or 'lab\\Administrator'
AD_BIND_USER = "YOUR_DOMAIN\\Administrator"
AD_BIND_PASSWORD = "Your_Admin_Password_Here"

# --- User Directory Search Settings ---
AD_SEARCH_BASE = "DC=yourdomain,DC=com"  # Search base for your domain

# --- Development / Simulation Mode ---
# Set to True to test the portal interface, OTP flow, and mock password resets 
# without needing an active Active Directory server connection.
DEVELOPMENT_MODE = False

# --- SMTP Email Settings for OTP Sending (Optional) ---
# Set SMTP_ENABLED = True if you want the portal to send real emails to users' accounts
SMTP_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"  # e.g., smtp.gmail.com, smtp.office365.com
SMTP_PORT = 587                  # 587 for TLS, 465 for SSL
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # Use App Passwords for safety (not main password)
SMTP_FROM = "SSPR Portal <your_email@gmail.com>"


