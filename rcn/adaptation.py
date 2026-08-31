"""
Target Adaptation Engine (Body vs. Identity Layer).
Transforms portable semantic meaning into body-specific actuator velocity,
steering limits, and sensor mappings for a new physical chassis.
"""

from typing import Dict, Any, List
from .models import RobotPassport, MemoryVault, ChassisProfile


class AdaptedRuntimeProfile:
    def __init__(self,
                 target_chassis_id: str,
                 effective_max_speed_mps: float,
                 turn_rate_radps: float,
                 sensor_routing: Dict[str, str],
                 active_mission_cursor: Dict[str, Any],
                 adaptation_log: List[str]):
        self.target_chassis_id = target_chassis_id
        self.effective_max_speed_mps = effective_max_speed_mps
        self.turn_rate_radps = turn_rate_radps
        self.sensor_routing = sensor_routing
        self.active_mission_cursor = active_mission_cursor
        self.adaptation_log = adaptation_log

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_chassis_id": self.target_chassis_id,
            "effective_max_speed_mps": self.effective_max_speed_mps,
            "turn_rate_radps": self.turn_rate_radps,
            "sensor_routing": self.sensor_routing,
            "active_mission_cursor": self.active_mission_cursor,
            "adaptation_log": self.adaptation_log
        }


class AdaptationEngine:
    """Adapts high-level portable memory to target hardware kinematics and sensors."""

    @classmethod
    def adapt(cls, passport: RobotPassport, vault: MemoryVault, target_chassis: ChassisProfile) -> AdaptedRuntimeProfile:
        log: List[str] = []

        # 1. Kinematics Adaptation
        permitted_speed = passport.permissions.get("max_speed_mps", 1.0)
        hardware_speed_limit = target_chassis.max_linear_speed_mps
        effective_speed = min(permitted_speed, hardware_speed_limit)
        log.append(f"Adapted linear velocity cap: {effective_speed} m/s (Permitted: {permitted_speed}, Chassis Max: {hardware_speed_limit})")

        # Turn rate adapted from wheelbase
        # standard angular velocity calculation: omega = v / (wheel_base / 2)
        safe_turn_rate = round(effective_speed / (target_chassis.wheel_base_meters * 0.5), 2)
        log.append(f"Recalculated angular rate limit for wheelbase {target_chassis.wheel_base_meters}m: {safe_turn_rate} rad/s")

        # 2. Sensor Topic & Driver Routing
        sensor_routing = {}
        for s in target_chassis.available_sensors:
            if "lidar" in s:
                sensor_routing["safety_laser"] = f"/hardware/{target_chassis.chassis_id}/sensors/lidar_raw"
            elif "camera" in s:
                sensor_routing["vision_depth"] = f"/hardware/{target_chassis.chassis_id}/sensors/depth_stream"
            elif "encoder" in s:
                sensor_routing["odometry_wheel"] = f"/hardware/{target_chassis.chassis_id}/odom"
        log.append(f"Mapped {len(sensor_routing)} logical sensor endpoints to physical driver buses")

        # 3. Mission Cursor Restoration
        active_tasks = vault.portable_meaning.get("active_tasks", [])
        resumed_mission = {}
        if active_tasks:
            current_task = active_tasks[0]
            cursor = current_task.get("execution_cursor", {})
            resumed_mission = {
                "task_id": current_task["task_id"],
                "title": current_task["title"],
                "resume_step_index": cursor.get("step_index", 0),
                "next_action": cursor.get("remaining_steps", ["idle"])[0],
                "target_coordinates": current_task.get("target_location", {}),
                "status": "resumed_on_target_chassis"
            }
            log.append(f"Resumed task {current_task['task_id']} from step #{cursor.get('step_index', 0)}: '{resumed_mission['next_action']}'")
        else:
            log.append("No active mission in vault; initialized in standby dispatch mode")

        return AdaptedRuntimeProfile(
            target_chassis_id=target_chassis.chassis_id,
            effective_max_speed_mps=effective_speed,
            turn_rate_radps=safe_turn_rate,
            sensor_routing=sensor_routing,
            active_mission_cursor=resumed_mission,
            adaptation_log=log
        )
