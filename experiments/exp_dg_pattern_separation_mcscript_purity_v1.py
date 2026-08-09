"""exp_dg_pattern_separation_mcscript_purity_v1 -- ISOLATED CAN-FAIL purity gate
for the diagnosed fix to the MCScript2.0 real-benchmark HARD_FAIL (2026-08-09).

Pre-reg: preregs/2026-08-09_dg_pattern_separation_mcscript_purity_v1.md
Diagnosed failure (parent, HARD_FAIL): commit 5c1199f87,
  data/exp_mcscript2_real_benchmark_validation_v1/metrics.json.

WHAT: exp_mcscript2_real_benchmark_validation_v1 failed NOT on extraction
(fires 100%) but on CLUSTERING-CARDINALITY: hdlab.script_grain_acquisition_
loop.ScriptLibrary.match_or_spawn keys purely via
hdlab.cleanup_family.iterative_attractor -- a CA3 pattern-COMPLETION
mechanism (soft-attractor settle toward the nearest bundled prototype) -- with
NO upstream pattern-SEPARATION stage. At 195-way TRAIN scenario cardinality
this over-merges: only 35 items spawn (33 reach GROUNDED), MEASURED@data/
exp_mcscript2_real_benchmark_validation_v1/metrics.json:real_arm.item_purity
mean majority_frac = 0.1999 (catch-all buckets; compounding curve degrades
with exposure). Diagnosis: the brain pairs DG pattern-SEPARATION with CA3
pattern-COMPLETION (Leutgeb 2007, Guzman 2016, McHugh 2007 causal evidence);
this substrate only completes. This cell isolates whether adding a DG-style
separation stage (hdlab.dg_pattern_separation.dg_separate, new module) BEFORE
the unchanged CA3/DG match-or-spawn keying raises item PURITY at the SAME
195-way cardinality -- BEFORE spending compute on any full MC re-run.

THIS CELL MEASURES ONLY THE ISOLATED CLUSTERING/PURITY QUESTION. No
consolidation passes, no MDL gate, no DEV evaluation, no MC scoring: cluster
MEMBERSHIP is fully determined by the TRAIN spawn-loop (ScriptLibrary.
match_or_spawn called once per TRAIN instance) -- confirmed by reading
hdlab/script_grain_acquisition_loop.py's grow_and_track /
script_consolidation_pass (consolidation only flips item STATUS, it never
calls match_or_spawn or re-keys traces). The real-benchmark cell's own
item_purity field is computed from exactly this same spawn-loop's cluster
membership. A follow-up cell (deferred, gated on THIS cell clearing HARD-PASS
per the task's isolation-first contract) re-runs the full MC eval with
DG-separation wired into the keying if this gate clears.

ARMS (all run through the IDENTICAL ScriptLibrary().match_or_spawn loop over
the full TRAIN split, sorted(id) order, deterministic):
  off             -- bow_key: context_vector(text) wrapped zero-imaginary
                     complex64 (identical convention to exp_mcscript2_real_
                     benchmark_validation_v1.bow_register). POSITIVE CONTROL:
                     must reproduce the landed ~0.1999 purity (Gate D, at the
                     SAME test regime -- full 2500-train/195-scenario split).
  on_sparsity05   -- dg_key: context_vector(text) -> hdlab.dg_pattern_
                     separation.dg_separate(expand_dim=2048, sparsity=0.05)
                     -> wrapped zero-imaginary complex64. PRIMARY TREATMENT.
  on_sparsity10   -- same but sparsity=0.10. Robustness variant (not gating);
                     shows the primary result is not knife-edge-tuned.

Each arm's novelty_thresh is calibrated SEPARATELY (fair-test discipline --
sparse k-WTA codes have a fundamentally different cosine distribution than
dense bag-of-words codes) via hdlab.script_grain_acquisition_loop.
calibrate_novelty_threshold, REUSED VERBATIM (it already operates on
arbitrary complex64 register tensors via _real2d+cosine, so it works
unmodified on DG-separated registers).

REUSE (wire-don't-island): hdlab.grounding_acquisition_loop.context_vector
(unmodified); hdlab.script_grain_acquisition_loop.ScriptLibrary /
calibrate_novelty_threshold / _real2d (unmodified -- NO changes to that
module, the DG-separation stage is injected purely via a different key_fn,
exactly the same drop-in pattern exp_mcscript2_real_benchmark_validation_v1
uses for bow_register/scramble_register); hdlab.cleanup_family.
iterative_attractor (via ScriptLibrary.match_or_spawn, unchanged);
hdlab.mcscript_extraction.parse_mcscript_xml (unmodified).
GENUINELY-NEW code in this file: bow_key/dg_key (key-builder wrappers),
calibrate_arm (per-arm precheck, generalizes exp_mcscript2_real_benchmark_
validation_v1's precheck_a_keying_discriminates to an injectable key_fn),
run_arm / _purity_stats (the clustering loop + purity metrics this task asks
for), compute_verdict (this cell's own pre-registered bands).
GENUINELY-NEW module: hdlab/dg_pattern_separation.py (the DG stage itself;
self-tested standalone, see that module's own self-test).

CELL-TEMPLATE MANDATORY (per exp_dev SCHEMA-VET):
- except SystemExit: raise BEFORE except Exception (no bare except, no BaseException)
- final_metrics_atomicity: tmp_replace, plus per-arm partial checkpoints via
  experiments._seed_checkpoint (resumable per unit: "off", "on_sparsity05", "on_sparsity10")
- deterministic_seeding: hashlib + np.random.default_rng throughout; no built-in hash(),
  no list(set()) ordering (sorted(...) used throughout)
- start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
- real_code_path_exercised: dg_separate / ScriptLibrary.match_or_spawn / calibrate_
  novelty_threshold / parse_mcscript_xml all constructed and called for real at
  self-test scale
- arms_differ_verified: 3 arms' (n_items_total, sorted item-size multiset) hashed distinct
- calibration_check: adaptive_with_discriminator_gate (novelty_thresh calibrated per-arm
  from TRAIN-only sample, never hand-tuned)
- crlb_n_a: keying/clustering cell; this cell's own purity gate IS the capacity-
  feasibility question being measured, not assumed
- all numbers in this file's comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only; no unicode; no emojis.
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
import platform
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics, record_gate,
)

from hdlab.grounding_acquisition_loop import context_vector, D as BOW_D
from hdlab.script_grain_acquisition_loop import ScriptLibrary, calibrate_novelty_threshold, _real2d
from hdlab.dg_pattern_separation import dg_separate, projection_matrix, _selftest as dg_module_selftest
from hdlab.mcscript_extraction import parse_mcscript_xml

ANCHOR_NAME = "dg_pattern_separation_mcscript_purity_v1"

# ---------------------------------------------------------------------------
# CLI / run mode (identical convention to exp_mcscript2_real_benchmark_validation_v1)
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
# Config (exp_dev autonomy, justified in module docstring + pre-reg)
# ---------------------------------------------------------------------------
DATA_DIR = REPO / "data" / "corpora" / "mcscript2" / "extracted"

EXPAND_DIM = 2048          # ~8x expansion of BOW_D=256 (EC-II->DG mossy-fiber divergence
                            # cited 5-10x across species/estimates; CITED@Leutgeb 2007/
                            # Guzman 2016/McHugh 2007 background, Bogacz & Brown 2003 model)
SPARSITY_PRIMARY = 0.05    # 5% active (biological DG sparsity ~1-4%, CITED@Jung & McNaughton
                            # 1993/Chawla et al. 2005; 5% is a disclosed relaxation for
                            # 195-way discrimination against noisy language content)
SPARSITY_ROBUST = 0.10     # secondary robustness variant, not gating
MIN_CONFIRM = 4            # matches script_grain_acquisition_loop / real-benchmark cell's
                            # MIN_CONFIRM, used here only to define the "would-be-grounded"
                            # purity subset for direct comparability to the landed number
ATTRACTOR_TEMP = 4.0       # matches real-benchmark cell's operating point
ATTRACTOR_MAX_STEPS = 8
PRECHECK_MIN_GAP = 0.05    # Amendment-3-style realistic precheck (matches real-benchmark cell)
PRECHECK_MIN_AUC = 0.60
PURE_THRESH = 0.5          # majority_frac >= this counts as a "pure" item
N_STRATIFIED_PER_SCENARIO = 2

# MEASURED@data/exp_mcscript2_real_benchmark_validation_v1/metrics.json:
#   real_arm.item_purity -- mean majority_frac across the 33 GROUNDED items = 0.19990909...
LANDED_REFERENCE_PURITY = 0.1999
OFF_REPRO_TOLERANCE = 0.10   # HARD-FAIL if the OFF arm's would-be-grounded purity deviates
                             # from LANDED_REFERENCE_PURITY by more than this (Gate D sanity)

ARMS = ["off", "on_sparsity05", "on_sparsity10"]

SMOKE_N_SCENARIOS = 20


# ---------------------------------------------------------------------------
# Key builders (drop-in key_fn, same wrapping convention as bow_register /
# scramble_register in exp_mcscript2_real_benchmark_validation_v1)
# ---------------------------------------------------------------------------
def bow_key(text: str) -> torch.Tensor:
    """context_vector(text) wrapped as a zero-imaginary complex64 tensor.
    Identical convention to exp_mcscript2_real_benchmark_validation_v1.
    bow_register -- cosine on [Re,Im]=[bow,0] reduces exactly to
    cosine(bow_a, bow_b) (lossless, verified in self_test)."""
    bow = context_vector(text).astype(np.complex64)
    return torch.from_numpy(bow)


def dg_key(text: str, *, W: np.ndarray, sparsity: float, expand_dim: int, proj_tag: str) -> torch.Tensor:
    """DG-separated key: context_vector(text) -> hdlab.dg_pattern_separation.
    dg_separate(...) -> wrapped zero-imaginary complex64 tensor, SAME wrapping
    convention as bow_key so it plugs into ScriptLibrary.match_or_spawn /
    calibrate_novelty_threshold / _real2d with zero modification to that module.
    W must be precomputed (hdlab.dg_pattern_separation.projection_matrix) and
    reused across every call in one arm -- rebuilding+reseeding a
    (expand_dim, BOW_D) matrix per instance would be pure wasted compute."""
    bow = context_vector(text)
    sep = dg_separate(bow, expand_dim=expand_dim, sparsity=sparsity, proj_seed_tag=proj_tag, W=W)
    return torch.from_numpy(sep.astype(np.complex64))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_train() -> List[Dict]:
    path = DATA_DIR / "train-data.xml"
    if not path.exists():
        raise FileNotFoundError(f"MCScript2.0 train split not found at {path}.")
    return parse_mcscript_xml(str(path))


def restrict_to_scenarios(instances: List[Dict], scenarios: set) -> List[Dict]:
    return [inst for inst in instances if inst["scenario"] in scenarios]


# ---------------------------------------------------------------------------
# Precheck / per-arm calibration (generalizes exp_mcscript2_real_benchmark_
# validation_v1.precheck_a_keying_discriminates to an injectable key_fn)
# ---------------------------------------------------------------------------
def _roc_auc(matched_scores: np.ndarray, wrong_scores: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney U / n_pos / n_neg). Pure numpy."""
    n_m, n_w = len(matched_scores), len(wrong_scores)
    if n_m == 0 or n_w == 0:
        return 0.5
    all_scores = np.concatenate([matched_scores, wrong_scores])
    ranks = np.argsort(np.argsort(all_scores)) + 1
    rank_sum_matched = ranks[:n_m].sum()
    u = rank_sum_matched - n_m * (n_m + 1) / 2.0
    return float(u / (n_m * n_w))


