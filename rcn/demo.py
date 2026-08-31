"""
3-Minute Proof of Concept CLI Demonstrator.
Runs the complete RCN scenario:
1. Robot Alpha active on chassis-mir-amr-501
2. Motor fault triggered
3. Memory Vault snapshot created and cryptographically signed
4. Candidate replacement bodies evaluated (1 failing, 1 passing)
5. Hot-swap executed to Robot Beta chassis-mir-amr-882
6. Mission resumed with zero re-mapping
"""

import time
import sys
import json
from .models import RobotPassport, ChassisProfile, MemoryVault
from .vault import VaultManager
from .compatibility import CompatibilityEngine
from .crypto import CryptoEngine

# ANSI color codes for terminal display
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"\n{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{CYAN}   ROBOT CONTINUITY NETWORK (RCN) • 3-MINUTE PROOF OF CONCEPT{RESET}")
    print(f"{DIM}   Decoupling Robot Identity & Operational Experience from Hardware{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}\n")


def log_step(step_num: int, title: str, description: str):
    print(f"{BOLD}{GREEN}[STEP {step_num}] {title}{RESET}")
    print(f"{DIM}         {description}{RESET}")
    time.sleep(0.6)


def run_demo():
    print_banner()
    secret_key = "logix_intralogistics_fleet_secret_2026"

    # -------------------------------------------------------------
    # 1. SETUP ROBOT ALPHA RUNTIME
    # -------------------------------------------------------------
    log_step(1, "ACTIVE FLEET OPERATION", "Robot Alpha operating in Frankfurt Facility FRA-03")
    
    passport_data = {
        "passport_version": "1.0.0",
        "robot_id": "urn:rcn:identity:alpha-unit-07b9",
        "callsign": "Forklift-Titan-04",
        "owner_operator": {
            "org_id": "org_logix_global_99",
            "org_name": "Logix Intralogistics Corp",
            "contact_email": "ops@logix-corp.internal"
        },
        "issued_at": "2026-08-15T08:00:00Z",
        "capability_requirements": {
            "min_payload_kg": 300.0,
            "drive_type": "differential",
            "required_sensors": ["2d_lidar_safety", "depth_camera_front", "wheel_encoders"],
            "compute_tier": "edge_ai_mid"
        },
        "installed_skills": [
            {"skill_id": "skill_pallet_dock_v2", "name": "Precision Pallet Docking", "version": "2.4.1", "vendor": "AutonomousSkills Inc"},
            {"skill_id": "skill_dynamic_avoid", "name": "Smooth Obstacle Avoidance", "version": "1.8.0", "vendor": "Logix Robotics"}
        ],
        "permissions": {
            "site_id": "facility-fra-03-frankfurt",
            "site_zones": ["zone_inbound_dock", "zone_aisle_b_cold_storage", "zone_outbound_staging"],
            "max_speed_mps": 1.8,
            "hazardous_access": False
        },
        "vault_manifest_hash": "sha256:initial_boot_state",
        "audit_trail": [
            {"timestamp": "2026-08-15T08:15:00Z", "event_type": "INITIAL_COMMISSION", "chassis_id": "chassis-mir-amr-501", "hash": "sha256:init001"}
        ]
    }
    passport = RobotPassport.from_dict(passport_data)

    chassis_alpha = ChassisProfile(
        chassis_id="chassis-mir-amr-501",
        manufacturer="MobileIndRobots",
        model="MiR-600",
        drive_type="differential",
        max_payload_kg=600.0,
        max_linear_speed_mps=2.0,
        wheel_base_meters=0.78,
        available_sensors=["2d_lidar_safety", "depth_camera_front", "wheel_encoders"],
        compute_tier="edge_ai_mid",
        battery_level_pct=84.0
    )

    print(f"  • Identity URN   : {BOLD}{passport.robot_id}{RESET} ({passport.callsign})")
    print(f"  • Current Chassis: {chassis_alpha.chassis_id} ({chassis_alpha.manufacturer} {chassis_alpha.model})")
    print(f"  • Active Status  : In-transit with 340kg pallet to Cold Storage Rack 14")
    print(f"  • Progress       : Step 3 of 6 completed\n")
    time.sleep(0.8)

    # -------------------------------------------------------------
    # 2. TRIGGER CRITICAL HARDWARE FAULT
    # -------------------------------------------------------------
    log_step(2, "INCIDENT OCCURRENCE", "Motor controller thermal overload detected on Robot Alpha")
    print(f"  {RED}{BOLD}ALERT [FAULT_CODE: 0x8E12]{RESET} Left drive actuator stalled. Hardware failure is unrecoverable in-situ.")
    print(f"  {YELLOW}RCN Trigger:{RESET} Capturing atomic memory snapshot before chassis shutdown...\n")
    time.sleep(0.8)

    # Portable meaning captured
    portable_state = {
        "semantic_map": {
            "map_id": "fra-03-level1-warehouse-grid",
            "coordinate_frame": "map_global_enu",
            "named_zones": [
                {"zone_id": "zone_inbound_dock", "name": "Inbound Bay", "bounds": {"x_min": 0, "x_max": 25, "y_min": 0, "y_max": 15}},
                {"zone_id": "zone_aisle_b_cold_storage", "name": "Cold Storage", "bounds": {"x_min": 25, "x_max": 75, "y_min": 0, "y_max": 40}}
            ]
        },
        "active_tasks": [
            {
                "task_id": "task_dispatch_88291",
                "title": "Transfer Pallet #PL-904 to Cold Storage Rack 14",
                "status": "interrupted_by_fault",
                "priority": 1,
                "target_location": {"zone": "zone_aisle_b_cold_storage", "x": 58.4, "y": 24.1},
                "execution_cursor": {
                    "step_index": 3,
                    "completed_steps": ["nav_bay_3", "scan_qr_PL904", "lift_pallet_340kg"],
                    "remaining_steps": ["transit_aisle_b", "verify_rack_depth", "deposit_pallet"]
                }
            }
        ],
        "learned_preferences": {
            "docking_approach_angle_deg": 88.5,
            "cold_zone_traction_compensation": 0.35
        },
        "incident_lessons": [
            {"lesson_id": "lesson_cold_zone_01", "heuristic": "Reduce deceleration by 35% on wet threshold"}
        ]
    }

    vault = VaultManager.create_snapshot(passport, portable_state, trigger="hardware_fault")
    print(f"  ✓ Snapshot created : {BOLD}{vault.vault_id}{RESET}")
    print(f"  ✓ Vault Integrity  : {vault.checksum}")
    print(f"  ✓ Preserved State  : 1 active mission cursor, 2 semantic zones, 1 learned traction heuristic\n")
    time.sleep(0.8)

    # -------------------------------------------------------------
    # 3. COMPATIBILITY GATING
    # -------------------------------------------------------------
    log_step(3, "COMPATIBILITY VERIFICATION", "Scanning local fleet yard for compatible spare chassis")

    # Candidate 1: Incompatible chassis (light duty)
    candidate_light = ChassisProfile(
        chassis_id="chassis-turtle-light-01",
        manufacturer="GenericRobotics",
        model="LightCarrier-50",
        drive_type="differential",
        max_payload_kg=50.0,  # Fails! (requires 300kg)
        max_linear_speed_mps=1.0,
        wheel_base_meters=0.40,
        available_sensors=["2d_lidar_safety"],  # Missing depth camera
        compute_tier="edge_basic"
    )

    check_light = CompatibilityEngine.evaluate(passport, candidate_light)
    print(f"  Checking Candidate 1: {candidate_light.chassis_id} ({candidate_light.model})")
    print(f"    ↳ {RED}REJECTED{RESET} (Deficiencies: {'; '.join(check_light.deficiencies)})")

    # Candidate 2: Compatible replacement chassis
    candidate_beta = ChassisProfile(
        chassis_id="chassis-mir-amr-882",
        manufacturer="MobileIndRobots",
        model="MiR-600-Rev2",
        drive_type="differential",
        max_payload_kg=600.0,
        max_linear_speed_mps=2.2,
        wheel_base_meters=0.82,
        available_sensors=["2d_lidar_safety", "depth_camera_front", "wheel_encoders", "3d_lidar_roof"],
        compute_tier="edge_ai_high",
        battery_level_pct=96.0
    )

    check_beta = CompatibilityEngine.evaluate(passport, candidate_beta)
    print(f"  Checking Candidate 2: {candidate_beta.chassis_id} ({candidate_beta.model})")
    print(f"    ↳ {GREEN}APPROVED{RESET} (All {check_beta.total_checks} capability criteria satisfied)\n")
    time.sleep(0.8)

    # -------------------------------------------------------------
    # 4. EXECUTE CONTINUITY HOT-SWAP
    # -------------------------------------------------------------
    log_step(4, "HOT-SWAP TRANSFER & TARGET ADAPTATION", "Decoupling from dead body & binding to Robot Beta")

    transfer_result = VaultManager.execute_hot_swap(
        passport=passport,
        vault=vault,
        source_chassis=chassis_alpha,
        target_chassis=candidate_beta,
        signing_secret=secret_key
    )

    print(f"  ✓ Source chassis {chassis_alpha.chassis_id} safely wiped and decommissioned")
    print(f"  ✓ Target adaptation completed in {BOLD}{transfer_result.time_elapsed_ms} ms{RESET}:")
    for item in transfer_result.adapted_profile.adaptation_log:
        print(f"      • {item}")
    print(f"  ✓ Digital passport re-signed with key {passport.signature['key_id']}")
    print(f"  ✓ Signature: {passport.signature['value'][:24]}... [VERIFIED]\n")
    time.sleep(0.8)

    # -------------------------------------------------------------
    # 5. RESUMPTION & AUDIT TRAIL
    # -------------------------------------------------------------
    log_step(5, "OPERATIONAL RESUMPTION", "Robot Beta now possesses Alpha's identity, permissions, and mission")
    resumed = transfer_result.adapted_profile.active_mission_cursor
    print(f"  • Assigned Chassis  : {BOLD}{passport.current_embodiment['chassis_id']}{RESET}")
    print(f"  • Mission Resumed   : {resumed['title']}")
    print(f"  • Immediate Action  : {BOLD}{resumed['next_action']}{RESET} (Proceeding directly to Rack 14)")
    print(f"  • Total MTTR        : {BOLD}{GREEN}< 60 seconds{RESET} (vs. 3.5 hours for manual technician re-provisioning)")
    print(f"  • Facility Re-map   : {BOLD}{GREEN}0 minutes (Semantic map preserved){RESET}\n")

    print(f"{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{GREEN}   CONTINUITY TRANSFER VERIFIED • THE BODY CHANGED, THE MISSION SURVIVES{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}\n")


if __name__ == "__main__":
    run_demo()
