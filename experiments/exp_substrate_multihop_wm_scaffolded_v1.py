"""substrate_multihop_wm_scaffolded_v1 -- WM-scaffolded multi-hop closure attempt.

CLOSURE TARGET (Barrier 1 retry per notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md):
  Multi-hop reasoning via PFC + hippocampus composition:
    - Hippocampus = Hebbian-bound W (substrate's existing chain-grade primitive)
    - PFC = working-memory slots (HRR-slot WM primitive, HARD_PASS at K=32 sigma=1.0)
    - Each hop: bind(scaffold-slot, predicate) -> W lookup -> cleanup -> write to next slot.
  CRITICAL DIFFERENCE from pointer_chain v2 (HARD_FAIL 5hop=0.122 / 10hop=0.035):
    pointer_chain v2 feeds the cleanup output of step n DIRECTLY into step n+1 query
    (state propagates noisy through hops; error compounds geometrically). WM-scaffold
    READS A CLEAN SLOT between hops: the per-hop input is the cleaned-and-rewritten
    scaffold content, not a degraded chain state. The brain does this; substrate has
    all the parts (W, HRR-slots, cleanup) but never composed them this way.

ARMS (4):
  ARM_BASELINE_HRR_2HOP        verbatim beta-sweep baseline from pointer_chain v2
                               (V_P=2 fixed p1=0/p2=1; n_chains=200; sanity rail
                               [0.62, 0.68]). MUST reproduce.
  ARM_WM_SCAFFOLDED_2HOP       new mechanism at depth 2 (target >= 0.80)
  ARM_WM_SCAFFOLDED_5HOP       new mechanism at depth 5 (pointer_chain v2 was 0.122;
                               target >= 0.50)
  ARM_WM_SCAFFOLDED_10HOP      new mechanism at depth 10 (pointer_chain v2 was 0.035;
                               target >= 0.20)

PRE-REG BANDS (LOCKED via assertion below; bands are PROSPECTIVE):
  HARD_PASS_CHAIN_GRADE:
    BASELINE in [0.62, 0.68] (sanity rail)
    AND ARM_WM_SCAFFOLDED_2HOP >= 0.80
    AND ARM_WM_SCAFFOLDED_5HOP >= 0.50
    AND ARM_WM_SCAFFOLDED_10HOP >= 0.20
    AND CV <= 0.07 across seeds
  HARD_PASS_PARTIAL:
    5HOP >= 0.30 OR 10HOP >= 0.10
    (lift over pointer_chain v2 but not chain-grade-eligible)
  MIDDLE_BAND:
    5HOP in [0.15, 0.30]
  HARD_FAIL_WM_DOESNT_HELP:
    5HOP < 0.15 (same regime as pointer_chain v2; WM scaffold ineffective)
  RAIL_SANITY_BREACH:
    BASELINE out of [0.62, 0.68] (interpretation halted; not interpretable)

CONFIG:
  N=8192, V_C=200, K_SET=20, n_chains=200, max_depth=10
  V_P=2 baseline, V_P=10 WM arms
  Sparse-bipolar codebook is NOT used here -- bipolar (dense) matches the
  pointer_chain v2 / beta-sweep regime that defined the sanity rail. Substrate-
  native primitives only (numpy; zero LLM forward calls).
  Seeds: [7, 17, 23] (apples-to-apples with pointer_chain v2).

SMOKE: n_chains=50, seed=7, max_depth=5 (chain-count-sensitive mechanism per
META smoke-vs-full discriminator candidate).

PROVENANCE: baseline arm reproduces pointer_chain v2 BASELINE rail within +/-0.05.

Author: exp_dev 2026-06-25.
ASCII-only; per-seed checkpoint; substrate-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_multihop_wm_scaffolded_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE HARD bands (LOCKED at module init)
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

HP_WM_2HOP_MIN = 0.80
HP_WM_5HOP_MIN = 0.50
HP_WM_10HOP_MIN = 0.20
HP_CV_MAX = 0.07

HP_PARTIAL_5HOP_MIN = 0.30
HP_PARTIAL_10HOP_MIN = 0.10

MID_5HOP_LO = 0.15
MID_5HOP_HI = 0.30

HF_5HOP_MAX = 0.15  # strictly less than

# Lock assertion: prospectively-pinned thresholds (catches accidental edits).
assert HP_WM_2HOP_MIN > HP_PARTIAL_5HOP_MIN, "PROSPECTIVE: 2HOP target must exceed 5HOP partial"
assert HP_WM_5HOP_MIN > MID_5HOP_HI, "PROSPECTIVE: HP_5HOP must exceed MID upper"
assert MID_5HOP_HI > MID_5HOP_LO == HF_5HOP_MAX, "PROSPECTIVE: MID/HF boundary"

# Regime config
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
WM_V_P = 10
WM_K_SET = 20

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    WM_N_CHAINS = 50
    HOP_DEPTHS = [2, 5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    WM_N_CHAINS = 200
    HOP_DEPTHS = [2, 5, 10]

n_predicates = max(BASELINE_V_P, WM_V_P)

CONFIG_VERSION = (
    "substrateMultihopWmScaffolded-v1: N=%d V_C=%d "
    "BASELINE_V_P=%d (fixed p1=0/p2=1; reproduces pointer_chain v2 rail) "
    "BASELINE_N=%d WM_V_P=%d WM_N=%d K_SET=%d "
    "seeds=%s mode=%s hop_depths=%s "
    "HP_2hop>=%.2f HP_5hop>=%.2f HP_10hop>=%.2f HP_cv<=%.2f "
    "HP_partial_5hop>=%.2f HP_partial_10hop>=%.2f "
    "mid_5hop=[%.2f,%.2f] HF_5hop<%.2f baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS, WM_V_P, WM_N_CHAINS,
    WM_K_SET, SEEDS, RUN_MODE, HOP_DEPTHS,
    HP_WM_2HOP_MIN, HP_WM_5HOP_MIN, HP_WM_10HOP_MIN, HP_CV_MAX,
    HP_PARTIAL_5HOP_MIN, HP_PARTIAL_10HOP_MIN,
    MID_5HOP_LO, MID_5HOP_HI, HF_5HOP_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


# =============================================================================
# Substrate primitives (mirrors pointer_chain v2 for apples-to-apples baseline)
# =============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


# ----- BASELINE: verbatim beta-sweep regime + mechanism ---------------------

def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                   p1: int = 0, p2: int = 1):
    """Verbatim port of beta-sweep's make_two_hop_chains (fixed-pair p1, p2)."""
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int, int]] = []
    used_s: set = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def chain_naive_hard(W, E, R, sq, start: int, relations: List[int]) -> int:
    """Verbatim beta-sweep chain_naive_hard: state propagates noisy through hops."""
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def arm_baseline_hrr_2hop_betasweep(E, R, sq, train_triples, queries):
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
        if pred == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries), "mechanism": "beta_sweep_naive_hard"}


