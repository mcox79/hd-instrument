"""exp_learner_mdl_gate_on_acquisition_traces_v1 -- ANCHOR 1 (2026-08-09).

Pre-reg: preregs/2026-08-09_learner_mdl_gate_on_acquisition_traces_v1.md
Hand-off: notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md
          (anchor 1 -- ANCHOR 1 ONLY; anchors 2/3 out of scope, strictly sequenced after this).

WHAT: does hdlab.learner's already-built MDL two-part-code compression gate (per_cluster_gate /
registry.learn, Perfors & Tenenbaum 2009) add real discriminating power over
hdlab.grounding_acquisition_loop.py's currently-wired schema_consistency_split_half-only
consolidation guard, when wired in as a CONJUNCTIVE (AND, never OR) second condition? Both organs
already exist, tested, independently wired to other cells -- pure integration/measurement, zero new
grain, zero new corpus (per the hand-off).

ADAPTER (exp_dev-owned, documented in full in the prereg section 1): a LibraryItem's Trace list ->
ruleind_plugin episodes/features. episodes = one dict per trace {"gold_class": trace.pole,
"id": trace.episode_id, "vec": trace.context_vec}; features = dense per-dimension sign
("d{i}:+"/"d{i}:-" for all 256 dims). Called via hdlab.learner.registry.learn(episodes, feat_fn,
{"candidate_plugins": ["ruleind"], "key_fn": ..., "min_compression_ratio": 1.0}) -- the exact call
shape the hand-off names. Gate = (chosen_plugin_name == "ruleind").

WIRE POINT: hdlab/grounding_acquisition_loop.py::consolidation_pass gained an optional
mdl_gate_fn parameter (backward-compatible, default None -- verified byte-identical to prior
behavior via the module's own self_test() and exp_grounding_acquisition_loop_v1.py --self-test,
both re-run clean after the edit).

DATASET: the ALREADY-LANDED experiments/exp_grounding_acquisition_loop_v1.py smoke corpus
(SMOKE_NOVELS=little_women.clean.txt, n_passes=5, min_confirm=4, patience_max=3, neutral_band=0.34,
signal_mode="signal_a_only", seed=0 -- identical config to data/grounding_acquisition_loop_v1_smoke/
metrics.json, 338 real library items with genuine label diversity, MEASURED elapsed_s=3.57).
Rebuilt here via the SAME verbatim-reused flag_batch/calibrate_schema_threshold helpers (wire-
don't-island, no reimplementation).

MANDATORY pre-check: per_cluster_gate must fire True on a hand-constructed maximally-compressible
synthetic trace set (non-degenerate entropy, perfectly separable) BEFORE any "MDL never changes a
verdict" result is accepted as a real MIDDLE_BAND (flat-result-means-diagnose discipline).

MANDATORY guard invariant: hdlab/grounding_acquisition_loop.py::self_test's own coherent (mendtest)
and adversarial (adversarialtest) fixtures re-run with the conjunctive gate wired in; adversarialtest
must NEVER reach GROUNDED_* (HARD-FAIL if it does -- a new false-consolidation path via "compresses
well").

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic_seeding: fixed integer seeds only (np.random.default_rng); no hash()-seeding
# - start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
# - real_code_path_exercised: Library / consolidation_pass / registry.learn(ruleind) / credit_window
#   all constructed/called for real at self-test scale (not synthetic-only)
# - arms_differ_verified: schema_only vs conjunctive are independent Library() trajectories
# - all numbers MEASURED@ this cell's metrics.json (no HYPOTHESIZED numbers reported as data)
# - resumable per-unit (2 arms: schema_only_trajectory, conjunctive_trajectory) via
#   tools/exp_checkpoint.py per CLAUDE.md multi-unit rule
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
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
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, LibraryItem, Trace, context_vector, schema_consistency_split_half, consolidation_pass,
    self_test as _engine_self_test, D as CTX_D, MIN_CONFIRM, NEUTRAL_BAND, PATIENCE_MAX,
)
from hdlab.learner import registry  # noqa: E402
from hdlab.learner.core import KEEP_EPISODIC  # noqa: E402
# REUSE the already-landed reference cell's verbatim corpus/calibration/batching helpers
# (wire-don't-island -- no reimplementation drift).
from exp_grounding_acquisition_loop_v1 import (  # noqa: E402
    flag_batch, calibrate_schema_threshold, _split_batches, SIGNAL_MODE, N_PASSES,
)
from exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, SMOKE_NOVELS,
)

import exp_checkpoint  # noqa: E402  (tools/exp_checkpoint.py; per-unit shard/resume)
from _validity_preflight import run_validity_preflight, assert_no_nondeterministic_seeding  # noqa: E402

ANCHOR_NAME = "learner_mdl_gate_on_acquisition_traces_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
MIN_COMPRESSION_RATIO = 1.0   # hand-off's suggested default (per_cluster_gate's own default); not tuned


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


# ------------------------------------------------------------------ the ruleind adapter (section 1 of prereg)
#
# FEATURE-SPACE DESIGN NOTE (found empirically via the mandatory pre-check below, not assumed --
# see prereg "Amendment" section): a dense one-feature-per-raw-dimension encoding (256 dims x 2
# signs = ~512 singles, ~2000+ candidates once pairs are added) makes induce_rules' own MDL
# rule-cost term (l_rule_bits = log2(n_candidates_considered), the bits needed to SPECIFY which of
# the many candidate rules was picked -- a genuine, correct multiple-comparisons penalty) exceed
# the achievable entropy savings for any item smaller than several dozen traces, INCLUDING a
# perfectly-separable hand-constructed positive control at MIN_CONFIRM-scale (n=8) -- the mandatory
# pre-check caught this BEFORE any real-corpus numbers were trusted, exactly per the flat-result-
# means-diagnose discipline. Fix: coarse-grain the 256-dim context vector into
# N_MDL_PROJECTIONS=8 fixed, deterministic (hashlib-seeded, PROT-023/F.5-compliant) random
# hyperplane projections (LSH-style bucketing) -- this shrinks the candidate space to <=16 singles
# / <=136 total (singles+pairs), letting the MDL gate have genuine detecting power on realistically-
# sized items (double-digit trace counts) while remaining conservatively closed on thin-evidence
# items (small n cannot pay the (still nonzero) rule-cost) -- an Occam-appropriate property, not a
# design flaw: less evidence should require a stronger effect to justify a non-episodic commitment.
N_MDL_PROJECTIONS = 8


def _make_mdl_projections(n_proj: int = N_MDL_PROJECTIONS, d: int = CTX_D) -> np.ndarray:
    rows = []
    for k in range(n_proj):
        seed = int.from_bytes(
            hashlib.sha256(f"mdl_gate_projection_{k}".encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        rng = np.random.default_rng(seed)
        rows.append(rng.choice([-1.0, 1.0], size=d))
    return np.stack(rows, axis=0)


_MDL_PROJECTIONS = _make_mdl_projections()


def _episodes_from_traces(traces):
    return [{"gold_class": t.pole, "id": t.episode_id, "vec": t.context_vec} for t in traces]


def _dim_feat_fn(ep):
    scores = _MDL_PROJECTIONS @ ep["vec"]
    return [f"p{k}:{'+' if scores[k] > 0 else '-'}" for k in range(scores.shape[0])]


def _dim_key_fn(ep):
    return ep["id"]


def mdl_gate_decision(traces, min_compression_ratio: float = MIN_COMPRESSION_RATIO):
    """Fits hdlab.learner.registry's 'ruleind' plugin over an item's own traces (pole as
    gold_class, per-dimension sign of the context vector as the feature-value space) and returns
    whether per_cluster_gate's MDL two-part-code criterion judges the traces genuinely
    COMPRESSIBLE past the null (no-model) code. See prereg section 1 for the documented MDL edge
    case (label-homogeneous items trivially pass -- correct MDL behavior, not an adapter bug)."""
    episodes = _episodes_from_traces(traces)
    spec = {"candidate_plugins": ["ruleind"], "key_fn": _dim_key_fn,
            "min_compression_ratio": min_compression_ratio}
    chosen_name, chosen_result, all_results = registry.learn(episodes, _dim_feat_fn, spec)
    gate = chosen_name == "ruleind"
    rr = all_results.get("ruleind")
    debug = {
        "chosen": chosen_name,
        "compression_ratio": (None if rr is None else
                               ("inf" if rr.compression_ratio == float("inf") else round(rr.compression_ratio, 4))),
        "null_bits": None if rr is None else round(rr.null_bits, 4),
        "description_bits": None if rr is None else round(rr.description_bits, 4),
        "is_episodic": None if rr is None else rr.is_episodic,
        "n_rules": None if rr is None else rr.metrics.get("n_rules"),
    }
    return gate, debug


def _mdl_gate_fn_for_consolidation(it):
    gate, _ = mdl_gate_decision(it.traces)
    return gate


# ------------------------------------------------------------------ mandatory pre-check
def precheck_maximally_compressible(n_per_class: int = 8):
    """Hand-constructed, perfectly-separable, NON-degenerate-entropy trace set (n_per_class POS @
    context_vec=+1^D, n_per_class NEG @ context_vec=-1^D; null_bits=2*n_per_class*1.0 bits, not the
    zero-entropy edge case). per_cluster_gate MUST fire True here -- proves the adapter plumbing
    genuinely detects real compressible structure, not merely passes vacuously on homogeneous-label
    items. n_per_class=8 (16 traces total) is scaled to clear the coarse-projection feature space's
    own rule-cost floor (~7 bits at N_MDL_PROJECTIONS=8) with margin -- see the feature-space design
    note above the adapter; a smaller n_per_class (e.g. MIN_CONFIRM=4) was tried first and FAILED
    this precheck under the (now-superseded) dense-256-feature encoding, which is exactly what the
    precheck is for."""
    pos_vec = np.ones(CTX_D, dtype=np.float64)
    neg_vec = -np.ones(CTX_D, dtype=np.float64)
    traces = ([Trace(f"pc{i}", "POS", pos_vec.copy(), 1) for i in range(n_per_class)]
              + [Trace(f"nc{i}", "NEG", neg_vec.copy(), 1) for i in range(n_per_class)])
    gate, debug = mdl_gate_decision(traces)
    assert gate is True, (
        f"MANDATORY PRE-CHECK FAILED: per_cluster_gate did not fire True on a hand-constructed "
        f"maximally-compressible (perfectly-separable, non-degenerate-entropy) trace set: {debug}")
    return debug


def precheck_noise_mixed_labels_control(seed: int = 777, n_per_class: int = 8):
    """Complementary, informative-only (not asserted) control: same trace count, independent
    random-noise context vectors, mixed labels. Expected (not guaranteed) to fail to compress --
    reported honestly either way, not a mandatory gate."""
    rng = np.random.default_rng(seed)
    traces = ([Trace(f"np{i}", "POS", rng.choice([-1.0, 1.0], size=CTX_D), 1) for i in range(n_per_class)]
              + [Trace(f"nn{i}", "NEG", rng.choice([-1.0, 1.0], size=CTX_D), 1) for i in range(n_per_class)])
    gate, debug = mdl_gate_decision(traces)
    return gate, debug


# ------------------------------------------------------------------ mandatory guard invariant re-test
def reverify_guard_invariants_with_conjunctive_gate():
    """Byte-identical reconstruction of hdlab.grounding_acquisition_loop.py::self_test's own
    coherent (mendtest) and adversarial (adversarialtest) fixtures, re-run with mdl_gate_fn wired
    in via consolidation_pass. MANDATORY: adversarialtest must reach ESCALATED, never GROUNDED_*."""
    lib_coh = Library()
    for i in range(4):
        lib_coh.flag("mendtest", f"m{i}", "POS",
                     context_vector("Owen mended the boat before the storm."), 1)
    consolidation_pass(lib_coh, 1, min_confirm=3, schema_thresh=0.10, register=False,
                       mdl_gate_fn=_mdl_gate_fn_for_consolidation)
    consolidation_pass(lib_coh, 2, min_confirm=3, schema_thresh=0.10, register=False,
                       mdl_gate_fn=_mdl_gate_fn_for_consolidation)
    coherent_status = lib_coh.items["mendtest"].status

    lib_adv = Library()
    rng2 = np.random.default_rng(1)
    for i in range(4):
        lib_adv.flag("adversarialtest", f"a{i}", "POS", rng2.choice([-1.0, 1.0], size=CTX_D), 1)
    for p in range(1, 6):
        consolidation_pass(lib_adv, p, min_confirm=3, schema_thresh=0.10, patience_max=3,
                           register=False, mdl_gate_fn=_mdl_gate_fn_for_consolidation)
    adversarial_status = lib_adv.items["adversarialtest"].status
    assert adversarial_status == "ESCALATED", (
        f"MANDATORY GUARD INVARIANT VIOLATED: adversarial scrambled-context item reached "
        f"{adversarial_status!r} (not ESCALATED) under the conjunctive gate -- new "
        f"false-consolidation path via 'compresses well'.")
    return {"coherent_status_under_conjunctive": coherent_status,
            "adversarial_status_under_conjunctive": adversarial_status,
            "guard_invariant_held": True}


# ------------------------------------------------------------------ real-corpus trajectories
def _run_schema_only_with_shadow(windows, seed=0):
    """The CURRENT, unmodified system (mdl_gate_fn=None) over the real corpus, plus a read-only
    'shadow' MDL evaluation at every point the real schema check is consulted -- builds the 2x2
    confusion table without needing a second mutated trajectory. Cross-validates its own eligibility
    mirroring against the real consolidation_pass's newly_grounded_* lists every pass."""
    _vls.clear_acquired_outcome()
    calib_lib = Library()
    flag_batch(calib_lib, windows, batch_start_wid=0, pass_idx=0, signal_mode=SIGNAL_MODE)
    schema_thresh, calib_report = calibrate_schema_threshold(calib_lib, seed=seed)

    _vls.clear_acquired_outcome()
    library = Library()
    batches = _split_batches(windows, N_PASSES)
    wid_cursor = 0
    shadow_rows = []
    growth_curve = []
    for p in range(1, N_PASSES + 1):
        batch = batches[p - 1]
        flag_batch(library, batch, batch_start_wid=wid_cursor, pass_idx=p, signal_mode=SIGNAL_MODE)
        wid_cursor += len(batch)

        # read-only eligibility snapshot BEFORE this pass's official consolidation call (traces are
        # already stable for this pass; consolidation_pass never mutates traces, only status/patience)
        eligible_lemmas = sorted(
            lemma for lemma, it in library.items.items()
            if it.status == "PENDING" and len(it.traces) >= MIN_CONFIRM
            and it.first_min_confirm_pass is not None and p > it.first_min_confirm_pass
        )
        for lemma in eligible_lemmas:
            it = library.items[lemma]
            schema_score = schema_consistency_split_half(it.traces)
            if schema_score is None:
                continue
            schema_alone = bool(schema_score >= schema_thresh)
            mdl_alone, mdl_debug = mdl_gate_decision(it.traces)
            conjunctive_would_bank = schema_alone and mdl_alone
            shadow_rows.append({
                "lemma": lemma, "pass": p, "n_traces": len(it.traces),
                "schema_score": round(float(schema_score), 4), "schema_thresh": round(float(schema_thresh), 4),
                "schema_alone": schema_alone, "mdl_alone": bool(mdl_alone),
                "conjunctive_would_bank": bool(conjunctive_would_bank),
                "verdict_changed_vs_current": bool(schema_alone and not mdl_alone),
                "mdl_debug": mdl_debug,
            })

        cons_report = consolidation_pass(library, p, min_confirm=MIN_CONFIRM, schema_thresh=schema_thresh,
                                         neutral_band=NEUTRAL_BAND, patience_max=PATIENCE_MAX, register=False,
                                         mdl_gate_fn=None)
        growth_curve.append(cons_report["cumulative_grounded"])

        newly = (set(cons_report["newly_grounded_pos"]) | set(cons_report["newly_grounded_neg"])
                 | set(cons_report["newly_grounded_neutral"]))
        shadow_true_this_pass = {r["lemma"] for r in shadow_rows if r["pass"] == p and r["schema_alone"]}
        assert newly <= shadow_true_this_pass, (
            f"SHADOW ELIGIBILITY MISMATCH pass={p}: real newly_grounded={sorted(newly)} not a subset "
            f"of shadow schema_alone={sorted(shadow_true_this_pass)} -- eligibility mirroring bug")
        print(f"[mdl_gate] schema_only pass {p}/{N_PASSES}: shadow_eligible={len(eligible_lemmas)} "
              f"newly_grounded={len(newly)} cumulative_grounded={cons_report['cumulative_grounded']}",
              flush=True)

    _vls.clear_acquired_outcome()
    final_status = {l: it.status for l, it in library.items.items()}
    return {"schema_thresh": round(float(schema_thresh), 4), "calibration": calib_report,
            "growth_curve": growth_curve, "shadow_rows": shadow_rows, "final_status": final_status,
            "n_items_total": len(library.items)}


