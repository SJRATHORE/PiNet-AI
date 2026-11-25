# Application deployment and operations

This guide documents the **tested example installation** and explains how to adapt it. Do not blindly copy the example username/path onto another Raspberry Pi.

## 1. Copy the code

The original installation used:

- Pi username: `sudh`
- Pi hostname: `RathorePi.local` (home Wi-Fi) or hotspot IP `10.42.0.1`
- Repository directory: `/home/sudh/PiNet-AI-starter/pinet-ai`

From a Windows PowerShell terminal in the local repository directory, with Windows connected to the appropriate network:

```powershell
scp app.py sudh@10.42.0.1:~/PiNet-AI-starter/pinet-ai/app.py
```

For initial installation, copy/clone the entire repository instead of only `app.py`. Do not overwrite a working deployment before running local tests and making a backup.

## 2. Run and test manually

On the Pi, from the repository root:

```bash
python3 app.py
```

Open `http://10.42.0.1:8080` while connected to the hotspot. Use `Ctrl+C` to stop the manually run process before starting the service. The application rebuilds its document index on startup.

## 3. Configure systemd

A systemd unit is stored at `deploy/pinet-ai.service`. **Its current username and paths reflect the original device**, and must be edited for other installs.

```bash
sudo cp deploy/pinet-ai.service /etc/systemd/system/pinet-ai.service
sudo systemctl daemon-reload
sudo systemctl enable --now pinet-ai.service
systemctl status pinet-ai.service --no-pager
```

**Before `enable --now`:** inspect the copied file and update `User=`, `WorkingDirectory=`, and `ExecStart=` to match the actual installation. Ensure `app.py` exists and is readable by the service account.

The tested service includes `Restart=on-failure`, which restarts after a crash (not every planned stop).

## 4. Verify the running server

```bash
systemctl is-enabled pinet-ai.service
systemctl is-active pinet-ai.service
curl -i http://127.0.0.1:8080/health
sudo ss -ltnp | grep ':8080'
```

Expected: `enabled`, `active`, HTTP `200 OK` body `OK`, and a Python process listening on port 8080.

`systemctl is-active` can report `active` a moment before the app starts listening. If `curl` briefly fails after restart, retry after a few seconds and check logs.

## 5. Logs and recovery

```bash
sudo journalctl -u pinet-ai.service -n 50 --no-pager
sudo systemctl restart pinet-ai.service
sudo systemctl stop pinet-ai.service
```

For a safe local rollback after a bad deployment, copy back your known-good `app.py`, then restart the service. A separate Git commit and branch history also provide previous source versions.

## 6. Editing the knowledge library

Place UTF-8 `.md` or `.txt` documents in `knowledge/`, then restart the service to refresh the generated SQLite index:

```bash
sudo systemctl restart pinet-ai.service
```

Do not commit generated `knowledge.db`, logs, passwords, private keys, or any private documents. Everyone on the PiNet hotspot can access the portal, and the current web app has no authentication.

## 7. Shutdown and startup

Shut down cleanly:

```bash
sudo shutdown -h now
```

Wait for shutdown/storage activity to finish before removing power. Restoring power starts Raspberry Pi OS, the preferred network profile, and the enabled PiNet AI service.

## 8. Development and GitHub workflow

Develop on Windows in a feature branch, run tests, commit and push to GitHub, and then deploy/test on the Pi. Keep a known-good deployment before copying new versions. A Git push does **not** automatically update the Pi; copying code and restarting the service remain separate actions.
