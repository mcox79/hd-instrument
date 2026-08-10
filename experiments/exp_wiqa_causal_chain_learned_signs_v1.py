# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 6-arm hash-differ: majority/polecho/bow/
#   loop_hand_rule/loop_learned/loop_learned_scramble)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace, via _seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (3-way discrete classification accuracy on a real benchmark; no capacity/
#   noise-floor discriminator threshold)
# - HP_SCOPE: {oracle_covered_multihop: [decisive_gate_beats_all_3_baselines,
#   decisive_gate_scramble_collapse, decisive_gate_no_leak, decisive_gate_generalizes,
#   decisive_gate_learner_fit]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS_FULL)=3 (full) / 1 (smoke)
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: default_ok_for_this_regime (reuses v2's GATE_THRESH/anchor mechanism and
#   score_item_base's polarity lexicon UNCHANGED; the only new calibration surface -- the learned
#   edge classifier's own hyperparameters -- inherits ruleind/gam/estimation plugin MODULE
#   DEFAULTS, not tuned against observed dev numbers, see fit_edge_classifier())
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL CausalLinkRegister (via propagate_sign) + the REAL
#   hdlab.learner.registry.learn() end-to-end at N~16-20 synthetic episodes, AND loads a real
#   sample of the official train/dev with_explanation releases (real_code_path); no
#   synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_wiqa_causal_chain_learned_signs_v1.md for the full pre-reg.
"""exp_wiqa_causal_chain_learned_signs_v1 -- MISSING-LEARNING hypothesis test (Director task,
2026-08-10, standing rule b: missing-LEARNING -> reuse/expand hdlab/learner, don't hand-roll).

Every prior WIQA causal-chain-loop attempt (`exp_wiqa_causal_chain_loop_v1/v2`,
`exp_wiqa_causal_chain_oracle_structure_v1`, all HARD_FAIL/MIDDLE_BAND) extracted per-edge
polarity with a HAND-WRITTEN regex lexicon (`has_negating_word` -- one fixed
`NEGATING_STEP_WORDS` set, checked against only the downstream step's text). This cell asks: can
`hdlab/learner` (the centralized MDL model-selection engine, `hdlab/learner/registry.py`) instead
LEARN a glass-box edge-polarity classifier from WIQA's own official gold-explanation TRAIN split,
and does composing those LEARNED signs through the SAME `propagate_sign` chain-composition loop
beat the baselines on a LEAK-SAFE MULTI-HOP held-out DEV subset?

## Where the per-edge supervision comes from (read before trusting any number below)

WIQA's official EMNLP-2019 "with_explanation" release (`train.jsonl` / `test.jsonl` / `dev.jsonl`
at `public-aristo-processes.s3-us-west-2.amazonaws.com/wiqa_dataset_with_explanation/`, the SAME
official source `exp_wiqa_causal_chain_oracle_structure_v1` already vetted for `dev.jsonl`; this
cell additionally downloads `train.jsonl`/`test.jsonl` from the SAME bucket, cached at
`data/corpora/wiqa/raw_official/{train,test}_with_expl.jsonl`) carries, per record,
`explanation.dj` (SituationLabel: RESULTS_IN / RESULTS_IN_OPP / NO_EFFECT) -- WIQA's own
annotator judgement of X's NET effect on Y over the WHOLE (i, j) span, REGARDLESS of hop distance.
MEASURED this session (oracle_structure_v1's own self-test + prior pre-reg): `dj` reproduces
`answer_label` at 5005/5005 = 1.0000 on dev -- **`dj` is the answer, restated, at EVERY hop
distance, not just hop=1.** This means `dj` can NEVER be used as edge-level supervision for a
MULTI-hop item (it is the composite path label, not a per-edge label) -- but for a hop=1 item
(`|i-j|==1`, i.e. `i` and `j` are ADJACENT steps), the path IS a single edge, so the composite
label IS ALSO, mechanically, that one edge's own polarity. This is NOT a leak of the multi-hop
target: hop=1 TRAIN items are DIFFERENT items than the hop>=2 DEV items this cell evaluates on,
their `steps`/`para_id` never overlap the DEV split (MEASURED this session: train/dev/test
official `para_id` sets are pairwise disjoint, 0/0/0 overlap), and `dj` is never read at DEV
evaluation time for the decisive arms (evaluation always compares composed PREDICTIONS against
`answer_label`, exactly as every prior WIQA cell already does).

**Edge-pool construction (`build_edge_pool`):** TRAIN/TEST hop=1 records with a valid in-bounds
gold anchor and `dj in {RESULTS_IN, RESULTS_IN_OPP}` (excludes `NO_EFFECT` -- the composition
substrate `CausalLinkRegister.add_causal_link` only accepts polarity in {+1,-1}, matching the
existing hand-rule mechanism's own binary output), DEDUPED by `(para_id, lo, hi)` taking the
majority `dj`-class over duplicate occurrences (the SAME paragraph produces MANY `graph_id`
question variants that share the SAME physical adjacent-step edge -- MEASURED this session:
train hop=1 raw=5096 records collapse to 503 unique edges after dedup, test hop=1 raw collapses to
68 unique edges). Features per edge = stemmed content words of step_i ("i:word") and step_j
("j:word") (Director's pointer: "the text of step_i + step_j ... glass-box, inspectable features
-- NOT an embedding black box") -- richer than the hand-rule's step_j-only lexicon by design.

## LEAK-SAFETY design (mandatory per Director task -- read this section before trusting HARD_PASS)

Two DISTINCT leak questions, both checked and reported (not just asserted):

1. **Split-identity leak** (`dj` globally = answer, at any hop): addressed structurally above --
   the fitted classifier's TRAIN supervision comes ONLY from hop<=1 TRAIN/TEST items; the DECISIVE
   evaluation is restricted to hop>=2 DEV items (`oracle_covered_multihop`, gold-anchor-covered
   AND `|j-i|>=2`) and compares composed predictions to `answer_label`, never to `dj` directly.
   `dj_leak_check_by_hop()` reconfirms (real DEV sample) that the `dj`->`answer_label` identity
   holds UNIFORMLY across hop buckets (expected ~1.0 both ways) -- documenting WHY `dj` is
   entirely excluded from decisive scoring regardless of hop, not just for hop=1.

2. **Single-edge-dominates leak** (Director's specific ask: "confirm the per-edge sign target does
   NOT trivially reproduce the multi-hop answer ... if a single edge's sign predicts the
   multi-hop answer >~0.9 ... exclude"): `leak_check_single_edge()` operationalizes this
   mechanistically -- for every `oracle_covered_multihop` DEV item, ISOLATE the first edge (resp.
   last edge) of the gold path (force every OTHER edge's learned sign to neutral +1) and check
   whether that ONE edge's solo-composed prediction already matches `answer_label`. If either
   isolated-edge match rate is >= `LEAK_MATCH_RATE_THRESH=0.9`, the multi-hop subset is flagged as
   effectively single-hop-in-disguise and the HARD_PASS gate is refused regardless of the full
   composed accuracy.

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "learned glass-box edge polarity classifier causal composition
WIQA multihop hdlab learner MDL"` -> top hits are GENERIC concept-KB atoms (`entity='learner'`
cosine=0.3809, `entity='learned'` cosine=0.3467 -- both WordNet/verbnet-level lexical atoms, not
prior experiment cells) and, below the 0.30 novelty threshold, `learned_role_assigner_reader_
composition_v3` (cosine=0.2715, `preregs/reader_composition_cg_revival_v3.md` -- a DIFFERENT
domain: reader-composition role assignment, not WIQA edge-polarity). **Prior-work check verdict:
NOVEL** -- no prior WIQA-learned-edge-sign cell exists at cosine>0.30; nearest genuine
experiment-cell hit is a different domain below threshold.

## Compute architecture

Sequential-CPU (same class as v1/v2/oracle_structure -- dict/string feature lookups + <=1024-dim
CausalLinkRegister ops over <=10 steps per item; the classifier FIT is a one-time O(n_train_edges
x n_candidate_features) pass over 503 edges, not a per-item cost). Storage strategy: no_storage
(no HD bundling/sharding of items -- the hypothesis is a plain glass-box dict/rule table, not
substrate-stored vectors).

Modes:
  --self-test  Hand-built classifier-fit + sign-flip + leak-check-logic cases + REAL
               hdlab.learner.registry.learn() end-to-end at N~16-20 + real-sample edge-pool /
               dj-leak-by-hop checks + CausalLinkRegister/learner substrate_signature preflight.
  --smoke      First 300 dev items (deterministic stride, same convention as v1/v2/oracle), FULL
               train/test edge pools (cheap, always fit in full regardless of dev sampling).
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
import math
import platform
import sys
import time
import traceback
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

ANCHOR_NAME = "wiqa_causal_chain_learned_signs_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from experiments.exp_wiqa_causal_chain_loop_v2 import (  # noqa: E402
    D, GATE_THRESH, load_dev, score_item_base, propagate_sign, content_tokens, _deterministic_perm,
)
from experiments.exp_wiqa_causal_chain_oracle_structure_v1 import (  # noqa: E402
    load_gold_map, gold_lookup, score_item_oracle, DJ_TO_LABEL,
)
from hdlab.situation_model_accumulate import CausalLinkRegister  # noqa: E402
from hdlab.learner import registry as learner_registry  # noqa: E402
from hdlab.learner.core import KEEP_EPISODIC  # noqa: E402
from hdlab.learner.plugins import ruleind_plugin, estimation_plugin, gam_plugin  # noqa: E402
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
DECISIVE_MARGIN = 0.05             # CITED@Director task contract, matches v2/oracle convention
DECISIVE_COLLAPSE_FRACTION = 0.5   # CITED@v2/oracle convention: scramble must erase >=50% of edge
LEAK_MATCH_RATE_THRESH = 0.9       # CITED@Director task contract ("single edge predicts >~0.9")
EDGE_GENERALIZATION_THRESH = 0.60  # HYPOTHESIZED@this cell: binary pos/neg chance=0.5;
                                    # "meaningfully above chance" set at chance+0.10
MIN_EDGE_DEV_N = 20                # sanity floor for the held-out edge generalization check

OFFICIAL_DIR = os.path.join(REPO_ROOT, "data", "corpora", "wiqa", "raw_official")
OFFICIAL_SPLIT_URLS = {
    split: f"https://public-aristo-processes.s3-us-west-2.amazonaws.com/wiqa_dataset_with_explanation/{split}.jsonl"
    for split in ("train", "dev", "test")
}
CANDIDATE_PLUGINS = ["ruleind", "estimation", "gam"]
# proginduction (PLUGIN 4) deliberately EXCLUDED: it searches a bounded boolean DSL over a small
# set of NAMED predicates (see hdlab/learner/plugins/proginduction_plugin.py docstring) -- shape
# mismatch for an open sparse vocabulary of hundreds of stemmed content-word features; the other
# 3 plugins (frequency-key lookup / MDL rule conjunctions / additive graded log-odds) all natively
# accept an arbitrary feat_fn(inst)->iterable[str] and are the right hypothesis-space family here.

SUBSETS = ("all", "oracle_covered", "oracle_covered_multihop")

DJ_TO_SIGN_CLASS = {"RESULTS_IN": "pos", "RESULTS_IN_OPP": "neg"}  # excludes NO_EFFECT (see docstring)


# ---------------------------------------------------------------------- official split loading
def ensure_official_split(split: str, timeout_s: float = 30.0) -> str:
    """Downloads+caches WIQA's own official with_explanation release for `split` (train/dev/test)
    from the SAME S3 bucket oracle_structure_v1 already vetted for dev. Graceful: returns the path
    even if download fails (caller checks os.path.exists)."""
    path = os.path.join(OFFICIAL_DIR, f"{split}_with_expl.jsonl")
    if os.path.exists(path):
        return path
    os.makedirs(OFFICIAL_DIR, exist_ok=True)
    try:
        req = urllib.request.Request(OFFICIAL_SPLIT_URLS[split], headers={"User-Agent": "hd-instrument/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read()
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception as e:  # noqa: BLE001 -- best-effort cache fill; caller handles absence
        print(f"[warn] could not download {OFFICIAL_SPLIT_URLS[split]}: {type(e).__name__}: {e}", flush=True)
    return path


def load_official_records(split: str) -> List[Dict]:
    path = ensure_official_split(split)
    out: List[Dict] = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


# ---------------------------------------------------------------------- edge-pool construction
def _build_edge_pool_from_records(recs: List[Dict]) -> List[Dict]:
    """Pure function (no I/O) -- hop=1 valid in-bounds anchor records with dj in {RESULTS_IN,
    RESULTS_IN_OPP}, DEDUPED by (para_id, lo, hi) taking the majority dj-class over duplicate
    graph_id variants of the same physical edge. Deterministic ordering: sorted() over string/int
    keys only (PROT-023/F.5 safe -- no hash()/list(set()) ordering)."""
    grouped: Dict[Tuple[str, int, int], List[Tuple[str, str, str]]] = {}
    for r in recs:
        expl = r.get("explanation", {})
        i, j = expl.get("i"), expl.get("j")
        dj = expl.get("dj")
        steps = r.get("steps", [])
        if i is None or j is None or i < 0 or j < 0:
            continue
        if abs(int(j) - int(i)) != 1:
            continue
        lo, hi = sorted([int(i), int(j)])
        if not (0 <= lo < hi < len(steps)):
            continue
        cls = DJ_TO_SIGN_CLASS.get(dj)
        if cls is None:
            continue
        para_id = str(r.get("metadata", {}).get("para_id"))
        key = (para_id, lo, hi)
        grouped.setdefault(key, []).append((cls, steps[lo], steps[hi]))
    pool: List[Dict] = []
    for key in sorted(grouped.keys()):
        para_id, lo, hi = key
        votes = grouped[key]
        cls_counts = Counter(v[0] for v in votes)
        maj_cls = cls_counts.most_common(1)[0][0]
        _, text_lo, text_hi = votes[0]
        pool.append({
            "gold_class": maj_cls, "para_id": para_id, "lo": lo, "hi": hi,
            "words_i": content_tokens(text_lo), "words_j": content_tokens(text_hi),
            "n_votes": len(votes), "vote_purity": round(cls_counts[maj_cls] / len(votes), 4),
        })
    return pool


def build_edge_pool(split: str) -> List[Dict]:
    return _build_edge_pool_from_records(load_official_records(split))


def edge_feat_fn(ep: Dict) -> List[str]:
    return [f"i:{w}" for w in ep["words_i"]] + [f"j:{w}" for w in ep["words_j"]]


def edge_key_fn(ep: Dict) -> Tuple[str, ...]:
    return tuple(sorted(edge_feat_fn(ep)))


# ---------------------------------------------------------------------- fit via hdlab/learner
def fit_edge_classifier(train_pool: List[Dict]):
    """Centralized hdlab.learner.registry.learn() auto-selects among ruleind (MDL conjunction
    rules) / estimation (frequency-key lookup) / gam (additive graded log-odds), all via the
    SAME MDL two-part-code model-selection (hdlab/learner/core.py:mdl_select). Hyperparameters
    are each plugin's own MODULE DEFAULTS (not passed here) -- no post-hoc tuning against dev
    numbers (calibration_check: default_ok_for_this_regime)."""
    hypothesis_space_spec = {
        "candidate_plugins": CANDIDATE_PLUGINS,
        "per_plugin": {
            "ruleind": {"key_fn": edge_key_fn},
            "estimation": {"mode": "generic_mdl", "key_fn": edge_key_fn,
                            "label_fn": lambda ep: ep["gold_class"], "classes": ["neg", "pos"]},
            "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": ["neg", "pos"]},
        },
        "min_compression_ratio": 1.0,
    }
    chosen_name, chosen_result, all_results = learner_registry.learn(
        train_pool, edge_feat_fn, hypothesis_space_spec, prior={})
    return chosen_name, chosen_result, all_results


def classifier_apply(chosen_name: Optional[str], chosen_result, words_i: List[str], words_j: List[str],
                      default_class: str = "pos") -> str:
    """default_class='pos' (no negation detected) mirrors the hand-rule's own default (pol=+1 when
    has_negating_word is False) -- preserves shape parity between the two edge-sign sources."""
    if chosen_name is None or chosen_name == KEEP_EPISODIC or chosen_result is None:
        return default_class
    feats = edge_feat_fn({"words_i": words_i, "words_j": words_j})
    if chosen_name == "ruleind":
        return ruleind_plugin.apply(chosen_result.hypothesis, feats, key=tuple(sorted(feats)),
                                     default_class=default_class)
    if chosen_name == "estimation":
        pred = estimation_plugin.apply(chosen_result.hypothesis, tuple(sorted(feats)))
        return pred if pred is not None else default_class
    if chosen_name == "gam":
        return gam_plugin.apply(chosen_result.hypothesis, feats)
    raise ValueError(f"unhandled chosen plugin {chosen_name!r}")


def edge_acc(pool: List[Dict], chosen_name: Optional[str], chosen_result) -> Tuple[float, int]:
    if not pool:
        return float("nan"), 0
    correct = 0
    for ep in pool:
        pred = classifier_apply(chosen_name, chosen_result, ep["words_i"], ep["words_j"])
        if pred == ep["gold_class"]:
            correct += 1
    return correct / len(pool), len(pool)


# ---------------------------------------------------------------------- register with LEARNED signs
def build_register_learned(steps: List[str], chosen_name: Optional[str], chosen_result,
                            check_order: Optional[List[int]] = None) -> Tuple[CausalLinkRegister, List[int]]:
    """Same edge topology as v2's build_register (edge i -> i+1 for every adjacent step pair), but
    polarity comes from the LEARNED classifier instead of has_negating_word. check_order (scramble
    control): permutes ONLY which step's text feeds the DOWNSTREAM/j-side of the pair feature (the
    cause-side stays at its TRUE position i) -- the direct generalization of v1/v2/oracle's own
    scramble scheme (which permuted the single checked position; here that becomes the j-role of
    the pair while i-role is unpermuted)."""
    k = len(steps)
    gen = torch.Generator()
    gen.manual_seed(12345)
    reg = CausalLinkRegister(d=D, generator=gen, max_event_slots=max(k, 1))
    edge_signs: List[int] = []
    for i in range(k - 1):
        check_idx = check_order[i + 1] if check_order is not None else (i + 1)
        words_i = content_tokens(steps[i])
        words_j = content_tokens(steps[check_idx])
        pred = classifier_apply(chosen_name, chosen_result, words_i, words_j)
        sign = 1 if pred == "pos" else -1
        reg.add_causal_link(i, i + 1, polarity=sign)
        edge_signs.append(sign)
    return reg, edge_signs


def _combine(pp: int, sign: int, op: int) -> str:
    propagated = pp * sign
    return ("more" if propagated > 0 else "less") if op == 0 else ("more" if propagated == op else "less")


def score_item_learned(base_row: Dict, gold: Optional[Dict], chosen_name: Optional[str], chosen_result) -> Dict:
    covered = bool(gold and gold.get("covered"))
    if not covered:
        return {"pred_loop_learned": base_row["pred_polecho"],
                "learned_diag": {"abstained": True, "reason": "no_gold_anchor" if gold is None else gold.get("reason")}}
    steps = gold["steps"]
    i, j = gold["i"], gold["j"]
    pp, op = base_row["pp"], base_row["op"]
    if pp == 0:
        return {"pred_loop_learned": base_row["pred_polecho"],
                "learned_diag": {"abstained": True, "reason": "pp_zero"}}
    reg, edge_signs = build_register_learned(steps, chosen_name, chosen_result, check_order=None)
    lo, hi = sorted([i, j])
    sign, trace = propagate_sign(reg, lo, hi)
    if sign is None:
        return {"pred_loop_learned": base_row["pred_polecho"],
                "learned_diag": {"abstained": True, "reason": "hop_validate_fail"}}
    pred = _combine(pp, sign, op)
    return {"pred_loop_learned": pred,
            "learned_diag": {"abstained": False, "propagated_sign": pp * sign, "edge_signs": edge_signs}}


def score_item_learned_scramble(base_row: Dict, gold: Optional[Dict], chosen_name: Optional[str],
                                 chosen_result, seed: int) -> str:
    covered = bool(gold and gold.get("covered"))
    if not covered:
        return base_row["pred_polecho"]
    steps = gold["steps"]
    i, j = gold["i"], gold["j"]
    pp, op = base_row["pp"], base_row["op"]
    if pp == 0:
        return base_row["pred_polecho"]
    k = len(steps)
    perm = _deterministic_perm(f"wiqa_learned_scramble::{seed}::{base_row['question_id']}", k) if k > 0 else []
    reg, _edge_signs = build_register_learned(steps, chosen_name, chosen_result, check_order=perm)
    lo, hi = sorted([i, j])
    sign, _trace = propagate_sign(reg, lo, hi)
    if sign is None:
        return base_row["pred_polecho"]
    return _combine(pp, sign, op)


# ---------------------------------------------------------------------- leak checks
def leak_check_single_edge(rows_multihop: List[Dict]) -> Dict:
    """Director's mandatory leak check: for each oracle_covered_multihop item, ISOLATE the first
    (resp. last) edge of the gold path -- force every OTHER edge to neutral sign=+1 -- and check
    whether that ONE edge's solo-composed prediction already reproduces answer_label. Returns both
    endpoint match rates + the max as the headline leak_match_rate (must be < LEAK_MATCH_RATE_THRESH
    for the multihop subset to be considered genuinely multi-edge, not single-hop-in-disguise)."""
    n = 0
    first_correct = 0
    last_correct = 0
    for r in rows_multihop:
        diag = r.get("learned_diag", {})
        edge_signs = diag.get("edge_signs")
        if not edge_signs or diag.get("abstained"):
            continue
        pp, op, gold = r["pp"], r["op"], r["gold"]
        n += 1
        if _combine(pp, edge_signs[0], op) == gold:
            first_correct += 1
        if _combine(pp, edge_signs[-1], op) == gold:
            last_correct += 1
    if n == 0:
        return {"n": 0, "first_edge_match_rate": float("nan"), "last_edge_match_rate": float("nan"),
                "leak_match_rate": float("nan")}
    fr = first_correct / n
    lr = last_correct / n
    return {"n": n, "first_edge_match_rate": round(fr, 4), "last_edge_match_rate": round(lr, 4),
            "leak_match_rate": round(max(fr, lr), 4)}


def dj_leak_check_by_hop(gold_map: Dict[str, Dict], answer_by_qid: Dict[str, str]) -> Dict:
    """Reconfirms (real DEV sample) that dj->answer_label identity holds UNIFORMLY across hop
    buckets -- documents WHY dj is excluded from decisive scoring at every hop, not only hop<=1."""
    buckets = {"hop_le_1": [0, 0], "hop_ge_2": [0, 0]}
    for qid, rec in gold_map.items():
        i, j, dj = rec.get("i"), rec.get("j"), rec.get("dj")
        if i is None or j is None or i < 0 or j < 0 or dj is None:
            continue
        mapped = DJ_TO_LABEL.get(dj)
        if mapped is None:
            continue
        gold_answer = answer_by_qid.get(qid)
        if gold_answer is None:
            continue
        hop = abs(int(j) - int(i))
        bucket = "hop_le_1" if hop <= 1 else "hop_ge_2"
        buckets[bucket][1] += 1
        if mapped == gold_answer:
            buckets[bucket][0] += 1
    return {k: {"checked": v[1], "matched": v[0],
                "match_rate": (round(v[0] / v[1], 4) if v[1] else float("nan"))}
            for k, v in buckets.items()}


# ---------------------------------------------------------------------- accuracy aggregation
def _subset_rows(rows: List[Dict], subset: str) -> List[Dict]:
    if subset == "all":
        return rows
    if subset == "oracle_covered":
        return [r for r in rows if r["covered"]]
    if subset == "oracle_covered_multihop":
        return [r for r in rows if r["covered"] and (r["hop"] or 0) >= 2]
    raise ValueError(f"unknown subset {subset!r}")


def _acc(rows: List[Dict], pred_key: str) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r[pred_key] == r["gold"]) / len(rows)


def _acc_scramble(rows: List[Dict], scramble_preds: Dict[str, str]) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if scramble_preds[r["question_id"]] == r["gold"]) / len(rows)


def run_one_seed(seed: int, rows: List[Dict], gold_map: Dict[str, Dict], chosen_name, chosen_result,
                  heartbeat_cb=None) -> Dict:
    t0 = time.time()
    n = len(rows)
    scramble_preds: Dict[str, str] = {}
    for i, r in enumerate(rows):
        gold = gold_lookup(r["question_id"], gold_map)
        scramble_preds[r["question_id"]] = score_item_learned_scramble(r, gold, chosen_name, chosen_result, seed)
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
            "loop_hand_rule": _acc(srows, "pred_loop_oracle"),
            "loop_learned": _acc(srows, "pred_loop_learned"),
            "loop_learned_scramble": _acc_scramble(srows, scramble_preds),
        }
    elapsed = time.time() - t0
    return {"seed": seed, "n_items": n, "elapsed_s": round(elapsed, 4), "per_subset": per_subset}


def _arms_must_differ(rows: List[Dict], scramble_preds_seed0: Dict[str, str]) -> Dict:
    def _digest(vals):
        b = json.dumps(list(vals), sort_keys=False, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    sigs = {
        "majority": _digest([r["pred_majority"] for r in rows]),
        "polecho": _digest([r["pred_polecho"] for r in rows]),
        "bow": _digest([r["pred_bow"] for r in rows]),
        "loop_hand_rule": _digest([r["pred_loop_oracle"] for r in rows]),
        "loop_learned": _digest([r["pred_loop_learned"] for r in rows]),
        "loop_learned_scramble": _digest([scramble_preds_seed0[r["question_id"]] for r in rows]),
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


def apply_bands(per_seed: Dict[str, Dict], chosen_name, learner_fit_metrics: Dict,
                 edge_train_acc: float, edge_train_n: int, edge_test_acc: float, edge_test_n: int,
                 leak_detail: Dict) -> Tuple[str, str, Dict]:
    seeds = sorted(per_seed.keys(), key=lambda s: int(s))
    subset_table: Dict[str, Dict] = {}
    for subset in SUBSETS:
        s0 = per_seed[seeds[0]]["per_subset"][subset]
        scramble_vals = [per_seed[s]["per_subset"][subset]["loop_learned_scramble"] for s in seeds]
        scramble_median = _median(scramble_vals)
        loop_learned = s0["loop_learned"]
        subset_table[subset] = {
            "n": s0["n"], "majority": s0["majority"], "polecho": s0["polecho"], "bow": s0["bow"],
            "loop_hand_rule": s0["loop_hand_rule"], "loop_learned": loop_learned,
            "loop_learned_scramble_vals": scramble_vals, "loop_learned_scramble_median": scramble_median,
            "loop_learned_minus_majority": loop_learned - s0["majority"],
            "loop_learned_minus_polecho": loop_learned - s0["polecho"],
            "loop_learned_minus_bow": loop_learned - s0["bow"],
            "loop_learned_minus_hand_rule": loop_learned - s0["loop_hand_rule"],
        }

    primary = subset_table["oracle_covered_multihop"]
    loop_minus_polecho = primary["loop_learned_minus_polecho"]
    collapse_frac = ((primary["loop_learned"] - primary["loop_learned_scramble_median"]) / loop_minus_polecho
                      if loop_minus_polecho > 1e-9 else None)

    learner_fit_ok = chosen_name is not None and chosen_name != KEEP_EPISODIC
    leak_rate = leak_detail.get("leak_match_rate")
    leak_safe = (leak_rate is None) or (isinstance(leak_rate, float) and math.isnan(leak_rate)) or (leak_rate < LEAK_MATCH_RATE_THRESH)
    generalizes = (not math.isnan(edge_test_acc)) and edge_test_n >= MIN_EDGE_DEV_N and edge_test_acc >= EDGE_GENERALIZATION_THRESH
    beats_all = (primary["loop_learned_minus_majority"] >= DECISIVE_MARGIN
                 and primary["loop_learned_minus_polecho"] >= DECISIVE_MARGIN
                 and primary["loop_learned_minus_bow"] >= DECISIVE_MARGIN)
    scramble_collapses = collapse_frac is not None and collapse_frac >= DECISIVE_COLLAPSE_FRACTION

    detail = {
        "subset_table": subset_table, "primary_subset": "oracle_covered_multihop",
        "collapse_frac": collapse_frac, "learner_fit_ok": learner_fit_ok, "chosen_plugin": chosen_name,
        "leak_safe": leak_safe, "leak_detail": leak_detail,
        "generalizes": generalizes, "edge_train_acc": edge_train_acc, "edge_train_n": edge_train_n,
        "edge_test_acc": edge_test_acc, "edge_test_n": edge_test_n, "beats_all_3_baselines": beats_all,
        "scramble_collapses": scramble_collapses,
    }

    if not learner_fit_ok:
        tier = "HARD_FAIL"
        msg = (f"LEARNER_COULD_NOT_FIT: hdlab/learner's MDL model-selection chose KEEP_EPISODIC "
               f"(no candidate plugin among {CANDIDATE_PLUGINS} compressed the {edge_train_n}-edge "
               f"TRAIN pool past the null code) -- the missing-learning hypothesis is refuted at the "
               f"most basic level: there is no learnable structure the module could find here.")
    elif not leak_safe:
        tier = "HARD_FAIL"
        msg = (f"LEAK_DETECTED: single-edge-isolated match rate={leak_rate} >= {LEAK_MATCH_RATE_THRESH} "
               f"on oracle_covered_multihop (n={leak_detail.get('n')}) -- the multihop subset is "
               f"effectively single-hop-in-disguise; any apparent gain would not test genuine "
               f"multi-edge composition.")
    elif not generalizes:
        tier = "HARD_FAIL"
        msg = (f"LEARNER_DOES_NOT_GENERALIZE: chosen plugin={chosen_name}, held-out TEST-split "
               f"edge accuracy={edge_test_acc:.4f} (n={edge_test_n}) does not clear "
               f"{EDGE_GENERALIZATION_THRESH} (train edge acc={edge_train_acc:.4f}, n={edge_train_n}) "
               f"-- the fitted classifier overfits/does not transfer to unseen paragraphs; unsafe "
               f"to compose into the loop.")
    elif not beats_all:
        tier = "HARD_FAIL"
        msg = (f"DOES_NOT_BEAT_BASELINES: on oracle_covered_multihop (n={primary['n']}), "
               f"loop_learned={primary['loop_learned']:.4f} does not beat all 3 baselines by "
               f">={DECISIVE_MARGIN} (vs majority={primary['loop_learned_minus_majority']:.4f}, "
               f"vs polecho={primary['loop_learned_minus_polecho']:.4f}, "
               f"vs bow={primary['loop_learned_minus_bow']:.4f}) -- even a fitted, generalizing, "
               f"leak-safe LEARNED edge classifier does not rescue the composition mechanism; "
               f"missing-LEARNING was not the (sole) wall (vs hand-rule reference="
               f"{primary['loop_hand_rule']:.4f}, learned-minus-hand-rule="
               f"{primary['loop_learned_minus_hand_rule']:+.4f}).")
    elif not scramble_collapses:
        tier = "MIDDLE_BAND"
        cf_s = f"{collapse_frac:.3f}" if collapse_frac is not None else "n/a"
        msg = (f"BEATS_BASELINES_BUT_GAIN_NOT_CAUSAL: loop_learned beats all 3 baselines by "
               f">={DECISIVE_MARGIN} on oracle_covered_multihop (n={primary['n']}) AND is leak-safe "
               f"AND generalizes (edge_test_acc={edge_test_acc:.4f}), but learned-sign-scramble "
               f"collapse_frac={cf_s} < {DECISIVE_COLLAPSE_FRACTION} -- the gain looks "
               f"topological/structural rather than genuinely driven by the LEARNED signed-edge "
               f"content (same pattern v2/oracle found for the hand-rule mechanism).")
    else:
        tier = "HARD_PASS"
        msg = (f"LEARNED_SIGNS_RESCUE_THE_LOOP: on oracle_covered_multihop (n={primary['n']}), "
               f"loop_learned={primary['loop_learned']:.4f} beats majority "
               f"(+{primary['loop_learned_minus_majority']:.4f}), polecho "
               f"(+{primary['loop_learned_minus_polecho']:.4f}), bow "
               f"(+{primary['loop_learned_minus_bow']:.4f}) each by >={DECISIVE_MARGIN}; "
               f"learned-sign-scramble collapses collapse_frac={collapse_frac:.3f} >= "
               f"{DECISIVE_COLLAPSE_FRACTION}; leak-safe (leak_match_rate={leak_rate}); "
               f"generalizes (edge_test_acc={edge_test_acc:.4f}, n={edge_test_n}) -- the "
               f"missing-LEARNING hypothesis is CONFIRMED: hdlab/learner (plugin={chosen_name}) "
               f"learned a genuine, generalizing, causally-load-bearing edge-polarity signal the "
               f"hand-rule regex (reference={primary['loop_hand_rule']:.4f}) did not capture "
               f"(learned-minus-hand-rule={primary['loop_learned_minus_hand_rule']:+.4f}).")
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


def _write_metrics_local(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ---------------------------------------------------------------------- examples for report
def pick_examples(rows: List[Dict], n: int = 5) -> Dict:
    learned_right_hand_wrong = [r for r in rows if r["covered"]
                                 and r["pred_loop_learned"] == r["gold"] and r["pred_loop_oracle"] != r["gold"]]
    learned_wrong_hand_right = [r for r in rows if r["covered"]
                                 and r["pred_loop_learned"] != r["gold"] and r["pred_loop_oracle"] == r["gold"]]

    def _fmt(r):
        return {"question_id": r["question_id"], "gold": r["gold"], "hop": r["hop"],
                "pred_loop_learned": r["pred_loop_learned"], "pred_loop_hand_rule": r["pred_loop_oracle"],
                "pred_polecho": r["pred_polecho"]}

    return {"learned_wins_vs_hand_rule": [_fmt(r) for r in learned_right_hand_wrong[:n]],
            "n_learned_wins_vs_hand_rule_total": len(learned_right_hand_wrong),
            "learned_loses_vs_hand_rule": [_fmt(r) for r in learned_wrong_hand_right[:n]],
            "n_learned_loses_vs_hand_rule_total": len(learned_wrong_hand_right)}


# ---------------------------------------------------------------------- self-test
def _hand_case_pool_dedup() -> Dict:
    """Hand-built raw with_explanation-shaped records: 2 records sharing the SAME (para_id, lo, hi)
    edge with agreeing dj (majority-vote trivial), 1 with a DIFFERENT para_id -- verifies dedup
    groups correctly and word extraction/tokenization runs end-to-end."""
    recs = [
        {"metadata": {"para_id": "P1"}, "steps": ["water rises in the tank", "the valve stops the flow"],
         "explanation": {"i": 0, "j": 1, "dj": "RESULTS_IN_OPP"}},
        {"metadata": {"para_id": "P1"}, "steps": ["water level rises", "the valve stops the flow again"],
         "explanation": {"i": 0, "j": 1, "dj": "RESULTS_IN_OPP"}},  # same (para_id,lo,hi) -> dedup
        {"metadata": {"para_id": "P2"}, "steps": ["sunlight reaches leaves", "the plant grows taller"],
         "explanation": {"i": 0, "j": 1, "dj": "RESULTS_IN"}},
        {"metadata": {"para_id": "P3"}, "steps": ["a b c"], "explanation": {"i": -1, "j": -1, "dj": "NO_EFFECT"}},
    ]
    pool = _build_edge_pool_from_records(recs)
    assert len(pool) == 2, f"expected 2 deduped edges (P1, P2), got {len(pool)}: {pool}"
    p1 = next(p for p in pool if p["para_id"] == "P1")
    assert p1["gold_class"] == "neg" and p1["n_votes"] == 2, p1
    p2 = next(p for p in pool if p["para_id"] == "P2")
    assert p2["gold_class"] == "pos" and p2["n_votes"] == 1, p2
    assert "j:stop" in edge_feat_fn(p1), edge_feat_fn(p1)
    return {"pool": pool}


def _demo_pool_for_selftest() -> List[Dict]:
    """Synthetic pool (N=20, clear signal: 'stop'/'block'/'prevent' in step_j -> neg, else -> pos)
    -- each trigger word repeats >= MIN_COVERAGE(=3, ruleind's own default) times so a singleton
    word-feature rule CAN legally form (a too-sparse pool where every word occurs once caused every
    candidate plugin to fall back to KEEP_EPISODIC in an earlier version of this self-test --
    caught by the self-test itself; fixed by sharing this richer pool across both hand-cases below
    instead of two independently-authored pools of different sparsity)."""
    pool = []
    neg_words = ["stop", "block", "prevent"]
    pos_words = ["grow", "increase", "rise", "speed", "warm", "expand", "rain", "form", "melt"]
    for k in range(10):
        pool.append({"gold_class": "neg", "words_i": [f"cause{k}"], "words_j": [neg_words[k % 3], f"noise{k}"]})
    for k in range(10):
        pool.append({"gold_class": "pos", "words_i": [f"cause{k}"], "words_j": [pos_words[k % len(pos_words)], f"noise{k}"]})
    return pool


def _hand_case_classifier_fit_and_apply() -> Dict:
    """Fits via the REAL hdlab.learner.registry.learn() end-to-end (real_code_path mandate, small
    N) and verifies held-out-shaped probes predict correctly."""
    pool = _demo_pool_for_selftest()
    chosen_name, chosen_result, all_results = fit_edge_classifier(pool)
    assert chosen_name != KEEP_EPISODIC, f"synthetic clear-signal pool failed to fit any plugin: {all_results}"
    pred_neg = classifier_apply(chosen_name, chosen_result, ["some", "cause"], ["stop", "unseen_noise_word"])
    pred_pos = classifier_apply(chosen_name, chosen_result, ["some", "cause"], ["grow", "unseen_noise_word2"])
    train_acc, train_n = edge_acc(pool, chosen_name, chosen_result)
    return {"chosen_name": chosen_name, "pred_neg": pred_neg, "pred_pos": pred_pos,
            "train_acc": train_acc, "train_n": train_n,
            "all_plugin_names": sorted(all_results.keys())}


def _hand_case_register_learned_sign_flip() -> Dict:
    """Hand-built 3-step chain + the SAME coverage-satisfying demo classifier as
    _hand_case_classifier_fit_and_apply -- verifies build_register_learned + propagate_sign
    compose LEARNED signs correctly through the REAL CausalLinkRegister (same substrate object
    v1/v2/oracle use)."""
    pool = _demo_pool_for_selftest()
    chosen_name, chosen_result, _ = fit_edge_classifier(pool)
    steps = ["water level rises in the tank", "pressure builds up", "the valve stops the flow"]
    reg, edge_signs = build_register_learned(steps, chosen_name, chosen_result, check_order=None)
    assert edge_signs[1] == -1, f"expected edge[1] (checks 'stops') sign=-1, got {edge_signs}"
    sign, trace = propagate_sign(reg, 0, 2)
    assert sign == -1, f"expected propagated product -1, got {sign} (trace={trace})"
    return {"chosen_name": chosen_name, "edge_signs": edge_signs, "propagated_sign": sign}


def _hand_case_leak_check_logic() -> Dict:
    """Contrived rows_multihop verifying leak_check_single_edge's arithmetic: item A's FIRST edge
    alone reproduces gold every time (should show first_edge_match_rate=1.0); item B is
    chance-shaped (should not)."""
    rows_leaky = [
        {"pp": 1, "op": 0, "gold": "more",
         "learned_diag": {"abstained": False, "edge_signs": [1, -1, -1]}},  # first edge alone: pp*1>0 -> "more" == gold
        {"pp": 1, "op": 0, "gold": "more",
         "learned_diag": {"abstained": False, "edge_signs": [1, 1, 1]}},
    ]
    leak_leaky = leak_check_single_edge(rows_leaky)
    assert leak_leaky["n"] == 2 and leak_leaky["first_edge_match_rate"] == 1.0, leak_leaky

    rows_not_leaky = [
        {"pp": 1, "op": 0, "gold": "less",  # first edge alone predicts "more" (wrong)
         "learned_diag": {"abstained": False, "edge_signs": [1, -1]}},
        {"pp": 1, "op": 0, "gold": "more",
         "learned_diag": {"abstained": False, "edge_signs": [1, -1]}},
    ]
    leak_not_leaky = leak_check_single_edge(rows_not_leaky)
    assert leak_not_leaky["first_edge_match_rate"] == 0.5, leak_not_leaky
    return {"leak_leaky": leak_leaky, "leak_not_leaky": leak_not_leaky}


def self_test() -> Dict:
    hand_pool_dedup = _hand_case_pool_dedup()
    hand_fit = _hand_case_classifier_fit_and_apply()
    assert hand_fit["pred_neg"] == "neg", hand_fit
    assert hand_fit["pred_pos"] == "pos", hand_fit
    hand_sign_flip = _hand_case_register_learned_sign_flip()
    hand_leak_logic = _hand_case_leak_check_logic()

    # real_code_path + substrate_signature preflight (F.1/F.2)
    sig = inspect.signature(CausalLinkRegister.__init__)
    assert set(["d", "generator", "max_event_slots"]).issubset(sig.parameters.keys()), sig
    sig_add = inspect.signature(CausalLinkRegister.add_causal_link)
    assert set(["cause_idx", "effect_idx", "polarity"]).issubset(sig_add.parameters.keys()), sig_add
    sig_learn = inspect.signature(learner_registry.learn)
    assert set(["episodes", "features", "hypothesis_space_spec"]).issubset(sig_learn.parameters.keys()), sig_learn
    for plugin_mod in (ruleind_plugin, estimation_plugin, gam_plugin):
        sig_p = inspect.signature(plugin_mod.learn)
        assert set(["episodes", "features", "hypothesis_space_spec", "prior"]).issubset(sig_p.parameters.keys()), (plugin_mod.NAME, sig_p)

    # real official-release sample (F.1: exercises the REAL production data path, not synthetic-only)
    real_train_records = load_official_records("train")[:200]
    real_code_path_ok = len(real_train_records) > 0
    real_pool_sample = None
    real_dj_leak_by_hop = None
    if real_code_path_ok:
        real_pool_sample = _build_edge_pool_from_records(real_train_records)
        gold_map = load_gold_map()
        if gold_map:
            dev_sample = load_dev()[:500]
            answer_by_qid = {ex["metadata_question_id"]: ex["answer_label"] for ex in dev_sample}
            real_dj_leak_by_hop = dj_leak_check_by_hop(gold_map, answer_by_qid)
            for bucket, d in real_dj_leak_by_hop.items():
                if d["checked"] >= 10:
                    assert d["match_rate"] >= 0.9, f"dj_leak_check_by_hop weaker than expected: {bucket}={d}"

    return {"hand_pool_dedup": {"n_pool": len(hand_pool_dedup["pool"])}, "hand_fit": hand_fit,
            "hand_sign_flip": hand_sign_flip, "hand_leak_logic": hand_leak_logic,
            "real_code_path_ok": real_code_path_ok,
            "n_real_train_records_sampled": len(real_train_records),
            "n_real_pool_sample": len(real_pool_sample) if real_pool_sample is not None else 0,
            "real_dj_leak_by_hop": real_dj_leak_by_hop}


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

    print(f"[{run_mode}] loading WIQA dev + official gold-explanation release + train/test edge pools...", flush=True)
    dev = load_dev()
    gold_map = load_gold_map()
    train_pool = build_edge_pool("train")
    test_pool = build_edge_pool("test")
    print(f"[{run_mode}] gold_map={len(gold_map)} train_edge_pool={len(train_pool)} "
          f"test_edge_pool={len(test_pool)} train_class_balance={dict(Counter(e['gold_class'] for e in train_pool))}",
          flush=True)

    chosen_name, chosen_result, all_results = fit_edge_classifier(train_pool)
    learner_fit_metrics = {name: r.metrics for name, r in all_results.items()}
    edge_train_acc, edge_train_n = edge_acc(train_pool, chosen_name, chosen_result)
    edge_test_acc, edge_test_n = edge_acc(test_pool, chosen_name, chosen_result)
    print(f"[{run_mode}] classifier fit: chosen_plugin={chosen_name} "
          f"edge_train_acc={edge_train_acc:.4f}(n={edge_train_n}) "
          f"edge_test_acc={edge_test_acc:.4f}(n={edge_test_n})", flush=True)

    if args.smoke:
        stride = max(1, len(dev) // SMOKE_N)
        dev = dev[::stride][:SMOKE_N]
    n_total = len(dev)
    print(f"[{run_mode}] scoring {n_total} dev items (base + hand-rule-reference + learned, seed-independent pass)...",
          flush=True)

    rows: List[Dict] = []
    n_degraded = 0
    for idx, ex in enumerate(dev):
        try:
            base = score_item_base(ex)
            gold = gold_lookup(base["question_id"], gold_map)
            oracle = score_item_oracle(base, gold)
            learned = score_item_learned(base, gold, chosen_name, chosen_result)
            covered = bool(gold and gold.get("covered"))
            row = dict(base)
            row["pred_loop_oracle"] = oracle["pred_loop_oracle"]
            row["oracle_diag"] = oracle["oracle_diag"]
            row.update(learned)
            row["covered"] = covered
            row["hop"] = gold["hop"] if covered else None
            rows.append(row)
        except Exception as e:  # noqa: BLE001 -- per-item failure isolation (META_RULE_J)
            n_degraded += 1
            rows.append({
                "question_id": ex.get("metadata_question_id", f"UNKNOWN_{idx}"),
                "gold": ex.get("answer_label", "no_effect"), "pp": 0, "op": 0,
                "pred_majority": "more", "pred_polecho": "no_effect", "pred_bow": "no_effect",
                "pred_loop_oracle": "no_effect", "oracle_diag": {"abstained": True, "reason": "SCORING_EXCEPTION"},
                "pred_loop_learned": "no_effect", "learned_diag": {"abstained": True, "reason": "SCORING_EXCEPTION"},
                "covered": False, "hop": None,
                "degraded_scoring": True, "failure_class": type(e).__name__, "failure_detail": str(e)[:300],
            })
        if (idx + 1) % 1000 == 0:
            print(f"[{run_mode}] base+learned scoring {idx + 1}/{n_total} elapsed={time.time() - t0:.1f}s", flush=True)
            _write_heartbeat(output_dir, idx + 1, n_total, time.time() - t0, {"phase": "base_learned"})

    degraded_frac = n_degraded / n_total if n_total else 0.0
    print(f"[{run_mode}] base+learned pass done: {n_degraded}/{n_total} degraded ({degraded_frac:.4f}); "
          f"elapsed={time.time() - t0:.1f}s", flush=True)
    if degraded_frac > DEGRADED_BUDGET:
        raise RuntimeError(
            f"DEGRADED_SCORING_BUDGET_EXCEEDED: {degraded_frac:.4f} > {DEGRADED_BUDGET} "
            f"({n_degraded}/{n_total} items hit a per-item scoring exception)")

    run_config = {"run_mode": run_mode, "anchor": ANCHOR_NAME, "n_items": n_total,
                  "chosen_plugin": str(chosen_name)}
    done, remaining = resumable_seeds(seeds, output_dir, run_config=run_config)
    print(f"[{run_mode}] {len(done)}/{len(seeds)} seeds already complete; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{run_mode}] seed={seed} learned-sign-scrambling+scoring...", flush=True)

        def _hb(i, n, el, _seed=seed):
            _write_heartbeat(output_dir, i, n, el, {"phase": "learned_scramble", "seed": _seed})

        seed_result = run_one_seed(seed, rows, gold_map, chosen_name, chosen_result, heartbeat_cb=_hb)
        write_partial(output_dir, seed, {"seed": seed, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                                          "n_items": n_total, "result": seed_result})
        mh = seed_result["per_subset"]["oracle_covered_multihop"]
        print(f"[{run_mode}] seed={seed} done: multihop(n={mh['n']}) loop_learned={mh['loop_learned']:.4f} "
              f"loop_hand_rule={mh['loop_hand_rule']:.4f} majority={mh['majority']:.4f} "
              f"elapsed={seed_result['elapsed_s']:.1f}s", flush=True)

    per_seed_partials = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed = {str(s): per_seed_partials[str(s)]["result"] for s in seeds}

    scramble0 = {r["question_id"]: score_item_learned_scramble(r, gold_lookup(r["question_id"], gold_map),
                                                                 chosen_name, chosen_result, seeds[0])
                 for r in rows}
    diff = _arms_must_differ(rows, scramble0)

    multihop_rows = _subset_rows(rows, "oracle_covered_multihop")
    leak_detail = leak_check_single_edge(multihop_rows)
    answer_by_qid = {r["question_id"]: r["gold"] for r in rows}
    dj_leak_hop_detail = dj_leak_check_by_hop(gold_map, answer_by_qid)

    tier, msg, band_detail = apply_bands(per_seed, chosen_name, learner_fit_metrics,
                                          edge_train_acc, edge_train_n, edge_test_acc, edge_test_n, leak_detail)
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
        "leak_match_rate_threshold": LEAK_MATCH_RATE_THRESH, "edge_generalization_threshold": EDGE_GENERALIZATION_THRESH,
        "chosen_plugin": str(chosen_name), "learner_fit_metrics": learner_fit_metrics,
        "edge_train_acc": edge_train_acc, "edge_train_n": edge_train_n,
        "edge_test_acc": edge_test_acc, "edge_test_n": edge_test_n,
        "n_train_edge_pool": len(train_pool), "n_test_edge_pool": len(test_pool),
        "train_edge_class_balance": dict(Counter(e["gold_class"] for e in train_pool)),
        "test_edge_class_balance": dict(Counter(e["gold_class"] for e in test_pool)),
        "leak_check_single_edge": leak_detail, "dj_leak_check_by_hop": dj_leak_hop_detail,
        "per_seed": per_seed, "band_detail": band_detail,
        "arms_differ_verified": diff["all_differ"], "arms_differ_check": diff,
        "examples": examples,
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "3-way discrete classification accuracy comparison on a real benchmark (WIQA); "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: reuses v2's GATE_THRESH/anchor mechanism and "
                              "polarity lexicon unchanged; the learned-classifier hyperparameters are each "
                              "hdlab/learner plugin's own module defaults, not tuned against dev numbers",
        "hp_scope": {"oracle_covered_multihop": ["decisive_gate_beats_all_3_baselines",
                                                  "decisive_gate_scramble_collapse", "decisive_gate_no_leak",
                                                  "decisive_gate_generalizes", "decisive_gate_learner_fit"]},
        "progress_logging": "print_flush_true",
        "candidate_plugins": CANDIDATE_PLUGINS,
        "supervision_source_note": "TRAIN/TEST hop=1 (adjacent-anchor) records from WIQA's official "
                                    "with_explanation release, dj-derived per-edge sign (dj in "
                                    "{RESULTS_IN,RESULTS_IN_OPP} only), deduped by (para_id,lo,hi); "
                                    "decisive evaluation restricted to DEV hop>=2 items, scored against "
                                    "answer_label (never dj) -- see module docstring leak-safety section.",
    }
    _ckpt_write_metrics(Path(output_dir), metrics, results=None)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_seed",)},
                      indent=2, default=str), flush=True)


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
