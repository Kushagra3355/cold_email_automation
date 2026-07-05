"""
data/recipients.py
------------------
Reads the recipient list from an Excel file.

The first row must be headers and must include an 'email' column.
Every column becomes a merge field usable in message templates,
so a header 'name' -> {name}, 'company' -> {company}, etc.

Returns a list of dicts, one per recipient:
    [{"email": "a@x.com", "name": "Alice"}, ...]
"""

from pathlib import Path
import openpyxl


def load_recipients(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)

    # Read header row
    try:
        raw_headers = next(rows)
    except StopIteration:
        wb.close()
        raise ValueError("Excel file is empty.")

    headers = [str(h).strip().lower() if h is not None else "" for h in raw_headers]
    if "email" not in headers:
        wb.close()
        raise ValueError("No 'email' column found in the first row of the Excel file.")

    email_idx = headers.index("email")
    recipients = []

    for r in rows:
        if r is None:
            continue
        email_val = r[email_idx] if email_idx < len(r) else None
        if not email_val:
            continue  # skip rows with no email
        row = {}
        for i, header in enumerate(headers):
            if header:  # ignore unnamed columns
                row[header] = "" if i >= len(r) or r[i] is None else str(r[i])
        recipients.append(row)

    wb.close()
    return recipients
