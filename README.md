# PingCheck

A small Python script that checks if your home or web services are up and sends Pushover notifications if they go down or come back up.

Currently monitors:

- Jellyfin
- Jellyseerr
- Unraid
- Home Assistant
- Obsidian Livesync (CouchDB)
- Tdarr
- Pi-hole

It checks every 5 minutes and won't spam you during sleep hours (1 AM – 7 AM).

---

## How it works

- Makes HTTP requests to each service to see if they respond.
- Tracks whether each service was previously up or down to avoid duplicate alerts.
- Sends notifications using Pushover API if a service goes down or comes back up.

Logs are written to `service_monitor.log` and rotated daily, with 7 days kept as default.

---

## Configuration

1. **Clone this repo:**

```bash
git clone https://github.com/yourusername/pingcheck.git
cd pingcheck
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Edit `.env.example` with your parameters and rename to `.env`:**

```ini
COUCHDB_USER=yourcouchdbuser
COUCHDB_PASS=yourcouchdbpassword
COUCHDB_HOST=192.168.x.x
COUCHDB_PORT=5984

PUSHOVER_API_TOKEN=yourpushovertoken
PUSHOVER_USER_KEY=yourpushoveruserkey
```

4. **Edit `pingcheck.py` to add new services or configure quiet hours.**

All user-configurable parameters are defined in the ## USER-DEFINED VARIABLES ## block.

Adding a new service is simple:
1. Create the service URL under ## SERVICE URLS ## section at the top of the script using the provided example
2. Add the service to the services dictionary in the main loop section of the script using the provided example
3. Voila! Your service is now being monitored.

---

## Running

Run directly:

```bash
python pingcheck.py
```

It will keep running, checking every 5 minutes.

---

## How to run it as a daemon on Windows

If you want it to run in the background:

- **Option 1: Use `pythonw.exe`**

  Run it using `pythonw.exe pingcheck.py` to run silently without a console window.

- **Option 2: NSSM (Non-Sucking Service Manager)**

  1. Download [nssm](https://nssm.cc/).
  2. Install the script as a Windows service:

  ```powershell
  nssm install PingCheck
  ```
  - Set **Path** to your `python.exe`.
  - Set **Arguments** to the full path of `pingcheck.py`.
  - Set **Startup directory** to your script’s folder.
  3. Start the service from the Services snap-in or using:

  ```powershell
  nssm start PingCheck
  ```

- **Option 3: Task Scheduler**

  Create a basic task that triggers at startup, runs `python pingcheck.py`, and configure it to run whether you are logged in or not.

---

## License

MIT - do whatever you want, just don’t blame me if it breaks your notifications at 3 AM.

---

## To-Do

- Add Telegram/Discord notifications as optional.
- Configurable sleep hours via `.env`.
- Docker container for easy deployment.

---

If you find it useful, chuck me a star.