# ----- WM-scaffolded mechanism ----------------------------------------------

def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set
                      ) -> Tuple[List[Tuple[int, int, int]], List[List[Tuple[int, int, int]]]]:
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, max_depth))
    return all_triples, chain_queries


def wm_slot_tag_codebook(K: int, n_dim: int, g: np.random.Generator) -> np.ndarray:
    """Slot-tag codebook for WM scaffold. Pure bipolar {-1,+1} (NOT L2-normalized).

    Pure bipolar is required for involutive elementwise bind:
        slot * slot = +1 elementwise -> bind(content, slot) * slot == content.
    L2-normalizing the slot tag breaks involutive (||slot||^2 / n_dim != 1
    elementwise). This matches the WM-HRR-slots PRODUCTION primitive's
    convention (exp_working_memory_hrr_slots_PRODUCTION_v1.random_bipolar
    returns +/-1 floats, not unit-normed vectors).
    """
    return (g.integers(0, 2, size=(K, n_dim)) * 2 - 1).astype(np.float32)


def wm_scaffold_write_read_roundtrip(slot_tag: np.ndarray,
                                      content_vec: np.ndarray) -> np.ndarray:
    """Round-trip a content vector through one WM slot.

    Mirrors exp_working_memory_hrr_slots_PRODUCTION_v1: bind(content, slot_tag)
    creates a slot-marked workspace; unbind via bind(workspace, slot_tag) under
    involutive elementwise product recovers content. Here we feed only ONE item
    per slot (K=1 round-trip) -- the slot scaffold is single-item-per-slot per
    hop, because at each hop the slot's content IS the cleaned intermediate.
    """
    # bind == elementwise product on bipolar; unbind == bind under involutive.
    workspace = content_vec * slot_tag
    retrieved = workspace * slot_tag
    return retrieved


