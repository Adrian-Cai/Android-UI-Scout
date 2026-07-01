from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser

from backend.adb_manager import check_adb_available, list_adb_devices, validate_serial
from backend.security_guard import validate_host, validate_port


def _start_frontend(port: int) -> subprocess.Popen | None:
    if not __import__("shutil").which("npm"):
        print("npm not found; start frontend manually after installing Node.js")
        return None
    return subprocess.Popen(["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(port)], cwd="frontend")


def start(args: argparse.Namespace) -> int:
    port = validate_port(args.port); frontend_port = validate_port(args.frontend_port); validate_host("127.0.0.1")
    if args.serial:
        validate_serial(args.serial)
    if not check_adb_available():
        print("adb not found. Install Android Platform Tools and add adb to PATH.", file=sys.stderr); return 1
    devices = list_adb_devices()
    if not devices:
        print("No devices found. Connect Android phone and enable USB debugging.", file=sys.stderr); return 1
    if any(d["status"] == "unauthorized" for d in devices):
        print("Some devices are unauthorized. Confirm USB debugging authorization on the phone.")
    if any(d["status"] == "offline" for d in devices):
        print("Some devices are offline. Reconnect USB or restart adb server.")
    ready = [d for d in devices if d["status"] == "device"]
    if not ready:
        print("No ready device found.", file=sys.stderr); return 1
    serial = args.serial or ready[0]["serial"]
    print(f"Using device: {serial}")
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(port)])
    frontend = _start_frontend(frontend_port)
    url = f"http://127.0.0.1:{frontend_port}"
    time.sleep(1.5); webbrowser.open(url)
    print(f"Backend: http://127.0.0.1:{port}")
    print(f"Frontend: {url}")
    try:
        backend.wait()
    except KeyboardInterrupt:
        backend.terminate()
        if frontend: frontend.terminate()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="android-ui-scout")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("start")
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--serial")
    p.add_argument("--frontend-port", type=int, default=5173)
    args = parser.parse_args(argv)
    return start(args) if args.command == "start" else 1

if __name__ == "__main__":
    raise SystemExit(main())
