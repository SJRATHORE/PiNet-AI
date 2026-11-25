# Configure the standalone PiNet hotspot

> **Risk warning:** Activating a hotspot on the Pi's single Wi-Fi interface usually disconnects its existing Wi-Fi client connection and SSH session. Have physical console access (monitor/keyboard) or another proven recovery method. Do not rely on a timer as your only recovery strategy.

These commands use NetworkManager (`nmcli`) and assume the wireless interface is `wlan0`. Use `nmcli device status` to check your interface name first.

## 1. Inspect existing connectivity

```bash
nmcli --version
nmcli device status
nmcli -f NAME,TYPE,DEVICE,AUTOCONNECT connection show
iw list | grep -A 12 'Supported interface modes'
```

Check for `AP` under supported modes. Record the current home-Wi-Fi profile name; in the original project it was `netplan-wlan0-RATHORE`, but other installations will differ.

## 2. Create profile (without activating)

```bash
sudo nmcli connection add type wifi ifname wlan0 con-name PiNet autoconnect no ssid PiNet
sudo nmcli connection modify PiNet \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  802-11-wireless-security.key-mgmt wpa-psk \
  ipv4.method shared \
  ipv4.addresses 10.42.0.1/24 \
  ipv6.method disabled
```

The `shared` IPv4 method provides client address allocation and local network sharing facilities. It does **not** conjure an internet connection; an uplink is needed for internet access.

## 3. Set a password without saving it in shell history

```bash
read -rsp 'Enter PiNet Wi-Fi password: ' PINET_PSK
echo
sudo nmcli connection modify PiNet wifi-sec.psk "$PINET_PSK"
unset PINET_PSK
```

Use a strong passphrase (8–63 characters for WPA-PSK). Do not paste it into documentation or Git. Note that NetworkManager stores this secret in the machine's protected connection profile.

## 4. Validate before switching

```bash
nmcli -g 802-11-wireless.mode,ipv4.method,ipv4.addresses connection show PiNet
nmcli -g 802-11-wireless-security.key-mgmt connection show PiNet
nmcli device status
```

Expected settings: `ap`, `shared`, `10.42.0.1/24`, `wpa-psk`. Home Wi-Fi should still be active.

## 5. Optional timed rollback during a controlled trial

Replace `HOME_PROFILE` with the actual existing profile name. A transient timer makes a **best-effort** attempt to restore home Wi-Fi after ten minutes; it is NOT a guaranteed recovery method.

```bash
sudo systemd-run --unit=pinet-rollback --on-active=10m \
  /usr/bin/nmcli connection up 'HOME_PROFILE'
systemctl list-timers --all pinet-rollback.timer
```

If timer creation fails, do not continue. A newly scheduled timer may use a different unit name if an existing unit conflicts; inspect it first.

## 6. Activate and test

```bash
sudo nmcli connection up PiNet
```

SSH through home Wi-Fi will likely disconnect. Connect your laptop or phone to `PiNet`, stay connected if the device warns that the network has no internet, then try:

- `http://10.42.0.1:8080`
- `ping 10.42.0.1`
- `ssh YOUR_PI_USER@10.42.0.1`

If SSH over PiNet works and you want to remain on the hotspot, cancel the trial rollback timer from that SSH session:

```bash
sudo systemctl stop pinet-rollback.timer
nmcli connection show --active
```

## 7. Prefer PiNet on boot (only after testing and arranging physical recovery)

```bash
sudo nmcli connection modify PiNet connection.autoconnect yes connection.autoconnect-priority 100
sudo nmcli connection modify 'HOME_PROFILE' connection.autoconnect-priority 0
nmcli -f NAME,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show
```

NetworkManager autoconnect priority makes the hotspot preferred among eligible profiles, but does not guarantee it will always be chosen. Reboot only with a recovery method ready; then confirm `PiNet` broadcasts and the site plus SSH work. The transient rollback timer does not protect a reboot.

## Switch to home Wi-Fi deliberately

When logged into the Pi over the hotspot, this command will disconnect your session:

```bash
sudo nmcli connection up 'HOME_PROFILE'
```

Reconnect from a device on the home network using the Pi's hostname or DHCP-assigned address. To revert hotspot-first boot behavior, from a working connection:

```bash
sudo nmcli connection modify PiNet connection.autoconnect no
```

If neither network works, use physical console access and inspect `nmcli device status`, `nmcli connection show`, and `journalctl -u NetworkManager -n 80 --no-pager`.

## Security

Do not commit `/etc/NetworkManager/system-connections/`, Netplan Wi-Fi secrets, saved connection exports, or the PiNet password. This document intentionally includes only commands and placeholders.

## Reference

- [NetworkManager nmcli manual](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html)
