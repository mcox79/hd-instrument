"""REASONING STORAGE 4-WAY CLEANUP v3 -- HADAMARD ORTHOGONAL HOP CODEWORDS at N=16384.

CONTEXT (v2 BORDERLINE-OVER-CLAIM #167; Hadamard orthogonalization closes deficit):
  v2 landed BORDERLINE-OVER-CLAIM: mean ratio 2.4pp above random (barely above 2.0pp
  strict HP gate; 4 of 5 seeds at strict-borderline).
  Research routing note identified "hop_id codebook orthogonality" as open tuning
  question: "drill B Axis 1 self-binding pathology check ... Optional refinement:
  Hadamard or Gram-Schmidt orthogonalization (drill B open question 3)".

  v3 hypothesis: random-draw BSC hop codewords have O(sqrt(N)) cross-correlations
  that add systematic noise to the 4-way binding. Hadamard-orthogonal D=10 hop
  codewords guarantee ZERO cross-correlation (exact orthogonality), closing the
  +0.4pp deficit.

HADAMARD CONSTRUCTION:
  D=10 hop codewords. N=16384 = 2^14. We need 10 orthogonal rows.
  Use the first 10 rows of the Walsh-Hadamard matrix H_{16384}.
  H_{2^k} is constructed recursively: H_1 = [1]; H_{2^k} = kron(H_2, H_{2^(k-1)}).
  Rows 0..9 of H_{16384} are perfectly orthogonal over {-1, +1}.
  Normalized to unit norm: each row has norm sqrt(N). Inner product between
  distinct rows = 0 (exact, not statistical).

  Key property for self-binding check:
  h_i . h_j = 0 for i != j (exact, vs O(sqrt(N)) for random BSC).
  h_i . entity_j: Hadamard rows have exact orthogonality to EACH OTHER but
  independence from entity/rule/relation codebooks (which are random BSC).
  Cross-product with random BSC: E[h_hadamard . e_bsc] = 0 (same as random, but
  with fixed, known structure).

  FORMULA SELF-TEST: h_0 . h_1 = 0; h_i . h_i = N (exact).

SINGLE DELTA ENGINEERING vs v2:
  Only change: cb_hop from make_bsc_codebook(N, D=10, seed+3) to
  make_hadamard_codebook(N, D=10).
  All other arms (A=4-way alone, B=cleanup alone, C=combined) identical to v2.
  3 ablation arms preserved for direct comparability with v2.

SCIENTIFIC QUESTION:
  Does Hadamard-orthogonal hop codeword construction close the +0.4pp borderline
  deficit to achieve mean ratio >= 0.98 (HP gate) on 5 seeds?

PRE-REGISTERED BANDS (identical to v2 / v1):
  Arm C (combined 4-way + cleanup) -- PRIMARY:
    HARD-PASS  : mean structured-key accuracy ratio >= 0.98 (gap < 2%);
                 ALL 5 seeds pass; cleanup verification rate >= 0.95.
    HARD-FAIL  : mean ratio < 0.96.
    MIDDLE-BAND: mean ratio 0.96-0.98 (partial closure; residual gap).

  Differential interpretation vs v2:
    If v3 >= HP and v2 was MIDDLE: Hadamard orthogonality was causal for gap.
    If v3 remains MIDDLE: gap source is elsewhere (capacity, chain depth, etc).
    If v3 is HF: Hadamard construction introduces interference (unexpected).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.
PROT-021: per-seed checkpointing.
PROT-022: device=cpu forced.

OOM CHECK: identical to v1/v2. N=16384 W = 1 GB. Remote CPU 64 GB RAM. OK.

TIMEOUT ESTIMATE:
  v2 elapsed ~5 min for 5 seeds (estimated 33s/seed). Hadamard adds tiny overhead
  (one matrix multiply for first 10 rows, done once). Same budget as v2.
  ceil(1.5 * 180) = 270s. PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. Hadamard H_{2^k}: H_{2^k} = kron([[1,1],[1,-1]], H_{2^(k-1)}).
     H_1 = [[1]]; H_2 = [[1,1],[1,-1]]; H_4 rows all orthogonal.
  2. Row orthogonality: h_0.h_1 = 0 (inner product = 0, exact).
  3. Row self-inner-product: h_0.h_0 = N (norm^2 = N).
  4. 4-way unbinding exact for Hadamard hop (same BSC algebra: h_i^2 = 1 per entry
     when normalized to {-1,+1}; need to verify Hadamard entries are {-1,+1}).
  5. Verdict gates HP/HF/MB work correctly.

Anchor: reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384
Queue: remote_cpu_queue (CPU-only)
Pre-reg: preregs/2026-06-01_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384.md
Total cells: 5 seeds x 3 arms = 15 arm evaluations
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ============================================================
# PROT-018: _n16384 binds N = 16384
# ============================================================
N_FULL  = 16384
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# Load v1 module to reuse ALL scientific functions except hop codebook construction
_v1_path = REPO / "experiments" / "exp_reasoning_storage_4way_cleanup_v1_n16384.py"
_v1_spec = importlib.util.spec_from_file_location("rs4w_v1_for_v3", _v1_path)
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
# v3 config: 5 seeds + Hadamard hop codebook
# ============================================================
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def make_hadamard_codebook(N: int, D: int, device: torch.device) -> torch.Tensor:
    """Build D x N Hadamard-orthogonal hop codewords.

    Uses first D rows of the Walsh-Hadamard matrix H_N.
    N must be a power of 2 and D <= N.
    Entries are {-1, +1} (same as BSC), so 4-way unbinding algebra is IDENTICAL
    to random BSC (each entry squares to 1), but cross-correlations h_i.h_j = 0
    for i != j (exact, vs O(sqrt(N)) for random BSC).

    Construction: H_{2^k} = kron([[1,1],[1,-1]], H_{2^(k-1)}).
    Row i of H_N encodes the i-th Rademacher function (i in binary selects sign flips).
    We use the natural Sylvester construction for efficiency.
    """
    assert (N & (N - 1)) == 0, f"N must be power of 2; got {N}"
    assert D <= N, f"D={D} > N={N}"

    # Build full H_N on CPU efficiently using the property:
    # H_N[i, j] = (-1)^(popcount(i & j)) for i, j in {0..N-1}
    # But for D=10 << N=16384 we only need the first D rows.
    # Efficient: build first D rows iteratively.
    # Row i of H_{2^k}: H[i, j] = (-1)^(popcount(i & j))
    # We compute this via the recursive Sylvester structure.

    # Build D x N matrix row by row
    rows = []
    j_idx = torch.arange(N, dtype=torch.long)  # [0, 1, ..., N-1]
    for i in range(D):
        # H[i, j] = (-1)^popcount(i & j)
        # popcount(i & j) for fixed i: precompute for all j
        bitwise_and = i & j_idx.numpy()  # use numpy for bit ops
        # popcount: count bits in each element
        import numpy as np
        popcount = torch.tensor(
            [bin(int(x)).count('1') for x in bitwise_and],
            dtype=torch.float32
        )
        row = (-1.0) ** popcount   # (-1)^popcount in {-1, +1}
        rows.append(row.unsqueeze(0))

    H = torch.cat(rows, dim=0).to(device)  # (D, N)
    # Verify: entries should be {-1, +1}
    assert H.abs().max().item() == 1.0, "Hadamard entries not in {-1, +1}"
    return H


def run_one_seed_hadamard(
    N_use: int,
    n_chains: int,
    seed: int,
    device: torch.device,
) -> Dict:
    """Run 3 arms with Hadamard-orthogonal hop codewords (single delta vs v1/v2)."""
    t0 = time.time()

    # Build codebooks -- same as v1 EXCEPT cb_hop uses Hadamard construction
    cb_rule    = make_bsc_codebook(N_use, N_RULE_CODEWORDS, seed + 0, device)
    cb_entity  = make_bsc_codebook(N_use, N_ENTITY_CODEWORDS, seed + 1, device)
    cb_rel     = make_bsc_codebook(N_use, N_RELATION_CODEWORDS, seed + 2, device)
    # HADAMARD: replace random-draw BSC hop codewords with Hadamard-orthogonal
    cb_hop = make_hadamard_codebook(N_use, N_HOP_ID_CODEWORDS, device)

    # Verify Hadamard orthogonality (formula self-test at runtime)
    gram = (cb_hop @ cb_hop.T) / float(N_use)
    gram_diag = gram.diag()
    gram_off  = gram - torch.diag(gram_diag)
    max_off_diag = float(gram_off.abs().max().item())
    assert abs(float(gram_diag.mean().item()) - 1.0) < 1e-4, \
        f"Hadamard norm not 1: {gram_diag.mean().item():.6f}"
    assert max_off_diag < 1e-4, \
        f"Hadamard off-diagonal not zero: max_off={max_off_diag:.6f}"

    # Spot check independence from entity codebook (should be ~0, statistical)
    hop_entity_sim = float((cb_hop @ cb_entity.T).abs().mean().item()) / float(N_use)

    # --- Baseline: 3-way structured corpus ---
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

    # --- Arm A: 4-way binding only (uses Hadamard cb_hop) ---
    keys_4w, vals_4w = make_4way_corpus(
        cb_rule, cb_entity, cb_rel, cb_hop, chain_meta, device)
    W_4w = build_W_from_corpus(keys_4w, vals_4w, N_use)
    arm_a_result = retrieval_accuracy(
        W_4w, keys_4w, chain_meta, cb_entity, N_use, n_probe, seed + 2000)
    arm_a_audit = audit_4way_encoding(
        cb_rule, cb_entity, cb_rel, cb_hop, keys_4w, chain_meta, N_use, n_audit=100)

    # --- Arm B: 3-way + cleanup ---
    keys_3wc, vals_3wc, audit_b = make_3way_cleanup_corpus(
        cb_rule, cb_entity, cb_rel, chain_meta, device)
    W_3wc = build_W_from_corpus(keys_3wc, vals_3wc, N_use)
    arm_b_result = retrieval_accuracy(
        W_3wc, keys_3wc, chain_meta, cb_entity, N_use, n_probe, seed + 3000)
    arm_b_cleanup_stats = cleanup_audit_stats(audit_b)

    # --- Arm C: 4-way + cleanup (primary; uses Hadamard cb_hop) ---
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
        f"hadamard_max_off={max_off_diag:.6f} "
        f"hop_entity_sim={hop_entity_sim:.5f} "
        f"({elapsed:.1f}s)",
        flush=True,
    )

    return {
        "seed":                 seed,
        "N":                    N_use,
        "M_steps":              M_steps,
        "n_chains":             n_chains,
        "elapsed_s":            elapsed,
        "hadamard_max_off_diag": round(max_off_diag, 8),
        "hop_entity_sim_mean":  round(hop_entity_sim, 6),
        "baseline":             baseline_result,
        "rand":                 rand_result,
        "arm_a_4way":           {"retrieval": arm_a_result, "audit": arm_a_audit},
        "arm_b_cleanup":        {"retrieval": arm_b_result, "cleanup_stats": arm_b_cleanup_stats},
        "arm_c_combined":       {"retrieval": arm_c_result, "cleanup_stats": arm_c_cleanup_stats},
    }


def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME",
                          "reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384")
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    PROT-018 binding: N_FULL == 16384.
    Formula self-tests:
      1. Hadamard rows are in {-1, +1}.
      2. H orthogonality: h_0.h_1 = 0 (exact).
      3. H norm: h_0.h_0 = N (exact).
      4. 4-way unbinding exact for Hadamard (h^2 = 1 per entry -> same as BSC).
      5. Verdict gates work correctly (imported from v1).
      6. Live smoke forward pass with Hadamard hop: metrics non-null.
    """
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"
    assert len(SEEDS_FULL) == 5, f"Expected 5 seeds, got {len(SEEDS_FULL)}"

    device = torch.device("cpu")
    N_st = 64   # power of 2 for Hadamard test

    # Formula self-test 1+2+3: Hadamard properties
    H_st = make_hadamard_codebook(N_st, N_HOP_ID_CODEWORDS, device)
    assert H_st.shape == (N_HOP_ID_CODEWORDS, N_st), \
        f"Hadamard shape mismatch: {H_st.shape}"
    # Entries in {-1, +1}
    vals = set(H_st.view(-1).tolist())
    assert vals.issubset({-1.0, 1.0}), f"Hadamard entries not in {{-1,+1}}: {vals}"
    # Row 0 . row 1 = 0
    h0h1 = float((H_st[0] * H_st[1]).sum().item())
    assert abs(h0h1) < 1e-5, f"Hadamard h0.h1 = {h0h1} (expected 0)"
    # Row 0 . row 0 = N
    h0h0 = float((H_st[0] * H_st[0]).sum().item())
    assert abs(h0h0 - N_st) < 1e-5, f"Hadamard h0.h0 = {h0h0} (expected {N_st})"
    print(f"[selftest] formula-1,2,3 Hadamard PASS: h0.h1={h0h1} h0.h0={h0h0}", flush=True)

    # Formula self-test 4: 4-way unbinding with Hadamard hop
    cb_st = make_bsc_codebook(N_st, 10, 42, device)
    H_sub = H_st[:4]  # use first 4 rows
    r_vec = cb_st[0]; k1 = cb_st[1]; k2 = cb_st[2]; h = H_sub[0]
    k_step = r_vec * k1 * k2 * h
    r_rec  = k_step * k1 * k2 * h   # unbind: k1^2=k2^2=h^2=1 -> r
    conf   = float((r_rec * r_vec).sum().item()) / float(N_st)
    assert abs(conf - 1.0) < 1e-5, f"4-way Hadamard unbinding failed: conf={conf}"
    print(f"[selftest] formula-4 4-way Hadamard unbinding PASS: conf={conf:.6f}", flush=True)

    # Verdict gate check (imported from v1 -- identical thresholds)
    hp_per_seed = [{
        "seed": s, "N": N_FULL, "M_steps": 500, "n_chains": 5, "elapsed_s": 1.0,
        "hadamard_max_off_diag": 0.0, "hop_entity_sim_mean": 0.0,
        "baseline": {"mean_per_hop_acc": 0.97, "n_hops_evaluated": 100, "n_correct": 97},
        "rand":     {"mean_per_hop_acc": 0.50, "n_hops_evaluated": 100, "n_correct": 50},
        "arm_a_4way": {
            "retrieval":  {"mean_per_hop_acc": 0.98, "n_hops_evaluated": 100, "n_correct": 98},
            "audit": {"mean_conf": 1.0, "frac_above_hp": 1.0, "frac_below_hf": 0.0, "n_checked": 100},
        },
        "arm_b_cleanup": {
            "retrieval":      {"mean_per_hop_acc": 0.98, "n_hops_evaluated": 100, "n_correct": 98},
            "cleanup_stats":  {"verify_rate": 1.0, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 100},
        },
        "arm_c_combined": {
            "retrieval":     {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 100, "n_correct": 99},
            "cleanup_stats": {"verify_rate": 0.98, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 100},
        },
    } for s in SEEDS_FULL]
    v, msg = compute_verdict(hp_per_seed)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # HF gate: ratio = arm_c_acc / rand_acc < HF_RATIO_C=0.96
    # Use rand=0.50, arm_c_acc=0.47 -> ratio=0.94 < 0.96 -> HARD_FAIL
    hf_per_seed = [{
        "seed": s, "N": N_FULL, "M_steps": 500, "n_chains": 5, "elapsed_s": 1.0,
        "hadamard_max_off_diag": 0.0, "hop_entity_sim_mean": 0.0,
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

    # Live smoke: small N, smoke scale
    N_smoke_st = N_SMOKE  # = 512 from v1
    smoke_result = run_one_seed_hadamard(
        N_use=N_smoke_st, n_chains=N_CHAINS_SMOKE, seed=17,
        device=device)
    assert smoke_result["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] >= 0.0, \
        "arm_c acc is negative"
    assert smoke_result["arm_c_combined"]["retrieval"]["n_hops_evaluated"] > 0, \
        "no hops evaluated in smoke"
    assert smoke_result["hadamard_max_off_diag"] < 1e-4, \
        f"smoke Hadamard off-diag too large: {smoke_result['hadamard_max_off_diag']}"
    # Validity filter: n_hops >= 1 (filter passes at least one item)
    assert smoke_result["arm_c_combined"]["retrieval"]["n_hops_evaluated"] >= 1, \
        "validity filter eliminated all cells at smoke scale"
    print(
        f"[selftest] reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384 PASS "
        f"smoke N={N_smoke_st} "
        f"C_acc={smoke_result['arm_c_combined']['retrieval']['mean_per_hop_acc']:.3f} "
        f"C_verify={smoke_result['arm_c_combined']['cleanup_stats']['verify_rate']:.3f} "
        f"hadamard_off={smoke_result['hadamard_max_off_diag']:.2e}",
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
        f"[run] reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384 "
        f"smoke={smoke} N={N_cfg} n_chains={n_ch} seeds={seeds} "
        f"done={len(done)} device={device.type} "
        f"[HADAMARD orthogonal hop codewords; D={N_HOP_ID_CODEWORDS}]",
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
        result = run_one_seed_hadamard(N_cfg, n_ch, seed, device)
        write_partial_key(out_dir, ck, result)
        per_seed.append(result)

    verdict, vm = compute_verdict(per_seed)
    elapsed     = round(time.time() - t0, 2)

    # Suspicious-result gate
    if per_seed:
        arm_c_accs = [s["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] for s in per_seed]
        rand_accs  = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
        if all(a == 0.0 for a in arm_c_accs + rand_accs):
            print("[INSTRUMENTATION_SUSPECT] all per-hop accuracies are 0.0 -- "
                  "possible retrieval bug", flush=True)

    summary = {
        "anchor":      "reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384",
        "N":           N_cfg,
        "smoke":       smoke,
        "n_chains":    n_ch,
        "seeds":       seeds,
        "n_seeds":     len(seeds),
        "hop_construction": "hadamard_orthogonal",
        "per_seed":    per_seed,
        "verdict":     verdict,
        "verdict_msg": vm,
        "elapsed_s":   elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"[verdict] {verdict}: {vm}", flush=True)
    print(f"[done] elapsed={elapsed}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    main()
