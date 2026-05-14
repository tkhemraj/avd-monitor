"""Tests for AVD pressure monitor — runs fully in demo mode, no Azure creds needed."""

import pytest
from avd_monitor.azure.demo import get_demo_hosts, get_demo_overview
from avd_monitor.models.host import SessionHost, PoolOverview


def test_demo_hosts_count():
    hosts = get_demo_hosts()
    assert len(hosts) == 8


def test_demo_hosts_types():
    hosts = get_demo_hosts()
    for h in hosts:
        assert isinstance(h, SessionHost)
        assert isinstance(h.cpu_percent, float)
        assert isinstance(h.memory_percent, float)
        assert 0.0 <= h.cpu_percent <= 100.0
        assert 0.0 <= h.memory_percent <= 100.0


def test_unavailable_host_zeroed():
    hosts = get_demo_hosts()
    unavail = [h for h in hosts if h.status == "Unavailable"]
    assert len(unavail) >= 1
    for h in unavail:
        assert h.cpu_percent == 0.0
        assert h.memory_percent == 0.0
        assert h.sessions == 0


def test_pressure_score_range():
    hosts = get_demo_hosts()
    for h in hosts:
        assert 0.0 <= h.pressure_score <= 100.0


def test_pressure_level_values():
    hosts = get_demo_hosts()
    valid = {"healthy", "moderate", "high", "critical"}
    for h in hosts:
        assert h.pressure_level in valid


def test_session_load_percent():
    hosts = get_demo_hosts()
    for h in hosts:
        assert 0.0 <= h.session_load_percent <= 100.0


def test_sparkline_history_length():
    hosts = get_demo_hosts()
    for h in hosts:
        assert len(h.cpu_history) == 20
        assert len(h.memory_history) == 20


def test_demo_overview():
    hosts = get_demo_hosts()
    ov = get_demo_overview(hosts)
    assert isinstance(ov, PoolOverview)
    assert ov.total_hosts == len(hosts)
    assert ov.available_hosts <= ov.total_hosts
    assert ov.data_source == "demo"


def test_overview_to_dict():
    hosts = get_demo_hosts()
    ov = get_demo_overview(hosts)
    d = ov.to_dict()
    required = {"host_pool_name", "total_hosts", "available_hosts", "total_sessions",
                "avg_cpu", "avg_memory", "avg_pressure", "critical_hosts", "high_hosts",
                "data_source", "last_updated"}
    assert required.issubset(d.keys())


def test_host_to_dict():
    hosts = get_demo_hosts()
    d = hosts[0].to_dict()
    required = {"name", "status", "cpu_percent", "memory_percent", "sessions",
                "max_sessions", "pressure_score", "pressure_level", "is_available"}
    assert required.issubset(d.keys())


def test_fastapi_app_imports():
    from avd_monitor.main import app
    from avd_monitor.routers.api import router
    assert app is not None
    assert router is not None


def test_api_hosts(client):
    resp = client.get("/api/hosts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 8


def test_api_overview(client):
    resp = client.get("/api/overview")
    assert resp.status_code == 200
    ov = resp.json()
    assert "avg_pressure" in ov
    assert ov["data_source"] == "demo"


def test_api_host_not_found(client):
    resp = client.get("/api/hosts/does-not-exist")
    assert resp.status_code == 404


def test_api_sessions(client):
    resp = client.get("/api/sessions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard_route(client):
    import sys
    if sys.version_info >= (3, 14):
        pytest.skip("Jinja2 LRU cache key incompatibility with Python 3.14")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"AVD" in resp.content


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    import os
    os.environ["DEMO_MODE"] = "true"
    from avd_monitor.main import app
    return TestClient(app)
