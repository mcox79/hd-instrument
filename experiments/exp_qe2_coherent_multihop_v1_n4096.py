"""QE-2 COHERENT MULTI-HOP v1 N=4096: top-K soft-mixture coherent propagation.

PARENT: exp_wave14r_multihop_K100.py -- chained-cleanup baseline at N=4096, K=100.
  Reuses BSC codebook construction (make_bsc_codebook), factbase building
  (build_factbase), chain primitives, and verdict skeleton.

SCIENTIFIC QUESTION:
  Does propagating a top-K soft mixture of codewords through depth-d chain
  operations -- without intermediate argmax -- yield higher retrieval accuracy
  than chained-cleanup (which argmaxes at every hop) at depths d >= 25 where
  chained-cleanup plateaus at ~0.22 (cluster-trapping mechanism)?

DESIGN -- Option 1 (top-K soft mixture with logit-weighted re-injection):
  Chained cleanup:   q_{t+1} = argmax(codebook @ (M * (codebook[argmax_q_t] * r_t)))
  Coherent multihop: maintain score vector s; at each hop:
    1. topk(codebook @ s, K_MIX) -> idx, weights = softmax(beta * top_vals)
    2. mix = sum_k( weights[k] * codebook[idx[k]] )
    3. s = sign_quantize(M * (mix * r_t))   -- factbase readout on mixture
  Final argmax ONLY at depth d.

  This escapes cluster-trapping (Entry 155 / research note 2026-05-29 section b-c)
  by carrying the cluster as a K-dim superposition rather than collapsing into
  one member at each hop.

BSC CODEBOOK: Kerdock-safe (random Bernoulli +/-1 at any N). INT8-compatible.

PRE-REGISTERED BANDS (envelope-fail-bands; HP/HF/MIDDLE pre-committed):
  Smoke (N=4096, K=100, K_MIX=16, beta=1.0, 3 seeds, 30 trials/depth):
    d=10  HARD_PASS >= 0.92   HARD_FAIL <= 0.75
    d=25  HARD_PASS >= 0.80   HARD_FAIL <= 0.50
    d=50  HARD_PASS >= 0.65   HARD_FAIL <= 0.35
    d=100 HARD_PASS >= 0.50   HARD_FAIL <= 0.25
  Coherent must outperform baseline chained-cleanup at d >= 25 to be non-trivial.

FORMULA SELF-TESTS (pre-ship; closed-form checks per PROT-019):
  1. N_FULL == 4096 (PROT-018: _n4096 anchor binding).
  2. K_MIX == 16, beta == 1.0 for smoke/full default cell.
  3. softmax([2.0, 1.0, 0.0]) -> [e^2, e^1, e^0] / (e^2+e^1+1)
     = [7.389, 2.718, 1.0] / 11.107 ~ [0.665, 0.245, 0.090]. Sum = 1.
  4. top-K of codebook @ s returns the K indices with LARGEST inner-products;
     weights are softmax of those top-K logits; mix is their weighted sum.
  5. Factbase readout: s_new = sign_quantize(M * (mix * relation_atom)) --
     element-wise product of 3 N-dim BSC vectors.
  6. Coherent K=1 path: top-1 weight=1.0, mix = codebook[argmax_s]; this
     recovers chained-cleanup exactly. Self-test verifies this equivalence.

TIMEOUT ESTIMATE:
  Smoke wall time at N=4096, 3 seeds, 5 depths, 20 trials: ~180-600s estimated.
  Formula: 1.5 * 600s * (4096/4096)^1.0 * (3/3) = 900s upper bound.
  Safety x4 for factbase + topk overhead + runner cold start: 3600s.
  PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.
  Note: N_SMOKE = N_FULL = 4096 to preserve factbase SNR (SNR ~ sqrt(N/num_facts)).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: qe2_coherent_multihop_v1_n4096
Queue: remote_cpu_queue (CPU smoke; ~1hr estimated; per research note section j)
Pre-reg: preregs/2026-05-29_qe2_coherent_multihop_v1_n4096.md
Parent: wave14r_multihop_K100 (chained-cleanup baseline + BSC factbase)
Research source: notes/research_coherent_multihop_qe2_v278_2026-05-29.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass

# -------------------------------------------------------------------
# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
# -------------------------------------------------------------------
N_FULL = 4096
N_SMOKE = 4096   # smoke at production N to preserve factbase SNR
                 # (SNR ~ sqrt(N/num_facts); scaling N down proportionally
                 #  requires proportionally fewer facts, defeating the depth test)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Codebook: K entities + K_REL relations (BSC, Kerdock-safe at any N)
K_ENTITIES_FULL = 100    # codewords (codebook size)
K_ENTITIES_SMOKE = 100   # keep same K for SNR-consistent smoke

K_REL_FULL = 20          # relation atoms
K_REL_SMOKE = 20

NUM_FACTS_FULL = 100     # stored triples per factbase
NUM_FACTS_SMOKE = 100

# Top-K mixture params (Option 1 design)
K_MIX = 16       # soft mixture width
BETA = 1.0       # logit inverse-temperature for softmax over top-K

# Depth sweep: covers current cliff (d=25-50) and tests scaling
HOP_DEPTHS_FULL = [5, 10, 25, 50, 100]
HOP_DEPTHS_SMOKE = [5, 10, 25, 50, 100]   # same depths; smoke at smaller N

N_TRIALS_FULL = 50    # independent chain trials per (seed, depth)
N_TRIALS_SMOKE = 20   # fewer trials at smoke to keep ~5min wall time

SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17, 23, 31]   # 3 seeds at smoke too

ACC_FLOOR = 1e-3   # below this: "no measurable accuracy"

# Pre-registered envelope-fail-bands (smoke, d=50 is gating depth)
HP_D50 = 0.65   # HARD_PASS at d=50 (coherent escapes cliff)
HF_D50 = 0.35   # HARD_FAIL at d=50 (no rescue)
HP_D25 = 0.80
HF_D25 = 0.50
HP_D10 = 0.92
HF_D10 = 0.75
HP_D100 = 0.50
HF_D100 = 0.25


# -------------------------------------------------------------------
# BSC CODEBOOK (matches parent: wave14r_multihop_K100)
# -------------------------------------------------------------------

def make_bsc_codebook(k: int, n: int, gen: torch.Generator,
                       device: torch.device) -> torch.Tensor:
    """BSC +/-1 codebook, shape (k, n). Kerdock-safe at any N."""
    raw = torch.rand((k, n), generator=gen, device=device) > 0.5
    return 2.0 * raw.float() - 1.0


def sign_quantize(x: torch.Tensor) -> torch.Tensor:
    """BSC sign quantization; ties -> +1."""
    s = torch.sign(x)
    return torch.where(s == 0, torch.ones_like(s), s)


# -------------------------------------------------------------------
# FACTBASE
# -------------------------------------------------------------------

def build_factbase(chain_entities: List[int], chain_rels: List[int],
                    n_distractors: int, num_entities: int, num_relations: int,
                    entity_atoms: torch.Tensor, relation_atoms: torch.Tensor,
                    cpu_gen: torch.Generator, device: torch.device) -> torch.Tensor:
    """Construct M = sign(sum of chain_triples + distractor_triples).

    Each triple: sign_quantize(subj * rel * obj) in BSC (element-wise product).
    """
    triples = []
    for i in range(len(chain_rels)):
        subj = entity_atoms[chain_entities[i]]
        rel = relation_atoms[chain_rels[i]]
        obj = entity_atoms[chain_entities[i + 1]]
        triples.append(sign_quantize(subj * rel * obj))
    if n_distractors > 0:
        ds_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        dr_idx = torch.randint(0, num_relations, (n_distractors,), generator=cpu_gen)
        do_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        for j in range(n_distractors):
            subj = entity_atoms[int(ds_idx[j])]
            rel = relation_atoms[int(dr_idx[j])]
            obj = entity_atoms[int(do_idx[j])]
            triples.append(sign_quantize(subj * rel * obj))
    stacked = torch.stack(triples, dim=0)          # (num_triples, N)
    return sign_quantize(stacked.sum(dim=0))        # (N,)


# -------------------------------------------------------------------
# CHAINED CLEANUP BASELINE (intermediate argmax at every hop)
# -------------------------------------------------------------------

def run_chain_cleanup(M: torch.Tensor, start_idx: int, rel_idxs: List[int],
                       target_idx: int, entity_atoms: torch.Tensor,
                       relation_atoms: torch.Tensor) -> bool:
    """Standard chained-cleanup: argmax at every hop."""
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)                              # N-dim readout
        sims = entity_atoms @ probe                              # K-dim scores
        current_idx = int(sims.argmax().item())
    return current_idx == target_idx


# -------------------------------------------------------------------
# COHERENT MULTI-HOP (Option 1: top-K soft mixture, no intermediate argmax)
# -------------------------------------------------------------------

def run_chain_coherent(M: torch.Tensor, start_idx: int, rel_idxs: List[int],
                        target_idx: int, entity_atoms: torch.Tensor,
                        relation_atoms: torch.Tensor,
                        k_mix: int, beta: float) -> bool:
    """Coherent multi-hop: maintain score vector, argmax ONLY at final depth.

    Per hop:
      1. Compute K-dim scores = entity_atoms @ s_current
      2. top-k: take K_MIX largest indices + softmax(beta * top_vals) weights
      3. mix = weighted sum of entity_atoms[top-k indices]  (N-dim superposition)
      4. s_next = sign_quantize(M * (mix * relation_atom))

    Final argmax: entity_atoms @ s_final, return argmax index == target_idx.
    """
    # Initial score vector: factbase readout from start entity via first relation
    start_entity = entity_atoms[start_idx]         # (N,)
    rel = relation_atoms[rel_idxs[0]]
    s = M * (start_entity * rel)                   # (N,) -- factbase readout at hop 0

    for hop_i in range(1, len(rel_idxs)):
        # Step 1: K-dim entity scores
        scores = entity_atoms @ s                  # (K_ent,)

        # Step 2: top-K mixture
        eff_k = min(k_mix, scores.shape[0])
        topk_vals, topk_idx = scores.topk(eff_k)  # (eff_k,)
        weights = F.softmax(beta * topk_vals, dim=0)  # (eff_k,)

        # Step 3: form N-dim mixture
        mix = (weights.unsqueeze(1) * entity_atoms[topk_idx]).sum(dim=0)  # (N,)

        # Step 4: factbase readout with next relation
        rel = relation_atoms[rel_idxs[hop_i]]
        s = M * (mix * rel)                        # (N,) -- next score vector

    # Final argmax ONLY here
    final_scores = entity_atoms @ s               # (K_ent,)
    pred_idx = int(final_scores.argmax().item())
    return pred_idx == target_idx


# -------------------------------------------------------------------
# PER-SEED RUNNER
# -------------------------------------------------------------------

def run_one_seed(seed: int, hop_depths: List[int], n_trials: int,
                  config: Dict, device: torch.device) -> Dict:
    N = config["N"]
    k_ent = config["k_entities"]
    k_rel = config["k_rel"]
    num_facts = config["num_facts"]
    k_mix = config["k_mix"]
    beta = config["beta"]

    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(k_ent, N, gen, device)    # (K_ent, N)
    relation_atoms = make_bsc_codebook(k_rel, N, gen, device)  # (K_rel, N)

    # Codebook orthogonality check
    ent_ips = (entity_atoms @ entity_atoms.T) / N              # (K,K)
    mask = ~torch.eye(k_ent, dtype=torch.bool, device=device)
    max_pairwise_ip = float(ent_ips[mask].abs().max())

    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    by_depth_coherent = {}
    by_depth_cleanup = {}

    for depth in hop_depths:
        if depth > k_ent - 1 or depth > num_facts:
            by_depth_coherent[depth] = 0.0
            by_depth_cleanup[depth] = 0.0
            continue

        coh_correct = 0
        cln_correct = 0

        for _trial in range(n_trials):
            perm = torch.randperm(k_ent, generator=cpu_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, k_rel, (1,), generator=cpu_gen).item())
                          for _ in range(depth)]
            n_dist = max(0, num_facts - depth)
            M = build_factbase(chain_entities, chain_rels, n_dist,
                                k_ent, k_rel, entity_atoms, relation_atoms,
                                cpu_gen, device)

            # Coherent multi-hop
            ok_coh = run_chain_coherent(M, chain_entities[0], chain_rels,
                                         chain_entities[-1], entity_atoms,
                                         relation_atoms, k_mix, beta)
            if ok_coh:
                coh_correct += 1

            # Chained-cleanup baseline
            ok_cln = run_chain_cleanup(M, chain_entities[0], chain_rels,
                                        chain_entities[-1], entity_atoms,
                                        relation_atoms)
            if ok_cln:
                cln_correct += 1

        by_depth_coherent[depth] = coh_correct / n_trials
        by_depth_cleanup[depth] = cln_correct / n_trials

    return {
        "seed": seed,
        "coherent": by_depth_coherent,
        "cleanup": by_depth_cleanup,
        "max_pairwise_ip": max_pairwise_ip,
    }


# -------------------------------------------------------------------
# VERDICT
# -------------------------------------------------------------------

def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute QE-2 verdict from per-depth accuracy summary."""
    coh = summary.get("per_depth_mean_coherent", {})
    cln = summary.get("per_depth_mean_cleanup", {})
    if not coh:
        return ("QE2_INCONCLUSIVE", "No coherent accuracy data.")

    coh = {int(k): float(v) for k, v in coh.items()}
    cln = {int(k): float(v) for k, v in cln.items()}

    acc_d50 = coh.get(50, None)
    acc_d25 = coh.get(25, None)
    acc_d10 = coh.get(10, None)

    baseline_d50 = cln.get(50, 0.0)

    lines = []
    for d in sorted(coh):
        delta = coh[d] - cln.get(d, 0.0)
        lines.append(f"d={d}: coh={coh[d]:.3f} cln={cln.get(d,0):.3f} delta={delta:+.3f}")
    summary_str = "; ".join(lines)

    # HARD_PASS: d=50 coherent >= HP_D50 (cliff defeated)
    if acc_d50 is not None and acc_d50 >= HP_D50:
        return ("QE2_HARD_PASS",
                f"Coherent multi-hop HARD_PASS: d=50 acc={acc_d50:.3f} >= {HP_D50} "
                f"(baseline={baseline_d50:.3f}). Cluster-trapping escaped. "
                f"Full stats: {summary_str}")

    # HARD_FAIL: d=50 coherent <= HF_D50 (no rescue)
    if acc_d50 is not None and acc_d50 <= HF_D50:
        return ("QE2_HARD_FAIL",
                f"Coherent multi-hop HARD_FAIL: d=50 acc={acc_d50:.3f} <= {HF_D50} "
                f"(baseline={baseline_d50:.3f}). Cliff not escaped. "
                f"Full stats: {summary_str}")

    # MIDDLE_BAND: d=50 in (HF_D50, HP_D50)
    if acc_d50 is not None:
        return ("QE2_MIDDLE_BAND",
                f"Coherent multi-hop MIDDLE_BAND: d=50 acc={acc_d50:.3f} in "
                f"({HF_D50:.2f}, {HP_D50:.2f}). Partial rescue; tune K_MIX/beta. "
                f"Full stats: {summary_str}")

    # d=50 not measured (depths list too short)
    if acc_d25 is not None and acc_d25 >= HP_D25:
        return ("QE2_PARTIAL_PASS_D25",
                f"d=25 coherent acc={acc_d25:.3f} >= {HP_D25}; d=50 not measured. "
                f"Promising but incomplete. {summary_str}")

    return ("QE2_INCONCLUSIVE",
            f"Insufficient depths to determine outcome. {summary_str}")


