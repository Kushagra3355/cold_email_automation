"""
main.py
-------
Run this file to send your emails:  python main.py

It wires the modules together:
  secret/     -> your credentials (never hardcoded)
  data/       -> recipient list from Excel
  message/    -> subject + body templates
  config.py   -> SMTP settings, paths, delays
  sender.py   -> the actual sending
"""

import config
from secret import credentials
from data import recipients as recipients_module
import sender


def main():
    print("Loading credentials...")
    sender_email, app_password = credentials.get_credentials()

    print(f"Loading recipients from {config.EXCEL_FILE} ...")
    recipients = recipients_module.load_recipients(config.EXCEL_FILE)
    print(f"  {len(recipients)} recipients loaded.")

    if not recipients:
        print("No recipients to send to. Exiting.")
        return

    confirm = input(f"Send to all {len(recipients)} recipients? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    print("Sending...\n")
    sent, failed = sender.send_all(sender_email, app_password, recipients)

    print(f"\nDone. {sent} sent, {failed} failed.")


if __name__ == "__main__":
    main()
