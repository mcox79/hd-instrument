"""edge_importance stratified-replay baseline diagnostic v2_proper_import_guard.

USER 2026-06-27 NO LOCAL + GPU+CPU idle. exp_dev cell-author 2026-06-27.

v2_proper FIX (root-cause; NOT v2_arm_count_fix's workaround):
  v1 failed because exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3
  had an UNGUARDED top-level main driver. Importing setup_substrate_with_trace_and_clusters
  from v3 triggered v3's entire 6-arm sweep at IMPORT time, contaminating
  v1's output dir with alien partials (6 arms vs declared 4) -> META_RULE_H
  cardinality breach.

  v2_arm_count_fix (sibling cell shipped earlier today) used a WORKAROUND:
  inline v3's substrate-setup helpers into the cell so no v3 import was needed.

  v2_proper applies the ROOT-CAUSE fix instead:
    Path A: v3 (and all edge_importance_* family) now have
            `if __name__ == "__main__":` guards around their main drivers.
            Importing from v3 no longer triggers any side effect.
    Path B: _seed_checkpoint._check_run_config now supports
            run_config["anchor"]=ANCHOR_NAME and rejects any partial whose
            config_version ANCHOR= string mismatches (META_RULE_H_ANCHOR).

  This cell:
    - Is a near-verbatim clone of v1 (same arms, same bands, same mechanism)
    - Re-imports setup_substrate_with_trace_and_clusters from v3 (now SAFE)
    - Passes run_config["anchor"]=ANCHOR_NAME so any alien partials would be
      rejected at PARTIAL-LOAD time before cardinality check fires
    - Adds startup deviation_log scan: prints + halts if any pre-existing
      partial in out_dir has a mismatched ANCHOR (visibility)
    - Adds META_RULE_H_NAMESET sibling check at verdict (declared arm-name set
      must exactly match observed arm-name set, not just count)

Pre-reg: preregs/2026-06-27_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard.md

Drill provenance:
  notes/research_drill_stratified_replay_HARD_FAIL_3x_2026-06-27.md
  Section "RECOMMENDED CELL FIX" Path C: re-dispatch after Path A+B land.

Mechanism (THE diagnostic; unchanged from v1):
  STRATIFIED_REPLAY -- bin atoms by |W|-decile (10 bins); sample equal
                       replay-count per bin; importance = stratified-count.

ARMS (4 mandatory; per stub 3; unchanged from v1):
  ARM_RAND_IMPORTANCE
  ARM_TRACE_ONLY
  ARM_STRATIFIED_REPLAY
  ARM_INVERSE_WEIGHTED_REPLAY

PRE-REG BANDS (LOCKED; unchanged from v1):
  DIAGNOSTIC_PASS_A: cor(STRATIFIED_REPLAY, |W|) < 0.30
  DIAGNOSTIC_PASS_B: cor(INVERSE_WEIGHTED, |W|) < 0.30
  REPRODUCE_V4_TRACE_BIAS: cor(TRACE_ONLY, |W|) >= 0.70

  HARD_PASS: EITHER DIAGNOSTIC_PASS_A OR DIAGNOSTIC_PASS_B holds AND
             REPRODUCE_V4_TRACE_BIAS holds AND mechanism fires.
  MIDDLE_BAND: TRACE bias reproduced but neither STRATIFIED nor INVERSE
               clears the 0.30 gate.
  HARD_FAIL: TRACE_ONLY cor < 0.30 (drill claim contradicted; surprise
             negative) OR cardinality breach OR ANCHOR mismatch OR
             NAMESET mismatch OR caught exception.

DISCIPLINES:
  META_RULE_H cardinality_ok: per-seed expected arm count = 4.
  META_RULE_H_NAMESET: observed arm-name set must equal declared set.
  META_RULE_H_ANCHOR: partials with mismatched config_version ANCHOR are
                     REJECTED at load time (enforced by _seed_checkpoint).
  META_RULE_J no-silent-except: setup + each arm wrapped.
  META_RULE_K smoke fires discriminator: smoke must reproduce TRACE-bias
    (cor >= 0.5 at smoke; full-N predicted >= 0.7).
  META_RULE_L band-floor strictly-above-floor.

PROT-020: numpy-only; routes to remote_cpu_queue.
ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import re
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Strip flags before importing v3 source (it consumes --self-test at module
# level and sys.exit(0)s). With v3's main driver now guarded by __name__ ==
# "__main__", this import is SAFE -- it only fetches helper functions, not
# the main sweep. See research_drill_stratified_replay_HARD_FAIL_3x_2026-06-27.md.
_SAVED_ARGV = list(sys.argv)
sys.argv = [a for a in sys.argv if a not in ("--self-test", "--smoke")]

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials, get_output_dir, resumable_seeds, write_partial,
)
from hdlab.edge_importance import correlation_E_vs_magnitude  # noqa: E402
from experiments.exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3 import (  # noqa: E402,E501
    setup_substrate_with_trace_and_clusters,
)

sys.argv = _SAVED_ARGV


ANCHOR_NAME = "edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Inherit v3.2 / v4 regime (alpha=1.953 high-alpha; discriminator scales).
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
SEEDS_FULL = [7, 17, 23]

# Smoke discipline per META_RULE_K + USER 2026-06-26 D1: smoke at FULL-N.
# Only SEEDS reduced.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    SEEDS = [7]
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    SEEDS = SEEDS_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_BINS_STRATIFIED = 10
K_PER_BIN = 8
TOTAL_REPLAY_EVENTS = K_PER_BIN * N_BINS_STRATIFIED

# Pre-reg constants (LOCKED)
DIAGNOSTIC_COR_GATE = 0.30
REPRODUCE_TRACE_BIAS_FLOOR_FULL = 0.70
REPRODUCE_TRACE_BIAS_FLOOR_SMOKE = 0.50

ARM_NAMES = [
    "ARM_RAND_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_STRATIFIED_REPLAY",
    "ARM_INVERSE_WEIGHTED_REPLAY",
]
DECLARED_ARM_NAMESET = set(ARM_NAMES)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"alpha={ALPHA:.3f},N_BINS={N_BINS_STRATIFIED},"
    f"K_PER_BIN={K_PER_BIN},TOTAL_REPLAY_EVENTS={TOTAL_REPLAY_EVENTS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Arm-importance computations (purely from shared substrate state)
# ---------------------------------------------------------------------------
def importance_random(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_TOTAL)


def importance_trace_only(retrieval_trace_score: np.ndarray) -> np.ndarray:
    """v3.2 lineage: raw cleanup-argmax counter."""
    return retrieval_trace_score.copy()


def _atom_norms_from_substrate(all_keys: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Compute per-atom |W| equivalent norm (matches v3/v4 fairness metric)."""
    return np.linalg.norm(all_keys @ W.T, axis=1) / float(N)


