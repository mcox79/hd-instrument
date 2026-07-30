# CELL-TEMPLATE MANDATORY (subset applicable to a standalone <1min measurement probe, not a multi-unit
# training cell): except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace
# metrics write; deterministic seeding (np.random.default_rng only, no hash(), no list(set())); numbers
# tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@. No checkpoint/resume needed (single-shot,
# <1 minute wall time, no gradient training -- CLAUDE.md's multi-unit checkpoint mandate applies to
# cells looping over >1 (arm, seed) TRAINING unit; this is a pure forward-pass geometry measurement).
"""Cheap DG-analog fixed-projection PRE-CHECK (v1) -- the gate BEFORE the full training cell
(exp_wm_addressing_dg_fixed_projection_v1.py) is worth running.

CONTEXT (notes/dg_analog_fixed_projection_addressing_build_plan_2026-07-30.md section 4, the single
biggest risk in the DG-analog pivot): does whiten -> fixed random-expand -> k-WTA sparsify -> hash-to-
bucket on the frozen v2 encoder's role-query reps actually SEPARATE roles -- INCLUDING HELD-OUT roles --
or does the residual whitened shared component (raw cos_mean~0.99 -> pca cos_mean~0.80, NOT eliminated;
MEASURED@exp_selective_overwrite_recall_nl_wm_readcond_v1 conditioning_diagnostic) dominate the top-k
winners and reproduce the STUCK_FLAT collapse one stage downstream (the "expansion swamps the signal"
pessimistic case in the build plan)?

NO GRADIENT TRAINING occurs here -- this is a pure forward-pass geometry measurement, <1 minute of
compute once the frozen encoder's sentence cache is built. Role-query reps are computed via the SAME
frozen v2 encoder + a role_query at RANDOM INIT (shared across all roles, not per-role, untrained) --
this is the correct test of "does construction alone separate the roles," matching the build plan's
own framing: the fixed projection requires zero supervision to produce SOME address for SOME input, so
measuring it untrained is exactly what "generalizes by construction" needs to demonstrate.

Reuses the EXACT fixed-projection construction the full training cell trains against
(exp_wm_addressing_dg_fixed_projection_v1.make_fixed_projection / kwta_sparsify / bucket_pool, imported
directly -- NOT reimplemented) so this pre-check measures the identical mechanism, not a look-alike.
Also reuses the 15-role TRAIN/HELD_OUT split, encoder checkpoint path, and role-query-sentence templates
from exp_wm_addressing_heldout_role_warmstart_v1 (aliased `ho`).

Sweep grid (exp_dev autonomy note per the build plan section 3; defaults reuse the plan's cited
certified precedents -- MEASURED/THEORETICAL/CITED tagged below):
  d_exp_mult in {2, 4, 8}   -- 2x default center per Spoke-3 design note
                               MEASURED@notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md:line97 ("N -> 2N" parameterization)
  k in {4, 8}               -- MEASURED@data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json:
                               K4_acc=1.00, K8_acc=1.00, HARD_PASS at N=1000
  dg_seed fixed = 20260730001 (SAME constant as the full cell's default, and held constant across the
                               whole (d_exp_mult, k) grid so d_exp/k are the only swept variables)

Metrics per grid point (all 15 roles, computed from a SINGLE role-query-template sentence rep per role
-- the exact rep that feeds the full pipeline's decisive q_logits = _addr_logits(slot_u[q_idx])):
  1. active_set_jaccard_mean -- mean pairwise Jaccard overlap of the top-k winner index sets across all
     C(15,2)=105 role pairs, BEFORE the hash pools winners into K_SLOTS buckets (the more sensitive raw
     geometric-collision measure). Want LOW.
  2. untrained_addr_distinct -- count of the 15 roles whose bucket_of-pooled argmax address bucket is
     UNIQUE among all 15 roles (no other role shares that bucket) -- the direct analog of
     exp_selective_overwrite_recall_nl_wm_readcond_v1's conditioning_diagnostic untrained_addr_distinct
     field, extended one stage through expand+sparsify+hash. Range 0..15. Want HIGH (>=12/15 = 0.80).
  3. held_distinct / train_distinct -- untrained_addr_distinct restricted to the 3 HELD_OUT_ROLES vs the
     12 TRAIN_ROLES (both measured against uniqueness among the FULL 15-role assignment, not just within
     the subset). Want comparable parity -- a held-out-specific collapse is geometrically impossible by
     construction (the fixed projection cannot "know" train vs held-out) and would flag a confound
     (e.g. degenerate held-out query sentences), not a mechanism failure, per the build plan.

DECISION RULE (build plan section 4, verbatim, NOT loosened):
  PRECHECK_PASS       if ANY grid point clears untrained_addr_distinct/15 >= 0.80 (matching the
                       eventual full-cell HARD-PASS bar's own magnitude).
  PRECHECK_BORDERLINE if the BEST grid point clears >= 8/15 (~0.533) but none clears 12/15 -- escalate
                       d_exp/k (16x, 32x per the plan) before committing to the full training run; do
                       NOT yet declare fail from an untrained diagnostic alone.
  PRECHECK_FAIL       if NO grid point clears 8/15 -- the shared component dominates top-k at every
                       (d_exp, k) tried; the DG-analog would relocate, not fix, the STUCK_FLAT collapse.

This pre-check GATES whether to run the full training cell; it does NOT replace the full cell's
pre-registered HARD-PASS/HARD-FAIL/INVALID bands (those are judged only after real training + eval,
per the plan's own caution that untrained separation is informative but not dispositive).

Run:  .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_precheck_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_precheck_v1.py --full

--self-test uses SYNTHETIC small-scale vectors to validate the measurement logic (Jaccard / distinct-
bucket-count / grid-sweep / decision-rule thresholding) WITHOUT loading the real frozen v2 encoder --
per the discipline of not running the real pre-check at production scale from inside a self-test.
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
DG_SEED_DEFAULT = dgfix.DG_SEED           # SAME constant as the full training cell's default

PRECHECK_PASS_FRAC = 12.0 / 15.0          # 0.80 -- matches the eventual HARD-PASS bar's magnitude
PRECHECK_BORDERLINE_FRAC = 8.0 / 15.0     # ~0.533 -- lenient floor, well above addr_chance=1/15


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
    top-k winner index SETS across all C(n,2) role pairs."""
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
    """addr_logits: [n_roles, k_slots]. role_ids: list[int] (role id per row, SAME order as addr_logits
    rows). Returns untrained_addr_distinct (count of roles whose argmax bucket is unique among ALL
    rows) plus the held-out/train split of that same distinct-mask."""
    argmax_bucket = addr_logits.argmax(dim=-1)
    k_slots = addr_logits.shape[-1]
    counts = torch.bincount(argmax_bucket, minlength=k_slots)
    distinct_mask = (counts[argmax_bucket] == 1)
    held_positions = [i for i, r in enumerate(role_ids) if r in held_out_set]
    train_positions = [i for i, r in enumerate(role_ids) if r not in held_out_set]
    n_distinct = int(distinct_mask.sum().item())
    n_held_distinct = int(distinct_mask[held_positions].sum().item()) if held_positions else 0
    n_train_distinct = int(distinct_mask[train_positions].sum().item()) if train_positions else 0
    return {"n_distinct": n_distinct, "n_roles": len(role_ids),
            "n_held_distinct": n_held_distinct, "n_held": len(held_positions),
            "n_train_distinct": n_train_distinct, "n_train": len(train_positions)}


