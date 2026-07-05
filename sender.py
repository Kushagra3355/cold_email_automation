"""
sender.py
---------
Sending logic. Pulls content from message/, recipients from data/,
credentials from secret/, and settings from config.
"""

import ssl
import time
import smtplib
from pathlib import Path
from email.message import EmailMessage

import config
from message import content


def build_message(sender, row):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = row["email"]
    msg["Subject"] = content.build_subject(row)
    msg.set_content(content.build_body(row))

    for f in config.ATTACHMENTS:
        p = Path(f)
        if p.exists():
            msg.add_attachment(
                p.read_bytes(),
                maintype="application",
                subtype="octet-stream",
                filename=p.name,
            )
        else:
            print(f"  ! attachment not found, skipping: {f}")
    return msg


def _connect(sender, password):
    context = ssl.create_default_context()
    if config.SMTP_MODE == "ssl":
        server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT,
                                  context=context, timeout=30)
    else:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
        server.starttls(context=context)
    server.login(sender, password)
    return server


def send_all(sender, password, recipients):
    sent = failed = 0
    context_server = _connect(sender, password)
    with context_server as server:
        for row in recipients:
            email = row["email"]
            for attempt in range(1, config.MAX_RETRIES + 2):
                try:
                    server.send_message(build_message(sender, row))
                    print(f"Sent to {email}")
                    sent += 1
                    break
                except Exception as e:
                    if attempt <= config.MAX_RETRIES:
                        print(f"  retry {attempt} for {email}: {e}")
                        time.sleep(1)
                    else:
                        print(f"FAILED {email}: {e}")
                        failed += 1
            time.sleep(config.DELAY_SEC)
    return sent, failed
