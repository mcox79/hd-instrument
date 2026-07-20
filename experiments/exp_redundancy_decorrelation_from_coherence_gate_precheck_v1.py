"""FORK-(C) STEP-0: is the REDUNDANCY signal (same-corpus cross-sentence corroboration count of a (verb,
patient) pair) a SAFE SECOND VIEW -- i.e. genuinely error-DECORRELATED from the coherence-gate's own error
mode -- so that ANY cross-document consolidation (the compounding payoff) is safe to build at all?

This is the still-open PREDICTION B / Step-0 gate from notes/research_fork_c_compounding_end_to_end_substrate_
loop_2026-07-19.md (Angle 5). It gates whether the cross-doc consolidation build is worth ANY representation
work -- BEFORE that work. Analysis on EXISTING eval data (reuses the atom-29346 pre-check's build_eval +
signals), NOT a new experiment.

WHAT THE PRE-CHECK (atom 29346) ALREADY ESTABLISHED (data/exp_coherence_filter_foundation_growth_safety_
precheck_v1/metrics.json):
  - coherence-gate sigB point-biserial corr with gold correctness = 0.139 (borderline; usable bar was 0.15;
    "safe-but-sub-usable").
  - sigC_redundancy point-biserial corr with correctness = 0.244 (clears the 0.15 usability bar ON ITS OWN).
  - the pre-check's error_decorrelation() measured sigB vs the LEXICAL (WordNet) view = -0.28 on the incorrect
    subset. It DID NOT measure sigB vs REDUNDANCY, and did NOT compute a redundancy double-filter.
  THE OPEN CHECK (this cell): redundancy's DECORRELATION FROM the coherence gate + the redundancy DOUBLE-FILTER.

CO-TRAINING REQUIREMENT (Blum-Mitchell): a second view helps only to the degree its errors are (conditionally)
  INDEPENDENT of the first view given the label. On the INCORRECT-extraction subset (label = wrong), two
  independent views have signal correlation ~ 0; a POSITIVELY-correlated second view is the SAME feature
  family (redundant, entrenches the same mistakes); a near-zero / negative correlation is a genuinely
  DECORRELATED view (co-training helps). The coherence gate's error pattern correlated WITH ITSELF is 1.0
  (trivially) -- that is the "no new information" reference a useful second view must beat.

SIGNALS (per raw reader extraction over the real McGuffey L04-L12 early-reading corpus, reused verbatim from
the pre-check; all seed-invariant except the extractor's own objecthood which is not used here):
  sigB   = coherence-gate schema-fit (situation-model selectional coherence; the existing gate's Score-1).
  redun  = # DISTINCT sentences the (v_lemma, patient) pair is extracted from across the corpus (Signal C.2).
           A STRUCTURAL corroboration count -- built from cross-sentence repetition, NOT from the parser's
           per-extraction construction cues that produce the errors. This is the candidate second view.
  correct= gold patient-lens match (the exact eval the 0.557 reader-precision number is measured on).

FILTERS (pre-registered operating points; identical extractions + gold):
  GATE   : keep extraction iff coherence-gate ACCEPTS it (sigB is None [unscorable -> accept, the gate's
           w_min behaviour] OR sigB >= 0.15). Reproduces the pre-check's FILTERED_RAW kept set (P=0.20).
  REDUN  : keep iff redun >= 2 (the pair is corroborated by >=2 separate sentences).
  DOUBLE : keep iff GATE-accept AND REDUN-keep (the co-training intersection = "coherence AND corroboration").

MEASURED (decisive):
  (M1) DECORRELATION on the INCORRECT subset: Pearson(sigB, redun) over extractions where correct==0 and the
       gate has an opinion (sigB not None), with a deterministic bootstrap 95% CI. Plus the binary
       error-indicator phi = Pearson(gate_keep, redun_keep) over the incorrect subset. Reference: gate-with-
       itself = 1.0. (Also reported over ALL both-opinion extractions for context.)
  (M2) SINGLE-filter correctness rates: precision of the GATE-kept set and the REDUN-kept set (Wilson 95% CI).
  (M3) DOUBLE-filter correctness rate: precision of the intersection set (Wilson 95% CI), and its lift over
       the BETTER single filter.
  (M4) complementarity: of the incorrect extractions, what fraction the gate catches (drops), the redun view
       catches, and what fraction BOTH miss (the shared blind spot -- the fraction co-training cannot help).

VERDICT BANDS (PRE-REGISTERED; the decorrelation number is reported PLAINLY, the bar is NOT redefined after
the fact -- this session has had 2 positive over-reads via criterion-swaps; guard against a 3rd):
  DECORRELATED   := Pearson(sigB, redun | incorrect) point estimate < +0.15 AND its 95%-CI UPPER bound < +0.30
                    (errors are at most weakly positively correlated -> a genuinely distinct view, not the
                    same feature family; negative is even better).
  SAME_FAMILY    := Pearson(sigB, redun | incorrect) point estimate >= +0.30 (moderate-or-higher positive
                    error correlation -> redundant view, entrenches the gate's own mistakes).
  DOUBLE_LIFT    := DOUBLE correctness - max(GATE correctness, REDUN correctness) >= +0.05 AND the DOUBLE kept
                    set is non-degenerate (n_kept >= 15, so the rate is not a small-sample artifact).
  DOUBLE_NOLIFT  := DOUBLE correctness <= max(GATE, REDUN) correctness OR the DOUBLE set is degenerate.

  HARD_PASS_SAFE_SECOND_VIEW_EXISTS  : DECORRELATED AND DOUBLE_LIFT.
    => a genuinely decorrelated second view exists AND stacking it raises correctness -> cross-document
       consolidation is SAFE TO BUILD as-is (green-light the representation work).
  HARD_FAIL_NO_SAFE_SECOND_VIEW      : SAME_FAMILY OR DOUBLE_NOLIFT.
    => redundancy is not a safe independent view on this substrate -> cross-doc consolidation is NOT safe to
       build as-is (a decisive, valuable NEGATIVE: redirect to finding a genuinely independent view, do NOT
       build the compounding harness on this filter).
  MIDDLE_BAND                        : partial (e.g. decorrelated but 0.03 <= double-lift < 0.05, or the CI
       straddles the decorrelation bar).

BRAIN-CHECK (pre-registered, outcome NOT pre-assumed): the brain corroborates across encounters (a repeated,
  cross-context fact is trusted more -- Bahrick reminiscence / multiple-trace consolidation), and it does NOT
  freely compound from a single noisy encounter (Kendeou & van den Broek). A corroboration-count view is thus
  brain-plausible AS a second, structurally-different signal. WHERE a same-limit could hit: if the reader
  systematically REPEATS the same wrong extraction across sentences (a stable construction error), redundancy
  would corroborate the wrong thing -- its errors would then correlate with the gate's (both fooled by the
  same repeated construction). That is exactly what M1 tests. decorrelated+lift => safe; correlated => the
  honest redirect is a view NOT built from the reader's own repeated output.

COMPUTE: foreground local-to-completion; reuses the pre-check's build_eval (LCCP train x3 seeds + GloVe +
  WordNet over 114 sentences; wall < ~1 min). Storage: LOCAL-ONLY (needs_orchestrator_store_sync). NO queue,
  NO push, NO remote-persist, NO git-add-A. Determinism: OMP/MKL/OPENBLAS=1 (inherited), fixed bootstrap seed,
  seed-invariance of the B/redun signals asserted across seeds 7/13/19.

CELL-TEMPLATE: except SystemExit raises before except Exception; atomic metrics (os.replace); formula
  self-tests hand-verified (pearson, Wilson interval, double-filter correctness on a 4-record hand case);
  determinism guard; arms-differ (GATE vs REDUN vs DOUBLE kept sets differ); numbers MEASURED@ at run /
  CITED@ (0.20 FILTERED_RAW cross-check; 0.244 redundancy corr; 0.139 gate corr from atom 29346).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_coherence_filter_foundation_growth_safety_precheck_v1 as PRE  # noqa: E402
from experiments.exp_coherence_filter_foundation_growth_safety_precheck_v1 import (  # noqa: E402
    build_eval, pearson, cfg_smoke, cfg_full, GATE_THR_KEEP,
)

ANCHOR_NAME = "redundancy_decorrelation_from_coherence_gate_precheck_v1"
SEEDS = [7, 13, 19]
REDUN_THR = 2                          # pre-registered: corroborated by >=2 separate sentences
BOOT_SEED = 20260719                   # deterministic bootstrap
N_BOOT = 3000
CITED_FILTERED_RAW_PRECISION = 0.20    # CITED@ atom 29346 FILTERED_RAW (gate-accept) precision -- cross-check
CITED_REDUN_CORR = 0.244               # CITED@ atom 29346 sigC_redundancy point-biserial vs correctness
CITED_GATE_CORR = 0.139                # CITED@ atom 29346 sigB coherence-gate point-biserial vs correctness


# ---------------------------------------------------------------------------------------------------
# filter decisions on a record
# ---------------------------------------------------------------------------------------------------
def gate_keep(r):
    """Coherence-gate ACCEPT (matches the pre-check gate_decision accept branch): unscorable -> accept."""
    s = r["sigB"]
    return (s is None) or (s >= GATE_THR_KEEP)


def redun_keep(r):
    return r["redun"] >= REDUN_THR


def precision_of(records, keep_fn):
    kept = [r for r in records if keep_fn(r)]
    k = sum(r["correct"] for r in kept)
    n = len(kept)
    return {"precision": round(k / n, 4) if n else None, "n_kept": n, "n_correct": k}


def wilson(k, n, z=1.96):
    """Wilson score interval for a binomial proportion (deterministic, no RNG)."""
    if n == 0:
        return None, None, None
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(p, 4), round(center - half, 4), round(center + half, 4)


def bootstrap_pearson_ci(x, y, n_boot=N_BOOT, seed=BOOT_SEED):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    n = len(x)
    if n < 3:
        return None, None, None
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        r = pearson(x[idx], y[idx])
        if r is not None:
            stats.append(r)
    if len(stats) < 10:
        return pearson(x, y), None, None
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return pearson(x, y), round(float(lo), 4), round(float(hi), 4)


# ---------------------------------------------------------------------------------------------------
# M1 -- redundancy vs coherence-gate error decorrelation on the incorrect subset
# ---------------------------------------------------------------------------------------------------
def decorrelation(records):
    """Pearson(sigB, redun) on incorrect subset (gate has opinion) + binary error-indicator phi + complement."""
    both = [(r["sigB"], float(r["redun"]), r["correct"]) for r in records if r["sigB"] is not None]
    wrong = [(b[0], b[1]) for b in both if b[2] == 0]
    # continuous signal correlation
    all_r = pearson([b[0] for b in both], [b[1] for b in both]) if len(both) >= 3 else None
    wrong_r, wlo, whi = bootstrap_pearson_ci([w[0] for w in wrong], [w[1] for w in wrong])
    # binary error-indicator phi over incorrect subset: does keeping/dropping co-move?
    gk = [1.0 if s >= GATE_THR_KEEP else 0.0 for s, _ in wrong]
    rk = [1.0 if u >= REDUN_THR else 0.0 for _, u in wrong]
    phi = pearson(gk, rk) if len(wrong) >= 3 else None
    # complementarity: of incorrect extractions, who CATCHES (drops) them
    n_wrong = len(wrong)
    gate_catch = sum(1 for s, _ in wrong if s < GATE_THR_KEEP)     # gate would DROP the wrong one
    redun_catch = sum(1 for _, u in wrong if u < REDUN_THR)         # redun would DROP the wrong one
    both_miss = sum(1 for s, u in wrong if s >= GATE_THR_KEEP and u >= REDUN_THR)  # both KEEP the wrong one
    return {
        "n_both_opinion": len(both), "n_incorrect": n_wrong,
        "pearson_sigB_redun_all": round(all_r, 4) if all_r is not None else None,
        "pearson_sigB_redun_on_incorrect": round(wrong_r, 4) if wrong_r is not None else None,
        "pearson_on_incorrect_ci95": [wlo, whi],
        "phi_gatekeep_redunkeep_on_incorrect": round(phi, 4) if phi is not None else None,
        "gate_with_itself_reference": 1.0,
        "gate_catches_wrong_frac": round(gate_catch / n_wrong, 4) if n_wrong else None,
        "redun_catches_wrong_frac": round(redun_catch / n_wrong, 4) if n_wrong else None,
        "both_miss_wrong_frac": round(both_miss / n_wrong, 4) if n_wrong else None,
    }


def kept_hash(records, keep_fn):
    items = sorted(f"{r['sid']}|{r['v']}|{r['p']}" for r in records if keep_fn(r))
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------------------------------
def build_verdict(decorr, gate_p, redun_p, double_p, n_double):
    wr = decorr["pearson_sigB_redun_on_incorrect"]
    whi = decorr["pearson_on_incorrect_ci95"][1]
    decorrelated = (wr is not None and wr < 0.15 and whi is not None and whi < 0.30)
    same_family = (wr is not None and wr >= 0.30)

    singles = [p for p in (gate_p, redun_p) if p is not None]
    best_single = max(singles) if singles else None
    double_lift = (double_p is not None and best_single is not None
                   and (double_p - best_single) >= 0.05 and n_double >= 15)
    double_nolift = (double_p is None or best_single is None
                     or double_p <= best_single or n_double < 15)

    if same_family or double_nolift:
        verdict = "HARD_FAIL_NO_SAFE_SECOND_VIEW"
    elif decorrelated and double_lift:
        verdict = "HARD_PASS_SAFE_SECOND_VIEW_EXISTS"
    else:
        verdict = "MIDDLE_BAND"
    return {
        "verdict": verdict,
        "decorrelated": bool(decorrelated), "same_family": bool(same_family),
        "double_lift": bool(double_lift), "double_nolift": bool(double_nolift),
        "pearson_on_incorrect": wr, "pearson_ci_upper": whi,
        "gate_precision": gate_p, "redun_precision": redun_p, "double_precision": double_p,
        "best_single_precision": best_single,
        "double_minus_best_single": round(double_p - best_single, 4)
        if (double_p is not None and best_single is not None) else None,
        "n_double_kept": n_double,
    }


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))

    per_seed = []
    for seed in SEEDS:
        ev = build_eval(cfg, seed)
        recs = ev["records"]
        decorr = decorrelation(recs)
        gate = precision_of(recs, gate_keep)
        redun = precision_of(recs, redun_keep)
        double = precision_of(recs, lambda r: gate_keep(r) and redun_keep(r))
        base = precision_of(recs, lambda r: True)
        hashes = {"GATE": kept_hash(recs, gate_keep), "REDUN": kept_hash(recs, redun_keep),
                  "DOUBLE": kept_hash(recs, lambda r: gate_keep(r) and redun_keep(r)),
                  "ALL": kept_hash(recs, lambda r: True)}
        per_seed.append({"seed": seed, "n_records": len(recs), "decorr": decorr, "base": base,
                         "GATE": gate, "REDUN": redun, "DOUBLE": double, "hashes": hashes})

    # the decorrelation + filter kept-sets are structural (sigB/redun/correct all seed-invariant); verify.
    d0 = per_seed[0]
    seed_invariant = all(
        (ps["decorr"]["pearson_sigB_redun_on_incorrect"] == d0["decorr"]["pearson_sigB_redun_on_incorrect"]
         and ps["GATE"]["precision"] == d0["GATE"]["precision"]
         and ps["DOUBLE"]["precision"] == d0["DOUBLE"]["precision"]) for ps in per_seed)

    decorr = d0["decorr"]
    gate_p = d0["GATE"]["precision"]; redun_p = d0["REDUN"]["precision"]; double_p = d0["DOUBLE"]["precision"]
    gate_ci = wilson(d0["GATE"]["n_correct"], d0["GATE"]["n_kept"])
    redun_ci = wilson(d0["REDUN"]["n_correct"], d0["REDUN"]["n_kept"])
    double_ci = wilson(d0["DOUBLE"]["n_correct"], d0["DOUBLE"]["n_kept"])
    base_ci = wilson(d0["base"]["n_correct"], d0["base"]["n_kept"])

    vd = build_verdict(decorr, gate_p, redun_p, double_p, d0["DOUBLE"]["n_kept"])

    # arms-differ: the two VIEWS must genuinely differ (GATE != REDUN) AND the double filter must actually
    # drop things (DOUBLE != ALL-kept). NOTE: DOUBLE == REDUN is NOT a bug -- it means REDUN's kept set is a
    # subset of GATE's (redundancy is the binding constraint); that subset structure is recorded, not asserted.
    hh = d0["hashes"]
    arms_differ = (hh["GATE"] != hh["REDUN"] and hh["DOUBLE"] != hh["ALL"])
    assert arms_differ, f"arms do not differ (GATE==REDUN or DOUBLE is a no-op): {hh}"
    double_equals_redun = (hh["DOUBLE"] == hh["REDUN"])   # REDUN subset of GATE
    double_equals_gate = (hh["DOUBLE"] == hh["GATE"])     # GATE subset of REDUN
    # cross-check GATE precision reproduces the pre-check FILTERED_RAW = 0.20
    gate_matches_precheck = (gate_p is not None and abs(gate_p - CITED_FILTERED_RAW_PRECISION) < 0.02)

    elapsed = time.perf_counter() - t0
    v = vd["verdict"]
    msg = (f"{v} | slice={'+'.join(cfg['slice_lessons'])} seeds={SEEDS} n_rec={d0['n_records']} "
           f"| M1 DECORR pearson(sigB,redun|incorrect)={decorr['pearson_sigB_redun_on_incorrect']} "
           f"ci95={decorr['pearson_on_incorrect_ci95']} phi_keep={decorr['phi_gatekeep_redunkeep_on_incorrect']} "
           f"(all={decorr['pearson_sigB_redun_all']}; gate-self-ref=1.0) "
           f"| decorrelated={vd['decorrelated']} same_family={vd['same_family']} "
           f"| M2/M3 correctness base={d0['base']['precision']} GATE={gate_p}(n={d0['GATE']['n_kept']}) "
           f"REDUN={redun_p}(n={d0['REDUN']['n_kept']}) DOUBLE={double_p}(n={d0['DOUBLE']['n_kept']}) "
           f"| double-best_single={vd['double_minus_best_single']} double_lift={vd['double_lift']} "
           f"| M4 gate_catch={decorr['gate_catches_wrong_frac']} redun_catch={decorr['redun_catches_wrong_frac']} "
           f"both_miss={decorr['both_miss_wrong_frac']} "
           f"| seed_inv={seed_invariant} arms_differ={arms_differ} gate~precheck0.20={gate_matches_precheck}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg, "seeds": SEEDS,
        "redun_threshold": REDUN_THR, "gate_thr_keep": GATE_THR_KEEP,
        "decorrelation_seed0": decorr, "verdict_detail": vd,
        "single_filters_seed0": {
            "base_rate": {"precision": d0["base"]["precision"], "n": d0["base"]["n_kept"], "wilson95": base_ci},
            "GATE": {**d0["GATE"], "wilson95": gate_ci},
            "REDUN": {**d0["REDUN"], "wilson95": redun_ci},
            "DOUBLE": {**d0["DOUBLE"], "wilson95": double_ci},
        },
        "seed_invariant": bool(seed_invariant), "arms_differ": bool(arms_differ),
        "double_equals_redun_subset_of_gate": bool(double_equals_redun),
        "double_equals_gate_subset_of_redun": bool(double_equals_gate),
        "gate_precision_matches_precheck_020": bool(gate_matches_precheck),
        "kept_hashes_seed0": d0["hashes"],
        "per_seed": [{"seed": ps["seed"], "GATE": ps["GATE"], "REDUN": ps["REDUN"], "DOUBLE": ps["DOUBLE"],
                      "decorr_on_incorrect": ps["decorr"]["pearson_sigB_redun_on_incorrect"]} for ps in per_seed],
        "final_metrics_atomicity": "tmp_replace",
        "needs_orchestrator_store_sync": True, "storage": "local_only",
        "cited_filtered_raw_precision": CITED_FILTERED_RAW_PRECISION,
        "cited_redun_corr_vs_correct": CITED_REDUN_CORR, "cited_gate_corr_vs_correct": CITED_GATE_CORR,
        "reuses_precheck": "experiments/exp_coherence_filter_foundation_growth_safety_precheck_v1.py (build_eval)",
        "independent_gold_source": "data/gold_mcguffey_lccp_argstruct_v1.json (single-annotator; pos + nopat).",
        "REQUIRED_FIELDS": ["verdict", "decorrelation_seed0", "verdict_detail", "single_filters_seed0"],
        "notes": ("FORK-(C) STEP-0 decisive gate: is REDUNDANCY a SAFE, error-DECORRELATED second view vs the "
                  "coherence gate (Blum-Mitchell co-training condition), and does the coherence-AND-redundancy "
                  "DOUBLE filter beat either single filter's correctness. HARD_PASS => cross-doc consolidation "
                  "safe to build; HARD_FAIL => no safe second view here (valuable negative, redirect). "
                  "Reuses the atom-29346 pre-check data (no new experiment). CLAIM-VET-pending; single-annotator "
                  "gold (caveated); McGuffey L04-L12 real early-reading text. Decorrelation number reported "
                  "PLAINLY, bar pre-registered (no criterion-swap).")
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  M1 decorrelation (incorrect subset, n={decorr['n_incorrect']}):", flush=True)
    print(f"     pearson(sigB,redun)={decorr['pearson_sigB_redun_on_incorrect']} "
          f"ci95={decorr['pearson_on_incorrect_ci95']}  phi(keep,keep)={decorr['phi_gatekeep_redunkeep_on_incorrect']}"
          f"  [gate-with-itself=1.0]", flush=True)
    print(f"  M2/M3 correctness (Wilson95): base={base_ci}  GATE={gate_ci}  REDUN={redun_ci}  DOUBLE={double_ci}",
          flush=True)
    print(f"  M4 complementarity: gate_catches_wrong={decorr['gate_catches_wrong_frac']} "
          f"redun_catches_wrong={decorr['redun_catches_wrong_frac']} both_miss={decorr['both_miss_wrong_frac']}",
          flush=True)
    return payload


def self_test():
    # pearson hand case (reused from pre-check; x=[1,2,3,4],y=[0,0,1,1] -> 2/sqrt5)
    assert abs(pearson([1, 2, 3, 4], [0, 0, 1, 1]) - 0.8944271909999159) < 1e-9, "pearson broken"
    # Wilson interval hand case: k=50,n=100 -> p=0.5, CI ~ [0.4038, 0.5962] (hand-verified)
    p, lo, hi = wilson(50, 100)
    assert abs(p - 0.5) < 1e-9 and abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3, f"wilson: {(p, lo, hi)}"
    # double-filter correctness on a 4-record hand case:
    #  r1 sigB=0.20(accept) redun=2(keep) correct=1 ; r2 sigB=0.10(defer,NOT accept) redun=3 correct=1
    #  r3 sigB=0.50(accept) redun=1 correct=0 ; r4 sigB=0.20(accept) redun=2(keep) correct=0
    #  GATE-accept={r1,r3,r4} -> 1/3=0.3333 ; REDUN={r1,r2,r4} -> 2/3=0.6667 ; DOUBLE={r1,r4} -> 1/2=0.5
    hand = [{"sid": "s", "v": "v", "p": "a", "sigB": 0.20, "redun": 2, "correct": 1},
            {"sid": "s", "v": "v", "p": "b", "sigB": 0.10, "redun": 3, "correct": 1},
            {"sid": "s", "v": "v", "p": "c", "sigB": 0.50, "redun": 1, "correct": 0},
            {"sid": "s", "v": "v", "p": "d", "sigB": 0.20, "redun": 2, "correct": 0}]
    g = precision_of(hand, gate_keep); rd = precision_of(hand, redun_keep)
    db = precision_of(hand, lambda r: gate_keep(r) and redun_keep(r))
    assert g["precision"] == 0.3333 and g["n_kept"] == 3, f"gate hand: {g}"
    assert rd["precision"] == 0.6667 and rd["n_kept"] == 3, f"redun hand: {rd}"
    assert db["precision"] == 0.5 and db["n_kept"] == 2, f"double hand: {db}"
    # sigB=None -> gate accepts (w_min behaviour)
    assert gate_keep({"sigB": None, "redun": 1}) is True, "None sigB must accept"
    # decorrelation direction sanity: perfectly co-moving wrong-subset signals -> phi=1
    dd = decorrelation([{"sid": "s", "v": "v", "p": "a", "sigB": 0.30, "redun": 3, "correct": 0},
                        {"sid": "s", "v": "v", "p": "b", "sigB": 0.05, "redun": 1, "correct": 0},
                        {"sid": "s", "v": "v", "p": "c", "sigB": 0.30, "redun": 3, "correct": 0}])
    assert dd["phi_gatekeep_redunkeep_on_incorrect"] == 1.0, f"phi co-move: {dd}"
    # determinism guard on the real signals (one seed, twice)
    ev1 = build_eval(cfg_smoke(), 7); ev2 = build_eval(cfg_smoke(), 7)
    d1 = decorrelation(ev1["records"]); d2 = decorrelation(ev2["records"])
    assert d1["pearson_sigB_redun_on_incorrect"] == d2["pearson_sigB_redun_on_incorrect"], "DETERMINISM BREACH"
    g1 = precision_of(ev1["records"], gate_keep)
    assert g1["n_kept"] <= len(ev1["records"]), "filter must not add"
    print(f"[{ANCHOR_NAME}] self-test OK: pearson/wilson/double-filter/None-accept/phi/determinism pass", flush=True)
    print(f"[{ANCHOR_NAME}] smoke(L04+L05,seed7): decorr(sigB,redun|incorrect)="
          f"{d1['pearson_sigB_redun_on_incorrect']} n_incorrect={d1['n_incorrect']} "
          f"GATE_P={g1['precision']}(n={g1['n_kept']})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