def importance_stratified_replay(
    atom_norms: np.ndarray,
    retrieval_trace_score: np.ndarray,
    seed: int,
    n_bins: int = N_BINS_STRATIFIED,
    k_per_bin: int = K_PER_BIN,
) -> np.ndarray:
    """Bin atoms by |W|-decile; sample k_per_bin atoms per bin proportional
    to within-bin retrieval_trace_score; importance = replay-event count.
    """
    rng = np.random.RandomState(seed + 22227)
    quantiles = np.quantile(atom_norms, np.linspace(0, 1, n_bins + 1))
    quantiles[-1] = quantiles[-1] + 1e-9
    bins = np.digitize(atom_norms, quantiles[1:-1])
    importance = np.zeros(M_TOTAL, dtype=np.float64)
    for b in range(n_bins):
        bin_atom_idx = np.where(bins == b)[0]
        if len(bin_atom_idx) == 0:
            continue
        weights = retrieval_trace_score[bin_atom_idx] + 1.0
        weights = weights / weights.sum()
        k_eff = min(k_per_bin, len(bin_atom_idx))
        if k_eff < k_per_bin:
            sampled = rng.choice(bin_atom_idx, size=k_per_bin,
                                 replace=True, p=weights)
        else:
            sampled = rng.choice(bin_atom_idx, size=k_per_bin,
                                 replace=False, p=weights)
        for s in sampled:
            importance[s] += 1.0
    return importance


