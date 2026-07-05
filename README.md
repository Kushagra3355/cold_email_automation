# Modular Email Sender

The original single script, split into clean modules. Each concern lives in its
own folder/file so you can edit content, data, and secrets independently.

## Structure

```
mailer/
├── main.py              # run this:  python main.py
├── sender.py            # sending logic (connect, build, retry)
├── config.py            # SMTP settings, file paths, delays
├── requirements.txt
├── .gitignore
│
├── message/
│   └── content.py       # SUBJECT + BODY templates ({name} merge tags)
│
├── data/
│   ├── recipients.py    # reads the Excel list
│   └── emails.xlsx      # your recipient list (gitignored)
│
└── secret/
    ├── credentials.py   # loads email + app password securely
    ├── .env.example     # copy to .env and fill in
    └── .env             # your real secrets (gitignored, you create this)
```

## What each folder does

- **secret/** — your email and app password. Loaded from environment variables,
  then a `secret/.env` file, then an interactive hidden prompt. Never hardcoded.
- **message/** — just the email content. Edit `SUBJECT` and `BODY`. Use `{name}`
  or any Excel column header as a placeholder.
- **data/** — the recipient list. First row = headers, must include an `email`
  column. Every column becomes a merge field.
- **config.py** — SMTP server/port, attachment paths, delay, retry count.

## Setup

1. `pip install -r requirements.txt`
2. Get a Gmail App Password (2FA on → https://myaccount.google.com/apppasswords).
3. Set your credentials one of three ways:
   - **Env vars:** `export EMAIL_SENDER=you@gmail.com` and
     `export EMAIL_APP_PASSWORD=xxxx`
   - **File:** copy `secret/.env.example` → `secret/.env` and fill it in
   - **Prompt:** just run and type them when asked (password stays hidden)
4. Put your list at `data/emails.xlsx` (first row headers, an `email` column).
5. Edit `message/content.py` for your subject/body.
6. Attachments: add paths to `ATTACHMENTS` in `config.py`.

## Run

```
python main.py
```

It loads credentials, reads recipients, asks for confirmation, then sends with a
per-recipient log and a final sent/failed count. Failed sends retry automatically
(`MAX_RETRIES` in config.py).

## Your Excel format

Your file `HR_Contact_List.xlsx` has these columns:

| SNo | Name         | Email                 | Title                | Company         |
|-----|--------------|-----------------------|----------------------|-----------------|
| 1   | Akanksha Puri| akanksha.puri@...     | Associate Director HR| SourceFuse Tech |

Available merge tags in `message/content.py`: `{name}`, `{title}`, `{company}`.
(`email` is the recipient address; `sno` is ignored.)

## Attaching your resume

1. Put your resume PDF in the `data/` folder, named exactly **resume.pdf**.
2. It's already wired in `config.py`:
   ```python
   ATTACHMENTS = ["data/resume.pdf"]
   ```
3. It attaches to every email automatically. To use a different name or add
   more files, edit that list, e.g.
   `ATTACHMENTS = ["data/MyResume_2026.pdf", "data/portfolio.pdf"]`.

## Security notes
- Real secrets (`secret/.env`) and your Excel (`data/*.xlsx`) are gitignored.
- The password is read with `getpass` (hidden) and never printed or saved.
- For a different provider, change `SMTP_SERVER`/`SMTP_PORT`/`SMTP_MODE` in config.py
  (Outlook: smtp.office365.com / 587 / starttls).

## Sending limits
Gmail free ~500/day, Workspace ~2000/day. Keep the delay on to avoid throttling.
```
