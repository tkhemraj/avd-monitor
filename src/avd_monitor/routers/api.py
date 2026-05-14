"""REST API routes — /api/hosts, /api/overview, /api/sessions."""

from fastapi import APIRouter, HTTPException
from ..config import settings

router = APIRouter(prefix="/api")


def _fetch():
    """Return (hosts, overview) using live or demo data."""
    if settings.DEMO_MODE or not settings.azure_configured:
        from ..azure.demo import get_demo_hosts, get_demo_overview
        hosts = get_demo_hosts()
        overview = get_demo_overview(hosts)
    else:
        try:
            from ..azure.hosts import get_live_hosts, get_live_overview
            hosts = get_live_hosts()
            overview = get_live_overview(hosts)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Azure query failed: {exc}")
    return hosts, overview


@router.get("/overview")
def get_overview():
    _, overview = _fetch()
    return overview.to_dict()


@router.get("/hosts")
def get_hosts():
    hosts, _ = _fetch()
    return [h.to_dict() for h in hosts]


@router.get("/hosts/{host_name}")
def get_host(host_name: str):
    hosts, _ = _fetch()
    match = next((h for h in hosts if h.name == host_name), None)
    if not match:
        raise HTTPException(status_code=404, detail="Host not found")
    return match.to_dict()


@router.get("/hosts/{host_name}/sessions")
def get_host_sessions(host_name: str):
    hosts, _ = _fetch()
    match = next((h for h in hosts if h.name == host_name), None)
    if not match:
        raise HTTPException(status_code=404, detail="Host not found")
    return [s.to_dict() for s in match.assigned_users]


@router.get("/sessions")
def get_all_sessions():
    hosts, _ = _fetch()
    return [s.to_dict() for h in hosts for s in h.assigned_users]


@router.get("/status")
def get_status():
    return {
        "demo_mode": settings.DEMO_MODE,
        "azure_configured": settings.azure_configured,
        "refresh_interval_seconds": settings.REFRESH_INTERVAL_SECONDS,
    }
