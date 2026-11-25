# PiNet AI architecture

## Purpose

PiNet AI is a lightweight offline knowledge service for devices connected to a Raspberry Pi hotspot. The Raspberry Pi 3 A+ has 512 MB RAM, so the design deliberately uses a small Python HTTP server and SQLite instead of a heavy application stack.

```text
Phone / laptop browser
        |
        | Wi-Fi (PiNet AP, e.g. 10.42.0.1)
        v
Raspberry Pi 3 A+
  NetworkManager hotspot profile (DHCP/DNS sharing)
        |
        v
  Python app.py (ThreadingHTTPServer, port 8080)
        |                 |
        |                 +--> GET /health -> OK
        v
  SQLite FTS5 index (knowledge.db, generated)
        ^
        |
  knowledge/*.md, knowledge/*.txt
```

## Components

- **Wi-Fi**: NetworkManager controls `wlan0`. In the tested setup, `PiNet` is a WPA2-Personal AP on `10.42.0.1/24`; the Pi has one built-in wireless interface, so switching away from home Wi-Fi interrupts that connection.
- **Web**: `app.py` serves the chat-style page on `0.0.0.0:8080` by default and responds to `/health`.
- **Index**: on application startup, Python creates/rebuilds an SQLite FTS5 index from supported files in `knowledge/`.
- **Answers**: the application selects source sentences relevant to question keywords and displays source filenames. No LLM runs in v0.2.
- **Service**: systemd starts/restarts the Python process when the Pi boots (see `docs/deployment.md`).

## Request flow

1. A client associates with `PiNet` and obtains an address.
2. The client opens `http://10.42.0.1:8080`.
3. The browser sends a question to `/chat?q=...`.
4. The server searches indexed documents and extracts relevant sentences.
5. The response includes source filenames, or reports that no supported answer was found.

## Constraints and security

- 512 MB RAM rules out treating a modern, large LLM as a standard dependency.
- There is no login or per-user access control: everyone with hotspot access can query the knowledge library.
- HTTP is unencrypted on the local network. Do not use the site for secrets.
- Generated databases, logs, passwords, and keys belong outside Git.
- The Wi-Fi hotspot alone does not provide internet access. Internet sharing requires a separate uplink and additional configuration.

## Tested setup (example, not portable defaults)

- Hostname: `RathorePi.local`; Linux username: `sudh`
- Application directory: `/home/sudh/PiNet-AI-starter/pinet-ai`
- Hotspot profile: `PiNet`; home network profile: `netplan-wlan0-RATHORE`
- Access: `http://10.42.0.1:8080`

Replace these instance-specific names and paths on other installations.
