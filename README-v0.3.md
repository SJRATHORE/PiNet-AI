# PiNet AI v0.3 — Knowledge Engine 2.0

This incremental update keeps the standard-library-only offline chatbot and makes document search more efficient for longer documents.

## Changes
- Splits `.md` and `.txt` knowledge documents into passages (normally at most 900 characters).
- Tracks Markdown headings and displays section references such as `guide.md — DNS`.
- Searches passage-sized SQLite FTS5 rows rather than entire documents.
- Rebuilds the SQLite search index on application startup; no database migration needed.
- Adds two tests for long documents and source-section citations.

## Install on Windows
Extract the ZIP into the existing repository root on a *new feature branch*; this replaces `app.py` and adds tests. Run:

```powershell
python -m unittest discover -s tests -v
python app.py
```

Open http://localhost:8080 and try searches against your offline library. The v0.3 footer should appear.

## Deploy to Pi
Back up the currently working app, then transfer `app.py` to the existing deployment directory. Restart with `sudo systemctl restart pinet-ai.service` and check `/health` and the browser interface.

## Limits
This is extractive search, **not an LLM**. Section citations are derived from Markdown headings and are not page numbers. The index is rebuilt at startup and plaintext knowledge is accessible to everyone who can access the portal. Do not put confidential documents on it.