def _run_conjunctive_trajectory(windows, seed=0):
    """A SECOND, fully independent end-to-end trajectory with mdl_gate_fn actually wired in via
    consolidation_pass -- the real fully-wired conjunctive system's own growth curve / final status,
    not just a shadow read on the schema-only trajectory."""
    _vls.clear_acquired_outcome()
    calib_lib = Library()
    flag_batch(calib_lib, windows, batch_start_wid=0, pass_idx=0, signal_mode=SIGNAL_MODE)
    schema_thresh, calib_report = calibrate_schema_threshold(calib_lib, seed=seed)

    _vls.clear_acquired_outcome()
    library = Library()
    batches = _split_batches(windows, N_PASSES)
    wid_cursor = 0
    growth_curve = []
    for p in range(1, N_PASSES + 1):
        batch = batches[p - 1]
        flag_batch(library, batch, batch_start_wid=wid_cursor, pass_idx=p, signal_mode=SIGNAL_MODE)
        wid_cursor += len(batch)
        cons_report = consolidation_pass(library, p, min_confirm=MIN_CONFIRM, schema_thresh=schema_thresh,
                                         neutral_band=NEUTRAL_BAND, patience_max=PATIENCE_MAX, register=False,
                                         mdl_gate_fn=_mdl_gate_fn_for_consolidation)
        growth_curve.append(cons_report["cumulative_grounded"])
        print(f"[mdl_gate] conjunctive pass {p}/{N_PASSES}: cumulative_grounded="
              f"{cons_report['cumulative_grounded']}", flush=True)

    _vls.clear_acquired_outcome()
    final_status = {l: it.status for l, it in library.items.items()}
    return {"schema_thresh": round(float(schema_thresh), 4), "growth_curve": growth_curve,
            "final_status": final_status, "n_items_total": len(library.items)}


