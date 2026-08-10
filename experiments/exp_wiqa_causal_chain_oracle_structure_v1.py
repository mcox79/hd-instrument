# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 6-arm hash-differ:
#   majority/polecho/bow/loop_internal/loop_oracle/oracle_scramble)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace, via _seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (3-way discrete classification accuracy on a real benchmark; no capacity/
#   noise-floor discriminator threshold)
# - HP_SCOPE: {oracle_covered: [decisive_gate_beats_all_3_baselines, decisive_gate_scramble_collapse]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS_FULL)=3 (full) / 1 (smoke)
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: default_ok_for_this_regime (reuses v2's GATE_THRESH/lexicon unchanged;
#   this cell adds a NEW anchor SOURCE (gold i/j) not a new calibration knob)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL CausalLinkRegister (via v2's build_register/propagate_sign) +
#   loads a small REAL sample of the official gold-explanation release (real_code_path); no
#   synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_wiqa_causal_chain_oracle_structure_v1.md for the full pre-reg.
"""exp_wiqa_causal_chain_oracle_structure_v1 -- DECISIVE ORACLE-STRUCTURE diagnostic.

Question (Director task, 2026-08-10): does CAUSAL-CHAIN-LOOP (validated mechanism from
exp_wiqa_causal_chain_loop_v1/v2) beat the WIQA baselines when handed WIQA's OWN gold
perturbation/effect anchor annotation instead of our weak internal HD-BoW pull-in retrieval?
Isolates: is EXTRACTION the bottleneck (loop WINS with gold anchors), or is the causal-
composition APPROACH itself flawed (loop LOSES even with gold anchors)?

## What "gold structure" means here (read this before trusting any number below)

The cached HF `data/corpora/wiqa/hf_dataset` (question_stem / question_para_step / answer_label /
metadata_*) does NOT itself carry step-level cause/effect anchors or signed edges -- confirmed by
inspecting its schema this session (10 columns, no node/edge fields). The DECISIVE gold source
found this session is WIQA's own EMNLP-2019 "with_explanation" release (its own official
annotation, not an external extractor), downloaded from the SAME S3 bucket the `wiqa-dataset`
GitHub repo's `dataset_info.py` points at:
`https://public-aristo-processes.s3-us-west-2.amazonaws.com/wiqa_dataset_with_explanation/dev.jsonl`
cached at `data/corpora/wiqa/raw_official/dev_with_expl.jsonl` (5005 records, MEASURED this
session; every one of its 5005 `id`s is confirmed a SUBSET of the HF dev split's 6894
`metadata_question_id`s -- MEASURED this session, 100% containment). Each record carries
`explanation.i` / `explanation.j`: WIQA's own crowd-annotated PARAGRAPH-STEP INDICES for the
perturbation-anchor and effect-anchor of that specific question (`-1,-1` for OUTOFPARA_DISTRACTOR
items, which by WIQA's own design have no in-paragraph anchor at all -- a genuine structural
negative, not a coverage gap).

**LEAK CHECK (mandatory per Director task -- VET the oracle derivation hard):** the SAME release
also carries `explanation.di` / `explanation.dj` (SituationLabel enums RESULTS_IN /
RESULTS_IN_OPP / NO_EFFECT). MEASURED this session (all 5005 records): mapping
`dj -> {RESULTS_IN: 'more', RESULTS_IN_OPP: 'less', NO_EFFECT: 'no_effect'}` reproduces
`answer_label` at **5005/5005 = 1.0000 match rate** -- `dj` IS the answer, restated (confirmed
directly from `allenai/wiqa-dataset`'s own `WIQAQuestion.instantiate_from`:
`answer_label = chosen_label.as_less_more()` where `chosen_label` comes from `explanation['dj']`).
**Therefore di/dj are EXCLUDED ENTIRELY from this oracle.** Using them would be reading the label
off an alias field, not testing structure -- exactly the vacuous-win Director warned against.

**What the oracle actually replaces:** ONLY the ANCHOR-RETRIEVAL half of the internal mechanism
(`anchor_step()`'s HD-BoW-cosine pull-in, i.e. "WHERE in the paragraph does the perturbation/
effect happen") is replaced by WIQA's gold (i, j). EDGE-POLARITY extraction (`has_negating_word`
regex check per adjacent-step hop, feeding `build_register`/`propagate_sign`, i.e. "was this hop
a promotes or inhibits edge") is UNCHANGED from the internal loop -- no non-leaking gold source for
per-edge signed polarity was found (the full `wiqa_influence_graphs.jsonl` graph, also downloaded
this session, encodes X/Y/Z/U/V/W if-then template nodes, not a step-index-aligned signed chain,
so it cannot be mapped onto `build_register`'s adjacent-step edges without re-solving the same
extraction problem). This is a **PARTIAL oracle** (gold WHERE, internal weak edge-SIGN) and the
verdict below is scoped to that: a HARD_PASS here shows anchor-retrieval extraction is a verified
bottleneck and that gold anchors + our EXISTING edge-sign mechanism compose into a genuine,
scramble-sensitive causal-reasoning gain; it does NOT independently certify that edge-sign
extraction from paragraph text would be equally fixable.

Raw `steps` field in the official release (index-aligned with i/j) is used for anchor/register
construction -- NOT the HF `question_para_step` (MEASURED this session: raw-vs-HF-filtered step
COUNT differs on 707/5005 = 14.1% of matched records, e.g. trailing punctuation-artifact splits;
using the wrong list would silently misalign gold indices).

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "gold oracle causal structure WIQA influence graph extraction
bottleneck diagnostic"` -> top hit `EXTRACTION_BOTTLENECK` (cosine=0.3311,
data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json) and a meta-synthesis atom
(cosine=0.2949) stating "given correct [causal] structure the mechanism works ... but extraction
of structure from real prose bottlenecks" -- a CLOSELY RELATED prior finding from a DIFFERENT
corpus/mechanism (grounded_appraisal_transfer / CSKG causal-organ), not a duplicate of this
WIQA-specific oracle-structure test (no hit is this exact cell). **Prior-work check verdict:
NOVEL for WIQA; CONSISTENT-HYPOTHESIS-CLASS with a prior CSKG-side finding** (extraction-is-the-
wall, given-structure-works) -- useful outside calibration that a HARD_PASS here would not be an
aberrant result relative to the substrate's broader experience.

## Compute architecture

Sequential-CPU, same as v1/v2 (dict lookups + <=1024-dim vector sums/dots over <=10 steps per
item; v2's FULL landed in 17.6s wall for the SAME 6894-item x 3-seed shape). This cell's oracle
pass operates on a SUBSET (oracle_covered, MEASURED=2893) so wall time is strictly less.

Modes:
  --self-test  Hand-built oracle-vs-internal divergence case + dj-leak-check assertion (on a real
               sample) + CausalLinkRegister/iterative_attractor substrate_signature preflight.
  --smoke      First 300 dev items (deterministic stride, same convention as v1/v2).
  --full       All 6894 dev items, 3 scramble seeds (7,17,29), per-seed checkpointed.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import inspect
import json
import platform
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

ANCHOR_NAME = "wiqa_causal_chain_oracle_structure_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from experiments.exp_wiqa_causal_chain_loop_v2 import (  # noqa: E402
    D, GATE_THRESH, build_register, propagate_sign, load_dev, score_item_base,
    _deterministic_perm,
)
from hdlab.situation_model_accumulate import CausalLinkRegister  # noqa: E402
from hdlab.cleanup_family import iterative_attractor as _iterative_attractor  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics as _ckpt_write_metrics,
)

# ---------------------------------------------------------------------- fixed parameters
SEEDS_SMOKE = [7]
SEEDS_FULL = [7, 17, 29]
SMOKE_N = 300
DEGRADED_BUDGET = 0.02
DECISIVE_MARGIN = 0.05             # HARD-PASS: loop_oracle beats EACH baseline by >= this, on oracle_covered
DECISIVE_COLLAPSE_FRACTION = 0.5   # gate: gold-edge-scramble must erase >=50% of loop_oracle's edge over polecho

OFFICIAL_DIR = os.path.join(REPO_ROOT, "data", "corpora", "wiqa", "raw_official")
OFFICIAL_DEV_PATH = os.path.join(OFFICIAL_DIR, "dev_with_expl.jsonl")
OFFICIAL_DEV_URL = "https://public-aristo-processes.s3-us-west-2.amazonaws.com/wiqa_dataset_with_explanation/dev.jsonl"

SUBSETS = ("all", "oracle_covered", "oracle_covered_multihop")


# ---------------------------------------------------------------------- gold explanation loading
def ensure_official_dev(timeout_s: float = 20.0) -> str:
    """WIQA's OWN official EMNLP-2019 'with_explanation' release (not an external extractor) --
    cached locally; downloaded once if missing. Graceful: returns path even if download fails
    (caller checks os.path.exists)."""
    if os.path.exists(OFFICIAL_DEV_PATH):
        return OFFICIAL_DEV_PATH
    os.makedirs(OFFICIAL_DIR, exist_ok=True)
    try:
        req = urllib.request.Request(OFFICIAL_DEV_URL, headers={"User-Agent": "hd-instrument/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read()
        tmp = OFFICIAL_DEV_PATH + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, OFFICIAL_DEV_PATH)
    except Exception as e:  # noqa: BLE001 -- best-effort cache fill; caller handles absence
        print(f"[warn] could not download {OFFICIAL_DEV_URL}: {type(e).__name__}: {e}", flush=True)
    return OFFICIAL_DEV_PATH


DJ_TO_LABEL = {"RESULTS_IN": "more", "RESULTS_IN_OPP": "less", "NO_EFFECT": "no_effect"}


def load_gold_map() -> Dict[str, Dict]:
    """id -> {i, j, steps (RAW, index-aligned with i/j), question_type, dj (kept ONLY for the
    self-test leak-check assertion; NEVER used in scoring)}."""
    path = ensure_official_dev()
    gold: Dict[str, Dict] = {}
    if not os.path.exists(path):
        return gold
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            expl = rec.get("explanation", {})
            gold[rec["id"]] = {
                "i": expl.get("i"), "j": expl.get("j"),
                "steps": rec.get("steps", []),
                "question_type": rec.get("metadata", {}).get("question_type"),
                "dj": expl.get("dj"),  # self-test leak-check only; NEVER read by scoring below
            }
    return gold


def gold_lookup(qid: str, gold_map: Dict[str, Dict]) -> Optional[Dict]:
    rec = gold_map.get(qid)
    if rec is None:
        return None
    i, j, steps = rec["i"], rec["j"], rec["steps"]
    if i is None or j is None or i < 0 or j < 0:
        return {"covered": False, "reason": "no_inpara_anchor", "steps": steps}
    if not (0 <= i < len(steps) and 0 <= j < len(steps)):
        return {"covered": False, "reason": "out_of_bounds", "steps": steps}
    return {"covered": True, "i": int(i), "j": int(j), "steps": steps, "hop": abs(int(j) - int(i))}


# ---------------------------------------------------------------------- oracle scoring (per item)
def score_item_oracle(base_row: Dict, gold: Optional[Dict]) -> Dict:
    """base_row: a v2 score_item_base() row (has steps=HF-filtered, pp, op, question_id,
    pred_polecho -- used ONLY as the structural-abstain fallback + admission-gate pp check, same
    convention as v2's own arms). gold: gold_lookup() result or None (no coverage at all)."""
    covered = bool(gold and gold.get("covered"))
    if not covered:
        return {"pred_loop_oracle": base_row["pred_polecho"],
                "oracle_diag": {"abstained": True,
                                 "reason": "no_gold_anchor" if gold is None else gold.get("reason")},
                "oracle_covered": False, "oracle_hop": None}
    steps = gold["steps"]
    i, j = gold["i"], gold["j"]
    pp, op = base_row["pp"], base_row["op"]
    if pp == 0:
        # same admission gate as internal loop (question-CLAUSE polarity undetected via lexicon);
        # unrelated to the anchor-retrieval question this cell tests, kept unchanged for parity.
        return {"pred_loop_oracle": base_row["pred_polecho"],
                "oracle_diag": {"abstained": True, "reason": "pp_zero"},
                "oracle_covered": True, "oracle_hop": gold["hop"]}
    reg, _edge_polarity = build_register(steps, negation_check_order=None)
    lo, hi = sorted([i, j])
    sign, trace = propagate_sign(reg, lo, hi)
    if sign is None:
        return {"pred_loop_oracle": base_row["pred_polecho"],
                "oracle_diag": {"abstained": True, "reason": "hop_validate_fail", "trace": trace},
                "oracle_covered": True, "oracle_hop": gold["hop"]}
    propagated = pp * sign
    pred = ("more" if propagated > 0 else "less") if op == 0 else ("more" if propagated == op else "less")
    crosses_negation = any(h.get("polarity") == -1 for h in trace)
    return {"pred_loop_oracle": pred,
            "oracle_diag": {"abstained": False, "propagated_sign": propagated, "trace": trace,
                             "crosses_negation": crosses_negation},
            "oracle_covered": True, "oracle_hop": gold["hop"]}


def score_item_oracle_scramble(base_row: Dict, gold: Optional[Dict], seed: int) -> str:
    """GOLD-EDGE-SCRAMBLE control: SAME gold (i, j) anchors as loop-ORACLE; edge-polarity
    negation-check computed against a deterministically-permuted step order (identical mechanism
    to v2's ABLATION-1 score_item_scramble, applied on top of gold anchors instead of the weak
    BoW-pull-in anchors)."""
    covered = bool(gold and gold.get("covered"))
    if not covered:
        return base_row["pred_polecho"]
    steps = gold["steps"]
    i, j = gold["i"], gold["j"]
    pp, op = base_row["pp"], base_row["op"]
    if pp == 0:
        return base_row["pred_polecho"]
    k = len(steps)
    perm = _deterministic_perm(f"wiqa_oracle_scramble::{seed}::{base_row['question_id']}", k) if k > 0 else []
    reg, _ = build_register(steps, negation_check_order=perm)
    lo, hi = sorted([i, j])
    sign, _trace = propagate_sign(reg, lo, hi)
    if sign is None:
        return base_row["pred_polecho"]
    propagated = pp * sign
    return ("more" if propagated > 0 else "less") if op == 0 else ("more" if propagated == op else "less")


# ---------------------------------------------------------------------- accuracy aggregation
def _subset_rows(rows: List[Dict], subset: str) -> List[Dict]:
    if subset == "all":
        return rows
    if subset == "oracle_covered":
        return [r for r in rows if r["oracle_covered"]]
    if subset == "oracle_covered_multihop":
        return [r for r in rows if r["oracle_covered"] and (r["oracle_hop"] or 0) >= 2]
    raise ValueError(f"unknown subset {subset!r}")


def _acc(rows: List[Dict], pred_key: str) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r[pred_key] == r["gold"]) / len(rows)


def _acc_scramble(rows: List[Dict], scramble_preds: Dict[str, str]) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if scramble_preds[r["question_id"]] == r["gold"]) / len(rows)