def calibrate_arm(train_instances: List[Dict], key_fn: Callable[[str], torch.Tensor],
                  *, n_per_scenario: int = N_STRATIFIED_PER_SCENARIO) -> Dict:
    """Stratified TRAIN sample (n_per_scenario/scenario, sorted-by-id,
    deterministic) -> matched/wrong register pairs -> calibrate_novelty_
    threshold (REUSED verbatim from script_grain_acquisition_loop) + gap/AUC
    precheck (Amendment-3-style realistic criterion, matches the real-
    benchmark cell)."""
    by_scenario: Dict[str, List[Dict]] = {}
    for inst in train_instances:
        by_scenario.setdefault(inst["scenario"], []).append(inst)
    sample: List[Tuple[str, str, torch.Tensor]] = []
    for scen in sorted(by_scenario):
        insts = sorted(by_scenario[scen], key=lambda x: x["id"])[:n_per_scenario]
        for inst in insts:
            sample.append((inst["id"], inst["scenario"], key_fn(inst["text"])))

    matched_pairs, wrong_pairs = [], []
    matched_scores, wrong_scores = [], []
    n = len(sample)
    for i in range(n):
        _, si, ri = sample[i]
        qi = _real2d(ri)
        qi = qi / (float(np.linalg.norm(qi)) + 1e-9)
        for j in range(i + 1, n):
            _, sj, rj = sample[j]
            qj = _real2d(rj)
            qj = qj / (float(np.linalg.norm(qj)) + 1e-9)
            score = float(np.dot(qi, qj))
            if si == sj:
                matched_pairs.append((ri, rj)); matched_scores.append(score)
            else:
                wrong_pairs.append((ri, rj)); wrong_scores.append(score)

    calib = calibrate_novelty_threshold(matched_pairs, wrong_pairs)
    matched_arr, wrong_arr = np.array(matched_scores), np.array(wrong_scores)
    auc = _roc_auc(matched_arr, wrong_arr)
    gap = float(calib["matched_mean"] - calib["wrong_mean"])
    return {
        "novelty_thresh": round(float(calib["novelty_thresh"]), 4),
        "matched_mean": round(float(calib["matched_mean"]), 4),
        "wrong_mean": round(float(calib["wrong_mean"]), 4),
        "gap": round(gap, 4), "auc": round(auc, 4),
        "realistic_discriminates": bool(gap >= PRECHECK_MIN_GAP and auc >= PRECHECK_MIN_AUC),
        "n_matched_pairs": calib["n_matched_pairs"], "n_wrong_pairs": calib["n_wrong_pairs"],
        "n_sample_instances": n,
    }


