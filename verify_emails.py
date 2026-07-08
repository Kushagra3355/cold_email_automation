import pandas as pd
import smtplib
import socket
import dns.resolver
import time

INPUT_FILE  = "Untitled spreadsheet.csv"          # your input CSV
OUTPUT_FILE = "emails_checked.csv"   # CSV output
DELAY = 1                            # seconds between checks

def get_mx(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return str(sorted(records, key=lambda r: r.preference)[0].exchange)
    except Exception:
        return None

def smtp_check(email, mx_host):
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_host)
        server.helo(socket.gethostname())
        server.mail('')            # empty sender
        code, _ = server.rcpt(email)
        server.quit()
        return code                # 250 = accepted, 550 = no such user
    except Exception:
        return None

def verify(email):
    email = str(email).strip()
    if '@' not in email:
        return None, "not exist"
    domain = email.split('@')[1]

    mx = get_mx(domain)
    if not mx:
        return None, "not exist"

    code = smtp_check(email, mx)
    if code == 250:
        return mx, "exist"
    if code == 550:
        return mx, "not exist"
    return mx, "unknown"

# --- main ---
df = pd.read_csv(INPUT_FILE)

mx_list, status_list = [], []
for email in df["Email"]:
    mx, status = verify(email)
    mx_list.append(mx)
    status_list.append(status)
    print(f"{email:40} -> {status}")
    time.sleep(DELAY)

df["MX"] = mx_list
df["Status"] = status_list
df.to_csv(OUTPUT_FILE, index=False)

print("\n", df["Status"].value_counts())