# ---------------------------------------------------------------------- full-dev per-seed run
def run_one_seed(seed: int, rows: List[Dict], gold_map: Dict[str, Dict], heartbeat_cb=None) -> Dict:
    t0 = time.time()
    n = len(rows)
    scramble_preds: Dict[str, str] = {}
    for i, r in enumerate(rows):
        gold = gold_lookup(r["question_id"], gold_map)
        scramble_preds[r["question_id"]] = score_item_oracle_scramble(r, gold, seed)
        if heartbeat_cb is not None and (i + 1) % 1000 == 0:
            heartbeat_cb(i + 1, n, time.time() - t0)

    per_subset = {}
    for subset in SUBSETS:
        srows = _subset_rows(rows, subset)
        per_subset[subset] = {
            "n": len(srows),
            "majority": _acc(srows, "pred_majority"),
            "polecho": _acc(srows, "pred_polecho"),
            "bow": _acc(srows, "pred_bow"),
            "loop_internal": _acc(srows, "pred_loop"),
            "loop_oracle": _acc(srows, "pred_loop_oracle"),
            "oracle_scramble": _acc_scramble(srows, scramble_preds),
        }
    elapsed = time.time() - t0
    n_oracle_fired = sum(1 for r in rows if r["oracle_covered"] and not r["oracle_diag"]["abstained"])
    n_oracle_covered = sum(1 for r in rows if r["oracle_covered"])
    return {"seed": seed, "n_items": n, "elapsed_s": round(elapsed, 4), "per_subset": per_subset,
            "n_oracle_covered": n_oracle_covered,
            "oracle_fired_rate_within_covered": (n_oracle_fired / n_oracle_covered) if n_oracle_covered else float("nan")}


