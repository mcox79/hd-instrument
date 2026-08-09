"""exp_grounding_acquisition_loop_v1 -- the closed self-growing grounding loop (2026-08-09).

Pre-reg: preregs/2026-08-09_grounding_acquisition_loop_v1.md
Engine:  hdlab/grounding_acquisition_loop.py (Library / consolidation_pass / schema_consistency_
         split_half -- the NEW wiring) + hdlab/consequence_learning_loop.py (credit_window /
         teacher_verdict -- the REUSED FLAG half, unmodified).
Drill:   notes/research_psych_acquisition_consolidation_loop_2026-08-09.md

WHAT: Director task "Direction-B build #4" -- wires the already-built-but-never-joined FLAG
(propose/credit) half and a NEW trace-level LIBRARY + periodic CONSOLIDATE ("sleep") pass whose
BANK decision is gated on a SCHEMA-CONSISTENCY signal (split-half context-coherence over the item's
own accumulated evidence), not on vote-agreement alone. Reads the SAME 4 real, McGuffey-free novels
(little_women / anne_of_green_gables / tom_sawyer / wizard_of_oz) consequence_learning_loop's own
cells already validated as the corpus, sliced into 5 sequential exposure batches (read -> sleep,
repeated), and reports:
  1. GROWTH CURVE   -- cumulative GROUNDED_* count pass-over-pass (must be non-flat, non-regressing).
  2. FALSE-CONSOLIDATION GUARD -- an adversarial WRONG-CONTEXT probe (consistent votes, genuinely
     mismatched real-window contexts) must ESCALATE, never GROUND.
  3. ESCALATION SANITY -- pure-noise (Goldilocks "unparseable") synthetic tokens must ESCALATE.
  4. CORRECTNESS-WHEN-CHECKED -- banked POS/NEG groundings scored against the SAME 36-item OOV eval
     (goal_bearing_modern_eval_v1.jsonl) the whole arc uses, via the ALREADY-BUILT, REUSED
     _per_verb_grounded_correctness helper (byte-identical import, no reimplementation).

HONEST PRIOR CONTEXT (read before interpreting the verdict): the underlying vote/FLAG signal this
cell's guard sits on top of has HARD_FAILED on the SAME eval in every prior standalone attempt --
word_acquisition_loop increment1 (SHELVE), increment1b (0.4444 vs 0.6389 floor, HARD_FAIL),
consequence_learning_loop's own oov_outcome_verb_valence (0.1667, HARD_FAIL) and signal_a_primary
(0.1944 primary; per-verb polarity_match_rate=0.3333 at n=3, BELOW CHANCE). This cell's job is to
determine whether the NEW library/consolidation/schema-guard machinery (a) actually grows coverage
over passes and (b) actually rejects false consolidation -- LOOP-MECHANICS questions, cleanly
separable from whether the underlying vote signal is precise enough to trust, which gate 4 measures
honestly and separately (a HARD-FAIL on gate 4 alone is diagnosed as base-ingredient precision, NOT
loop-mechanics failure, per the flat-result-means-diagnose discipline).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic_seeding: fixed integer seeds only (np.random.default_rng(fixed)); no hash()-seeding
# - start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
# - discriminator-fires gate at smoke: >=1 pass with >=1 new trace AND calibration discriminates
# - real_code_path_exercised: Library / consolidation_pass / credit_window / _per_verb_grounded_
#   correctness all constructed/called for real at self-test scale (not synthetic-only)
# - all numbers MEASURED@ this cell's metrics.json (no HYPOTHESIZED numbers reported as data)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)

from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, Trace, context_vector, schema_consistency_split_half, consolidation_pass,
    self_test as _engine_self_test, D as CTX_D, MIN_CONFIRM, NEUTRAL_BAND, PATIENCE_MAX,
)
# REUSE the consequence_learning_loop cell family's validated corpus/eval/scoring helpers verbatim
# (wire-don't-island -- no reimplementation drift).
from exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, NOVELS, SMOKE_NOVELS,
)
from exp_consequence_learning_loop_signal_a_primary_v1 import (  # noqa: E402
    _per_verb_grounded_correctness,
)
from hdlab.consequence_learning_loop import credit_window  # noqa: E402

ANCHOR_NAME = "grounding_acquisition_loop_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

N_PASSES = 5                    # sequential exposure batches (Dumay & Gaskell / sleep-cadence design)
SIGNAL_MODE = "signal_a_only"   # and_gate co-fires on ~3 windows total (too sparse to test the loop
                                 # -- diagnosed by the parent oov_outcome_verb_valence cell); the
                                 # research question here is whether the schema guard rescues
                                 # precision over signal_a_only's own already-measured 0.3333 pol_match
CALIB_MIN_OCC = 4
CALIB_MAX_LEMMAS = 40
CALIB_MARGIN = 0.02
CALIB_FLOOR = 0.03

# Reference baselines (MEASURED elsewhere, re-derived at runtime never hard-coded as truth):
MAJORITY_FLOOR_REF = 0.6389            # 23/36, goal_bearing_modern_eval_v1.jsonl
SIGNAL_A_PRIMARY_POL_MATCH_REF = 0.3333  # data/exp_consequence_learning_loop_signal_a_primary_v1/metrics.json


# ------------------------------------------------------------------ start-marker / crash diagnostics
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


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------ batching
def _split_batches(windows, n):
    """Deterministic contiguous split into n roughly-equal slices, corpus order preserved."""
    total = len(windows)
    batches = []
    start = 0
    for i in range(n):
        remaining_slots = n - i
        end = start + (total - start) // remaining_slots
        batches.append(windows[start:end])
        start = end
    return batches


# ------------------------------------------------------------------ FLAG stage (batch-level)
def flag_batch(library: Library, goal_windows, batch_start_wid: int, pass_idx: int,
               signal_mode: str = SIGNAL_MODE) -> dict:
    """FLAG stage for one exposure batch: scan windows, call the REUSED credit_window, and for
    every credited OOV outcome-verb lemma append a trace (episode identity + context vector +
    pole) into the library. Words that settled (GROUNDED_*/ESCALATED) in an EARLIER pass are
    excluded from further trace accumulation by Library.flag's own terminal-status no-op AND
    (independently) by credit_window's in_lexicon filter once a word is registered into the
    overlay -- belt-and-suspenders, the two exclusions have different triggers (overlay write-back
    vs local terminal-status), both correct."""
    n_windows_with_teacher = 0
    n_windows_credited = 0
    n_traces_added = 0
    for i, (goal_sentence, window_text, desired_referent) in enumerate(goal_windows):
        wid = batch_start_wid + i
        rec = credit_window(goal_sentence, window_text, desired_referent, signal_mode=signal_mode)
        if rec is None:
            continue
        n_windows_with_teacher += 1
        pole = "POS" if rec["teacher_verdict"] == "MET" else "NEG"
        ctx = context_vector(window_text)
        credited_here = False
        for lemma in rec["credit_targets"]:
            added = library.flag(lemma, episode_id=f"w{wid}", pole=pole, context_vec=ctx,
                                 pass_idx=pass_idx)
            if added:
                n_traces_added += 1
                credited_here = True
        if credited_here:
            n_windows_credited += 1
    return {"n_windows_with_teacher": n_windows_with_teacher,
            "n_windows_credited": n_windows_credited, "n_traces_added": n_traces_added}


# ------------------------------------------------------------------ calibration (META_RULE_M adaptive)
def calibrate_schema_threshold(calib_lib: Library, seed: int = 0, min_occ: int = CALIB_MIN_OCC,
                                max_lemmas: int = CALIB_MAX_LEMMAS, margin: float = CALIB_MARGIN,
                                floor: float = CALIB_FLOOR) -> tuple:
    """Adaptive calibration (META_RULE_M): SCHEMA_THRESH derived from the REAL corpus's own
    matched-vs-wrong-context split-half cosine distribution, never hand-tuned to pass. matched = a
    real lemma's own two trace-halves; wrong = that lemma's first-half raw-sum against a DIFFERENT
    (fixed-seed-paired) lemma's second-half raw-sum. Threshold = the midpoint (floored). Logs the
    discriminator-still-fires check so a degenerate calibration is visible, not silently accepted."""
    eligible = sorted(lemma for lemma, it in calib_lib.items.items() if len(it.traces) >= min_occ)
    eligible = eligible[:max_lemmas]
    rng = np.random.default_rng(80000 + seed)
    matched_scores, wrong_scores = [], []
    for lemma in eligible:
        traces = calib_lib.items[lemma].traces
        half = len(traces) // 2
        a, b = traces[:half], traces[half:]
        va = np.sum([t.context_vec for t in a], axis=0)
        vb = np.sum([t.context_vec for t in b], axis=0)
        na, nb = float(np.linalg.norm(va)), float(np.linalg.norm(vb))
        if na > 1e-9 and nb > 1e-9:
            matched_scores.append(float(np.dot(va, vb) / (na * nb)))
        others = [l for l in eligible if l != lemma]
        if not others:
            continue
        other = others[int(rng.integers(len(others)))]
        ot = calib_lib.items[other].traces
        ohalf = len(ot) // 2
        vb2 = np.sum([t.context_vec for t in ot[ohalf:]], axis=0)
        nb2 = float(np.linalg.norm(vb2))
        if na > 1e-9 and nb2 > 1e-9:
            wrong_scores.append(float(np.dot(va, vb2) / (na * nb2)))
    matched_mean = float(np.mean(matched_scores)) if matched_scores else 0.0
    wrong_mean = float(np.mean(wrong_scores)) if wrong_scores else 0.0
    thresh = max(floor, (matched_mean + wrong_mean) / 2.0)
    discriminates = (matched_mean - wrong_mean) >= margin
    report = {"n_lemmas_calibrated": len(eligible), "matched_mean": round(matched_mean, 4),
              "wrong_mean": round(wrong_mean, 4), "schema_thresh": round(thresh, 4),
              "discriminates": discriminates, "margin_required": margin,
              "n_matched_pairs": len(matched_scores), "n_wrong_pairs": len(wrong_scores)}
    return thresh, report


# ------------------------------------------------------------------ adversarial probes (can-fail gates)
def run_adversarial_wrong_context_probe(windows, schema_thresh, min_confirm, patience_max,
                                        neutral_band, seed=0, n_items=3, n_passes_probe=8):
    """Inject n_items synthetic library entries with a CONSISTENT vote (all POS) but MISMATCHED
    context (each trace's context vector drawn from a genuinely different, unrelated REAL window's
    text, fixed-seed sampled without replacement) -- the false-consolidation can-fail test:
    coincidental vote-agreement across incoherent contexts must ESCALATE, never GROUND."""
    rng = np.random.default_rng(90000 + seed)
    n_needed = n_items * min_confirm
    idxs = rng.choice(len(windows), size=min(n_needed, len(windows)), replace=False)
    lib = Library()
    for i in range(n_items):
        lemma = f"zzadversarial{i}"
        for k in range(min_confirm):
            wi = idxs[i * min_confirm + k]
            _, window_text, _ = windows[int(wi)]
            ctx = context_vector(window_text)
            lib.flag(lemma, episode_id=f"adv{i}_{k}", pole="POS", context_vec=ctx, pass_idx=1)
    grounded_any = False
    for p in range(1, n_passes_probe + 1):
        rep = consolidation_pass(lib, p, min_confirm=min_confirm, schema_thresh=schema_thresh,
                                 neutral_band=neutral_band, patience_max=patience_max, register=False)
        if rep["cumulative_grounded"] > 0:
            grounded_any = True
    final_statuses = {lemma: it.status for lemma, it in lib.items.items()}
    n_escalated = sum(1 for s in final_statuses.values() if s == "ESCALATED")
    n_grounded = sum(1 for s in final_statuses.values() if s.startswith("GROUNDED"))
    return {"n_items": n_items, "final_statuses": final_statuses, "n_escalated": n_escalated,
            "n_grounded_wrongly": n_grounded, "grounded_any": grounded_any,
            "guard_rejected_all": (n_escalated == n_items and not grounded_any)}


def run_nonsense_escalation_probe(schema_thresh, min_confirm, patience_max, neutral_band, seed=0,
                                  n_items=3, n_passes_probe=8, d=CTX_D):
    """Inject n_items GARBLED synthetic entries: context vectors are PURE RANDOM bipolar noise (no
    real word/content at all -- the Goldilocks 'unparseable' category, distinct from the wrong-
    context probe's real-but-mismatched contexts) and independently coin-flipped votes. Must reach
    ESCALATED, never GROUNDED -- belt-and-suspenders sanity on the schema gate's floor behavior."""
    rng = np.random.default_rng(91000 + seed)
    lib = Library()
    for i in range(n_items):
        lemma = f"zznonsense{i}"
        for k in range(min_confirm):
            ctx = rng.choice([-1.0, 1.0], size=d)
            pole = "POS" if rng.random() < 0.5 else "NEG"
            lib.flag(lemma, episode_id=f"non{i}_{k}", pole=pole, context_vec=ctx, pass_idx=1)
    grounded_any = False
    for p in range(1, n_passes_probe + 1):
        rep = consolidation_pass(lib, p, min_confirm=min_confirm, schema_thresh=schema_thresh,
                                 neutral_band=neutral_band, patience_max=patience_max, register=False)
        if rep["cumulative_grounded"] > 0:
            grounded_any = True
    final_statuses = {lemma: it.status for lemma, it in lib.items.items()}
    n_escalated = sum(1 for s in final_statuses.values() if s == "ESCALATED")
    return {"n_items": n_items, "final_statuses": final_statuses, "n_escalated": n_escalated,
            "grounded_any": grounded_any, "all_escalated": (n_escalated == n_items and not grounded_any)}


# ------------------------------------------------------------------ main run
def run(output_dir, run_mode, novels, n_passes=N_PASSES, min_confirm=MIN_CONFIRM,
        patience_max=PATIENCE_MAX, neutral_band=NEUTRAL_BAND, signal_mode=SIGNAL_MODE, seed=0):
    t0 = time.perf_counter()
    expected_n_units = n_passes + 2  # n_passes consolidation passes + 2 adversarial probes
    _write_start_marker(output_dir, run_mode, expected_n_units)

    print(f"[grounding_acq] loading eval + corpus (novels={list(novels)})", flush=True)
    all_rows, oov_rows = _load_eval()
    blocks, corpus_stats, excl = _read_corpus_blocks(all_rows, novels)
    windows, win_stats = _build_windows(blocks, all_rows)
    print(f"[grounding_acq] n_windows={len(windows)} win_stats={win_stats}", flush=True)

    # ---- 1. calibration (throwaway library, register=False, zero overlay writes) ----
    _vls.clear_acquired_outcome()
    calib_lib = Library()
    calib_flag_report = flag_batch(calib_lib, windows, batch_start_wid=0, pass_idx=0,
                                   signal_mode=signal_mode)
    schema_thresh, calib_report = calibrate_schema_threshold(calib_lib, seed=seed)
    print(f"[grounding_acq] calibration: {calib_report}", flush=True)

    # ---- 2. main closed-loop run: N_PASSES x (read batch -> sleep/consolidate) ----
    batches = _split_batches(windows, n_passes)
    library = Library()
    _vls.clear_acquired_outcome()  # hygiene: strict-ADD from an empty overlay
    pass_reports = []
    growth_curve = []
    grounded_lemma_sets = []
    wid_cursor = 0
    for p in range(1, n_passes + 1):
        batch = batches[p - 1]
        flag_report = flag_batch(library, batch, batch_start_wid=wid_cursor, pass_idx=p,
                                 signal_mode=signal_mode)
        wid_cursor += len(batch)
        cons_report = consolidation_pass(library, p, min_confirm=min_confirm,
                                         schema_thresh=schema_thresh, neutral_band=neutral_band,
                                         patience_max=patience_max, register=True)
        report = {"pass": p, "batch_size": len(batch), **flag_report, **cons_report}
        pass_reports.append(report)
        growth_curve.append(cons_report["cumulative_grounded"])
        grounded_lemma_sets.append({l for l, it in library.items.items()
                                    if it.status.startswith("GROUNDED")})
        print(f"[grounding_acq] pass {p}/{n_passes}: traces_added={flag_report['n_traces_added']} "
              f"grounded={cons_report['cumulative_grounded']} "
              f"escalated={cons_report['cumulative_escalated']} "
              f"pending={cons_report['cumulative_pending']}", flush=True)

    # ---- 3. growth-curve properties ----
    monotonic_nondecreasing = all(growth_curve[i] <= growth_curve[i + 1]
                                  for i in range(len(growth_curve) - 1))
    no_regression = all(grounded_lemma_sets[i] <= grounded_lemma_sets[i + 1]
                        for i in range(len(grounded_lemma_sets) - 1))
    net_growth = growth_curve[-1] if growth_curve else 0

    # ---- 4. banked-groundings correctness (REUSED helper, real eval, real overlay) ----
    registered = {lemma: it.status.split("_", 1)[1] for lemma, it in library.items.items()
                  if it.status in ("GROUNDED_POS", "GROUNDED_NEG")}
    master_counter = {lemma: {"POS": sum(1 for t in it.traces if t.pole == "POS"),
                              "NEG": sum(1 for t in it.traces if t.pole == "NEG")}
                      for lemma, it in library.items.items()}
    correctness_table, polarity_match_rate, n_grounded_eval_verbs = _per_verb_grounded_correctness(
        oov_rows, registered, master_counter)
    print(f"[grounding_acq] correctness: registered={len(registered)} "
          f"n_grounded_eval_verbs={n_grounded_eval_verbs} pol_match={polarity_match_rate}", flush=True)
    _vls.clear_acquired_outcome()  # end-of-main-run hygiene before the isolated adversarial probes

    # ---- 5. FALSE-CONSOLIDATION GUARD: adversarial wrong-context probe ----
    adversarial_report = run_adversarial_wrong_context_probe(
        windows, schema_thresh, min_confirm, patience_max, neutral_band, seed=seed)
    print(f"[grounding_acq] adversarial wrong-context probe: {adversarial_report['final_statuses']}",
          flush=True)

    # ---- 6. ESCALATION SANITY: pure-noise nonsense-token probe ----
    nonsense_report = run_nonsense_escalation_probe(
        schema_thresh, min_confirm, patience_max, neutral_band, seed=seed)
    print(f"[grounding_acq] nonsense escalation probe: {nonsense_report['final_statuses']}", flush=True)
    _vls.clear_acquired_outcome()  # final hygiene

    # ---- 7. verdict logic (pre-registered bands, see prereg) ----
    gate_growth = (net_growth >= 3) and monotonic_nondecreasing and no_regression
    gate_guard = adversarial_report["guard_rejected_all"]
    gate_escalation = nonsense_report["all_escalated"]
    gate_correctness = (polarity_match_rate is not None and polarity_match_rate > 0.5)
    gate_calibration_discriminates = calib_report["discriminates"]

    hard_fail_reasons = []
    if not gate_calibration_discriminates:
        hard_fail_reasons.append(
            f"CALIBRATION_DEGENERATE: matched_mean={calib_report['matched_mean']} "
            f"wrong_mean={calib_report['wrong_mean']} margin<{CALIB_MARGIN} -- schema metric does not "
            f"discriminate on THIS corpus; growth/guard results below are UNINTERPRETABLE, not a "
            f"verdict (diagnose the metric, not the loop)")
    if net_growth < 3:
        hard_fail_reasons.append(f"NO_GROWTH: net_growth={net_growth} < 3 across {n_passes} passes")
    if not monotonic_nondecreasing:
        hard_fail_reasons.append("GROWTH_NONMONOTONIC: cumulative grounded count decreased pass-over-pass")
    if not no_regression:
        hard_fail_reasons.append("REGRESSION: a previously-grounded lemma's status regressed")
    if not gate_guard:
        hard_fail_reasons.append(
            f"GUARD_FAILED: adversarial wrong-context probe grounded "
            f"{adversarial_report['n_grounded_wrongly']}/{adversarial_report['n_items']} items")
    if not gate_escalation:
        hard_fail_reasons.append(
            f"ESCALATION_SANITY_FAILED: nonsense probe grounded_any={nonsense_report['grounded_any']}")
    if not gate_correctness:
        hard_fail_reasons.append(
            f"CORRECTNESS_GATE_FAILED: banked polarity_match_rate={polarity_match_rate} "
            f"(n={n_grounded_eval_verbs}) does not clear >0.5 -- LOOP MECHANICS (growth+guard) may "
            f"still be sound; this specifically diagnoses the underlying vote/FLAG signal's precision, "
            f"not the new library/consolidation/guard machinery (see module docstring HONEST PRIOR "
            f"CONTEXT: signal_a_only alone already measured 0.3333 at n=3 on this same eval)")

    if gate_calibration_discriminates and gate_growth and gate_guard and gate_escalation and gate_correctness:
        verdict = "HARD_PASS"
    elif not gate_calibration_discriminates:
        verdict = "MIDDLE_BAND"
    elif gate_growth and gate_guard and gate_escalation and not gate_correctness:
        verdict = "MIDDLE_BAND"  # loop mechanics sound, base-ingredient precision the open question
    else:
        verdict = "HARD_FAIL"

    verdict_msg = (
        f"{verdict}: growth={gate_growth}(net={net_growth},monotonic={monotonic_nondecreasing},"
        f"no_regress={no_regression}) guard={gate_guard}(n_grounded_wrongly="
        f"{adversarial_report['n_grounded_wrongly']}/{adversarial_report['n_items']}) "
        f"escalation={gate_escalation} correctness={gate_correctness}(pol_match={polarity_match_rate},"
        f"n={n_grounded_eval_verbs}) calibration_discriminates={gate_calibration_discriminates} | "
        f"reasons={hard_fail_reasons}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:200]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {"n_passes": n_passes, "min_confirm": min_confirm, "patience_max": patience_max,
                  "neutral_band": neutral_band, "signal_mode": signal_mode, "seed": seed,
                  "novels": list(novels), "context_dim": CTX_D},
        "corpus_stats": corpus_stats, "window_stats": win_stats,
        "calibration": calib_report,
        "growth_curve": growth_curve,
        "pass_reports": pass_reports,
        "net_growth": net_growth,
        "monotonic_nondecreasing": monotonic_nondecreasing,
        "no_regression": no_regression,
        "registered": registered,
        "correctness_table": correctness_table,
        "polarity_match_rate": polarity_match_rate,
        "n_grounded_eval_verbs": n_grounded_eval_verbs,
        "reference_baselines": {"majority_floor": MAJORITY_FLOOR_REF,
                                "signal_a_primary_pol_match": SIGNAL_A_PRIMARY_POL_MATCH_REF},
        "adversarial_wrong_context_probe": adversarial_report,
        "nonsense_escalation_probe": nonsense_report,
        "gates": {"growth": gate_growth, "guard": gate_guard, "escalation": gate_escalation,
                 "correctness": gate_correctness, "calibration_discriminates": gate_calibration_discriminates},
        "hard_fail_reasons": hard_fail_reasons,
        "final_library_status": {l: it.status for l, it in library.items.items()},
        "cardinality_ok": len(pass_reports) == n_passes,
        "expected_n_units": expected_n_units,
        "arms_differ_verified": True,  # adversarial/nonsense/main libraries are distinct Library() instances
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "closed-loop growth/guard-discrimination test; not an argmax/capacity-noise-floor cell",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# ------------------------------------------------------------------ self-test (real code path)
def self_test():
    """Fast real-code-path self-test: exercises the REAL Library/consolidation_pass/credit_window/
    context_vector machinery at tiny scale (not synthetic-only), plus the module's own self_test."""
    print("[self-test] hdlab.grounding_acquisition_loop.self_test()", flush=True)
    engine_result = _engine_self_test()
    assert engine_result["real_credit_window_exercised"] is True

    print("[self-test] real corpus slice: batching + calibration + consolidation", flush=True)
    all_rows, oov_rows = _load_eval()
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows_real, _win_stats = _build_windows(blocks, all_rows)
    windows_toy = windows_real[:250]   # small real slice: enough occurrences of common light verbs
                                       # (e.g. 'be'/'have') to reach MIN_CONFIRM within a self-test budget

    print("[self-test] real calibration on toy library (drives the threshold used below, matching run())",
          flush=True)
    calib_lib = Library()
    flag_batch(calib_lib, windows_toy, batch_start_wid=0, pass_idx=0, signal_mode="signal_a_only")
    thresh, calib_report = calibrate_schema_threshold(calib_lib, min_occ=2, max_lemmas=5)
    assert isinstance(thresh, float) and thresh > 0.0

    lib = Library()
    flag_report = flag_batch(lib, windows_toy, batch_start_wid=0, pass_idx=1, signal_mode="signal_a_only")
    assert flag_report["n_traces_added"] >= 4, f"expected >=4 real traces added, got {flag_report}"
    assert len(lib.items) >= 1, "real flag_batch on a real corpus slice created zero library items"
    r1 = consolidation_pass(lib, 1, min_confirm=4, schema_thresh=thresh, register=False)
    assert r1["cumulative_grounded"] == 0, "must not ground on the pass an item first reaches min_confirm"
    r2 = consolidation_pass(lib, 2, min_confirm=4, schema_thresh=thresh, register=False)
    assert r2["cumulative_grounded"] >= 1, (
        f"real end-to-end batching+consolidation on a real corpus slice must ground >=1 item by the "
        f"intervening pass, got r1={r1} r2={r2}")

    print("[self-test] real adversarial + nonsense probes at reduced scale (using the SAME calibrated "
          "threshold run() would use, not an arbitrary constant)", flush=True)
    adv = run_adversarial_wrong_context_probe(windows_real, schema_thresh=thresh, min_confirm=4,
                                              patience_max=3, neutral_band=0.34, n_items=1,
                                              n_passes_probe=6)
    assert adv["guard_rejected_all"], f"self-test adversarial probe did not guard-reject: {adv}"
    non = run_nonsense_escalation_probe(schema_thresh=thresh, min_confirm=4, patience_max=3,
                                        neutral_band=0.34, n_items=1, n_passes_probe=6)
    assert non["all_escalated"], f"self-test nonsense probe did not escalate: {non}"

    print("[self-test] PASS: real Library/consolidation/credit_window/calibration/probes all exercised",
          flush=True)
    return {"engine_self_test": engine_result, "flag_report": flag_report,
            "toy_calibration": calib_report, "adversarial_probe": adv, "nonsense_probe": non}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, run_mode="smoke", novels=SMOKE_NOVELS, n_passes=N_PASSES,
            min_confirm=MIN_CONFIRM, patience_max=PATIENCE_MAX, neutral_band=NEUTRAL_BAND,
            signal_mode=SIGNAL_MODE, seed=0)
    else:
        output_dir = OUTPUT_DIR_FULL
        run(output_dir, run_mode="full", novels=NOVELS, n_passes=N_PASSES,
            min_confirm=MIN_CONFIRM, patience_max=PATIENCE_MAX, neutral_band=NEUTRAL_BAND,
            signal_mode=SIGNAL_MODE, seed=0)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = OUTPUT_DIR_FULL
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
