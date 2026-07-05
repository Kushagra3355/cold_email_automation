import smtplib, ssl, time
from email.message import EmailMessage
from pathlib import Path
import openpyxl

# --- CONFIG ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 465
SENDER      = "you@gmail.com"
APP_PASSWORD = "your16charapppassword"   # keep this secret
SUBJECT     = "Hello {name}"
BODY = """Hi {name},

This is my message.

Regards,
Me"""
ATTACHMENTS = []   # paths; leave [] for none
EXCEL_FILE  = "emails.xlsx"
DELAY_SEC   = 2   # pause between sends to avoid rate limits
# --------------

def load_recipients(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = ws.iter_rows(min_row=2, values_only=True)  # skip header
    return [(r[0], r[1] if len(r) > 1 and r[1] else "") for r in rows if r[0]]

def build_message(to_email, name):
    msg = EmailMessage()
    msg["From"] = SENDER
    msg["To"] = to_email
    msg["Subject"] = SUBJECT.format(name=name)
    msg.set_content(BODY.format(name=name))
    for f in ATTACHMENTS:
        p = Path(f)
        if p.exists():
            msg.add_attachment(p.read_bytes(),
                               maintype="application",
                               subtype="octet-stream",
                               filename=p.name)
    return msg

def main():
    recipients = load_recipients(EXCEL_FILE)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER, APP_PASSWORD)
        for email, name in recipients:
            try:
                server.send_message(build_message(email, name))
                print(f"Sent to {email}")
            except Exception as e:
                print(f"FAILED {email}: {e}")
            time.sleep(DELAY_SEC)

if __name__ == "__main__":
    main()