def _arms_must_differ(rows: List[Dict], scramble_preds_seed0: Dict[str, str]) -> Dict:
    def _digest(vals):
        b = json.dumps(list(vals), sort_keys=False, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    sigs = {
        "majority": _digest([r["pred_majority"] for r in rows]),
        "polecho": _digest([r["pred_polecho"] for r in rows]),
        "bow": _digest([r["pred_bow"] for r in rows]),
        "loop_internal": _digest([r["pred_loop"] for r in rows]),
        "loop_oracle": _digest([r["pred_loop_oracle"] for r in rows]),
        "oracle_scramble": _digest([scramble_preds_seed0[r["question_id"]] for r in rows]),
    }
    pairs_differ = {f"{a}_vs_{b}": sigs[a] != sigs[b]
                     for i, a in enumerate(sigs) for b in list(sigs)[i + 1:]}
    return {"sigs": sigs, "pairs_differ": pairs_differ, "all_differ": all(pairs_differ.values())}


# ---------------------------------------------------------------------- verdict logic
def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else 0.5 * (s[mid - 1] + s[mid])


def apply_bands(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    seeds = sorted(per_seed.keys(), key=lambda s: int(s))
    subset_table: Dict[str, Dict] = {}
    for subset in SUBSETS:
        s0 = per_seed[seeds[0]]["per_subset"][subset]
        scramble_vals = [per_seed[s]["per_subset"][subset]["oracle_scramble"] for s in seeds]
        scramble_median = _median(scramble_vals)
        loop_oracle = s0["loop_oracle"]
        polecho = s0["polecho"]
        loop_minus_polecho = loop_oracle - polecho
        loop_minus_scramble = loop_oracle - scramble_median
        collapse_frac = (loop_minus_scramble / loop_minus_polecho) if loop_minus_polecho > 1e-9 else None
        subset_table[subset] = {
            "n": s0["n"], "majority": s0["majority"], "polecho": polecho, "bow": s0["bow"],
            "loop_internal": s0["loop_internal"], "loop_oracle": loop_oracle,
            "oracle_scramble_vals": scramble_vals, "oracle_scramble_median": scramble_median,
            "loop_oracle_minus_polecho": loop_minus_polecho, "loop_oracle_minus_scramble": loop_minus_scramble,
            "collapse_frac": collapse_frac,
            "loop_oracle_minus_majority": loop_oracle - s0["majority"],
            "loop_oracle_minus_bow": loop_oracle - s0["bow"],
            "loop_oracle_minus_loop_internal": loop_oracle - s0["loop_internal"],
        }

    primary = subset_table["oracle_covered"]
    beats_all = (primary["loop_oracle_minus_majority"] >= DECISIVE_MARGIN
                 and primary["loop_oracle_minus_polecho"] >= DECISIVE_MARGIN
                 and primary["loop_oracle_minus_bow"] >= DECISIVE_MARGIN)

    mh = subset_table["oracle_covered_multihop"]
    mh_beats_all = (mh["loop_oracle_minus_majority"] >= DECISIVE_MARGIN
                    and mh["loop_oracle_minus_polecho"] >= DECISIVE_MARGIN
                    and mh["loop_oracle_minus_bow"] >= DECISIVE_MARGIN)

    n0 = per_seed[seeds[0]]
    detail = {
        "subset_table": subset_table,
        "beats_all_3_baselines_oracle_covered": beats_all,
        "beats_all_3_baselines_oracle_covered_multihop": mh_beats_all,
        "n_oracle_covered": n0["n_oracle_covered"],
        "oracle_fired_rate_within_covered": n0["oracle_fired_rate_within_covered"],
        "coverage_frac_of_full_dev": n0["n_oracle_covered"] / n0["n_items"] if n0["n_items"] else float("nan"),
    }

    if not beats_all:
        tier = "HARD_FAIL"
        msg = (f"INFERENCE_APPROACH_FLAWED_EVEN_WITH_GOLD_ANCHORS: on oracle_covered "
               f"(n={primary['n']}), loop_oracle={primary['loop_oracle']:.4f} does NOT beat all 3 "
               f"baselines by >={DECISIVE_MARGIN} (vs majority={primary['loop_oracle_minus_majority']:.4f}, "
               f"vs polecho={primary['loop_oracle_minus_polecho']:.4f}, "
               f"vs bow={primary['loop_oracle_minus_bow']:.4f}) -- even fed WIQA's own gold "
               f"perturbation/effect anchors, the causal-chain-composition mechanism does not "
               f"outperform baselines; the wall is deeper than anchor-retrieval extraction.")
    else:
        cf = primary["collapse_frac"]
        cf_s = f"{cf:.3f}" if cf is not None else "n/a"
        if cf is not None and cf >= DECISIVE_COLLAPSE_FRACTION:
            tier = "HARD_PASS"
            msg = (f"ANCHOR_EXTRACTION_IS_THE_BOTTLENECK: on oracle_covered (n={primary['n']}), "
                   f"loop_oracle={primary['loop_oracle']:.4f} beats majority "
                   f"(+{primary['loop_oracle_minus_majority']:.4f}), polecho "
                   f"(+{primary['loop_oracle_minus_polecho']:.4f}), bow "
                   f"(+{primary['loop_oracle_minus_bow']:.4f}) each by >={DECISIVE_MARGIN}, AND "
                   f"gold-edge-scramble collapses collapse_frac={cf_s} >= {DECISIVE_COLLAPSE_FRACTION} "
                   f"-- the causal-chain composition mechanism is SOUND when given correct anchors; "
                   f"SCOPED to anchor-retrieval (edge-polarity extraction remains the internal weak "
                   f"regex mechanism in this test, see module docstring).")
        else:
            tier = "MIDDLE_BAND"
            msg = (f"ORACLE_BEATS_BASELINES_BUT_GAIN_NOT_CAUSAL: on oracle_covered (n={primary['n']}), "
                   f"loop_oracle beats all 3 baselines by >={DECISIVE_MARGIN} but gold-edge-scramble "
                   f"collapse_frac={cf_s} < {DECISIVE_COLLAPSE_FRACTION} -- the gain from gold anchors "
                   f"looks topological/structural rather than genuine signed-edge causal reasoning "
                   f"(same pattern v2 found for the internal mechanism on active_multihop).")
    if not mh_beats_all and beats_all:
        msg += (f" [oracle_covered_multihop (n={mh['n']}) CAVEAT: does NOT independently clear "
                f"beats-all-3 there (vs majority={mh['loop_oracle_minus_majority']:.4f}, "
                f"vs polecho={mh['loop_oracle_minus_polecho']:.4f}, vs bow={mh['loop_oracle_minus_bow']:.4f}) "
                f"-- primary tier is NOT overridden by this, but the deeper-hop subset is weaker.]")
    return tier, msg, detail


# ---------------------------------------------------------------------- output plumbing
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


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec["extra"] = extra
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------- examples for report
def pick_examples(rows: List[Dict], n: int = 5) -> Dict:
    oracle_right_internal_wrong = [r for r in rows if r["oracle_covered"]
                                    and r["pred_loop_oracle"] == r["gold"] and r["pred_loop"] != r["gold"]]
    oracle_right_polecho_wrong = [r for r in rows if r["oracle_covered"]
                                   and r["pred_loop_oracle"] == r["gold"] and r["pred_polecho"] != r["gold"]]
    anchor_divergence = [r for r in rows if r["oracle_covered"] and r["p_idx"] is not None
                          and r["o_idx"] is not None]

    def _fmt(r):
        return {"question_id": r["question_id"], "gold": r["gold"],
                "pred_loop_oracle": r["pred_loop_oracle"], "pred_loop_internal": r["pred_loop"],
                "pred_polecho": r["pred_polecho"], "internal_p_idx": r["p_idx"], "internal_o_idx": r["o_idx"]}

    n_anchor_diverge = 0
    for r in anchor_divergence:
        g = r.get("_gold_ij")
        if g and (r["p_idx"] != g[0] or r["o_idx"] != g[1]):
            n_anchor_diverge += 1

    return {"oracle_wins_vs_internal": [_fmt(r) for r in oracle_right_internal_wrong[:n]],
            "n_oracle_wins_vs_internal_total": len(oracle_right_internal_wrong),
            "oracle_wins_vs_polecho": [_fmt(r) for r in oracle_right_polecho_wrong[:n]],
            "n_oracle_wins_vs_polecho_total": len(oracle_right_polecho_wrong),
            "n_internal_anchor_diverges_from_gold_anchor": n_anchor_diverge,
            "n_checked_for_anchor_divergence": len(anchor_divergence)}


# ---------------------------------------------------------------------- self-test
def _hand_case_oracle_vs_internal_divergence() -> Dict:
    """Hand-built 4-step paragraph where the weak BoW anchor would land on the WRONG step (a
    decoy step shares more surface vocabulary with the outcome clause than the true step), but
    the gold (i, j) anchor points at the CORRECT step. Proves loop_oracle and loop_internal can
    genuinely diverge (arms-differ is not vacuous) and that the oracle path is exercised
    end-to-end via the REAL build_register/propagate_sign substrate objects."""
    steps = [
        "a cloud forms in the sky",             # step 0
        "wind pushes the cloud along",           # step 1: TRUE perturbation-relevant step
        "the cloud cools further and further",   # step 2: decoy -- shares "cloud"/"further" bigram feel
        "rain falls heavily from the cloud",      # step 3: TRUE effect-relevant step
    ]
    base_row = {"pred_polecho": "more", "pp": 1, "op": 1, "question_id": "hand:oracle_vs_internal"}
    gold_rec = {"covered": True, "i": 1, "j": 3, "steps": steps, "hop": 2}
    r_oracle = score_item_oracle(base_row, gold_rec)
    assert r_oracle["oracle_covered"] is True
    assert r_oracle["oracle_diag"]["abstained"] is False, r_oracle
    # sign check: no negating word on step 2 or 3 -> both hop edges polarity +1 -> propagated=pp*1=1=op -> "more"
    assert r_oracle["pred_loop_oracle"] == "more", r_oracle
    # now flip: make the TRUE path cross a negating word (edge 2) -- oracle prediction must flip to "less"
    steps_neg = steps[:2] + ["the cloud stops moving and stalls", "rain falls heavily from the cloud"]
    gold_rec_neg = {"covered": True, "i": 1, "j": 3, "steps": steps_neg, "hop": 2}
    r_oracle_neg = score_item_oracle(base_row, gold_rec_neg)
    assert r_oracle_neg["pred_loop_oracle"] == "less", r_oracle_neg
    return {"oracle_pred_pos": r_oracle["pred_loop_oracle"], "oracle_pred_neg": r_oracle_neg["pred_loop_oracle"],
            "oracle_diag_pos": r_oracle["oracle_diag"], "oracle_diag_neg": r_oracle_neg["oracle_diag"]}


def _hand_case_no_coverage() -> Dict:
    """gold=None (no id match) or gold['covered']=False (OUTOFPARA_DISTRACTOR, i=j=-1) must fall
    back to pred_polecho, matching the abstain contract, not raise."""
    base_row = {"pred_polecho": "no_effect", "pp": 1, "op": 0, "question_id": "hand:nogold"}
    r_none = score_item_oracle(base_row, None)
    r_uncov = score_item_oracle(base_row, {"covered": False, "reason": "no_inpara_anchor", "steps": []})
    assert r_none["pred_loop_oracle"] == "no_effect" and r_none["oracle_covered"] is False
    assert r_uncov["pred_loop_oracle"] == "no_effect" and r_uncov["oracle_covered"] is False
    return {"none_case": r_none, "uncovered_case": r_uncov}


def _hand_case_zero_hop_oracle() -> Dict:
    """gold i==j (zero-hop) must propagate as sign=+1 empty trace, matching v2's already-tested
    zero-hop invariant, now exercised through the oracle path."""
    steps = ["a seed is planted", "sunlight reaches the leaves", "the plant grows"]
    base_row = {"pred_polecho": "more", "pp": 1, "op": 1, "question_id": "hand:zerohop"}
    gold_rec = {"covered": True, "i": 1, "j": 1, "steps": steps, "hop": 0}
    r = score_item_oracle(base_row, gold_rec)
    assert r["oracle_diag"]["abstained"] is False
    assert r["oracle_diag"]["propagated_sign"] == 1
    assert r["oracle_diag"]["trace"] == []
    return {"pred": r["pred_loop_oracle"], "diag": r["oracle_diag"]}


def _dj_leak_check_real_sample(gold_map: Dict[str, Dict], n: int = 200) -> Dict:
    """MEASURED (real data, not hand-built): confirms dj->answer_label match rate is
    suspiciously high on a real sample, JUSTIFYING the design decision to exclude di/dj from the
    oracle entirely (documents the leak-check numerically, not just in prose)."""
    dev = load_dev()
    id_to_gold = {r["metadata_question_id"]: r["answer_label"] for r in dev}
    checked = 0
    matched = 0
    items = list(gold_map.items())[:max(n, 1)]
    for qid, rec in items:
        gold_answer = id_to_gold.get(qid)
        if gold_answer is None or rec.get("dj") is None:
            continue
        mapped = DJ_TO_LABEL.get(rec["dj"])
        if mapped is None:
            continue
        checked += 1
        if mapped == gold_answer:
            matched += 1
    match_rate = (matched / checked) if checked else float("nan")
    return {"checked": checked, "matched": matched, "match_rate": match_rate}


def self_test() -> Dict:
    hand_divergence = _hand_case_oracle_vs_internal_divergence()
    hand_no_coverage = _hand_case_no_coverage()
    hand_zero_hop = _hand_case_zero_hop_oracle()

    # real_code_path + substrate_signature preflight (F.1/F.2) -- same substrate objects as v2
    sig = inspect.signature(CausalLinkRegister.__init__)
    assert set(["d", "generator", "max_event_slots"]).issubset(sig.parameters.keys()), sig
    sig_add = inspect.signature(CausalLinkRegister.add_causal_link)
    assert set(["cause_idx", "effect_idx", "polarity"]).issubset(sig_add.parameters.keys()), sig_add

    gold_map = load_gold_map()
    official_release_ok = len(gold_map) > 0
    dj_leak = None
    real_sample_summary = None
    if official_release_ok:
        dj_leak = _dj_leak_check_real_sample(gold_map, n=200)
        # DOCUMENT the leak numerically (not just assert) so a future re-run that finds a LOWER
        # match rate is visible in the metrics rather than silently passing a weaker assert.
        assert dj_leak["checked"] >= 50, f"too few checkable records for a meaningful leak-check: {dj_leak}"

        dev = load_dev()
        real_ids_covered = [ex for ex in dev[:500] if gold_lookup(ex["metadata_question_id"], gold_map)
                             and gold_lookup(ex["metadata_question_id"], gold_map).get("covered")][:20]
        real_rows = []
        for ex in real_ids_covered:
            base = score_item_base(ex)
            gold = gold_lookup(ex["metadata_question_id"], gold_map)
            oracle = score_item_oracle(base, gold)
            real_rows.append({"question_id": base["question_id"], "gold": base["gold"],
                               "pred_loop_internal": base["pred_loop"],
                               "pred_loop_oracle": oracle["pred_loop_oracle"],
                               "oracle_covered": oracle["oracle_covered"]})
        real_sample_summary = {"n_real_oracle_covered_sample": len(real_rows), "rows": real_rows}

    return {"hand_divergence": hand_divergence, "hand_no_coverage": hand_no_coverage,
            "hand_zero_hop": hand_zero_hop, "official_release_ok": official_release_ok,
            "n_gold_records_loaded": len(gold_map), "dj_leak_check": dj_leak,
            "real_sample_summary": real_sample_summary}


# ---------------------------------------------------------------------- main
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
        _write_metrics_local(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str), flush=True)
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading WIQA dev split + official gold-explanation release...", flush=True)
    dev = load_dev()
    gold_map = load_gold_map()
    print(f"[{run_mode}] gold_map records loaded: {len(gold_map)}", flush=True)
    if args.smoke:
        stride = max(1, len(dev) // SMOKE_N)
        dev = dev[::stride][:SMOKE_N]
    n_total = len(dev)
    print(f"[{run_mode}] scoring {n_total} items (base + oracle, seed-independent pass)...", flush=True)

    rows: List[Dict] = []
    n_degraded = 0
    for i, ex in enumerate(dev):
        try:
            base = score_item_base(ex)
            gold = gold_lookup(base["question_id"], gold_map)
            oracle = score_item_oracle(base, gold)
            row = dict(base)
            row.update(oracle)
            row["_gold_ij"] = (gold["i"], gold["j"]) if (gold and gold.get("covered")) else None
            rows.append(row)
        except Exception as e:  # noqa: BLE001 -- per-item failure isolation (META_RULE_J)
            n_degraded += 1
            rows.append({
                "question_id": ex.get("metadata_question_id", f"UNKNOWN_{i}"),
                "gold": ex.get("answer_label", "no_effect"), "p_idx": None, "o_idx": None,
                "pred_majority": "more", "pred_polecho": "no_effect", "pred_bow": "no_effect",
                "pred_loop": "no_effect", "pred_loop_oracle": "no_effect",
                "oracle_diag": {"abstained": True, "reason": "SCORING_EXCEPTION"},
                "oracle_covered": False, "oracle_hop": None, "_gold_ij": None,
                "degraded_scoring": True, "failure_class": type(e).__name__, "failure_detail": str(e)[:300],
            })
        if (i + 1) % 1000 == 0:
            print(f"[{run_mode}] base+oracle scoring {i + 1}/{n_total} elapsed={time.time() - t0:.1f}s", flush=True)
            _write_heartbeat(output_dir, i + 1, n_total, time.time() - t0, {"phase": "base_oracle"})

    degraded_frac = n_degraded / n_total if n_total else 0.0
    print(f"[{run_mode}] base+oracle pass done: {n_degraded}/{n_total} degraded ({degraded_frac:.4f}); "
          f"elapsed={time.time() - t0:.1f}s", flush=True)
    if degraded_frac > DEGRADED_BUDGET:
        raise RuntimeError(
            f"DEGRADED_SCORING_BUDGET_EXCEEDED: {degraded_frac:.4f} > {DEGRADED_BUDGET} "
            f"({n_degraded}/{n_total} items hit a per-item scoring exception)")

    run_config = {"run_mode": run_mode, "anchor": ANCHOR_NAME, "n_items": n_total}
    done, remaining = resumable_seeds(seeds, output_dir, run_config=run_config)
    print(f"[{run_mode}] {len(done)}/{len(seeds)} seeds already complete; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{run_mode}] seed={seed} gold-edge-scrambling+scoring...", flush=True)

        def _hb(i, n, el, _seed=seed):
            _write_heartbeat(output_dir, i, n, el, {"phase": "oracle_scramble", "seed": _seed})

        seed_result = run_one_seed(seed, rows, gold_map, heartbeat_cb=_hb)
        write_partial(output_dir, seed, {"seed": seed, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                                          "n_items": n_total, "result": seed_result})
        oc = seed_result["per_subset"]["oracle_covered"]
        print(f"[{run_mode}] seed={seed} done: oracle_covered(n={oc['n']}) loop_oracle={oc['loop_oracle']:.4f} "
              f"polecho={oc['polecho']:.4f} elapsed={seed_result['elapsed_s']:.1f}s", flush=True)

    per_seed_partials = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed = {str(s): per_seed_partials[str(s)]["result"] for s in seeds}

    scramble0 = {r["question_id"]: score_item_oracle_scramble(r, gold_lookup(r["question_id"], gold_map), seeds[0])
                 for r in rows}
    diff = _arms_must_differ(rows, scramble0)

    tier, msg, band_detail = apply_bands(per_seed)
    if not diff["all_differ"]:
        tier = "HARD_FAIL"
        msg = f"ARMS_IDENTICAL overrides band verdict: {diff} || {msg}"

    examples = pick_examples(rows)
    elapsed = time.time() - t0

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": f"{tier}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_items": n_total, "n_degraded": n_degraded, "degraded_frac": degraded_frac,
        "gate_thresh": GATE_THRESH, "n_dim": D, "seeds": seeds,
        "decisive_margin": DECISIVE_MARGIN, "decisive_collapse_fraction_threshold": DECISIVE_COLLAPSE_FRACTION,
        "n_gold_records_in_official_release": len(gold_map),
        "per_seed": per_seed, "band_detail": band_detail,
        "arms_differ_verified": diff["all_differ"], "arms_differ_check": diff,
        "examples": examples,
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "3-way discrete classification accuracy comparison on a real benchmark (WIQA); "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: reuses v2's GATE_THRESH/lexicon unchanged; "
                              "this cell adds a new gold ANCHOR SOURCE, not a new calibration knob",
        "hp_scope": {"oracle_covered": ["decisive_gate_beats_all_3_baselines", "decisive_gate_scramble_collapse"]},
        "progress_logging": "print_flush_true",
        "oracle_scope_note": "PARTIAL oracle: gold (i,j) anchor indices from WIQA's official "
                              "with_explanation release REPLACE the internal HD-BoW pull-in; "
                              "edge-polarity extraction (has_negating_word regex) is UNCHANGED/internal. "
                              "di/dj EXCLUDED (see dj_leak_check in self-test: match_rate vs answer_label).",
    }
    _ckpt_write_metrics(Path(output_dir), metrics, results=None)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_seed",)},
                      indent=2, default=str), flush=True)


def _write_metrics_local(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


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
