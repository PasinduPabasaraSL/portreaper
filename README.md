# PortReaper

**The silent harbinger for processes hogging your ports.**

```bash
portreaper find 3000        # Who’s on 3000?
portreaper kill 3000        # Graceful death
portreaper kill 3000 -9     # No mercy
portreaper scan             # Show open ports
portreaper monitor          # Live dashboard
```
# Install
```
pip install portreaper
```
### Commands

| Command               | Description                          |
|-----------------------|--------------------------------------|
| `find <port>`         | Show which process owns the port     |
| `kill <port>`         | Graceful kill (SIGTERM)              |
| `kill <port> -9`      | Force kill (SIGKILL)                 |
| `scan`                | Scan open ports (default 1–1024)     |
| `scan -p 1-65535`     | Scan all ports                       |
| `monitor`             | Live dashboard of listening ports    |
| `--help`              | Show help                            |
| `--version`           | Show version                         |

# Requirements
* Python 3.8+
* Linux / macOS / WSL
  
