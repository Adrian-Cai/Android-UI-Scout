# Android-UI-Scout

Android-UI-Scout is a lightweight local visual element picker for Android UI automation. Connect an Android device over USB with ADB debugging enabled, start one local command, and inspect screenshots, UI hierarchy nodes, element properties, and generated uiautomator2 locators/click snippets in a browser.

## Features

- Local FastAPI backend bound to `127.0.0.1` by default.
- ADB discovery with statuses for `device`, `unauthorized`, and `offline`.
- uiautomator2 integration for screenshots, hierarchy XML, taps, text input, and Back.
- Vue 3 + Vite three-column UI:
  - left: parsed element tree;
  - center: live phone screenshot with bounds highlight;
  - right: element details and copyable code snippets.
- Coordinate-to-bounds matching with smallest-area preference.
- Locator generation for `resource-id`, `content-desc`, `text`, XPath, and coordinate clicks.

## Requirements

- Python 3.10+
- Node.js 18+ and npm
- Android Platform Tools (`adb` in `PATH`)
- Android phone with USB debugging enabled

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

## Start

```bash
python -m cli.main start
```

Options:

```bash
python -m cli.main start --port 8787 --frontend-port 5173 --serial <adb-serial>
```

Backend health endpoint:

```bash
curl http://127.0.0.1:8787/api/health
```

Frontend:

```text
http://127.0.0.1:5173
```

## ADB connection notes

1. Enable Developer Options on the Android device.
2. Enable USB debugging.
3. Connect with USB.
4. Run `adb devices`.
5. If prompted on the phone, approve the USB debugging authorization dialog.

If multiple ready devices are attached and `--serial` is not provided, Android-UI-Scout selects the first `device` entry from `adb devices`.

## Common issues

### `adb` not found

Install Android Platform Tools and ensure `adb` is available in `PATH`:

```bash
adb version
```

### Phone is `unauthorized`

Unlock the phone and confirm the USB debugging authorization prompt. If the prompt does not appear, unplug/replug USB or run:

```bash
adb kill-server
adb start-server
adb devices
```

### Device is `offline`

Reconnect USB, toggle USB debugging, or restart the ADB server. Avoid using unstable cables or hubs.

### Screenshot capture failed

Confirm the device is unlocked and reachable by uiautomator2. Reinstall/init uiautomator2 dependencies if needed:

```bash
python -m uiautomator2 init
```

### Page has no element tree

Refresh the page snapshot. Some secure or special system surfaces may expose limited hierarchy data. Confirm `dump_hierarchy()` works through uiautomator2.

## Security

- Backend services listen only on `127.0.0.1` by default.
- Screenshots, XML hierarchy, and device information remain local and are not uploaded to public networks.
- The API does not expose arbitrary command execution or arbitrary ADB command execution.
- Backend subprocess usage avoids `shell=True`.
- The frontend does not load third-party CDN scripts.
- `vendor_review/` is reserved for temporary review of code copied from other projects before any migration.
- `docs/source-import-log.md` records source origins, migrated content, removals, and modifications.

## Development

Backend:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

Frontend:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