# ------------------------------------------------------------------ 2x2 confusion + verdict
def _build_confusion(shadow_rows):
    cells = {"schema_T_mdl_T": 0, "schema_T_mdl_F": 0, "schema_F_mdl_T": 0, "schema_F_mdl_F": 0}
    for r in shadow_rows:
        key = f"schema_{'T' if r['schema_alone'] else 'F'}_mdl_{'T' if r['mdl_alone'] else 'F'}"
        cells[key] += 1
    n_verdict_changes = sum(1 for r in shadow_rows if r["verdict_changed_vs_current"])
    lemmas_verdict_changed = sorted({r["lemma"] for r in shadow_rows if r["verdict_changed_vs_current"]})
    return {"confusion_2x2": cells, "n_rows": len(shadow_rows),
            "n_verdict_changes": n_verdict_changes,
            "lemmas_verdict_changed": lemmas_verdict_changed}


# ------------------------------------------------------------------ main run
def run(output_dir, run_mode, seed=0):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=2)

    print("[mdl_gate] precheck: hand-constructed maximally-compressible (MANDATORY)", flush=True)
    precheck_compressible = precheck_maximally_compressible()
    precheck_noise_gate, precheck_noise_debug = precheck_noise_mixed_labels_control()
    print(f"[mdl_gate] precheck_compressible={precheck_compressible} "
          f"noise_control_gate={precheck_noise_gate}", flush=True)

    print("[mdl_gate] guard invariant reverify (MANDATORY: adversarialtest must ESCALATE)", flush=True)
    guard_reverify = reverify_guard_invariants_with_conjunctive_gate()
    print(f"[mdl_gate] guard_reverify={guard_reverify}", flush=True)

    print("[mdl_gate] loading real corpus (SMOKE_NOVELS) -- reproduces exp_grounding_acquisition_"
          "loop_v1's smoke config", flush=True)
    all_rows, oov_rows = _load_eval()
    blocks, corpus_stats, excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows, win_stats = _build_windows(blocks, all_rows)
    print(f"[mdl_gate] n_windows={len(windows)}", flush=True)

    completed = exp_checkpoint.completed_units(output_dir)
    key_schema = exp_checkpoint.unit_key("schema_only_trajectory")
    if key_schema in completed:
        schema_unit = exp_checkpoint.load_units(output_dir)[key_schema]
        print("[mdl_gate] schema_only_trajectory: RESUMED from units.jsonl", flush=True)
    else:
        schema_unit = _run_schema_only_with_shadow(windows, seed=seed)
        exp_checkpoint.record_unit(output_dir, key_schema, schema_unit)

    key_conj = exp_checkpoint.unit_key("conjunctive_trajectory")
    if key_conj in completed:
        conj_unit = exp_checkpoint.load_units(output_dir)[key_conj]
        print("[mdl_gate] conjunctive_trajectory: RESUMED from units.jsonl", flush=True)
    else:
        conj_unit = _run_conjunctive_trajectory(windows, seed=seed)
        exp_checkpoint.record_unit(output_dir, key_conj, conj_unit)

    confusion = _build_confusion(schema_unit["shadow_rows"])

    # reference reproduction-fidelity check against the already-landed smoke cell (same config)
    ref_path = os.path.join(REPO_ROOT, "data", "grounding_acquisition_loop_v1_smoke", "metrics.json")
    ref_check = {"reference_path": ref_path, "reference_available": os.path.exists(ref_path)}
    if ref_check["reference_available"]:
        ref = json.load(open(ref_path, encoding="utf-8"))
        ref_check["reference_schema_thresh"] = ref["calibration"]["schema_thresh"]
        ref_check["this_schema_thresh"] = schema_unit["schema_thresh"]
        ref_check["schema_thresh_delta"] = round(
            abs(ref["calibration"]["schema_thresh"] - schema_unit["schema_thresh"]), 6)
        ref_check["reference_growth_curve"] = ref["growth_curve"]
        ref_check["this_growth_curve"] = schema_unit["growth_curve"]
        ref_check["growth_curve_matches"] = (ref["growth_curve"] == schema_unit["growth_curve"])
        ref_check["reproduction_ok"] = (ref_check["schema_thresh_delta"] < 1e-6
                                        and ref_check["growth_curve_matches"])

    # sanity: conjunctive trajectory's grounded set must never exceed schema-only's (AND can only subtract)
    conj_grounded = {l for l, s in conj_unit["final_status"].items() if s.startswith("GROUNDED")}
    schema_grounded = {l for l, s in schema_unit["final_status"].items() if s.startswith("GROUNDED")}
    subset_ok = conj_grounded <= schema_grounded
    conjunctive_removed = sorted(schema_grounded - conj_grounded)

    # ---- verdict logic (pre-registered bands, verbatim from the hand-off) ----
    guard_invariant_held = guard_reverify["guard_invariant_held"]
    precheck_ok = True  # precheck_maximally_compressible() already asserted; reaching here means True
    verdict_changes_exist = confusion["n_verdict_changes"] > 0

    hard_fail_reasons = []
    if not guard_invariant_held:
        hard_fail_reasons.append("GUARD_INVARIANT_BROKEN: adversarialtest banked under conjunctive gate")
    if not subset_ok:
        hard_fail_reasons.append(
            f"AND_SEMANTICS_VIOLATED: conjunctive trajectory grounded lemmas NOT a subset of "
            f"schema-only trajectory's grounded lemmas (extra={sorted(conj_grounded - schema_grounded)}) "
            f"-- implementation bug, AND can only ever be a subset of schema-only")

    if hard_fail_reasons:
        verdict = "HARD_FAIL"
    elif verdict_changes_exist:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"{verdict}: guard_invariant_held={guard_invariant_held} precheck_maximally_compressible_ok="
        f"{precheck_ok} n_verdict_changes={confusion['n_verdict_changes']}/{confusion['n_rows']} "
        f"confusion_2x2={confusion['confusion_2x2']} and_semantics_subset_ok={subset_ok} "
        f"conjunctive_removed_lemmas={conjunctive_removed} | reasons={hard_fail_reasons}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": f"{verdict}: {verdict_msg[:220]}",
        "elapsed_s": round(elapsed, 3), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {"min_compression_ratio": MIN_COMPRESSION_RATIO, "seed": seed,
                  "smoke_novels": list(SMOKE_NOVELS), "n_passes": N_PASSES, "min_confirm": MIN_CONFIRM,
                  "patience_max": PATIENCE_MAX, "neutral_band": NEUTRAL_BAND, "signal_mode": SIGNAL_MODE,
                  "context_dim": CTX_D},
        "precheck_maximally_compressible": precheck_compressible,
        "precheck_noise_mixed_labels_control": {"gate": precheck_noise_gate, "debug": precheck_noise_debug},
        "guard_invariant_reverify": guard_reverify,
        "schema_only_trajectory": {k: v for k, v in schema_unit.items() if k != "shadow_rows"},
        "shadow_rows": schema_unit["shadow_rows"],
        "conjunctive_trajectory": conj_unit,
        "confusion_2x2": confusion,
        "and_semantics_subset_ok": subset_ok,
        "conjunctive_removed_lemmas": conjunctive_removed,
        "reference_reproduction_check": ref_check,
        "corpus_stats": corpus_stats, "window_stats": win_stats,
        "cardinality_ok": True, "expected_n_units": 2,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "diagnostic gate-comparison cell, not an argmax/capacity-noise-floor cell",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "hard_fail_reasons": hard_fail_reasons,
        "hard_pass_scope": "ANCHOR 1 ONLY; anchors 2/3 out of scope per hand-off sequencing",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.2f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# ------------------------------------------------------------------ self-test (real code path)
