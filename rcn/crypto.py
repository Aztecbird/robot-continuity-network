"""
Cryptographic verification and integrity module for RCN.
Implements canonical hash calculation, HMAC-SHA256 signatures, and tamper detection.
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Tuple


class CryptoEngine:
    """Manages digital seals and verification for passports and memory vaults."""

    @staticmethod
    def canonical_json(data: Dict[str, Any]) -> str:
        """Serializes dictionary to sorted, whitespace-stripped canonical JSON."""
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

    @staticmethod
    def compute_hash(data: Dict[str, Any]) -> str:
        """Computes SHA-256 hash formatted as sha256:<hex>."""
        raw = CryptoEngine.canonical_json(data).encode('utf-8')
        digest = hashlib.sha256(raw).hexdigest()
        return f"sha256:{digest}"

    @staticmethod
    def sign_payload(data: Dict[str, Any], secret_key: str, key_id: str = "fleet_root_key_2026") -> Dict[str, str]:
        """Signs a canonical JSON payload using HMAC-SHA256."""
        raw = CryptoEngine.canonical_json(data).encode('utf-8')
        signature_value = hmac.new(secret_key.encode('utf-8'), raw, hashlib.sha256).hexdigest()
        return {
            "algorithm": "HMAC-SHA256",
            "key_id": key_id,
            "value": signature_value
        }

    @staticmethod
    def verify_signature(data: Dict[str, Any], signature: Dict[str, str], secret_key: str) -> bool:
        """Verifies signature integrity against payload and secret key."""
        if not signature or signature.get("algorithm") != "HMAC-SHA256":
            return False
        
        expected_sig = CryptoEngine.sign_payload(data, secret_key, signature.get("key_id", ""))
        return hmac.compare_digest(expected_sig["value"], signature["value"])
