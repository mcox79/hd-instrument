"""exp_intrinsic_foundation_loop_tie_gaps_powered_v1 -- POWER the v1 tie-resolution test.

v1 (banked 29572) was leak-free + directionally positive but UNDERPOWERED at n=44 genuine ties: the
load-bearing concept-specific contrast ARM1-vs-ARM3global (+0.181) was only p=0.096; ARM1-vs-ARM0 (+0.205)
p=0.064. This cell settles whether the directional tie-resolution effect is REAL or noise by EXPANDING the
TIE POPULATION to n>=~120 and running a paired McNemar significance test on the concept-specific contrast.

THE ONE CHANGE vs v1 = the TIE POOL. ALL FOUR ARMS + FLOOR + GLOBAL-scramble are IMPORTED UNCHANGED from
exp_intrinsic_foundation_loop_tie_gaps_v1 (VET-cleared leak-free; commit c7d9ad894 / amend e35befda0). The
acquisition (answer-agnostic), the meaning-match tie-break, the HDFactStore trust-gate ARM2 loop, and the
GLOBAL scramble control are the SAME functions -- so leak stays impossible by construction.

TIE POOL EXPANSION (this cell's only new logic):
  (1) ARC-EASY too (v1 was Challenge-only 1172Q -> 44 lemma ties; Easy 2376Q roughly doubles the pool).
  (2) POOL BOTH link modes' genuine ties (lemma + glove). GENUINE-tie definition IDENTICAL to v1: a
      lemma_syn tie that STAYS a tie under the tighter link mode (both a gold-chain AND a distractor-chain
      co-derive; excludes BROKE_GOLD/BROKE_BOTH/gold_only). glove-genuine and lemma-genuine ties are both
      subsets of the lemma_syn tie set, so only the lemma_syn sweep runs over ALL questions; lemma/glove
      re-eval is restricted to the lemma_syn tie qids (compute stays small).
  DEDUP: each (split, qid) enters the pool ONCE -> paired McNemar units are INDEPENDENT (no same-qid double
  count that would fake power). Operating link mode per unit: prefer lemma if genuine there, else glove. The
  ladder is evaluated in the regime where the tie IS a tie (reasoner.link_mode set per unit).

POSITIVE CONTROL (Gate D, reproduce prior at test regime): on the CHALLENGE split at link_mode=lemma the
  genuine tie count MUST reproduce v1 EXACT (44 genuine, ARM0 legacy tie-break = 15/44 = 0.3409 = 29570).

CONTRACT (pre-registered, can-fail):
  HARD-PASS = ARM1-vs-ARM3global paired McNemar exact-binomial p < 0.05 AND arm1_acc > arm3global_acc
    (concept-specific tie-resolution ESTABLISHED at the larger n).
  HONEST-NEG = still not significant (p >= 0.05) at the larger n -> the directional effect was NOISE, routes
    to revival (b): grounded (non-thin-GloVe) meaning-match.
  Also report ARM1-vs-ARM0 and ARM2-vs-ARM3global McNemar (p + discordant b/c counts), plus per-arm accs,
  per-arity (2/3/4-way) and per-split (Easy/Challenge) breakdowns. gold_only preserved @1.00 (by construction).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic (fixed
  seed, sorted iteration); repo .venv. VET-PENDING (skunkworks owns landed-VET); NO atom banking.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no bare/BaseException); atomic
  metrics (tmp+os.replace); start-marker; crash-diagnostic; heartbeat; progress prints. self-test builds a
  planted 2-way pool + runs the McNemar path + reuses v1's real HDFactStore self-test path. All numbers
  MEASURED@ this run. The four arms are IMPORTED from v1 (not re-implemented) -> provably identical.
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_reasoner_link_precision_tie_prune_v1 as tp
# THE FOUR ARMS + FLOOR + GLOBAL-scramble come from v1 UNCHANGED (leak-free, VET-cleared).
from experiments import exp_intrinsic_foundation_loop_tie_gaps_v1 as v1

ANCHOR_NAME = "intrinsic_foundation_loop_tie_gaps_powered_v1"
SEED = 20260725
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")

BASE_MODE = "lemma_syn"          # defines the ties (VET baseline; same as v1)
GAP_MODES = ["lemma", "glove"]   # POOL genuine ties from BOTH tighter link modes
PREFER_MODE = "lemma"            # dedup: a qid genuine at both modes operates at lemma (v1 canonical)
TIEBREAK_MODE = "legacy"         # ARM0 uses the reasoner's own legacy node-combiner tie-break
K_FACTS = v1.K_FACTS

# ---- POSITIVE-CONTROL target (Challenge split, lemma mode; reproduces v1 / 29570 EXACT) ----
CHAL_LEMMA_GENUINE_EXPECTED = 44
CHAL_LEMMA_ARM0_CORRECT_EXPECTED = 15

# ---- pre-registered bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned) ----
HP_MCNEMAR_P = 0.05              # ARM1-vs-ARM3global exact-binomial McNemar p < this = ESTABLISHED
POWER_TARGET_N = 120            # design target for the expanded pool (reported; not a hard gate)
GOLD_ONLY_FLOOR = 1.0           # single-valid decisions unchanged (preserved by construction)

_T0 = [time.perf_counter()]


# ===========================================================================
# atomic metrics / start-marker / crash-diag / heartbeat  (same pattern as v1)
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
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
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
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ===========================================================================
# paired McNemar (exact two-sided binomial on discordant pairs)
# ===========================================================================
def mcnemar(a_correct: List[int], b_correct: List[int], a_name: str, b_name: str) -> dict:
    """Paired binary correctness McNemar. b = a-right & b-wrong (a wins); c = a-wrong & b-right (b wins).
    Exact two-sided binomial p under H0 (discordants ~ Binomial(n, 0.5)). scipy.stats.binomtest."""
    assert len(a_correct) == len(b_correct), "paired arrays must align"
    b = sum(1 for x, y in zip(a_correct, b_correct) if x == 1 and y == 0)
    c = sum(1 for x, y in zip(a_correct, b_correct) if x == 0 and y == 1)
    n_disc = b + c
    if n_disc == 0:
        p = 1.0
    else:
        from scipy.stats import binomtest
        p = float(binomtest(min(b, c), n_disc, 0.5, alternative="two-sided").pvalue)
    return {"contrast": f"{a_name}_vs_{b_name}",
            f"{a_name}_wins": b, f"{b_name}_wins": c, "n_discordant": n_disc,
            "b_first_better": b, "c_second_better": c, "p_exact": round(p, 5)}


# ===========================================================================
# POOL CONSTRUCTION: genuine ties across (split x link mode), deduped to one unit per (split,qid)
# ===========================================================================
def build_pool(reasoner: DerivationReasoner, output_dir: str,
               splits: List[Tuple[str, str]], n_sample: int, seed: int) -> Tuple[List[dict], dict]:
    """Return (pool_units, cfg_cache). Each unit = {split, qid, mode, question, arm0_chosen, arm0_correct}.
    GENUINE-tie definition identical to v1: lemma_syn tie that STAYS a tie under the tighter mode."""
    pool: List[dict] = []
    cfg_cache: Dict[str, dict] = {}
    detect_summary: Dict[str, dict] = {}
    scratch = os.path.join(output_dir, "_reproduce_scratch")

    for split_name, split_path in splits:
        all_q = arc._load_questions(split_path, limit=0)
        if n_sample and n_sample < len(all_q):
            rng = np.random.default_rng(seed)
            idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
            qs = [all_q[i] for i in idx]
        else:
            qs = all_q
        qmap = {q["qid"]: q for q in qs}

        # FULL sweep at lemma_syn defines the tie set for this split.
        base_cfg = tp.eval_config(reasoner, qs, scratch, BASE_MODE)
        tie_qids_syn = sorted(qid for qid, r in base_cfg["per_q"].items() if r["subset"] == "tie")
        tie_qs = [qmap[qid] for qid in tie_qids_syn]
        _heartbeat(output_dir, f"lemma_syn_swept:{split_name}",
                   {"n_q": len(qs), "n_lemma_syn_ties": len(tie_qids_syn)})

        # restricted re-eval at each tighter mode ONLY over the lemma_syn tie qids (genuine subset of them).
        mode_cfg: Dict[str, dict] = {}
        genuine_by_mode: Dict[str, List[str]] = {}
        for gm in GAP_MODES:
            cfg = tp.eval_config(reasoner, tie_qs, scratch, gm)
            mode_cfg[gm] = cfg
            genuine_by_mode[gm] = sorted(qid for qid in tie_qids_syn
                                         if cfg["per_q"][qid]["subset"] == "tie")
        cfg_cache[split_name] = {"base": base_cfg, "modes": mode_cfg}

        # DEDUP: prefer lemma; add glove-only-genuine as extra independent units.
        chosen_mode: Dict[str, str] = {}
        for qid in genuine_by_mode.get(PREFER_MODE, []):
            chosen_mode[qid] = PREFER_MODE
        for gm in GAP_MODES:
            if gm == PREFER_MODE:
                continue
            for qid in genuine_by_mode[gm]:
                chosen_mode.setdefault(qid, gm)

        for qid in sorted(chosen_mode):
            gm = chosen_mode[qid]
            pq = mode_cfg[gm]["per_q"][qid]
            pool.append({"split": split_name, "qid": qid, "mode": gm, "question": qmap[qid],
                         "arm0_chosen": pq["chosen"], "arm0_correct": pq["correct"],
                         "correct_index": qmap[qid]["correct_index"]})

        detect_summary[split_name] = {
            "n_q": len(qs), "n_lemma_syn_ties": len(tie_qids_syn),
            "n_genuine_lemma": len(genuine_by_mode.get("lemma", [])),
            "n_genuine_glove": len(genuine_by_mode.get("glove", [])),
            "n_units_from_split": sum(1 for u in pool if u["split"] == split_name),
            "n_glove_only_units": sum(1 for u in pool if u["split"] == split_name and u["mode"] == "glove"),
        }
        _heartbeat(output_dir, f"pool_built:{split_name}", detect_summary[split_name])

    return pool, {"detect": detect_summary, "cfg_cache": cfg_cache}


# ===========================================================================
# LADDER over the pooled units -- arms are v1's functions, unchanged
# ===========================================================================
def evaluate_pool(reasoner: DerivationReasoner, pool: List[dict], output_dir: str,
                  index: Dict[str, List[int]], facts: List[dict], wn,
                  encode: Callable[[str], np.ndarray], seed: int) -> dict:
    """PASS1 build per-unit context (valid choices, stem vec, oracle + autonomous facts) at the unit's
    operating link mode; PASS2 decide every arm incl. the GLOBAL scramble. Reuses v1 arm functions."""
    # ---- PASS 1 ----
    contexts: List[dict] = []
    consolidation_totals = {"n_ingested": 0, "n_live_recovered": 0, "n_conflict": 0}
    n_units = len(pool)
    for ui, unit in enumerate(pool):
        q = unit["question"]
        ci = unit["correct_index"]
        reasoner.link_mode = unit["mode"]
        reasoner.tiebreak_mode = TIEBREAK_MODE
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        valid = [{"choice_index": c["choice_index"], "choice_text": c["choice_text"]}
                 for c in v1._valid_choices(res["per_choice"])]
        stem_vec = v1._l2(np.asarray(encode(q["stem"]), dtype=np.float32))
        # ARM1 oracle: widest answer-agnostic retrieval (content+lemma+WN synonyms).
        oracle_facts = {}
        for c in valid:
            fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
            oracle_facts[c["choice_index"]] = [f["text"] for f in v1._select_facts(facts, fids, K_FACTS)]
        # ARM2 autonomous loop: detect -> ingest(trust-gate) -> consolidate -> query back.
        auto_facts, clog = v1.autonomous_facts(valid, index, facts, wn, seed + ui)
        for k in consolidation_totals:
            consolidation_totals[k] += clog[k]
        contexts.append({"split": unit["split"], "qid": unit["qid"], "mode": unit["mode"], "ci": ci,
                         "valid": valid, "stem_vec": stem_vec, "oracle_facts": oracle_facts,
                         "auto_facts": auto_facts, "arm0_chosen": unit["arm0_chosen"],
                         "arm0_correct": unit["arm0_correct"]})
        if (ui + 1) % 20 == 0:
            _heartbeat(output_dir, "ladder_pass1", {"done": ui + 1, "total": n_units})

    # global fact pool for the GLOBAL scramble: every valid choice's oracle fact-set, tagged by qid.
    global_pool = [(ctx["qid"], fts) for ctx in contexts for fts in ctx["oracle_facts"].values() if fts]

    # ---- PASS 2: decisions for every arm ----
    per_tie: List[dict] = []
    grng = np.random.default_rng(seed * 101 + 5)
    for ctx in contexts:
        qid, ci, valid, stem_vec = ctx["qid"], ctx["ci"], ctx["valid"], ctx["stem_vec"]
        oracle_facts, auto_facts = ctx["oracle_facts"], ctx["auto_facts"]
        no_facts = {c["choice_index"]: [] for c in valid}
        floor_pick = v1.decide_by_meaning(valid, no_facts, encode, stem_vec)
        arm1_pick = v1.decide_by_meaning(valid, oracle_facts, encode, stem_vec)
        arm2_pick = v1.decide_by_meaning(valid, auto_facts, encode, stem_vec)
        arm3_within_pick = v1.decide_by_meaning(
            valid, v1.scramble_facts(valid, oracle_facts, seed + len(per_tie)), encode, stem_vec)
        # ARM3b GLOBAL scramble (v1 logic unchanged): each choice gets a fact-set from a DIFFERENT question.
        other = [fts for (sq, fts) in global_pool if sq != qid]
        gscr = {}
        for c in valid:
            gscr[c["choice_index"]] = list(other[int(grng.integers(len(other)))]) if other else []
        arm3_global_pick = v1.decide_by_meaning(valid, gscr, encode, stem_vec)

        per_tie.append({
            "split": ctx["split"], "qid": qid, "mode": ctx["mode"], "correct_index": ci,
            "n_valid": len(valid), "valid_indices": [c["choice_index"] for c in valid],
            "arm0_pick": ctx["arm0_chosen"], "arm0_correct": int(ctx["arm0_correct"]),
            "floor_pick": floor_pick, "arm1_pick": arm1_pick, "arm2_pick": arm2_pick,
            "arm3_within_pick": arm3_within_pick, "arm3_global_pick": arm3_global_pick,
            "floor_correct": int(floor_pick == ci), "arm1_correct": int(arm1_pick == ci),
            "arm2_correct": int(arm2_pick == ci),
            "arm3_within_correct": int(arm3_within_pick == ci),
            "arm3_global_correct": int(arm3_global_pick == ci),
            "n_oracle_facts": sum(len(v) for v in oracle_facts.values()),
            "n_auto_facts": sum(len(v) for v in auto_facts.values()),
        })

    return {"per_tie": per_tie, "consolidation_totals": consolidation_totals,
            "n_units": n_units}


def _acc(rows: List[dict], key: str) -> float:
    return round(sum(r[key] for r in rows) / len(rows), 4) if rows else 0.0


def _breakdown(rows: List[dict]) -> dict:
    ks = ("arm0_correct", "floor_correct", "arm1_correct", "arm2_correct",
          "arm3_within_correct", "arm3_global_correct")
    return {"n": len(rows), **{k.replace("_correct", ""): _acc(rows, k) for k in ks}}


# ===========================================================================
# gold_only preservation check (bounded, per split; unchanged decision semantics)
# ===========================================================================
def check_gold_only_preserved(reasoner: DerivationReasoner, cfg_cache: dict,
                              splits: List[Tuple[str, str]], index, facts, wn, encode,
                              n_sample: int, seed: int, cap: int = 40) -> Tuple[float, int]:
    preserved = 1.0
    checked = 0
    for split_name, split_path in splits:
        all_q = arc._load_questions(split_path, limit=0)
        if n_sample and n_sample < len(all_q):
            rng = np.random.default_rng(seed)
            idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
            qs = [all_q[i] for i in idx]
        else:
            qs = all_q
        qmap = {q["qid"]: q for q in qs}
        # gold_only qids are defined at the BASE (lemma_syn) mode -> evaluate the guardrail THERE, where the
        # qid has exactly ONE valid choice by definition (at a tighter mode gold may not derive -> 0 valid).
        base_pq = cfg_cache[split_name]["base"]["per_q"]
        go_qids = sorted(qid for qid, r in base_pq.items() if r["subset"] == "gold_only")[:cap]
        reasoner.link_mode = BASE_MODE
        reasoner.tiebreak_mode = TIEBREAK_MODE
        for qid in go_qids:
            q = qmap[qid]
            res = reasoner._reason_arm(q, reasoner.arms["typed"])
            valid = v1._valid_choices(res["per_choice"])
            if len(valid) != 1:
                continue  # defensive: only the genuinely single-valid case tests the preservation guardrail
            stem_vec = v1._l2(np.asarray(encode(q["stem"]), dtype=np.float32))
            oracle = {}
            for c in valid:
                fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
                oracle[c["choice_index"]] = [f["text"] for f in v1._select_facts(facts, fids, K_FACTS)]
            pick = v1.decide_by_meaning(valid, oracle, encode, stem_vec)
            checked += 1
            if pick != valid[0]["choice_index"]:
                preserved = 0.0
    return preserved, checked


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", POWER_TARGET_N)
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})

    rows = tp._load_rules(RULES_PATH)
    _heartbeat(output_dir, "rules_loaded", {"n_rules": len(rows)})

    index, facts = v1.build_acq_index()
    _heartbeat(output_dir, "acq_index_built", {"n_facts": len(facts), "n_concept_keys": len(index)})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon
    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    encode = base.encode
    _heartbeat(output_dir, "encoder_ready")

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed, rows=rows,
                                  link_mode=BASE_MODE, tiebreak_mode=TIEBREAK_MODE)
    _heartbeat(output_dir, "graph_built",
               {"n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"]})

    splits = [("easy", arc._EASY_TEST), ("challenge", arc._CHAL_TEST)]
    pool, pool_meta = build_pool(reasoner, output_dir, splits, n_sample, seed)
    _heartbeat(output_dir, "pool_ready", {"n_pool": len(pool), "detect": pool_meta["detect"]})

    rep = evaluate_pool(reasoner, pool, output_dir, index, facts, wn, encode, seed)
    per_tie = rep["per_tie"]
    _heartbeat(output_dir, "ladder_done", {"n_units": rep["n_units"]})

    go_preserved, go_checked = check_gold_only_preserved(
        reasoner, pool_meta["cfg_cache"], splits, index, facts, wn, encode, n_sample, seed)
    reasoner.link_mode = BASE_MODE

    # ---- arm accuracies over the WHOLE pool ----
    arms = {
        "arm0_legacy_combiner": _acc(per_tie, "arm0_correct"),
        "floor_mm_no_facts": _acc(per_tie, "floor_correct"),
        "arm1_oracle_ceiling": _acc(per_tie, "arm1_correct"),
        "arm2_autonomous_loop": _acc(per_tie, "arm2_correct"),
        "arm3_scramble_within": _acc(per_tie, "arm3_within_correct"),
        "arm3_scramble_global": _acc(per_tie, "arm3_global_correct"),
    }
    a1 = [r["arm1_correct"] for r in per_tie]
    a2 = [r["arm2_correct"] for r in per_tie]
    a0 = [r["arm0_correct"] for r in per_tie]
    a3g = [r["arm3_global_correct"] for r in per_tie]
    a3w = [r["arm3_within_correct"] for r in per_tie]
    fl = [r["floor_correct"] for r in per_tie]

    mc = {
        "arm1_vs_arm3global": mcnemar(a1, a3g, "arm1", "arm3global"),   # HARD-PASS contrast
        "arm1_vs_arm0": mcnemar(a1, a0, "arm1", "arm0"),
        "arm2_vs_arm3global": mcnemar(a2, a3g, "arm2", "arm3global"),
        "arm1_vs_floor": mcnemar(a1, fl, "arm1", "floor"),
        "arm1_vs_arm3within": mcnemar(a1, a3w, "arm1", "arm3within"),
    }

    # ---- breakdowns ----
    by_arity = {f"{k}_way": _breakdown([r for r in per_tie if r["n_valid"] == k]) for k in (2, 3, 4)}
    by_arity["ge5_way"] = _breakdown([r for r in per_tie if r["n_valid"] >= 5])
    by_split = {sn: _breakdown([r for r in per_tie if r["split"] == sn]) for sn, _ in splits}
    by_mode = {m: _breakdown([r for r in per_tie if r["mode"] == m]) for m in GAP_MODES}

    # ---- POSITIVE CONTROL: Challenge/lemma genuine ties reproduce v1 / 29570 EXACT ----
    chal_lemma = [r for r in per_tie if r["split"] == "challenge" and r["mode"] == "lemma"]
    smoke_run = (n_sample != 0)
    pc_n = len(chal_lemma)
    pc_arm0 = sum(r["arm0_correct"] for r in chal_lemma)
    pc_ok = (pc_n == CHAL_LEMMA_GENUINE_EXPECTED and pc_arm0 == CHAL_LEMMA_ARM0_CORRECT_EXPECTED)
    positive_control = {
        "chal_lemma_genuine_n": pc_n, "chal_lemma_genuine_expected": CHAL_LEMMA_GENUINE_EXPECTED,
        "chal_lemma_arm0_correct": pc_arm0, "chal_lemma_arm0_expected": CHAL_LEMMA_ARM0_CORRECT_EXPECTED,
        "reproduces_v1_29570": bool(pc_ok),
        "note": ("full-set only; smoke subsamples so the Challenge/lemma gap set is NOT the canonical 44"
                 if smoke_run else "full ARC test sets; Challenge/lemma subset must reproduce v1 EXACT"),
    }

    n_pool = len(per_tie)
    d_arm1_arm3g = round(arms["arm1_oracle_ceiling"] - arms["arm3_scramble_global"], 4)
    d_arm1_arm0 = round(arms["arm1_oracle_ceiling"] - arms["arm0_legacy_combiner"], 4)
    d_arm2_arm3g = round(arms["arm2_autonomous_loop"] - arms["arm3_scramble_global"], 4)

    hp_p = mc["arm1_vs_arm3global"]["p_exact"]
    hp_direction = arms["arm1_oracle_ceiling"] > arms["arm3_scramble_global"]
    hp_established = (hp_p < HP_MCNEMAR_P and hp_direction
                     and go_preserved >= GOLD_ONLY_FLOOR and (pc_ok or smoke_run))

    bands = {
        "arm1_vs_arm3global_mcnemar_p_lt_0.05": hp_p < HP_MCNEMAR_P,
        "arm1_beats_arm3global_direction": bool(hp_direction),
        "gold_only_preserved": go_preserved >= GOLD_ONLY_FLOOR,
        "positive_control_reproduces_v1": bool(pc_ok or smoke_run),
        "power_target_n_reached": n_pool >= POWER_TARGET_N,
    }

    if not pc_ok and not smoke_run:
        tier, verdict = "POSITIVE_CONTROL_FAIL", "REPRODUCE_v1_29570_MISMATCH"
    elif hp_established:
        tier, verdict = "HARD_PASS", "CONCEPT_SPECIFIC_TIE_RESOLUTION_ESTABLISHED"
    elif hp_p >= HP_MCNEMAR_P:
        tier, verdict = "HONEST_NEG", "DIRECTIONAL_EFFECT_WAS_NOISE_ROUTE_TO_GROUNDED_MEANING"
    else:
        tier, verdict = "MIDDLE_BAND", "SIGNIFICANT_BUT_WRONG_DIRECTION_OR_GUARDRAIL"

    summary = (
        f"POWERED tie-resolution on n={n_pool} genuine ties (Easy+Challenge, lemma+glove pooled) | "
        f"ARM0(legacy)={arms['arm0_legacy_combiner']:.3f} FLOOR={arms['floor_mm_no_facts']:.3f} "
        f"ARM1(oracle)={arms['arm1_oracle_ceiling']:.3f} ARM2(auto)={arms['arm2_autonomous_loop']:.3f} "
        f"ARM3global={arms['arm3_scramble_global']:.3f} ARM3within={arms['arm3_scramble_within']:.3f} | "
        f"d(ARM1-ARM3global)={d_arm1_arm3g:+.3f} McNemar p={hp_p:.4f} "
        f"(b={mc['arm1_vs_arm3global']['b_first_better']},c={mc['arm1_vs_arm3global']['c_second_better']}) | "
        f"d(ARM1-ARM0)={d_arm1_arm0:+.3f} p={mc['arm1_vs_arm0']['p_exact']:.4f} | "
        f"d(ARM2-ARM3global)={d_arm2_arm3g:+.3f} p={mc['arm2_vs_arm3global']['p_exact']:.4f} | "
        f"gold_only_preserved={go_preserved:.2f} | repro_v1={positive_control['reproduces_v1_29570']} | "
        f"tier={tier}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "POWERED replication of the v1 intrinsic-foundation-loop tie-resolution test (v1 banked 29572 was "
            "leak-free + directionally positive but UNDERPOWERED at n=44: ARM1-vs-ARM3global +0.181 p=0.096). "
            "THE ONE CHANGE = the TIE POOL is expanded to reach power; ALL FOUR ARMS + FLOOR + GLOBAL-scramble "
            "are IMPORTED UNCHANGED from exp_intrinsic_foundation_loop_tie_gaps_v1 (acquisition answer-agnostic, "
            "meaning-match tie-break, HDFactStore trust-gate ARM2 loop, GLOBAL scramble) -> leak stays impossible "
            "by construction. POOL: genuine ties from BOTH ARC-Easy and ARC-Challenge, pooling BOTH tighter link "
            "modes (lemma + glove); GENUINE-tie definition IDENTICAL to v1 (a lemma_syn tie that STAYS a tie under "
            "the tighter mode = both a gold-chain AND a distractor-chain co-derive; excludes BROKE_*/gold_only). "
            "Each (split,qid) enters the pool ONCE (deduped -> paired McNemar units independent; no same-qid "
            "double-count faking power); operating link mode per unit prefers lemma, else glove. POSITIVE CONTROL "
            "(Gate D): Challenge/lemma genuine ties must reproduce v1 EXACT (44 genuine, ARM0 legacy=15/44). "
            "PRE-REGISTERED can-fail: HARD-PASS = ARM1-vs-ARM3global paired McNemar exact-binomial p<0.05 AND "
            "arm1>arm3global (concept-specific tie-resolution ESTABLISHED at the larger n); HONEST-NEG = still not "
            "significant (p>=0.05) -> the directional effect was NOISE, routes to revival (b) grounded (non-thin-"
            "GloVe) meaning-match. Reports ARM1-vs-ARM0 and ARM2-vs-ARM3global McNemar (p + discordant b/c), per-arm "
            "accs, per-arity (2/3/4/ge5-way) and per-split (Easy/Challenge) breakdowns. gold_only preserved @1.00 by "
            "construction. NOTE: meaning-match is still thin GloVe (SemanticHDEncoder, INTERIM). HELD-OUT ARC; "
            "science rules not from test labels. VET-PENDING; no atom banking."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_sample_per_split": n_sample, "seed": seed, "rules_path": RULES_PATH,
                   "n_rules": len(rows), "base_mode": BASE_MODE, "gap_modes": GAP_MODES,
                   "prefer_mode": PREFER_MODE, "tiebreak_mode": TIEBREAK_MODE, "k_facts": K_FACTS,
                   "arms_source": "exp_intrinsic_foundation_loop_tie_gaps_v1 (IMPORTED UNCHANGED)",
                   "meaning_match": "SemanticHDEncoder text cosine (thin GloVe; INTERIM, HONEST caveat)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)",
                   "progress_logging": "heartbeat jsonl + stdout flush per stage/20-unit"},
        "n_pool": n_pool, "pool_detection": pool_meta["detect"],
        "positive_control": positive_control,
        "arms": arms,
        "deltas": {"arm1_minus_arm3global": d_arm1_arm3g, "arm1_minus_arm0": d_arm1_arm0,
                   "arm2_minus_arm3global": d_arm2_arm3g,
                   "arm1_minus_floor": round(arms["arm1_oracle_ceiling"] - arms["floor_mm_no_facts"], 4),
                   "arm2_minus_arm0": round(arms["arm2_autonomous_loop"] - arms["arm0_legacy_combiner"], 4)},
        "mcnemar": mc,
        "breakdown_by_arity": by_arity, "breakdown_by_split": by_split, "breakdown_by_mode": by_mode,
        "acquisition": {"source": "WorldTree tablestore (parse_tablestore_typed, ALL relations)",
                        "n_facts": len(facts), "n_concept_keys": len(index),
                        "trust_gate": "hd_fact_store.HDFactStore (WorldTree=TRUST_HIGH)",
                        "totals": rep["consolidation_totals"]},
        "gold_only_preserved": round(go_preserved, 4), "gold_only_checked": go_checked,
        "preregistered_bands": bands, "n_bands_pass": sum(1 for v in bands.values() if v),
        "bands_definition": {
            "hard_pass": f"arm1_vs_arm3global exact McNemar p < {HP_MCNEMAR_P} AND arm1>arm3global AND "
                         "gold_only preserved AND positive-control reproduces v1",
            "honest_neg": f"arm1_vs_arm3global p >= {HP_MCNEMAR_P} -> directional effect was noise, route to "
                          "revival (b) grounded meaning-match",
            "power_target_n": POWER_TARGET_N,
        },
        "per_tie": per_tie,
        "REQUIRED_FIELDS": ["verdict", "tier", "n_pool", "positive_control", "arms", "mcnemar",
                            "deltas", "preregistered_bands", "gold_only_preserved", "breakdown_by_split"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== POWERED INTRINSIC FOUNDATION LOOP (tie-gaps) RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"bands: {bands} -> {metrics['n_bands_pass']}/5 | tier={tier}", flush=True)
    print(f"McNemar arm1_vs_arm3global: {mc['arm1_vs_arm3global']}", flush=True)
    print(f"positive_control: {positive_control}", flush=True)
    print(f"by_split: {by_split}", flush=True)
    print(f"by_arity: {by_arity}", flush=True)
    return metrics


# ===========================================================================
# self-test (real code path: planted pool + real McNemar + reuse v1's real HDFactStore self-test)
# ===========================================================================
def _self_test() -> None:
    print("[self-test] powered pool + McNemar (GloVe-free) ...", flush=True)
    exercised = set()

    # ---- (1) McNemar exact binomial on a hand pair; discordant counts + p sanity ----
    a = [1, 1, 1, 0, 0, 1, 1, 1]   # arm1
    b = [0, 0, 0, 0, 0, 1, 1, 0]   # arm3global: arm1 wins the 4 discordant (a=1,b=0), none the other way
    res = mcnemar(a, b, "arm1", "arm3global")
    assert res["b_first_better"] == 4 and res["c_second_better"] == 0, res
    assert res["n_discordant"] == 4, res
    # 4/4 one-directional discordant -> exact two-sided p = 2*0.5^4 = 0.125
    assert abs(res["p_exact"] - 0.125) < 1e-6, f"exact binomial p wrong: {res['p_exact']}"
    # perfectly symmetric -> p == 1.0
    sym = mcnemar([1, 0, 1, 0], [0, 1, 0, 1], "x", "y")
    assert sym["n_discordant"] == 4 and abs(sym["p_exact"] - 1.0) < 1e-6, sym
    exercised.add("mcnemar")
    print(f"[self-test] McNemar: 4-0 discordant p={res['p_exact']} (expect 0.125); symmetric p={sym['p_exact']}",
          flush=True)

    # ---- (2) breakdown helpers ----
    rows = [{"n_valid": 2, "split": "easy", "mode": "lemma", "arm0_correct": 1, "floor_correct": 0,
             "arm1_correct": 1, "arm2_correct": 1, "arm3_within_correct": 0, "arm3_global_correct": 0},
            {"n_valid": 3, "split": "challenge", "mode": "glove", "arm0_correct": 0, "floor_correct": 0,
             "arm1_correct": 0, "arm2_correct": 1, "arm3_within_correct": 1, "arm3_global_correct": 1}]
    bd = _breakdown(rows)
    assert bd["n"] == 2 and bd["arm1"] == 0.5 and bd["arm0"] == 0.5, bd
    exercised.add("_breakdown")

    # ---- (3) the four arms are the v1 objects (identity check, not a re-implementation) ----
    for fn in ("decide_by_meaning", "autonomous_facts", "scramble_facts", "retrieve_fact_ids",
               "build_acq_index", "_select_facts", "_valid_choices", "_l2", "mm_score"):
        assert hasattr(v1, fn), f"v1 missing reused arm function {fn}"
    exercised.add("arms_imported_from_v1")

    # ---- (4) reuse v1's REAL HDFactStore + instrument self-test (the leak-free arm path) ----
    v1._self_test()
    exercised.add("v1_real_code_path")
    print("[self-test] v1 arm self-test (real HDFactStore round-trip + instrument fires) PASSED", flush=True)

    # ---- (5) real rules + ARC data paths bind (real_code_path for the FULL entrypoint) ----
    real_rows = tp._load_rules(RULES_PATH)
    assert len(real_rows) > 100, "real rules file must load"
    assert os.path.exists(arc._EASY_TEST) and os.path.exists(arc._CHAL_TEST), "ARC Easy+Challenge must exist"
    exercised.add("real_paths")

    need = {"mcnemar", "_breakdown", "arms_imported_from_v1", "v1_real_code_path", "real_paths"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=250, help="smoke sample size PER SPLIT (full ignores this)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = args.n if args.mode == "smoke" else 0   # full = all test questions both splits
    output_dir = args.out if args.mode == "full" else args.out + "_smoke"
    try:
        run(output_dir, n_sample, args.seed)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
