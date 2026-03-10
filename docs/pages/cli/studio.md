## What is it?
A web-based translation editor that runs locally.
It lets you browse, edit, and save translations in real time from the browser. Multiple users can work simultaneously — edits are synced via WebSocket.

Studio requires extra dependencies:
```bash
pip install doti18n[studio]
```

## Example
Imagine you have this structure:

```text
project_root/  
├── locales/  
│   ├── en.yaml
│   └── fr.yaml
└── main.py  
```

`en.yaml`:
```yaml
greeting: "Hello, World!"
menu:
  save: "Save"
  open: "Open"
```

`fr.yaml`:
```yaml
greeting: "Bonjour le monde!"
menu:
  save: "Sauvegarder"
  open: "Ouvrir"
```

First, create a user:
```bash
doti18n studio add-user admin mypassword
```

Then start the server:
```bash
doti18n studio run locales/
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), log in, and you'll see all your locales and keys ready to edit.

### What happens under the hood

*Key Locking:*
When you click a key to edit it, the server locks it for you. Other users see it's taken and can't overwrite your work.

---
*Live Updates:*
When someone saves a change, every other connected client gets the update instantly — no refresh needed.

---
*Auto-Save:*
The server doesn't write to disk on every keystroke. It waits 2 seconds of inactivity before flushing changes. On shutdown (`Ctrl+C` / `SIGTERM`), all pending edits are saved automatically.

---
*Authentication:*
All routes are protected. Sessions live in memory with a 1-hour TTL by default, so users will need to log back in after a server restart.

!!! note
    User credentials are stored in `studio_users.json` in the current directory. Passwords are hashed (PBKDF2), never stored in plain text.

## Options

**Add users:**
Create as many accounts as you need. Re-adding an existing username overwrites the old password.
```bash
doti18n studio add-user translator1 p@ssw0rd
```

**Set the default locale:**
Change which locale is treated as the source of truth (default is `en`).
```bash
doti18n studio run locales/ --locale fr
```

**Change host and port:**
By default it binds to `127.0.0.1:5000`.
```bash
doti18n studio run locales/ --host 0.0.0.0 --port 8080
```

!!! warning
    Binding to `0.0.0.0` exposes the studio to your network. Use a reverse proxy with HTTPS if you're not on localhost.

**Session lifetime:**
Override the default 1-hour TTL with an environment variable.
```bash
export DOTI18N_SESSION_TTL=7200
```

**Auth file location:**
By default it's `studio_users.json` in the working directory. Override it if needed.
```bash
export DOTI18N_AUTH_FILE=/path/to/users.json
```

