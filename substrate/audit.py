"""
substrate.audit -- Merkle hash chain + cryptographic proofs.

Shared utility used by:
  - khop.py        (per-hop audit chain on K-hop traversal)
  - gdpr.py        (cryptographic proof of erasure)
  - counterfactual.py (Pearl-style do() operator audit chain)

Extracted from exp_counterfactual_do_operator_v1.py + exp_fact_checked_khop_merkle_chain_hp12_root_v1.py.
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional


def sha256(s: str) -> str:
    """Hex SHA-256 digest of a UTF-8 string."""
    return hashlib.sha256(s.encode()).hexdigest()


@dataclass
class AuditStep:
    """One step in a Merkle hash chain."""
    seq: int                            # 0-based position in the chain
    label: str                          # human-readable description
    payload: dict                       # the actual data (e.g., hop result, intervention)
    prev_hash: str                      # parent hash in the chain
    hash: str = ""                      # filled by AuditChain.append

    def canonical(self) -> str:
        """Deterministic string for hashing (sorted keys)."""
        return json.dumps(
            {"seq": self.seq, "label": self.label, "payload": self.payload, "prev": self.prev_hash},
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass
class AuditChain:
    """A linear Merkle hash chain. Each step's hash = sha256(canonical(step) including prev_hash).

    The chain root (last step's hash) cryptographically commits to the entire sequence.
    Tampering with any earlier step invalidates the root.
    """
    chain_id: str
    genesis: str = ""                   # filled by build
    steps: list[AuditStep] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.genesis:
            self.genesis = sha256(f"genesis:{self.chain_id}:{self.created_at}")

    @property
    def root(self) -> str:
        """The chain root (cryptographic commitment to all steps)."""
        if not self.steps:
            return self.genesis
        return self.steps[-1].hash

    def append(self, label: str, payload: dict) -> AuditStep:
        """Append a new step. Hash is computed automatically."""
        prev = self.root
        step = AuditStep(
            seq=len(self.steps),
            label=label,
            payload=payload,
            prev_hash=prev,
        )
        step.hash = sha256(step.canonical())
        self.steps.append(step)
        return step

    def verify(self) -> bool:
        """Replay the chain; return True iff every hash matches."""
        prev = self.genesis
        for step in self.steps:
            expected = AuditStep(
                seq=step.seq,
                label=step.label,
                payload=step.payload,
                prev_hash=prev,
            )
            expected.hash = sha256(expected.canonical())
            if expected.hash != step.hash:
                return False
            prev = step.hash
        return True

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "genesis": self.genesis,
            "root": self.root,
            "created_at": self.created_at,
            "steps": [
                {"seq": s.seq, "label": s.label, "payload": s.payload, "prev_hash": s.prev_hash, "hash": s.hash}
                for s in self.steps
            ],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AuditChain":
        chain = cls(chain_id=d["chain_id"], created_at=d["created_at"])
        chain.genesis = d["genesis"]
        for step_d in d["steps"]:
            step = AuditStep(
                seq=step_d["seq"],
                label=step_d["label"],
                payload=step_d["payload"],
                prev_hash=step_d["prev_hash"],
                hash=step_d["hash"],
            )
            chain.steps.append(step)
        return chain


def proof_of_erasure(entity: str, deleted_count: int, intact_check_passed: bool) -> AuditChain:
    """GDPR-compliance Merkle proof for the 'delete a person' wow moment."""
    chain = AuditChain(chain_id=f"gdpr-erase:{entity}")
    chain.append("identify_entity", {"entity": entity})
    chain.append("enumerate_facts", {"deleted_fact_count": deleted_count})
    chain.append("surgical_erase", {"method": "pinv_downdate"})
    chain.append("intact_verify", {"remaining_recall_unchanged": intact_check_passed})
    return chain


# ============================================================
# Self-test
# ============================================================

def _self_test():
    chain = AuditChain(chain_id="test-chain")
    chain.append("hop_1", {"from": "OpenAI", "to": "Sam Altman", "confidence": 0.99})
    chain.append("hop_2", {"from": "Sam Altman", "to": "Loopt", "confidence": 0.97})
    chain.append("hop_3", {"from": "Loopt", "to": "Y Combinator", "confidence": 0.93})

    assert chain.verify(), "fresh chain verifies"
    root = chain.root
    assert len(root) == 64, "sha256 hex root is 64 chars"

    # Tampering detected
    chain.steps[1].payload["confidence"] = 0.10  # tamper with hop 2
    assert not chain.verify(), "tampered chain rejected"

    # Round-trip serialization
    chain.steps[1].payload["confidence"] = 0.97  # restore
    serialized = chain.to_dict()
    restored = AuditChain.from_dict(serialized)
    assert restored.verify(), "round-trip verifies"
    assert restored.root == root, "root matches after round-trip"

    # GDPR proof
    erase_chain = proof_of_erasure(entity="John Doe", deleted_count=12, intact_check_passed=True)
    assert erase_chain.verify(), "erasure chain verifies"

    print("[substrate.audit] self-test PASS")


if __name__ == "__main__":
    _self_test()