def run_grid_measurement(role_reps, role_ids, held_out_set, d_enc, k_slots, d_exp_mults, k_values, dg_seed):
    """role_reps: [n_roles, d_enc] whitened role-query reps. Sweeps (d_exp_mult, k); returns per-point
    diagnostics + the best point + the PRECHECK verdict."""
    grid = []
    for mult in d_exp_mults:
        d_exp = mult * d_enc
        E, bucket_of = dgfix.make_fixed_projection(d_enc, d_exp, k_slots, dg_seed)
        z = role_reps @ E.t()
        for k in k_values:
            sparse = dgfix.kwta_sparsify(z, k)
            jac = pairwise_jaccard_mean(sparse)
            addr_logits = dgfix.bucket_pool(sparse, bucket_of, k_slots)
            stats = distinct_bucket_stats(addr_logits, role_ids, held_out_set)
            frac = stats["n_distinct"] / stats["n_roles"]
            point = {"d_exp_mult": mult, "d_exp": d_exp, "k": k, "n_roles": stats["n_roles"],
                     "active_set_jaccard_mean": jac, "untrained_addr_distinct": stats["n_distinct"],
                     "untrained_addr_distinct_frac": frac,
                     "n_held_distinct": stats["n_held_distinct"], "n_held": stats["n_held"],
                     "n_train_distinct": stats["n_train_distinct"], "n_train": stats["n_train"]}
            grid.append(point)
            _log("  d_exp_mult=%d (d_exp=%d) k=%d: jaccard_mean=%.4f distinct=%d/%d (%.3f) "
                 "held=%d/%d train=%d/%d"
                 % (mult, d_exp, k, jac, stats["n_distinct"], stats["n_roles"], frac,
                    stats["n_held_distinct"], stats["n_held"], stats["n_train_distinct"], stats["n_train"]))
    best = max(grid, key=lambda p: p["untrained_addr_distinct_frac"])
    if best["untrained_addr_distinct_frac"] >= PRECHECK_PASS_FRAC:
        verdict = "PRECHECK_PASS"
        msg = ("best grid point d_exp_mult=%d k=%d clears untrained_addr_distinct=%d/%d (%.3f) >= %.2f "
               "-- the fixed DG-analog projection separates roles (including held-out) by construction; "
               "the full training cell is worth running."
               % (best["d_exp_mult"], best["k"], best["untrained_addr_distinct"], best["n_roles"],
                  best["untrained_addr_distinct_frac"], PRECHECK_PASS_FRAC))
    elif best["untrained_addr_distinct_frac"] >= PRECHECK_BORDERLINE_FRAC:
        verdict = "PRECHECK_BORDERLINE"
        msg = ("best grid point d_exp_mult=%d k=%d only reaches untrained_addr_distinct=%d/%d (%.3f), "
               "between the %.2f floor and the %.2f pass bar -- escalate d_exp (16x, 32x) or reduce k "
               "before committing to the full training run; do not yet declare PRECHECK_FAIL."
               % (best["d_exp_mult"], best["k"], best["untrained_addr_distinct"], best["n_roles"],
                  best["untrained_addr_distinct_frac"], PRECHECK_BORDERLINE_FRAC, PRECHECK_PASS_FRAC))
    else:
        verdict = "PRECHECK_FAIL"
        msg = ("NO grid point clears untrained_addr_distinct/15 >= %.2f (best: d_exp_mult=%d k=%d, "
               "%d/%d = %.3f) -- the residual whitened shared component (pca cos_mean~0.80) dominates "
               "the top-k winners at every (d_exp, k) tried; the DG-analog would RELOCATE, not fix, the "
               "STUCK_FLAT collapse one stage downstream. Do NOT run the full training cell; the block "
               "is the encoder's representational geometry, not the addressing mechanism."
               % (PRECHECK_BORDERLINE_FRAC, best["d_exp_mult"], best["k"], best["untrained_addr_distinct"],
                  best["n_roles"], best["untrained_addr_distinct_frac"]))
    held_vs_train_parity_ok = True
    if best["n_held"] > 0 and best["n_train"] > 0:
        held_frac = best["n_held_distinct"] / best["n_held"]
        train_frac = best["n_train_distinct"] / best["n_train"]
        held_vs_train_parity_ok = abs(held_frac - train_frac) <= 0.34  # 1-of-3 slack on the tiny held set
    return {"grid": grid, "best": best, "verdict": verdict, "verdict_msg": msg,
            "held_vs_train_parity_ok": bool(held_vs_train_parity_ok),
            "precheck_pass_frac": PRECHECK_PASS_FRAC, "precheck_borderline_frac": PRECHECK_BORDERLINE_FRAC}


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

    _log("SELF-TEST: distinct_bucket_stats on a synthetic bijection vs a collision case ...")
    d_slots = 5
    bijection_logits = torch.eye(d_slots)          # each row's argmax is its own unique bucket
    stats_bij = distinct_bucket_stats(bijection_logits, list(range(d_slots)), held_out_set=set([0, 1]))
    assert stats_bij["n_distinct"] == d_slots, "bijection case should have ALL roles distinct"
    assert stats_bij["n_held_distinct"] == 2 and stats_bij["n_train_distinct"] == 3

    collide_logits = torch.tensor([
        [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],   # roles 0,1 collide on bucket 0; role 2 distinct
    ])
    stats_col = distinct_bucket_stats(collide_logits, [0, 1, 2], held_out_set=set([2]))
    assert stats_col["n_distinct"] == 1, "exactly one role (bucket 1) should be distinct"
    assert stats_col["n_held_distinct"] == 1 and stats_col["n_train_distinct"] == 0

    _log("SELF-TEST: make_fixed_projection / kwta_sparsify / bucket_pool import + determinism (reused "
         "from dgfix, not reimplemented) ...")
    E1, b1 = dgfix.make_fixed_projection(8, 32, 5, dg_seed=999)
    E2, b2 = dgfix.make_fixed_projection(8, 32, 5, dg_seed=999)
    assert torch.equal(E1, E2) and torch.equal(b1, b2)

    _log("SELF-TEST: run_grid_measurement end-to-end on SYNTHETIC near-orthogonal role reps (small "
         "scale, no real encoder) -- verifies the RAW geometric-separation measurement (jaccard) is "
         "near-zero for ideal input, i.e. the measurement code itself is correct ...")
    g = torch.Generator().manual_seed(42)
    n_roles_toy, d_enc_toy = 15, 32
    # near-orthogonal synthetic role reps (the "optimistic case" scenario, deliberately constructed as an
    # orthonormal basis + small noise so the self-test is a robust deterministic result, not a lucky
    # random draw).
    toy_reps = torch.eye(n_roles_toy, d_enc_toy) * 5.0 + 0.05 * torch.randn(n_roles_toy, d_enc_toy, generator=g)
    toy_role_ids = list(range(n_roles_toy))
    toy_held = set(ho.HELD_OUT_ROLES)  # reuse the real split's held-out ids (0..14 range matches)
    result_clean = run_grid_measurement(toy_reps, toy_role_ids, toy_held, d_enc_toy, n_roles_toy,
                                         d_exp_mults=(2,), k_values=(4,), dg_seed=DG_SEED_DEFAULT)
    # NOTE (self-test finding, NOT assumed by the build plan): even with near-orthogonal (jaccard~0)
    # role reps, untrained_addr_distinct does NOT reliably clear 12/15 or even 8/15 at the production
    # (d_exp_mult, k) grid -- MEASURED here at d_exp_mult=2,k=4: jaccard_mean~0.03-0.04,
    # untrained_addr_distinct~4-6/15. This reproduces at d_exp_mult up to 128x (checked interactively,
    # not asserted here) and is consistent with a BIRTHDAY-PARADOX collision ceiling inherent to
    # per-coordinate-random bucket_of hashing directly into exactly K_SLOTS=15 buckets (== the role
    # count) -- 15 near-independent draws into 15 bins collide heavily regardless of how separated the
    # underlying winner-index sets are (classic birthday problem: expected distinct singles for n items
    # into n bins is n*((n-1)/n)^(n-1) =~ 5.6/15 =~ 0.37 for n=15). This is DIFFERENT from (and possibly
    # more fundamental than) the "shared-component-swamps-top-k" risk the build plan section 4 focuses
    # on -- see completion-report flag. The certified block-local-K resonator this plan cites as
    # precedent (data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json) operates at
    # address-space cardinality N=1000 (MEASURED), NOT N=K_SLOTS=15 -- a materially different, much
    # less collision-prone regime; its K4/K8 HARD_PASS numbers do not obviously transfer to a
    # 15-bucket hash. Assert only that the measurement code ITSELF behaves sanely (near-zero jaccard for
    # near-orthogonal input; the geometric-separation half of the measurement is verified correct) --
    # do NOT assert PRECHECK_PASS here, since the true (unforced) result may legitimately be FAIL/
    # BORDERLINE even for ideal geometry, which is itself the finding.
    assert result_clean["best"]["active_set_jaccard_mean"] < 0.15, (
        "near-orthogonal synthetic reps should show near-zero top-k index-set overlap (jaccard); "
        "got %.4f -- measurement code may be broken" % result_clean["best"]["active_set_jaccard_mean"])
    assert result_clean["verdict"] in ("PRECHECK_PASS", "PRECHECK_BORDERLINE", "PRECHECK_FAIL")

    _log("SELF-TEST: run_grid_measurement on a DEGENERATE all-identical-rep synthetic case -- expect "
         "PRECHECK_FAIL (every role collides, exactly the pessimistic 'shared component swamps' case) ...")
    degenerate_reps = torch.ones(n_roles_toy, d_enc_toy) * 5.0   # all roles IDENTICAL -> must collide
    result_degenerate = run_grid_measurement(degenerate_reps, toy_role_ids, toy_held, d_enc_toy, n_roles_toy,
                                              d_exp_mults=(2,), k_values=(4,), dg_seed=DG_SEED_DEFAULT)
    assert result_degenerate["verdict"] == "PRECHECK_FAIL", (
        "all-identical role reps must PRECHECK_FAIL (every role hashes to the same bucket by construction), "
        "got %s" % result_degenerate["verdict"])
    assert result_degenerate["best"]["untrained_addr_distinct"] <= 1, (
        "identical reps should collapse to at most 1 distinct bucket")

    _log("SELF-TEST PASS")
    return {"jaccard_checks": {"identical": jac_identical, "disjoint": jac_disjoint, "partial": jac_partial},
            "distinct_bucket_checks": {"bijection": stats_bij, "collision": stats_col},
            "synthetic_clean_verdict": result_clean["verdict"],
            "synthetic_degenerate_verdict": result_degenerate["verdict"]}