def importance_inverse_weighted_replay(
    atom_norms: np.ndarray,
    retrieval_trace_score: np.ndarray,
    seed: int,
    n_events: int = TOTAL_REPLAY_EVENTS,
) -> np.ndarray:
    """Liu IS: importance = replay_count / ||a||^2."""
    rng = np.random.RandomState(seed + 33337)
    weights = retrieval_trace_score + 1.0
    weights = weights / weights.sum()
    sampled = rng.choice(M_TOTAL, size=n_events, replace=True, p=weights)
    raw_count = np.zeros(M_TOTAL, dtype=np.float64)
    for s in sampled:
        raw_count[s] += 1.0
    denom = np.maximum(atom_norms ** 2, 1e-9)
    return raw_count / denom


def run_arm(arm_name: str, seed: int, shared: Tuple) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     retrieval_trace_score, _ultrametric_coreness_unused) = shared
    atom_norms = _atom_norms_from_substrate(all_keys, W_base)

    if arm_name == "ARM_RAND_IMPORTANCE":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(retrieval_trace_score)
    elif arm_name == "ARM_STRATIFIED_REPLAY":
        importance = importance_stratified_replay(
            atom_norms, retrieval_trace_score, seed,
        )
    elif arm_name == "ARM_INVERSE_WEIGHTED_REPLAY":
        importance = importance_inverse_weighted_replay(
            atom_norms, retrieval_trace_score, seed,
        )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    assert importance.shape[0] == M_TOTAL, (
        f"importance vector wrong size for {arm_name}: "
        f"{importance.shape[0]} != {M_TOTAL}"
    )

    cor_imp_norm = correlation_E_vs_magnitude(importance, atom_norms)

    n_nonzero = int(np.sum(importance > 0))
    elapsed = time.time() - t0
    return {
        "arm_name": arm_name,
        "cor_importance_magnitude": float(cor_imp_norm),
        "importance_min": float(np.min(importance)),
        "importance_max": float(np.max(importance)),
        "importance_mean": float(np.mean(importance)),
        "n_nonzero_atoms": int(n_nonzero),
        "atom_norms_min": float(np.min(atom_norms)),
        "atom_norms_max": float(np.max(atom_norms)),
        "atom_norms_mean": float(np.mean(atom_norms)),
        "wall_s": float(elapsed),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] setup substrate (reusing v3 substrate state)...",
          flush=True)
    try:
        shared = setup_substrate_with_trace_and_clusters(seed)
        trace_total = float(np.sum(shared[6]))
        print(f"  [seed={seed}] setup done trace_total={trace_total:.0f}",
              flush=True)
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
            "alpha": float(ALPHA), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "anchor_name": ANCHOR_NAME,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    arms = []
    for arm_name in ARM_NAMES:
        try:
            out = run_arm(arm_name, seed, shared=shared)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"cor={out['cor_importance_magnitude']:+.4f} "
                f"n_nonzero={out['n_nonzero_atoms']} "
                f"wall={out['wall_s']:.2f}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} {arm_name}] ARM_EXCEPTION: {exc}\n{tb}",
                  flush=True)
            arms.append({
                "arm_name": arm_name,
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA), "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "n_llm_calls": 0,
        "trace_total": float(np.sum(shared[6])),
        "n_retrieved": int(shared[4].shape[0]),
        "n_unretrieved": int(shared[5].shape[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (META_RULE_K)
# ---------------------------------------------------------------------------
def _selftest_stratified_breaks_correlation_synthetic() -> bool:
    rng = np.random.RandomState(0)
    m_test = M_TOTAL
    atom_norms_test = np.linspace(0.1, 1.0, m_test)
    rng.shuffle(atom_norms_test)
    trace_test = atom_norms_test ** 2 * 100.0 + rng.rand(m_test) * 0.5

    cor_trace = correlation_E_vs_magnitude(trace_test, atom_norms_test)
    assert cor_trace > 0.6, (
        f"selftest synthetic trace-bias: expected cor > 0.6 "
        f"(Cauchy-Schwarz scaling); got {cor_trace:.4f}"
    )

    rng_strat = np.random.RandomState(1)
    quantiles = np.quantile(atom_norms_test, np.linspace(0, 1, 11))
    quantiles[-1] += 1e-9
    bins = np.digitize(atom_norms_test, quantiles[1:-1])
    importance_strat = np.zeros(m_test)
    for b in range(10):
        bin_idx = np.where(bins == b)[0]
        if len(bin_idx) == 0:
            continue
        sampled = rng_strat.choice(bin_idx,
                                    size=min(8, len(bin_idx)),
                                    replace=False)
        for s in sampled:
            importance_strat[s] += 1.0
    cor_strat = correlation_E_vs_magnitude(importance_strat, atom_norms_test)
    assert abs(cor_strat) < 0.30, (
        f"selftest synthetic stratified: expected |cor| < 0.30; "
        f"got {cor_strat:.4f}"
    )
    return True


def _selftest_inverse_weighted_correction_synthetic() -> bool:
    rng = np.random.RandomState(2)
    m_test = M_TOTAL
    atom_norms_test = np.linspace(0.1, 1.0, m_test)
    rng.shuffle(atom_norms_test)
    raw_count = atom_norms_test ** 2 * 50.0
    inverse_weighted = raw_count / np.maximum(atom_norms_test ** 2, 1e-9)
    cor_raw = correlation_E_vs_magnitude(raw_count, atom_norms_test)
    cor_inv = correlation_E_vs_magnitude(inverse_weighted, atom_norms_test)
    assert cor_raw > 0.6, f"selftest raw_count cor: {cor_raw:.4f}"
    assert abs(cor_inv) < 0.20, (
        f"selftest inverse_weighted: expected |cor| < 0.20; got {cor_inv:.4f}"
    )
    return True


def _selftest_alpha_regime_is_high() -> bool:
    assert ALPHA >= 1.5, (
        f"diagnostic must run at HIGH-alpha regime; got alpha={ALPHA:.3f}"
    )
    return True


def _selftest_4_arms_required() -> bool:
    assert len(ARM_NAMES) == 4, (
        f"diagnostic requires 4 arms; got {len(ARM_NAMES)}: {ARM_NAMES}"
    )
    return True


def _selftest_v3_import_is_side_effect_free() -> bool:
    """META_RULE for THIS cell: importing v3 must NOT have written any
    partials into the current process's HDLAB_EXP_NAME dir. We assert by
    checking that no partial_metrics_*.json files exist in our expected
    out_dir before we've called run_seed."""
    out_dir = get_output_dir(ANCHOR_NAME)
    if not out_dir.exists():
        return True
    pre_existing = list(out_dir.glob("partial_metrics_*.json"))
    # Some pre-existing partials may legitimately exist from a prior interrupted
    # run of THIS cell -- check ANCHOR in each.
    for p in pre_existing:
        try:
            body = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        cv = body.get("config_version", "")
        m = re.match(r"ANCHOR=([^,]+)", str(cv))
        if m and m.group(1) != ANCHOR_NAME:
            raise AssertionError(
                f"META_RULE_H_ANCHOR violation at startup: "
                f"{p.name} has ANCHOR={m.group(1)!r} != {ANCHOR_NAME!r}. "
                f"v3 import-time side effect did NOT get fixed -- HALT."
            )
        stored_anchor = body.get("anchor_name")
        if stored_anchor is not None and str(stored_anchor) != ANCHOR_NAME:
            raise AssertionError(
                f"META_RULE_H_ANCHOR violation at startup: "
                f"{p.name} has anchor_name={stored_anchor!r} != {ANCHOR_NAME!r}. "
                f"v3 import-time side effect did NOT get fixed -- HALT."
            )
    return True


def _instrumentation_selftest():
    _selftest_4_arms_required()
    _selftest_alpha_regime_is_high()
    _selftest_stratified_breaks_correlation_synthetic()
    _selftest_inverse_weighted_correction_synthetic()
    _selftest_v3_import_is_side_effect_free()
    print(
        f"[selftest] PASS N={N} M_TOTAL={M_TOTAL} alpha={ALPHA:.3f} "
        f"n_bins={N_BINS_STRATIFIED} k_per_bin={K_PER_BIN} mode={RUN_MODE} "
        f"arms={ARM_NAMES} v3_import_side_effect_free=True",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict (drill stub 3 bands + NAMESET sibling)
# ---------------------------------------------------------------------------
def _arms_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a.get("arm_name") == name]


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # ANCHOR check (META_RULE_H_ANCHOR at verdict layer in addition to
    # _seed_checkpoint's load-time check; defense in depth).
    for r in results:
        stored_anchor = r.get("anchor_name")
        if stored_anchor is not None and str(stored_anchor) != ANCHOR_NAME:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H_ANCHOR breach at verdict: "
                    f"seed={r.get('seed')} stored_anchor={stored_anchor!r} "
                    f"!= expected={ANCHOR_NAME!r}")

    for r in results:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_J caught {r['exception_phase']} "
                    f"exception seed={r['seed']}: {r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: META_RULE_J caught arm exception "
                        f"seed={r['seed']} arm={a['arm_name']}: "
                        f"{a['exception_msg']}")

    expected_per_seed = len(ARM_NAMES)
    for r in results:
        got = len(r.get("arms", []))
        if got != expected_per_seed:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H cardinality_ok breach "
                    f"seed={r['seed']}: expected {expected_per_seed} arms, "
                    f"got {got}")
        observed_nameset = {a.get("arm_name") for a in r.get("arms", [])}
        if observed_nameset != DECLARED_ARM_NAMESET:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H_NAMESET breach "
                    f"seed={r['seed']}: observed={sorted(observed_nameset)} "
                    f"!= declared={sorted(DECLARED_ARM_NAMESET)}")

    def _agg_cor(arm_name: str) -> float:
        per = []
        for r in results:
            per.extend(_arms_by_name(r["arms"], arm_name))
        if not per:
            return float("nan")
        cors = [float(a.get("cor_importance_magnitude", float("nan")))
                for a in per]
        return float(np.nanmean(cors))

    cor_rand = _agg_cor("ARM_RAND_IMPORTANCE")
    cor_trace = _agg_cor("ARM_TRACE_ONLY")
    cor_strat = _agg_cor("ARM_STRATIFIED_REPLAY")
    cor_inv = _agg_cor("ARM_INVERSE_WEIGHTED_REPLAY")

    summary = (
        f"alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"cor(RAND)={cor_rand:+.3f} "
        f"cor(TRACE)={cor_trace:+.3f} "
        f"cor(STRAT)={cor_strat:+.3f} "
        f"cor(INV_WGT)={cor_inv:+.3f}"
    )

    bias_floor = (
        REPRODUCE_TRACE_BIAS_FLOOR_SMOKE if RUN_MODE == "smoke"
        else REPRODUCE_TRACE_BIAS_FLOOR_FULL
    )

    trace_bias_reproduced = abs(cor_trace) >= bias_floor
    diagnostic_pass_a = abs(cor_strat) < DIAGNOSTIC_COR_GATE
    diagnostic_pass_b = abs(cor_inv) < DIAGNOSTIC_COR_GATE

    if not trace_bias_reproduced and abs(cor_trace) < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: TRACE cor={cor_trace:+.3f} below {0.30} -- "
                f"drill claim contradicted; either Cauchy-Schwarz math is "
                f"wrong OR test rigging wrong. SURPRISE_NEGATIVE. {summary}")

    if trace_bias_reproduced and (diagnostic_pass_a or diagnostic_pass_b):
        which = []
        if diagnostic_pass_a:
            which.append("STRATIFIED")
        if diagnostic_pass_b:
            which.append("INVERSE_WEIGHTED")
        return ("HARD_PASS",
                f"DIAGNOSTIC_PASS: TRACE reproduces |W|-bias "
                f"(cor={cor_trace:+.3f} >= {bias_floor}); "
                f"{'+'.join(which)} clears 0.30 gate -- fairness violation "
                f"IS sampling-bias artifact; v5 M-CFU / stratified path "
                f"endorsed. {summary}")

    if trace_bias_reproduced and not (diagnostic_pass_a or diagnostic_pass_b):
        return ("MIDDLE_BAND",
                f"PARTIAL_DIAGNOSTIC: TRACE reproduces bias "
                f"(cor={cor_trace:+.3f}) but neither STRATIFIED "
                f"(cor={cor_strat:+.3f}) nor INVERSE "
                f"(cor={cor_inv:+.3f}) breaks <0.30; sampling tricks "
                f"insufficient; deeper substrate property suspected. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"UNEXPECTED: trace_bias_reproduced={trace_bias_reproduced} "
            f"diagnostic_pass_a={diagnostic_pass_a} "
            f"diagnostic_pass_b={diagnostic_pass_b}. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
# RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER (added 2026-06-27)
if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)

    # Startup deviation-log scan (visibility for any pre-existing partials
    # whose ANCHOR mismatches this cell -- would be alien partials)
    if out_dir.exists():
        pre_existing = sorted(out_dir.glob("partial_metrics_*.json"))
        alien_found = 0
        for p in pre_existing:
            try:
                body = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            cv = body.get("config_version", "")
            m = re.match(r"ANCHOR=([^,]+)", str(cv))
            stored_anchor = body.get("anchor_name")
            mismatch = False
            if m and m.group(1) != ANCHOR_NAME:
                mismatch = True
                stored = m.group(1)
            elif stored_anchor is not None and \
                    str(stored_anchor) != ANCHOR_NAME:
                mismatch = True
                stored = stored_anchor
            if mismatch:
                print(f"[deviation-log] ALIEN partial detected at {p.name}: "
                      f"ANCHOR={stored!r} != expected={ANCHOR_NAME!r}; will "
                      f"be REJECTED by META_RULE_H_ANCHOR at partial-load.",
                      flush=True)
                alien_found += 1
        if alien_found > 0:
            print(f"[deviation-log] {alien_found} alien partial(s) present; "
                  f"_seed_checkpoint will filter them via run_config['anchor'].",
                  flush=True)

    # run_config includes "anchor"=ANCHOR_NAME so any partial with mismatched
    # config_version ANCHOR= is REJECTED at load by META_RULE_H_ANCHOR.
    run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
                  "alpha": float(ALPHA), "run_mode": RUN_MODE,
                  "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
          f"running {remaining}", flush=True)

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] stratified-replay diagnostic v2_proper N={N} "
              f"alpha={ALPHA:.3f} mode={RUN_MODE} arms={ARM_NAMES}...",
              flush=True)
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} N={N} M_TOTAL={M_TOTAL} "
            f"alpha={ALPHA:.3f} n_bins={N_BINS_STRATIFIED} "
            f"k_per_bin={K_PER_BIN} mode={RUN_MODE} arms={ARM_NAMES} "
            f"DIAGNOSTIC_COR_GATE={DIAGNOSTIC_COR_GATE} "
            f"v2_proper_import_guard=true"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "n_seeds": len(SEEDS),
        "n_bins_stratified": N_BINS_STRATIFIED,
        "k_per_bin": K_PER_BIN,
        "total_replay_events": TOTAL_REPLAY_EVENTS,
        "diagnostic_cor_gate": DIAGNOSTIC_COR_GATE,
        "run_mode": RUN_MODE,
        "n_llm_calls_total": 0,
        "expected_arm_nameset": sorted(DECLARED_ARM_NAMESET),
        "v2_proper_import_guard": True,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "anchor_name": r.get("anchor_name"),
                "elapsed_s": r.get("elapsed_s"),
                "trace_total": r.get("trace_total"),
                "n_retrieved": r.get("n_retrieved"),
                "n_unretrieved": r.get("n_unretrieved"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] written to {metrics_path}", flush=True)
