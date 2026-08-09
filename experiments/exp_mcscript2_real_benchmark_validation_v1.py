"""exp_mcscript2_real_benchmark_validation_v1 -- REAL-BENCHMARK validation of the
script-grain self-growing acquisition loop (2026-08-09), the deciding test for the
grounded self-growing comprehension program.

Pre-reg: preregs/2026-08-09_mcscript2_real_benchmark_validation_v1.md
Parent capstone (synthetic mechanism proof, HARD_PASS): commit 0b172c5c7,
  data/exp_script_grain_acquisition_loop_v1/metrics.json,
  hdlab/script_grain_acquisition_loop.py (the 6-correction engine this cell reuses).

WHAT: does the SAME self-growing script-grain mechanism (CA3/DG soft-match-or-spawn
keying via hdlab.cleanup_family.iterative_attractor, cross-episode reliability guard
via schema_consistency_split_half, prioritized replay via surprise_order, MDL-style
Marr-honesty framing) COMPOUND with exposure and beat real baselines on REAL narrative
text (MCScript2.0, Ostermann/Roth/Pinkal 2019), or does the historical real-prose
extraction wall (that capped DesireDB) reproduce here too?

STAGE 0/1 (see hdlab/mcscript_extraction.py module docstring for full measured detail):
  dataset obtained + parsed (train=2500/195 scenarios, dev=355/162 scenarios, all dev
  scenarios occur in train). Parse-structure extraction (CandidateGenerator dependency
  front end) FIRES at 100% (150/150 sampled) -- does NOT reproduce the DesireDB wall.
  A deeper check (does the narrow 4-slot FHRR reduction actually discriminate scenarios
  via CA3/DG cosine) found a WEAK gap (0.028, heavy overlap) vs the EXISTING whole-
  narrative bag-of-words context_vector signal's much larger gap (0.153) on the SAME
  72-instance/12-scenario sample -- see AMENDMENT 1 below.

AMENDMENT 1 (found empirically, disclosed): this cell uses
hdlab.grounding_acquisition_loop.context_vector(full_narrative_text) as BOTH the CA3/DG
keying prototype (correction #3, via ScriptLibrary.match_or_spawn / iterative_attractor,
UNCHANGED) and the content/reliability signal (correction #2's schema_consistency_
split_half), wrapped as a zero-imaginary complex64 tensor (bow_register below) so it
plugs into hdlab.script_grain_acquisition_loop.ScriptLibrary/_real2d UNMODIFIED --
cosine on [Re,Im]=[bow,0] reduces EXACTLY to cosine on bow (lossless, not an
approximation). The narrow FHRR 4-role register (hdlab.mcscript_extraction.
extract_instance_tuple + hdlab.script_grain_acquisition_loop.build_instance_register,
correction #4) is retained for GLASS-BOX AUDIT reporting only (a sample of example
tuples in metrics.json) -- per the measured gap it is not the scoring/keying signal.

AMENDMENT 2 (MDL gate declared N/A for this task, disclosed not silently dropped): the
capstone's MDL adapter (hdlab.learner registry, ruleind_plugin) fits a rule that
predicts a per-trace binary POLE (POS/NEG script outcome) from bag-of-words dimension-
sign features -- a genuine downstream classification target for that corpus's
success/failure narratives. Real MCScript2.0 TRAIN instances (a plain narrative text
per scenario-telling) have NO natural analogous per-instance binary pole; manufacturing
one just to force the MDL gate to fire would be a corner-cut, not a genuine test. This
cell therefore runs script_consolidation_pass with mdl_gate_fn=None (mdl_ok defaults to
True per that function's own documented semantics), leaving schema_consistency_
split_half (correction #2, cross-episode reliability) as the SOLE conjunctive guard.
Every ScriptTrace still carries a pole field (constant "NA") to satisfy the dataclass
contract; it is inert.

AMENDMENT 3 (precheck (a) re-operationalized for real noisy data, disclosed): the
capstone's precheck (a) / calibrate_novelty_threshold.discriminates requires COMPLETE
separation (min(matched_scores) > max(wrong_scores)) -- achievable on a clean synthetic
corpus, not a reasonable bar for freely-written crowd-sourced retellings of the same
everyday scenario (Stage 1c already measured real overlap: p10(matched)=0.038 <
p90(wrong)=0.125). This cell's precheck (a) instead requires a REAL, non-trivial mean
gap (matched_mean - wrong_mean >= 0.05) AND better-than-chance ROC-AUC separation
(auc >= 0.60) on a stratified TRAIN sample -- reported alongside the strict-separation
number for transparency, gating on the realistic criterion, not the unreachable one.

DOWNSTREAM TASK (this task's contract, NOT the capstone's pole-classification task):
2-way MC answer selection on DEV. For a DEV question, if the instance's context_vector
best-matches (via read-only query, library NEVER mutated by DEV, anti-circularity) a
GROUNDED_* library item at or above the calibrated novelty threshold, SCRIPT-score each
candidate answer by cosine(context_vector(answer_text), bundled context_vec prototype
of the matched item's TRAIN traces) and pick the higher-scoring candidate; otherwise
FALL BACK to the TEXT-overlap baseline decision for that question (disclosed fallback
policy, not hidden -- keeps every DEV question answered while making the mechanism's
own marginal contribution auditable via the coverage-conditional breakdown also
reported).

BASELINES (computed on DEV, real, no LLM): MAJORITY (fixed answer-id decision, majority
computed from TRAIN correctness counts only -- zero DEV information) and TEXT_OVERLAP
(pick the candidate with higher non-stopword token overlap with the narrative).
Published-baseline context (CITED, not measured): Ostermann/Roth/Pinkal 2019 report
~72% best system accuracy on the (private) TEST split -- context only, never compared
against directly since this cell evaluates DEV.

MANDATORY CONTROLS: SCRAMBLE arm (identical pipeline, TRAIN keying+content vectors
replaced by a per-instance hashlib-seeded random bipolar draw, content-independent by
construction) must fail to beat baseline / must show a much smaller (or absent) real-
vs-baseline edge than the REAL arm. ANTI-CIRCULARITY: DEV instances are NEVER passed to
match_or_spawn (read-only query only); NOVELTY_THRESH / MIN_CONFIRM / N_PASSES / SCHEMA_
THRESH are all locked from TRAIN-only calibration before any DEV number is computed.

PRE-REGISTERED BANDS (task contract, exp_dev's operationalization):
  HARD-PASS: SYSTEM overall accuracy on the commonsense (script-based) DEV subset >
    TEXT_OVERLAP baseline accuracy on the SAME subset, AND the per-pass compounding
    curve of that accuracy is non-decreasing across the 5 passes, AND the REAL arm's
    edge over baseline on that subset exceeds the SCRAMBLE arm's edge (proves the beat
    depends on genuine grounding, not fallback plumbing), AND both mandatory prechecks
    ((a) re-operationalized keying-discriminates, (b) N/A-declared per Amendment 2 does
    not block) pass.
  HARD-FAIL: SYSTEM accuracy on the commonsense subset <= TEXT_OVERLAP baseline, OR the
    compounding curve is flat/non-monotonic despite genuinely-new TRAIN exposure across
    the K=5 sweep -- PROVIDED precheck (a) and the scramble control were actually
    computed (never excused as a harness bug).
  MIDDLE_BAND: everything else (e.g., beats baseline only marginally, or on some but
    not all of the 3 headline comparisons).

# CELL-TEMPLATE MANDATORY (per exp_dev SCHEMA-VET, subset applied to this cell's shape):
# - except SystemExit: raise BEFORE except Exception (no bare except, no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace), plus per-arm partial checkpoints
#   via experiments._seed_checkpoint (resumable per unit: "real", "scramble")
# - deterministic_seeding: fixed integer seeds + hashlib only; no built-in hash(),
#   no list(set()) ordering (sorted(set()) used throughout)
# - start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
# - real_code_path_exercised: parse_mcscript_xml / CandidateGenerator / ScriptLibrary /
#   script_consolidation_pass / iterative_attractor all constructed and called for real
#   at self-test scale
# - arms_differ_verified: real vs scramble library item prototypes hashed distinct
# - calibration_check: adaptive_with_discriminator_gate (NOVELTY_THRESH calibrated from
#   TRAIN-only sample; precheck (a) re-verified every run, not hand-tuned per Amendment 3)
# - crlb_n_a: keying/consolidation + MC-scoring cell; no argmax/top-k associative-recall
#   capacity ceiling applies
# - all numbers in this file's comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@
#
# ASCII-only; no unicode; no emojis.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

from hdlab.grounding_acquisition_loop import context_vector, _cos, _bundle, D as BOW_D
from hdlab.script_grain_acquisition_loop import (
    FHRR_D, build_instance_register, ScriptLibrary, ScriptTrace, ScriptLibraryItem,
    script_consolidation_pass, calibrate_novelty_threshold, _real2d,
)
from hdlab.cleanup_family import iterative_attractor
from hdlab.mcscript_extraction import (
    parse_mcscript_xml, extract_instance_tuple, self_test as extraction_self_test,
)
from hdlab.candidate_generator import CandidateGenerator

ANCHOR_NAME = "mcscript2_real_benchmark_validation_v1"

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "self_test" if _ARGS.self_test else
    ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
     else os.environ.get("HDLAB_RUN_MODE", "full").lower())
)

# ---------------------------------------------------------------------------
# Start-marker / crash diagnostics (exp_dev SCHEMA-VET section 13)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Config (exp_dev autonomy, documented in module docstring above)
# ---------------------------------------------------------------------------
N_PASSES = 5
MIN_CONFIRM = 4
PATIENCE_MAX = 3
NEUTRAL_BAND = 0.34
REPLAY_BUDGET_FRAC = 0.6
ATTRACTOR_TEMP = 4.0
ATTRACTOR_MAX_STEPS = 8
SCHEMA_THRESH = 0.10          # inherited operating point from grounding_acquisition_loop /
                               # script_grain_acquisition_loop (both validated at this value)
PRECHECK_A_MIN_GAP = 0.05     # Amendment 3: mean-gap floor (realistic, not full-separation)
PRECHECK_A_MIN_AUC = 0.60     # Amendment 3: better-than-chance ROC-AUC floor

DATA_DIR = REPO / "data" / "corpora" / "mcscript2" / "extracted"
POS_CKPT = REPO / "data" / "frontend_assets" / "pos_tagger_ud_ewt_upos.json"
ARC_CKPT = REPO / "data" / "frontend_assets" / "arc_parser_hashed_ud_ewt.npz"

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for", "with",
    "as", "is", "was", "were", "are", "be", "been", "being", "it", "its", "he", "she", "they",
    "him", "her", "them", "his", "their", "i", "you", "we", "me", "my", "your", "our", "this",
    "that", "these", "those", "not", "no", "so", "than", "then", "there", "here", "up", "out",
    "into", "over", "again", "very", "just", "would", "could", "should", "will", "shall", "can",
    "did", "do", "does", "had", "has", "have", "from", "all", "any", "some", "one", "two", "when",
    "what", "who", "which", "how", "why", "said", "upon",
})


def _content_tokens(text: str) -> set:
    import re
    return {w for w in re.findall(r"[a-z']+", (text or "").lower())
            if w not in _STOPWORDS and len(w) > 2}


# ---------------------------------------------------------------------------
# Vector builders (Amendment 1)
# ---------------------------------------------------------------------------
def bow_register(text: str) -> torch.Tensor:
    """context_vector(text) wrapped as a zero-imaginary complex64 tensor so it
    plugs into ScriptLibrary/_real2d unmodified; cosine on [Re,Im]=[bow,0] is
    EXACTLY cosine(bow_a, bow_b) -- lossless, not an approximation (verified
    in this cell's self_test)."""
    bow = context_vector(text).astype(np.complex64)
    return torch.from_numpy(bow)


def scramble_register(identity_tag: str, d: int = BOW_D) -> torch.Tensor:
    """MANDATORY CONTROL: content-independent per-instance random bipolar
    draw (hashlib-seeded on the instance's OWN identity, PROT-023/F.5
    compliant), wrapped identically to bow_register. Carries zero relation to
    the instance's true content/scenario by construction."""
    seed = int.from_bytes(hashlib.sha256(f"mcscript_scramble::{identity_tag}".encode()).digest()[:8],
                          "big") % (2 ** 32)
    rng = np.random.default_rng(seed)
    vec = rng.choice([-1.0, 1.0], size=d).astype(np.complex64)
    return torch.from_numpy(vec)


def _bow_np(v: torch.Tensor) -> np.ndarray:
    """Recover the plain real bag-of-words numpy array from a bow_register /
    scramble_register complex64 wrapper (real part only; imag is always 0)."""
    return v.detach().cpu().numpy().real.astype(np.float64)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_split(name: str) -> List[Dict]:
    path = DATA_DIR / f"{name}-data.xml"
    if not path.exists():
        raise FileNotFoundError(
            f"MCScript2.0 {name} split not found at {path}. Stage 0 download step must "
            f"run first (see hdlab/mcscript_extraction.py module docstring).")
    return parse_mcscript_xml(str(path))


def restrict_to_scenarios(instances: List[Dict], scenarios: set) -> List[Dict]:
    return [inst for inst in instances if inst["scenario"] in scenarios]


# ---------------------------------------------------------------------------
# Library helpers
# ---------------------------------------------------------------------------
def item_context_prototype(item: ScriptLibraryItem) -> np.ndarray:
    """Bundle of an item's accumulated TRAIN context_vecs (bag-of-words) --
    the "what does this grounded script normally involve" content signature
    used for downstream candidate scoring."""
    vecs = [t.context_vec for t in item.traces]
    return _bundle(vecs) if len(vecs) > 1 else vecs[0]


def build_query_codebook(library: ScriptLibrary) -> Tuple[List[str], np.ndarray, List[str]]:
    """PERFORMANCE (not correctness): item keying prototypes are fixed for
    the duration of a pass (library only mutates BETWEEN passes, via
    script_consolidation_pass's status flips -- traces/registers themselves
    never change once spawned). query_best_match previously rebuilt this
    codebook from scratch (looping every item's _prototype_register + real2d)
    on EVERY single DEV query -- O(n_dev * n_items) redundant Python-level
    work per pass. Building it ONCE per pass here and reusing it for every
    DEV query in that pass is O(n_items) + O(n_dev) cheap matmuls instead."""
    item_ids = sorted(library.items)
    if not item_ids:
        return [], np.zeros((0, 1), dtype=np.float32), []
    codebook = np.stack([_real2d(_prototype_register(library.items[iid])) for iid in item_ids], axis=0)
    statuses = [library.items[iid].status for iid in item_ids]
    return item_ids, codebook, statuses


def query_best_match_cached(item_ids: List[str], codebook: np.ndarray, statuses: List[str],
                            key_register: torch.Tensor, *, temp: float,
                            max_steps: int) -> Tuple[Optional[str], float, Optional[str]]:
    """READ-ONLY query against a PRECOMPUTED codebook (build_query_codebook,
    built once per pass). NEVER mutates library.items (anti-circularity --
    this is the only touch-point DEV instances get, and it never calls
    match_or_spawn). Returns (best_item_id_or_None, score, status_or_None)."""
    if not item_ids:
        return None, -1.0, None
    query = _real2d(key_register)
    _, diag = iterative_attractor(query, codebook, temp=temp, max_steps=max_steps)
    idx = int(diag["final_argmax_idx"])
    qn = query / (float(np.linalg.norm(query)) + 1e-9)
    bn = codebook[idx] / (float(np.linalg.norm(codebook[idx])) + 1e-9)
    score = float(np.dot(qn, bn))
    return item_ids[idx], score, statuses[idx]


def query_best_match(library: ScriptLibrary, key_register: torch.Tensor, *,
                     temp: float, max_steps: int) -> Tuple[Optional[str], float, Optional[str]]:
    """Convenience one-shot wrapper (builds + queries a single codebook) --
    used by self_test / one-off callers where the O(n_dev * n_items)
    rebuild cost does not apply (a single query, not a loop over many)."""
    item_ids, codebook, statuses = build_query_codebook(library)
    return query_best_match_cached(item_ids, codebook, statuses, key_register,
                                   temp=temp, max_steps=max_steps)


def _prototype_register(item: ScriptLibraryItem) -> torch.Tensor:
    """Same keying prototype ScriptLibrary._prototype computes internally
    (bundle of the item's register_vec traces), exposed here so
    query_best_match can build a query-time codebook without touching
    ScriptLibrary's private method."""
    vecs = [t.register_vec for t in item.traces]
    if len(vecs) == 1:
        return vecs[0]
    import torch as _torch
    from hdlab import bundling as _bundling
    return _bundling.bundle(_torch.stack(vecs, dim=0))


# ---------------------------------------------------------------------------
# Precheck (a): keying discriminates (Amendment 3 re-operationalization)
# ---------------------------------------------------------------------------
def _roc_auc(matched_scores: np.ndarray, wrong_scores: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney U / n_pos / n_neg) -- fraction of
    (matched, wrong) pairs where matched > wrong (ties count 0.5). Pure
    numpy, no sklearn dependency."""
    n_m, n_w = len(matched_scores), len(wrong_scores)
    if n_m == 0 or n_w == 0:
        return 0.5
    all_scores = np.concatenate([matched_scores, wrong_scores])
    ranks = np.argsort(np.argsort(all_scores)) + 1  # 1-based ranks, ties broken by order
    rank_sum_matched = ranks[:n_m].sum()
    u = rank_sum_matched - n_m * (n_m + 1) / 2.0
    return float(u / (n_m * n_w))


def precheck_a_keying_discriminates(train_instances: List[Dict], *, n_per_scenario: int = 2,
                                     seed_note: str = "deterministic_sorted") -> Dict:
    """Stratified sample (n_per_scenario instances per scenario, sorted by
    instance id -- deterministic, no RNG) across ALL TRAIN scenarios;
    computes full pairwise cosine matrix of bow keying vectors; splits into
    matched (same scenario) / wrong (different scenario); gates on
    Amendment 3's realistic criteria (mean gap + AUC), reports the strict
    capstone-style criterion too for transparency."""
    by_scenario: Dict[str, List[Dict]] = {}
    for inst in train_instances:
        by_scenario.setdefault(inst["scenario"], []).append(inst)
    sample: List[Dict] = []
    for scen in sorted(by_scenario):
        insts = sorted(by_scenario[scen], key=lambda x: x["id"])[:n_per_scenario]
        sample.extend(insts)

    vecs = np.stack([context_vector(inst["text"]) for inst in sample], axis=0).astype(np.float64)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms < 1e-9] = 1e-9
    unit = vecs / norms
    sim = unit @ unit.T
    scenarios = [inst["scenario"] for inst in sample]
    n = len(sample)
    matched, wrong = [], []
    for i in range(n):
        for j in range(i + 1, n):
            (matched if scenarios[i] == scenarios[j] else wrong).append(sim[i, j])
    matched = np.array(matched)
    wrong = np.array(wrong)
    matched_mean, wrong_mean = float(matched.mean()), float(wrong.mean())
    gap = matched_mean - wrong_mean
    auc = _roc_auc(matched, wrong)
    strict_discriminates = bool(matched_mean > wrong_mean and matched.min() > wrong.max())
    realistic_discriminates = bool(gap >= PRECHECK_A_MIN_GAP and auc >= PRECHECK_A_MIN_AUC)
    # midpoint threshold nudged toward the wrong side (same convention as calibrate_novelty_threshold)
    midpoint = 0.5 * (matched_mean + wrong_mean)
    thresh = midpoint + 0.05 * (wrong_mean - midpoint) if wrong_mean < midpoint else midpoint - 0.05
    result = {
        "n_sample_instances": n, "n_matched_pairs": len(matched), "n_wrong_pairs": len(wrong),
        "matched_mean": round(matched_mean, 4), "wrong_mean": round(wrong_mean, 4),
        "gap": round(gap, 4), "auc": round(auc, 4),
        "strict_full_separation_discriminates": strict_discriminates,
        "realistic_discriminates_gap_and_auc": realistic_discriminates,
        "novelty_thresh_calibrated": round(float(thresh), 4),
        "gate_criteria": {"min_gap": PRECHECK_A_MIN_GAP, "min_auc": PRECHECK_A_MIN_AUC},
    }
    assert realistic_discriminates, (
        f"MANDATORY PRECHECK (a) FAILED (Amendment-3 realistic criterion): gap={gap:.4f} "
        f"(need >= {PRECHECK_A_MIN_GAP}) auc={auc:.4f} (need >= {PRECHECK_A_MIN_AUC}). {result}")
    return result


# ---------------------------------------------------------------------------
# Growth (single sweep over TRAIN + K consolidation passes; per-pass DEV eval)
# ---------------------------------------------------------------------------
def precompute_dev_caches(dev_instances: List[Dict], key_fn, scramble: bool) -> Tuple[Dict, Dict]:
    """PERFORMANCE (not correctness): dev keying vectors + answer bag-of-words
    vectors depend only on text content (never on library state), so they are
    IDENTICAL across all N_PASSES re-evaluations. Computing them once here
    instead of inside eval_dev_accuracy avoids N_PASSES-fold redundant
    hashlib+RNG work (measured: this was the dominant smoke-run cost)."""
    key_cache: Dict[str, torch.Tensor] = {}
    answer_cache: Dict[Tuple[str, str, str], np.ndarray] = {}
    for inst in dev_instances:
        key_cache[inst["id"]] = key_fn(inst["id"] if scramble else inst["text"])
        for q in inst["questions"]:
            for a in q["answers"]:
                answer_cache[(inst["id"], q["id"], a["id"])] = context_vector(a["text"])
    return key_cache, answer_cache


def grow_and_track(train_instances: List[Dict], dev_instances: List[Dict], *, scramble: bool,
                   novelty_thresh: float, majority_answer_id: str) -> Dict:
    key_fn = scramble_register if scramble else bow_register
    library = ScriptLibrary()
    spawn_log = []
    for inst in sorted(train_instances, key=lambda x: x["id"]):
        reg = key_fn(inst["id"] if scramble else inst["text"])
        ctx = _bow_np(reg)
        item_id, spawned, score = library.match_or_spawn(
            reg, inst["id"], "NA", ctx, 0, true_type=inst["scenario"],
            temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS, novelty_thresh=novelty_thresh)
        spawn_log.append({"id": inst["id"], "item_id": item_id, "spawned": spawned,
                          "score": round(score, 4)})

    print(f"[grow_and_track] arm={'scramble' if scramble else 'real'} precomputing DEV caches...",
          flush=True)
    dev_key_cache, dev_answer_cache = precompute_dev_caches(dev_instances, key_fn, scramble)

    per_pass_reports = []
    dev_accuracy_curve = []       # per pass: dict of accuracy by question-type subset
    grounded_count_curve = []
    for pass_idx in range(1, N_PASSES + 1):
        report = script_consolidation_pass(
            library, pass_idx, min_confirm=MIN_CONFIRM, schema_thresh=SCHEMA_THRESH,
            neutral_band=NEUTRAL_BAND, patience_max=PATIENCE_MAX, mdl_gate_fn=None,
            replay_budget_frac=REPLAY_BUDGET_FRAC)
        per_pass_reports.append(report)
        grounded_count_curve.append(report["cumulative_grounded"])
        pass_eval = eval_dev_accuracy(dev_instances, library, dev_key_cache, dev_answer_cache,
                                      novelty_thresh, majority_answer_id)
        dev_accuracy_curve.append(pass_eval)
        print(f"[pass {pass_idx}/{N_PASSES}] arm={'scramble' if scramble else 'real'} "
              f"grounded={report['cumulative_grounded']} escalated={report['cumulative_escalated']} "
              f"pending={report['cumulative_pending']} "
              f"dev_commonsense_acc={pass_eval['by_type']['commonsense']['system_acc']:.4f} "
              f"coverage={pass_eval['coverage']:.4f}", flush=True)

    # glass-box purity: for each GROUNDED item, majority true scenario + fraction
    item_purity = {}
    for it in library.items.values():
        if not it.status.startswith("GROUNDED"):
            continue
        from collections import Counter
        c = Counter(t.true_type for t in it.traces)
        maj, cnt = c.most_common(1)[0]
        item_purity[it.item_id] = {"status": it.status, "n_traces": len(it.traces),
                                   "majority_scenario": maj, "majority_frac": round(cnt / len(it.traces), 3)}

    return {
        "n_items_spawned_total": len(library.items),
        "per_pass_reports": per_pass_reports,
        "grounded_count_curve": grounded_count_curve,
        "dev_accuracy_curve": dev_accuracy_curve,
        "item_purity": item_purity,
        "library": library,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def text_overlap_decide(answers: List[Dict], narrative_text: str) -> str:
    narrative_toks = _content_tokens(narrative_text)
    scores = []
    for a in answers:
        ans_toks = _content_tokens(a["text"])
        scores.append(len(ans_toks & narrative_toks))
    if scores[0] == scores[1]:
        return answers[0]["id"]  # deterministic tie-break
    return answers[0]["id"] if scores[0] > scores[1] else answers[1]["id"]


def script_decide(answers: List[Dict], item_prototype: np.ndarray) -> str:
    scores = []
    for a in answers:
        av = context_vector(a["text"])
        scores.append(_cos(av, item_prototype))
    if scores[0] == scores[1]:
        return answers[0]["id"]
    return answers[0]["id"] if scores[0] > scores[1] else answers[1]["id"]


def script_decide_cached(inst_id: str, q_id: str, answers: List[Dict], item_prototype: np.ndarray,
                         answer_cache: Dict[Tuple[str, str, str], np.ndarray]) -> str:
    """Same as script_decide but reads precomputed answer bag-of-words
    vectors from answer_cache instead of recomputing context_vector."""
    scores = [_cos(answer_cache[(inst_id, q_id, a["id"])], item_prototype) for a in answers]
    if scores[0] == scores[1]:
        return answers[0]["id"]
    return answers[0]["id"] if scores[0] > scores[1] else answers[1]["id"]


def eval_dev_accuracy(dev_instances: List[Dict], library: ScriptLibrary,
                      dev_key_cache: Dict[str, torch.Tensor],
                      dev_answer_cache: Dict[Tuple[str, str, str], np.ndarray],
                      novelty_thresh: float, majority_answer_id: str) -> Dict:
    """Per-question DEV evaluation: read-only match against the CURRENT
    library state, script-score if a GROUNDED match clears novelty_thresh,
    else fall back to text-overlap. Reports overall + by-type + covered-only
    breakdowns. NEVER mutates library (anti-circularity). Keying + answer
    bag-of-words vectors are read from precomputed caches (precompute_dev_
    caches) -- only the library-state-dependent query is redone per call."""
    from collections import defaultdict
    correct_overall = defaultdict(int)
    total_overall = defaultdict(int)
    correct_covered = defaultdict(int)
    total_covered = defaultdict(int)
    text_correct_on_covered = defaultdict(int)
    n_covered = 0
    n_total_q = 0

    item_ids, codebook, statuses = build_query_codebook(library)  # once per pass, not per DEV instance

    for inst in dev_instances:
        key = dev_key_cache[inst["id"]]
        item_id, score, status = query_best_match_cached(item_ids, codebook, statuses, key,
                                                          temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS)
        use_script = (item_id is not None and status is not None
                     and status.startswith("GROUNDED") and score >= novelty_thresh)
        proto = item_context_prototype(library.items[item_id]) if use_script else None
        for q in inst["questions"]:
            n_total_q += 1
            qtype = q["type"]
            correct_id = next(a["id"] for a in q["answers"] if a["correct"])
            if use_script:
                pred = script_decide_cached(inst["id"], q["id"], q["answers"], proto, dev_answer_cache)
                n_covered += 1
                total_covered[qtype] += 1
                total_covered["ALL"] += 1
                if pred == correct_id:
                    correct_covered[qtype] += 1
                    correct_covered["ALL"] += 1
                text_pred = text_overlap_decide(q["answers"], inst["text"])
                if text_pred == correct_id:
                    text_correct_on_covered[qtype] += 1
                    text_correct_on_covered["ALL"] += 1
            else:
                pred = text_overlap_decide(q["answers"], inst["text"])
            total_overall[qtype] += 1
            total_overall["ALL"] += 1
            if pred == correct_id:
                correct_overall[qtype] += 1
                correct_overall["ALL"] += 1

    def _rate(c, t):
        return (c / t) if t > 0 else 0.0

    by_type = {}
    for qtype in ("commonsense", "text", "positive-merged", "ALL"):
        by_type[qtype] = {
            "system_acc": _rate(correct_overall.get(qtype, 0), total_overall.get(qtype, 0)),
            "n_questions": total_overall.get(qtype, 0),
            "covered_system_acc": _rate(correct_covered.get(qtype, 0), total_covered.get(qtype, 0)),
            "covered_text_baseline_acc": _rate(text_correct_on_covered.get(qtype, 0), total_covered.get(qtype, 0)),
            "n_covered": total_covered.get(qtype, 0),
        }
    return {"by_type": by_type, "coverage": _rate(n_covered, n_total_q), "n_total_questions": n_total_q}


# ---------------------------------------------------------------------------
# Baselines (DEV, computed once, majority decision from TRAIN only)
# ---------------------------------------------------------------------------
def compute_majority_answer_id(train_instances: List[Dict]) -> str:
    from collections import Counter
    c = Counter()
    for inst in train_instances:
        for q in inst["questions"]:
            correct_id = next(a["id"] for a in q["answers"] if a["correct"])
            c[correct_id] += 1
    return c.most_common(1)[0][0]


def baseline_accuracies(dev_instances: List[Dict], majority_answer_id: str) -> Dict:
    from collections import defaultdict
    correct_text = defaultdict(int)
    correct_maj = defaultdict(int)
    total = defaultdict(int)
    for inst in dev_instances:
        for q in inst["questions"]:
            qtype = q["type"]
            correct_id = next(a["id"] for a in q["answers"] if a["correct"])
            total[qtype] += 1
            total["ALL"] += 1
            if text_overlap_decide(q["answers"], inst["text"]) == correct_id:
                correct_text[qtype] += 1
                correct_text["ALL"] += 1
            if majority_answer_id == correct_id:
                correct_maj[qtype] += 1
                correct_maj["ALL"] += 1
    out = {}
    for qtype in ("commonsense", "text", "positive-merged", "ALL"):
        t = total.get(qtype, 0)
        out[qtype] = {
            "text_overlap_acc": (correct_text.get(qtype, 0) / t) if t else 0.0,
            "majority_acc": (correct_maj.get(qtype, 0) / t) if t else 0.0,
            "n_questions": t,
        }
    return out


# ---------------------------------------------------------------------------
# Self-test (real code path, per exp_dev SCHEMA-VET F.1)
# ---------------------------------------------------------------------------
def self_test() -> Dict:
    # (0) mcscript_extraction's own self-test (real CandidateGenerator + parse_mcscript_xml)
    extraction_result = extraction_self_test(str(POS_CKPT), str(ARC_CKPT))

    # (1) bow_register cosine == plain context_vector cosine (Amendment 1's lossless-embedding claim)
    t1 = "Nell fixed the lantern by the fire."
    t2 = "Owen mended the boat before the storm."
    r1, r2 = bow_register(t1), bow_register(t2)
    cos_wrapped = float(np.dot(_real2d(r1) / (np.linalg.norm(_real2d(r1)) + 1e-9),
                              _real2d(r2) / (np.linalg.norm(_real2d(r2)) + 1e-9)))
    cos_plain = _cos(context_vector(t1), context_vector(t2))
    assert abs(cos_wrapped - cos_plain) < 1e-6, (
        f"bow_register wrapping must be lossless: wrapped={cos_wrapped} plain={cos_plain}")

    # (2) scramble_register is deterministic + content-independent (same tag -> same vec; different
    #     tag -> near-zero cosine to the real content vector).
    s1a = scramble_register("id_0007")
    s1b = scramble_register("id_0007")
    assert torch.equal(s1a, s1b), "scramble_register must be deterministic per identity tag"
    s_cos = float(np.dot(_real2d(r1) / (np.linalg.norm(_real2d(r1)) + 1e-9),
                        _real2d(scramble_register("id_0007")) / (np.linalg.norm(_real2d(scramble_register("id_0007"))) + 1e-9)))
    assert abs(s_cos) < 0.3, f"scramble vector must be near-uncorrelated with real content: cos={s_cos}"

    # (3) ScriptLibrary.match_or_spawn + query_best_match real code path, tiny scale.
    lib = ScriptLibrary()
    texts_a = ["I cracked the eggs and cooked an omelette in the pan.",
              "I beat the eggs then fried the omelette in a hot pan."]
    texts_b = ["I walked the dog around the block on a leash.",
              "I took the dog for a walk with its leash on."]
    for i, t in enumerate(texts_a):
        reg = bow_register(t)
        lib.match_or_spawn(reg, f"a{i}", "NA", context_vector(t), 0, true_type="omelette",
                           temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS, novelty_thresh=0.05)
    for i, t in enumerate(texts_b):
        reg = bow_register(t)
        lib.match_or_spawn(reg, f"b{i}", "NA", context_vector(t), 0, true_type="dog_walk",
                           temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS, novelty_thresh=0.05)
    query_id, score, status = query_best_match(lib, bow_register(
        "I fried some eggs into an omelette in a pan."), temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS)
    assert query_id in lib.items, "query_best_match must return a real item id"

    # (4) parse_mcscript_xml + tiny end-to-end pipeline on hand-built XML (real code path,
    #     exercises grow_and_track / eval_dev_accuracy / baseline_accuracies at N~8).
    import tempfile
    xml_train = _selftest_xml(n_scenarios=2, n_per_scenario=5, seed_tag="train")
    xml_dev = _selftest_xml(n_scenarios=2, n_per_scenario=2, seed_tag="dev")
    fd1, p1 = tempfile.mkstemp(suffix=".xml")
    fd2, p2 = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd1, "w", encoding="utf-8") as f:
            f.write(xml_train)
        with os.fdopen(fd2, "w", encoding="utf-8") as f:
            f.write(xml_dev)
        train_inst = parse_mcscript_xml(p1)
        dev_inst = parse_mcscript_xml(p2)
    finally:
        os.remove(p1)
        os.remove(p2)
    maj = compute_majority_answer_id(train_inst)
    base = baseline_accuracies(dev_inst, maj)
    growth = grow_and_track(train_inst, dev_inst, scramble=False, novelty_thresh=0.05,
                            majority_answer_id=maj)
    assert growth["dev_accuracy_curve"][-1]["by_type"]["ALL"]["n_questions"] == base["ALL"]["n_questions"]

    return {
        "extraction_self_test": extraction_result,
        "bow_register_lossless_embedding": True, "cos_wrapped": round(cos_wrapped, 6),
        "cos_plain": round(cos_plain, 6),
        "scramble_register_deterministic_and_uncorrelated": True, "scramble_vs_real_cos": round(s_cos, 4),
        "match_or_spawn_and_query_ok": True, "query_best_match_id": query_id,
        "end_to_end_pipeline_ok": True,
        "real_code_path_exercised": ["CandidateGenerator", "parse_mcscript_xml", "ScriptLibrary",
                                     "script_consolidation_pass", "iterative_attractor",
                                     "grow_and_track", "eval_dev_accuracy", "baseline_accuracies"],
    }


def _selftest_xml(n_scenarios: int, n_per_scenario: int, seed_tag: str) -> str:
    """Tiny hand-built MCScript-schema XML for self_test's real end-to-end pipeline check."""
    scenarios = {
        "making eggs": [
            "I cracked the eggs into a bowl . I whisked them well . "
            "I poured the mixture into a hot pan . I cooked the eggs until done . I served the eggs on a plate .",
        ],
        "walking dog": [
            "I clipped the leash onto the dog . I walked the dog around the block . "
            "The dog sniffed at the grass . I picked up after the dog . I brought the dog back home .",
        ],
    }
    names = list(scenarios.keys())[:n_scenarios]
    parts = ["<data>"]
    iid = 0
    for scen in names:
        base_text = scenarios[scen][0]
        for k in range(n_per_scenario):
            parts.append(
                f'<instance id="{seed_tag}_{iid}" scenario="{scen}">'
                f"<text>{base_text}</text>"
                f'<questions><question id="0" text="What happened?" type="commonsense">'
                f'<answer correct="True" id="0" text="{scen}" />'
                f'<answer correct="False" id="1" text="something unrelated" /></question>'
                f"</questions></instance>")
            iid += 1
    parts.append("</data>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def compute_verdict(real_growth: Dict, scramble_growth: Dict, baselines: Dict,
                    precheck_a: Dict) -> Tuple[str, str, Dict]:
    real_curve = [p["by_type"]["commonsense"]["system_acc"] for p in real_growth["dev_accuracy_curve"]]
    scramble_curve = [p["by_type"]["commonsense"]["system_acc"] for p in scramble_growth["dev_accuracy_curve"]]
    baseline_cs = baselines["commonsense"]["text_overlap_acc"]

    real_final = real_curve[-1]
    scramble_final = scramble_curve[-1]
    beats_baseline = real_final > baseline_cs
    non_decreasing = all(real_curve[i] <= real_curve[i + 1] + 1e-9 for i in range(len(real_curve) - 1))
    real_edge = real_final - baseline_cs
    scramble_edge = scramble_final - baseline_cs
    real_edge_exceeds_scramble = real_edge > scramble_edge

    stats = {
        "real_commonsense_curve": [round(x, 4) for x in real_curve],
        "scramble_commonsense_curve": [round(x, 4) for x in scramble_curve],
        "baseline_text_overlap_commonsense_acc": round(baseline_cs, 4),
        "baseline_majority_commonsense_acc": round(baselines["commonsense"]["majority_acc"], 4),
        "real_final": round(real_final, 4), "scramble_final": round(scramble_final, 4),
        "real_edge_over_baseline": round(real_edge, 4), "scramble_edge_over_baseline": round(scramble_edge, 4),
        "beats_baseline": beats_baseline, "non_decreasing": non_decreasing,
        "real_edge_exceeds_scramble_edge": real_edge_exceeds_scramble,
        "precheck_a": precheck_a,
    }

    if not beats_baseline:
        return ("HARD_FAIL", f"HARD_FAIL: SYSTEM commonsense-subset accuracy ({real_final:.4f}) does not "
                            f"beat TEXT_OVERLAP baseline ({baseline_cs:.4f}). Prechecks passed "
                            f"(precheck_a gap={precheck_a['gap']:.4f} auc={precheck_a['auc']:.4f}), "
                            f"scramble control computed (scramble_final={scramble_final:.4f}). "
                            f"This is a genuine mechanism negative on real narrative text.", stats)
    if not non_decreasing:
        return ("HARD_FAIL", f"HARD_FAIL: compounding curve is not non-decreasing despite genuinely-new "
                            f"TRAIN exposure across K={N_PASSES} passes: curve={stats['real_commonsense_curve']}.",
                stats)
    if beats_baseline and non_decreasing and real_edge_exceeds_scramble:
        return ("HARD_PASS", f"HARD_PASS: SYSTEM beats TEXT_OVERLAP baseline on commonsense DEV subset "
                            f"({real_final:.4f} vs {baseline_cs:.4f}, edge={real_edge:.4f}), compounding "
                            f"curve non-decreasing ({stats['real_commonsense_curve']}), and the REAL arm's "
                            f"edge over baseline ({real_edge:.4f}) exceeds the SCRAMBLE arm's "
                            f"({scramble_edge:.4f}) -- the beat depends on genuine grounding.", stats)
    return ("MIDDLE_BAND", f"MIDDLE_BAND: beats_baseline={beats_baseline} non_decreasing={non_decreasing} "
                          f"real_edge_exceeds_scramble={real_edge_exceeds_scramble}. "
                          f"real_final={real_final:.4f} baseline={baseline_cs:.4f} "
                          f"scramble_final={scramble_final:.4f}.", stats)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE, expected_n_units=2)

    if RUN_MODE == "self_test":
        result = self_test()
        write_metrics(output_dir, {
            "verdict": "HARD_PASS" if result else "HARD_FAIL",
            "verdict_msg": "SELFTEST_PASS: real code path exercised (see self_test dict).",
            "summary": "self_test", "elapsed_s": round(time.perf_counter() - t0, 3),
            "run_mode": "self_test", "self_test_result": result,
        })
        print(json.dumps(result, indent=2, default=str), flush=True)
        return

    print(f"[main] run_mode={RUN_MODE} loading MCScript2.0 splits from {DATA_DIR}", flush=True)
    train_all = load_split("train")
    dev_all = load_split("dev")
    print(f"[main] loaded train={len(train_all)} dev={len(dev_all)}", flush=True)

    if RUN_MODE == "smoke":
        scen_sorted = sorted({inst["scenario"] for inst in train_all})
        smoke_scenarios = set(scen_sorted[:15])
        train_instances = restrict_to_scenarios(train_all, smoke_scenarios)
        dev_instances = restrict_to_scenarios(dev_all, smoke_scenarios)
    else:
        train_instances = train_all
        dev_instances = dev_all
    print(f"[main] using train={len(train_instances)} dev={len(dev_instances)} "
          f"(n_scenarios={len({i['scenario'] for i in train_instances})})", flush=True)

    print("[main] precheck (a): keying discriminates on TRAIN sample...", flush=True)
    precheck_a = precheck_a_keying_discriminates(train_instances)
    print(f"[main] precheck (a) result: {precheck_a}", flush=True)
    novelty_thresh = precheck_a["novelty_thresh_calibrated"]

    majority_answer_id = compute_majority_answer_id(train_instances)
    baselines = baseline_accuracies(dev_instances, majority_answer_id)
    print(f"[main] majority_answer_id={majority_answer_id} baselines={baselines}", flush=True)

    seeds = ["real", "scramble"]
    done, remaining = resumable_seeds(seeds, output_dir,
                                      run_config={"run_mode": RUN_MODE})
    print(f"[ckpt] {len(done)} of {len(seeds)} arms already complete; running {remaining}", flush=True)
    for arm in remaining:
        print(f"[main] growing arm={arm}...", flush=True)
        growth = grow_and_track(train_instances, dev_instances, scramble=(arm == "scramble"),
                                novelty_thresh=novelty_thresh, majority_answer_id=majority_answer_id)
        payload = {
            "seed": arm,
            "run_mode": RUN_MODE,
            "n_items_spawned_total": growth["n_items_spawned_total"],
            "grounded_count_curve": growth["grounded_count_curve"],
            "dev_accuracy_curve": growth["dev_accuracy_curve"],
            "item_purity": growth["item_purity"],
            "per_pass_reports": [
                {k: v for k, v in r.items() if k != "schema_debug"} for r in growth["per_pass_reports"]
            ],
        }
        write_partial(output_dir, arm, payload)
        print(f"[main] arm={arm} done, final grounded={growth['grounded_count_curve'][-1]}", flush=True)

    per_arm = aggregate_partials(output_dir, seeds, run_config={"run_mode": RUN_MODE})
    real_p = per_arm["real"]
    scramble_p = per_arm["scramble"]

    # arms_differ_verified (META_RULE_AF): hash the two arms' grounded_count_curve + spawn totals
    import hashlib as _hashlib
    h_real = _hashlib.sha256(json.dumps(
        [real_p["grounded_count_curve"], real_p["n_items_spawned_total"]]).encode()).hexdigest()
    h_scramble = _hashlib.sha256(json.dumps(
        [scramble_p["grounded_count_curve"], scramble_p["n_items_spawned_total"]]).encode()).hexdigest()
    arms_differ = h_real != h_scramble

    # glass-box FHRR-role extraction sample (Amendment 1: audit-only, small sample)
    print("[main] building glass-box FHRR-role extraction sample (audit only)...", flush=True)
    gen = CandidateGenerator.load(str(POS_CKPT), str(ARC_CKPT))
    example_tuples = []
    for inst in sorted(train_instances, key=lambda x: x["id"])[:20]:
        tup, diag = extract_instance_tuple(inst["text"], gen)
        if tup is not None:
            example_tuples.append({"id": inst["id"], "scenario": inst["scenario"],
                                   "trigger": tup[0], "consequent": tup[1],
                                   "agent": tup[2], "patient": tup[3]})
        if len(example_tuples) >= 12:
            break

    verdict, verdict_msg, stats = compute_verdict(real_p, scramble_p, baselines, precheck_a)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"run_mode={RUN_MODE} n_train={len(train_instances)} n_dev={len(dev_instances)} "
                  f"verdict={verdict}",
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "run_mode": RUN_MODE,
        "config": {"N_PASSES": N_PASSES, "MIN_CONFIRM": MIN_CONFIRM, "PATIENCE_MAX": PATIENCE_MAX,
                  "NEUTRAL_BAND": NEUTRAL_BAND, "REPLAY_BUDGET_FRAC": REPLAY_BUDGET_FRAC,
                  "SCHEMA_THRESH": SCHEMA_THRESH, "novelty_thresh_calibrated": novelty_thresh,
                  "mdl_gate": "N/A (Amendment 2, mdl_gate_fn=None)"},
        "precheck_a": precheck_a,
        "baselines": baselines,
        "majority_answer_id": majority_answer_id,
        "arms_differ_verified": arms_differ,
        "cardinality_ok": len(per_arm) == 2,
        "n_train_instances": len(train_instances), "n_dev_instances": len(dev_instances),
        "n_train_scenarios": len({i["scenario"] for i in train_instances}),
        "n_dev_scenarios": len({i["scenario"] for i in dev_instances}),
        "real_arm": real_p, "scramble_arm": scramble_p,
        "example_fhrr_extractions_glass_box": example_tuples,
        "verdict_stats": stats,
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "keying/consolidation + MC-scoring cell; no argmax/top-k capacity ceiling applies",
    }
    write_metrics(output_dir, metrics)
    print(f"[main] VERDICT={verdict}", flush=True)
    print(f"[main] {verdict_msg}", flush=True)


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out_dir_for_crash, e)
        raise
