"""
substrate.gdpr -- PP-104 surgical exact erasure via pinv downdate.

Port of exp_delete_downdate_exactness_cpu_v1.py + exp_eu_aiact_gdpr_cocompliance_v1.py.

CORE IDEA:
A pinv-trained associative memory W satisfies W = (K^T K + lambda I)^-1 K^T V where K
are keys and V are values. To delete a subset of rows (entity's facts), recompute:
    W' = (K_keep^T K_keep + lambda I)^-1 K_keep^T V_keep

Properties (validated cycle 162 + 178):
- Remaining facts: intact (~1.0 recall)
- Deleted facts: removed (~1.0 prediction != gold)
- Per-erase: <1 ms at M=1M (PP-104)

Demo wow moment: "Delete all facts about John Doe; substrate forgets exactly. Bare LLM
cannot do this — training data persists in weights."

V1.1 FLAG per Research VERIFY 2026-06-08: intact_sample_size=32 is acceptable for v1
demo at <100K facts. Production should bump to 256+ samples OR a percentage of substrate
size for stronger statistical confidence in the intact_check_passed assertion.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from substrate.audit import proof_of_erasure


@dataclass
class EraseResult:
    entity: str
    deleted_count: int
    elapsed_ms: float
    intact_check_passed: bool
    proof_root: str                  # Merkle root of the erasure audit chain
    proof: dict = field(default_factory=dict)


def surgical_erase(
    keys: np.ndarray,                # (M, D) bipolar key matrix
    values: np.ndarray,              # (M, V) value matrix (bipolar or one-hot)
    delete_indices: np.ndarray,      # row indices to delete
    entity_name: str,
    lambda_reg: float = 1e-3,
    intact_sample_size: int = 32,
) -> tuple[np.ndarray, EraseResult]:
    """Re-solve the substrate matrix W with delete_indices removed.

    Returns (new_W, erase_result_with_audit_proof).
    """
    t0 = time.perf_counter()
    M, D = keys.shape
    keep_mask = np.ones(M, dtype=bool)
    keep_mask[delete_indices] = False

    K_keep = keys[keep_mask]
    V_keep = values[keep_mask]

    gram = K_keep.T @ K_keep + lambda_reg * np.eye(D)
    W_new = np.linalg.solve(gram, K_keep.T @ V_keep)

    # Intact-check: for a sample of remaining keys, predicted argmax matches gold
    intact_passed = True
    if intact_sample_size > 0 and len(keys[keep_mask]) >= intact_sample_size:
        rng = np.random.default_rng(0)
        sample_idx = rng.choice(np.where(keep_mask)[0], min(intact_sample_size, keep_mask.sum()), replace=False)
        pred = (keys[sample_idx] @ W_new) @ values.T
        sample_pred_argmax = np.argmax(pred, axis=1)
        sample_gold_argmax = np.argmax(values[sample_idx] @ values.T, axis=1)
        intact_passed = bool((sample_pred_argmax == sample_gold_argmax).mean() > 0.95)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    proof = proof_of_erasure(
        entity=entity_name,
        deleted_count=int(len(delete_indices)),
        intact_check_passed=intact_passed,
    )
    return W_new, EraseResult(
        entity=entity_name,
        deleted_count=int(len(delete_indices)),
        elapsed_ms=elapsed_ms,
        intact_check_passed=intact_passed,
        proof_root=proof.root,
        proof=proof.to_dict(),
    )


def _self_test():
    rng = np.random.default_rng(14)
    D = 512
    M = int(0.7 * D)
    V_DIM = 256

    # Build bipolar keys + one-hot values
    K = np.sign(rng.standard_normal((M, D))).astype(np.float32)
    bk = np.sign(rng.standard_normal((M * 4, V_DIM))).astype(np.float32)
    V = bk[rng.integers(0, len(bk), M)]
    gold = np.argmax(V @ bk.T, axis=1)

    delete_idx = rng.choice(M, M // 5, replace=False)

    W_new, result = surgical_erase(
        keys=K,
        values=V,
        delete_indices=delete_idx,
        entity_name="TestEntity",
    )

    # Recompute predictions
    pred = np.argmax((K @ W_new) @ bk.T, axis=1)
    keep_mask = np.ones(M, dtype=bool)
    keep_mask[delete_idx] = False

    intact_rate = (pred[keep_mask] == gold[keep_mask]).mean()
    removed_rate = (pred[delete_idx] != gold[delete_idx]).mean()
    assert intact_rate >= 0.99, f"intact_rate {intact_rate:.4f} < 0.99"
    assert removed_rate >= 0.90, f"removed_rate {removed_rate:.4f} < 0.90"
    assert result.proof_root, "proof root should be non-empty"
    assert len(result.proof_root) == 64, "sha256 hex"

    print(f"[substrate.gdpr] self-test PASS (intact={intact_rate:.4f} removed={removed_rate:.4f} in {result.elapsed_ms:.1f} ms)")


if __name__ == "__main__":
    _self_test()