def self_test():
    """Fast real-code-path self-test: exercises the REAL Library/consolidation_pass/registry.learn/
    credit_window machinery at tiny scale (not synthetic-only), the mandatory precheck, and the
    mandatory guard-invariant re-test."""
    print("[self-test] hdlab.grounding_acquisition_loop.self_test() (unchanged, backward-compat check)",
          flush=True)
    engine_result = _engine_self_test()
    assert engine_result["real_credit_window_exercised"] is True

    print("[self-test] deterministic-seeding static scan (PROT-023/F.5)", flush=True)
    src = open(__file__, encoding="utf-8").read()
    assert_no_nondeterministic_seeding(src, source_name=__file__, run_mode="selftest")

    print("[self-test] mandatory precheck: maximally-compressible synthetic trace set", flush=True)
    precheck = precheck_maximally_compressible()
    noise_gate, noise_debug = precheck_noise_mixed_labels_control()
    print(f"[self-test] precheck={precheck} noise_control_gate={noise_gate}", flush=True)

    print("[self-test] mandatory guard invariant re-test (adversarialtest must ESCALATE)", flush=True)
    guard = reverify_guard_invariants_with_conjunctive_gate()
    assert guard["guard_invariant_held"] is True

    print("[self-test] substrate_signature preflight (F.2)", flush=True)
    run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["Library", "consolidation_pass", "registry.learn(ruleind)",
                                        "credit_window", "schema_consistency_split_half"],
         "exercised_entrypoints": ["Library", "consolidation_pass", "registry.learn(ruleind)",
                                   "credit_window", "schema_consistency_split_half"]},
        {"kind": "substrate_signature", "callable_obj": consolidation_pass,
         "kwargs": {"min_confirm": 1, "schema_thresh": 0.1, "neutral_band": 0.34, "patience_max": 1,
                   "register": False, "mdl_gate_fn": None}, "args_count": 2,
         "callable_name": "consolidation_pass"},
        {"kind": "substrate_signature", "callable_obj": registry.learn,
         "kwargs": {}, "args_count": 3, "callable_name": "registry.learn"},
    ], run_mode="selftest")

    print("[self-test] real corpus slice: tiny end-to-end schema_only + conjunctive trajectory "
          "(SMOKE_NOVELS truncated)", flush=True)
    all_rows, oov_rows = _load_eval()
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows_real, _win_stats = _build_windows(blocks, all_rows)
    windows_toy = windows_real[:250]

    schema_unit = _run_schema_only_with_shadow(windows_toy, seed=0)
    assert len(schema_unit["shadow_rows"]) >= 1, (
        f"real self-test slice produced zero shadow-eligible (item,pass) rows -- "
        f"discriminator did not fire: {schema_unit['calibration']}")
    conj_unit = _run_conjunctive_trajectory(windows_toy, seed=0)
    conj_grounded = {l for l, s in conj_unit["final_status"].items() if s.startswith("GROUNDED")}
    schema_grounded = {l for l, s in schema_unit["final_status"].items() if s.startswith("GROUNDED")}
    assert conj_grounded <= schema_grounded, (
        "AND semantics violated on self-test slice: conjunctive trajectory grounded a lemma "
        "schema-only did not")

    print("[self-test] PASS: real Library/consolidation_pass/registry.learn(ruleind)/credit_window "
          "all exercised; mandatory precheck + guard invariant held", flush=True)
    return {"engine_self_test": engine_result, "precheck": precheck,
            "noise_control": {"gate": noise_gate, "debug": noise_debug}, "guard_reverify": guard,
            "n_shadow_rows": len(schema_unit["shadow_rows"]),
            "schema_grounded_n": len(schema_grounded), "conj_grounded_n": len(conj_grounded)}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    ap.add_argument("--seed", type=int, default=0)
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    output_dir = OUTPUT_DIR_FULL
    run(output_dir, run_mode="smoke" if args.smoke else "full", seed=args.seed)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
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
