# CELL-TEMPLATE MANDATORY (subset applicable to a standalone <1min measurement probe, not a multi-unit
# training cell): except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace
# metrics write; deterministic seeding (np.random.default_rng only, no hash(), no list(set())); numbers
# tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@. No checkpoint/resume needed (single-shot,
# <1 minute wall time, no gradient training -- CLAUDE.md's multi-unit checkpoint mandate applies to
# cells looping over >1 (arm, seed) TRAINING unit; this is a pure forward-pass geometry measurement).
"""Cheap DG-analog fixed-projection PRE-CHECK (v2) -- the gate BEFORE the full training cell
(exp_wm_addressing_dg_fixed_projection_v1.py) is worth running.

CONFOUND FIX (this file supersedes v1's decisive metric; commit dac206619 flagged its own two bugs,
this is the fix, per exp_dev spawn spec): v1 measured "untrained_addr_distinct" by hashing 15 role reps
directly into exactly K_SLOTS=15 buckets. That is a BIRTHDAY-PARADOX collision ceiling (~37% expected
distinct for 15 draws into 15 bins) REGARDLESS of representation geometry -- v1's own self-test caught
this (see the NOTE in the old file: near-orthogonal synthetic reps topped out at 4-6/15 distinct at
every (d_exp_mult, k) tried, up to 128x expansion, interactively checked). The certified precedent this
plan cites (data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json, K4/K8=1.00
HARD_PASS) ran at address-space CARDINALITY N=1000, not N=15 -- a materially less collision-prone
regime. v1's decisive metric was therefore CONSTRUCTION-PINNED (bucket collision by counting-argument,
not mechanism-sensitive), and its own cell's decisive metric (argmax(addr_logits) == literal q_slot) is
ALSO structurally unsatisfiable by a fixed random projection: a random hash gives a consistent-but-
arbitrary bucket, never aligned to an arbitrary numeric slot id.

THE CORRECT GENERALIZATION CLAIM (this file measures it directly): a fixed projection generalizes to
HELD-OUT roles iff each held-out role's address is (a) CONSISTENT -- the SAME bucket whether the role
appears in an ASSIGNMENT-context sentence rep ("the door was painted red .") or a QUERY-context sentence
rep ("what color was the door ?") -- and (b) DISTINCT -- separable from every other role's address
(trained AND held-out), so no cross-contamination when reading. If both hold for held-out roles with
ZERO per-role training, the content-general write-then-read recall works for unseen roles by
construction. Consistency and distinctness are now measured at a LARGE address-space cardinality
N_ADDR >> K_SLOTS (grid {256, 512, 1024}, matching the certified N~1000 regime) -- decoupled from the
production WM's K_SLOTS=15 memory-slot count (which is a downstream architectural constraint of THIS
WM, not a property of role-representation separability; the precheck is diagnostic evidence about the
REPRESENTATIONS, not a rehearsal of the production bucket-pooling step).

CAN-FAIL FLOOR (mandatory, computed at every grid point so a PASS can never be reported from an invalid
floor): (1) SHUFFLED-PAIRING consistency control -- pair role r's query-context address with a
DIFFERENT role's (a fixed derangement, no self-pairs) assignment-context address; a wrong pairing has no
legitimate reason to match unless the address space has collapsed onto a dominant bucket (the "shared
component swamps top-k" failure mode this whole pre-check exists to catch) -- MUST stay near-chance, or
the "real" consistency number at that grid point is not trustworthy. (2) DEGENERATE-distinctness control
-- all 15 role reps set IDENTICAL; a FIXED hash of identical input MUST collapse to <=1 distinct bucket
regardless of n_addr (sanity: enlarging n_addr cannot manufacture distinctness the underlying geometry
does not have). A grid point is only eligible to certify PRECHECK_PASS/BORDERLINE if BOTH floor checks
pass at that point (`floor_valid`); if NO grid point's floor validates, the whole grid is reported
PRECHECK_FAIL with a floor-invalid flag (never silently trust an unvalidated PASS/BORDERLINE read).

NO GRADIENT TRAINING occurs here -- pure forward-pass geometry measurement, <1 minute of compute once
the frozen encoder's sentence cache is built. Role-query AND role-assignment reps both come from the SAME
frozen v2 encoder + the wm's pca_whiten conditioning at RANDOM INIT (untrained, shared role_query) --
this is the correct test of "does construction alone separate + align the roles."

Reuses the EXACT fixed-projection construction the full training cell trains against
(exp_wm_addressing_dg_fixed_projection_v1.make_fixed_projection / kwta_sparsify / bucket_pool, imported
directly -- NOT reimplemented) so this pre-check measures the identical mechanism, not a look-alike.
Also reuses the 15-role TRAIN/HELD_OUT split, encoder checkpoint path, and role-query/assignment sentence
templates from exp_wm_addressing_heldout_role_warmstart_v1 (aliased `ho`).

Sweep grid (exp_dev autonomy note per the build plan section 3; defaults reuse the plan's cited
certified precedents -- MEASURED/THEORETICAL/CITED tagged below):
  d_exp_mult in {2, 4, 8}   -- 2x default center per Spoke-3 design note
                               MEASURED@notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md:line97 ("N -> 2N" parameterization)
  k in {4, 8}               -- MEASURED@data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json:
                               K4_acc=1.00, K8_acc=1.00, HARD_PASS at N=1000
  n_addr in {256, 512, 1024} -- HYPOTHESIZED@this file: matches the certified precedent's address
                               cardinality order-of-magnitude (N~1000), decoupled from the production
                               WM's K_SLOTS=15 memory-slot count (the confound this file fixes)
  dg_seed fixed = 20260730001 (SAME constant as the full cell's default, held constant across the whole
                               (d_exp_mult, k, n_addr) grid so those three are the only swept variables)
  derangement_seed fixed = 20260730002 (the shuffled-pairing can-fail-floor control's fixed permutation
                               seed; a FIXED derangement of the 15 roles, no self-pairs)

Metrics per grid point (all computed from the frozen v2 encoder's whitened role reps -- QUERY-context
("what color was the {slot} ?") and ASSIGNMENT-context ("the {slot} was painted {fill} .", canonical
filler=ho.COLORS[0]) sentence reps for the SAME 15 roles):
  held_consistency_frac / train_consistency_frac -- fraction of HELD-OUT (n=3) / TRAIN (n=12) roles whose
    query-context argmax bucket EQUALS their assignment-context argmax bucket. Want HIGH (this is
    property (a), the decisive generalization requirement).
  held_distinct_frac / train_distinct_frac -- fraction of HELD-OUT / TRAIN roles whose query-context
    argmax bucket is UNIQUE among all 15 roles' query-context addresses. Want HIGH (property (b)).
  shuffled_consistency_frac -- the can-fail floor for (a): query[r] paired with assign[derangement(r)].
    Want LOW (near chance); high value here means the "real" consistency at this point is not trustworthy.
  degenerate_n_distinct -- the can-fail floor for (b): all-identical-rep control's distinct count.
    Want <=1 (sanity; large n_addr must not manufacture distinctness from nothing).
  gate_score = min(held_consistency_frac, held_distinct_frac) -- BOTH properties are required jointly;
    ranking/verdict uses the worse of the two, not their average.

DECISION RULE (build plan section 4 intent, adapted to the n=3 held-out cardinality and the corrected
consistency+distinctness+can-fail-floor measurement -- NOT loosened in spirit):
  PRECHECK_PASS       if ANY floor_valid grid point clears gate_score >= 1.0 (all 3 held-out roles both
                       consistent AND distinct) -- the fixed DG-analog projection generalizes to
                       held-out roles by construction; the full training cell is worth running.
  PRECHECK_BORDERLINE if the BEST floor_valid grid point clears gate_score >= 2/3 (~0.667) but none
                       clears 1.0 -- escalate n_addr / d_exp / k before committing to the full run; do
                       NOT yet declare fail from an untrained diagnostic alone.
  PRECHECK_FAIL       if NO floor_valid grid point clears 2/3 -- OR if NO grid point's can-fail floor
                       validates at all (floor_invalid_everywhere: the measurement cannot be trusted at
                       any point tried; treat conservatively as FAIL, never as an unvalidated PASS).

This pre-check GATES whether to run the full training cell; it does NOT replace the full cell's
pre-registered HARD-PASS/HARD-FAIL/INVALID bands (those are judged only after real training + eval,
per the plan's own caution that untrained separation is informative but not dispositive).

Run:  .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_precheck_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_precheck_v1.py --full

--self-test uses SYNTHETIC small-scale vectors to validate the measurement logic (consistency / distinct
bucket-count / can-fail floors / grid-sweep / decision-rule thresholding) WITHOUT loading the real frozen
v2 encoder -- per the discipline of not running the real pre-check at production scale from inside a
self-test.
--full loads the REAL encoder + REAL 15-role split and performs the actual measurement (Director runs
this as the gate; exp_dev does not run it at scale).

ASCII-only. No emojis. Deterministic seeding (np.random.default_rng + torch.Generator only; no hash(),
no list(set())). CPU-only, expected <1 minute wall time dominated by the frozen-encoder sentence cache
build (no gradient training).
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_wm_addressing_heldout_role_warmstart_v1 as ho  # noqa: E402
import exp_wm_addressing_dg_fixed_projection_v1 as dgfix  # noqa: E402  -- reuse EXACT mechanism, not a copy

ANCHOR_NAME = "wm_addressing_dg_precheck_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

D_EXP_MULTS_DEFAULT = (2, 4, 8)
K_VALUES_DEFAULT = (4, 8)
N_ADDR_VALUES_DEFAULT = (256, 512, 1024)   # HYPOTHESIZED@this file: N~1000-order regime (the fix)
DG_SEED_DEFAULT = dgfix.DG_SEED            # SAME constant as the full training cell's default
DERANGEMENT_SEED_DEFAULT = 20260730002     # fixed; shuffled-pairing can-fail-floor permutation

HELD_PASS_FRAC = 1.0            # 3/3 held-out roles both consistent AND distinct
HELD_BORDERLINE_FRAC = 2.0 / 3.0  # 2/3 -- lenient floor, well above 1/n_addr chance
FLOOR_SHUFFLED_CONSISTENCY_MAX = 0.20   # shuffled-pairing consistency must stay <= this to certify floor
FLOOR_DEGENERATE_DISTINCT_MAX = 1       # all-identical-rep control must collapse to <=1 distinct bucket


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- measurement primitives ----------------
def pairwise_jaccard_mean(sparse):
    """sparse: [n_roles, d_exp] (post-kwta, zeros elsewhere). Returns mean Jaccard overlap of the
    top-k winner index SETS across all C(n,2) role pairs. Diagnostic only (raw geometric-collision
    measure); NOT the decisive metric."""
    n = sparse.shape[0]
    active = (sparse != 0)
    total, count = 0.0, 0
    for i in range(n):
        ai = active[i]
        for j in range(i + 1, n):
            aj = active[j]
            inter = int((ai & aj).sum().item())
            union = int((ai | aj).sum().item())
            jac = (inter / union) if union > 0 else 0.0
            total += jac
            count += 1
    return total / count if count else 0.0


def distinct_bucket_stats(addr_logits, role_ids, held_out_set):
    """addr_logits: [n_roles, n_addr]. role_ids: list[int] (role id per row, SAME order as addr_logits
    rows). Returns the count of roles whose argmax bucket is unique among ALL rows, plus the
    held-out/train split of that same distinct-mask. Generic over n_addr (the bucket-space cardinality
    is NOT assumed to equal len(role_ids); this is exactly the fix -- v1 always passed n_addr==15)."""
    argmax_bucket = addr_logits.argmax(dim=-1)
    n_addr = addr_logits.shape[-1]
    counts = torch.bincount(argmax_bucket, minlength=n_addr)
    distinct_mask = (counts[argmax_bucket] == 1)
    held_positions = [i for i, r in enumerate(role_ids) if r in held_out_set]
    train_positions = [i for i, r in enumerate(role_ids) if r not in held_out_set]
    n_distinct = int(distinct_mask.sum().item())
    n_held_distinct = int(distinct_mask[held_positions].sum().item()) if held_positions else 0
    n_train_distinct = int(distinct_mask[train_positions].sum().item()) if train_positions else 0
    return {"n_distinct": n_distinct, "n_roles": len(role_ids),
            "n_held_distinct": n_held_distinct, "n_held": len(held_positions),
            "n_train_distinct": n_train_distinct, "n_train": len(train_positions)}


def _fixed_derangement(n, seed):
    """A deterministic derangement (permutation with NO fixed points) of range(n). Used only for the
    shuffled-pairing can-fail-floor control (deterministic seeding per CLAUDE.md; no hash(), no
    list(set()))."""
    rng = np.random.default_rng(seed)
    perm = np.arange(n)
    for _ in range(10000):
        perm = rng.permutation(n)
        if not np.any(perm == np.arange(n)):
            return perm
    raise RuntimeError("could not find a derangement of size %d in 10000 tries" % n)  # pragma: no cover


def run_grid_measurement(role_reps_query, role_reps_assign, role_ids, held_out_set, d_enc,
                          d_exp_mults, k_values, n_addr_values, dg_seed, derangement_seed):
    """role_reps_query / role_reps_assign: [n_roles, d_enc] whitened reps for the SAME roles, in the
    SAME order, from QUERY-context vs ASSIGNMENT-context sentences. Sweeps (d_exp_mult, k, n_addr);
    returns per-point diagnostics + the best floor-valid point + the PRECHECK verdict."""
    n_roles = len(role_ids)
    held_positions = [i for i, r in enumerate(role_ids) if r in held_out_set]
    train_positions = [i for i, r in enumerate(role_ids) if r not in held_out_set]
    n_held = len(held_positions)
    n_train = len(train_positions)
    perm = torch.as_tensor(_fixed_derangement(n_roles, derangement_seed))

    grid = []
    for mult in d_exp_mults:
        d_exp = mult * d_enc
        for k in k_values:
            for n_addr in n_addr_values:
                E, bucket_of = dgfix.make_fixed_projection(d_enc, d_exp, n_addr, dg_seed)

                z_q = role_reps_query @ E.t()
                sparse_q = dgfix.kwta_sparsify(z_q, k)
                addr_q = dgfix.bucket_pool(sparse_q, bucket_of, n_addr)
                argmax_q = addr_q.argmax(dim=-1)

                z_a = role_reps_assign @ E.t()
                sparse_a = dgfix.kwta_sparsify(z_a, k)
                addr_a = dgfix.bucket_pool(sparse_a, bucket_of, n_addr)
                argmax_a = addr_a.argmax(dim=-1)

                jac = pairwise_jaccard_mean(sparse_q)

                # (a) CONSISTENCY: same role, assignment-context address == query-context address
                match = (argmax_q == argmax_a)
                n_match_held = int(match[held_positions].sum().item()) if held_positions else 0
                n_match_train = int(match[train_positions].sum().item()) if train_positions else 0

                # (b) DISTINCTNESS: query-context address uniqueness among ALL n_roles
                dstats = distinct_bucket_stats(addr_q, role_ids, held_out_set)

                # CAN-FAIL FLOOR #1: shuffled-pairing consistency (query[r] vs assign[derangement(r)])
                argmax_a_shuffled = argmax_a[perm]
                shuffled_consistency_frac = float((argmax_q == argmax_a_shuffled).float().mean().item())

                # CAN-FAIL FLOOR #2: all-identical-rep distinctness control
                degenerate_reps = role_reps_query[0:1].expand(n_roles, -1)
                z_deg = degenerate_reps @ E.t()
                sparse_deg = dgfix.kwta_sparsify(z_deg, k)
                addr_deg = dgfix.bucket_pool(sparse_deg, bucket_of, n_addr)
                dstats_deg = distinct_bucket_stats(addr_deg, role_ids, held_out_set)

                held_consistency_frac = (n_match_held / n_held) if n_held else float("nan")
                train_consistency_frac = (n_match_train / n_train) if n_train else float("nan")
                held_distinct_frac = (dstats["n_held_distinct"] / dstats["n_held"]) if dstats["n_held"] else float("nan")
                train_distinct_frac = (dstats["n_train_distinct"] / dstats["n_train"]) if dstats["n_train"] else float("nan")

                floor_valid = bool(shuffled_consistency_frac <= FLOOR_SHUFFLED_CONSISTENCY_MAX
                                    and dstats_deg["n_distinct"] <= FLOOR_DEGENERATE_DISTINCT_MAX)
                gate_score = min(held_consistency_frac, held_distinct_frac)

                point = {
                    "d_exp_mult": mult, "d_exp": d_exp, "k": k, "n_addr": n_addr,
                    "active_set_jaccard_mean": jac,
                    "held_consistency_frac": held_consistency_frac, "n_held_match": n_match_held, "n_held": n_held,
                    "train_consistency_frac": train_consistency_frac, "n_train_match": n_match_train, "n_train": n_train,
                    "held_distinct_frac": held_distinct_frac, "n_held_distinct": dstats["n_held_distinct"],
                    "train_distinct_frac": train_distinct_frac, "n_train_distinct": dstats["n_train_distinct"],
                    "all_distinct_frac": dstats["n_distinct"] / n_roles, "n_distinct": dstats["n_distinct"],
                    "shuffled_consistency_frac": shuffled_consistency_frac,
                    "degenerate_n_distinct": dstats_deg["n_distinct"],
                    "floor_valid": floor_valid,
                    "gate_score": gate_score,
                }
                grid.append(point)
                _log("  d_exp_mult=%d k=%d n_addr=%d: held_consist=%d/%d(%.3f) held_distinct=%d/%d(%.3f) "
                     "shuffled_floor=%.3f degen_floor=%d floor_valid=%s gate_score=%.3f"
                     % (mult, k, n_addr, n_match_held, n_held, held_consistency_frac,
                        dstats["n_held_distinct"], dstats["n_held"], held_distinct_frac,
                        shuffled_consistency_frac, dstats_deg["n_distinct"], floor_valid, gate_score))

    valid_points = [p for p in grid if p["floor_valid"]]
    any_floor_valid = len(valid_points) > 0
    search_space = valid_points if any_floor_valid else grid
    best = max(search_space, key=lambda p: p["gate_score"])

    if not any_floor_valid:
        verdict = "PRECHECK_FAIL"
        msg = ("CAN-FAIL FLOOR NEVER VALIDATED at any (d_exp_mult, k, n_addr) tried (shuffled-pairing "
               "consistency stayed above %.2f and/or the degenerate-rep control failed to collapse to "
               "<=%d distinct bucket at every point) -- the measurement cannot be trusted at any point; "
               "treat conservatively as FAIL rather than report an unvalidated PASS/BORDERLINE. best "
               "(floor-invalid) point: d_exp_mult=%d k=%d n_addr=%d gate_score=%.3f."
               % (FLOOR_SHUFFLED_CONSISTENCY_MAX, FLOOR_DEGENERATE_DISTINCT_MAX,
                  best["d_exp_mult"], best["k"], best["n_addr"], best["gate_score"]))
    elif best["gate_score"] >= HELD_PASS_FRAC:
        verdict = "PRECHECK_PASS"
        msg = ("best floor-valid grid point d_exp_mult=%d k=%d n_addr=%d clears gate_score=%.3f "
               "(all %d/%d held-out roles both CONSISTENT [assignment-context addr == query-context "
               "addr] and DISTINCT [unique among all 15 roles' addresses]) -- the fixed DG-analog "
               "projection generalizes to held-out roles by construction; the full training cell is "
               "worth running."
               % (best["d_exp_mult"], best["k"], best["n_addr"], best["gate_score"],
                  best["n_held"], best["n_held"]))
    elif best["gate_score"] >= HELD_BORDERLINE_FRAC:
        verdict = "PRECHECK_BORDERLINE"
        msg = ("best floor-valid grid point d_exp_mult=%d k=%d n_addr=%d only reaches gate_score=%.3f "
               "(held_consistency=%.3f, held_distinct=%.3f), between the %.3f floor and the %.2f pass "
               "bar -- escalate n_addr / d_exp (larger) or reduce k before committing to the full "
               "training run; do not yet declare PRECHECK_FAIL."
               % (best["d_exp_mult"], best["k"], best["n_addr"], best["gate_score"],
                  best["held_consistency_frac"], best["held_distinct_frac"],
                  HELD_BORDERLINE_FRAC, HELD_PASS_FRAC))
    else:
        verdict = "PRECHECK_FAIL"
        msg = ("NO floor-valid grid point clears gate_score >= %.3f (best: d_exp_mult=%d k=%d n_addr=%d, "
               "gate_score=%.3f, held_consistency=%.3f, held_distinct=%.3f) -- held-out roles are NOT "
               "reliably both consistent and distinct at any (d_exp, k, n_addr) tried; the DG-analog "
               "fixed projection does not separate/align held-out roles from the frozen encoder's "
               "reps. Do NOT run the full training cell; the block is the encoder's representational "
               "geometry, not the addressing mechanism."
               % (HELD_BORDERLINE_FRAC, best["d_exp_mult"], best["k"], best["n_addr"], best["gate_score"],
                  best["held_consistency_frac"], best["held_distinct_frac"]))

    held_vs_train_parity_ok = True
    if best["n_held"] > 0 and best["n_train"] > 0 and any_floor_valid:
        held_vs_train_parity_ok = bool(
            (best["train_consistency_frac"] - best["held_consistency_frac"]) <= 0.34
            and (best["train_distinct_frac"] - best["held_distinct_frac"]) <= 0.34)

    return {"grid": grid, "best": best, "verdict": verdict, "verdict_msg": msg,
            "any_floor_valid": bool(any_floor_valid),
            "held_vs_train_parity_ok": held_vs_train_parity_ok,
            "held_pass_frac": HELD_PASS_FRAC, "held_borderline_frac": HELD_BORDERLINE_FRAC,
            "floor_shuffled_consistency_max": FLOOR_SHUFFLED_CONSISTENCY_MAX,
            "floor_degenerate_distinct_max": FLOOR_DEGENERATE_DISTINCT_MAX}


# ---------------- self-test (SYNTHETIC small-scale; no real encoder load) ----------------
def run_self_test():
    _log("SELF-TEST: role split integrity (reused from ho, no encoder load) ...")
    assert ho.HELD_OUT_SET.isdisjoint(ho.TRAIN_SET)
    assert os.path.exists(ho.V2_CKPT), "v2 checkpoint path missing (would block --full, checked but not loaded): %s" % ho.V2_CKPT

    _log("SELF-TEST: pairwise_jaccard_mean on known-overlap synthetic cases ...")
    identical = torch.tensor([[1.0, 2.0, 0.0, 0.0], [1.0, 2.0, 0.0, 0.0]])
    jac_identical = pairwise_jaccard_mean(identical)
    assert abs(jac_identical - 1.0) < 1e-9, "identical active sets should have Jaccard=1.0, got %.4f" % jac_identical
    disjoint = torch.tensor([[1.0, 2.0, 0.0, 0.0], [0.0, 0.0, 3.0, 4.0]])
    jac_disjoint = pairwise_jaccard_mean(disjoint)
    assert abs(jac_disjoint - 0.0) < 1e-9, "disjoint active sets should have Jaccard=0.0, got %.4f" % jac_disjoint
    partial = torch.tensor([[1.0, 2.0, 0.0, 0.0], [1.0, 0.0, 3.0, 0.0]])   # intersection={0}, union={0,1,2} -> 1/3
    jac_partial = pairwise_jaccard_mean(partial)
    assert abs(jac_partial - (1.0 / 3.0)) < 1e-9, "partial-overlap Jaccard expected 1/3, got %.4f" % jac_partial

    _log("SELF-TEST: distinct_bucket_stats on a synthetic bijection vs a collision case (n_addr != n_roles, "
         "the actual confound fix -- generic bucket-space cardinality) ...")
    d_slots = 5
    bijection_logits = torch.eye(d_slots)          # each row's argmax is its own unique bucket
    stats_bij = distinct_bucket_stats(bijection_logits, list(range(d_slots)), held_out_set=set([0, 1]))
    assert stats_bij["n_distinct"] == d_slots, "bijection case should have ALL roles distinct"
    assert stats_bij["n_held_distinct"] == 2 and stats_bij["n_train_distinct"] == 3
    # n_addr > n_roles case (the fix): 5 roles into 20 buckets, each row a distinct one-hot -- should
    # STILL correctly report all-distinct (function is generic over bucket-space size, not hardcoded 15)
    wide_logits = torch.zeros(d_slots, 20)
    for i in range(d_slots):
        wide_logits[i, i * 3] = 1.0   # spread across a much larger bucket space
    stats_wide = distinct_bucket_stats(wide_logits, list(range(d_slots)), held_out_set=set([0, 1]))
    assert stats_wide["n_distinct"] == d_slots, "wide bucket-space bijection should also be all-distinct"

    collide_logits = torch.tensor([
        [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],   # roles 0,1 collide on bucket 0; role 2 distinct
    ])
    stats_col = distinct_bucket_stats(collide_logits, [0, 1, 2], held_out_set=set([2]))
    assert stats_col["n_distinct"] == 1, "exactly one role (bucket 1) should be distinct"
    assert stats_col["n_held_distinct"] == 1 and stats_col["n_train_distinct"] == 0

    _log("SELF-TEST: _fixed_derangement produces a genuine derangement, deterministic across calls ...")
    perm1 = _fixed_derangement(15, DERANGEMENT_SEED_DEFAULT)
    perm2 = _fixed_derangement(15, DERANGEMENT_SEED_DEFAULT)
    assert np.array_equal(perm1, perm2), "derangement not deterministic for the same seed"
    assert not np.any(perm1 == np.arange(15)), "derangement has a fixed point"
    assert sorted(perm1.tolist()) == list(range(15)), "derangement is not a valid permutation"

    _log("SELF-TEST: make_fixed_projection / kwta_sparsify / bucket_pool import + determinism (reused "
         "from dgfix, not reimplemented) ...")
    E1, b1 = dgfix.make_fixed_projection(8, 32, 5, dg_seed=999)
    E2, b2 = dgfix.make_fixed_projection(8, 32, 5, dg_seed=999)
    assert torch.equal(E1, E2) and torch.equal(b1, b2)

    _log("SELF-TEST: run_grid_measurement end-to-end on SYNTHETIC near-orthogonal role reps, "
         "query==assign (the 'optimistic case' -- clean geometry, perfectly consistent by construction) "
         "-- verifies the BIRTHDAY-PARADOX FIX: distinctness at n_addr=1024 must beat n_addr=15 for the "
         "SAME clean geometry ...")
    g = torch.Generator().manual_seed(42)
    n_roles_toy, d_enc_toy = 15, 32
    toy_reps = torch.eye(n_roles_toy, d_enc_toy) * 5.0 + 0.05 * torch.randn(n_roles_toy, d_enc_toy, generator=g)
    toy_role_ids = list(range(n_roles_toy))
    toy_held = set(ho.HELD_OUT_ROLES)  # reuse the real split's held-out ids (0..14 range matches)
    result_clean = run_grid_measurement(toy_reps, toy_reps.clone(), toy_role_ids, toy_held, d_enc_toy,
                                         d_exp_mults=(2,), k_values=(4,), n_addr_values=(15, 1024),
                                         dg_seed=DG_SEED_DEFAULT, derangement_seed=DERANGEMENT_SEED_DEFAULT)
    pts_by_naddr = {p["n_addr"]: p for p in result_clean["grid"]}
    assert pts_by_naddr[1024]["all_distinct_frac"] >= pts_by_naddr[15]["all_distinct_frac"], (
        "FIX REGRESSION: enlarging n_addr from 15 to 1024 should not make distinctness WORSE for "
        "identical clean geometry -- got n_addr=15: %.3f, n_addr=1024: %.3f"
        % (pts_by_naddr[15]["all_distinct_frac"], pts_by_naddr[1024]["all_distinct_frac"]))
    # query==assign identical -> consistency must be 1.0 at EVERY point (trivial, but asserts the
    # consistency computation itself is correct: same input -> same address, always).
    for p in result_clean["grid"]:
        assert abs(p["held_consistency_frac"] - 1.0) < 1e-9, (
            "query==assign identical reps must give held_consistency_frac=1.0, got %.4f at n_addr=%d"
            % (p["held_consistency_frac"], p["n_addr"]))
    assert result_clean["verdict"] in ("PRECHECK_PASS", "PRECHECK_BORDERLINE", "PRECHECK_FAIL")

    _log("SELF-TEST: run_grid_measurement on a DEGENERATE all-identical-rep synthetic case -- expect "
         "PRECHECK_FAIL via distinctness (every role collides into 1 bucket regardless of n_addr) ...")
    degenerate_reps = torch.ones(n_roles_toy, d_enc_toy) * 5.0   # all roles IDENTICAL -> must collide
    result_degenerate = run_grid_measurement(degenerate_reps, degenerate_reps.clone(), toy_role_ids, toy_held,
                                              d_enc_toy, d_exp_mults=(2,), k_values=(4,), n_addr_values=(1024,),
                                              dg_seed=DG_SEED_DEFAULT, derangement_seed=DERANGEMENT_SEED_DEFAULT)
    assert result_degenerate["verdict"] == "PRECHECK_FAIL", (
        "all-identical role reps must PRECHECK_FAIL (every role hashes to the same bucket by "
        "construction, even at n_addr=1024), got %s" % result_degenerate["verdict"])
    assert result_degenerate["best"]["n_distinct"] <= 1, (
        "identical reps should collapse to at most 1 distinct bucket")
    assert result_degenerate["best"]["degenerate_n_distinct"] <= 1

    _log("SELF-TEST: CAN-FAIL FLOOR -- a RANDOM/INDEPENDENT-encoder control (query and assign reps drawn "
         "independently per role, no shared identity structure) must PRECHECK_FAIL via consistency (no "
         "legitimate reason an independent draw should reproduce the same address) ...")
    g2 = torch.Generator().manual_seed(4242)
    random_query = torch.randn(n_roles_toy, d_enc_toy, generator=g2) * 3.0
    random_assign = torch.randn(n_roles_toy, d_enc_toy, generator=g2) * 3.0   # INDEPENDENT draw, same role
    result_random = run_grid_measurement(random_query, random_assign, toy_role_ids, toy_held, d_enc_toy,
                                          d_exp_mults=(2, 4), k_values=(4, 8), n_addr_values=(256, 1024),
                                          dg_seed=DG_SEED_DEFAULT, derangement_seed=DERANGEMENT_SEED_DEFAULT)
    assert result_random["verdict"] == "PRECHECK_FAIL", (
        "independent-draw (no identity-preserving structure) control must PRECHECK_FAIL, got %s "
        "(best gate_score=%.3f)" % (result_random["verdict"], result_random["best"]["gate_score"]))

    _log("SELF-TEST PASS")
    return {"jaccard_checks": {"identical": jac_identical, "disjoint": jac_disjoint, "partial": jac_partial},
            "distinct_bucket_checks": {"bijection": stats_bij, "wide": stats_wide, "collision": stats_col},
            "derangement_deterministic": True,
            "synthetic_clean_verdict": result_clean["verdict"],
            "synthetic_clean_distinct_by_naddr": {int(k): v["all_distinct_frac"] for k, v in pts_by_naddr.items()},
            "synthetic_degenerate_verdict": result_degenerate["verdict"],
            "synthetic_random_independent_verdict": result_random["verdict"]}


# ---------------- full pre-check (REAL encoder; Director runs this, not exp_dev at scale) ----------------
def run_full_precheck(d_exp_mults, k_values, n_addr_values, dg_seed, derangement_seed):
    _log("FULL PRECHECK: loading REAL frozen v2 encoder + building sentence cache ...")
    assert os.path.exists(ho.V2_CKPT), "v2 checkpoint missing: %s" % ho.V2_CKPT
    enc = ho.base.FrozenV2Encoder(ho.V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = ho.rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    _log("FULL PRECHECK: building an UNTRAINED role_query (shared, random-init, never optimized) + "
         "pca_whiten conditioning ...")
    wm = ho.build_wm(seed=7, enc=enc, cond=cond, kind="pca_whiten")
    with torch.no_grad():
        slot_u, _ = wm._role_reps()

    role_ids = list(range(ho.S_TARGET_TOTAL))
    q_idxs = [enc.idx_of(ho.QUERY_TEMPLATE.format(slot=ho.SLOT_NOUNS[r])) for r in role_ids]
    a_idxs = [enc.idx_of(ho.EVENT_TEMPLATES[0].format(slot=ho.SLOT_NOUNS[r], fill=ho.COLORS[0]))
              for r in role_ids]
    role_reps_query = slot_u[torch.tensor(q_idxs)].detach()   # [15, d_enc], whitened, untrained role_query
    role_reps_assign = slot_u[torch.tensor(a_idxs)].detach()  # [15, d_enc], SAME roles, ASSIGNMENT context

    _log("FULL PRECHECK: sweeping (d_exp_mult, k, n_addr) grid, no gradient training ...")
    result = run_grid_measurement(role_reps_query, role_reps_assign, role_ids, ho.HELD_OUT_SET, enc.d,
                                   d_exp_mults, k_values, n_addr_values, dg_seed, derangement_seed)
    result["n_cached"] = n_cached
    result["d_enc"] = enc.d
    return result


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--d-exp-mults", type=int, nargs="+", default=list(D_EXP_MULTS_DEFAULT))
    ap.add_argument("--k-values", type=int, nargs="+", default=list(K_VALUES_DEFAULT))
    ap.add_argument("--n-addr-values", type=int, nargs="+", default=list(N_ADDR_VALUES_DEFAULT))
    ap.add_argument("--dg-seed", type=int, default=DG_SEED_DEFAULT)
    ap.add_argument("--derangement-seed", type=int, default=DERANGEMENT_SEED_DEFAULT)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    _write_start_marker(OUTPUT_DIR, run_mode)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (jaccard + distinct-bucket-stats [generic n_addr] + "
                           "derangement + fixed-projection-import + synthetic clean/degenerate/"
                           "random-independent grid-measurement sanity incl. can-fail floors, no real "
                           "encoder load)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    result = run_full_precheck(args.d_exp_mults, args.k_values, args.n_addr_values, args.dg_seed,
                                args.derangement_seed)
    elapsed = time.perf_counter() - t0
    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": result["verdict"], "verdict_msg": result["verdict_msg"],
        "summary": "%s | %s" % (result["verdict"], result["verdict_msg"][:200]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "grid": result["grid"], "best": result["best"],
        "any_floor_valid": result["any_floor_valid"],
        "held_vs_train_parity_ok": result["held_vs_train_parity_ok"],
        "held_pass_frac": result["held_pass_frac"], "held_borderline_frac": result["held_borderline_frac"],
        "floor_shuffled_consistency_max": result["floor_shuffled_consistency_max"],
        "floor_degenerate_distinct_max": result["floor_degenerate_distinct_max"],
        "n_cached_sentences": result["n_cached"], "d_enc": result["d_enc"],
        "params": {"d_exp_mults": args.d_exp_mults, "k_values": args.k_values,
                   "n_addr_values": args.n_addr_values, "dg_seed": args.dg_seed,
                   "derangement_seed": args.derangement_seed,
                   "role_split_seed": ho.ROLE_SPLIT_SEED, "train_roles": ho.TRAIN_ROLES,
                   "held_out_roles": ho.HELD_OUT_ROLES, "v2_ckpt": os.path.relpath(ho.V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true"})
    _log("VERDICT: %s" % result["verdict"])
    _log("  %s" % result["verdict_msg"])
    _log("DONE full precheck in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
