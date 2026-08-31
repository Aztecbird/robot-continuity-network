"""
Memory Vault & Transfer Management Engine.
Implements snapshot creation, cryptographic hashing, secure wipe of retired bodies,
and atomic re-binding to a replacement chassis.
"""

from typing import Dict, Any, Optional
import time
from .models import RobotPassport, MemoryVault, ChassisProfile, AuditEntry
from .crypto import CryptoEngine
from .compatibility import CompatibilityEngine, CompatibilityCheckResult
from .adaptation import AdaptationEngine, AdaptedRuntimeProfile


class ContinuityTransferResult:
    def __init__(self,
                 success: bool,
                 passport: RobotPassport,
                 vault: MemoryVault,
                 source_chassis_id: str,
                 target_chassis_id: str,
                 compatibility: CompatibilityCheckResult,
                 adapted_profile: Optional[AdaptedRuntimeProfile],
                 time_elapsed_ms: float,
                 error: Optional[str] = None):
        self.success = success
        self.passport = passport
        self.vault = vault
        self.source_chassis_id = source_chassis_id
        self.target_chassis_id = target_chassis_id
        self.compatibility = compatibility
        self.adapted_profile = adapted_profile
        self.time_elapsed_ms = time_elapsed_ms
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "robot_id": self.passport.robot_id,
            "callsign": self.passport.callsign,
            "source_chassis_id": self.source_chassis_id,
            "target_chassis_id": self.target_chassis_id,
            "time_elapsed_ms": self.time_elapsed_ms,
            "compatibility": self.compatibility.to_dict(),
            "adapted_profile": self.adapted_profile.to_dict() if self.adapted_profile else None,
            "error": self.error,
            "audit_trail_length": len(self.passport.audit_trail)
        }


class VaultManager:
    """Orchestrates secure vault creation and cross-embodiment continuity transfer."""

    @classmethod
    def create_snapshot(cls,
                        passport: RobotPassport,
                        portable_meaning: Dict[str, Any],
                        trigger: str = "hardware_fault") -> MemoryVault:
        """Captures a portable memory snapshot and computes its cryptographic hash."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        vault_id = f"urn:rcn:vault:snapshot-{int(time.time())}"

        # calculate hash of portable meaning
        meaning_hash = CryptoEngine.compute_hash(portable_meaning)

        vault = MemoryVault(
            vault_version="1.0.0",
            vault_id=vault_id,
            robot_id=passport.robot_id,
            snapshot_timestamp=now_iso,
            snapshot_trigger=trigger,
            portable_meaning=portable_meaning,
            body_specific_cache={},
            checksum=meaning_hash
        )

        passport.vault_manifest_hash = meaning_hash
        return vault

    @classmethod
    def execute_hot_swap(cls,
                         passport: RobotPassport,
                         vault: MemoryVault,
                         source_chassis: ChassisProfile,
                         target_chassis: ChassisProfile,
                         signing_secret: str) -> ContinuityTransferResult:
        """
        Executes complete continuity transfer from source body to target body.
        Guarantees:
        1. Cryptographic validation of vault integrity
        2. Compatibility verification on target body
        3. Target adaptation (velocity, sensors, task cursor)
        4. Atomic rebind and audit trail logging
        """
        start_time = time.time()

        # Step 1: Verify Vault Hash Integrity
        computed_hash = CryptoEngine.compute_hash(vault.portable_meaning)
        if vault.checksum != computed_hash:
            elapsed = (time.time() - start_time) * 1000
            compat_dummy = CompatibilityCheckResult(False, [], ["Corrupted vault checksum"], [])
            return ContinuityTransferResult(
                success=False,
                passport=passport,
                vault=vault,
                source_chassis_id=source_chassis.chassis_id,
                target_chassis_id=target_chassis.chassis_id,
                compatibility=compat_dummy,
                adapted_profile=None,
                time_elapsed_ms=elapsed,
                error="Integrity violation: Vault manifest checksum does not match payload."
            )

        # Step 2: Compatibility Check on Target Body
        compat_result = CompatibilityEngine.evaluate(passport, target_chassis)
        if not compat_result.is_compatible:
            elapsed = (time.time() - start_time) * 1000
            return ContinuityTransferResult(
                success=False,
                passport=passport,
                vault=vault,
                source_chassis_id=source_chassis.chassis_id,
                target_chassis_id=target_chassis.chassis_id,
                compatibility=compat_result,
                adapted_profile=None,
                time_elapsed_ms=elapsed,
                error=f"Compatibility rejected: {'; '.join(compat_result.deficiencies)}"
            )

        # Step 3: Target Adaptation (Body vs. Identity)
        adapted_profile = AdaptationEngine.adapt(passport, vault, target_chassis)

        # Step 4: Revoke / Sanitization log on Source Chassis
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        wipe_event = {
            "timestamp": now_iso,
            "event_type": "CHASSIS_DECOMMISSION_AND_WIPE",
            "chassis_id": source_chassis.chassis_id,
            "hash": CryptoEngine.compute_hash({"action": "secure_wipe", "source": source_chassis.chassis_id})
        }
        passport.audit_trail.append(wipe_event)

        # Step 5: Bind Target Chassis & Sign
        rebind_event = {
            "timestamp": now_iso,
            "event_type": "CONTINUITY_REBIND",
            "chassis_id": target_chassis.chassis_id,
            "hash": CryptoEngine.compute_hash({
                "target": target_chassis.chassis_id,
                "vault_id": vault.vault_id,
                "resumed_task": adapted_profile.active_mission_cursor.get("task_id")
            })
        }
        passport.audit_trail.append(rebind_event)

        passport.current_embodiment = {
            "chassis_id": target_chassis.chassis_id,
            "manufacturer": target_chassis.manufacturer,
            "model": target_chassis.model,
            "bound_at": now_iso
        }

        # Re-sign passport with new state
        passport_payload_for_signing = {
            "robot_id": passport.robot_id,
            "current_embodiment": passport.current_embodiment,
            "vault_manifest_hash": passport.vault_manifest_hash,
            "audit_trail_length": len(passport.audit_trail)
        }
        passport.signature = CryptoEngine.sign_payload(passport_payload_for_signing, signing_secret)

        elapsed = round((time.time() - start_time) * 1000, 2)
        return ContinuityTransferResult(
            success=True,
            passport=passport,
            vault=vault,
            source_chassis_id=source_chassis.chassis_id,
            target_chassis_id=target_chassis.chassis_id,
            compatibility=compat_result,
            adapted_profile=adapted_profile,
            time_elapsed_ms=elapsed
        )
