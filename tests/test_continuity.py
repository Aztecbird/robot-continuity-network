"""
Automated unit tests for Robot Continuity Network (RCN).
Tests passport validation, cryptographic integrity, compatibility checks, and hot-swap transfers.
"""

import unittest
from rcn.models import RobotPassport, ChassisProfile, MemoryVault
from rcn.crypto import CryptoEngine
from rcn.compatibility import CompatibilityEngine
from rcn.adaptation import AdaptationEngine
from rcn.vault import VaultManager


class TestRCNContinuity(unittest.TestCase):

    def setUp(self):
        self.secret_key = "test_fleet_secret_key_999"
        self.passport_data = {
            "passport_version": "1.0.0",
            "robot_id": "urn:rcn:identity:alpha-unit-07b9",
            "callsign": "Forklift-Titan-04",
            "owner_operator": {
                "org_id": "org_logix_global_99",
                "org_name": "Logix Intralogistics",
                "contact_email": "ops@logix.internal"
            },
            "issued_at": "2026-08-15T08:00:00Z",
            "capability_requirements": {
                "min_payload_kg": 300.0,
                "drive_type": "differential",
                "required_sensors": ["2d_lidar_safety", "depth_camera_front", "wheel_encoders"],
                "compute_tier": "edge_ai_mid"
            },
            "installed_skills": [
                {"skill_id": "skill_pallet_dock_v2", "name": "Precision Docking", "version": "2.4.1", "vendor": "AutoSkills"}
            ],
            "permissions": {
                "site_id": "facility-fra-03",
                "site_zones": ["zone_inbound_dock", "zone_aisle_b"],
                "max_speed_mps": 1.8,
                "hazardous_access": False
            },
            "vault_manifest_hash": "sha256:init",
            "audit_trail": []
        }
        self.passport = RobotPassport.from_dict(self.passport_data)

        self.chassis_source = ChassisProfile(
            chassis_id="chassis-source-01",
            manufacturer="MiR",
            model="MiR-600",
            drive_type="differential",
            max_payload_kg=600.0,
            max_linear_speed_mps=2.0,
            wheel_base_meters=0.78,
            available_sensors=["2d_lidar_safety", "depth_camera_front", "wheel_encoders"],
            compute_tier="edge_ai_mid"
        )

        self.chassis_target = ChassisProfile(
            chassis_id="chassis-target-02",
            manufacturer="MiR",
            model="MiR-600-Rev2",
            drive_type="differential",
            max_payload_kg=650.0,
            max_linear_speed_mps=2.2,
            wheel_base_meters=0.80,
            available_sensors=["2d_lidar_safety", "depth_camera_front", "wheel_encoders", "3d_lidar"],
            compute_tier="edge_ai_high"
        )

    def test_crypto_signing_and_tamper_detection(self):
        payload = {"robot_id": "urn:rcn:identity:alpha-unit-07b9", "site": "fra-03"}
        sig = CryptoEngine.sign_payload(payload, self.secret_key)
        self.assertTrue(CryptoEngine.verify_signature(payload, sig, self.secret_key))

        # Tampered payload must fail
        tampered_payload = {"robot_id": "urn:rcn:identity:alpha-unit-07b9", "site": "fra-99-unauthorized"}
        self.assertFalse(CryptoEngine.verify_signature(tampered_payload, sig, self.secret_key))

        # Wrong secret key must fail
        self.assertFalse(CryptoEngine.verify_signature(payload, sig, "wrong_secret_key"))

    def test_compatibility_rejection_missing_sensors(self):
        inadequate_chassis = ChassisProfile(
            chassis_id="chassis-bad-sensors",
            manufacturer="VendorX",
            model="ModelB",
            drive_type="differential",
            max_payload_kg=500.0,
            max_linear_speed_mps=1.5,
            wheel_base_meters=0.6,
            available_sensors=["2d_lidar_safety"],  # missing depth_camera_front & wheel_encoders
            compute_tier="edge_ai_mid"
        )
        res = CompatibilityEngine.evaluate(self.passport, inadequate_chassis)
        self.assertFalse(res.is_compatible)
        self.assertTrue(any("Missing mandatory sensors" in d for d in res.deficiencies))

    def test_compatibility_rejection_low_payload(self):
        weak_chassis = ChassisProfile(
            chassis_id="chassis-weak",
            manufacturer="VendorX",
            model="ModelTiny",
            drive_type="differential",
            max_payload_kg=150.0,  # requires 300kg
            max_linear_speed_mps=1.5,
            wheel_base_meters=0.5,
            available_sensors=["2d_lidar_safety", "depth_camera_front", "wheel_encoders"],
            compute_tier="edge_ai_mid"
        )
        res = CompatibilityEngine.evaluate(self.passport, weak_chassis)
        self.assertFalse(res.is_compatible)
        self.assertTrue(any("Insufficient payload capacity" in d for d in res.deficiencies))

    def test_adaptation_engine(self):
        portable = {
            "semantic_map": {"map_id": "map-01"},
            "active_tasks": [{
                "task_id": "task-01",
                "title": "Pick Pallet",
                "execution_cursor": {"step_index": 2, "remaining_steps": ["move_to_rack"]}
            }]
        }
        vault = VaultManager.create_snapshot(self.passport, portable)
        adapted = AdaptationEngine.adapt(self.passport, vault, self.chassis_target)

        # Permitted speed is 1.8, target chassis limit is 2.2 -> effective must be 1.8
        self.assertEqual(adapted.effective_max_speed_mps, 1.8)
        self.assertEqual(adapted.active_mission_cursor["task_id"], "task-01")
        self.assertEqual(adapted.active_mission_cursor["next_action"], "move_to_rack")

    def test_full_hot_swap_success(self):
        portable = {
            "semantic_map": {"map_id": "map-01"},
            "active_tasks": [{
                "task_id": "task-99",
                "title": "Unload Pallet",
                "execution_cursor": {"step_index": 1, "remaining_steps": ["confirm_drop"]}
            }]
        }
        vault = VaultManager.create_snapshot(self.passport, portable)
        result = VaultManager.execute_hot_swap(
            passport=self.passport,
            vault=vault,
            source_chassis=self.chassis_source,
            target_chassis=self.chassis_target,
            signing_secret=self.secret_key
        )

        self.assertTrue(result.success)
        self.assertEqual(self.passport.current_embodiment["chassis_id"], self.chassis_target.chassis_id)
        self.assertIsNotNone(self.passport.signature)
        self.assertTrue(len(self.passport.audit_trail) >= 2)


if __name__ == "__main__":
    unittest.main()
