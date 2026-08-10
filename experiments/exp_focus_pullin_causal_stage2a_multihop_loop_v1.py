# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; VALIDATE vs NO_VALIDATE vs BASELINE vs
#   SCRAMBLE trace outputs hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (accuracy-comparison ablation over a fixed 6-chain micro-world; no
#   capacity/noise-floor discriminator threshold)
# - HP_SCOPE: {micro_world: [validate_recovery, baseline_must_fail, novalidate_degradation, scramble]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS_FULL)=5 (full) / 1 (smoke)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (GATE_THRESH=0.32 MEASURED@calibration this
#   session, distinct from Stage-1's 0.28 because the role/overlap construction differs --
#   validated unchanged across seeds 7/17/29/41/53 at calibration time, see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL EventBundleCodec / BipolarCausalRegister / iterative_attractor
#   objects (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_focus_pullin_causal_stage2a_multihop_loop_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage2a_multihop_loop_v1 -- Stage 2 SUB-TEST A of the simulation-engine
program: does an ITERATED retrieve -> validate -> advance loop (built from Stage-1's validated
salience-gated pull_in()) recover a MULTI-HOP causal chain that is structurally invisible to a
SINGLE pull_in() call, and does the VALIDATE step arrest multiplicative per-hop error accumulation
(the VSA-drill capacity risk)?

Chain design (6 chains x 6 events = depths 1..5 hops from "now" back to the chain root):
  event(i) and event(i+1) share exactly 2 of 4 role terms (TENSE, chain-constant; + a LINK token
  unique to that one adjacency, injected via a role_keys ALIAS trick -- see "Role-alias construction"
  in the prereg). Non-adjacent same-chain events share only TENSE; cross-chain events share nothing.
  MEASURED@calibration (this session, N_DIM=1024, seed=7): adjacent cosine mean=0.443 (std=0.033),
  same-chain-nonadjacent mean=0.257 (std=0.012), cross-chain mean=0.140 (std=0.032) -- 3 clean tiers,
  >=3.4-sigma separated at every boundary.

  A single DECOY event per chain (planted at DECOY_HOP_DEPTH=3, i.e. it confuses the hop retrieving
  event(2) from event(3)) shares the SAME 2/4-term overlap magnitude with event(3) as the TRUE
  event(2) does -- a genuine, by-construction near-tie (MEASURED@calibration: decoy wins outright in
  ~1/6 chains, ties in ~1/6, loses in ~4/6, across 5 seeds). The decoy carries NO causal-register
  fact (BipolarCausalRegister, ported unchanged from Stage 1, only knows the TRUE adjacency chain),
  so it is a pure CONTENT-similarity confuser that the register-based VALIDATE step can and does
  correctly reject.

Two loop arms (both built on Stage-1's pull_in() mechanism, generalized to a growing exclude-set --
see "pull_in_multi_exclude" and its equivalence self-test):
  VALIDATE loop    : at each hop, pull_in; if NOT (admitted AND register.query_cause_of(cur) ==
                     candidate), exclude the rejected candidate and retry (bounded, MAX_RETRIES=2);
                     stop the loop (report partial depth) if retries exhaust.
  NO_VALIDATE loop : at each hop, take pull_in's candidate unconditionally, never checks the
                     register, never retries, always advances (chain_len-1 hops, no early stop).