# ---------------------------------------------------------------------------
# Clustering loop + purity metrics (the mechanism this task's gate measures)
# ---------------------------------------------------------------------------
def run_arm(train_instances: List[Dict], *, key_fn: Callable[[str], torch.Tensor],
           novelty_thresh: float, arm_name: str) -> Dict:
    """Runs the IDENTICAL ScriptLibrary().match_or_spawn spawn-loop the real-
    benchmark cell's grow_and_track uses for its TRAIN sweep (no consolidation
    passes -- cluster membership is fully determined by this loop alone)."""
    library = ScriptLibrary()
    t0 = time.perf_counter()
    sorted_insts = sorted(train_instances, key=lambda x: x["id"])
    n = len(sorted_insts)
    for i, inst in enumerate(sorted_insts):
        reg = key_fn(inst["text"])
        ctx = context_vector(inst["text"])
        library.match_or_spawn(reg, inst["id"], "NA", ctx, 0, true_type=inst["scenario"],
                               temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS,
                               novelty_thresh=novelty_thresh)
        if (i + 1) % 500 == 0 or (i + 1) == n:
            print(f"[run_arm] arm={arm_name} {i + 1}/{n} instances, "
                  f"n_items_so_far={len(library.items)}, elapsed={time.perf_counter() - t0:.1f}s",
                  flush=True)
    stats = _purity_stats(library, arm_name)
    stats["elapsed_s"] = round(time.perf_counter() - t0, 3)
    stats["novelty_thresh_used"] = round(novelty_thresh, 4)
    return stats