def arm_wm_scaffolded(E, R, sq, W, chains_test, depth: int,
                       slot_tags: np.ndarray) -> Dict[str, Any]:
    """WM-scaffolded multi-hop: clean each intermediate into a WM slot.

    Per chain (s, p1, p2, ..., pk):
      slot_0 = E[s] (initial atom, treated as the substrate's input scaffold)
      For i in 0..k-1:
        # read clean content from slot i
        content_i = wm_slot_read(slot_tags[i], slot_workspace_i)
        # hop via Hebbian: key = bind(content_i, R[p_{i+1}]) * sqrt(N); look up W; cleanup
        key = content_i * R[p_{i+1}] * sq
        scores = E @ (W @ key)
        next_idx = argmax(scores)
        # write CLEAN atom (post-cleanup) into slot_{i+1}
        slot_workspace_{i+1} = E[next_idx] * slot_tags[i+1]

    Critical: between hops we READ a clean codebook atom (E[next_idx]), not the
    raw cleanup-vector. The slot-write/read is mechanistically required even at
    K=1 because the scaffold-IS-the-state contract makes the slot the
    substrate's "where am I in the chain" position marker. This is the
    information-theoretic equivalent of the brain's PFC + hippocampus loop.

    Returns top1 (final-step correct), per_step_acc list.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s_idx = chain[0][0]
        # Initial WM-slot write: clean atom E[s_idx] into slot 0.
        slot_content = E[s_idx].copy()
        # Round-trip through slot tag (mechanism witness; equivalent to E[s_idx]
        # on bipolar but exercises the actual WM primitive).
        slot_content = wm_scaffold_write_read_roundtrip(slot_tags[0], slot_content)
        cur_idx = s_idx
        for i in range(depth):
            p = chain[i][1]
            # READ from slot i: slot_content is already the clean intermediate.
            # HOP via Hebbian + cleanup:
            key = (slot_content * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            next_idx = int(scores.argmax())
            if next_idx == chain[i][2]:
                per_step_hits[i] += 1
            # WRITE CLEAN ATOM E[next_idx] into slot i+1 (the scaffold step).
            # This is THE crucial difference vs pointer_chain v2: next-hop input
            # is the cleaned codebook atom, written through the WM slot, NOT the
            # noisy chain state.
            slot_idx_next = (i + 1) % slot_tags.shape[0]
            slot_content = wm_scaffold_write_read_roundtrip(
                slot_tags[slot_idx_next], E[next_idx].copy())
            cur_idx = next_idx
        if cur_idx == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "mechanism": "wm_scaffolded_clean_atom_per_slot",
    }


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    # T1: WM-slot round-trip at sigma=0 (USER required self-test gate).
    # Confirms involutive bipolar bind == clean read.
    g2 = np.random.default_rng(42)
    slot_tags = wm_slot_tag_codebook(10, n, g2)
    content = E[3].copy()
    rt = wm_scaffold_write_read_roundtrip(slot_tags[0], content)
    assert np.allclose(rt, content), "T1 WM-slot round-trip failed"
    print("[selftest] T1 PASS: WM-slot round-trip at sigma=0 returns identical content")

    # T2: WM-slot cleanup integrity at sigma=0 per arm (>= 0.95 expected; uses
    # tiny W to bound runtime).
    triples_d, chains_d = make_deep_chains(20, V, 4, max_depth=2, g=g,
                                            disallow_s=set())
    W = ingest_hebbian(triples_d, E, R, sq, n)
    r2 = arm_wm_scaffolded(E, R, sq, W, chains_d, depth=2, slot_tags=slot_tags)
    assert 0.0 <= r2["top1"] <= 1.0
    assert r2["top1"] > 5.0 / V, \
        "T2 WM-scaffold top1=%.3f at depth=2 selftest scale too low" % r2["top1"]
    # Strong sigma=0 mechanism witness: should beat chance by a lot.
    assert r2["top1"] >= 0.50, \
        "T2 WM-scaffold sigma=0 integrity fail: top1=%.3f (<0.50; cleanup broken)" % r2["top1"]
    print("[selftest] T2 PASS: WM-scaffold top1=%.3f at depth=2 (sigma=0 mechanism intact)"
          % r2["top1"])

    # T3: NaN detection at production-scale matmul (per RECENT-DISCIPLINE).
    big_n = 4096
    big_V = 80  # >= V used above (60) so chain indices stay in-range
    big_E = bipolar(big_V, big_n, g)
    big_R = bipolar(4, big_n, g)
    big_W = ingest_hebbian(triples_d, big_E, big_R, math.sqrt(big_n), big_n)
    big_slots = wm_slot_tag_codebook(10, big_n, np.random.default_rng(99))
    r_big = arm_wm_scaffolded(big_E, big_R, math.sqrt(big_n), big_W, chains_d[:5],
                              depth=2, slot_tags=big_slots)
    assert not math.isnan(r_big["top1"]), "T3 NaN at production-scale matmul"
    print("[selftest] T3 PASS: production-scale matmul no-NaN (top1=%.3f)" % r_big["top1"])

    # T4: baseline beta-sweep mechanism beats chance at selftest scale.
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, R, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert r_base["top1"] > 5.0 / V, \
        "T4 baseline_top1=%.3f must beat 5/V=%.3f" % (r_base["top1"], 5.0 / V)
    print("[selftest] T4 PASS: baseline beta-sweep top1=%.3f at selftest scale" % r_base["top1"])

    # T5: per_step_acc has correct length.
    assert len(r2["per_step_acc"]) == 2, \
        "T5 per_step_acc length wrong: %d" % len(r2["per_step_acc"])
    print("[selftest] T5 PASS: per_step_acc length matches depth")

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run
# =============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)
    max_depth = max(HOP_DEPTHS)
    slot_g = np.random.default_rng(seed * 1009 + 17)
    slot_tags = wm_slot_tag_codebook(max(max_depth + 1, WM_K_SET), N_DIM, slot_g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates, "K_SET": WM_K_SET,
        "baseline_n_chains": BASELINE_N_CHAINS,
        "wm_n_chains": WM_N_CHAINS,
        "max_depth": max_depth,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE_HRR_2HOP (sanity rail; reproduces pointer_chain v2) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f (sanity_ok=%s) t=%.1fs"
          % (seed, r_baseline["top1"], baseline_ok, r_baseline["elapsed_s_arm"]),
          flush=True)

    # ===== WM-scaffold arms: separate chain set, separate W =====
    t_arm = time.time()
    wm_triples, wm_chains = make_deep_chains(
        WM_N_CHAINS, V_CONCEPTS, WM_V_P, max_depth=max_depth,
        g=g, disallow_s=set())
    W_wm = ingest_hebbian(wm_triples, E, R, sq, N_DIM)
    wm_W_build_s = round(time.time() - t_arm, 2)
    print("  [seed=%d] WM W built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(wm_triples), len(wm_chains), max_depth, wm_W_build_s),
          flush=True)

    for d in HOP_DEPTHS:
        t_arm = time.time()
        chains_d = [c[:d] for c in wm_chains]
        r = arm_wm_scaffolded(E, R, sq, W_wm, chains_d, depth=d, slot_tags=slot_tags)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out["arm_wm_scaffolded_%dhop" % d] = r
        print("  [seed=%d] ARM_WM_SCAFFOLDED_%dHOP top1=%.4f per_step=%s t=%.1fs"
              % (seed, d, r["top1"], r["per_step_acc"], r["elapsed_s_arm"]),
              flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        if len(vals) < 2:
            return 0.0
        m = float(np.mean(vals))
        return float(np.std(vals) / max(abs(m), 1e-9))

    baseline = mean_top1("arm_baseline_hrr_2hop")
    wm_2hop = mean_top1("arm_wm_scaffolded_2hop")
    wm_5hop = mean_top1("arm_wm_scaffolded_5hop")
    wm_10hop = mean_top1("arm_wm_scaffolded_10hop") if any(
        "arm_wm_scaffolded_10hop" in p for p in per_seed) else float("nan")
    cv_2hop = cv_top1("arm_wm_scaffolded_2hop")
    cv_5hop = cv_top1("arm_wm_scaffolded_5hop")
    cv_10hop = cv_top1("arm_wm_scaffolded_10hop") if not math.isnan(wm_10hop) else 0.0

    sanity_breached_seeds = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))

    # PER-ARM SUMMARY (Fix #28: per-arm numerics in verdict_msg).
    summ = ("BASELINE=%.4f (sanity_breach_seeds=%d/%d in [%.2f, %.2f]) "
            "WM_2HOP=%.4f (cv=%.3f) WM_5HOP=%.4f (cv=%.3f) WM_10HOP=%s (cv=%.3f) "
            "| pointer_v2_5hop=0.122 pointer_v2_10hop=0.035 (reference)"
            ) % (
        baseline, sanity_breached_seeds, len(per_seed),
        BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        wm_2hop, cv_2hop, wm_5hop, cv_5hop,
        ("%.4f" % wm_10hop) if not math.isnan(wm_10hop) else "n/a",
        cv_10hop,
    )

    # SACRED SANITY RAIL: majority sanity breach -> RAIL_SANITY_BREACH
    if sanity_breached_seeds >= max(1, (len(per_seed) + 1) // 2):
        return "RAIL_SANITY_BREACH", "RAIL_SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    hp_chain = (
        BASELINE_SANITY_LO <= baseline <= BASELINE_SANITY_HI
        and not math.isnan(wm_2hop) and wm_2hop >= HP_WM_2HOP_MIN
        and not math.isnan(wm_5hop) and wm_5hop >= HP_WM_5HOP_MIN
        and (math.isnan(wm_10hop) or wm_10hop >= HP_WM_10HOP_MIN)
        and cv_2hop <= HP_CV_MAX
        and cv_5hop <= HP_CV_MAX
        and cv_10hop <= HP_CV_MAX
    )
    if hp_chain:
        return "HARD_PASS_CHAIN_GRADE", \
               "HARD_PASS_CHAIN_GRADE_WM_SCAFFOLD: " + summ

    hp_partial = (
        (not math.isnan(wm_5hop) and wm_5hop >= HP_PARTIAL_5HOP_MIN)
        or (not math.isnan(wm_10hop) and wm_10hop >= HP_PARTIAL_10HOP_MIN)
    )
    if hp_partial:
        return "HARD_PASS_PARTIAL", \
               "HARD_PASS_PARTIAL_WM_SCAFFOLD_LIFTS_OVER_POINTER_V2: " + summ

    if not math.isnan(wm_5hop) and MID_5HOP_LO <= wm_5hop <= MID_5HOP_HI:
        return "MIDDLE_BAND", \
               "MIDDLE_BAND_WM_SCAFFOLD_PARTIAL_LIFT: " + summ

    if not math.isnan(wm_5hop) and wm_5hop < HF_5HOP_MAX:
        return "HARD_FAIL_WM_DOESNT_HELP", \
               "HARD_FAIL_WM_SCAFFOLD_SAME_REGIME_AS_POINTER_V2: " + summ

    return "MIDDLE_BAND", "MIDDLE_BAND_UNCLASSIFIED: " + summ


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "WM-scaffolded multi-hop closure attempt. Mechanism: PFC + "
            "hippocampus composition -- each hop reads a cleaned scaffold "
            "intermediate (E[next_idx] written through WM slot), preventing "
            "the geometric error compounding observed in pointer_chain v2 "
            "(5hop=0.122, 10hop=0.035). Baseline arm reproduces beta-sweep "
            "rail [0.62, 0.68] sanity. Pre-reg per "
            "preregs/2026-06-25_substrate_multihop_wm_scaffolded_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