Both loops track and exclude the WHOLE VISITED PATH (not just the current node) at every hop --
without this an early prototype of this cell found the loop could bounce backward to the node it
just came from (event i's OTHER adjacent partner), a real bug caught during calibration, not a
decoy effect (see prereg "Design bug found during calibration").

Baseline (Stage-1's pull_in(), reused UNCHANGED, called ONCE, not iterated): from "now" (event 5),
one pull_in call, compared against the true node at EVERY depth 1..5. MEASURED@calibration:
baseline recovers depth=1 at 1.000 (its one call IS the depth-1 neighbor) and depth>=2 at 0.000
EXACTLY, every seed -- the required structural floor proving the loop is load-bearing for anything
beyond 1 hop.

Modes:
  --self-test  Real-code-path check: trivial 2-hop hand-case (flat=broken-experiment precheck,
               per Stage-2 task CONTRACT) + run_one_seed(7) (the REAL pipeline) + verdict-logic
               sanity + arms-must-differ. No queue dispatch.
  --smoke      1 seed (7) at FULL parameters (N_DIM=1024, N_CHAINS=6 -- identical regime to FULL).
  --full       5 seeds (7,17,29,41,53), per-seed checkpointed (experiments/_seed_checkpoint.py).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2a_multihop_loop_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.event_bundle import EventBundleCodec  # noqa: E402
from hdlab.role_slot_summarizer import _bipolar_random  # noqa: E402
from hdlab.cleanup_family import iterative_attractor as _iterative_attractor  # noqa: E402
# REUSE (literal): Stage-1's own pull_in(), BipolarCausalRegister, and the deterministic-scramble
# helper -- imported, not re-transcribed. Stage-1's module guards its script body under
# `if __name__ == "__main__"`, so importing it here does not execute Stage-1's main().
from experiments.exp_focus_pullin_causal_stage1_micro_world_v1 import (  # noqa: E402
    pull_in as stage1_pull_in,
    BipolarCausalRegister,
    _deterministic_perm,
    _cos,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics as _ckpt_write_metrics,
)

# ---- fixed micro-world / mechanism parameters (exp_dev-owned; see prereg for calibration) ----
N_DIM = 1024
N_CHAINS = 6
CHAIN_LEN = 6            # positions 0..5; "now" = position 5; depths 1..5 hop back to position 0
DECOY_HOP_DEPTH = 3      # decoy confuses the hop retrieving event(2) from event(3)
GATE_THRESH = 0.32       # MEASURED@calibration: sits between same-chain-nonadjacent~0.257 and
                         # adjacent~0.443 (>=3.4 sigma both sides at seed=7); UNCHANGED across
                         # seeds 7/17/29/41/53 at calibration time (see prereg). Distinct from
                         # Stage-1's 0.28 -- different role/overlap construction, recalibrated
                         # honestly rather than blindly reused (see prereg "Dtype/gate reconciliation").
IATTR_TEMP = 4.0         # UNCHANGED from Stage 1 (reuse, not retuned)
IATTR_MAX_STEPS = 8      # UNCHANGED from Stage 1 (reuse, not retuned)
MAX_RETRIES = 2          # bounded retry budget for the VALIDATE loop's reject-and-retry
SEEDS_SMOKE = [7]
SEEDS_FULL = [7, 17, 29, 41, 53]


# ============================================================================ role-alias codec
def build_chain_codec(seed: int, n_dim: int = N_DIM) -> EventBundleCodec:
    """4 roles (PRED, TENSE, LINKA, LINKB); LINKA and LINKB are injected with the IDENTICAL role
    key (role_keys[2] used for both). This makes bind(LINKA_key, tok) == bind(LINKB_key, tok) for
    the SAME token tok -- so if event(i)'s LINKA filler equals event(i+1)'s LINKB filler, the two
    event bundles share a literal term, producing genuine cosine overlap for that ONE adjacent
    pair only (not for any other pair). This is the mechanism used to make "adjacent" content-
    overlap strictly decay with hop distance (a property Stage-1's whole-cluster-constant-AGENT
    design did not need, since Stage 1 only tested ONE fixed long-distance pair per cluster, not a
    chain of pairwise-decaying adjacencies).

    IMPORTANT (bug found + fixed during calibration): the role-key generator MUST use a seed
    DIFFERENT from the codec's own `seed`. EventBundleCodec, when given explicit role_keys, does
    NOT consume its internal self._gen for role-key generation; that generator is then FIRST
    consumed by the lazy per-symbol draws. If the external role-key generator and the codec's
    internal generator share a seed, the first few lazily-registered symbols reproduce the
    role-key draws bit-for-bit (K0 == first symbol, etc.), causing degenerate self-bind collisions
    (measured: this bug made adjacent-event cosine hit exactly 1.0, i.e. bit-identical event
    vectors -- caught by the calibration harness before any pre-reg band was set, per
    flat=broken-experiment discipline). Fixed by namespacing the role-key seed with a fixed offset.
    """
    rk_gen = torch.Generator()
    rk_gen.manual_seed(int(seed) + 999_983)
    r0 = _bipolar_random((n_dim,), rk_gen)
    r1 = _bipolar_random((n_dim,), rk_gen)
    r2 = _bipolar_random((n_dim,), rk_gen)
    role_keys = torch.stack([r0, r1, r2, r2], 0)  # PRED, TENSE, LINKA, LINKB (LINKA key == LINKB key)
    return EventBundleCodec(n_dim=n_dim, roles=("PRED", "TENSE", "LINKA", "LINKB"),
                            seed=seed, role_keys=role_keys)


# ============================================================================ multi-hop world construction
def build_world(seed: int, n_chains: int = N_CHAINS, chain_len: int = CHAIN_LEN,
                decoy_depth: int = DECOY_HOP_DEPTH, n_dim: int = N_DIM):
    """n_chains x chain_len events + 1 decoy per chain. Returns (codebook_np, meta, chain_start,
    decoy_idx, register)."""
    codec = build_chain_codec(seed, n_dim)
    all_events: List[torch.Tensor] = []
    meta: List[Tuple] = []
    chain_start: Dict[int, int] = {}
    decoy_idx: Dict[int, int] = {}
    for c in range(n_chains):
        chain_start[c] = len(all_events)
        for i in range(chain_len):
            rf = {
                "PRED": f"pred_{c}_{i}_s{seed}",
                "TENSE": f"tense_{c}_s{seed}",
                "LINKA": (f"link_{c}_{i}_s{seed}" if i < chain_len - 1 else f"END_{c}_s{seed}"),
                "LINKB": (f"link_{c}_{i-1}_s{seed}" if i > 0 else f"START_{c}_s{seed}"),
            }
            all_events.append(codec.encode_event(rf))
            meta.append((c, i))
        d = decoy_depth
        decoy_rf = {
            "PRED": f"decoy_pred_{c}_s{seed}",
            "TENSE": f"tense_{c}_s{seed}",
            "LINKA": f"link_{c}_{d-1}_s{seed}",   # ties event(d-1)'s LINKA -> confuses the
                                                  # event(d)->event(d-1) retrieval specifically
            "LINKB": f"decoy_none_{c}_s{seed}",
        }
        all_events.append(codec.encode_event(decoy_rf))
        decoy_idx[c] = len(all_events) - 1
        meta.append(("decoy", c))
    codebook = torch.stack(all_events, 0).numpy()

    gen = torch.Generator()
    gen.manual_seed(int(seed) + 10_000)
    reg = BipolarCausalRegister(n_dim, len(all_events), gen)
    facts: List[Tuple[int, int]] = []
    for c in range(n_chains):
        for i in range(chain_len - 1):
            a = chain_start[c] + i
            b = chain_start[c] + i + 1
            reg.add_causal_link(a, b)
            facts.append((a, b))
    return codebook, meta, chain_start, decoy_idx, reg, facts


# ============================================================================ generalized pull-in (multi-exclude)
def pull_in_multi_exclude(probe_np: np.ndarray, cb_full_np: np.ndarray, exclude_set: Set[int],
                          gate: float = GATE_THRESH, temp: float = IATTR_TEMP,
                          max_steps: int = IATTR_MAX_STEPS) -> Dict:
    """Generalizes Stage-1's pull_in(single exclude_idx) to an exclude SET, needed for the
    VALIDATE loop's reject-and-retry (excluding a growing visited-path + rejected-candidate set).
    Identical body to Stage-1's pull_in() -- same _iterative_attractor call, same raw-cosine gate
    formula -- generalized only in the masking step. Equivalence to pull_in() for a singleton
    exclude_set is asserted in self_test() (byte-identical result, not just same verdict)."""
    mask = np.ones(cb_full_np.shape[0], dtype=bool)
    for ex in exclude_set:
        mask[ex] = False
    cb_sub = cb_full_np[mask]
    sub_to_global = np.nonzero(mask)[0]
    state, diag = _iterative_attractor(probe_np, cb_sub, temp=temp, max_steps=max_steps)
    arg_sub = diag["final_argmax_idx"]
    glob = int(sub_to_global[arg_sub])
    score = _cos(probe_np, cb_full_np[glob])
    return {
        "admitted": bool(score >= gate), "candidate_idx": glob, "score": float(score),
        "n_iterations": int(diag["n_iterations"]), "converged": bool(diag["converged"]),
    }


# ============================================================================ retrieve-validate-advance loop
def run_loop(start_idx: int, n_hops: int, codebook: np.ndarray, register: BipolarCausalRegister,
            gate: float, validate: bool, max_retries: int = MAX_RETRIES) -> List[Dict]:
    """retrieve -> [validate] -> advance. `visited` accumulates the WHOLE path so far (not just
    the current node) and is always excluded -- otherwise the loop can bounce backward to an
    already-visited neighbor (a real bug caught during calibration; see build_chain_codec
    docstring's sibling note in the prereg). VALIDATE: reject-and-retry (bounded) against the
    causal register's INDEPENDENT confirmation; stop the loop (partial trace) if retries exhaust.
    NO_VALIDATE: unconditionally advance to whatever pull_in returns, never stops early."""
    cur = start_idx
    visited: Set[int] = {start_idx}
    trace: List[Dict] = []
    for hop in range(1, n_hops + 1):
        exclude = set(visited)
        result = None
        got = False
        attempt = 0
        for attempt in range(max_retries + 1):
            r = pull_in_multi_exclude(codebook[cur], codebook, exclude, gate=gate)
            result = r
            if not validate:
                got = True
                break
            reg_says = register.query_cause_of(cur)
            ok = r["admitted"] and (reg_says == r["candidate_idx"])
            if ok:
                got = True
                break
            exclude.add(r["candidate_idx"])
        validated_ok = True if not validate else got
        trace.append({"hop": hop, "from": cur, "to": result["candidate_idx"],
                      "score": result["score"], "admitted": result["admitted"],
                      "validated_ok": validated_ok, "attempts": attempt + 1})
        if validate and not validated_ok:
            break
        cur = result["candidate_idx"]
        visited.add(cur)
    return trace


# ============================================================================ trivial hand-case precheck
def precheck_trivial_2hop() -> Dict:
    """flat=broken-experiment discipline, per Stage-2 task CONTRACT: a 2-hop hand-case (A->B->C, no
    decoy, no chunking) that the VALIDATE loop MUST recover correctly (both hops) before any
    downstream HARD-FAIL on the main test is trusted."""
    codec = build_chain_codec(seed=0, n_dim=256)
    ev_a = codec.encode_event({"PRED": "crack", "TENSE": "past", "LINKA": "link01", "LINKB": "START"})
    ev_b = codec.encode_event({"PRED": "whisk", "TENSE": "past", "LINKA": "link12", "LINKB": "link01"})
    ev_c = codec.encode_event({"PRED": "pour", "TENSE": "past", "LINKA": "END", "LINKB": "link12"})
    cb = torch.stack([ev_a, ev_b, ev_c], 0).numpy()
    gen = torch.Generator(); gen.manual_seed(999)
    reg = BipolarCausalRegister(256, 3, gen)
    reg.add_causal_link(0, 1)
    reg.add_causal_link(1, 2)
    trace = run_loop(2, 2, cb, reg, gate=0.10, validate=True)
    ok = (len(trace) == 2 and trace[0]["to"] == 1 and trace[1]["to"] == 0)
    return {"ok": ok, "trace": trace,
            "detail": "2-hop hand-case: C->B->A via the validate loop (B causes... wait C's cause "
            "is B, B's cause is A); both hops must recover exactly."}


# ============================================================================ per-seed run
def run_one_seed(seed: int) -> Dict:
    t0 = time.time()
    codebook, meta, chain_start, decoy_idx, reg, facts = build_world(seed)
    n_hops = CHAIN_LEN - 1

    per_chain: Dict[int, Dict] = {}
    for c in range(N_CHAINS):
        start = chain_start[c] + (CHAIN_LEN - 1)
        true_at_depth = {d: chain_start[c] + (CHAIN_LEN - 1 - d) for d in range(1, CHAIN_LEN)}

        tr_validate = run_loop(start, n_hops, codebook, reg, GATE_THRESH, validate=True)
        tr_novalidate = run_loop(start, n_hops, codebook, reg, GATE_THRESH, validate=False)
        base_r = pull_in_multi_exclude(codebook[start], codebook, {start}, gate=GATE_THRESH)

        rec_validate = {d: bool(len(tr_validate) >= d and tr_validate[d - 1]["to"] == true_at_depth[d])
                        for d in range(1, CHAIN_LEN)}
        rec_novalidate = {d: bool(len(tr_novalidate) >= d and tr_novalidate[d - 1]["to"] == true_at_depth[d])
                          for d in range(1, CHAIN_LEN)}
        rec_baseline = {d: bool(base_r["candidate_idx"] == true_at_depth[d]) for d in range(1, CHAIN_LEN)}

        decoy_attempts = (tr_validate[DECOY_HOP_DEPTH - 1]["attempts"]
                          if len(tr_validate) >= DECOY_HOP_DEPTH else None)

        per_chain[c] = {
            "true_at_depth": true_at_depth,
            "trace_validate": tr_validate, "trace_novalidate": tr_novalidate,
            "baseline_candidate_idx": base_r["candidate_idx"], "baseline_score": base_r["score"],
            "rec_validate": rec_validate, "rec_novalidate": rec_novalidate, "rec_baseline": rec_baseline,
            "decoy_hop_attempts_validate": decoy_attempts,
        }

    # SCRAMBLE control: hashlib-seeded permutation of content-to-position (destroys structure),
    # applied to the VALIDATE loop (the arm claiming the real mechanism).
    perm = _deterministic_perm(f"stage2a_scramble_seed{seed}", len(codebook))
    cb_scr = codebook[np.array(perm)]
    scramble_depth5_rec = []
    for c in range(N_CHAINS):
        start = chain_start[c] + (CHAIN_LEN - 1)
        true0 = chain_start[c] + 0
        tr = run_loop(start, n_hops, cb_scr, reg, GATE_THRESH, validate=True)
        scramble_depth5_rec.append(bool(len(tr) >= 5 and tr[4]["to"] == true0))
    scramble_depth5_rate = float(np.mean(scramble_depth5_rec))

    per_depth_summary = {}
    for d in range(1, CHAIN_LEN):
        per_depth_summary[str(d)] = {
            "validate_rate": float(np.mean([per_chain[c]["rec_validate"][d] for c in range(N_CHAINS)])),
            "novalidate_rate": float(np.mean([per_chain[c]["rec_novalidate"][d] for c in range(N_CHAINS)])),
            "baseline_rate": float(np.mean([per_chain[c]["rec_baseline"][d] for c in range(N_CHAINS)])),
        }
    pre_decoy_depths = [d for d in range(1, DECOY_HOP_DEPTH)]          # {1, 2}
    post_decoy_depths = [d for d in range(DECOY_HOP_DEPTH, CHAIN_LEN)]  # {3, 4, 5}
    novalidate_pre = float(np.mean([per_depth_summary[str(d)]["novalidate_rate"] for d in pre_decoy_depths]))
    novalidate_post = float(np.mean([per_depth_summary[str(d)]["novalidate_rate"] for d in post_decoy_depths]))
    validate_post = float(np.mean([per_depth_summary[str(d)]["validate_rate"] for d in post_decoy_depths]))
    validate_mean_all = float(np.mean([per_depth_summary[str(d)]["validate_rate"] for d in range(1, CHAIN_LEN)]))
    baseline_depth_ge2 = float(np.mean([per_depth_summary[str(d)]["baseline_rate"]
                                       for d in range(2, CHAIN_LEN)]))

    elapsed = time.time() - t0
    return {
        "seed": seed, "n_dim": N_DIM, "n_chains": N_CHAINS, "chain_len": CHAIN_LEN,
        "decoy_hop_depth": DECOY_HOP_DEPTH, "gate_thresh": GATE_THRESH, "elapsed_s": round(elapsed, 4),
        "per_chain": {str(c): per_chain[c] for c in per_chain},
        "per_depth_summary": per_depth_summary,
        "novalidate_pre_decoy_mean": novalidate_pre, "novalidate_post_decoy_mean": novalidate_post,
        "novalidate_pre_minus_post_gap": novalidate_pre - novalidate_post,
        "validate_post_decoy_mean": validate_post,
        "validate_minus_novalidate_post_gap": validate_post - novalidate_post,
        "validate_mean_all_depths": validate_mean_all,
        "baseline_depth_ge2_mean": baseline_depth_ge2,
        "scramble_validate_depth5_rate": scramble_depth5_rate,
    }


# ============================================================================ verdict logic
GAP_MIN_HARD_PASS = 0.20   # HARD-PASS needs the pre/post-decoy novalidate gap >= this (MEASURED
                           # min across 5 calibration seeds was 0.278; 0.20 leaves real margin)
GAP_MIN_HARD_FAIL = 0.10   # HARD-FAIL if the gap is below this (discriminator did not fire)


def seed_verdict(result: Dict) -> Tuple[str, str]:
    validate_ok = result["validate_mean_all_depths"] >= 0.95
    baseline_ok = result["baseline_depth_ge2_mean"] == 0.0
    gap = result["novalidate_pre_minus_post_gap"]
    protect_gap = result["validate_minus_novalidate_post_gap"]
    scramble_ok = result["scramble_validate_depth5_rate"] <= 0.10

    hard_fail = ((not baseline_ok) or (result["validate_mean_all_depths"] < 0.70)
                or (gap < GAP_MIN_HARD_FAIL) or (result["scramble_validate_depth5_rate"] > 0.30))
    hard_pass = (validate_ok and baseline_ok and gap >= GAP_MIN_HARD_PASS
                and protect_gap >= GAP_MIN_HARD_PASS and scramble_ok)

    msg = (f"seed={result.get('seed', 'synthetic')} validate_all={result['validate_mean_all_depths']:.3f} "
          f"baseline_ge2={result['baseline_depth_ge2_mean']:.3f}(must be 0) "
          f"novalidate_gap={gap:.3f}(>= {GAP_MIN_HARD_PASS} for HARD_PASS) "
          f"validate_vs_novalidate_post_gap={protect_gap:.3f} "
          f"scramble_depth5={result['scramble_validate_depth5_rate']:.3f}(<=0.10 for HARD_PASS)")

    if hard_fail:
        return "HARD_FAIL", f"HARD_FAIL: {msg}"
    if hard_pass:
        return "HARD_PASS", f"HARD_PASS: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: {msg}"


def combine_verdicts(per_seed_verdicts: List[str]) -> Tuple[str, str]:
    if any(v == "HARD_FAIL" for v in per_seed_verdicts):
        return "HARD_FAIL", f"OVERALL_HARD_FAIL: >=1 seed HARD_FAIL ({per_seed_verdicts})"
    if all(v == "HARD_PASS" for v in per_seed_verdicts):
        return "HARD_PASS", f"OVERALL_HARD_PASS: all {len(per_seed_verdicts)} seeds HARD_PASS"
    return "MIDDLE_BAND", f"OVERALL_MIDDLE_BAND: mixed seed verdicts ({per_seed_verdicts})"


def _arms_must_differ(result: Dict) -> Dict:
    """META_RULE_AF: VALIDATE / NO_VALIDATE / BASELINE traces must be bit-different (hash-compared).
    Uses the ALL-CHAINS combined trace/candidate as the signature per arm (not a single chain --
    the decoy only actually flips NO_VALIDATE's pick on a SUBSET of chains per seed, so a
    single-chain digest can spuriously tie when that one chain happens not to hit the decoy trap;
    aggregating over all N_CHAINS chains makes the differ-check robust to that per-chain luck)."""
    def _digest(obj):
        b = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    all_validate = {c: result["per_chain"][c]["trace_validate"] for c in result["per_chain"]}
    all_novalidate = {c: result["per_chain"][c]["trace_novalidate"] for c in result["per_chain"]}
    all_baseline = {c: result["per_chain"][c]["baseline_candidate_idx"] for c in result["per_chain"]}
    sigs = {
        "validate": _digest(all_validate),
        "novalidate": _digest(all_novalidate),
        "baseline": _digest(all_baseline),
    }
    pairs_differ = {f"{a}_vs_{b}": sigs[a] != sigs[b]
                    for i, a in enumerate(sigs) for b in list(sigs)[i + 1:]}
    return {"sigs": sigs, "pairs_differ": pairs_differ, "all_differ": all(pairs_differ.values())}


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    """Real-code-path check: trivial 2-hop hand-case (CONTRACT precheck) + run_one_seed(7) (the REAL
    pipeline) + pull_in_multi_exclude/pull_in equivalence + verdict-logic sanity + arms-must-differ."""
    pre = precheck_trivial_2hop()
    assert pre["ok"], f"PRECHECK_FAIL (flat=broken-experiment discipline): {pre}"

    # pull_in_multi_exclude(singleton) must be BYTE-IDENTICAL to Stage-1's pull_in() -- proves
    # faithful generalization, not reimplementation drift.
    codebook, meta, chain_start, decoy_idx, reg, facts = build_world(7)
    probe_i = chain_start[0] + 5
    r_multi = pull_in_multi_exclude(codebook[probe_i], codebook, {probe_i})
    r_stage1 = stage1_pull_in(codebook[probe_i], codebook, probe_i)
    equiv = (r_multi["candidate_idx"] == r_stage1["candidate_idx"]
            and abs(r_multi["score"] - r_stage1["score"]) < 1e-9
            and r_multi["admitted"] == r_stage1["admitted"])
    assert equiv, f"PULL_IN_MULTI_EXCLUDE_NOT_EQUIVALENT: multi={r_multi} stage1={r_stage1}"

    result = run_one_seed(7)
    verdict, msg = seed_verdict(result)
    diff = _arms_must_differ(result)
    assert diff["all_differ"], f"ARMS_IDENTICAL: {diff}"

    hf_result = {"validate_mean_all_depths": 0.5, "baseline_depth_ge2_mean": 0.0,
                "novalidate_pre_minus_post_gap": 0.0, "validate_minus_novalidate_post_gap": 0.0,
                "scramble_validate_depth5_rate": 0.0}
    hf_v, _ = seed_verdict(hf_result)
    assert hf_v == "HARD_FAIL", hf_v  # validate_mean_all_depths < 0.70 forces HARD_FAIL

    hp_result = {"validate_mean_all_depths": 1.0, "baseline_depth_ge2_mean": 0.0,
                "novalidate_pre_minus_post_gap": 0.5, "validate_minus_novalidate_post_gap": 0.5,
                "scramble_validate_depth5_rate": 0.0}
    hp_v, _ = seed_verdict(hp_result)
    assert hp_v == "HARD_PASS", hp_v

    return {"precheck": pre, "pull_in_equivalence": {"multi": r_multi, "stage1": r_stage1, "equiv": equiv},
            "seed7_result_summary": {
                "validate_mean_all_depths": result["validate_mean_all_depths"],
                "baseline_depth_ge2_mean": result["baseline_depth_ge2_mean"],
                "novalidate_pre_minus_post_gap": result["novalidate_pre_minus_post_gap"],
                "validate_minus_novalidate_post_gap": result["validate_minus_novalidate_post_gap"],
                "scramble_validate_depth5_rate": result["scramble_validate_depth5_rate"],
                "per_depth_summary": result["per_depth_summary"],
            },
            "seed7_verdict": verdict, "seed7_verdict_msg": msg,
            "arms_differ_check": diff,
            "verdict_logic_unit_checks": {"hard_fail_case": hf_v, "hard_pass_case": hp_v}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))
        print(json.dumps({"result_summary": result["seed7_result_summary"],
                          "seed7_verdict": result["seed7_verdict"]}, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    run_config = {"run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds, output_dir, run_config=run_config)
    print(f"[{run_mode}] {len(done)}/{len(seeds)} seeds already complete; running {remaining}",
        flush=True)

    for i, seed in enumerate(remaining):
        print(f"[{run_mode}] seed={seed} running...", flush=True)
        result = run_one_seed(seed)
        verdict, msg = seed_verdict(result)
        payload = {"seed": seed, "N": N_DIM, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                  "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},gate={GATE_THRESH}",
                  "verdict": verdict, "verdict_msg": msg, "result": result}
        write_partial(output_dir, seed, payload)
        print(f"[{run_mode}] seed={seed} {verdict}: {msg}", flush=True)
        _write_heartbeat(output_dir, len(done) + i + 1, expected_units, time.time() - t0)

    per_seed = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed_verdicts = [per_seed[str(s)]["verdict"] for s in seeds]
    overall_verdict, overall_msg = combine_verdicts(per_seed_verdicts)

    last_seed_key = str(seeds[-1])
    last_result = per_seed[last_seed_key]["result"]
    diff = _arms_must_differ(last_result)
    if not diff["all_differ"]:
        overall_verdict = "HARD_FAIL"
        overall_msg = f"SMOKE_ARMS_IDENTICAL overrides combined verdict: {diff} || {overall_msg}"

    elapsed = time.time() - t0
    per_seed_summary = {
        s: {"verdict": per_seed[str(s)]["verdict"],
            "validate_mean_all_depths": per_seed[str(s)]["result"]["validate_mean_all_depths"],
            "baseline_depth_ge2_mean": per_seed[str(s)]["result"]["baseline_depth_ge2_mean"],
            "novalidate_pre_minus_post_gap": per_seed[str(s)]["result"]["novalidate_pre_minus_post_gap"],
            "validate_minus_novalidate_post_gap": per_seed[str(s)]["result"]["validate_minus_novalidate_post_gap"],
            "scramble_validate_depth5_rate": per_seed[str(s)]["result"]["scramble_validate_depth5_rate"],
            "per_depth_summary": per_seed[str(s)]["result"]["per_depth_summary"]}
        for s in seeds}

    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "gate_thresh": GATE_THRESH, "n_dim": N_DIM, "seeds": seeds,
        "per_seed_verdicts": dict(zip([str(s) for s in seeds], per_seed_verdicts)),
        "per_seed_summary": per_seed_summary,
        "per_seed_full": {k: v for k, v in per_seed.items()},
        "arms_differ_verified": diff["all_differ"], "arms_differ_check": diff,
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "accuracy-comparison retrieval ablation over a fixed 6-chain micro-world; "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: GATE_THRESH=0.32 fixed before this run, "
                            "validated unchanged across seeds 7/17/29/41/53 at calibration time "
                            "(see prereg)",
    }
    _ckpt_write_metrics(
        Path(output_dir), metrics,
        results=[{"elapsed_s": per_seed[str(s)]["result"]["elapsed_s"]} for s in seeds])
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("per_seed_full",)}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