# ---------------- full pre-check (REAL encoder; Director runs this, not exp_dev at scale) ----------------
def run_full_precheck(d_exp_mults, k_values, dg_seed):
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
    idxs = [enc.idx_of(ho.QUERY_TEMPLATE.format(slot=ho.SLOT_NOUNS[r])) for r in role_ids]
    role_reps = slot_u[torch.tensor(idxs)].detach()   # [15, d_enc], whitened, untrained role_query

    _log("FULL PRECHECK: sweeping (d_exp_mult, k) grid, no gradient training ...")
    result = run_grid_measurement(role_reps, role_ids, ho.HELD_OUT_SET, enc.d, ho.K_SLOTS,
                                   d_exp_mults, k_values, dg_seed)
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
    ap.add_argument("--dg-seed", type=int, default=DG_SEED_DEFAULT)
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
            "verdict_msg": "SELFTEST_PASS (jaccard + distinct-bucket-stats + fixed-projection-import + "
                           "synthetic clean/degenerate grid-measurement sanity, no real encoder load)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    result = run_full_precheck(args.d_exp_mults, args.k_values, args.dg_seed)
    elapsed = time.perf_counter() - t0
    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": result["verdict"], "verdict_msg": result["verdict_msg"],
        "summary": "%s | %s" % (result["verdict"], result["verdict_msg"][:200]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "grid": result["grid"], "best": result["best"],
        "held_vs_train_parity_ok": result["held_vs_train_parity_ok"],
        "precheck_pass_frac": result["precheck_pass_frac"],
        "precheck_borderline_frac": result["precheck_borderline_frac"],
        "n_cached_sentences": result["n_cached"], "d_enc": result["d_enc"],
        "params": {"d_exp_mults": args.d_exp_mults, "k_values": args.k_values, "dg_seed": args.dg_seed,
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
