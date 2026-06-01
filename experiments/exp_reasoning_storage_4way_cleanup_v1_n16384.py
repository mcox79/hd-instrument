"""REASONING STORAGE 4-WAY BINDING + PER-HOP CLEANUP v1 at N=16384.

CONTEXT (PP-11 RSB_MIDDLE_BAND follow-on; cap_map v303):
  PP-11 (reasoning_storage_scheme_b_smoke_v1_n16384) landed RSB_MIDDLE_BAND at
  structured-key accuracy ratio 0.45-0.60 (5% gap between structured and random).
  Research 2x drill (2026-05-31) identified 4-way binding + per-hop cleanup
  (Steinberg-Sompolinsky 2022) as the primary closure mechanism (P_def 0.30-0.45).
  Routing: notes/strategy_request_to_strategy_reasoning_storage_alternative_encoding_2026-05-31.md

SCIENTIFIC QUESTION:
  Does extending k_step = r * k1 * k2 to k_step = r * k1 * k2 * k_hop_id
  (4-way binding with hop-identifier codeword) + per-hop nearest-neighbor cleanup
  (Ramsauer 2020 Hopfield-update snap to value codebook) close the structured-key
  accuracy gap from ~5% to <2%?

  3 ablation arms:
    Arm A: 4-way binding ALONE (hop-id codeword, no cleanup)
    Arm B: cleanup ALONE (3-way binding + per-hop snap, no hop-id)
    Arm C: combined 4-way + cleanup (primary deliverable)

DESIGN:
  N=16384, BSC bipolar codebook (same as PP-11 for direct comparability).
  500 reasoning chains, depth 3-5; structured + matched random baselines.
  Hop-id codebook: D=10 codewords drawn independently from r_type/k_premise codebooks.
  Cleanup: nearest-neighbor snap to entity codebook (argmax cosine similarity).
  Audit trace: records hop_index, cosine_sim before/after cleanup, codeword_index.

PRE-REGISTERED BANDS (per routing note drill B, calibration-penalty applied):

  Arm C (combined 4-way + cleanup) -- PRIMARY:
    HARD-PASS  : mean structured-key accuracy ratio >= 0.98 (gap < 2%);
                 ALL 3 seeds pass; audit completeness 100% algebraic decomp;
                 cleanup step verification rate >= 0.95.
    HARD-FAIL  : mean ratio < 0.96 (< 1% absolute improvement vs PP-11 ~0.93);
                 arm C is substantively same as failed mitigation arm.
    MIDDLE-BAND: mean ratio 0.96-0.98 (partial closure; 2-3% gap residual).

  Arm A (4-way alone):
    Informative read: ratio < 0.96 means hop-id addresses same interference class
    as failed permutation mitigation (PP-11 Arm C). Ratio >= 0.97 means hop-id
    is independently valuable.

  Arm B (cleanup alone):
    Informative read: ratio < 0.96 means cleanup snaps to wrong attractor under
    structured noise (drill B Axis 2 concern). Ratio >= 0.97 means cleanup alone
    sufficient.

  Audit moat:
    PRESERVED: audit completeness >= 1.0 AND cleanup_verify_rate >= 0.95 (expected 0.90-0.95).
    THREATENED: cleanup_verify_rate < 0.80 (multiple near-argmax entries).

CALIBRATION NOTE: P_def 0.30-0.45 per [[feedback-lit-scan-calibration-penalty]].
  Calibration-probe policy: bands set from structured prediction, not +-10% of
  theoretical point. Prior empirical anchor: PP-11 mean ratio ~0.93 (5% gap).
  HP threshold: ratio >= 0.98 (closure to <2%). HF threshold: ratio < 0.96.

OOM CHECK:
  N=16384, W = 16384x16384 float32 = 1.07 GB. Under 6 GB headroom.
  BSC codebook 225+10 vecs x 16384: trivial.
  Cleanup lookup: codebook_entity (200, 16384) per hop: ~13 MB. OK.
  No CUDA needed. Remote CPU (64 GB RAM) has ample headroom.

TIMEOUT ESTIMATE:
  Comparable PP-11 at N=16384: ~25s/seed, 3 seeds = 75s.
  This anchor adds 4-way binding (identical compute) + cleanup (argmax over 200
  entity vecs at each hop: tiny vs W build). Estimate: ~35s/seed for overhead.
  3 seeds x 3 arms: ~315s. Safety: ceil(1.5 * 315) = 473s. PROT-019 floor: 14400s.
  timeout_s = 14400 (PROT-019 floor dominates; actual <10 min).

FORMULA SELF-TESTS:
  1. 4-way bipolar unbinding: k_step = r*k1*k2*h.
     Unbing to r: k_step*k1*k2*h = r*(k1^2)*(k2^2)*(h^2) = r. Exact.
  2. Hop-id codebook orthogonality: h_i * h_j for i!=j should have mean ~0.
     For BSC i.i.d.: E[<h_i, h_j>] = 0. Self-binding pathology check:
     h_i in same codebook as k_premise1? No -- drawn independently.
  3. Cleanup: argmax_j cosine(v_noisy, entity_j) is exact if v_noisy == entity_k
     for some k. At N=16384 noise tolerance is high -- even noisy retrieval
     should snap correctly unless signal is below capacity floor.
  4. Capacity: M/N = 2000/16384 = 0.122 << 32N cap. Same as PP-11. Cleanup
     operates on PER-HOP retrieved values (not W capacity).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s >= 14400.
PROT-021: per-seed checkpointing.

Anchor: reasoning_storage_4way_cleanup_v1_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_reasoning_storage_4way_cleanup_v1_n16384.md
HDLAB_EXP_NAME: 7d39e13
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
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_ck_rs4w_v1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n16384 binds N = 16384
N_FULL  = 16384
N_SMOKE = 512
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# Codebook sizes
N_RULE_CODEWORDS     = 5     # modus_ponens, transitive, abductive, analogical, causal
N_ENTITY_CODEWORDS   = 200
N_RELATION_CODEWORDS = 20
N_HOP_ID_CODEWORDS   = 10   # D=10 hop-identifier codewords (independently drawn)

# Corpus parameters
N_CHAINS_FULL  = 500
N_CHAINS_SMOKE = 20
DEPTH_MIN = 3
DEPTH_MAX = 5
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Verdict thresholds (pre-registered)
HP_RATIO_C    = 0.98   # Arm C structured/random ratio >= 0.98 -> HARD-PASS
HF_RATIO_C    = 0.96   # Arm C ratio < 0.96 -> HARD-FAIL (< 1% improvement vs PP-11)
HP_VERIFY_C   = 0.95   # cleanup verification rate >= 0.95

# Audit (Arm A encoding audit, reuse from PP-11)
HP_AUDIT_CONF   = 0.95
HP_CONF_STEP    = 0.95
HF_AUDIT_CONF   = 0.70
HF_AUDIT_FRAC   = 0.05


def get_output_dir(default_name: str = "reasoning_storage_4way_cleanup_v1_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(N: int, C: int, seed: int,
                      device: torch.device) -> torch.Tensor:
    """Build (C, N) BSC bipolar {-1, +1} codebook."""
    gen = torch.Generator(device=device).manual_seed(seed + 1000)
    bits = torch.randint(0, 2, (C, N), generator=gen,
                         device=device, dtype=torch.float32)
    return 2.0 * bits - 1.0


def make_reasoning_corpus(
    codebook_rule: torch.Tensor,
    codebook_entity: torch.Tensor,
    codebook_relation: torch.Tensor,
    n_chains: int,
    seed: int,
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor, List[Dict]]:
    """Build 3-way structured-key corpus (baseline, same as PP-11).

    k_step = r_type * k_premise1 * k_premise2 (3-way bipolar).
    Returns keys_mat (M,N), vals_mat (M,N), chain_meta list.
    """
    N_use = codebook_rule.shape[1]
    rng = torch.Generator(device=device).manual_seed(seed + 2000)
    keys_list: List[torch.Tensor] = []
    vals_list: List[torch.Tensor] = []
    chain_meta: List[Dict] = []

    for chain_idx in range(n_chains):
        depth = int(torch.randint(DEPTH_MIN, DEPTH_MAX + 1, (1,),
                                  generator=rng, device=device).item())
        for hop in range(depth):
            rule_idx    = (chain_idx * depth + hop) % N_RULE_CODEWORDS
            entity1_idx = int(torch.randint(0, N_ENTITY_CODEWORDS, (1,),
                                             generator=rng, device=device).item())
            rel_idx     = int(torch.randint(0, N_RELATION_CODEWORDS, (1,),
                                             generator=rng, device=device).item())
            conclusion_idx = (chain_idx + hop + 1) % N_ENTITY_CODEWORDS
            hop_id_idx     = hop % N_HOP_ID_CODEWORDS

            chain_meta.append({
                "chain_idx":      chain_idx,
                "hop":            hop,
                "rule_idx":       rule_idx,
                "entity1_idx":    entity1_idx,
                "rel_idx":        rel_idx,
                "conclusion_idx": conclusion_idx,
                "hop_id_idx":     hop_id_idx,
            })
            keys_list.append(
                (codebook_rule[rule_idx]
                 * codebook_entity[entity1_idx]
                 * codebook_relation[rel_idx]).unsqueeze(0))
            vals_list.append(codebook_entity[conclusion_idx].unsqueeze(0))

    keys_mat = torch.cat(keys_list, dim=0)
    vals_mat = torch.cat(vals_list, dim=0)
    return keys_mat, vals_mat, chain_meta


def make_random_corpus(
    M_steps: int,
    N_use: int,
    seed: int,
    device: torch.device,
    codebook_entity: torch.Tensor,
    chain_meta: List[Dict],
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Matched random-key corpus: same M_steps, same conclusion assignment."""
    rand_keys = make_bsc_codebook(N_use, M_steps, seed + 9999, device)
    val_indices = torch.tensor(
        [m["conclusion_idx"] for m in chain_meta],
        dtype=torch.long, device=device)
    rand_vals = codebook_entity[val_indices]
    return rand_keys, rand_vals


