# NewAPI Model Monitor 🔍

A lightweight Python + Flask + SQLite monitoring dashboard for NewAPI multi-model availability tracking.

![Dashboard](image/README/1778227850325.png)
![Dashboard](image/README/1778228544876.png)

## ✨ Features

- 📡 Auto-discover models from NewAPI `/models` endpoint
- ⏰ Scheduled health checks with configurable time window (default: 8:00-18:00)
- 📊 Multi-timeframe availability: 3m / 30m / 3h / 6h / 12h / 24h
- 📈 Latency & availability trend charts
- 🔎 Model search & filter (online/offline)
- 💾 SQLite persistence with auto-cleanup

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Edit config.yaml with your NewAPI endpoint and API key
cp config.yaml.example config.yaml

# Start services (Linux/macOS)
./start.sh

# Or on Windows
start.bat
```

Visit **http://localhost:5000**

## ⚙️ Configuration

```yaml
newapi:
  endpoint: "http://your-api:3000/v1"
  api_key: "sk-your-key"
  timeout: 60

scheduler:
  interval_minutes: 3
  time_window:
    start_hour: 8
    end_hour: 18

database:
  path: "data/monitor.db"

retention:
  days: 30

web:
  host: "127.0.0.1"
  port: 5000
```

Or use environment variables:
```bash
export NEWAPI_API_KEY="sk-your-key"
export NEWAPI_ENDPOINT="http://your-api:3000/v1"
```

## 🌐 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/models` | All models sorted by availability + latency |
| `GET /api/status` | Real-time status map |
| `GET /api/availability` | Multi-window availability stats |
| `GET /api/history` | Last 24h history |
| `GET /api/models/<name>/availability` | Single model availability |
| `GET /api/models/<name>/history` | Single model history |

## 📁 Project Structure

```
├── monitor/
│   ├── agent.py      # Scheduling & health check
│   ├── adapter.py    # NewAPI client
│   ├── database.py   # SQLite operations
│   └── config.py     # Config loader
├── web/
│   └── app.py        # Flask API server
├── data/
│   └── monitor.db    # SQLite database
├── config.yaml       # Configuration
├── requirements.txt  # Dependencies
└── start.sh / start.bat  # Launch scripts
```

## 🛡️ Security

- ✅ `config.yaml` is gitignored (contains API key)
- ✅ `.gitignore` excludes database, logs, and cache files
- ✅ Environment variable override supported

## 📜 License

MIT License - free for commercial and personal use.
