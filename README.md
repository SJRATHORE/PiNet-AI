# PiNet AI v0.1 (Raspberry Pi 3 A+)

Offline knowledge search portal. Runs entirely with Python standard library and SQLite FTS5; it is **not yet a generative AI chatbot**.

## Start

On Raspberry Pi OS Lite (Bookworm/Trixie), from this folder:

```sh
python3 app.py
```

Visit `http://PI_IP:8080` on a device on the same network. Test locally with `curl http://localhost:8080/health`.

Add UTF-8 `.txt` or `.md` files to `knowledge/`, and restart the app to rebuild the index.

## Hotspot

**Warning:** the next command disconnects the Pi from its current Wi-Fi. If your SSH session uses Wi-Fi, you will lose it. Arrange alternate access/recovery first or have a display/keyboard available.

```sh
sudo nmcli device wifi hotspot ifname wlan0 ssid PiNet password 'REPLACE-WITH-A-STRONG-PASSWORD'
ip -4 address show wlan0
```

Connect phone/laptop to `PiNet`, and open `http://PI_HOTSPOT_IP:8080`, usually `http://10.42.0.1:8080`. Read `ip -4 address show wlan0` to confirm; don't assume this address.

Check hotspot: `nmcli connection show --active`.

Restore normal Wi-Fi: `sudo nmcli connection down Hotspot` (connection name may differ; inspect `nmcli connection show`), then `sudo nmcli device wifi connect 'YOUR_HOME_SSID' password 'YOUR_HOME_WIFI_PASSWORD'`.

## Autostart (optional)

Replace `YOUR_USERNAME` with your actual Linux username. Put the project at `/home/YOUR_USERNAME/pinet-ai`.

```ini
[Unit]
Description=PiNet offline knowledge portal
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/pinet-ai
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/pinet-ai/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Save at `/etc/systemd/system/pinet-ai.service` and run:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now pinet-ai
sudo systemctl status pinet-ai
```

Security: only share the hotspot password with trusted users. This starter portal has no login/authentication. Don't put sensitive documents on it or expose port 8080 to the public internet.
