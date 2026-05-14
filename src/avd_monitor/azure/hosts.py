"""Live Azure AVD session host and session queries."""

from datetime import datetime, timedelta
from ..config import settings
from ..models.host import SessionHost, UserSession, PoolOverview
from .client import get_clients


def _get_cpu_memory(clients, resource_group: str, vm_names: list[str]) -> dict[str, tuple[float, float]]:
    """Returns {vm_name: (cpu_percent, memory_percent)} from Azure Monitor."""
    results: dict[str, tuple[float, float]] = {}
    end = datetime.utcnow()
    start = end - timedelta(minutes=10)

    for vm_name in vm_names:
        resource_id = (
            f"/subscriptions/{settings.AZURE_SUBSCRIPTION_ID}"
            f"/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        )
        try:
            resp = clients.metrics.query_resource(
                resource_id,
                metric_names=["Percentage CPU", "Available Memory Bytes"],
                timespan=(start, end),
                granularity=timedelta(minutes=5),
            )
            cpu = 0.0
            mem_avail_bytes = None
            for metric in resp.metrics:
                for ts in metric.timeseries:
                    vals = [d.average for d in ts.data if d.average is not None]
                    if vals:
                        if metric.name == "Percentage CPU":
                            cpu = round(vals[-1], 1)
                        elif metric.name == "Available Memory Bytes":
                            mem_avail_bytes = vals[-1]

            # Estimate memory % from available bytes — assumes 16 GB default if VM size unknown
            mem_percent = 0.0
            if mem_avail_bytes is not None:
                total_bytes = 16 * 1024 ** 3
                mem_percent = round(max(0.0, min(100.0, (1 - mem_avail_bytes / total_bytes) * 100)), 1)

            results[vm_name] = (cpu, mem_percent)
        except Exception:
            results[vm_name] = (0.0, 0.0)

    return results


def get_live_hosts() -> list[SessionHost]:
    clients = get_clients()
    rg = settings.AZURE_RESOURCE_GROUP
    pool = settings.AZURE_HOST_POOL

    raw_hosts = list(clients.avd.session_hosts.list(rg, pool))
    vm_names = [h.name.split("/")[-1] for h in raw_hosts]
    metrics_map = _get_cpu_memory(clients, rg, vm_names)

    hosts = []
    for raw in raw_hosts:
        vm_name = raw.name.split("/")[-1]
        cpu, mem = metrics_map.get(vm_name, (0.0, 0.0))
        session_count = raw.sessions_active or 0
        max_sessions = raw.max_session_limit or 16

        raw_sessions = list(clients.avd.user_sessions.list(rg, pool, vm_name))
        sessions = [
            UserSession(
                session_id=s.name,
                username=s.user_principal_name or "unknown",
                state=s.session_state or "Unknown",
                host_name=vm_name,
                connected_since=s.create_time.strftime("%H:%M") if s.create_time else None,
                client_type=s.client_type,
            )
            for s in raw_sessions
        ]

        hosts.append(SessionHost(
            name=vm_name,
            status=raw.status or "Unknown",
            cpu_percent=cpu,
            memory_percent=mem,
            sessions=session_count,
            max_sessions=max_sessions,
            os_version=raw.os_version,
            vm_size=raw.virtual_machine_id,
            allow_new_sessions=raw.allow_new_session or False,
            last_heartbeat=raw.last_heart_beat.strftime("%H:%M:%S UTC") if raw.last_heart_beat else None,
            cpu_history=[cpu],
            memory_history=[mem],
            assigned_users=sessions,
        ))

    return hosts


def get_live_overview(hosts: list[SessionHost]) -> PoolOverview:
    available = [h for h in hosts if h.is_available]
    all_sessions = [s for h in hosts for s in h.assigned_users]
    disconnected = sum(1 for s in all_sessions if s.is_disconnected)
    pressures = [h.pressure_score for h in available]

    return PoolOverview(
        host_pool_name=settings.AZURE_HOST_POOL,
        total_hosts=len(hosts),
        available_hosts=len(available),
        total_sessions=sum(h.sessions for h in hosts),
        disconnected_sessions=disconnected,
        avg_cpu=sum(h.cpu_percent for h in available) / max(len(available), 1),
        avg_memory=sum(h.memory_percent for h in available) / max(len(available), 1),
        avg_pressure=sum(pressures) / max(len(pressures), 1),
        critical_hosts=sum(1 for h in hosts if h.pressure_level == "critical"),
        high_hosts=sum(1 for h in hosts if h.pressure_level == "high"),
        data_source="live",
        last_updated=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
