# AVD Pressure Monitor

> **Azure's built-in tools don't tell you a host is about to fall over — they tell you it already did.**
> A real-time dashboard that shows exactly how stressed every session host in your AVD pool is, before your users start filing tickets.

---

## Why This Exists

If you run Azure Virtual Desktop at any real scale, you already know the problem. Azure Monitor shows you CPU. Log Analytics shows you something different. The host pool blade shows you session counts. None of it is in the same place, none of it refreshes fast enough, and none of it tells you the thing you actually need to know: **which hosts are in trouble right now, and how bad is it?**

The result: you find out a host is saturated when a user calls saying their session is freezing. By then it's too late.

This tool gives you a single dashboard — dark, fast, auto-refreshing — that shows a composite pressure score per host, with trend history, session load, and who's on each box. You can see at a glance which hosts are healthy, which are trending bad, and which ones are on fire.

---

## What You See

| Signal | What It Tells You |
|---|---|
| **Pressure score** | Composite 0–100: CPU × 40% + memory × 35% + session load × 25%. One number that summarises host health |
| **Colour-coded ring** | Green / amber / orange / pulsing red — critical hosts announce themselves |
| **CPU + memory bars** | Current utilisation, colour-coded by severity |
| **Session fill bar** | Sessions vs. max capacity — know when a host stops accepting new connections |
| **Sparklines** | Last 20 readings for CPU and memory — is this host trending up or has it been red for 10 minutes? |
| **User list** | Who's on each host, session state, how long they've been connected, disconnected sessions flagged |
| **Pool summary strip** | Total hosts, active sessions, disconnected count, avg CPU/memory/pressure, critical + high alert count |

---

## Pressure Levels

| Level | Score | Colour | What It Means |
|---|---|---|---|
| Healthy | 0–39 | Green | Plenty of headroom |
| Moderate | 40–64 | Amber | Worth watching |
| High | 65–84 | Orange | Users are likely feeling it |
| Critical | 85–100 | Red (pulsing) | Intervention required |

The pressure score is a weighted composite — not just CPU, not just sessions. A host with 50% CPU, 90% memory, and 15/16 sessions is more dangerous than one with 80% CPU and three users. This tool captures that.

---

## Why Not Just Use Azure Monitor?

You can. Here's what that looks like in practice:

| | Azure Monitor / Portal | This Tool |
|---|---|---|
| **Time to see all host pressure** | 3–5 minutes across multiple blades | 2 seconds |
| **Composite pressure signal** | No — you build it yourself in KQL | Built in |
| **Trend history on the same screen** | No | Yes |
| **Who's on each host** | Separate query | On the same card |
| **Auto-refreshes** | Portal doesn't | Yes, configurable |
| **Runs without an Azure portal login** | No | Yes (service principal or managed identity) |
| **Demo / offline mode for testing** | No | Yes — 8 realistic hosts out of the box |

This isn't a replacement for Azure Monitor alerts. It's what you run when you're on a call and someone says "AVD is slow" and you need to know which host is the problem in under 5 seconds.

---

## Quick Start (Demo Mode — No Azure Required)

```bash
git clone https://github.com/tkhemraj/avd-monitor.git
cd avd-monitor
pip install -e .
uvicorn avd_monitor.main:app --reload --port 8000
```

Open `http://localhost:8000`.

You'll see 8 realistic demo hosts — idle, moderate, overloaded, and one fully unavailable — so you can see exactly what the dashboard looks like under real load before you point it at production.

---

## Connect to Live Azure Data

```bash
cp .env.example .env
```

Edit `.env`:
```
DEMO_MODE=false
AZURE_SUBSCRIPTION_ID=your-sub-id
AZURE_RESOURCE_GROUP=your-rg
AZURE_HOST_POOL=your-pool-name
```

Then authenticate:
```bash
az login
```

Or use a service principal:
```
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
```

The app uses `DefaultAzureCredential` — it picks up `az login`, environment variables, managed identity, or workload identity automatically. No code changes needed between local dev and production.

**Required Azure RBAC:**
- `Desktop Virtualization Reader` on the host pool
- `Monitoring Reader` on the subscription or resource group

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `true` | Set to `false` to query live Azure data |
| `REFRESH_INTERVAL_SECONDS` | `30` | How often the dashboard polls for new data |
| `AZURE_SUBSCRIPTION_ID` | — | Required for live mode |
| `AZURE_RESOURCE_GROUP` | — | Resource group containing the host pool |
| `AZURE_HOST_POOL` | — | Host pool name |
| `APP_TITLE` | `AVD Pressure Monitor` | Dashboard title |
| `PORT` | `8000` | Server port |

---

## API

Every metric the dashboard shows is also available as JSON — useful for feeding into alerting systems or building your own tooling on top.

```
GET /api/overview          Pool-level summary (avg pressure, critical count, etc.)
GET /api/hosts             All hosts with full metrics
GET /api/hosts/{name}      Single host detail
GET /api/hosts/{name}/sessions  Active sessions on a specific host
GET /api/sessions          All sessions across the pool
GET /api/status            App config (demo vs live, refresh interval)
```

---

## Architecture

```
src/avd_monitor/
├── main.py              FastAPI app + dashboard route
├── config.py            Settings from .env
├── models/
│   └── host.py          SessionHost, UserSession, PoolOverview — typed dataclasses
├── azure/
│   ├── client.py        DefaultAzureCredential + SDK client bundle (lazy init)
│   ├── hosts.py         Live AVD session host + Azure Monitor metric queries
│   └── demo.py          Realistic demo data — jitter, sparkline history, fake sessions
├── routers/
│   └── api.py           REST endpoints — demo and live share the same routes
└── templates/
    └── dashboard.html   Self-contained dark dashboard — Chart.js sparklines, SVG rings, no build step
```

No webpack. No node_modules. No build pipeline. It's a Python package — install it, run it.

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

16 tests, all run in demo mode. No Azure credentials, no mocks, no network calls.

---

## What This Doesn't Do

Honest limitations:

- **It doesn't fix overloaded hosts.** It shows you which ones are suffering. Draining sessions, adjusting autoscale, or right-sizing VMs is still your job.
- **CPU and memory come from Azure Monitor.** There's a 1–5 minute lag on those metrics — this is an Azure SDK limitation, not something we can work around.
- **No alerting built in.** The `/api/overview` endpoint is designed to be polled by whatever alerting system you already have. Native alerting is on the roadmap.
- **Single host pool per instance.** One pool per running instance. Run multiple instances for multiple pools.

---

## Need Help With Your AVD Environment?

This dashboard shows you where the pressure is. Solving it — right-sizing VM SKUs, tuning session limits, configuring autoscale that actually works, or figuring out why one host always hits 90% while others sit at 20% — is a different problem.

**Tarique Khemraj** is an Azure infrastructure specialist with hands-on experience building and troubleshooting AVD environments for enterprise clients.

**What I can help with:**
- Deploying this dashboard against your production AVD environment
- Diagnosing chronic high-pressure hosts — is it the VM size, the app, the session limit, or something else?
- Right-sizing your host pool SKUs and session maximums for your actual user workload
- Setting up Azure Monitor autoscale that doesn't over-provision or strand users
- Building the alerting layer so you're not watching a dashboard all day

📧 **t.khemraj@gmail.com**
🐙 **github.com/tkhemraj**

> If your users keep saying AVD is slow and Azure keeps saying everything is fine — that's exactly the gap this tool was built for.

---

## License

MIT — use it, fork it, build on it.

---

*FastAPI + Chart.js + Azure SDK. No build tools. Runs anywhere Python runs.*
