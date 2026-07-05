"""
config.py
---------
Central settings. Edit these to point at your files and provider.
Nothing sensitive lives here - credentials come from secret/.
"""

# --- SMTP server (pick your provider) ---
# Gmail:   smtp.gmail.com   / 465 / ssl
# Outlook: smtp.office365.com / 587 / starttls
# Yahoo:   smtp.mail.yahoo.com / 465 / ssl
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_MODE = "ssl"          # "ssl" (port 465) or "starttls" (port 587)

# --- Files ---
EXCEL_FILE = "data/HR_Contact_List.xlsx"   # your recipient list

# Files attached to EVERY email. Put your resume in the data/ folder and
# reference it here. The filename recipients see keeps this exact name.
ATTACHMENTS = [
    "data/resume.pdf",
]

# --- Behaviour ---
DELAY_SEC = 2              # pause between emails to avoid rate limits
MAX_RETRIES = 2           # retry a failed send this many times before giving up
