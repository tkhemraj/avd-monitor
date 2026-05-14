"""Realistic demo data for development and environments without Azure credentials."""

import random
import math
from datetime import datetime, timedelta
from ..models.host import SessionHost, UserSession, PoolOverview

_USERNAMES = [
    "alice.morgan", "bob.chen", "carol.smith", "david.park",
    "emma.johnson", "frank.wilson", "grace.lee", "henry.brown",
    "iris.taylor", "jack.davis", "karen.white", "liam.harris",
    "mia.martin", "noah.thompson", "olivia.garcia", "paul.martinez",
    "quinn.robinson", "rachel.clark", "sam.rodriguez", "tina.lewis",
]

_VM_SIZES = ["Standard_D4s_v5", "Standard_D8s_v5", "Standard_D4as_v5", "Standard_NV6ads_A10_v5"]

# Persistent "personality" per host so metrics stay plausible across refreshes
_HOST_PROFILES = [
    {"name": "avd-host-001", "base_cpu": 78, "base_mem": 82, "sessions": 14, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[1]},
    {"name": "avd-host-002", "base_cpu": 92, "base_mem": 88, "sessions": 16, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[1]},
    {"name": "avd-host-003", "base_cpu": 34, "base_mem": 51, "sessions":  6, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[0]},
    {"name": "avd-host-004", "base_cpu": 55, "base_mem": 63, "sessions": 10, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[0]},
    {"name": "avd-host-005", "base_cpu": 12, "base_mem": 29, "sessions":  2, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[0]},
    {"name": "avd-host-006", "base_cpu": 96, "base_mem": 94, "sessions": 16, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[2]},
    {"name": "avd-host-007", "base_cpu":  0, "base_mem":  0, "sessions":  0, "max": 16, "status": "Unavailable", "vm_size": _VM_SIZES[0]},
    {"name": "avd-host-008", "base_cpu": 67, "base_mem": 71, "sessions": 11, "max": 16, "status": "Available",   "vm_size": _VM_SIZES[3]},
]


def _jitter(base: float, spread: float = 5.0) -> float:
    return max(0.0, min(100.0, base + random.uniform(-spread, spread)))


def _history(base: float, n: int = 20) -> list:
    """Generate a plausible sparkline history trending toward base."""
    vals = []
    v = base + random.uniform(-15, 15)
    for _ in range(n):
        v += random.uniform(-4, 4)
        v = max(0, min(100, v))
        vals.append(round(v, 1))
    vals[-1] = round(_jitter(base, 3), 1)
    return vals


def _sessions_for_host(host_name: str, count: int) -> list:
    users = random.sample(_USERNAMES, min(count, len(_USERNAMES)))
    sessions = []
    for i, user in enumerate(users):
        connected = datetime.utcnow() - timedelta(minutes=random.randint(5, 480))
        state = "Disconnected" if random.random() < 0.15 else "Active"
        sessions.append(UserSession(
            session_id=f"{host_name}-s{i:02d}",
            username=user,
            state=state,
            host_name=host_name,
            connected_since=connected.strftime("%H:%M"),
            client_type=random.choice(["Windows Client", "Web Client", "macOS Client"]),
        ))
    return sessions


def get_demo_hosts() -> list:
    hosts = []
    for p in _HOST_PROFILES:
        cpu = _jitter(p["base_cpu"])
        mem = _jitter(p["base_mem"])
        sessions = p["sessions"]
        if p["status"] == "Unavailable":
            cpu, mem, sessions = 0.0, 0.0, 0

        host = SessionHost(
            name=p["name"],
            status=p["status"],
            cpu_percent=round(cpu, 1),
            memory_percent=round(mem, 1),
            sessions=sessions,
            max_sessions=p["max"],
            os_version="Windows 11 Enterprise 23H2",
            vm_size=p["vm_size"],
            allow_new_sessions=sessions < p["max"] and p["status"] == "Available",
            last_heartbeat=datetime.utcnow().strftime("%H:%M:%S UTC"),
            cpu_history=_history(p["base_cpu"]),
            memory_history=_history(p["base_mem"]),
            assigned_users=_sessions_for_host(p["name"], sessions),
        )
        hosts.append(host)
    return hosts


def get_demo_overview(hosts: list) -> PoolOverview:
    available = [h for h in hosts if h.is_available]
    all_sessions = [s for h in hosts for s in h.assigned_users]
    disconnected = sum(1 for s in all_sessions if s.is_disconnected)
    pressures = [h.pressure_score for h in available]

    return PoolOverview(
        host_pool_name="avd-prod-hostpool",
        total_hosts=len(hosts),
        available_hosts=len(available),
        total_sessions=sum(h.sessions for h in hosts),
        disconnected_sessions=disconnected,
        avg_cpu=sum(h.cpu_percent for h in available) / max(len(available), 1),
        avg_memory=sum(h.memory_percent for h in available) / max(len(available), 1),
        avg_pressure=sum(pressures) / max(len(pressures), 1),
        critical_hosts=sum(1 for h in hosts if h.pressure_level == "critical"),
        high_hosts=sum(1 for h in hosts if h.pressure_level == "high"),
        data_source="demo",
        last_updated=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
