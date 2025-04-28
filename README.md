# Shadow Bubble ELITE

**Tactical Wi-Fi & Bluetooth Disruption Script**  
Built for real-world pentesting, defense, and tactical signal control.

---

## 🚀 Features
- Parallel Beacon Flood + Deauthentication Flood (separate processes)
- Sequential Channel Hopping (channels 1-13 cycling)
- Full Bluetooth Inquiry Jamming
- SSH Connection Protection (does not kill your own management link)
- Real-time Split Terminal Display (Logs + System Stats)
- Adapter Restoration (return to managed mode after shutdown)
- Proper PID-tracked Process Management (no blind `killall`)
- CPU and RAM Monitoring
- RAM-Optimized, No File Write Beacon Injection

---

## 📍 Use Cases

### Physical Pentesting

Shadow Bubble ELITE is designed for scenarios where temporarily disrupting Wi-Fi and Bluetooth communications is essential to achieving physical access objectives. By flooding nearby wireless networks with randomized SSID beacons and deauthentication packets, it can destabilize and interrupt wireless connections to access points, IoT devices, and employee workstations. This can create windows of opportunity for further actions, such as cloning badges or accessing internal wired infrastructure.

Although not specifically tested against surveillance cameras, in theory, by destabilizing Wi-Fi connections, Shadow Bubble ELITE could potentially disrupt Wi-Fi-connected cameras and other wireless security systems. While it does not block signals in the same way a full Faraday cage would, it acts as a mobile RF disruption tool capable of overwhelming local wireless environments, offering strategic advantages in rapid entry scenarios. Real-world effectiveness will depend on environmental factors such as distance, obstacles, and the resilience of the target wireless systems.

### Red Team Operations

In covert engagements, preventing external alerts or detection through wireless channels is critical. Shadow Bubble ELITE allows operators to create an active disruption zone where Bluetooth devices and Wi-Fi-connected infrastructure are severely impaired. This minimizes the risk of real-time notifications, camera feed uploads, or sensor alerts being successfully transmitted outside the compromised environment. All observations have been verified in controlled lab simulations, and operational use should be tailored carefully to match the technical landscape and rules of engagement.

---
## Tested

This was tested one a Raspberry Pi 4B 8GB in a Home Lab enviornment using Kali linux purple

---
## ⚙️ Requirements

### Python Packages
Install Python packages:
```bash
pip3 install -r requirements.txt
```

Contents of `requirements.txt`:
```
psutil
```

---

### System Packages
Install required system tools:
```bash
sudo apt install aircrack-ng mdk4 bluez python3-pip
```

> **Note:**  
> - `aircrack-ng` for monitor mode (`airmon-ng`)  
> - `mdk4` for Wi-Fi beacon and deauth attacks  
> - `bluez` for Bluetooth jamming (`hciconfig`, `btmgmt`, `hcitool`)  
> - `python3-pip` to install `psutil`

---

## 📂 How To Run

1. Clone or copy the project to your machine.
2. Ensure your Wi-Fi and Bluetooth adapters are connected.
3. Start the script:
```bash
sudo python3 Shadow_Bubble_Elite.py
```

4. Use the arrow keys and spacebar to **select** Wi-Fi and Bluetooth adapters.
5. Press **Enter** after selecting your adapters.
6. Watch the terminal split into:
    - **Left side:** Activity logs
    - **Right side:** System CPU/RAM stats

---

## 🔝 How To Stop

Simply press **Ctrl+C**  
The script will:
- Stop all jamming processes
- Restore Wi-Fi adapters to **managed mode**
- Safely shutdown without damaging anything

---

## 📋 Notes
- Always run as **root** or with **sudo** to access wireless hardware.
- Only use in environments where you have permission.
- Make sure your adapters support **monitor mode** for Wi-Fi jamming.

---

# 🛡️ MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**Disclaimer**: The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

# 🛡️ Disclaimer

ShadowDrums and ShadowTEAM members will not be held liable for any misuse of this source code, program, or software. It is the responsibility of the user to ensure that their use of this software complies with all applicable laws and regulations. By using this software, you agree to indemnify and hold harmless Shadowdrums and ShadowTEAM members from any claims, damages, or liabilities arising from your use or misuse of the software.

---

## 🤝 Credits
- Built with love for real operators. Stay sharp. 🛡️
- Shadowdrums

