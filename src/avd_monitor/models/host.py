"""Data models for AVD session hosts and sessions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class UserSession:
    session_id: str
    username: str
    state: str          # Active, Disconnected, Pending
    host_name: str
    connected_since: Optional[str] = None
    client_type: Optional[str] = None

    @property
    def is_disconnected(self) -> bool:
        return self.state == "Disconnected"

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "username": self.username,
            "state": self.state,
            "host_name": self.host_name,
            "connected_since": self.connected_since,
            "client_type": self.client_type,
        }


@dataclass
class SessionHost:
    name: str
    status: str             # Available, Unavailable, Upgrading, NeedsAssistance
    cpu_percent: float
    memory_percent: float
    sessions: int
    max_sessions: int
    os_version: Optional[str] = None
    vm_size: Optional[str] = None
    allow_new_sessions: bool = True
    last_heartbeat: Optional[str] = None
    cpu_history: List[float] = field(default_factory=list)  # last N readings
    memory_history: List[float] = field(default_factory=list)
    assigned_users: List[UserSession] = field(default_factory=list)

    @property
    def session_load_percent(self) -> float:
        if self.max_sessions == 0:
            return 0.0
        return min(100.0, (self.sessions / self.max_sessions) * 100)

    @property
    def pressure_score(self) -> float:
        """Composite 0–100 pressure score. Higher = worse."""
        return round(
            self.cpu_percent * 0.40
            + self.memory_percent * 0.35
            + self.session_load_percent * 0.25,
            1,
        )

    @property
    def pressure_level(self) -> str:
        score = self.pressure_score
        if score >= 85:
            return "critical"
        if score >= 65:
            return "high"
        if score >= 40:
            return "moderate"
        return "healthy"

    @property
    def is_available(self) -> bool:
        return self.status == "Available"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "sessions": self.sessions,
            "max_sessions": self.max_sessions,
            "session_load_percent": round(self.session_load_percent, 1),
            "pressure_score": self.pressure_score,
            "pressure_level": self.pressure_level,
            "os_version": self.os_version,
            "vm_size": self.vm_size,
            "allow_new_sessions": self.allow_new_sessions,
            "last_heartbeat": self.last_heartbeat,
            "cpu_history": self.cpu_history,
            "memory_history": self.memory_history,
            "is_available": self.is_available,
        }


@dataclass
class PoolOverview:
    host_pool_name: str
    total_hosts: int
    available_hosts: int
    total_sessions: int
    disconnected_sessions: int
    avg_cpu: float
    avg_memory: float
    avg_pressure: float
    critical_hosts: int
    high_hosts: int
    data_source: str   # "live" or "demo"
    last_updated: str

    def to_dict(self) -> dict:
        return {
            "host_pool_name": self.host_pool_name,
            "total_hosts": self.total_hosts,
            "available_hosts": self.available_hosts,
            "total_sessions": self.total_sessions,
            "disconnected_sessions": self.disconnected_sessions,
            "avg_cpu": round(self.avg_cpu, 1),
            "avg_memory": round(self.avg_memory, 1),
            "avg_pressure": round(self.avg_pressure, 1),
            "critical_hosts": self.critical_hosts,
            "high_hosts": self.high_hosts,
            "data_source": self.data_source,
            "last_updated": self.last_updated,
        }
