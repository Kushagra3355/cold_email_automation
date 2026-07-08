"""
data/recipients.py
------------------
Reads the recipient list from a CSV file.

The first row must be headers and must include an 'email' column.
Every column becomes a merge field usable in message templates,
so a header 'name' -> {name}, 'company' -> {company}, etc.

Returns a list of dicts, one per recipient:
    [{"email": "a@x.com", "name": "Alice"}, ...]
"""

import csv
from pathlib import Path


def load_recipients(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    recipients = []

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = [str(h).strip().lower() if h is not None else "" for h in (reader.fieldnames or [])]

        if not headers:
            raise ValueError("CSV file is empty.")

        if "email" not in headers:
            raise ValueError("No 'email' column found in the first row of the CSV file.")

        for raw_row in reader:
            row = {}
            for key, value in raw_row.items():
                header = str(key).strip().lower() if key is not None else ""
                if header:
                    row[header] = "" if value is None else str(value)
            if not row.get("email"):
                continue  # skip rows with no email
            recipients.append(row)

    return recipients
