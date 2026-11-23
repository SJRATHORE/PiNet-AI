# PiNet AI v0.2 — offline assistant upgrade

This patch adds a chat-style question interface and **extractive** source-backed replies. It does not provide multi-turn memory or run a generative AI/LLM. It requires only Python's standard library and SQLite FTS5.

## Local test

```sh
python -m unittest discover -s tests -v
python app.py
```

Then open `http://localhost:8080/chat?q=What+is+DNS%3F`.

## Raspberry Pi deployment

First take a backup of `app.py`. Copy the updated `app.py` and `tests/` to your existing installation, then restart the service:

```sh
sudo systemctl restart pinet-ai.service
systemctl is-active pinet-ai.service
curl -fsS http://127.0.0.1:8080/health
```

On PiNet, open `http://10.42.0.1:8080`.

New `.txt` or `.md` files placed in `knowledge/` are indexed after restarting the service. Do **not** place private information in a shared hotspot portal.
