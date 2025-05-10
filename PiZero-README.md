# Shadow Bubble Mini - Setup Instructions for Raspberry Pi Zero 2 W

## Overview

This guide explains how to cleanly install `mdk4`, configure your Wi-Fi adapter region, and ensure the tool runs correctly on devices such as the **Raspberry Pi Zero 2 W**. These steps ensure optimal performance and compatibility with `Shadow Bubble ELITE`.

---

## 🔧 MDK4 Installation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y libpcap-dev libnl-3-dev libnl-genl-3-dev build-essential git
```

### 2. Clone and Build `mdk4`

```bash
cd ~
git clone https://github.com/aircrack-ng/mdk4.git
cd mdk4
make
```

### 3. Move Binary to System PATH

```bash
sudo cp src/mdk4 /usr/local/bin/
```

Ensure `/usr/local/bin` is included in your `$PATH`:

```bash
echo $PATH
```

---

## 🌍 Set Wi-Fi Adapter Regulatory Region

### 1. Temporarily Set to US

```bash
sudo iw reg set US
```

### 2. Persist Region Across Reboots

#### Method A: Using WPA Supplicant (Headless Ubuntu)

Edit the config file:

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add this line if not present:

```
country=US
```

Then reboot:

```bash
sudo reboot
```

#### Method B: Using NetworkManager

```bash
sudo nano /etc/NetworkManager/conf.d/regdom.conf
```

Add:

```
[device]
wifi.scan-rand-mac-address=no

[global]
wifi.country=US
```

Then restart the service:

```bash
sudo systemctl restart NetworkManager
```

---

## ✅ Verification Steps

### 1. Check Current Region

```bash
iw reg get
```

Output should include:

```
country US: DFS-FCC
```

### 2. Check Supported Bands

```bash
iw phy | grep -A5 'Band 1'
```

This will list the capabilities of your adapters.

---

## 🚀 Ready to Run Shadow Bubble ELITE

Once the setup is complete, simply execute:

```bash
sudo python3 Shadow_Bubble_Elite.py
```

The script will auto-detect available adapters, configure them, and start beacon + deauth + Bluetooth jamming based on availability.

---

For help or updates, visit the ShadowTEAM project page.
