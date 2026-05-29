"""Ed25519-signed deletion certificates (GDPR Article 17 aligned)."""

from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature


CERT_VERSION = "1.0"
SIGNING_ALGORITHM = "Ed25519"


def _b64(blob: bytes) -> str:
    """URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(blob).rstrip(b"=").decode("ascii")


def _b64decode(s: str) -> bytes:
    """Inverse of _b64."""
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _canonical(obj: Any) -> bytes:
    """Deterministic JSON serialization for signature payload."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _utc_iso(ts_ns: int) -> str:
    """ISO 8601 UTC string from ns timestamp."""
    return datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc).isoformat()


@dataclass
class SignedCertificate:
    """Ed25519-signed deletion record (GDPR Art 17 alignment)."""

    version: str
    cert_id: str
    fact_id: str
    audit_id: str
    deletion_ts: str
    deletion_ts_ns: int
    state_hash_before: str
    state_hash_after: str
    signer_pubkey: str
    signing_key_id: str
    signing_algorithm: str
    signature: str

    def to_dict(self) -> dict[str, Any]:
        """Return a dict copy suitable for JSON serialization."""
        return asdict(self)


def generate_keypair(key_dir: str, key_id: str = "key_default") -> tuple[str, str]:
    """Create Ed25519 keypair; persist PEMs; return (private_path, public_path)."""
    os.makedirs(key_dir, exist_ok=True)
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_path = os.path.join(key_dir, f"{key_id}.priv.pem")
    pub_path = os.path.join(key_dir, f"{key_id}.pub.pem")
    with open(priv_path, "wb") as fh:
        fh.write(
            priv.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    with open(pub_path, "wb") as fh:
        fh.write(
            pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    return priv_path, pub_path


def load_private_key(path: str) -> Ed25519PrivateKey:
    """Load Ed25519 private key from PEM file."""
    with open(path, "rb") as fh:
        key = serialization.load_pem_private_key(fh.read(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError(f"Expected Ed25519PrivateKey, got {type(key).__name__}")
    return key


def load_public_key(path: str) -> Ed25519PublicKey:
    """Load Ed25519 public key from PEM file."""
    with open(path, "rb") as fh:
        key = serialization.load_pem_public_key(fh.read())
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError(f"Expected Ed25519PublicKey, got {type(key).__name__}")
    return key


def _pubkey_b64(pub: Ed25519PublicKey) -> str:
    """Return raw 32-byte public key as urlsafe-b64 string."""
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64(raw)


def _pubkey_from_b64(s: str) -> Ed25519PublicKey:
    """Reconstruct Ed25519 public key from urlsafe-b64 string."""
    return Ed25519PublicKey.from_public_bytes(_b64decode(s))


class DeletionCertService:
    """Issuer + verifier for substrate deletion certificates."""

    def __init__(self, private_key: Ed25519PrivateKey, key_id: str = "key_default") -> None:
        self._priv = private_key
        self._pub = private_key.public_key()
        self.key_id = key_id

    @property
    def public_key_b64(self) -> str:
        """Return signer public key as urlsafe-b64 string."""
        return _pubkey_b64(self._pub)

    def issue_certificate(
        self,
        deleted_fact_id: str,
        audit_record_id: str,
        ts_ns: int | None,
        substrate_state_before_hash: str,
        substrate_state_after_hash: str,
    ) -> SignedCertificate:
        """Build, sign and return a deletion certificate."""
        if ts_ns is None:
            ts_ns = time.time_ns()
        body = {
            "version": CERT_VERSION,
            "cert_id": "cert_" + uuid.uuid4().hex,
            "fact_id": deleted_fact_id,
            "audit_id": audit_record_id,
            "deletion_ts": _utc_iso(ts_ns),
            "deletion_ts_ns": ts_ns,
            "state_hash_before": substrate_state_before_hash,
            "state_hash_after": substrate_state_after_hash,
            "signer_pubkey": self.public_key_b64,
            "signing_key_id": self.key_id,
            "signing_algorithm": SIGNING_ALGORITHM,
        }
        signature = self._priv.sign(_canonical(body))
        return SignedCertificate(**body, signature=_b64(signature))


def verify_certificate(cert: SignedCertificate | dict[str, Any]) -> bool:
    """Verify a deletion certificate's Ed25519 signature against its embedded pubkey."""
    data = cert.to_dict() if isinstance(cert, SignedCertificate) else dict(cert)
    sig_b64 = data.pop("signature", None)
    if not sig_b64:
        return False
    try:
        pub = _pubkey_from_b64(data["signer_pubkey"])
        pub.verify(_b64decode(sig_b64), _canonical(data))
        return True
    except (InvalidSignature, KeyError, ValueError):
        return False


def load_or_create_service(key_dir: str, key_id: str = "key_default") -> DeletionCertService:
    """Load existing Ed25519 keypair from key_dir or generate one."""
    priv_path = os.path.join(key_dir, f"{key_id}.priv.pem")
    if not os.path.exists(priv_path):
        generate_keypair(key_dir, key_id)
    return DeletionCertService(load_private_key(priv_path), key_id=key_id)
