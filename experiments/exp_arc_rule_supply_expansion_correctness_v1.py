"""ARC rule-supply expansion -> CORRECTNESS (not just coverage), selectively (v1).

QUESTION (one variable = the RULE SET; reasoner / link / CI / do / decision identical across arms):
  Does adding the 20 VETTED GENERAL science rules (data/rules/arc_science_typed_rules_v2_expansion.json)
  to the base 233 (data/rules/arc_science_typed_rules_v1.json) raise the number of CORRECT ARC-Challenge
  answers the composed DerivationReasoner (hdlab/reasoner.py) derives -- WITHOUT becoming promiscuous
  (helping distractors derive)? The coverage gap is 60.5% genuine rule-graph gaps (STRUCTURALLY_ABSENT
  bucket = 69/114 dist_only, VET-confirmed @ data/exp_arc_reasoner_sr_gated_tiebreak_v1/metrics.json).

REUSE (do NOT rebuild): hdlab.reasoner.DerivationReasoner (build one instance per RULE SET, passing rows=;
  ONE shared SemanticHDEncoder so GloVe stays cached across arms). The bucket classifier + coverage
  diagnostic shape is REPRODUCED from experiments/exp_arc_reasoner_sr_gated_tiebreak_v1.py (same
  gold_only / dist_only / tie / not_derived buckets; same LINK_FAILURE / DEPTH_BLOCKED / STRUCTURALLY_ABSENT
  3-way; DEPTH_BUMP=6). Adding rules is MONOTONE (more edges -> only more derivable), so BASE->EXPANSION
  bucket moves are one-directional and map cleanly to "newly-derived" decomposition.

ARMS (rule sets):
  BASE            -- 233 v1 rules (Gate-D positive control: MUST reproduce prior buckets exactly:
                     lemma_syn gold_only/dist_only/tie = 26/114/66 ; lemma = 16/69/44).
  EXPANSION       -- 233 + 20 = 253 rules (the lever under test).
  SCRAMBLE_PAIR   -- must-fail #1: 233 + the 20 with arg1 fillers PERMUTED across the 20 (seeded derangement).
                     SAME vocabulary, SAME relations, SAME degree (+20 edges) -> destroys the KNOWLEDGE
                     (which concept relates to which) while preserving graph density. If it lifts as much
                     as EXPANSION, the "gain" is graph-density artifact, not knowledge.
  FLIP_DIR        -- must-fail #2: 233 + the 20 with arg0<->arg1 swapped (direction reversed). meet_connected
                     is direction-sensitive; a reversed causal edge should not bridge given->gold.

PRIMARY METRIC (the honest lever value):
  target bucket = the STRUCTURALLY_ABSENT questions under BASE (gold-answer nodes exist but no path connects
    givens to gold at depth<=6; base typed-accuracy on them is ~0 by construction -- gold cannot be picked
    by derivation because it is not derivable). accuracy_delta = EXPANSION typed-acc(target) - BASE typed-acc.
  Newly-gold-derivable decomposition (gold derivable in EXPANSION but NOT in BASE), classified by EXPANSION
    bucket: gold_only = CLEAN WIN (~1.0) ; tie = MEANING-BOUND (~0.36 pick rate). Honest lever value =
    clean-win + tie-level gain MINUS any new dist_only / gold_only->tie promiscuity harm.

SELECTIVITY GATE (load-bearing, the 29559 promiscuity failure mode): candidate-level distractor-derive rate
  (# derivable distractor candidates / # distractor candidates, over all 1172 Qs) with EXPANSION must stay
  <= BASE + SEL_TOL. Per-rule attribution: for each of the 20 new rules, how many DISTRACTOR candidates its
  edge helps derive (chain-reconstruction label match) -- hub concepts (energy / oxygen / force) are the risk.

MUST-FAIL: SCRAMBLE_PAIR + FLIP_DIR target-bucket lift must COLLAPSE (<= SCRAMBLE_MAX and clearly below the
  real lift). If a scramble helps as much as real -> the gain is density/direction artifact, HARD_FAIL.

POSITIVE CONTROL: BASE reproduces prior buckets exactly (26/114/66 lemma_syn; 16/69/44 lemma).

BANDS:
  HARD_PASS  : target-bucket accuracy rises (real_lift >= LIFT_MIN) AND selectivity held (dist-derive <= base
               + SEL_TOL) AND scramble collapses (both scramble lifts <= SCRAMBLE_MAX AND real_lift beats the
               max scramble lift by >= LIFT_OVER_SCRAMBLE) AND positive control reproduced.
  HONEST_NEG : rules add only ties / promiscuity with no net correct-lift (real_lift < LIFT_MIN), OR
               distractor-derive rises above base (promiscuous) = the known coverage-not-correctness wall.
  INCONCLUSIVE: positive control drift (BASE buckets != anchor) OR scramble artifact (scramble lift ~ real).
  Honest expectation: MODEST -- newly-derivable golds often become meaning-bound TIES the thin-cosine
  combiner cannot resolve; the DIAGNOSTIC (clean-win vs tie-conversion vs promiscuity) is the real deliverable.

## Compute architecture
class: (b) sequential-CPU with justification. Dominant cost = the real DerivationReasoner eval over 1172 ARC
  questions x candidates (nodes_for + meet_connected) per RULE SET -- a per-question CPU loop over a ~230-node
  graph; GPU buys nothing at n~230. ONE shared SemanticHDEncoder keeps GloVe fused vectors cached across all
  arms (the encode is the only non-trivial cost; graph BFS is microseconds). Storage: no_storage (glass-box
  symbolic graph; no HD bundle). device: cpu (numpy only).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): BASE / EXPANSION / SCRAMBLE_PAIR / FLIP_DIR produce
#   DISTINCT derivable-sets on the planted question set (rule sets genuinely differ).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: base target-bucket acc = 0.0 (MEASURED floor: gold not derivable -> cannot be
#   picked). Ceiling on the 69 target Qs = fraction whose gold becomes derivable x (1.0 clean-win | ~0.36
#   tie). crlb_n/a: no closed-form noise floor -- discriminator is a discrete derive/decide, not an estimate.
# - baseline_in_band: BASE whole-set typed-acc in (0.05, 0.95) (prior ~0.20); target-bucket base acc = 0 is
#   the DELIBERATE floor (the lever must move it up), reported honestly, not a saturation flag.
# - discriminator survives scale: buckets only fully populate at FULL N=1172; smoke reports partial buckets
#   as preview; the planted self-test fires expansion-lift + scramble-collapse deterministically (GloVe-free).
# - HARD_PASS strictly above floor: real_lift >= LIFT_MIN (categorical margin over base 0.0) + beats scramble.
# - HP_SCOPE: lift+selectivity gates apply to EXPANSION only. BASE = positive-control reproduction (must repro
#   anchor buckets); SCRAMBLE_PAIR + FLIP_DIR = must-fail controls (must collapse).
# - cardinality: buckets per (ruleset, link_mode) sum to 1172; asserted.
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: default_ok_for_this_regime -- reasoner thresholds (tau_unify/tau_sim/depth) inherited
#   UNCHANGED from hdlab.reasoner; NOTHING tuned here; only the rule SET varies. Bands pre-registered.
# - deterministic_seeding: fixed int seed; scramble permutations via seeded default_rng + sorted; NO hash()
#   seeds; NO list(set()) ordering.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the report.
# - progress_logging: print_flush_true (line-buffered stdout; per-config / per-stage flush prints; heartbeat).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic; repo
.venv. Agent-reported VET-PENDING; NO atom banking (skunkworks VETs).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner  # noqa: E402
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate  # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc  # noqa: E402
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean  # noqa: E402

ANCHOR_NAME = "arc_rule_supply_expansion_correctness_v1"
SEED = 20260726

BASE_RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")
EXPANSION_RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v2_expansion.json")

DEPTH_BUMP = 6                    # coverage-diagnostic depth for STRUCTURALLY_ABSENT classification

# ---- pre-registered bands (NOT tuned; rule SET is the only variable) ----
LIFT_MIN = 0.05                  # min target-bucket accuracy rise for EXPANSION to count as a real lift
SEL_TOL = 0.005                  # distractor-derive rate may rise at most this much above BASE (selectivity)
SCRAMBLE_MAX = 0.02              # a scramble arm's target-bucket lift must stay <= this (collapse)
LIFT_OVER_SCRAMBLE = 0.03        # real lift must beat the max scramble lift by >= this margin

# ---- Gate-D positive-control anchors (MEASURED@exp_arc_reasoner_sr_gated_tiebreak_v1/metrics.json) ----
REPRO_BUCKETS = {"lemma_syn": {"gold_only": 26, "dist_only": 114, "tie": 66},
                 "lemma": {"gold_only": 16, "dist_only": 69, "tie": 44}}

# arm (rule set) names
BASE = "BASE"
EXPANSION = "EXPANSION"
SCRAMBLE_PAIR = "SCRAMBLE_PAIR"
FLIP_DIR = "FLIP_DIR"
ALL_ARMS = [BASE, EXPANSION, SCRAMBLE_PAIR, FLIP_DIR]

_T0 = [time.perf_counter()]


def _log(m: str) -> None:
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x) -> str:
    if x is None:
        return "None"
    if isinstance(x, float):
        return "nan" if x != x else ("%.4f" % x)
    return str(x)


# ===========================================================================
# rule loading + scramble construction
# ===========================================================================
def _norm_rule(r: dict) -> dict:
    """Keep ONLY the (relation, arg0, arg1) the graph builder consumes (strip targets_qid / textbook_fact)."""
    return {"relation": r["relation"], "arg0": r["arg0"], "arg1": r["arg1"]}


def _load_rules(path: str) -> List[dict]:
    d = json.load(open(path, "r", encoding="utf-8"))
    rows = d.get("rules", d.get("rows"))
    if not rows:
        raise ValueError("no 'rules'/'rows' key in %s; keys=%s" % (path, list(d.keys())))
    for r in rows:
        if not all(k in r for k in ("relation", "arg0", "arg1")):
            raise ValueError("malformed rule row: %s" % r)
    return rows


def _load_expansion_raw(path: str) -> List[dict]:
    """Load the 20 expansion rules WITH their metadata (targets_qid) for the attribution split."""
    d = json.load(open(path, "r", encoding="utf-8"))
    return d["rules"]


def _derange_arg1(rules: List[dict], rng: np.random.Generator) -> List[dict]:
    """Permute arg1 fillers across the rules with NO fixed point (seeded derangement). Preserves vocabulary,
    relations, and degree; destroys the concept pairing (knowledge)."""
    n = len(rules)
    arg1s = [r["arg1"] for r in rules]
    idx = list(range(n))
    for _attempt in range(1000):
        perm = rng.permutation(n).tolist()
        if all(perm[i] != i or arg1s[perm[i]] != arg1s[i] for i in idx):
            # accept if no rule keeps its ORIGINAL arg1 string (handles duplicate fillers)
            if all(arg1s[perm[i]] != arg1s[i] for i in idx):
                break
    out = []
    for i, r in enumerate(rules):
        out.append({"relation": r["relation"], "arg0": r["arg0"], "arg1": arg1s[perm[i]]})
    return out


def _flip_dir(rules: List[dict]) -> List[dict]:
    """Swap arg0<->arg1 (reverse the directed edge)."""
    return [{"relation": r["relation"], "arg0": r["arg1"], "arg1": r["arg0"]} for r in rules]


def build_rulesets(seed: int) -> Dict[str, List[dict]]:
    base = [_norm_rule(r) for r in _load_rules(BASE_RULES_PATH)]
    exp_raw = _load_expansion_raw(EXPANSION_RULES_PATH)
    exp = [_norm_rule(r) for r in exp_raw]
    rng = np.random.default_rng(seed * 17 + 3)
    scr = _derange_arg1(exp, rng)
    flp = _flip_dir(exp)
    return {
        BASE: base,
        EXPANSION: base + exp,
        SCRAMBLE_PAIR: base + scr,
        FLIP_DIR: base + flp,
    }, exp_raw


# ===========================================================================
# per-question bucketing + typed decision, over one reasoner (one rule set + link mode)
# ===========================================================================
def bucket_eval(reasoner: DerivationReasoner, questions: List[dict], link_mode: str,
                output_dir: str, tag: str) -> dict:
    reasoner.link_mode = link_mode
    typed = reasoner.arms["typed"]
    fwd, bwd = typed["fwd"], typed["bwd"]

    buckets = {"gold_only": 0, "dist_only": 0, "tie": 0, "not_derived": 0}
    per_q: List[dict] = []
    n = len(questions)
    n_typed_correct = 0
    n_covered = 0
    n_covered_correct = 0
    n_dist_cand_total = 0
    n_dist_cand_derivable = 0

    dist_only_qs: List[int] = []

    for qi, q in enumerate(questions):
        ci_gold = q["correct_index"]
        res = reasoner._reason_arm(q, typed)
        pc = res["per_choice"]
        chosen = res["chosen_index"]
        mode = res["decision_mode"]
        derivable_idx = set(c["choice_index"] for c in pc if c["derivable"] and not c["rejected_by_ci"])
        gold_derivable = ci_gold in derivable_idx
        dist_derivable_idx = sorted(i for i in derivable_idx if i != ci_gold)
        dist_derivable = len(dist_derivable_idx) > 0

        n_choices = len(q["choices"])
        n_dist_cand_total += (n_choices - 1)                       # all non-gold candidates
        n_dist_cand_derivable += len(dist_derivable_idx)

        if gold_derivable and dist_derivable:
            bucket = "tie"
        elif gold_derivable and not dist_derivable:
            bucket = "gold_only"
        elif dist_derivable and not gold_derivable:
            bucket = "dist_only"
            dist_only_qs.append(qi)
        else:
            bucket = "not_derived"
        buckets[bucket] += 1

        typed_correct = int(chosen == ci_gold)
        n_typed_correct += typed_correct
        any_derivable = (len(derivable_idx) > 0)
        if any_derivable:
            n_covered += 1
            n_covered_correct += typed_correct

        per_q.append({
            "qid": q["qid"], "correct_index": ci_gold, "chosen": chosen, "mode": mode,
            "typed_correct": typed_correct, "bucket": bucket,
            "gold_derivable": bool(gold_derivable),
            "dist_derivable_idx": dist_derivable_idx,
            "any_derivable": bool(any_derivable),
        })
        if (qi + 1) % 300 == 0:
            _log("  [%s/%s] bucketed %d/%d gold_only=%d dist_only=%d tie=%d" % (
                tag, link_mode, qi + 1, n, buckets["gold_only"], buckets["dist_only"], buckets["tie"]))

    # coverage diagnostic on dist_only: WHY does gold fail?  (LINK / DEPTH_BLOCKED / STRUCTURALLY_ABSENT)
    cov = {"LINK_FAILURE": 0, "DEPTH_BLOCKED": 0, "STRUCTURALLY_ABSENT": 0}
    struct_absent_qids: List[str] = []
    for qi in dist_only_qs:
        q = questions[qi]
        given_nodes = reasoner.nodes_for(q["stem"])
        gold_nodes = reasoner.nodes_for(q["choices"][q["correct_index"]])
        if not gold_nodes:
            cov["LINK_FAILURE"] += 1
        elif gate.meet_connected(fwd, bwd, given_nodes, gold_nodes, DEPTH_BUMP, min_len=1):
            cov["DEPTH_BLOCKED"] += 1
        else:
            cov["STRUCTURALLY_ABSENT"] += 1
            struct_absent_qids.append(q["qid"])

    dist_derive_rate = (n_dist_cand_derivable / n_dist_cand_total) if n_dist_cand_total else 0.0
    return {
        "link_mode": link_mode, "n_questions": n, "buckets": buckets,
        "typed_acc": round(n_typed_correct / n, 6) if n else 0.0,
        "n_typed_correct": n_typed_correct,
        "covered_subset": {"n": n_covered, "acc": round(n_covered_correct / n_covered, 6) if n_covered else 0.0},
        "distractor_derive_rate": round(dist_derive_rate, 6),
        "n_dist_cand_total": n_dist_cand_total, "n_dist_cand_derivable": n_dist_cand_derivable,
        "coverage_diagnostic": {"counts": cov, "n_dist_only": len(dist_only_qs)},
        "struct_absent_qids": struct_absent_qids,
        "per_q": per_q,
    }


# ===========================================================================
# per-rule attribution: which new rules help DISTRACTORS derive (selectivity), and which help GOLD.
# Chain-reconstruction label-match: reconstruct the derivation chain for each newly-derivable candidate and
# check which new-rule (arg0, rel, arg1) triples appear as steps. Best-effort + attribution-coverage reported.
# ===========================================================================
def _norm(s: str) -> str:
    return " ".join(str(s).lower().split())


def attribute_new_rules(reasoner_exp: DerivationReasoner, questions: List[dict],
                        base_per_q: List[dict], exp_per_q: List[dict],
                        exp_raw: List[dict], link_mode: str) -> dict:
    """For each newly-derivable candidate (gold or distractor) in EXPANSION vs BASE, reconstruct the chain
    and attribute traversed NEW-rule edges. Returns per-rule distractor-help + gold-help counts."""
    reasoner_exp.link_mode = link_mode
    typed = reasoner_exp.arms["typed"]
    g_shim = {"fwd": typed["fwd"], "bwd": typed["bwd"], "edge_rel": typed["edge_rel"],
              "node_label": reasoner_exp.g["node_label"], "node_rep": reasoner_exp.g["node_rep"]}
    depth = reasoner_exp.depth

    new_triples = {}
    for ri, r in enumerate(exp_raw):
        key = (_norm(r["arg0"]), r["relation"], _norm(r["arg1"]))
        new_triples.setdefault(key, []).append(ri)

    per_rule = [{"rule_index": ri,
                 "rule": "%s --%s--> %s" % (r["arg0"], r["relation"], r["arg1"]),
                 "targets_qid": r.get("targets_qid", []),
                 "dist_help": 0, "gold_help": 0, "questions_dist": [], "questions_gold": []}
                for ri, r in enumerate(exp_raw)]

    base_by_qid = {p["qid"]: p for p in base_per_q}
    n_dist_new = 0
    n_dist_attributed = 0
    n_gold_new = 0
    n_gold_attributed = 0

    for exp_p in exp_per_q:
        qid = exp_p["qid"]
        base_p = base_by_qid.get(qid)
        if base_p is None:
            continue
        q = next(qq for qq in questions if qq["qid"] == qid)
        given_nodes = reasoner_exp.nodes_for(q["stem"])
        base_dist = set(base_p["dist_derivable_idx"])
        exp_dist = set(exp_p["dist_derivable_idx"])
        newly_dist = sorted(exp_dist - base_dist)
        for ci in newly_dist:
            n_dist_new += 1
            cnodes = reasoner_exp.nodes_for(q["choices"][ci])
            chain = gate.reconstruct_chain(g_shim, given_nodes, cnodes, depth)
            _, steps = DerivationReasoner._parse_chain(chain)
            hit = False
            for (s, rel, d) in steps:
                key = (_norm(s), rel, _norm(d))
                if key in new_triples:
                    for ri in new_triples[key]:
                        per_rule[ri]["dist_help"] += 1
                        per_rule[ri]["questions_dist"].append(qid)
                    hit = True
            if hit:
                n_dist_attributed += 1
        # gold newly derivable
        if exp_p["gold_derivable"] and not base_p["gold_derivable"]:
            n_gold_new += 1
            cnodes = reasoner_exp.nodes_for(q["choices"][q["correct_index"]])
            chain = gate.reconstruct_chain(g_shim, given_nodes, cnodes, depth)
            _, steps = DerivationReasoner._parse_chain(chain)
            hit = False
            for (s, rel, d) in steps:
                key = (_norm(s), rel, _norm(d))
                if key in new_triples:
                    for ri in new_triples[key]:
                        per_rule[ri]["gold_help"] += 1
                        per_rule[ri]["questions_gold"].append(qid)
                    hit = True
            if hit:
                n_gold_attributed += 1

    for pr in per_rule:
        pr["questions_dist"] = sorted(set(pr["questions_dist"]))
        pr["questions_gold"] = sorted(set(pr["questions_gold"]))
    return {
        "per_rule": per_rule,
        "n_dist_newly_derivable": n_dist_new, "n_dist_attributed": n_dist_attributed,
        "n_gold_newly_derivable": n_gold_new, "n_gold_attributed": n_gold_attributed,
        "attribution_coverage_dist": round(n_dist_attributed / n_dist_new, 4) if n_dist_new else None,
        "attribution_coverage_gold": round(n_gold_attributed / n_gold_new, 4) if n_gold_new else None,
    }


# ===========================================================================
# BASE vs ARM comparison: target-bucket accuracy delta + newly-derived decomposition + promiscuity harm.
# ===========================================================================
def compare_to_base(base_res: dict, arm_res: dict, target_qids: List[str], exp_raw: List[dict]) -> dict:
    base_by = {p["qid"]: p for p in base_res["per_q"]}
    arm_by = {p["qid"]: p for p in arm_res["per_q"]}
    tset = set(target_qids)

    # target-bucket accuracy (the STRUCTURALLY_ABSENT-under-BASE questions)
    base_tc = sum(base_by[qid]["typed_correct"] for qid in target_qids)
    arm_tc = sum(arm_by[qid]["typed_correct"] for qid in target_qids)
    nT = max(1, len(target_qids))
    base_tacc = base_tc / nT
    arm_tacc = arm_tc / nT

    # newly-gold-derivable decomposition (gold derivable in ARM, not in BASE), by ARM bucket
    clean_win = {"n": 0, "correct": 0, "qids": []}     # -> gold_only in ARM
    tie_conv = {"n": 0, "correct": 0, "qids": []}      # -> tie in ARM
    for qid, bp in base_by.items():
        ap = arm_by[qid]
        if ap["gold_derivable"] and not bp["gold_derivable"]:
            if ap["bucket"] == "gold_only":
                clean_win["n"] += 1
                clean_win["correct"] += ap["typed_correct"]
                clean_win["qids"].append(qid)
            elif ap["bucket"] == "tie":
                tie_conv["n"] += 1
                tie_conv["correct"] += ap["typed_correct"]
                tie_conv["qids"].append(qid)

    # promiscuity harm: a DISTRACTOR became newly-derivable
    new_dist_only = {"n": 0, "qids": []}      # not_derived(base) -> dist_only(arm): pure promiscuity
    gold_only_eroded = {"n": 0, "flipped_wrong": 0, "qids": []}   # gold_only(base) -> tie(arm)
    net_correct_delta_on_promisc = 0
    for qid, bp in base_by.items():
        ap = arm_by[qid]
        base_dist = set(bp["dist_derivable_idx"])
        arm_dist = set(ap["dist_derivable_idx"])
        if arm_dist - base_dist:  # some distractor newly derivable
            net_correct_delta_on_promisc += (ap["typed_correct"] - bp["typed_correct"])
            if bp["bucket"] == "not_derived" and ap["bucket"] == "dist_only":
                new_dist_only["n"] += 1
                new_dist_only["qids"].append(qid)
            if bp["bucket"] == "gold_only" and ap["bucket"] == "tie":
                gold_only_eroded["n"] += 1
                gold_only_eroded["qids"].append(qid)
                if bp["typed_correct"] == 1 and ap["typed_correct"] == 0:
                    gold_only_eroded["flipped_wrong"] += 1

    # targeted vs non-targeted split of the newly-HELPED questions (gold newly derivable)
    targeted_qids = set()
    for r in exp_raw:
        for t in r.get("targets_qid", []):
            targeted_qids.add(t)
    newly_gold_qids = clean_win["qids"] + tie_conv["qids"]
    n_targeted = sum(1 for qid in newly_gold_qids if qid in targeted_qids)
    n_nontargeted = len(newly_gold_qids) - n_targeted

    return {
        "target_bucket_n": len(target_qids),
        "base_target_acc": round(base_tacc, 6), "arm_target_acc": round(arm_tacc, 6),
        "target_acc_delta": round(arm_tacc - base_tacc, 6),
        "base_target_correct": base_tc, "arm_target_correct": arm_tc,
        "newly_gold_derivable": {
            "clean_win": clean_win, "tie_conversion": tie_conv,
            "total": clean_win["n"] + tie_conv["n"],
            "correct_gained": clean_win["correct"] + tie_conv["correct"],
        },
        "promiscuity": {
            "new_dist_only": new_dist_only, "gold_only_eroded": gold_only_eroded,
            "net_correct_delta_on_promisc_questions": net_correct_delta_on_promisc,
        },
        "targeted_split": {"n_newly_gold": len(newly_gold_qids),
                           "n_targeted": n_targeted, "n_nontargeted": n_nontargeted,
                           "overfit_signal": "targeted_only" if (len(newly_gold_qids) > 0 and n_nontargeted == 0)
                           else ("general" if n_nontargeted > 0 else "none")},
        "whole_set_typed_acc_delta": round(arm_res["typed_acc"] - base_res["typed_acc"], 6),
        "distractor_derive_rate_base": base_res["distractor_derive_rate"],
        "distractor_derive_rate_arm": arm_res["distractor_derive_rate"],
        "distractor_derive_rate_delta": round(arm_res["distractor_derive_rate"]
                                              - base_res["distractor_derive_rate"], 6),
    }


# ===========================================================================
# verdict / bands (per link_mode, primary = lemma_syn)
# ===========================================================================
def verdict_for_config(link_mode: str, base_res: dict, arm_results: Dict[str, dict],
                       comparisons: Dict[str, dict]) -> dict:
    exp_cmp = comparisons[EXPANSION]
    real_lift = exp_cmp["target_acc_delta"]
    scr_lift = comparisons[SCRAMBLE_PAIR]["target_acc_delta"]
    flp_lift = comparisons[FLIP_DIR]["target_acc_delta"]
    max_scr = max(scr_lift, flp_lift)

    dr_base = base_res["distractor_derive_rate"]
    dr_exp = arm_results[EXPANSION]["distractor_derive_rate"]
    selectivity_held = bool(dr_exp <= dr_base + SEL_TOL)

    # positive control: BASE buckets reproduce the anchor exactly
    anchor = REPRO_BUCKETS.get(link_mode, {})
    repro_ok = all(base_res["buckets"].get(k) == v for k, v in anchor.items()) if anchor else True

    scramble_collapsed = bool(scr_lift <= SCRAMBLE_MAX and flp_lift <= SCRAMBLE_MAX)
    real_beats_scramble = bool(real_lift - max_scr >= LIFT_OVER_SCRAMBLE)
    real_lift_ok = bool(real_lift >= LIFT_MIN)

    scramble_artifact = bool(max_scr > SCRAMBLE_MAX and max_scr >= real_lift - 0.01)

    if not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_DRIFT"
    elif scramble_artifact:
        verdict = "INCONCLUSIVE_SCRAMBLE_ARTIFACT"
    elif real_lift_ok and selectivity_held and scramble_collapsed and real_beats_scramble:
        verdict = "HARD_PASS_RULE_SUPPLY_LIFTS_CORRECTNESS_SELECTIVELY"
    elif (not selectivity_held) or (real_lift < LIFT_MIN):
        verdict = "HONEST_NEG_COVERAGE_NOT_CORRECTNESS"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_LIFT"

    return {
        "link_mode": link_mode, "verdict": verdict,
        "real_lift": real_lift, "scramble_pair_lift": scr_lift, "flip_dir_lift": flp_lift,
        "max_scramble_lift": round(max_scr, 6),
        "distractor_derive_rate_base": dr_base, "distractor_derive_rate_expansion": dr_exp,
        "selectivity_held": selectivity_held, "repro_ok": repro_ok,
        "scramble_collapsed": scramble_collapsed, "real_beats_scramble": real_beats_scramble,
        "real_lift_ok": real_lift_ok,
    }


# ===========================================================================
# I/O helpers
# ===========================================================================
def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": round(time.perf_counter() - _T0[0], 1), "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir: str, stage: str, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    _log("hb %s %s" % (stage, extra if extra else ""))


# ===========================================================================
# self-test: planted rules; real DerivationReasoner (GloVe-free FakeBase). Expansion-lift fires; scramble
# collapses; attribution + bucketing exercised end-to-end.
# ===========================================================================
def _self_test() -> None:
    print("[self-test] rule-supply expansion mechanism (planted, GloVe-free) ...", flush=True)
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    base_enc = clean._FakeBase()
    wn = _load_wordnet()
    pol = PolarityLexicon()

    # BASE graph: rain->runoff->river (gold path exists); volcano->lava (distractor lure exists, disconnected
    #   from the 'metal' gold-question). A SECOND question's gold ('current'->'magnet') is DISCONNECTED in
    #   base (structurally absent) but the EXPANSION rule 'electricity CAUSE magnetism' bridges it.
    base_rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "runoff"},
        {"relation": "SOURCEOF", "arg0": "runoff", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
        {"relation": "CAUSE", "arg0": "electricity", "arg1": "current"},
    ]
    # EXPANSION new rule that bridges given(electricity/current) -> gold(magnetism): a REAL knowledge edge.
    exp_new = [{"relation": "CAUSE", "arg0": "current", "arg1": "magnetism",
                "targets_qid": ["Q_MAG"], "textbook_fact": "electric current causes magnetism"}]
    exp_rows = base_rows + [_norm_rule(r) for r in exp_new]

    def mk(rows, lm="lemma_syn"):
        return DerivationReasoner(base_encoder=base_enc, pol_lexicon=pol, wn=wn, tau_unify=0.99,
                                  tau_sim=0.5, depth=3, rows=rows, link_mode=lm, verbose=False)

    r_base = mk(base_rows)
    r_exp = mk(exp_rows)

    # a question whose gold ('magnetism') is UNREACHABLE in base but reachable in expansion; a distractor
    # ('lava') is reachable in neither from this given.
    q_mag = {"qid": "Q_MAG", "stem": "what does electric current cause",
             "choices": ["magnetism field", "lava rock", "metal wire", "glass sheet"], "correct_index": 0}
    res_b = r_base.reason(q_mag)
    res_e = r_exp.reason(q_mag)
    gold_deriv_base = res_b["per_choice"][0]["derivable"]
    gold_deriv_exp = res_e["per_choice"][0]["derivable"]
    assert not gold_deriv_base, "planted gold must be UNREACHABLE in base (structurally absent)"
    assert gold_deriv_exp, "expansion rule must bridge given->gold (lift fires)"
    # the LIFT proof: expansion now DERIVES the gold and picks it BY DERIVATION (not similarity fallback).
    assert res_e["chosen_index"] == 0, "expansion reasoner must now pick the derivable gold"
    assert res_e["decision_mode"] == "derivation", "expansion pick must be BY DERIVATION, mode=%s" % res_e["decision_mode"]
    print("[self-test] expansion lift fires: gold derivable base=%s exp=%s (exp mode=%s)"
          % (gold_deriv_base, gold_deriv_exp, res_e["decision_mode"]), flush=True)

    # SCRAMBLE (derange): permute arg1 across a multi-rule expansion so the bridge concept moves off-path.
    exp_multi = [
        {"relation": "CAUSE", "arg0": "current", "arg1": "magnetism"},
        {"relation": "CAUSE", "arg0": "sunlight", "arg1": "photosynthesis"},
        {"relation": "CAUSE", "arg0": "friction", "arg1": "heat"},
    ]
    rng = np.random.default_rng(7)
    scr = _derange_arg1(exp_multi, rng)
    for a, b in zip(exp_multi, scr):
        assert a["arg1"] != b["arg1"], "derangement must move every arg1 filler"
    r_scr = mk(base_rows + scr)
    res_s = r_scr.reason(q_mag)
    assert not res_s["per_choice"][0]["derivable"], "scrambled expansion must NOT bridge given->gold (collapse)"
    print("[self-test] scramble collapses: gold derivable under scramble=%s" % res_s["per_choice"][0]["derivable"],
          flush=True)

    # FLIP_DIR: reversed edge (magnetism->current) must not bridge given(current)->gold(magnetism) forward.
    flp = _flip_dir([{"relation": "CAUSE", "arg0": "current", "arg1": "magnetism"}])
    assert flp[0]["arg0"] == "magnetism" and flp[0]["arg1"] == "current", "flip must swap arg0<->arg1"

    # arms-differ: BASE / EXPANSION / SCRAMBLE / FLIP produce distinct derivable-sets on q_mag
    def dsig(r):
        res = r.reason(q_mag)
        vec = np.asarray([1 if c["derivable"] else 0 for c in res["per_choice"]], dtype=np.int64)
        return hashlib.sha256(vec.tobytes()).hexdigest()[:16]
    r_flp = mk(base_rows + flp)
    sigs = {BASE: dsig(r_base), EXPANSION: dsig(r_exp), SCRAMBLE_PAIR: dsig(r_scr), FLIP_DIR: dsig(r_flp)}
    assert sigs[BASE] != sigs[EXPANSION], "BASE and EXPANSION must differ (rule set changed derivability)"
    assert sigs[EXPANSION] != sigs[SCRAMBLE_PAIR], "EXPANSION and SCRAMBLE must differ"
    print("[self-test] arms-differ sigs=%s" % sigs, flush=True)

    # bucket_eval + compare_to_base + attribution end-to-end (real code path)
    out_dir = os.path.join(_REPO, "data", "_rule_supply_selftest_scratch")
    base_res = bucket_eval(r_base, [q_mag], "lemma_syn", out_dir, "BASE")
    exp_res = bucket_eval(r_exp, [q_mag], "lemma_syn", out_dir, "EXPANSION")
    assert sum(base_res["buckets"].values()) == 1, "buckets must sum to n_questions (cardinality)"
    # target bucket for the self-test = the qid whose gold was absent in base
    tgt = [q_mag["qid"]] if not base_res["per_q"][0]["gold_derivable"] else []
    cmp = compare_to_base(base_res, exp_res, tgt, exp_new)
    # gold newly-derivable and NO distractor derivable in expansion -> clean_win (gold_only) decomposition.
    assert cmp["newly_gold_derivable"]["clean_win"]["n"] == 1, \
        "planted newly-gold-derivable must classify as a clean_win (gold_only): %s" % cmp["newly_gold_derivable"]
    assert cmp["target_acc_delta"] >= 0.0, "target-bucket accuracy must not DROP under expansion (monotone)"
    attr = attribute_new_rules(r_exp, [q_mag], base_res["per_q"], exp_res["per_q"], exp_new, "lemma_syn")
    assert attr["n_gold_newly_derivable"] == 1, "one newly-gold-derivable question expected"
    assert sum(pr["gold_help"] for pr in attr["per_rule"]) >= 1, "the bridging new rule must get gold_help credit"
    print("[self-test] compare+attribute OK: clean_win=%d target_delta=%.3f gold_help=%s"
          % (cmp["newly_gold_derivable"]["clean_win"]["n"], cmp["target_acc_delta"],
             [pr["gold_help"] for pr in attr["per_rule"]]), flush=True)
    print("[self-test] ALL PASS", flush=True)


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, link_modes: List[str], arms: List[str], seed: int,
        run_mode: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, run_mode, len(link_modes) * len(arms))
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _log("run_mode=%s n_sample=%d link_modes=%s arms=%s" % (run_mode, n_sample, link_modes, arms))

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    rulesets, exp_raw = build_rulesets(seed)
    for a in arms:
        _log("ruleset %s: n_rules=%d" % (a, len(rulesets[a])))

    base_enc = SemanticHDEncoder()          # ONE shared encoder -> GloVe cached across all arms
    pol = PolarityLexicon()
    wn = base_enc._wn
    _heartbeat(output_dir, "encoder_ready", {"elapsed_s": round(time.perf_counter() - _T0[0], 1)})

    # build ONE reasoner per rule set (shared encoder/pol/wn); reused across link modes
    reasoners: Dict[str, DerivationReasoner] = {}
    for a in arms:
        t = time.perf_counter()
        reasoners[a] = DerivationReasoner(base_encoder=base_enc, pol_lexicon=pol, wn=wn, seed=seed,
                                          rows=rulesets[a], tiebreak_mode="legacy", verbose=False)
        g = reasoners[a].g
        _heartbeat(output_dir, "graph_built_%s" % a,
                   {"n_nodes": g["n_nodes"], "n_typed_edges": g["n_typed_edges"],
                    "mean_out_deg": round(g["n_typed_edges"] / max(1, g["n_nodes"]), 3),
                    "build_s": round(time.perf_counter() - t, 1)})

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_eval": len(questions)})

    per_config = {}
    verdicts = {}
    attributions = {}
    for lm in link_modes:
        arm_results: Dict[str, dict] = {}
        for a in arms:
            t = time.perf_counter()
            arm_results[a] = bucket_eval(reasoners[a], questions, lm, output_dir, a)
            _heartbeat(output_dir, "bucketed_%s_%s" % (a, lm),
                       {"buckets": arm_results[a]["buckets"],
                        "typed_acc": arm_results[a]["typed_acc"],
                        "dist_derive_rate": arm_results[a]["distractor_derive_rate"],
                        "eval_s": round(time.perf_counter() - t, 1)})
        base_res = arm_results[BASE]
        target_qids = base_res["struct_absent_qids"]   # STRUCTURALLY_ABSENT under BASE = the target bucket
        comparisons = {}
        for a in arms:
            if a == BASE:
                continue
            comparisons[a] = compare_to_base(base_res, arm_results[a], target_qids, exp_raw)
        # per-rule attribution for the EXPANSION arm (selectivity instrument)
        attr = attribute_new_rules(reasoners[EXPANSION], questions, base_res["per_q"],
                                   arm_results[EXPANSION]["per_q"], exp_raw, lm)
        attributions[lm] = attr

        vdict = verdict_for_config(lm, base_res, arm_results, comparisons)
        verdicts[lm] = vdict

        # strip heavy per_q from stored arm_results (keep summaries); retain struct_absent_qids
        stored_arms = {}
        for a in arms:
            ar = dict(arm_results[a])
            ar.pop("per_q", None)
            ar["struct_absent_qids"] = ar.get("struct_absent_qids", [])[:80]
            stored_arms[a] = ar
        per_config[lm] = {"arm_results": stored_arms, "comparisons": comparisons,
                          "target_bucket_n": len(target_qids),
                          "positive_control_buckets_anchor": REPRO_BUCKETS.get(lm, {})}
        _log("config %s verdict=%s | real_lift=%s scr_pair=%s flip=%s | dr_base=%.4f dr_exp=%.4f sel_held=%s"
             % (lm, vdict["verdict"], _fmt(vdict["real_lift"]), _fmt(vdict["scramble_pair_lift"]),
                _fmt(vdict["flip_dir_lift"]), vdict["distractor_derive_rate_base"],
                vdict["distractor_derive_rate_expansion"], vdict["selectivity_held"]))

    primary = "lemma_syn" if "lemma_syn" in link_modes else link_modes[0]
    pv = verdicts[primary]
    pc = per_config[primary]
    exp_cmp = pc["comparisons"][EXPANSION]
    ng = exp_cmp["newly_gold_derivable"]

    summary = (
        "RULE-SUPPLY EXPANSION correctness [%s]: BASE buckets=%s (repro_ok=%s) EXPANSION buckets=%s | "
        "target-bucket(STRUCT_ABSENT n=%d) acc %.4f->%.4f (delta=%s) | newly-gold-derivable=%d "
        "(clean_win=%d[correct=%d] tie_conv=%d[correct=%d]) | promiscuity: new_dist_only=%d gold_only_eroded=%d "
        "| dist-derive rate base=%.4f exp=%.4f (delta=%s) sel_held=%s | scramble_pair_lift=%s flip_lift=%s | "
        "whole-set typed_acc base=%.4f exp=%.4f | %s" % (
            primary, pc["arm_results"][BASE]["buckets"], pv["repro_ok"],
            pc["arm_results"][EXPANSION]["buckets"], pc["target_bucket_n"],
            exp_cmp["base_target_acc"], exp_cmp["arm_target_acc"], _fmt(exp_cmp["target_acc_delta"]),
            ng["total"], ng["clean_win"]["n"], ng["clean_win"]["correct"],
            ng["tie_conversion"]["n"], ng["tie_conversion"]["correct"],
            exp_cmp["promiscuity"]["new_dist_only"]["n"], exp_cmp["promiscuity"]["gold_only_eroded"]["n"],
            pv["distractor_derive_rate_base"], pv["distractor_derive_rate_expansion"],
            _fmt(exp_cmp["distractor_derive_rate_delta"]), pv["selectivity_held"],
            _fmt(pv["scramble_pair_lift"]), _fmt(pv["flip_dir_lift"]),
            pc["arm_results"][BASE]["typed_acc"], pc["arm_results"][EXPANSION]["typed_acc"], pv["verdict"]))
    _log("SUMMARY: %s" % summary)

    metrics = {
        "REQUIRED_FIELDS": ["verdict", "tier", "per_config", "verdicts", "attributions",
                            "preregistered_bands", "prereg_thresholds"],
        "anchor_name": ANCHOR_NAME, "verdict": pv["verdict"], "tier": "VET_PENDING",
        "summary": summary, "run_mode": run_mode, "primary_config": primary,
        "verdict_msg": (
            "Rule-supply expansion (233 v1 -> 253 with 20 VETTED general science rules) tested for CORRECTNESS "
            "(not just coverage) + SELECTIVITY on ARC-Challenge (1172) via the composed DerivationReasoner. ONE "
            "variable = the rule SET (reasoner/link/CI/do/decision identical). PRIMARY = target-bucket "
            "(STRUCTURALLY_ABSENT-under-BASE) typed-accuracy delta; newly-gold-derivable split into clean_win "
            "(gold_only) vs meaning-bound tie_conversion; promiscuity harm (new dist_only + gold_only erosion) "
            "netted out. SELECTIVITY gate = candidate-level distractor-derive rate must stay <= base + %.3f. "
            "MUST-FAIL controls: SCRAMBLE_PAIR (arg1 deranged: same vocab/relations/degree, knowledge destroyed) "
            "+ FLIP_DIR (arg0<->arg1 reversed) -- both target-bucket lifts must collapse. POSITIVE CONTROL: BASE "
            "reproduces prior buckets exactly. Held-out ARC test; rules NOT derived from labels (targets_qid is a "
            "recording tag). INLINE-LOCAL; VET-PENDING; no bank." % SEL_TOL),
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "link_modes": link_modes,
                   "arms": arms, "seed": seed, "depth_bump": DEPTH_BUMP,
                   "base_rules_path": BASE_RULES_PATH, "expansion_rules_path": EXPANSION_RULES_PATH,
                   "n_rules": {a: len(rulesets[a]) for a in arms},
                   "one_variable_across_arms": "rule_set (reasoner/link/CI/do/decision identical)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "per_config": per_config, "verdicts": verdicts, "attributions": attributions,
        "preregistered_bands": {
            "hard_pass": pv["verdict"].startswith("HARD_PASS"),
            "honest_neg": pv["verdict"].startswith("HONEST_NEG"),
            "middle_band": pv["verdict"].startswith("MIDDLE_BAND"),
            "inconclusive": pv["verdict"].startswith("INCONCLUSIVE"),
        },
        "prereg_thresholds": {"lift_min": LIFT_MIN, "sel_tol": SEL_TOL, "scramble_max": SCRAMBLE_MAX,
                              "lift_over_scramble": LIFT_OVER_SCRAMBLE, "depth_bump": DEPTH_BUMP,
                              "positive_control_anchor": REPRO_BUCKETS},
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "host": platform.node(),
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)
    _log("done (%.1fs)" % (time.perf_counter() - _T0[0]))
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=0, help="ARC-Challenge sample size (0 = all 1172)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--link-modes", type=str, default="lemma_syn,lemma")
    ap.add_argument("--arms", type=str, default=",".join(ALL_ARMS))
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    link_modes = [x.strip() for x in args.link_modes.split(",") if x.strip()]
    arms = [x.strip() for x in args.arms.split(",") if x.strip()]
    if BASE not in arms:
        arms = [BASE] + arms
    if args.mode == "smoke":
        n_sample = args.n if args.n else 150
        output_dir = args.out + "_smoke"
        link_modes = link_modes[:1]
    else:
        n_sample = args.n
        output_dir = args.out
    try:
        run(output_dir, n_sample, link_modes, arms, args.seed, args.mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print("[CRASH] %s: %s" % (type(exc).__name__, exc), flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
