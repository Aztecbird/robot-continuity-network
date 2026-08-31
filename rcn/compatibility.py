"""
Hardware Compatibility Engine.
Verifies whether a candidate physical chassis can satisfy a Robot Passport's requirements.
"""

from typing import Dict, Any, List, Tuple
from .models import ChassisProfile, RobotPassport


class CompatibilityCheckResult:
    def __init__(self, is_compatible: bool, checks: List[Dict[str, Any]], deficiencies: List[str], warnings: List[str]):
        self.is_compatible = is_compatible
        self.checks = checks
        self.deficiencies = deficiencies
        self.warnings = warnings

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        return len([c for c in self.checks if c["passed"]])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compatible": self.is_compatible,
            "passed_checks": self.passed_checks,
            "total_checks": self.total_checks,
            "deficiencies": self.deficiencies,
            "warnings": self.warnings,
            "details": self.checks
        }


class CompatibilityEngine:
    COMPUTE_TIER_RANK = {
        "edge_basic": 1,
        "edge_ai_mid": 2,
        "edge_ai_high": 3
    }

    @classmethod
    def evaluate(cls, passport: RobotPassport, chassis: ChassisProfile) -> CompatibilityCheckResult:
        reqs = passport.capability_requirements
        checks = []
        deficiencies = []
        warnings = []

        # 1. Payload Capacity
        min_payload = reqs.get("min_payload_kg", 0.0)
        payload_ok = chassis.max_payload_kg >= min_payload
        checks.append({
            "dimension": "payload_capacity",
            "required": f"{min_payload} kg",
            "available": f"{chassis.max_payload_kg} kg",
            "passed": payload_ok
        })
        if not payload_ok:
            deficiencies.append(f"Insufficient payload capacity: required {min_payload} kg, chassis supports {chassis.max_payload_kg} kg")

        # 2. Drive / Kinematics Type
        req_drive = reqs.get("drive_type")
        drive_ok = (chassis.drive_type == req_drive)
        checks.append({
            "dimension": "drive_kinematics",
            "required": req_drive,
            "available": chassis.drive_type,
            "passed": drive_ok
        })
        if not drive_ok:
            deficiencies.append(f"Kinematic mismatch: required {req_drive}, chassis is {chassis.drive_type}")

        # 3. Required Sensors
        req_sensors = set(reqs.get("required_sensors", []))
        avail_sensors = set(chassis.available_sensors)
        missing_sensors = list(req_sensors - avail_sensors)
        sensors_ok = len(missing_sensors) == 0
        checks.append({
            "dimension": "sensor_complement",
            "required": list(req_sensors),
            "available": list(avail_sensors),
            "missing": missing_sensors,
            "passed": sensors_ok
        })
        if not sensors_ok:
            deficiencies.append(f"Missing mandatory sensors: {', '.join(missing_sensors)}")

        # 4. Compute Tier
        req_tier = reqs.get("compute_tier", "edge_basic")
        avail_tier = chassis.compute_tier
        req_rank = cls.COMPUTE_TIER_RANK.get(req_tier, 1)
        avail_rank = cls.COMPUTE_TIER_RANK.get(avail_tier, 1)
        tier_ok = avail_rank >= req_rank
        checks.append({
            "dimension": "onboard_compute",
            "required": req_tier,
            "available": avail_tier,
            "passed": tier_ok
        })
        if not tier_ok:
            deficiencies.append(f"Underpowered compute tier: requires {req_tier}, chassis has {avail_tier}")

        # 5. Battery Level Warning
        if chassis.battery_level_pct < 20.0:
            warnings.append(f"Low battery on candidate chassis: {chassis.battery_level_pct}%")

        is_compatible = (len(deficiencies) == 0)
        return CompatibilityCheckResult(is_compatible, checks, deficiencies, warnings)