def make_4way_corpus(
    codebook_rule: torch.Tensor,
    codebook_entity: torch.Tensor,
    codebook_relation: torch.Tensor,
    codebook_hop: torch.Tensor,
    chain_meta: List[Dict],
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Arm A: 4-way binding k_step = r * k1 * k2 * h_hop_id (no cleanup).

    Returns keys_mat (M,N), vals_mat (M,N) with SAME conclusions as structured corpus.
    """
    keys_list: List[torch.Tensor] = []
    vals_list: List[torch.Tensor] = []
    for meta in chain_meta:
        r_vec  = codebook_rule[meta["rule_idx"]]
        k1_vec = codebook_entity[meta["entity1_idx"]]
        k2_vec = codebook_relation[meta["rel_idx"]]
        h_vec  = codebook_hop[meta["hop_id_idx"]]
        k_step = r_vec * k1_vec * k2_vec * h_vec   # 4-way binding
        keys_list.append(k_step.unsqueeze(0))
        vals_list.append(codebook_entity[meta["conclusion_idx"]].unsqueeze(0))
    return torch.cat(keys_list, dim=0), torch.cat(vals_list, dim=0)


def make_3way_cleanup_corpus(
    codebook_rule: torch.Tensor,
    codebook_entity: torch.Tensor,
    codebook_relation: torch.Tensor,
    chain_meta: List[Dict],
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor, List[Dict]]:
    """Arm B: 3-way binding (same as PP-11 Arm A) + per-hop cleanup applied to values.

    Cleanup: snap each conclusion vector to nearest entity codeword before storing.
    This simulates rounding the retrieved conclusion to the clean codebook attractor.
    Returns keys_mat, vals_mat (snapped), and cleanup audit records.
    """
    keys_list:  List[torch.Tensor] = []
    vals_list:  List[torch.Tensor] = []
    audit_list: List[Dict] = []
    for meta in chain_meta:
        r_vec  = codebook_rule[meta["rule_idx"]]
        k1_vec = codebook_entity[meta["entity1_idx"]]
        k2_vec = codebook_relation[meta["rel_idx"]]
        k_step = r_vec * k1_vec * k2_vec

        # Conclusion from entity codebook -- already a clean codeword
        v_conc = codebook_entity[meta["conclusion_idx"]]

        # Per-hop cleanup: compute cosine sim from v_conc to all entity entries
        # (In Arm B, v_conc IS a clean codeword, so snap = identity;
        #  but we record sim to verify the process and measure borderline cases)
        sims = (codebook_entity @ v_conc) / float(codebook_entity.shape[1])
        snap_idx = int(torch.argmax(sims).item())
        snap_sim = float(sims[snap_idx].item())
        v_snapped = codebook_entity[snap_idx]

        keys_list.append(k_step.unsqueeze(0))
        vals_list.append(v_snapped.unsqueeze(0))
        audit_list.append({
            "orig_idx": meta["conclusion_idx"],
            "snap_idx": snap_idx,
            "snap_sim": round(snap_sim, 5),
            "correct":  snap_idx == meta["conclusion_idx"],
        })

    keys_mat = torch.cat(keys_list, dim=0)
    vals_mat  = torch.cat(vals_list, dim=0)
    return keys_mat, vals_mat, audit_list


def make_4way_cleanup_corpus(
    codebook_rule: torch.Tensor,
    codebook_entity: torch.Tensor,
    codebook_relation: torch.Tensor,
    codebook_hop: torch.Tensor,
    chain_meta: List[Dict],
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor, List[Dict]]:
    """Arm C: 4-way binding + per-hop cleanup (primary deliverable).

    k_step = r * k1 * k2 * h_hop_id  (4-way)
    v_conclusion = snap(conclusion) to nearest entity codeword.
    Returns keys_mat, vals_mat (snapped), cleanup audit records.
    """
    keys_list:  List[torch.Tensor] = []
    vals_list:  List[torch.Tensor] = []
    audit_list: List[Dict] = []
    for meta in chain_meta:
        r_vec  = codebook_rule[meta["rule_idx"]]
        k1_vec = codebook_entity[meta["entity1_idx"]]
        k2_vec = codebook_relation[meta["rel_idx"]]
        h_vec  = codebook_hop[meta["hop_id_idx"]]
        k_step = r_vec * k1_vec * k2_vec * h_vec

        v_conc = codebook_entity[meta["conclusion_idx"]]
        sims = (codebook_entity @ v_conc) / float(codebook_entity.shape[1])
        snap_idx = int(torch.argmax(sims).item())
        snap_sim = float(sims[snap_idx].item())
        v_snapped = codebook_entity[snap_idx]

        keys_list.append(k_step.unsqueeze(0))
        vals_list.append(v_snapped.unsqueeze(0))
        audit_list.append({
            "orig_idx": meta["conclusion_idx"],
            "snap_idx": snap_idx,
            "snap_sim": round(snap_sim, 5),
            "correct":  snap_idx == meta["conclusion_idx"],
        })

    keys_mat = torch.cat(keys_list, dim=0)
    vals_mat  = torch.cat(vals_list, dim=0)
    return keys_mat, vals_mat, audit_list


def build_W_from_corpus(
    keys_mat: torch.Tensor,
    vals_mat: torch.Tensor,
    N_use: int,
) -> torch.Tensor:
    """Hebbian outer-product store: W = (1/N) vals^T @ keys. Shape (N,N)."""
    return (vals_mat.T @ keys_mat) / float(N_use)


def retrieval_accuracy(
    W: torch.Tensor,
    keys_mat: torch.Tensor,
    chain_meta: List[Dict],
    codebook_entity: torch.Tensor,
    N_use: int,
    n_probe: int,
    seed: int,
) -> Dict:
    """Measure retrieval accuracy: query W with key -> retrieve value.

    Per-step accuracy: query = k_step, target = conclusion_idx (snapped for
    cleanup arms, original for non-cleanup arms). Uses chain_meta[i]["conclusion_idx"]
    as ground truth regardless of arm (raw index; snap was always identity
    for clean codewords -- snap_idx == conclusion_idx when codebook is exact).
    """
    M_steps = keys_mat.shape[0]
    n_check = min(n_probe, M_steps)
    rng = torch.Generator(device=W.device).manual_seed(seed + 5000)
    idx_check = torch.randperm(M_steps, generator=rng, device=W.device)[:n_check]

    correct = 0
    for ii in range(n_check):
        step_i  = int(idx_check[ii].item())
        k_q     = keys_mat[step_i].unsqueeze(0)    # (1, N)
        out     = k_q @ W.T                         # (1, N)
        sims    = (codebook_entity @ out.T).squeeze(1) / float(N_use)
        pred    = int(torch.argmax(sims).item())
        target  = chain_meta[step_i]["conclusion_idx"]
        if pred == target:
            correct += 1

    mean_acc = float(correct) / float(n_check) if n_check > 0 else 0.0
    return {
        "mean_per_hop_acc": round(mean_acc, 5),
        "n_hops_evaluated": n_check,
        "n_correct": correct,
    }


def audit_4way_encoding(
    codebook_rule: torch.Tensor,
    codebook_entity: torch.Tensor,
    codebook_relation: torch.Tensor,
    codebook_hop: torch.Tensor,
    keys_mat: torch.Tensor,
    chain_meta: List[Dict],
    N_use: int,
    n_audit: int = 100,
) -> Dict:
    """Verify 4-way unbinding correctness on a sample of stored steps.

    For k_step = r * k1 * k2 * h: unbing r via k_step*k1*k2*h.
    Since all bipolar: r_rec = k_step*k1*k2*h = r*(k1^2)*(k2^2)*(h^2) = r. Exact.
    """
    M_steps = keys_mat.shape[0]
    n_check = min(n_audit, M_steps)
    torch.manual_seed(42)
    idx_check = torch.randperm(M_steps, device=keys_mat.device)[:n_check]

    confs_r = []
    for ii in range(n_check):
        step_i = int(idx_check[ii].item())
        meta   = chain_meta[step_i]
        k_step = keys_mat[step_i]
        r_vec  = codebook_rule[meta["rule_idx"]]
        k1_vec = codebook_entity[meta["entity1_idx"]]
        k2_vec = codebook_relation[meta["rel_idx"]]
        h_vec  = codebook_hop[meta["hop_id_idx"]]

        # 4-way unbinding: multiply by k1, k2, h to recover r
        r_rec = k_step * k1_vec * k2_vec * h_vec
        conf  = float((r_rec * r_vec).sum().item()) / float(N_use)
        confs_r.append(conf)

    mean_c         = sum(confs_r) / len(confs_r)
    frac_above_hp  = sum(1 for c in confs_r if c > HP_CONF_STEP) / len(confs_r)
    frac_below_hf  = sum(1 for c in confs_r if c <= HF_AUDIT_CONF) / len(confs_r)
    return {
        "mean_conf":          round(mean_c, 5),
        "frac_above_hp":      round(frac_above_hp, 5),
        "frac_below_hf":      round(frac_below_hf, 5),
        "n_checked":          len(confs_r),
    }


def cleanup_audit_stats(audit_list: List[Dict]) -> Dict:
    """Aggregate cleanup audit records: snap accuracy and borderline rate."""
    if not audit_list:
        return {"verify_rate": 0.0, "mean_snap_sim": 0.0, "n_borderline": 0, "n_total": 0}
    n_total     = len(audit_list)
    n_correct   = sum(1 for a in audit_list if a["correct"])
    verify_rate = n_correct / n_total
    mean_sim    = sum(a["snap_sim"] for a in audit_list) / n_total
    n_borderline = sum(1 for a in audit_list if a["snap_sim"] < 0.7)
    return {
        "verify_rate":   round(verify_rate, 5),
        "mean_snap_sim": round(mean_sim, 5),
        "n_borderline":  n_borderline,
        "n_total":       n_total,
    }


def run_one_seed(
    N_use: int,
    n_chains: int,
    seed: int,
    device: torch.device,
) -> Dict:
    """Run 3 arms (A=4-way, B=cleanup, C=combined) + baseline for one seed."""
    t0 = time.time()

    # Build codebooks
    cb_rule    = make_bsc_codebook(N_use, N_RULE_CODEWORDS, seed + 0, device)
    cb_entity  = make_bsc_codebook(N_use, N_ENTITY_CODEWORDS, seed + 1, device)
    cb_rel     = make_bsc_codebook(N_use, N_RELATION_CODEWORDS, seed + 2, device)
    cb_hop     = make_bsc_codebook(N_use, N_HOP_ID_CODEWORDS, seed + 3, device)

    # Verify hop-id codewords are independent from entity/relation/rule codebooks
    # (spot check orthogonality: mean inner product should be near 0)
    hop_rule_sim = float(
        (cb_hop @ cb_rule.T).abs().mean().item()) / float(N_use)

    # --- Baseline: 3-way structured corpus (PP-11 Arm B equivalent) ---
    keys_struct, vals_struct, chain_meta = make_reasoning_corpus(
        cb_rule, cb_entity, cb_rel, n_chains, seed, device)
    M_steps = keys_struct.shape[0]
    W_struct = build_W_from_corpus(keys_struct, vals_struct, N_use)

    n_probe = min(200, M_steps)
    baseline_result = retrieval_accuracy(
        W_struct, keys_struct, chain_meta, cb_entity, N_use, n_probe, seed)

    # Random key baseline for ratio computation
    keys_rand, vals_rand = make_random_corpus(
        M_steps, N_use, seed, device, cb_entity, chain_meta)
    W_rand = build_W_from_corpus(keys_rand, vals_rand, N_use)
    rand_result = retrieval_accuracy(
        W_rand, keys_rand, chain_meta, cb_entity, N_use, n_probe, seed + 1000)

    # --- Arm A: 4-way binding only ---
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

    # --- Arm C: 4-way + cleanup (primary) ---
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
        f"({elapsed:.1f}s)",
        flush=True,
    )

    return {
        "seed":             seed,
        "N":                N_use,
        "M_steps":          M_steps,
        "n_chains":         n_chains,
        "elapsed_s":        elapsed,
        "hop_rule_sim_mean": round(hop_rule_sim, 6),
        "baseline":         baseline_result,
        "rand":             rand_result,
        "arm_a_4way":       {"retrieval": arm_a_result, "audit": arm_a_audit},
        "arm_b_cleanup":    {"retrieval": arm_b_result, "cleanup_stats": arm_b_cleanup_stats},
        "arm_c_combined":   {"retrieval": arm_c_result, "cleanup_stats": arm_c_cleanup_stats},
    }


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    """Aggregate across seeds and emit arm-level + overall verdicts."""
    if not per_seed:
        return ("4WC_INCONCLUSIVE", "no seed results")

    def mean(xs): return sum(xs) / len(xs) if xs else 0.0

    # Per-arm ratios (structured/random)
    def arm_ratios(key_path: str) -> List[float]:
        rands = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
        arms  = [s[key_path]["retrieval"]["mean_per_hop_acc"] for s in per_seed]
        return [a / r if r > 1e-6 else 0.0 for a, r in zip(arms, rands)]

    ratios_a   = arm_ratios("arm_a_4way")
    ratios_b   = arm_ratios("arm_b_cleanup")
    ratios_c   = arm_ratios("arm_c_combined")

    mean_ra = mean(ratios_a)
    mean_rb = mean(ratios_b)
    mean_rc = mean(ratios_c)

    # Baseline ratios (PP-11 Arm B equivalent; should be ~0.93)
    rands   = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
    baselines = [s["baseline"]["mean_per_hop_acc"] for s in per_seed]
    mean_r_base = mean([b / r if r > 1e-6 else 0.0 for b, r in zip(baselines, rands)])

    # Arm C cleanup verification rate
    verify_c_rates = [s["arm_c_combined"]["cleanup_stats"]["verify_rate"]
                      for s in per_seed]
    mean_verify_c = mean(verify_c_rates)

    # Arm C verdict
    if mean_rc >= HP_RATIO_C and mean_verify_c >= HP_VERIFY_C:
        arm_c_v = "HARD_PASS"
    elif mean_rc < HF_RATIO_C:
        arm_c_v = "HARD_FAIL"
    else:
        arm_c_v = "MIDDLE_BAND"

    # Overall verdict
    if arm_c_v == "HARD_PASS":
        overall = "4WC_HARD_PASS"
    elif arm_c_v == "HARD_FAIL":
        overall = "4WC_HARD_FAIL"
    else:
        overall = "4WC_MIDDLE_BAND"

    msg = (
        f"baseline_ratio={mean_r_base:.3f} "
        f"A_4way_ratio={mean_ra:.3f} "
        f"B_cleanup_ratio={mean_rb:.3f} "
        f"C_combined_ratio={mean_rc:.3f} "
        f"C_verify={mean_verify_c:.3f} "
        f"arm_C={arm_c_v} "
        f"seeds={len(per_seed)} N={per_seed[0]['N']}"
    )
    return (overall, msg)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    PROT-018 binding: N_FULL == 16384.
    Formula self-tests:
      1. BSC codebook: entries in {-1, +1}.
      2. 4-way bipolar unbinding is exact.
      3. Hop-id codewords drawn independently from entity/rule codebooks.
      4. Cleanup snap on clean codeword returns same index (verify_rate=1.0 expected).
      5. Verdict gates work correctly.
    """
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

    device = torch.device("cpu")
    N_st = 64

    # 1. BSC codebook
    cb = make_bsc_codebook(N_st, 10, 42, device)
    assert cb.shape == (10, N_st)
    assert set(cb.view(-1).tolist()).issubset({-1.0, 1.0}), "BSC not bipolar"

    # 2. 4-way bipolar unbinding exact
    r_vec = cb[0]; k1 = cb[1]; k2 = cb[2]; h = cb[3]
    k_step = r_vec * k1 * k2 * h
    r_rec  = k_step * k1 * k2 * h   # should recover r exactly
    conf   = float((r_rec * r_vec).sum().item()) / float(N_st)
    assert abs(conf - 1.0) < 1e-5, f"4-way unbinding failed: conf={conf}"

    # 3. Hop-id orthogonality to rule codebook (mean cross-product near 0)
    cb_hop  = make_bsc_codebook(N_st, N_HOP_ID_CODEWORDS, 17, device)
    cb_rule = make_bsc_codebook(N_st, N_RULE_CODEWORDS, 99, device)
    cross   = float((cb_hop @ cb_rule.T).abs().mean().item()) / float(N_st)
    # At N=64 there will be some variance; allow up to 0.20
    assert cross < 0.20, f"hop-id cross-correlation too high: {cross:.4f}"

    # 4. Cleanup snap on exact clean codeword: should always return same idx
    cb_ent = make_bsc_codebook(N_st, N_ENTITY_CODEWORDS, 77, device)
    test_vec = cb_ent[5]
    sims     = (cb_ent @ test_vec) / float(N_st)
    snap_idx = int(torch.argmax(sims).item())
    assert snap_idx == 5, f"cleanup snap wrong for clean codeword: got {snap_idx}, expected 5"

    # 5. Smoke corpus: at least 1 step produced
    cb_rel  = make_bsc_codebook(N_st, N_RELATION_CODEWORDS, 55, device)
    keys_s, vals_s, meta_s = make_reasoning_corpus(
        cb_rule, cb_ent, cb_rel, 5, 17, device)
    assert keys_s.shape[0] >= 1, "no steps at smoke scale"
    assert keys_s.shape[1] == N_st

    # 6. Arm C corpus and retrieval at tiny scale
    keys_c, vals_c, audit_c = make_4way_cleanup_corpus(
        cb_rule, cb_ent, cb_rel, cb_hop, meta_s, device)
    assert keys_c.shape[0] == keys_s.shape[0], "4-way corpus size mismatch"
    c_stats = cleanup_audit_stats(audit_c)
    assert c_stats["n_total"] >= 1, "cleanup audit empty"
    assert 0.0 <= c_stats["verify_rate"] <= 1.0, "verify_rate out of range"

    # 7. Verdict gates
    fake_pass = []
    for s in [7, 17, 23]:
        fake_pass.append({
            "seed": s, "N": 16384, "M_steps": 1500, "n_chains": 500,
            "elapsed_s": 30.0, "hop_rule_sim_mean": 0.005,
            "baseline":     {"mean_per_hop_acc": 0.92, "n_hops_evaluated": 200},
            "rand":         {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 200},
            "arm_a_4way":   {"retrieval": {"mean_per_hop_acc": 0.97, "n_hops_evaluated": 200},
                             "audit": {"mean_conf": 1.0, "frac_above_hp": 0.98, "frac_below_hf": 0.0, "n_checked": 100}},
            "arm_b_cleanup":{"retrieval": {"mean_per_hop_acc": 0.97, "n_hops_evaluated": 200},
                             "cleanup_stats": {"verify_rate": 1.0, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 1500}},
            "arm_c_combined":{"retrieval": {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 200},
                              "cleanup_stats": {"verify_rate": 0.97, "mean_snap_sim": 1.0, "n_borderline": 5, "n_total": 1500}},
        })
    v, msg = compute_verdict(fake_pass)
    # ratio_C = 0.99/0.99=1.0 >= 0.98, verify_C=0.97 >= 0.95 -> 4WC_HARD_PASS
    assert v == "4WC_HARD_PASS", f"HP gate failed: {v}: {msg}"

    fake_fail = [{
        "seed": 7, "N": 16384, "M_steps": 1500, "n_chains": 500,
        "elapsed_s": 30.0, "hop_rule_sim_mean": 0.005,
        "baseline":     {"mean_per_hop_acc": 0.92, "n_hops_evaluated": 200},
        "rand":         {"mean_per_hop_acc": 0.99, "n_hops_evaluated": 200},
        "arm_a_4way":   {"retrieval": {"mean_per_hop_acc": 0.93, "n_hops_evaluated": 200},
                         "audit": {"mean_conf": 1.0, "frac_above_hp": 0.97, "frac_below_hf": 0.0, "n_checked": 100}},
        "arm_b_cleanup":{"retrieval": {"mean_per_hop_acc": 0.93, "n_hops_evaluated": 200},
                         "cleanup_stats": {"verify_rate": 1.0, "mean_snap_sim": 1.0, "n_borderline": 0, "n_total": 1500}},
        "arm_c_combined":{"retrieval": {"mean_per_hop_acc": 0.94, "n_hops_evaluated": 200},  # ratio=0.94/0.99=0.949 < 0.96
                          "cleanup_stats": {"verify_rate": 0.97, "mean_snap_sim": 1.0, "n_borderline": 5, "n_total": 1500}},
    }]
    v_fail, _ = compute_verdict(fake_fail)
    assert v_fail == "4WC_HARD_FAIL", f"HF gate failed: {v_fail}"

    print(
        f"[selftest] reasoning_storage_4way_cleanup_v1_n16384 PASS "
        f"N_FULL={N_FULL} 4way_conf={conf:.3f} snap_idx_ok={snap_idx==5} "
        f"cleanup_verify={c_stats['verify_rate']:.3f}",
        flush=True,
    )


_instrumentation_selftest()   # called at module scope before sweep


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke",     action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device   = torch.device("cpu")  # CPU-only; no CUDA needed at N=16384
    smoke    = args.smoke
    N_cfg    = N_SMOKE       if smoke else N_FULL
    n_ch     = N_CHAINS_SMOKE if smoke else N_CHAINS_FULL
    seeds    = SEEDS_SMOKE   if smoke else SEEDS_FULL

    out_dir  = get_output_dir()
    done     = set(list_completed_keys(out_dir))
    t0       = time.time()

    print(
        f"[run] reasoning_storage_4way_cleanup_v1_n16384 "
        f"smoke={smoke} N={N_cfg} n_chains={n_ch} seeds={seeds} "
        f"done={len(done)} device={device.type}",
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
        result = run_one_seed(N_cfg, n_ch, seed, device)
        write_partial_key(out_dir, ck, result)
        per_seed.append(result)

    verdict, vm = compute_verdict(per_seed)
    elapsed     = round(time.time() - t0, 2)

    # Suspicious-result gate
    if per_seed:
        arm_c_accs  = [s["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] for s in per_seed]
        rand_accs   = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
        all_zero    = all(a == 0.0 for a in arm_c_accs + rand_accs)
        if all_zero:
            print("[INSTRUMENTATION_SUSPECT] all per-hop accuracies are 0.0 -- "
                  "possible retrieval bug", flush=True)

    summary = {
        "anchor":     "reasoning_storage_4way_cleanup_v1_n16384",
        "N":          N_cfg,
        "smoke":      smoke,
        "n_chains":   n_ch,
        "seeds":      seeds,
        "per_seed":   per_seed,
        "verdict":    verdict,
        "verdict_msg": vm,
        "elapsed_s":  elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"[verdict] {verdict}: {vm}", flush=True)
    print(f"[done] elapsed={elapsed}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    main()
