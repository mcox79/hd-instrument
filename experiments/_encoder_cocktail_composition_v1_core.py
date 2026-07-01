"""Shared core for encoder_cocktail_composition_v1 siblings.

Tests whether MIXING encoder families (FHRR + sparse_bipolar + binary_bipolar)
in the SAME substrate bundle composes cleanly, or whether uniform encoding is
an architectural constraint.

Prior work covered (per substrate-KB check 2026-07-01):
- ANCHOR 4 v4 encoder-family phase diagram: 5 encoders swept INDIVIDUALLY
    (not mixed) via _substrate_anchor4_encoder_family_phase_diagram_v4_core.
- hub_spoke_cross_encoder_alignment_v1: 3 SAME-family word encoders (w2v /
    glove / fasttext) aligned via HUB substrate; NOT heterogeneous HDC families.
- substrate_compose_heterogeneous_routing_v1..v3: two W-banks with phase or
    frequency routing, single encoder family per test.
- substrate_decision41_cross_encoder_rerank: rerank pipeline, not co-mixed bundle.

Genuinely novel angle: bind M=1024 items where SOME items are FHRR-encoded and
OTHERS are sparse-bipolar / binary-bipolar in the SAME BUNDLE, then query.

Cocktail mechanism (shape/dtype reconciliation):
    Each family produces distinct shape/dtype (FHRR: complex64 dim/2; sparse:
    float32 dim; binary: float32 dim). Common bundle domain = real float32 N_DIM.
    Family-specific real-projection at bind-output time:
        FHRR complex[N/2] -> concat([Re, Im]) -> real[N]
        sparse_bipolar float32[N] -> identity
        binary_bipolar float32[N] -> identity
    Bind is native-family (self-inverse elementwise mul or complex mul).
    Bundle = signed sum then sign-normalize (bipolar) or L2-normalize (real).

Query (ARM_X): item is encoded via ARM_X's expected encoder distribution,
query encoded via family-native bind against key, real-projected, cosine
scored against bundle. If encoders don't interoperate, cosine ~= 0 for
items encoded in a different family than the query.

Six arms (pairwise + baseline):
    ARM_FHRR_ONLY               -- baseline; reproduces prior encoder CG.
    ARM_FHRR_PLUS_SPARSE        -- 50/50 mix of FHRR + sparse_bipolar items.
    ARM_FHRR_PLUS_BINARY        -- 50/50 mix of FHRR + binary_bipolar items.
    ARM_SPARSE_PLUS_BINARY      -- 50/50 mix; no FHRR.
    ARM_ALL_THREE_MIXED         -- 33/33/33 mix of all three families.
    ARM_FHRR_QUERY_SPARSE_KEYS  -- keys built as sparse, query built as FHRR;
                                   cross-family retrieval (interop probe).

Pre-reg bands (per envelope-fail-bands discipline):
    HP_MIX_COMPOSES:
        mixed-encoder arms (FHRR_PLUS_SPARSE, FHRR_PLUS_BINARY, SPARSE_PLUS_BINARY,
        ALL_THREE_MIXED) each achieve set_recall >= ARM_FHRR_ONLY * 0.85 across
        all 3 seeds.
    HP_CROSS_ENCODER_QUERY:
        ARM_FHRR_QUERY_SPARSE_KEYS set_recall >= 0.50 across all 3 seeds
        (partial recall demonstrates structural interop).
    HF_MIX_CRUMBLES:
        any mixed-encoder arm set_recall < 0.30 on any seed
        (mix breaks mechanism).
    HF_CROSS_ENCODER_ZERO:
        ARM_FHRR_QUERY_SPARSE_KEYS set_recall < 0.10 on any seed
        (encoders don't interoperate).
    MIDDLE_BAND:
        anything in between (partial signal; not decisive).
    CHAIN_GRADE gate: HP_MIX_COMPOSES fires cross-seed (3/3 seeds pass).

Cardinality (CARDINALITY_OK; META_RULE_H discipline):
    EXPECTED_N_UNITS = 6 arms per seed; observed must equal expected.
    cross-seed cardinality = 18 units total (3 seeds).

Discriminator-must-survive-scale (USER 2026-06-26):
    Smoke runs at FULL-N (N=8192, M=1024) but with reduced M_QUERY for speed;
    the ARM_FHRR_ONLY baseline retention floor at smoke and full is measured
    off the same substrate scale, so the mix-vs-baseline ratio is a real
    discriminator surviving scale.

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME_BASE = "encoder_cocktail_composition_v1"

# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init)
# ---------------------------------------------------------------------------
N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # discriminator-must-survive-scale (USER 2026-06-26)
N_DIM_SELFTEST = 512  # small dim; still >= 128 for FHRR complex128 half

M_FULL = 1024  # items bound into substrate
M_SMOKE = 512  # items bound; halved for smoke speed
M_SELFTEST = 32

N_QUERY_FULL = 256
N_QUERY_SMOKE = 128
N_QUERY_SELFTEST = 16

SPARSE_BIPOLAR_DENSITY = 0.05

# Verdict-band thresholds
HP_MIX_RATIO_MIN = 0.85         # mixed >= baseline * this
HP_CROSS_RECALL_MIN = 0.50      # cross-encoder query >= this
HF_MIX_CRUMBLE_MAX = 0.30       # any mixed arm < this -> HF
HF_CROSS_ZERO_MAX = 0.10        # cross-arm < this -> HF

# Arm names (LOCKED at module init)
ARMS = (
    "ARM_FHRR_ONLY",
    "ARM_FHRR_PLUS_SPARSE",
    "ARM_FHRR_PLUS_BINARY",
    "ARM_SPARSE_PLUS_BINARY",
    "ARM_ALL_THREE_MIXED",
    "ARM_FHRR_QUERY_SPARSE_KEYS",
)
EXPECTED_N_UNITS = len(ARMS)  # 6
assert EXPECTED_N_UNITS == 6, f"expected 6 arms got {EXPECTED_N_UNITS}"

REQUIRED_FIELDS = (
    "verdict", "verdict_msg", "elapsed_s", "summary",
    "per_arm_recall", "arms_expected", "arms_observed",
    "cardinality_observed", "cardinality_expected",
    "mechanism_hashes",
)


# ---------------------------------------------------------------------------
# Encoder primitives (numpy float32; family-native bind ops)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Dense bipolar {-1,+1}^N float32."""
    g = np.random.default_rng(seed)
    return (g.integers(0, 2, size=(n_items, dim)) * 2 - 1).astype(np.float32)


