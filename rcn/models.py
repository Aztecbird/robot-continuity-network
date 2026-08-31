"""
Data models for the Robot Continuity Network.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import time


@dataclass
class ChassisProfile:
    """Represents the physical capabilities and limits of a specific robot body."""
    chassis_id: str
    manufacturer: str
    model: str
    drive_type: str  # e.g., "differential", "omni", "ackermann"
    max_payload_kg: float
    max_linear_speed_mps: float
    wheel_base_meters: float
    available_sensors: List[str]
    compute_tier: str  # "edge_basic", "edge_ai_mid", "edge_ai_high"
    battery_level_pct: float = 100.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChassisProfile":
        return cls(**data)


@dataclass
class CapabilityRequirements:
    min_payload_kg: float
    drive_type: str
    required_sensors: List[str]
    compute_tier: str


@dataclass
class AuditEntry:
    timestamp: str
    event_type: str
    chassis_id: str
    hash: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobotPassport:
    """The persistent, verifiable identity of a robot independent of its chassis."""
    passport_version: str
    robot_id: str
    callsign: str
    owner_operator: Dict[str, str]
    issued_at: str
    capability_requirements: Dict[str, Any]
    installed_skills: List[Dict[str, Any]]
    permissions: Dict[str, Any]
    vault_manifest_hash: str
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    current_embodiment: Optional[Dict[str, Any]] = None
    signature: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RobotPassport":
        return cls(**data)


@dataclass
class MemoryVault:
    """The portable semantic memory, active missions, and environmental maps."""
    vault_version: str
    vault_id: str
    robot_id: str
    snapshot_timestamp: str
    snapshot_trigger: str
    portable_meaning: Dict[str, Any]
    body_specific_cache: Dict[str, Any]
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryVault":
        return cls(**data)