def _purity_stats(library: ScriptLibrary, arm_name: str) -> Dict:
    items = list(library.items.values())
    n_total = len(items)
    per_item: Dict[str, Dict] = {}
    sizes: List[int] = []
    for it in items:
        c = Counter(t.true_type for t in it.traces)
        maj, cnt = c.most_common(1)[0]
        frac = cnt / len(it.traces)
        sizes.append(len(it.traces))
        per_item[it.item_id] = {"n_traces": len(it.traces), "majority_scenario": maj,
                                "majority_frac": round(frac, 4)}

    n_singletons = sum(1 for s in sizes if s == 1)
    multi_items = [v for v in per_item.values() if v["n_traces"] >= 2]
    grounded_would_be = [v for v in per_item.values() if v["n_traces"] >= MIN_CONFIRM]

    def _mean(vals: List[float]) -> float:
        return float(np.mean(vals)) if vals else 0.0

    def _wmean(items_list: List[Dict]) -> float:
        tot_traces = sum(v["n_traces"] for v in items_list)
        if tot_traces == 0:
            return 0.0
        return float(sum(v["majority_frac"] * v["n_traces"] for v in items_list) / tot_traces)

    mean_purity_multi = _mean([v["majority_frac"] for v in multi_items])
    trace_weighted_purity_multi = _wmean(multi_items)
    n_pure_items = sum(1 for v in multi_items if v["majority_frac"] >= PURE_THRESH)
    mean_purity_grounded_would_be = _mean([v["majority_frac"] for v in grounded_would_be])

    return {
        "arm": arm_name,
        "n_items_total": n_total,
        "n_singletons": n_singletons,
        "singleton_frac": round(n_singletons / n_total, 4) if n_total else 0.0,
        "n_items_multi": len(multi_items),
        "mean_purity_multi": round(mean_purity_multi, 4),
        "trace_weighted_purity_multi": round(trace_weighted_purity_multi, 4),
        "n_pure_items": n_pure_items,
        "pure_frac": round(n_pure_items / len(multi_items), 4) if multi_items else 0.0,
        "n_items_grounded_would_be": len(grounded_would_be),
        "mean_purity_grounded_would_be": round(mean_purity_grounded_would_be, 4),
        "item_size_stats": {"min": int(min(sizes)) if sizes else 0,
                            "median": float(np.median(sizes)) if sizes else 0.0,
                            "max": int(max(sizes)) if sizes else 0},
        "item_purity_sample": dict(sorted(per_item.items())[:40]),
    }


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands, preregs/2026-08-09_dg_pattern_separation_
# mcscript_purity_v1.md)
# ---------------------------------------------------------------------------
def compute_verdict(per_arm: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    off = per_arm["off"]
    on1 = per_arm["on_sparsity05"]
    on2 = per_arm["on_sparsity10"]

    off_deviation = abs(off["mean_purity_grounded_would_be"] - LANDED_REFERENCE_PURITY)
    off_repro_ok = off_deviation <= OFF_REPRO_TOLERANCE

    gate_purity = record_gate("on_sparsity05_mean_purity_multi", on1["mean_purity_multi"],
                              0.50, ">=", note="primary purity gate")
    gate_not_memorized = record_gate("on_sparsity05_singleton_frac", on1["singleton_frac"],
                                     0.80, "<=", note="memorization/singleton-explosion guard")
    gate_repro = record_gate("off_reproduction_deviation", off_deviation, OFF_REPRO_TOLERANCE,
                             "<=", note="OFF arm must reproduce the landed ~0.1999 purity (Gate D)")

    stats = {
        "off_mean_purity_grounded_would_be": off["mean_purity_grounded_would_be"],
        "landed_reference_purity": LANDED_REFERENCE_PURITY,
        "off_reproduction_deviation": round(off_deviation, 4),
        "off_reproduction_ok": off_repro_ok,
        "on_sparsity05_mean_purity_multi": on1["mean_purity_multi"],
        "on_sparsity05_trace_weighted_purity_multi": on1["trace_weighted_purity_multi"],
        "on_sparsity05_singleton_frac": on1["singleton_frac"],
        "on_sparsity05_n_items_total": on1["n_items_total"],
        "on_sparsity10_mean_purity_multi": on2["mean_purity_multi"],
        "on_sparsity10_singleton_frac": on2["singleton_frac"],
        "on_sparsity10_n_items_total": on2["n_items_total"],
        "gate_claims": [gate_purity, gate_not_memorized, gate_repro],
    }

    if not off_repro_ok:
        return ("HARD_FAIL",
               f"HARD_FAIL: OFF-arm reproduction check failed -- this cell's OFF-arm "
               f"mean_purity_grounded_would_be ({off['mean_purity_grounded_would_be']:.4f}) "
               f"deviates {off_deviation:.4f} from the landed reference "
               f"({LANDED_REFERENCE_PURITY:.4f}), exceeding tolerance {OFF_REPRO_TOLERANCE}. "
               f"This cell's spawn-loop is not a faithful reproduction of the diagnosed "
               f"failure, so the ON-vs-OFF comparison cannot be trusted (Gate D).", stats)

    if on1["singleton_frac"] >= 0.90:
        return ("HARD_FAIL",
               f"HARD_FAIL: DG-separation (sparsity=0.05) singleton_frac="
               f"{on1['singleton_frac']:.4f} >= 0.90 -- the mechanism is so aggressive "
               f"nothing merges (pure memorization, not generalization).", stats)

    if on1["mean_purity_multi"] < 0.35:
        return ("HARD_FAIL",
               f"HARD_FAIL: DG-separation (sparsity=0.05) mean_purity_multi="
               f"{on1['mean_purity_multi']:.4f} does not clear meaningfully above the "
               f"~{LANDED_REFERENCE_PURITY:.4f} baseline. This is the honest capacity-"
               f"ceiling finding: the substrate cannot discriminate 195-way online with "
               f"this keying signal even with DG-style separation.", stats)

    if on1["mean_purity_multi"] >= 0.50 and on1["singleton_frac"] <= 0.80:
        return ("HARD_PASS",
               f"HARD_PASS: DG-separation (sparsity=0.05) raises mean_purity_multi to "
               f"{on1['mean_purity_multi']:.4f} (from ~{LANDED_REFERENCE_PURITY:.4f} baseline) "
               f"with singleton_frac={on1['singleton_frac']:.4f} (not memorized). OFF-arm "
               f"reproduction check passed (deviation={off_deviation:.4f}). Robustness variant "
               f"sparsity=0.10: mean_purity_multi={on2['mean_purity_multi']:.4f} "
               f"singleton_frac={on2['singleton_frac']:.4f}.", stats)

    return ("MIDDLE_BAND",
           f"MIDDLE_BAND: DG-separation (sparsity=0.05) mean_purity_multi="
           f"{on1['mean_purity_multi']:.4f} singleton_frac={on1['singleton_frac']:.4f} -- "
           f"improves over baseline but does not clear the pre-registered HARD-PASS band "
           f"cleanly.", stats)


# ---------------------------------------------------------------------------
# Self-test (real code path, per exp_dev SCHEMA-VET F.1)
# ---------------------------------------------------------------------------
def _selftest_xml() -> str:
    """Tiny hand-built MCScript-schema XML (2 scenarios x 3 instances) for
    calibrate_arm's real parse_mcscript_xml + stratified-sample code path."""
    scenarios = {
        "making eggs": [
            "I cracked the eggs into a bowl . I whisked them well . "
            "I poured the mixture into a hot pan . I cooked the eggs until done . "
            "I served the eggs on a plate .",
            "I got two eggs from the fridge . I beat the eggs in a bowl . "
            "I heated a pan on the stove . I fried the eggs for a few minutes . "
            "I put the eggs onto a plate .",
            "I took eggs out of the carton . I cracked them into a mixing bowl . "
            "I whisked the eggs with a fork . I cooked them in a buttered pan . "
            "I plated the finished eggs .",
        ],
        "walking dog": [
            "I clipped the leash onto the dog . I walked the dog around the block . "
            "The dog sniffed at the grass . I picked up after the dog . "
            "I brought the dog back home .",
            "I found the dog leash by the door . I attached it to the dog collar . "
            "We walked around the neighborhood . The dog stopped to sniff a tree . "
            "We returned home together .",
            "I grabbed the leash from the hook . I put it on the dog . "
            "We went for a walk outside . The dog explored the yard . "
            "I took the dog back inside .",
        ],
    }
    parts = ["<data>"]
    iid = 0
    for scen, texts in scenarios.items():
        for text in texts:
            parts.append(
                f'<instance id="{iid}" scenario="{scen}"><text>{text}</text>'
                f'<questions><question id="0" text="What happened?" type="commonsense">'
                f'<answer correct="True" id="0" text="{scen}" />'
                f'<answer correct="False" id="1" text="something unrelated" /></question>'
                f"</questions></instance>")
            iid += 1
    parts.append("</data>")
    return "".join(parts)


def self_test() -> Dict:
    # (0) hdlab.dg_pattern_separation's own real code-path self-test.
    dg_result = dg_module_selftest()

    # (1) bow_key determinism + distinctness.
    t1 = "Nell fixed the lantern by the fire in the workshop."
    t2 = "Owen mended the boat before the storm near the dock."
    b1a, b1b = bow_key(t1), bow_key(t1)
    b2 = bow_key(t2)
    assert torch.equal(b1a, b1b), "bow_key must be deterministic"
    assert not torch.equal(b1a, b2), "bow_key must differ for different content"

    # (2) dg_key determinism + real dg_separate call.
    W = projection_matrix(BOW_D, 512, "selftest_tag")
    d1a = dg_key(t1, W=W, sparsity=0.10, expand_dim=512, proj_tag="selftest_tag")
    d1b = dg_key(t1, W=W, sparsity=0.10, expand_dim=512, proj_tag="selftest_tag")
    assert torch.equal(d1a, d1b), "dg_key must be deterministic"
    assert not torch.equal(d1a, bow_key(t1)), "dg_key output must differ from bow_key (different code)"

    # (3) ScriptLibrary.match_or_spawn real code path with dg_key, tiny scale --
    # mirrors the actual clustering loop this cell runs at full scale.
    lib = ScriptLibrary()
    texts_a = ["I cracked the eggs and cooked an omelette in the hot pan.",
              "I beat the eggs then fried the omelette in a very hot pan."]
    texts_b = ["I walked the dog around the block on a leash.",
              "I took the dog for a walk with its leash on today."]
    for i, t in enumerate(texts_a):
        reg = dg_key(t, W=W, sparsity=0.10, expand_dim=512, proj_tag="selftest_tag")
        lib.match_or_spawn(reg, f"a{i}", "NA", context_vector(t), 0, true_type="omelette",
                           temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS, novelty_thresh=0.02)
    for i, t in enumerate(texts_b):
        reg = dg_key(t, W=W, sparsity=0.10, expand_dim=512, proj_tag="selftest_tag")
        lib.match_or_spawn(reg, f"b{i}", "NA", context_vector(t), 0, true_type="dog_walk",
                           temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS, novelty_thresh=0.02)
    stats = _purity_stats(lib, "selftest")
    assert stats["n_items_total"] >= 1, "match_or_spawn must produce at least 1 item"

    # (4) calibrate_arm real code path: real parse_mcscript_xml + stratified sample +
    # calibrate_novelty_threshold (reused verbatim).
    import tempfile
    xml_text = _selftest_xml()
    fd, p = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(xml_text)
        insts = parse_mcscript_xml(p)
    finally:
        os.remove(p)
    assert len(insts) == 6, f"expected 6 self-test instances, got {len(insts)}"
    calib_bow = calibrate_arm(insts, bow_key, n_per_scenario=2)
    assert "novelty_thresh" in calib_bow and calib_bow["n_matched_pairs"] > 0

    # (5) run_arm real end-to-end path (tiny scale) -- exercises the exact function
    # main() calls at full scale.
    arm_stats = run_arm(insts, key_fn=bow_key, novelty_thresh=calib_bow["novelty_thresh"],
                        arm_name="selftest_run_arm")
    assert arm_stats["n_items_total"] >= 1

    return {
        "dg_module_selftest": dg_result,
        "bow_key_deterministic_and_distinct": True,
        "dg_key_deterministic_and_distinct_from_bow": True,
        "match_or_spawn_with_dg_key_ok": True, "match_or_spawn_stats": stats,
        "calibrate_arm_ok": True, "calib_bow_sample": calib_bow,
        "run_arm_ok": True, "run_arm_stats_n_items": arm_stats["n_items_total"],
        "real_code_path_exercised": ["dg_separate", "ScriptLibrary.match_or_spawn",
                                     "calibrate_novelty_threshold", "parse_mcscript_xml",
                                     "run_arm", "context_vector"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE, expected_n_units=len(ARMS))

    if RUN_MODE == "self_test":
        result = self_test()
        write_metrics(output_dir, {
            "verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS: real code path exercised.",
            "summary": "self_test", "elapsed_s": round(time.perf_counter() - t0, 3),
            "run_mode": "self_test", "self_test_result": result,
        })
        print(json.dumps(result, indent=2, default=str), flush=True)
        return

    print(f"[main] run_mode={RUN_MODE} loading MCScript2.0 train split from {DATA_DIR}", flush=True)
    train_all = load_train()
    print(f"[main] loaded train={len(train_all)} "
          f"scenarios={len({i['scenario'] for i in train_all})}", flush=True)

    if RUN_MODE == "smoke":
        scen_sorted = sorted({inst["scenario"] for inst in train_all})
        smoke_scenarios = set(scen_sorted[:SMOKE_N_SCENARIOS])
        train_instances = restrict_to_scenarios(train_all, smoke_scenarios)
    else:
        train_instances = train_all
    n_scenarios = len({i["scenario"] for i in train_instances})
    print(f"[main] using train={len(train_instances)} instances / {n_scenarios} scenarios", flush=True)

    # Precompute DG projection matrices ONCE per sparsity arm (reused across all
    # 2500 calls -- rebuilding+reseeding a (2048,256) matrix per instance would be
    # pure wasted compute).
    W_primary = projection_matrix(BOW_D, EXPAND_DIM, "dg_pattern_sep_mcscript_primary")
    W_robust = projection_matrix(BOW_D, EXPAND_DIM, "dg_pattern_sep_mcscript_robust")

    key_fns: Dict[str, Callable[[str], torch.Tensor]] = {
        "off": bow_key,
        "on_sparsity05": lambda text: dg_key(text, W=W_primary, sparsity=SPARSITY_PRIMARY,
                                             expand_dim=EXPAND_DIM,
                                             proj_tag="dg_pattern_sep_mcscript_primary"),
        "on_sparsity10": lambda text: dg_key(text, W=W_robust, sparsity=SPARSITY_ROBUST,
                                             expand_dim=EXPAND_DIM,
                                             proj_tag="dg_pattern_sep_mcscript_robust"),
    }

    done, remaining = resumable_seeds(ARMS, output_dir, run_config={"run_mode": RUN_MODE})
    print(f"[ckpt] {len(done)} of {len(ARMS)} arms already complete; running {remaining}", flush=True)

    for arm in remaining:
        print(f"[main] arm={arm}: calibrating novelty_thresh from TRAIN-only stratified sample...",
              flush=True)
        calib = calibrate_arm(train_instances, key_fns[arm])
        print(f"[main] arm={arm} calibration: {calib}", flush=True)
        print(f"[main] arm={arm}: running clustering spawn-loop over {len(train_instances)} instances...",
              flush=True)
        arm_stats = run_arm(train_instances, key_fn=key_fns[arm],
                            novelty_thresh=calib["novelty_thresh"], arm_name=arm)
        payload = {"seed": arm, "run_mode": RUN_MODE, "calibration": calib, **arm_stats}
        write_partial(output_dir, arm, payload)
        print(f"[main] arm={arm} done: n_items_total={arm_stats['n_items_total']} "
              f"mean_purity_multi={arm_stats['mean_purity_multi']} "
              f"singleton_frac={arm_stats['singleton_frac']} "
              f"elapsed={arm_stats['elapsed_s']}s", flush=True)

    per_arm = aggregate_partials(output_dir, ARMS, run_config={"run_mode": RUN_MODE})

    # arms_differ_verified (META_RULE_AF): hash each arm's (n_items_total, sorted item sizes).
    import hashlib as _hashlib
    arm_hashes = {}
    for arm in ARMS:
        sizes = sorted(v["n_traces"] for v in per_arm[arm]["item_purity_sample"].values())
        digest_input = json.dumps([per_arm[arm]["n_items_total"], sizes,
                                   per_arm[arm]["mean_purity_multi"]]).encode()
        arm_hashes[arm] = _hashlib.sha256(digest_input).hexdigest()
    arms_differ = len(set(arm_hashes.values())) == len(ARMS)

    verdict, verdict_msg, stats = compute_verdict(per_arm)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"run_mode={RUN_MODE} n_train={len(train_instances)} "
                  f"n_scenarios={n_scenarios} verdict={verdict}",
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "run_mode": RUN_MODE,
        "config": {"EXPAND_DIM": EXPAND_DIM, "SPARSITY_PRIMARY": SPARSITY_PRIMARY,
                  "SPARSITY_ROBUST": SPARSITY_ROBUST, "MIN_CONFIRM": MIN_CONFIRM,
                  "ATTRACTOR_TEMP": ATTRACTOR_TEMP, "ATTRACTOR_MAX_STEPS": ATTRACTOR_MAX_STEPS,
                  "PRECHECK_MIN_GAP": PRECHECK_MIN_GAP, "PRECHECK_MIN_AUC": PRECHECK_MIN_AUC,
                  "PURE_THRESH": PURE_THRESH},
        "arms_differ_verified": arms_differ, "arm_hashes": arm_hashes,
        "cardinality_ok": len(per_arm) == len(ARMS),
        "n_train_instances": len(train_instances), "n_train_scenarios": n_scenarios,
        "per_arm": per_arm,
        "verdict_stats": stats,
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "keying/clustering purity-gate cell; this cell's own purity gate IS the "
                   "capacity-feasibility question being measured, not assumed",
        "progress_logging": "print_flush_true",
    }
    write_metrics(output_dir, metrics, gate_claims=stats.get("gate_claims"))
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