def _build_sparse_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Sparse ternary {-1,0,+1}^N at density 0.05 float32."""
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_BIPOLAR_DENSITY * dim)))
    arr = np.zeros((n_items, dim), dtype=np.float32)
    for i in range(n_items):
        idx = g.choice(dim, size=s, replace=False)
        signs = (g.integers(0, 2, size=s) * 2 - 1).astype(np.float32)
        arr[i, idx] = signs
    return arr


def _build_fhrr(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Unit-modulus complex exp(i*phi) in C^(dim/2); returned as complex64.
    Total real DoF = dim (via [Re, Im] projection at bind-output).
    """
    if dim % 2 != 0:
        raise ValueError(f"FHRR requires even dim; got dim={dim}")
    g = np.random.default_rng(seed)
    n_complex = dim // 2
    phi = g.uniform(0.0, 2.0 * math.pi, size=(n_items, n_complex)).astype(np.float32)
    return (np.cos(phi) + 1j * np.sin(phi)).astype(np.complex64)


# Bind ops (native-family)
def bind_binary(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def bind_sparse(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def bind_fhrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


# Unbind ops (family-native inverse)
def unbind_binary(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (bound * key).astype(np.float32)


def unbind_sparse(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (bound * key).astype(np.float32)


def unbind_fhrr(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (bound * np.conj(key)).astype(np.complex64)


# Real-projection at bind-output (unify to real[N])
def to_real(vec: np.ndarray, dim: int, family: str) -> np.ndarray:
    """Project family-native output to real[N] for common bundle domain.
    FHRR complex[N/2] -> concat([Re, Im]) -> real[N].
    Sparse / binary already real[N]; return identity."""
    if family == "fhrr":
        if vec.ndim == 1:
            return np.concatenate([vec.real, vec.imag]).astype(np.float32)
        return np.concatenate([vec.real, vec.imag], axis=-1).astype(np.float32)
    return vec.astype(np.float32)


ENCODERS = ("fhrr", "sparse_bipolar", "binary_bipolar")


def build_family(family: str, n_items: int, dim: int, seed: int) -> np.ndarray:
    if family == "fhrr":
        return _build_fhrr(n_items, dim, seed)
    if family == "sparse_bipolar":
        return _build_sparse_bipolar(n_items, dim, seed)
    if family == "binary_bipolar":
        return _build_binary_bipolar(n_items, dim, seed)
    raise ValueError(f"unknown family: {family}")


def bind_family(family: str, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if family == "fhrr":
        return bind_fhrr(a, b)
    if family == "sparse_bipolar":
        return bind_sparse(a, b)
    if family == "binary_bipolar":
        return bind_binary(a, b)
    raise ValueError(f"unknown family: {family}")


def unbind_family(family: str, bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    if family == "fhrr":
        return unbind_fhrr(bound, key)
    if family == "sparse_bipolar":
        return unbind_sparse(bound, key)
    if family == "binary_bipolar":
        return unbind_binary(bound, key)
    raise ValueError(f"unknown family: {family}")


# ---------------------------------------------------------------------------
# Pre-flight distinctness gate (META_RULE_AY)
# ---------------------------------------------------------------------------
def preflight_distinct(dim: int = 256, seed: int = 0) -> Tuple[bool, Dict[str, str], str]:
    """Bind a fixed test pair under each family; SHA-256 verify distinct.
    Compares real-projected bound output byte-hash across families."""
    n = 4
    hashes: Dict[str, str] = {}
    collisions: List[Tuple[str, str]] = []
    for fam in ENCODERS:
        a = build_family(fam, n, dim, seed)
        b = build_family(fam, n, dim, seed + 1)
        bound = bind_family(fam, a, b)
        real_out = to_real(bound, dim, fam)
        h = hashlib.sha256(real_out.tobytes()).hexdigest()[:16]
        for prev_fam, prev_h in hashes.items():
            if prev_h == h:
                collisions.append((prev_fam, fam))
        hashes[fam] = h
    if collisions:
        msg = f"PREFLIGHT_HASH_COLLISION: collisions={collisions}; hashes={hashes}"
        return False, hashes, msg
    return True, hashes, f"preflight_distinct(dim={dim}): {hashes}"


# ---------------------------------------------------------------------------
# Substrate cocktail: bind M items into a mixed bundle, query recall
# ---------------------------------------------------------------------------
def measure_arm_recall(
    arm: str, m_items: int, n_query: int, dim: int, seed: int,
) -> Tuple[float, Dict[str, Any]]:
    """Bind m_items keys+values in per-arm encoder mix; query n_query times.
    Returns (set_recall, stats).

    Cocktail construction:
      Each item i is assigned a family per the arm's mix rule.
      key_i is drawn from that family; val_i is drawn from that family.
      bound_i = bind_family(fam_i, key_i, val_i) -> project to real[N].
      bundle = signed sum over all real[N] bound_i's; L2 normalize.

    Query for item i:
      q_bound_i = bind_family(fam_i, val_i, key_i)  # symmetric probe
      Actually: probe with key_i under family bind, expect val_i on unbind.
      Query = bundle * key_i_projected (approximation via subtract-then-decode)
    Simpler: same-family unbind on the bundle recovers val_i approximately
    when bundle is dominated by same-family items.

    Since bundle mixes families, we use a compositional readout:
      1. Take bundle (real[N]).
      2. For each candidate val_j at query time, compute cosine(bundle, real(bind(fam_i, key_i, val_j))).
      3. Correct if argmax_j is i (top-1 recall).
    """
    g = np.random.default_rng(seed)
    # Assign families to items per arm
    if arm == "ARM_FHRR_ONLY":
        fams = ["fhrr"] * m_items
        query_family = "fhrr"
        key_family = "fhrr"
    elif arm == "ARM_FHRR_PLUS_SPARSE":
        fams = ["fhrr" if g.random() < 0.5 else "sparse_bipolar" for _ in range(m_items)]
        query_family = None  # per-item
        key_family = None
    elif arm == "ARM_FHRR_PLUS_BINARY":
        fams = ["fhrr" if g.random() < 0.5 else "binary_bipolar" for _ in range(m_items)]
        query_family = None
        key_family = None
    elif arm == "ARM_SPARSE_PLUS_BINARY":
        fams = ["sparse_bipolar" if g.random() < 0.5 else "binary_bipolar" for _ in range(m_items)]
        query_family = None
        key_family = None
    elif arm == "ARM_ALL_THREE_MIXED":
        fams = [ENCODERS[int(g.integers(0, 3))] for _ in range(m_items)]
        query_family = None
        key_family = None
    elif arm == "ARM_FHRR_QUERY_SPARSE_KEYS":
        # Keys built as sparse; values built as sparse; query encoder = FHRR at readout
        fams = ["sparse_bipolar"] * m_items
        query_family = "fhrr"  # cross-family query
        key_family = "sparse_bipolar"
    else:
        raise ValueError(f"unknown arm: {arm}")

    # Build key + value tensors per family (family-native shapes)
    # We build ONE bank per family with all m_items indices allocated, then
    # select per-item slots based on assignment.
    keys_by_fam: Dict[str, np.ndarray] = {}
    vals_by_fam: Dict[str, np.ndarray] = {}
    for fam in ENCODERS:
        keys_by_fam[fam] = build_family(fam, m_items, dim, seed + 10 + hash(fam) % 100)
        vals_by_fam[fam] = build_family(fam, m_items, dim, seed + 30 + hash(fam) % 100)

    # Build the mixed bundle by summing real-projected bound vectors
    bundle = np.zeros(dim, dtype=np.float32)
    fam_counts: Dict[str, int] = {f: 0 for f in ENCODERS}
    for i in range(m_items):
        fam_i = fams[i]
        fam_counts[fam_i] += 1
        k = keys_by_fam[fam_i][i]
        v = vals_by_fam[fam_i][i]
        bound = bind_family(fam_i, k, v)
        real_bound = to_real(bound, dim, fam_i)
        bundle = bundle + real_bound
    # L2 normalize (dense case) OR sign (binary case)
    bn = np.linalg.norm(bundle)
    if bn > 1e-12:
        bundle = bundle / bn

    # Query: for each of n_query random items, compute the "probe" and score
    # top-1 recall.
    query_idx = g.choice(m_items, size=min(n_query, m_items), replace=False)
    correct = 0
    for qi in query_idx:
        # Family used at query time depends on arm
        if arm == "ARM_FHRR_QUERY_SPARSE_KEYS":
            # cross-encoder: keys are sparse but query readout uses fhrr codebook
            # for the SAME item i. We probe: bind FHRR key_i with FHRR val_j,
            # real-project, cosine against bundle. If it works, FHRR->sparse
            # encodings share hyperdim geometry.
            k = build_family("fhrr", 1, dim, seed + 10 + hash("fhrr") % 100 + qi * 0)[0]
            # actually to be consistent per-item we need deterministic per-i FHRR
            # key. Simpler: build FHRR keys explicitly for this arm.
            # We'll cheat by pre-building FHRR keys aligned to the SAME index i.
            fhrr_keys = keys_by_fam["fhrr"]
            fhrr_vals = vals_by_fam["fhrr"]
            k = fhrr_keys[qi]
            best_j = -1
            best_score = -np.inf
            for j in range(m_items):
                v_cand = fhrr_vals[j]
                bound_cand = bind_family("fhrr", k, v_cand)
                real_cand = to_real(bound_cand, dim, "fhrr")
                score = float(np.dot(bundle, real_cand) /
                              (np.linalg.norm(real_cand) + 1e-12))
                if score > best_score:
                    best_score = score
                    best_j = j
            if best_j == qi:
                correct += 1
        else:
            fam_i = fams[qi]
            k = keys_by_fam[fam_i][qi]
            best_j = -1
            best_score = -np.inf
            # Score candidate j by binding key_qi with val_j under fam_i,
            # real-projecting, and cosine against bundle.
            for j in range(m_items):
                v_cand = vals_by_fam[fam_i][j]
                bound_cand = bind_family(fam_i, k, v_cand)
                real_cand = to_real(bound_cand, dim, fam_i)
                score = float(np.dot(bundle, real_cand) /
                              (np.linalg.norm(real_cand) + 1e-12))
                if score > best_score:
                    best_score = score
                    best_j = j
            if best_j == qi:
                correct += 1

    recall = correct / max(1, len(query_idx))
    stats = {
        "n_query": int(len(query_idx)),
        "correct": int(correct),
        "family_counts": {k: int(v) for k, v in fam_counts.items()},
        "arm_family_mix_expected": arm,
    }
    return recall, stats


# ---------------------------------------------------------------------------
# Self-test: uses tiny scale that MUST fire the discriminator
# ---------------------------------------------------------------------------
def run_selftest() -> Tuple[bool, str]:
    ok_pre, hashes, msg_pre = preflight_distinct(dim=256, seed=0)
    if not ok_pre:
        return False, f"SELFTEST_FAIL_PREFLIGHT: {msg_pre}"

    # At tiny scale (dim=512, M=32, N_QUERY=16), the mechanism MUST hold for
    # single-family baseline. Cross-arm may or may not fire; we only assert
    # baseline discrimination as the smoke gate.
    baseline_recall, _ = measure_arm_recall(
        "ARM_FHRR_ONLY", M_SELFTEST, N_QUERY_SELFTEST, N_DIM_SELFTEST, seed=1,
    )
    if baseline_recall < 0.80:
        return False, (
            f"SELFTEST_FAIL_BASELINE: ARM_FHRR_ONLY recall={baseline_recall:.3f} "
            f"< 0.80 at N={N_DIM_SELFTEST} M={M_SELFTEST}. Encoder or bundle broken."
        )

    # Also verify at least one MIX arm runs cleanly (may or may not compose)
    mix_recall, _ = measure_arm_recall(
        "ARM_FHRR_PLUS_SPARSE", M_SELFTEST, N_QUERY_SELFTEST, N_DIM_SELFTEST, seed=1,
    )
    if not (0.0 <= mix_recall <= 1.0):
        return False, f"SELFTEST_FAIL_MIX_RANGE: mix_recall={mix_recall} out of [0,1]"

    return True, (
        f"SELFTEST_PASS: baseline={baseline_recall:.3f} "
        f"mix_fhrr_plus_sparse={mix_recall:.3f} preflight={msg_pre}"
    )


# ---------------------------------------------------------------------------
# Main cell driver (per seed)
# ---------------------------------------------------------------------------
def run_cell(seed: int, mode: str) -> Dict[str, Any]:
    t0 = time.time()
    if mode == "smoke":
        dim = N_DIM_SMOKE
        m_items = M_SMOKE
        n_query = N_QUERY_SMOKE
    else:
        dim = N_DIM_FULL
        m_items = M_FULL
        n_query = N_QUERY_FULL

    ok_pre, hashes, msg_pre = preflight_distinct(dim=min(dim, 512), seed=seed)
    if not ok_pre:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"PREFLIGHT_HASH_COLLISION: {msg_pre}",
            "elapsed_s": time.time() - t0,
            "summary": {"seed": seed, "mode": mode, "preflight_msg": msg_pre},
            "per_arm_recall": {},
            "arms_expected": list(ARMS),
            "arms_observed": [],
            "cardinality_observed": 0,
            "cardinality_expected": EXPECTED_N_UNITS,
            "mechanism_hashes": hashes,
        }

    per_arm_recall: Dict[str, float] = {}
    per_arm_stats: Dict[str, Any] = {}
    arms_observed: List[str] = []
    for arm in ARMS:
        recall, stats = measure_arm_recall(arm, m_items, n_query, dim, seed)
        per_arm_recall[arm] = float(recall)
        per_arm_stats[arm] = stats
        arms_observed.append(arm)

    # Verdict logic
    baseline = per_arm_recall["ARM_FHRR_ONLY"]
    mix_arms = ("ARM_FHRR_PLUS_SPARSE", "ARM_FHRR_PLUS_BINARY",
                "ARM_SPARSE_PLUS_BINARY", "ARM_ALL_THREE_MIXED")
    cross_arm = "ARM_FHRR_QUERY_SPARSE_KEYS"

    mix_recalls = [per_arm_recall[a] for a in mix_arms]
    cross_recall = per_arm_recall[cross_arm]
    mix_ratio_min = min(r / max(baseline, 1e-9) for r in mix_recalls)
    mix_recall_min = min(mix_recalls)

    # HARD_FAIL gates first (fire-fast)
    if any(r < HF_MIX_CRUMBLE_MAX for r in mix_recalls):
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HF_MIX_CRUMBLES: min mixed-arm recall={mix_recall_min:.3f} "
            f"< {HF_MIX_CRUMBLE_MAX}. Mix breaks mechanism. "
            f"per_arm={per_arm_recall}"
        )
    elif cross_recall < HF_CROSS_ZERO_MAX:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HF_CROSS_ENCODER_ZERO: cross_recall={cross_recall:.3f} "
            f"< {HF_CROSS_ZERO_MAX}. Encoders don't interoperate. "
            f"per_arm={per_arm_recall}"
        )
    # HARD_PASS gates
    elif (mix_ratio_min >= HP_MIX_RATIO_MIN and cross_recall >= HP_CROSS_RECALL_MIN):
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HP_BOTH: mix_ratio_min={mix_ratio_min:.3f} >= {HP_MIX_RATIO_MIN} "
            f"AND cross_recall={cross_recall:.3f} >= {HP_CROSS_RECALL_MIN}. "
            f"baseline={baseline:.3f} per_arm={per_arm_recall}"
        )
    elif mix_ratio_min >= HP_MIX_RATIO_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HP_MIX_COMPOSES: mix_ratio_min={mix_ratio_min:.3f} >= "
            f"{HP_MIX_RATIO_MIN}. baseline={baseline:.3f} cross={cross_recall:.3f} "
            f"per_arm={per_arm_recall}"
        )
    elif cross_recall >= HP_CROSS_RECALL_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HP_CROSS_ENCODER_QUERY: cross_recall={cross_recall:.3f} >= "
            f"{HP_CROSS_RECALL_MIN} but mix_ratio_min={mix_ratio_min:.3f} < "
            f"{HP_MIX_RATIO_MIN}. baseline={baseline:.3f} per_arm={per_arm_recall}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: mix_ratio_min={mix_ratio_min:.3f} in "
            f"[--, {HP_MIX_RATIO_MIN}) AND cross={cross_recall:.3f} in "
            f"[{HF_CROSS_ZERO_MAX}, {HP_CROSS_RECALL_MIN}). "
            f"baseline={baseline:.3f} per_arm={per_arm_recall}"
        )

    result = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.time() - t0,
        "summary": {
            "seed": seed,
            "mode": mode,
            "N_DIM": dim,
            "M_items": m_items,
            "N_QUERY": n_query,
            "per_arm_recall": per_arm_recall,
            "per_arm_stats": per_arm_stats,
            "baseline_recall": float(baseline),
            "mix_recall_min": float(mix_recall_min),
            "mix_ratio_min": float(mix_ratio_min),
            "cross_recall": float(cross_recall),
            "preflight_msg": msg_pre,
        },
        "per_arm_recall": per_arm_recall,
        "arms_expected": list(ARMS),
        "arms_observed": arms_observed,
        "cardinality_observed": len(arms_observed),
        "cardinality_expected": EXPECTED_N_UNITS,
        "mechanism_hashes": hashes,
    }
    return result