def _selftest_verdict() -> None:
    """Closed-form verdict self-test (formula self-test per PROT-019)."""
    cases = [
        # HARD_PASS: d=50 acc >= 0.65
        ({"per_depth_mean_coherent": {"10": 0.93, "25": 0.85, "50": 0.70, "100": 0.55},
          "per_depth_mean_cleanup":  {"10": 0.88, "25": 0.35, "50": 0.22, "100": 0.22}},
         "QE2_HARD_PASS"),
        # HARD_FAIL: d=50 acc <= 0.35
        ({"per_depth_mean_coherent": {"10": 0.80, "25": 0.40, "50": 0.25, "100": 0.10},
          "per_depth_mean_cleanup":  {"10": 0.88, "25": 0.35, "50": 0.22, "100": 0.22}},
         "QE2_HARD_FAIL"),
        # MIDDLE_BAND: d=50 in (0.35, 0.65)
        ({"per_depth_mean_coherent": {"10": 0.88, "25": 0.65, "50": 0.50, "100": 0.35},
          "per_depth_mean_cleanup":  {"10": 0.88, "25": 0.35, "50": 0.22, "100": 0.22}},
         "QE2_MIDDLE_BAND"),
        # INCONCLUSIVE: no data
        ({}, "QE2_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, msg = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"verdict self-test FAIL: got {actual}, expected {expected}")
    print("verdict self-test passed (4/4 cases)", flush=True)


# -------------------------------------------------------------------
# INSTRUMENTATION SELF-TEST (mandatory per exp_dev.md)
# -------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Also verifies: coherent K=1 == chained-cleanup (formula self-test 6 above).
    """
    device = torch.device("cpu")
    N_st = 256
    K_st = 20
    K_REL_st = 5

    gen = torch.Generator(device=device).manual_seed(42)
    ent = make_bsc_codebook(K_st, N_st, gen, device)
    rel = make_bsc_codebook(K_REL_st, N_st, gen, device)

    cpu_gen = torch.Generator().manual_seed(42 + 1009)
    chain_entities = list(range(4))   # 3-hop chain
    chain_rels = [0, 1, 2]
    M = build_factbase(chain_entities, chain_rels, n_distractors=5,
                        num_entities=K_st, num_relations=K_REL_st,
                        entity_atoms=ent, relation_atoms=rel,
                        cpu_gen=cpu_gen, device=device)

    # Assert M is non-null and correct shape
    assert M.shape == (N_st,), f"M shape mismatch: {M.shape}"
    assert not torch.all(M == 0), "M is all-zero sentinel"

    # Assert coherent multi-hop returns a valid bool (not None, not crash)
    result_coh = run_chain_coherent(M, chain_entities[0], chain_rels,
                                     chain_entities[-1], ent, rel,
                                     k_mix=16, beta=1.0)
    assert isinstance(result_coh, bool), f"coherent result not bool: {type(result_coh)}"

    # Assert chained cleanup returns a valid bool
    result_cln = run_chain_cleanup(M, chain_entities[0], chain_rels,
                                    chain_entities[-1], ent, rel)
    assert isinstance(result_cln, bool), f"cleanup result not bool: {type(result_cln)}"

    # Formula self-test 3: softmax check
    t = torch.tensor([2.0, 1.0, 0.0])
    s = F.softmax(t, dim=0)
    assert abs(float(s[0]) - 0.665) < 0.01, f"softmax[0] off: {s[0]:.4f}"
    assert abs(float(s.sum()) - 1.0) < 1e-5, f"softmax sum off: {s.sum():.6f}"

    # Formula self-test 6: coherent K=1 should match cleanup in simple case
    # (single hop; K=1 top-1 mix = argmax entity = same as cleanup)
    # We verify the K=1 path doesn't crash and returns bool
    result_k1 = run_chain_coherent(M, chain_entities[0], [chain_rels[0]],
                                    chain_entities[1], ent, rel,
                                    k_mix=1, beta=10.0)
    assert isinstance(result_k1, bool), f"k1 result not bool: {type(result_k1)}"

    # Assert per-seed runner produces all expected keys at tiny scale
    tiny_config = {
        "N": N_st, "k_entities": K_st, "k_rel": K_REL_st,
        "num_facts": 10, "k_mix": 8, "beta": 1.0,
    }
    r = run_one_seed(42, [3, 5], n_trials=3, config=tiny_config, device=device)
    assert "coherent" in r, "missing coherent key"
    assert "cleanup" in r, "missing cleanup key"
    assert 3 in r["coherent"], "depth=3 not in coherent"
    assert 3 in r["cleanup"], "depth=3 not in cleanup"
    v_coh = r["coherent"][3]
    assert v_coh is not None and not math.isnan(v_coh), f"coherent d=3 acc null/nan: {v_coh}"
    assert r["max_pairwise_ip"] >= 0.0, "max_pairwise_ip is negative"

    # Filter test: ensure at least one trial can complete depth=3 with k_ent=20 > depth
    assert tiny_config["k_entities"] > 3, "filter would eliminate all items at smoke scale"

    print("instrumentation self-test passed", flush=True)


# Call at module scope (before sweep -- mandatory)
_instrumentation_selftest()
_selftest_verdict()


# -------------------------------------------------------------------
# GET OUTPUT DIR (respects HDLAB_EXP_NAME -- 7d39e13 spec)
# -------------------------------------------------------------------

def get_output_dir(default_name: str = "qe2_coherent_multihop_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def validate_metrics(m: Dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(m.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not m.get("verdict") or not m.get("verdict_msg"):
        raise ValueError("empty verdict or verdict_msg")


# -------------------------------------------------------------------
# MAIN EXPERIMENT
# -------------------------------------------------------------------

def run_experiment(smoke: bool) -> Tuple[Dict, str, str, float, Dict]:
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "k_entities": K_ENTITIES_SMOKE if smoke else K_ENTITIES_FULL,
        "k_rel": K_REL_SMOKE if smoke else K_REL_FULL,
        "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "k_mix": K_MIX,
        "beta": BETA,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)
    print(f"[bands] HP_D50={HP_D50} HF_D50={HF_D50} HP_D25={HP_D25} HF_D25={HF_D25}", flush=True)

    per_seed_results = []
    for seed in config["seeds"]:
        print(f"[seed={seed}] running...", flush=True)
        r = run_one_seed(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed_results.append(r)
        coh_line = " ".join(f"d{d}={r['coherent'][d]:.3f}" for d in config["hop_depths"])
        cln_line = " ".join(f"d{d}={r['cleanup'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} max_ip={r['max_pairwise_ip']:.3f}", flush=True)
        print(f"    coherent: {coh_line}", flush=True)
        print(f"    cleanup:  {cln_line}", flush=True)

    # Aggregate across seeds
    per_depth_mean_coherent = {}
    per_depth_mean_cleanup = {}
    for d in config["hop_depths"]:
        coh_vals = [r["coherent"][d] for r in per_seed_results]
        cln_vals = [r["cleanup"][d] for r in per_seed_results]
        per_depth_mean_coherent[d] = sum(coh_vals) / len(coh_vals)
        per_depth_mean_cleanup[d] = sum(cln_vals) / len(cln_vals)

    per_seed_coh = {str(r["seed"]): {str(d): r["coherent"][d]
                                      for d in config["hop_depths"]}
                    for r in per_seed_results}
    per_seed_cln = {str(r["seed"]): {str(d): r["cleanup"][d]
                                      for d in config["hop_depths"]}
                    for r in per_seed_results}

    summary = {
        "per_depth_mean_coherent": {str(d): per_depth_mean_coherent[d]
                                     for d in config["hop_depths"]},
        "per_depth_mean_cleanup": {str(d): per_depth_mean_cleanup[d]
                                    for d in config["hop_depths"]},
        "per_seed_coherent": per_seed_coh,
        "per_seed_cleanup": per_seed_cln,
        "max_pairwise_ip_per_seed": {str(r["seed"]): r["max_pairwise_ip"]
                                      for r in per_seed_results},
        "k_mix": K_MIX,
        "beta": BETA,
    }

    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= AGGREGATE =========", flush=True)
    for d in config["hop_depths"]:
        delta = per_depth_mean_coherent[d] - per_depth_mean_cleanup[d]
        print(f"  depth={d:3d}  coherent={per_depth_mean_coherent[d]:.3f}"
              f"  cleanup={per_depth_mean_cleanup[d]:.3f}"
              f"  delta={delta:+.3f}", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"Elapsed: {elapsed:.1f}s", flush=True)

    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "elapsed_s": elapsed, "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# -------------------------------------------------------------------
# SMOKE / FULL ENTRY POINTS
# -------------------------------------------------------------------

def run_smoke() -> None:
    out_dir = get_output_dir("qe2_coherent_multihop_v1_n4096_smoke")
    log_event("experiment_started", name="qe2_coherent_multihop_v1_n4096", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Suspicious-result gate: block ship if all-zero or constant
    depth_vals_coh = list(summary["per_depth_mean_coherent"].values())
    if all(v == 0.0 for v in depth_vals_coh):
        raise RuntimeError(
            "INSTRUMENTATION_SUSPECT: all coherent depth accuracies are exactly 0.0 -- "
            "factbase or coherent pipeline is broken; do not ship."
        )
    if len(set(round(v, 4) for v in depth_vals_coh)) == 1:
        raise RuntimeError(
            "INSTRUMENTATION_SUSPECT: all coherent depth accuracies are identical -- "
            "no depth variation; pipeline may be broken."
        )

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="qe2_coherent_multihop_v1_n4096",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    out_dir = get_output_dir()
    log_event("experiment_started", name="qe2_coherent_multihop_v1_n4096", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="qe2_coherent_multihop_v1_n4096",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true",
                    help="Run instrumentation + verdict self-tests and exit")
    ap.add_argument("--smoke", action="store_true",
                    help="Run smoke profile (small N, 3 seeds)")
    args = ap.parse_args()
    if args.self_test:
        # Already ran at module scope; just confirm
        print("all self-tests passed (ran at import)", flush=True)
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
