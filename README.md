# AVD Pressure Monitor

> **See exactly how badly your Azure Virtual Desktop hosts are suffering — in real time.**
> A dark, live-updating dashboard that shows CPU, memory, session load, and a composite pressure score for every host in your AVD pool. Because Azure's built-in monitoring is garbage and your users deserve better answers than "it's fine."

---

## Why This Exists

Azure Virtual Desktop gives you fragmented performance data scattered across Log Analytics, Azure Monitor, and the portal. None of it is fast. None of it shows you which host is about to fall over before it does.

This tool surfaces the right signal in one place: a **composite pressure score** (CPU × 40% + memory × 35% + session load × 25%) per host, updated on a cadence you control, with sparkline history so you can see if a host is trending up or has been red for the last ten minutes.

---

## What You See

| Signal | What It Tells You |
|---|---|
| **Pressure ring** | Composite 0–100 score — glanceable, colour-coded, animated |
| **CPU / Memory bars** | Current utilisation with live colour feedback |
| **Session fill bar** | Sessions / max capacity — know when a host is about to stop accepting connections |
| **Sparklines** | Last 20 readings for CPU and memory — trend at a glance |
| **User list** | Who's on each host, their session state, and how long they've been connected |
| **Summary strip** | Pool-wide totals: hosts, sessions, disconnected users, avg pressure, critical/high count |

---

## Pressure Levels

| Level | Score | Colour | Meaning |
|---|---|---|---|
| Healthy | 0–39 | Green | Plenty of headroom |
| Moderate | 40–64 | Amber | Worth watching |
| High | 65–84 | Orange | Users probably feeling it |
| Critical | 85–100 | Red (pulsing) | Intervention required |

---

## Quick Start

```bash
git clone https://github.com/tkhemraj/avd-monitor.git
cd avd-monitor
pip install -e .
uvicorn avd_monitor.main:app --reload --port 8000
```

Open `http://localhost:8000` — you'll see a demo with 8 realistic hosts, ranging from idle to completely maxed out.

---

## Connect to Live Azure Data

```bash
cp .env.example .env
# Edit .env:
DEMO_MODE=false
AZURE_SUBSCRIPTION_ID=your-sub-id
AZURE_RESOURCE_GROUP=your-rg
AZURE_HOST_POOL=your-pool-name
```

Then authenticate:
```bash
az login
# or set AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_TENANT_ID for a service principal
```

The app uses `DefaultAzureCredential` — it picks up `az login`, environment variables, managed identity, or workload identity automatically.

**Required Azure roles:**
- `Desktop Virtualization Reader` on the host pool
- `Monitoring Reader` on the subscription or resource group

---

## Configuration

All settings via environment variables or `.env`:

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `true` | `false` to use live Azure data |
| `REFRESH_INTERVAL_SECONDS` | `30` | Dashboard auto-refresh cadence |
| `AZURE_SUBSCRIPTION_ID` | — | Required for live mode |
| `AZURE_RESOURCE_GROUP` | — | Resource group containing the host pool |
| `AZURE_HOST_POOL` | — | Host pool name |
| `APP_TITLE` | `AVD Pressure Monitor` | Dashboard title |
| `PORT` | `8000` | Server port |

---

## API

The dashboard is backed by a REST API you can query independently:

```
GET /api/overview          Pool-level summary
GET /api/hosts             All hosts with metrics
GET /api/hosts/{name}      Single host detail
GET /api/hosts/{name}/sessions  Sessions on a specific host
GET /api/sessions          All active sessions across the pool
GET /api/status            App config (demo vs live, refresh interval)
```

---

## Architecture

```
src/avd_monitor/
├── main.py              FastAPI app + dashboard route
├── config.py            Settings from env / .env
├── models/
│   └── host.py          SessionHost, UserSession, PoolOverview dataclasses
├── azure/
│   ├── client.py        DefaultAzureCredential + SDK client bundle
│   ├── hosts.py         Live AVD session host + Azure Monitor queries
│   └── demo.py          Realistic demo data (no Azure creds required)
├── routers/
│   └── api.py           REST API endpoints
└── templates/
    └── dashboard.html   Dark glass-morphism dashboard (Chart.js sparklines, SVG rings)
```

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

All tests run in demo mode — no Azure credentials required.

---

## Need Help With Your AVD Environment?

This tool shows you where the pressure is. Fixing it — right-sizing hosts, tuning session limits, setting up autoscale, getting Azure Monitor actually alerting on the right things — is where most teams get stuck.

**Tarique Khemraj** is an Azure infrastructure specialist who's built and managed AVD environments for enterprise clients.

**What I can help with:**
- Deploying this dashboard against your production AVD environment
- Diagnosing chronic high-pressure hosts and identifying root causes
- Right-sizing VM SKUs and session limits for your actual workload
- Setting up Azure Monitor alerts before users start complaining
- AVD autoscale configuration that actually makes sense

📧 **t.khemraj@gmail.com**
🐙 **github.com/tkhemraj**

> If you're running AVD in production and your users keep saying it's slow — let's talk.

---

## License

MIT