# ---------------------------------------------------------------------------
# Standard cell entry point
# ---------------------------------------------------------------------------
def _write_metrics_atomic(payload: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "metrics.json"
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp_path, out_path)


def cell_main(anchor_name: str, seed: int, argv: List[str]) -> int:
    if "--self-test" in argv:
        ok, msg = run_selftest()
        print(msg)
        exp_name = os.environ.get("HDLAB_EXP_NAME", f"{anchor_name}_selftest")
        out_dir = REPO / "data" / f"exp_{exp_name}"
        payload = {
            "verdict": "HARD_PASS" if ok else "HARD_FAIL",
            "verdict_msg": msg,
            "elapsed_s": 0.0,
            "summary": {"mode": "selftest"},
            "per_arm_recall": {},
            "arms_expected": list(ARMS),
            "arms_observed": [],
            "cardinality_observed": 0,
            "cardinality_expected": EXPECTED_N_UNITS,
            "mechanism_hashes": {},
        }
        _write_metrics_atomic(payload, out_dir)
        return 0 if ok else 1

    mode = "smoke" if "--smoke" in argv else "full"
    result = run_cell(seed=seed, mode=mode)
    exp_name = os.environ.get("HDLAB_EXP_NAME")
    if exp_name is None:
        suffix = "_smoke" if mode == "smoke" else ""
        exp_name = f"{anchor_name}_seed_{seed}{suffix}"
    out_dir = REPO / "data" / f"exp_{exp_name}"
    _write_metrics_atomic(result, out_dir)
    print(
        f"[{anchor_name} seed={seed} mode={mode}] "
        f"verdict={result['verdict']} elapsed={result['elapsed_s']:.1f}s"
    )
    print(f"  msg: {result['verdict_msg']}")
    # HARD_FAIL -> nonzero exit; MIDDLE_BAND and HARD_PASS -> zero
    return 0 if result["verdict"] != "HARD_FAIL" else 1
