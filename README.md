# PiNet AI

A lightweight, offline Wi-Fi knowledge portal for Raspberry Pi. Connect to the **PiNet** hotspot and ask questions against locally stored documents, without internet access.

> **Current release: v0.2.** This is an **extractive, source-grounded question-answer system**, not a generative LLM. It returns excerpts from local documents; it does not invent new answers or maintain conversation memory.

## Features

- Standalone Raspberry Pi Wi-Fi hotspot (after configuration)
- Local web-based question-answer interface, accessible from a browser
- Offline `.md` / `.txt` knowledge library indexed with SQLite FTS5
- Health endpoint at `/health`
- Python standard library only; no cloud API required
- Background startup using systemd

## Hardware and requirements

- Tested on Raspberry Pi 3 Model A+ (512 MB RAM) with Raspberry Pi OS Lite
- Python 3 with SQLite FTS5 support
- NetworkManager (`nmcli`) for the optional hotspot configuration
- A microSD card and stable power supply

## Try it on your workstation

```bash
python -m unittest discover -s tests -v
python app.py
```

Open `http://localhost:8080`, or verify `http://localhost:8080/health` returns `OK`.

## Run it on the Pi

Copy this repository to the Pi, then from the repository directory:

```bash
python3 app.py
```

Open `http://<PI_IP>:8080` on a device connected to the same network. To run it on boot, follow [deployment instructions](docs/deployment.md).

## Offline hotspot

To create the independent `PiNet` Wi-Fi network, follow [hotspot setup and recovery](docs/hotspot-setup.md). **Hotspot activation can interrupt SSH over Wi-Fi**. Prepare a physical recovery method first.

The example hotspot uses `10.42.0.1/24`. Once it is active, connect to `PiNet` and open `http://10.42.0.1:8080`.

## Knowledge library

Add UTF-8 `.md` or `.txt` files to `knowledge/`. Restart `pinet-ai.service` (or `app.py`) to rebuild the search index. The current app indexes individual files smaller than 2 MB and searches the indexed text. **All hotspot clients can access the contents returned by the site, so do not add confidential documents.**

## Architecture

See [architecture](docs/architecture.md) for the service diagram and operating limits.

## Security notes

- Use a strong hotspot password, and never commit credentials, private SSH keys, or live NetworkManager profiles.
- The portal has **no user authentication**. Only use it on a trusted local network; do not forward its port to the internet.
- `knowledge.db` is a generated index and should remain ignored by Git.

## Development

```bash
git switch -c feature/my-change
python -m unittest discover -s tests -v
```

Commit tested changes on a feature branch and merge into `main`. Windows can be your development workstation while the Pi is the deployment machine.

## Roadmap

- **v0.1**: Offline knowledge search portal
- **v0.2**: Extractive, source-backed question-answer interface
- **Next**: Better indexing and citations, safer deployment automation, and experiments with tiny local language models

## Documentation

- [System overview](docs/architecture.md)
- [Wi-Fi hotspot setup, testing, and recovery](docs/hotspot-setup.md)
- [Application deployment and troubleshooting](docs/deployment.md)
