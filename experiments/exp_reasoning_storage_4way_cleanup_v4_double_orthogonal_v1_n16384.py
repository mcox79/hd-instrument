"""REASONING STORAGE 4-WAY CLEANUP v4 -- DOUBLE-DELTA HADAMARD: hop-id AND entity at N=16384.

CONTEXT (v3 MIDDLE_BAND at 2pp exact bound; double-delta escalation):
  v3 introduced Hadamard-orthogonal hop-id codewords (single delta). It landed
  AT the 2pp strict bound: 2/5 seeds strict-pass, mean ratio borderline.
  Verdict_handler routed DOUBLE-DELTA as next escalation:
  combine Hadamard-orthogonal hop-id AND Hadamard-orthogonal entity codewords
  (vs random-draw BSC for entity).

  Single-delta (v3) showed orthogonality helps; double-delta tests whether
  compound orthogonalization closes the remaining gap.

DOUBLE-DELTA CONSTRUCTION (vs v3):
  Delta 1 (from v3): cb_hop uses Hadamard rows (first D=10 rows of H_{N}).
  Delta 2 (new v4): cb_entity uses Hadamard rows EXTENDED to N_ENTITY_CODEWORDS rows.

  N=16384 = 2^14. N_ENTITY_CODEWORDS rows of H_{16384}. We need rows 10..10+N_entity-1
  (starting after the D=10 hop rows to avoid overlap).

  Key properties:
  - Entity rows are mutually orthogonal (h_i . h_j = 0 for i != j, exact).
  - Entity rows are orthogonal to hop rows (all distinct rows of H_{N}).
  - Unbinding algebra IDENTICAL: Hadamard entries are {-1,+1}, so h^2 = 1 per entry,
    same as BSC. 4-way unbinding: k_step * k1 * k2 * h -> r (same algebra).
  - Cross-correlation reduction: where random BSC entity codewords have O(sqrt(N))
    cross-talk (in both 4-way and cleanup lookup), Hadamard gives exact zero
    for all entity-entity and entity-hop cross-correlations.

  FORMULA SELF-TEST: H_{16384}[i] . H_{16384}[j] = 0 for i != j; N for i == j.

  SINGLE DELTA ENGINEERING vs v3:
  All other arms (A, B, C) IDENTICAL to v3. Rule and relation codebooks remain BSC.
  The only changes are cb_hop (Hadamard, same as v3) AND cb_entity (Hadamard, new).

SCIENTIFIC QUESTION:
  Does compound orthogonalization (both hop-id and entity codewords Hadamard) close
  the structured-key gap to < 2% across ALL 5 seeds?

PRE-REGISTERED BANDS:
  Arm C (combined 4-way + cleanup) -- PRIMARY:
    HARD-PASS  : Arm C structured-key accuracy ratio >= 0.98 (gap < 2%);
                 ALL 5 seeds pass; cleanup verification rate >= 0.95.
    HARD-FAIL  : ratio < 0.96.
    MIDDLE-BAND: ratio 0.96-0.98 (further partial closure; gap not yet closed).

  Differential interpretation vs v3:
    If v4 >= HP and v3 was MIDDLE: compound orthogonality causally closes gap.
    If v4 remains MIDDLE: gap source is elsewhere (capacity, chain depth).
    If v4 is HF: Hadamard entity codewords introduce interference (investigate).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.
PROT-021: per-seed checkpointing.
PROT-022: device=cpu forced (identical to v1/v2/v3).

OOM CHECK: N=16384 W = 1 GB. Remote CPU 64 GB RAM. OK.

TIMEOUT ESTIMATE:
  v3 elapsed ~5 min for 5 seeds. v4 adds Hadamard entity construction overhead
  (second make_hadamard_codebook call, N_entity rows instead of D=10; slightly
  slower but same asymptotic profile). Upper bound: same as v3.
  ceil(1.5 * 180) = 270s. PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. Hadamard H_{2^k}: rows are {-1,+1}, mutually orthogonal.
  2. h_i . h_j = 0 for i != j (exact). h_i . h_i = N.
  3. Hop rows and entity rows are distinct rows of H_N -> also orthogonal to each other.
  4. 4-way unbinding: k_step * k1 * k2 * h = r (h^2=1, k1^2=1, k2^2=1 per {-1,+1}).
  5. Verdict gates HP/HF/MB work correctly.

Anchor: reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384
Queue: remote_cpu_queue (CPU-only)
Pre-reg: preregs/2026-06-01_reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384.md
Total cells: 5 seeds x 3 arms = 15 arm evaluations.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ============================================================
# PROT-018: _n16384 binds N = 16384
# ============================================================
N_FULL  = 16384
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# Load v1 module to reuse ALL scientific functions
_v1_path = REPO / "experiments" / "exp_reasoning_storage_4way_cleanup_v1_n16384.py"
_v1_spec = importlib.util.spec_from_file_location("rs4w_v1_for_v4", _v1_path)
_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_v1)

# All scientific functions from v1
make_bsc_codebook         = _v1.make_bsc_codebook
make_reasoning_corpus     = _v1.make_reasoning_corpus
make_random_corpus        = _v1.make_random_corpus
make_4way_corpus          = _v1.make_4way_corpus
make_3way_cleanup_corpus  = _v1.make_3way_cleanup_corpus
make_4way_cleanup_corpus  = _v1.make_4way_cleanup_corpus
build_W_from_corpus       = _v1.build_W_from_corpus
retrieval_accuracy        = _v1.retrieval_accuracy
audit_4way_encoding       = _v1.audit_4way_encoding
cleanup_audit_stats       = _v1.cleanup_audit_stats
compute_verdict           = _v1.compute_verdict

# Checkpoint helpers from v1
list_completed_keys = _v1.list_completed_keys
write_partial_key   = _v1.write_partial_key
load_partial_key    = _v1.load_partial_key

# v1 constants
N_RULE_CODEWORDS      = _v1.N_RULE_CODEWORDS
N_ENTITY_CODEWORDS    = _v1.N_ENTITY_CODEWORDS
N_RELATION_CODEWORDS  = _v1.N_RELATION_CODEWORDS
N_HOP_ID_CODEWORDS    = _v1.N_HOP_ID_CODEWORDS   # D=10
N_CHAINS_FULL         = _v1.N_CHAINS_FULL
N_CHAINS_SMOKE        = _v1.N_CHAINS_SMOKE
N_SMOKE               = _v1.N_SMOKE
HP_RATIO_C            = _v1.HP_RATIO_C
HP_VERIFY_C           = _v1.HP_VERIFY_C
HF_RATIO_C            = _v1.HF_RATIO_C
HP_CONF_STEP          = _v1.HP_CONF_STEP

# ============================================================
# v4 config: 5 seeds + Hadamard HOP + Hadamard ENTITY
# ============================================================
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Hadamard row offsets: first D=10 rows for hop, next N_ENTITY_CODEWORDS for entity
# This guarantees all rows are distinct -> orthogonal to each other
HOP_ROW_OFFSET    = 0
ENTITY_ROW_OFFSET = N_HOP_ID_CODEWORDS  # = 10; entity rows start after hop rows


def make_hadamard_codebook(N: int, D: int, row_offset: int,
                            device: torch.device) -> torch.Tensor:
    """Build D x N Hadamard-orthogonal codewords from rows [row_offset, row_offset+D).

    H[i, j] = (-1)^popcount(i & j). Row i has entries in {-1, +1}.
    Rows with different i values are exactly orthogonal.

    Args:
        N:          Vector dimension (must be power of 2).
        D:          Number of rows to extract.
        row_offset: Starting row index in H_N (to allow non-overlapping hop vs entity).
        device:     Target torch device.

    Returns:
        Tensor of shape (D, N) with entries {-1, +1}.
    """
    assert (N & (N - 1)) == 0, f"N must be power of 2; got {N}"
    assert row_offset + D <= N, f"row_offset+D={row_offset+D} > N={N}"

    j_idx = np.arange(N, dtype=np.int64)
    rows = []
    for r in range(row_offset, row_offset + D):
        bitwise_and = r & j_idx
        popcount = np.array([bin(int(x)).count('1') for x in bitwise_and],
                            dtype=np.float32)
        row_vals = torch.tensor((-1.0) ** popcount, dtype=torch.float32)
        rows.append(row_vals.unsqueeze(0))

    H = torch.cat(rows, dim=0).to(device)  # (D, N)
    assert H.abs().max().item() == 1.0, "Hadamard entries not in {-1, +1}"
    return H


def run_one_seed_double_orthogonal(
    N_use: int,
    n_chains: int,
    seed: int,
    device: torch.device,
) -> Dict:
    """Run 3 arms with BOTH Hadamard hop AND Hadamard entity codewords (double-delta)."""
    t0 = time.time()

    # Build codebooks
    cb_rule    = make_bsc_codebook(N_use, N_RULE_CODEWORDS, seed + 0, device)
    cb_rel     = make_bsc_codebook(N_use, N_RELATION_CODEWORDS, seed + 2, device)

    # DOUBLE DELTA:
    # Delta 1 (from v3): Hadamard hop-id codewords
    cb_hop    = make_hadamard_codebook(N_use, N_HOP_ID_CODEWORDS,
                                        HOP_ROW_OFFSET, device)
    # Delta 2 (new v4): Hadamard entity codewords
    cb_entity = make_hadamard_codebook(N_use, N_ENTITY_CODEWORDS,
                                        ENTITY_ROW_OFFSET, device)

    # Verify Hadamard orthogonality for hop codebook
    gram_hop = (cb_hop @ cb_hop.T) / float(N_use)
    hop_off  = gram_hop - torch.diag(gram_hop.diag())
    max_hop_off = float(hop_off.abs().max().item())
    assert abs(float(gram_hop.diag().mean().item()) - 1.0) < 1e-4, \
        f"Hadamard hop norm not 1: {gram_hop.diag().mean().item():.6f}"
    assert max_hop_off < 1e-4, \
        f"Hadamard hop off-diagonal not zero: max_off={max_hop_off:.6f}"

    # Verify Hadamard orthogonality for entity codebook
    # N_ENTITY_CODEWORDS may be large; spot-check first 10 rows for speed
    n_ent_check = min(10, N_ENTITY_CODEWORDS)
    gram_ent = (cb_entity[:n_ent_check] @ cb_entity[:n_ent_check].T) / float(N_use)
    ent_off  = gram_ent - torch.diag(gram_ent.diag())
    max_ent_off = float(ent_off.abs().max().item())
    assert abs(float(gram_ent.diag().mean().item()) - 1.0) < 1e-4, \
        f"Hadamard entity norm not 1: {gram_ent.diag().mean().item():.6f}"
    assert max_ent_off < 1e-4, \
        f"Hadamard entity off-diagonal not zero (first {n_ent_check} rows): {max_ent_off:.6f}"

    # Verify hop-entity cross-orthogonality (distinct rows of H_N -> orthogonal)
    cross = (cb_hop @ cb_entity[:n_ent_check].T) / float(N_use)
    max_cross = float(cross.abs().max().item())
    # All rows are distinct from H_N -> should be exactly 0
    assert max_cross < 1e-4, \
        f"Hadamard hop-entity cross not zero: max_cross={max_cross:.6f}"

    hop_entity_sim = max_cross

    # --- Baseline: 3-way structured corpus (uses Hadamard entity) ---
    keys_struct, vals_struct, chain_meta = make_reasoning_corpus(
        cb_rule, cb_entity, cb_rel, n_chains, seed, device)
    M_steps = keys_struct.shape[0]
    W_struct = build_W_from_corpus(keys_struct, vals_struct, N_use)

    n_probe = min(200, M_steps)
    baseline_result = retrieval_accuracy(
        W_struct, keys_struct, chain_meta, cb_entity, N_use, n_probe, seed)

    keys_rand, vals_rand = make_random_corpus(
        M_steps, N_use, seed, device, cb_entity, chain_meta)
    W_rand = build_W_from_corpus(keys_rand, vals_rand, N_use)
    rand_result = retrieval_accuracy(
        W_rand, keys_rand, chain_meta, cb_entity, N_use, n_probe, seed + 1000)

    # --- Arm A: 4-way binding only (Hadamard hop + Hadamard entity) ---
    keys_4w, vals_4w = make_4way_corpus(
        cb_rule, cb_entity, cb_rel, cb_hop, chain_meta, device)
    W_4w = build_W_from_corpus(keys_4w, vals_4w, N_use)
    arm_a_result = retrieval_accuracy(
        W_4w, keys_4w, chain_meta, cb_entity, N_use, n_probe, seed + 2000)
    arm_a_audit = audit_4way_encoding(
        cb_rule, cb_entity, cb_rel, cb_hop, keys_4w, chain_meta, N_use, n_audit=100)

    # --- Arm B: 3-way + cleanup (Hadamard entity) ---
    keys_3wc, vals_3wc, audit_b = make_3way_cleanup_corpus(
        cb_rule, cb_entity, cb_rel, chain_meta, device)
    W_3wc = build_W_from_corpus(keys_3wc, vals_3wc, N_use)
    arm_b_result = retrieval_accuracy(
        W_3wc, keys_3wc, chain_meta, cb_entity, N_use, n_probe, seed + 3000)
    arm_b_cleanup_stats = cleanup_audit_stats(audit_b)

    # --- Arm C: 4-way + cleanup (Hadamard hop + Hadamard entity; PRIMARY) ---
    keys_4wc, vals_4wc, audit_c = make_4way_cleanup_corpus(
        cb_rule, cb_entity, cb_rel, cb_hop, chain_meta, device)
    W_4wc = build_W_from_corpus(keys_4wc, vals_4wc, N_use)
    arm_c_result = retrieval_accuracy(
        W_4wc, keys_4wc, chain_meta, cb_entity, N_use, n_probe, seed + 4000)
    arm_c_cleanup_stats = cleanup_audit_stats(audit_c)

    elapsed = round(time.time() - t0, 2)

    ra = rand_result["mean_per_hop_acc"]
    def ratio(a): return round(a / ra, 5) if ra > 1e-6 else 0.0

    print(
        f"  seed={seed} M={M_steps} "
        f"baseline={baseline_result['mean_per_hop_acc']:.3f} "
        f"rand={ra:.3f} "
        f"A_4way={arm_a_result['mean_per_hop_acc']:.3f}(ratio={ratio(arm_a_result['mean_per_hop_acc']):.3f}) "
        f"B_cleanup={arm_b_result['mean_per_hop_acc']:.3f}(ratio={ratio(arm_b_result['mean_per_hop_acc']):.3f}) "
        f"C_combined={arm_c_result['mean_per_hop_acc']:.3f}(ratio={ratio(arm_c_result['mean_per_hop_acc']):.3f}) "
        f"verify_C={arm_c_cleanup_stats['verify_rate']:.3f} "
        f"hop_off={max_hop_off:.6f} ent_off={max_ent_off:.6f} cross={max_cross:.6f} "
        f"({elapsed:.1f}s)",
        flush=True,
    )

    return {
        "seed":                      seed,
        "N":                         N_use,
        "M_steps":                   M_steps,
        "n_chains":                  n_chains,
        "elapsed_s":                 elapsed,
        "hadamard_hop_max_off_diag": round(max_hop_off, 8),
        "hadamard_ent_max_off_diag": round(max_ent_off, 8),
        "hadamard_cross_max":        round(max_cross, 8),
        "hop_entity_sim_mean":       round(hop_entity_sim, 6),
        "baseline":                  baseline_result,
        "rand":                      rand_result,
        "arm_a_4way":                {"retrieval": arm_a_result, "audit": arm_a_audit},
        "arm_b_cleanup":             {"retrieval": arm_b_result,
                                      "cleanup_stats": arm_b_cleanup_stats},
        "arm_c_combined":            {"retrieval": arm_c_result,
                                      "cleanup_stats": arm_c_cleanup_stats},
    }


def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME",
                          "reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384")
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    PROT-018 binding: N_FULL == 16384.
    Formula self-tests:
      1. Hadamard rows in {-1, +1}.
      2. h_i . h_j = 0 for i != j (exact). h_i . h_i = N.
      3. Hop rows and entity rows use distinct row indices -> also orthogonal.
      4. 4-way unbinding: h^2=1, k^2=1 per {-1,+1} -> r recovered.
      5. Verdict gates work correctly (imported from v1).
      6. Live smoke: all metrics non-null, validity filter passes >= 1 hop.
    """
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"
    assert len(SEEDS_FULL) == 5, f"Expected 5 seeds, got {len(SEEDS_FULL)}"
    assert ENTITY_ROW_OFFSET == N_HOP_ID_CODEWORDS, \
        f"ENTITY_ROW_OFFSET={ENTITY_ROW_OFFSET} must equal N_HOP_ID_CODEWORDS={N_HOP_ID_CODEWORDS}"

    device = torch.device("cpu")
    N_st = 64   # power of 2

    # Formula self-test 1+2: Hadamard properties
    H_hop = make_hadamard_codebook(N_st, N_HOP_ID_CODEWORDS, HOP_ROW_OFFSET, device)
    assert H_hop.shape == (N_HOP_ID_CODEWORDS, N_st), \
        f"Hadamard hop shape mismatch: {H_hop.shape}"
    vals_hop = set(H_hop.view(-1).tolist())
    assert vals_hop.issubset({-1.0, 1.0}), f"Hadamard hop entries not in {{-1,+1}}: {vals_hop}"
    h0h1 = float((H_hop[0] * H_hop[1]).sum().item())
    assert abs(h0h1) < 1e-5, f"Hadamard hop h0.h1 = {h0h1} (expected 0)"
    h0h0 = float((H_hop[0] * H_hop[0]).sum().item())
    assert abs(h0h0 - N_st) < 1e-5, f"Hadamard hop h0.h0 = {h0h0} (expected {N_st})"
    print(f"[selftest] formula-1,2 Hadamard hop PASS: h0.h1={h0h1} h0.h0={h0h0}", flush=True)

    # Hadamard entity codebook (use small D for test)
    n_ent_test = min(5, N_ENTITY_CODEWORDS)
    H_ent = make_hadamard_codebook(N_st, n_ent_test, ENTITY_ROW_OFFSET, device)
    assert H_ent.shape == (n_ent_test, N_st), \
        f"Hadamard entity shape mismatch: {H_ent.shape}"
    vals_ent = set(H_ent.view(-1).tolist())
    assert vals_ent.issubset({-1.0, 1.0}), f"Hadamard entity entries not in {{-1,+1}}: {vals_ent}"
    e0e1 = float((H_ent[0] * H_ent[1]).sum().item())
    assert abs(e0e1) < 1e-5, f"Hadamard entity e0.e1 = {e0e1} (expected 0)"
    print(f"[selftest] formula-1,2 Hadamard entity PASS: e0.e1={e0e1}", flush=True)

    # Formula self-test 3: hop and entity rows are orthogonal (distinct row indices)
    cross_st = (H_hop @ H_ent.T) / float(N_st)
    max_cross_st = float(cross_st.abs().max().item())
    assert max_cross_st < 1e-5, \
        f"Hadamard hop-entity cross not zero: {max_cross_st:.6f}"
    print(f"[selftest] formula-3 hop-entity cross={max_cross_st:.2e} (expected 0)",
          flush=True)

    # Formula self-test 4: 4-way unbinding with Hadamard hop + entity
    cb_st = make_hadamard_codebook(N_st, 8, ENTITY_ROW_OFFSET, device)  # use entity rows
    H_hop_sub = H_hop[:4]
    r_vec = cb_st[0]; k1 = cb_st[1]; k2 = cb_st[2]; h = H_hop_sub[0]
    k_step = r_vec * k1 * k2 * h
    r_rec  = k_step * k1 * k2 * h
    conf   = float((r_rec * r_vec).sum().item()) / float(N_st)
    assert abs(conf - 1.0) < 1e-5, f"4-way Hadamard double unbinding failed: conf={conf}"
    print(f"[selftest] formula-4 4-way double Hadamard unbinding PASS: conf={conf:.6f}",
          flush=True)

    # Verdict gate check
    hp_per_seed = [{
        "seed": s, "N": N_FULL, "M_steps": 500, "n_chains": 5, "elapsed_s": 1.0,
        "hadamard_hop_max_off_diag": 0.0, "hadamard_ent_max_off_diag": 0.0,
        "hadamard_cross_max": 0.0, "hop_entity_sim_mean": 0.0,
        "baseline": {"mean_per_hop_acc": 0.97, "n_hops_evaluated": 100, "n_correct": 97},
        "rand":     {"mean_per_hop_acc": 0.50, "n_hops_evaluated": 100, "n_correct": 50},
        "arm_a_4way": {
            "retrieval":  {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 100, "n_correct": 99},
            "audit": {"mean_conf": 1.0, "frac_above_hp": 1.0, "frac_below_hf": 0.0, "n_checked": 100},
        },
        "arm_b_cleanup": {
            "retrieval":     {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 100, "n_correct": 99},
            "cleanup_stats": {"verify_rate": 1.0, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 100},
        },
        "arm_c_combined": {
            "retrieval":     {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 100, "n_correct": 99},
            "cleanup_stats": {"verify_rate": 0.98, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 100},
        },
    } for s in SEEDS_FULL]
    v, msg = compute_verdict(hp_per_seed)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    hf_per_seed = [{
        "seed": s, "N": N_FULL, "M_steps": 500, "n_chains": 5, "elapsed_s": 1.0,
        "hadamard_hop_max_off_diag": 0.0, "hadamard_ent_max_off_diag": 0.0,
        "hadamard_cross_max": 0.0, "hop_entity_sim_mean": 0.0,
        "baseline": {"mean_per_hop_acc": 0.47, "n_hops_evaluated": 100, "n_correct": 47},
        "rand":     {"mean_per_hop_acc": 0.50, "n_hops_evaluated": 100, "n_correct": 50},
        "arm_a_4way": {
            "retrieval":  {"mean_per_hop_acc": 0.47, "n_hops_evaluated": 100, "n_correct": 47},
            "audit": {"mean_conf": 0.5, "frac_above_hp": 0.3, "frac_below_hf": 0.1, "n_checked": 100},
        },
        "arm_b_cleanup": {
            "retrieval":     {"mean_per_hop_acc": 0.47, "n_hops_evaluated": 100, "n_correct": 47},
            "cleanup_stats": {"verify_rate": 0.9, "mean_snap_sim": 0.9, "n_borderline": 5, "n_total": 100},
        },
        "arm_c_combined": {
            "retrieval":     {"mean_per_hop_acc": 0.47, "n_hops_evaluated": 100, "n_correct": 47},
            "cleanup_stats": {"verify_rate": 0.9, "mean_snap_sim": 0.9, "n_borderline": 5, "n_total": 100},
        },
    } for s in SEEDS_FULL]
    v, msg = compute_verdict(hf_per_seed)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Live smoke: N_SMOKE, N_CHAINS_SMOKE
    N_smoke_st = N_SMOKE  # from v1
    smoke_result = run_one_seed_double_orthogonal(
        N_use=N_smoke_st, n_chains=N_CHAINS_SMOKE, seed=17, device=device)
    assert smoke_result["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] >= 0.0, \
        "arm_c acc is negative"
    assert smoke_result["arm_c_combined"]["retrieval"]["n_hops_evaluated"] >= 1, \
        "validity filter eliminated all cells at smoke scale"
    assert smoke_result["hadamard_hop_max_off_diag"] < 1e-4, \
        f"smoke Hadamard hop off-diag too large: {smoke_result['hadamard_hop_max_off_diag']}"
    assert smoke_result["hadamard_ent_max_off_diag"] < 1e-4, \
        f"smoke Hadamard entity off-diag too large: {smoke_result['hadamard_ent_max_off_diag']}"
    assert smoke_result["hadamard_cross_max"] < 1e-4, \
        f"smoke Hadamard cross not zero: {smoke_result['hadamard_cross_max']}"
    print(
        f"[selftest] reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384 PASS "
        f"smoke N={N_smoke_st} "
        f"C_acc={smoke_result['arm_c_combined']['retrieval']['mean_per_hop_acc']:.3f} "
        f"C_verify={smoke_result['arm_c_combined']['cleanup_stats']['verify_rate']:.3f} "
        f"hop_off={smoke_result['hadamard_hop_max_off_diag']:.2e} "
        f"ent_off={smoke_result['hadamard_ent_max_off_diag']:.2e} "
        f"cross={smoke_result['hadamard_cross_max']:.2e}",
        flush=True,
    )


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke",     action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")   # PROT-022
    smoke  = args.smoke or os.environ.get("HDLAB_SMOKE", "0") == "1"
    N_cfg  = N_SMOKE        if smoke else N_FULL
    n_ch   = N_CHAINS_SMOKE if smoke else N_CHAINS_FULL
    seeds  = SEEDS_SMOKE    if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()

    print(
        f"[run] reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384 "
        f"smoke={smoke} N={N_cfg} n_chains={n_ch} seeds={seeds} "
        f"done={len(done)} device={device.type} "
        f"[DOUBLE-DELTA Hadamard: hop D={N_HOP_ID_CODEWORDS} + entity D={N_ENTITY_CODEWORDS}]",
        flush=True,
    )

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body)
                print(f"  [ckpt] seed={seed} resumed", flush=True)
                continue
        result = run_one_seed_double_orthogonal(N_cfg, n_ch, seed, device)
        write_partial_key(out_dir, ck, result)
        per_seed.append(result)

    verdict, vm = compute_verdict(per_seed)
    elapsed     = round(time.time() - t0, 2)

    if per_seed:
        arm_c_accs = [s["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] for s in per_seed]
        rand_accs  = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
        if all(a == 0.0 for a in arm_c_accs + rand_accs):
            print("[INSTRUMENTATION_SUSPECT] all per-hop accuracies are 0.0 -- "
                  "possible retrieval bug", flush=True)

    summary = {
        "anchor":           "reasoning_storage_4way_cleanup_v4_double_orthogonal_v1_n16384",
        "N":                N_cfg,
        "smoke":            smoke,
        "n_chains":         n_ch,
        "seeds":            seeds,
        "n_seeds":          len(seeds),
        "hop_construction": "hadamard_orthogonal",
        "entity_construction": "hadamard_orthogonal",
        "double_delta":     True,
        "hop_row_offset":   HOP_ROW_OFFSET,
        "entity_row_offset": ENTITY_ROW_OFFSET,
        "per_seed":         per_seed,
        "verdict":          verdict,
        "verdict_msg":      vm,
        "elapsed_s":        elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"[verdict] {verdict}: {vm}", flush=True)
    print(f"[done] elapsed={elapsed}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    main()
