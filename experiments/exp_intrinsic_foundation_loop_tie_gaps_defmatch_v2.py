"""exp_intrinsic_foundation_loop_tie_gaps_defmatch_v2 -- REFINED definitional-structure match that fixes the
three operationalization flaws the VET found in defmatch_v1 (c6aeeb2b3, HONEST_NEG operationalization-bound),
and DECISIVELY tests whether definitional grounding lifts the CHALLENGE-split ceiling or is genuinely dead.

WHY v1 failed for FIXABLE reasons (VET): the v1 def match (a) DROPPED the concept label (discarded signal),
(b) scored MAX-SINGLE-PREDICATE cosine over GENERIC-FILLER-dominated profiles (water/energy/object/push swamp
the discriminators -> the hub wins for every choice -> non-discriminating), and (c) got WORSE with more facts
(auto 0.484 > oracle 0.406) = LOSSY scoring. A discriminating-predicate-WEIGHTED, label-INCLUSIVE match was
UNTESTED. This cell tests exactly that.

THE THREE REFINEMENTS (isolate the MATCH SCORING; reuse everything else):
  R1 KEEP THE LABEL: the concept label (choice_text) is a scored CANDIDATE alongside the definitional predicates
     (combine label + definitional structure; v1 dropped it). The label-only candidate reduces to the FLOOR arm,
     so the refined match strictly GENERALIZES floor -- it can only add structure, never lose the label signal.
  R2 SPECIFICITY WEIGHTING: tie-pool IDF over the FILLER DISTRIBUTION across the n=128 tie-concept set.
     dfc(w) = # of (unit,choice) profile-bags (label words + predicate-object words) containing content-word w;
     idf(w) = log((1+N_bags)/(1+dfc(w))). Generic hubs (water/energy/object/push -> high dfc) get LOW idf and
     cannot dominate; rare discriminating predicate words get HIGH idf. GLASS-BOX: the top up/down-weighted
     tokens + their dfc are reported.
  R3 NON-LOSSY MONOTONE AGGREGATION: per candidate predicate p, a DISCRIMINATING-SCORE = specificity(p) *
     relevance(p, stem); the BEST candidate decides (max). Generic hubs are suppressed by low specificity, so
     adding MORE TRUE facts only adds MORE discriminating candidates -> oracle (more facts) must be >= auto.
     Two relevance backends, each principled:
       GROUNDED  : specificity(p)=sum idf(word in p) ; relevance=cosine(encode(p), stem) [encoder held CONSTANT
                   across the def and GloVe arms -> STRUCTURE is the one variable, not the encoder]
       SYMBOLIC  : GloVe-FREE; discriminating-score = sum idf(w) over w in content(p) INTERSECT content(stem)
                   (rarity-weighted lexical overlap; purely propositional assignment-lookup, no borrowed vector)

REUSE UNCHANGED (VET-cleared, leak-free): arms + n=128 tie pool + FLOOR + GLOBAL-scramble + positive control,
imported from powered_v1 (build_pool, mcnemar) + v1 (decide_by_meaning, retrieval, autonomous loop, scramble)
+ defmatch_v1 (build_def_profile trust-gate glass-box recover, grounded_align, _content_set, _heldout_side).
The 6 reused arms replicate powered's EXACT rng draw order -> reproduce 29573 EXACT (128/48/51/68/60/47).

ARMS (isolate the refined match as the ONE variable):
  REUSED (imported; positive control): ARM0/FLOOR/ARM1(GloVe oracle)/ARM2(GloVe auto)/ARM3within/ARM3global.
  NEW refined arms (label + tie-pool IDF + specificity*relevance monotone-max):
    RDEF_ORACLE   refined grounded match over ORACLE facts   -- ceiling + oracle>=auto sanity (R3).
    RDEF_AUTO     refined grounded match over AUTONOMOUS facts-- the PRIMARY decisive arm (end-to-end capability).
    RDEF_SCR      refined grounded match over GLOBALLY-SCRAMBLED facts -- MUST-FAIL control for RDEF_AUTO.
    RDEF_SYM_AUTO refined SYMBOLIC (GloVe-free) match over AUTONOMOUS facts -- GloVe-free companion.
    RDEF_SYM_SCR  refined SYMBOLIC match over scrambled facts -- MUST-FAIL for the symbolic companion.
  (label is included in ALL refined arms, so RDEF_AUTO-vs-RDEF_SCR isolates the incremental value of TRUE
   definitional STRUCTURE over-and-above the label -- the exact honest must-fail control.)

HARD CAN-FAIL BAR (VET-MANDATED decisive gate -- designed to FAIL cleanly if the signal isn't there):
  the refined match must LIFT OVER SCRAMBLE ON THE CHALLENGE SPLIT SPECIFICALLY (n=44), not just Easy.
  PRIMARY GATE = per-split (Challenge) paired McNemar RDEF_AUTO vs RDEF_SCR: p<0.05 AND acc>scr on Challenge.
  HARD_PASS  = Challenge-split RDEF_AUTO significantly beats RDEF_SCR (p<0.05, right direction) => definitional
               grounding is REAL, greenlights build B.
  HONEST_NEG = Challenge RDEF_AUTO does NOT beat scramble (collapses) => definitional/taxonomic grounding
               genuinely dead, B DISCONFIRMED, route to a different grounding. DECISIVE: saves the B investment.
  Also reports (per-split Challenge AND Easy): RDEF_AUTO vs GloVe ARM2, RDEF_AUTO vs GloVe ARM1, symbolic
  companion vs its scramble; oracle>=auto sanity (lossy-scoring fixed?); the specificity weighting chosen +
  which predicates it up/down-weighted (glass-box).
  Guardrails (for HARD_PASS): gold_only preserved @1.00; positive control reproduces powered EXACT.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic (fixed seed,
  numpy default_rng, sorted iteration, sha256 not python hash()); repo .venv. VET-PENDING; NO atom banking.
  Anti-leak: acquisition answer-agnostic; IDF built from objects/labels only (never correct_index); refined
  match uses stem+profile+label, never the answer; correct_index only in tally + decision-independent split.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no bare/BaseException); atomic
  metrics (tmp+os.replace); start-marker; crash-diagnostic; heartbeat; progress prints. self-test builds a
  planted discriminator (GloVe-free fake encoder) proving the REFINED match CAN-FIRE (label + a rare
  discriminating predicate -> gold, even when a generic hub is present) and CAN-FAIL (scrambled predicate ->
  not gold), the tie-pool IDF down-weights the hub, the REAL HDFactStore round-trip, and the REAL imports. All
  numbers MEASURED@ this run. The 6 reused arms are IMPORTED (not re-implemented) -> identical draw order.
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import hashlib
import argparse
import platform
import traceback
from collections import defaultdict, Counter
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner
from hdlab.hd_fact_store import HDFactStore
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_reasoner_link_precision_tie_prune_v1 as tp
# reused arms + tie pool + significance test (leak-free, VET-cleared) + v1 def-profile machinery.
from experiments import exp_intrinsic_foundation_loop_tie_gaps_v1 as v1
from experiments import exp_intrinsic_foundation_loop_tie_gaps_powered_v1 as powered
from experiments import exp_intrinsic_foundation_loop_tie_gaps_defmatch_v1 as dm1

ANCHOR_NAME = "intrinsic_foundation_loop_tie_gaps_defmatch_v2"
SEED = 20260725                     # SAME seed as powered/defmatch_v1 -> byte-identical pool -> reused arms EXACT
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")

BASE_MODE = "lemma_syn"
GAP_MODES = ["lemma", "glove"]
PREFER_MODE = "lemma"
TIEBREAK_MODE = "legacy"
K_FACTS = v1.K_FACTS                # 8
STORE_DIM = v1.STORE_DIM            # 4096
HELDOUT_PCT = 30

# ---- POSITIVE-CONTROL targets (MEASURED@ data/exp_intrinsic_foundation_loop_tie_gaps_powered_v1/metrics.json) ----
PC_N_POOL = 128
PC_ARM0_CORRECT = 48               # 0.3750
PC_FLOOR_CORRECT = 51              # 0.3984
PC_ARM1_CORRECT = 68               # 0.5312
PC_ARM2_CORRECT = 60               # 0.4688
PC_ARM3G_CORRECT = 47              # 0.3672

# ---- pre-registered bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned) ----
HP_MCNEMAR_P = 0.05
GOLD_ONLY_FLOOR = 1.0
NEG_INF = -1e9                     # score sentinel for an empty candidate set (below any specificity*relevance)

# reuse v1/defmatch_v1 leak-free glass-box machinery (identical objects -> identical profiles)
_content_set = dm1._content_set
build_def_profile = dm1.build_def_profile
grounded_align = dm1.grounded_align
_heldout_side = dm1._heldout_side

_T0 = [time.perf_counter()]


# ===========================================================================
# atomic metrics / start-marker / crash-diag / heartbeat  (same pattern as powered/v1/defmatch_v1)
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
# R2: tie-pool specificity IDF over the FILLER DISTRIBUTION (label words + predicate-object words)
# ===========================================================================
def build_tiepool_idf(contexts: List[dict]) -> Tuple[Dict[str, float], Counter, int]:
    """Document-frequency IDF over the n=128 tie-concept set. Each (unit,choice) is a 'document' whose bag =
    {label content-words} UNION {content-words of every definitional-predicate object in its ORACLE profile}.
    Generic hubs (water/energy/object/push) appear in MANY bags -> high dfc -> LOW idf -> suppressed. Rare
    discriminating predicate words -> LOW dfc -> HIGH idf -> dominate. Answer-agnostic (never uses correct_index)."""
    dfc: Counter = Counter()
    n_bags = 0
    for ctx in contexts:
        for c in ctx["valid"]:
            ci = c["choice_index"]
            bag: set = set()
            bag |= _content_set(c["choice_text"])                       # R1: label words are part of the vocab
            for (_rel, obj) in ctx["def_oracle_prof"].get(ci, []):
                bag |= _content_set(obj)
            if bag:
                n_bags += 1
                for w in bag:
                    dfc[w] += 1
    idf = {w: math.log((1.0 + n_bags) / (1.0 + dfc[w])) for w in dfc}
    return idf, dfc, n_bags


def _idf_of(w: str, idf: Dict[str, float], n_bags: int) -> float:
    """idf lookup; an UNSEEN word (df=0, maximally specific) gets the ceiling idf = log(1+N_bags)."""
    return idf.get(w, math.log(1.0 + n_bags) if n_bags > 0 else 1.0)


def specificity(text: str, idf: Dict[str, float], n_bags: int) -> float:
    """R2 specificity weight of a candidate predicate = sum of tie-pool idf over its UNIQUE content-words."""
    return float(sum(_idf_of(w, idf, n_bags) for w in _content_set(text)))


# ===========================================================================
# R1+R3: refined match -- label is a candidate; per-candidate discriminating-score; best candidate decides
# ===========================================================================
def grounded_pred_score(text: str, stem_vec: np.ndarray, encode: Callable[[str], np.ndarray],
                        idf: Dict[str, float], n_bags: int) -> float:
    """GROUNDED discriminating-score of a candidate = specificity(text) * cosine(encode(text), stem).
    Specificity suppresses generic hubs; cosine measures relevance to the stem (encoder held CONSTANT vs GloVe
    arms -> STRUCTURE is the one variable)."""
    ws = _content_set(text)
    if not ws:
        return NEG_INF
    return specificity(text, idf, n_bags) * grounded_align(encode, text, stem_vec)


def symbolic_pred_score(text: str, stem_content: set, idf: Dict[str, float], n_bags: int) -> float:
    """SYMBOLIC (GloVe-free) discriminating-score = sum of tie-pool idf over content-words SHARED with the stem
    (rarity-weighted lexical overlap). A predicate that shares a RARE word with the stem scores high; a generic
    shared word (water/energy) contributes almost nothing. Purely propositional assignment-lookup."""
    shared = _content_set(text) & stem_content
    if not shared:
        return 0.0
    return float(sum(_idf_of(w, idf, n_bags) for w in shared))


def decide_by_refined_def(valid: List[dict], profile_per_choice: Dict[int, List[Tuple[str, str]]],
                          pred_score: Callable[[str, str], float]) -> int:
    """R1+R3: candidates for each choice = [LABEL=choice_text] + its definitional predicates. Each candidate
    gets a discriminating-score (specificity*relevance); the BEST candidate is the choice's score (monotone in
    facts: more true facts add more candidates, hubs suppressed -> non-lossy). Highest-scoring choice wins.
    GUARDRAIL: single valid choice (gold_only) returned UNCHANGED. Deterministic lowest-index tiebreak."""
    if len(valid) == 1:
        return valid[0]["choice_index"]
    scored = []
    for c in valid:
        ci = c["choice_index"]
        cands = [("LABEL", c["choice_text"])] + list(profile_per_choice.get(ci, []))
        best = NEG_INF
        for (rel, txt) in cands:
            s = pred_score(txt, rel)
            if s > best:
                best = s
        scored.append((-best, ci))              # higher score first; lower index breaks exact ties
    scored.sort()
    return scored[0][1]


# ===========================================================================
# LADDER over the powered pool -- reused arms IMPORTED (identical), refined arms added
# ===========================================================================
def evaluate_pool(reasoner: DerivationReasoner, pool: List[dict], output_dir: str,
                  index: Dict[str, List[int]], facts: List[dict], wn,
                  encode: Callable[[str], np.ndarray], seed: int) -> dict:
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
        stem_content = _content_set(q["stem"])

        oracle_texts: Dict[int, List[str]] = {}
        oracle_dicts: Dict[int, List[dict]] = {}
        for c in valid:
            fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
            sel = v1._select_facts(facts, fids, K_FACTS)
            oracle_texts[c["choice_index"]] = [f["text"] for f in sel]
            oracle_dicts[c["choice_index"]] = sel
        auto_dicts: Dict[int, List[dict]] = {}
        for c in valid:
            fids = v1.retrieve_fact_ids(index, c["choice_text"], wn, use_syn=False)
            auto_dicts[c["choice_index"]] = v1._select_facts(facts, fids, K_FACTS)
        # ARM2 (reused GloVe autonomous) uses v1.autonomous_facts UNCHANGED (identical draw order).
        auto_texts, clog = v1.autonomous_facts(valid, index, facts, wn, seed + ui)
        for k in consolidation_totals:
            consolidation_totals[k] += clog[k]

        def_oracle_prof = {c["choice_index"]: build_def_profile(oracle_dicts[c["choice_index"]], seed + ui)
                           for c in valid}
        def_auto_prof = {c["choice_index"]: build_def_profile(auto_dicts[c["choice_index"]], seed + ui + 7919)
                         for c in valid}

        contexts.append({
            "split": unit["split"], "qid": unit["qid"], "mode": unit["mode"], "ci": ci,
            "valid": valid, "stem_vec": stem_vec, "stem_content": stem_content,
            "oracle_texts": oracle_texts, "oracle_dicts": oracle_dicts, "auto_texts": auto_texts,
            "def_oracle_prof": def_oracle_prof, "def_auto_prof": def_auto_prof,
            "gold_text": next((c["choice_text"] for c in valid if c["choice_index"] == ci), ""),
            "arm0_chosen": unit["arm0_chosen"], "arm0_correct": unit["arm0_correct"],
        })
        if (ui + 1) % 20 == 0:
            _heartbeat(output_dir, "ladder_pass1", {"done": ui + 1, "total": n_units})

    # ---- R2: build the tie-pool specificity IDF from ALL profiles/labels (answer-agnostic) ----
    idf, dfc, n_bags = build_tiepool_idf(contexts)
    _heartbeat(output_dir, "tiepool_idf_built", {"n_bags": n_bags, "vocab": len(idf)})

    # global pools for the GLOBAL-scramble arms: reused arm uses TEXTS, refined arm uses DICTS (tagged by qid).
    global_pool_texts = [(c["qid"], fts) for c in contexts for fts in c["oracle_texts"].values() if fts]
    global_pool_dicts = [(c["qid"], fd) for c in contexts for fd in c["oracle_dicts"].values() if fd]

    # ---- PASS 2 ----
    per_tie: List[dict] = []
    grng = np.random.default_rng(seed * 101 + 5)         # reused-arm rng (replicate powered EXACT draw order)
    rdgrng = np.random.default_rng(seed * 211 + 7)       # SEPARATE rng for the refined global-scramble (never perturbs grng)
    for ctx in contexts:
        qid, ci, valid = ctx["qid"], ctx["ci"], ctx["valid"]
        stem_vec, stem_content = ctx["stem_vec"], ctx["stem_content"]
        oracle_texts, auto_texts = ctx["oracle_texts"], ctx["auto_texts"]
        no_facts = {c["choice_index"]: [] for c in valid}

        # --- reused GloVe arms (IMPORTED v1.decide_by_meaning; BYTE-IDENTICAL draw order to powered) ---
        floor_pick = v1.decide_by_meaning(valid, no_facts, encode, stem_vec)
        arm1_pick = v1.decide_by_meaning(valid, oracle_texts, encode, stem_vec)
        arm2_pick = v1.decide_by_meaning(valid, auto_texts, encode, stem_vec)
        arm3w_pick = v1.decide_by_meaning(
            valid, v1.scramble_facts(valid, oracle_texts, seed + len(per_tie)), encode, stem_vec)
        other_t = [fts for (sq, fts) in global_pool_texts if sq != qid]
        gscr_t = {c["choice_index"]: (list(other_t[int(grng.integers(len(other_t)))]) if other_t else [])
                  for c in valid}
        arm3g_pick = v1.decide_by_meaning(valid, gscr_t, encode, stem_vec)

        # --- refined global-scramble profiles (each choice gets ANOTHER question's oracle fact DICTS) ---
        other_d = [fd for (sq, fd) in global_pool_dicts if sq != qid]
        rdef_scr_prof = {}
        for c in valid:
            if other_d:
                fd = other_d[int(rdgrng.integers(len(other_d)))]
                rdef_scr_prof[c["choice_index"]] = build_def_profile(fd, seed + len(per_tie) + 104729)
            else:
                rdef_scr_prof[c["choice_index"]] = []

        # --- NEW refined arms: label + tie-pool IDF specificity * relevance, best candidate decides ---
        g_score = (lambda txt, rel="": grounded_pred_score(txt, stem_vec, encode, idf, n_bags))
        s_score = (lambda txt, rel="": symbolic_pred_score(txt, stem_content, idf, n_bags))
        rdef_oracle_pick = decide_by_refined_def(valid, ctx["def_oracle_prof"], g_score)
        rdef_auto_pick = decide_by_refined_def(valid, ctx["def_auto_prof"], g_score)
        rdef_scr_pick = decide_by_refined_def(valid, rdef_scr_prof, g_score)
        rdef_sym_auto_pick = decide_by_refined_def(valid, ctx["def_auto_prof"], s_score)
        rdef_sym_scr_pick = decide_by_refined_def(valid, rdef_scr_prof, s_score)

        n_oracle_prof = sum(len(p) for p in ctx["def_oracle_prof"].values())
        n_auto_prof = sum(len(p) for p in ctx["def_auto_prof"].values())
        gold_has_prof = int(len(ctx["def_auto_prof"].get(ci, [])) > 0)
        per_tie.append({
            "split": ctx["split"], "qid": qid, "mode": ctx["mode"], "correct_index": ci,
            "n_valid": len(valid), "valid_indices": [c["choice_index"] for c in valid],
            "gold_text": ctx["gold_text"], "heldout_side": _heldout_side(ctx["gold_text"]),
            "arm0_pick": ctx["arm0_chosen"], "arm0_correct": int(ctx["arm0_correct"]),
            "floor_pick": floor_pick, "arm1_pick": arm1_pick, "arm2_pick": arm2_pick,
            "arm3_within_pick": arm3w_pick, "arm3_global_pick": arm3g_pick,
            "rdef_oracle_pick": rdef_oracle_pick, "rdef_auto_pick": rdef_auto_pick,
            "rdef_scr_pick": rdef_scr_pick, "rdef_sym_auto_pick": rdef_sym_auto_pick,
            "rdef_sym_scr_pick": rdef_sym_scr_pick,
            "floor_correct": int(floor_pick == ci), "arm1_correct": int(arm1_pick == ci),
            "arm2_correct": int(arm2_pick == ci), "arm3_within_correct": int(arm3w_pick == ci),
            "arm3_global_correct": int(arm3g_pick == ci),
            "rdef_oracle_correct": int(rdef_oracle_pick == ci), "rdef_auto_correct": int(rdef_auto_pick == ci),
            "rdef_scr_correct": int(rdef_scr_pick == ci),
            "rdef_sym_auto_correct": int(rdef_sym_auto_pick == ci),
            "rdef_sym_scr_correct": int(rdef_sym_scr_pick == ci),
            "n_oracle_facts": sum(len(v) for v in oracle_texts.values()),
            "n_oracle_prof": n_oracle_prof, "n_auto_prof": n_auto_prof, "gold_has_prof": gold_has_prof,
        })

    return {"per_tie": per_tie, "consolidation_totals": consolidation_totals, "n_units": n_units,
            "contexts_for_profiles": contexts, "idf": idf, "dfc": dfc, "n_bags": n_bags}


_ARM_KEYS = ("arm0_correct", "floor_correct", "arm1_correct", "arm2_correct", "arm3_within_correct",
             "arm3_global_correct", "rdef_oracle_correct", "rdef_auto_correct", "rdef_scr_correct",
             "rdef_sym_auto_correct", "rdef_sym_scr_correct")


def _acc(rows: List[dict], key: str) -> float:
    return round(sum(r[key] for r in rows) / len(rows), 4) if rows else 0.0


def _breakdown(rows: List[dict]) -> dict:
    return {"n": len(rows), **{k.replace("_correct", ""): _acc(rows, k) for k in _ARM_KEYS}}


def _mcnemar_rows(rows: List[dict], a_key: str, b_key: str, a_name: str, b_name: str) -> dict:
    return powered.mcnemar([r[a_key] for r in rows], [r[b_key] for r in rows], a_name, b_name)


# ===========================================================================
# gold_only preservation (single-valid decisions UNCHANGED under the refined match too)
# ===========================================================================
def check_gold_only_preserved(reasoner, cfg_cache, splits, index, facts, wn, encode,
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
        base_pq = cfg_cache[split_name]["base"]["per_q"]
        go_qids = sorted(qid for qid, r in base_pq.items() if r["subset"] == "gold_only")[:cap]
        reasoner.link_mode = BASE_MODE
        reasoner.tiebreak_mode = TIEBREAK_MODE
        for qid in go_qids:
            q = qmap[qid]
            res = reasoner._reason_arm(q, reasoner.arms["typed"])
            valid = v1._valid_choices(res["per_choice"])
            if len(valid) != 1:
                continue
            stem_vec = v1._l2(np.asarray(encode(q["stem"]), dtype=np.float32))
            c0 = {"choice_index": valid[0]["choice_index"], "choice_text": valid[0]["choice_text"]}
            fids = v1.retrieve_fact_ids(index, c0["choice_text"], wn, use_syn=True)
            prof = {c0["choice_index"]: build_def_profile(v1._select_facts(facts, fids, K_FACTS), seed)}
            pick = decide_by_refined_def([c0], prof, lambda txt, rel="": 0.0)  # single valid: guardrail path
            checked += 1
            if pick != c0["choice_index"]:
                preserved = 0.0
    return preserved, checked


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", PC_N_POOL)
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
    pool, pool_meta = powered.build_pool(reasoner, output_dir, splits, n_sample, seed)
    _heartbeat(output_dir, "pool_ready", {"n_pool": len(pool), "detect": pool_meta["detect"]})

    rep = evaluate_pool(reasoner, pool, output_dir, index, facts, wn, encode, seed)
    per_tie = rep["per_tie"]
    idf, dfc, n_bags = rep["idf"], rep["dfc"], rep["n_bags"]
    _heartbeat(output_dir, "ladder_done", {"n_units": rep["n_units"]})

    go_preserved, go_checked = check_gold_only_preserved(
        reasoner, pool_meta["cfg_cache"], splits, index, facts, wn, encode, n_sample, seed)
    reasoner.link_mode = BASE_MODE

    # ---- arm accuracies ----
    arms = {
        "arm0_legacy_combiner": _acc(per_tie, "arm0_correct"),
        "floor_mm_no_facts": _acc(per_tie, "floor_correct"),
        "arm1_oracle_ceiling": _acc(per_tie, "arm1_correct"),
        "arm2_autonomous_loop": _acc(per_tie, "arm2_correct"),
        "arm3_scramble_within": _acc(per_tie, "arm3_within_correct"),
        "arm3_scramble_global": _acc(per_tie, "arm3_global_correct"),
        "rdef_oracle_grounded": _acc(per_tie, "rdef_oracle_correct"),
        "rdef_auto_grounded": _acc(per_tie, "rdef_auto_correct"),
        "rdef_scramble_grounded": _acc(per_tie, "rdef_scr_correct"),
        "rdef_auto_symbolic": _acc(per_tie, "rdef_sym_auto_correct"),
        "rdef_scramble_symbolic": _acc(per_tie, "rdef_sym_scr_correct"),
    }

    # ---- McNemar: FULL pool ----
    mc = {
        "rdefauto_vs_rdefscr": _mcnemar_rows(per_tie, "rdef_auto_correct", "rdef_scr_correct", "rdefauto", "rdefscr"),
        "rdefauto_vs_arm2": _mcnemar_rows(per_tie, "rdef_auto_correct", "arm2_correct", "rdefauto", "arm2"),
        "rdefauto_vs_arm1": _mcnemar_rows(per_tie, "rdef_auto_correct", "arm1_correct", "rdefauto", "arm1"),
        "rdefauto_vs_floor": _mcnemar_rows(per_tie, "rdef_auto_correct", "floor_correct", "rdefauto", "floor"),
        "rdeforacle_vs_rdefauto": _mcnemar_rows(per_tie, "rdef_oracle_correct", "rdef_auto_correct",
                                                "rdeforacle", "rdefauto"),
        "rdefsymauto_vs_rdefsymscr": _mcnemar_rows(per_tie, "rdef_sym_auto_correct", "rdef_sym_scr_correct",
                                                   "rdefsymauto", "rdefsymscr"),
    }

    # ---- McNemar: PER-SPLIT (the DECISIVE gate is Challenge) ----
    def split_rows(sn):
        return [r for r in per_tie if r["split"] == sn]
    mc_by_split = {}
    for sn, _ in splits:
        sr = split_rows(sn)
        mc_by_split[sn] = {
            "n": len(sr),
            "rdefauto_vs_rdefscr": _mcnemar_rows(sr, "rdef_auto_correct", "rdef_scr_correct", "rdefauto", "rdefscr"),
            "rdefauto_vs_arm2": _mcnemar_rows(sr, "rdef_auto_correct", "arm2_correct", "rdefauto", "arm2"),
            "rdefauto_vs_arm1": _mcnemar_rows(sr, "rdef_auto_correct", "arm1_correct", "rdefauto", "arm1"),
            "rdefsymauto_vs_rdefsymscr": _mcnemar_rows(sr, "rdef_sym_auto_correct", "rdef_sym_scr_correct",
                                                       "rdefsymauto", "rdefsymscr"),
        }

    by_arity = {f"{k}_way": _breakdown([r for r in per_tie if r["n_valid"] == k]) for k in (2, 3, 4)}
    by_arity["ge5_way"] = _breakdown([r for r in per_tie if r["n_valid"] >= 5])
    by_split = {sn: _breakdown(split_rows(sn)) for sn, _ in splits}
    by_mode = {m: _breakdown([r for r in per_tie if r["mode"] == m]) for m in GAP_MODES}
    by_heldout = {side: _breakdown([r for r in per_tie if r["heldout_side"] == side])
                  for side in ("train", "heldout")}

    # ---- POSITIVE CONTROL: reused arms reproduce powered EXACT ----
    smoke_run = (n_sample != 0)
    col = lambda k: [r[k] for r in per_tie]
    reused_counts = {"n_pool": len(per_tie),
                     "arm0": sum(col("arm0_correct")), "floor": sum(col("floor_correct")),
                     "arm1": sum(col("arm1_correct")), "arm2": sum(col("arm2_correct")),
                     "arm3global": sum(col("arm3_global_correct"))}
    pc_ok = (reused_counts["n_pool"] == PC_N_POOL and reused_counts["arm0"] == PC_ARM0_CORRECT
             and reused_counts["floor"] == PC_FLOOR_CORRECT and reused_counts["arm1"] == PC_ARM1_CORRECT
             and reused_counts["arm2"] == PC_ARM2_CORRECT and reused_counts["arm3global"] == PC_ARM3G_CORRECT)
    positive_control = {
        "reused_counts_measured": reused_counts,
        "expected": {"n_pool": PC_N_POOL, "arm0": PC_ARM0_CORRECT, "floor": PC_FLOOR_CORRECT,
                     "arm1": PC_ARM1_CORRECT, "arm2": PC_ARM2_CORRECT, "arm3global": PC_ARM3G_CORRECT},
        "reproduces_powered_29573": bool(pc_ok),
        "note": ("full-set only; smoke subsamples so the pool is NOT the canonical 128"
                 if smoke_run else "full ARC test sets; reused arms must reproduce powered EXACT"),
    }

    # ---- R3 sanity: oracle >= auto (lossy scoring fixed?) FULL + per-split ----
    oracle_ge_auto = {
        "full": {"rdef_oracle": arms["rdef_oracle_grounded"], "rdef_auto": arms["rdef_auto_grounded"],
                 "oracle_ge_auto": bool(arms["rdef_oracle_grounded"] >= arms["rdef_auto_grounded"])},
    }
    for sn, _ in splits:
        bd = by_split[sn]
        oracle_ge_auto[sn] = {"rdef_oracle": bd["rdef_oracle"], "rdef_auto": bd["rdef_auto"],
                              "oracle_ge_auto": bool(bd["rdef_oracle"] >= bd["rdef_auto"])}

    # ---- R2 GLASS-BOX: which predicates the specificity weighting up/down-weighted ----
    idf_sorted = sorted(idf.items(), key=lambda kv: kv[1])
    down_weighted = [{"word": w, "dfc": int(dfc[w]), "idf": round(iv, 4)} for w, iv in idf_sorted[:20]]
    up_weighted = [{"word": w, "dfc": int(dfc[w]), "idf": round(iv, 4)} for w, iv in idf_sorted[-20:]][::-1]
    idf_glassbox = {
        "n_bags": n_bags, "vocab": len(idf),
        "scheme": "idf(w)=log((1+N_bags)/(1+dfc(w))); dfc=# (unit,choice) profile-bags (label+object words) with w",
        "most_down_weighted_generic_hubs": down_weighted,
        "most_up_weighted_discriminators": up_weighted,
    }

    # ---- def-profile coverage preflight ----
    n_gold_with_prof = sum(1 for r in per_tie if r["gold_has_prof"])
    cov_gold = round(n_gold_with_prof / len(per_tie), 4) if per_tie else 0.0
    coverage = {
        "gold_units_with_profile": n_gold_with_prof, "n_units": len(per_tie),
        "gold_profile_coverage": cov_gold,
        "n_unique_gold_concepts": len(sorted({r["gold_text"] for r in per_tie if r["gold_text"]})),
        "mean_oracle_profile_facts_per_unit": round(sum(col("n_oracle_prof")) / len(per_tie), 3) if per_tie else 0.0,
        "mean_auto_profile_facts_per_unit": round(sum(col("n_auto_prof")) / len(per_tie), 3) if per_tie else 0.0,
        "thin_flag": bool(cov_gold < 0.5),
    }

    # ---- FEED B: per-concept role-slot profiles + held-out split ----
    concept_profiles: Dict[str, Dict[str, set]] = {}
    concept_side: Dict[str, str] = {}
    for ctx in rep["contexts_for_profiles"]:
        for c in ctx["valid"]:
            txt = c["choice_text"]
            if not txt:
                continue
            prof = ctx["def_oracle_prof"].get(c["choice_index"], [])
            if not prof:
                continue
            slot = concept_profiles.setdefault(txt, defaultdict(set))
            for (rel, obj) in prof:
                slot[rel].add(obj)
    feed_b_profiles = {}
    for txt, slot in sorted(concept_profiles.items()):
        feed_b_profiles[txt] = {rel: sorted(objs) for rel, objs in sorted(slot.items())}
        concept_side[txt] = _heldout_side(txt)

    # ---- deltas ----
    d = {
        "rdefauto_minus_rdefscr": round(arms["rdef_auto_grounded"] - arms["rdef_scramble_grounded"], 4),
        "rdefauto_minus_arm2": round(arms["rdef_auto_grounded"] - arms["arm2_autonomous_loop"], 4),
        "rdefauto_minus_arm1": round(arms["rdef_auto_grounded"] - arms["arm1_oracle_ceiling"], 4),
        "rdefauto_minus_floor": round(arms["rdef_auto_grounded"] - arms["floor_mm_no_facts"], 4),
        "rdeforacle_minus_rdefauto": round(arms["rdef_oracle_grounded"] - arms["rdef_auto_grounded"], 4),
        "rdefsymauto_minus_rdefsymscr": round(arms["rdef_auto_symbolic"] - arms["rdef_scramble_symbolic"], 4),
    }
    # per-split challenge deltas (decisive)
    ch = by_split["challenge"]
    d_challenge = {
        "rdefauto_minus_rdefscr": round(ch["rdef_auto"] - ch["rdef_scr"], 4),
        "rdefauto_minus_arm2": round(ch["rdef_auto"] - ch["arm2"], 4),
        "rdefauto_minus_arm1": round(ch["rdef_auto"] - ch["arm1"], 4),
        "rdefsymauto_minus_rdefsymscr": round(ch["rdef_sym_auto"] - ch["rdef_sym_scr"], 4),
    }

    # ---- pre-registered bands (DECISIVE gate = CHALLENGE split) ----
    ch_mc = mc_by_split["challenge"]
    challenge_lift = (ch_mc["rdefauto_vs_rdefscr"]["p_exact"] < HP_MCNEMAR_P
                      and ch["rdef_auto"] > ch["rdef_scr"])
    challenge_wrong_dir_sig = (ch_mc["rdefauto_vs_rdefscr"]["p_exact"] < HP_MCNEMAR_P
                               and ch["rdef_auto"] < ch["rdef_scr"])
    # secondary signal (informative only; NOT the gate): any full-pool or Easy lift over scramble
    full_lift = (mc["rdefauto_vs_rdefscr"]["p_exact"] < HP_MCNEMAR_P
                 and arms["rdef_auto_grounded"] > arms["rdef_scramble_grounded"])
    easy_mc = mc_by_split["easy"]
    easy_lift = (easy_mc["rdefauto_vs_rdefscr"]["p_exact"] < HP_MCNEMAR_P
                 and by_split["easy"]["rdef_auto"] > by_split["easy"]["rdef_scr"])
    guardrails_ok = (go_preserved >= GOLD_ONLY_FLOOR) and (pc_ok or smoke_run)

    bands = {
        "CHALLENGE_rdefauto_lifts_scramble_p_lt_0.05": bool(challenge_lift),
        "gold_only_preserved": go_preserved >= GOLD_ONLY_FLOOR,
        "positive_control_reproduces_powered": bool(pc_ok or smoke_run),
        "secondary_full_pool_lift": bool(full_lift),
        "secondary_easy_lift": bool(easy_lift),
    }

    if not pc_ok and not smoke_run:
        tier, verdict = "POSITIVE_CONTROL_FAIL", "REPRODUCE_POWERED_29573_MISMATCH"
    elif challenge_lift and guardrails_ok:
        tier, verdict = "HARD_PASS", "REFINED_DEFINITIONAL_MATCH_LIFTS_CHALLENGE_OVER_SCRAMBLE_GREENLIGHT_B"
    elif challenge_wrong_dir_sig:
        tier, verdict = "MIDDLE_BAND", "CHALLENGE_SIGNIFICANT_BUT_WRONG_DIRECTION_INVESTIGATE"
    elif full_lift or easy_lift:
        tier, verdict = "MIDDLE_BAND", "LIFT_ON_FULL_OR_EASY_BUT_CHALLENGE_COLLAPSES_NOT_DECISIVE"
    else:
        tier, verdict = "HONEST_NEG", "DEFINITIONAL_GROUNDING_DEAD_ON_CHALLENGE_DISCONFIRM_B_ROUTE_ELSEWHERE"

    summary = (
        f"REFINED DEF-MATCH (label + tie-pool IDF + specificity*relevance monotone-max) on n={len(per_tie)} "
        f"genuine ties | CHALLENGE n={ch['n']}: RDEF_AUTO={ch['rdef_auto']:.3f} vs RDEF_SCR={ch['rdef_scr']:.3f} "
        f"(d={d_challenge['rdefauto_minus_rdefscr']:+.3f} p={ch_mc['rdefauto_vs_rdefscr']['p_exact']:.4f} "
        f"b={ch_mc['rdefauto_vs_rdefscr']['rdefauto_wins']},c={ch_mc['rdefauto_vs_rdefscr']['rdefscr_wins']}) | "
        f"CHAL GloVe ARM2={ch['arm2']:.3f} ARM1={ch['arm1']:.3f} | FULL RDEF_AUTO={arms['rdef_auto_grounded']:.3f} "
        f"RDEF_ORACLE={arms['rdef_oracle_grounded']:.3f} RDEF_SCR={arms['rdef_scramble_grounded']:.3f} "
        f"SYM_AUTO={arms['rdef_auto_symbolic']:.3f} | oracle>=auto(full)={oracle_ge_auto['full']['oracle_ge_auto']} "
        f"| cov_gold={cov_gold:.2f}{' THIN' if coverage['thin_flag'] else ''} gold_only={go_preserved:.2f} "
        f"repro_powered={pc_ok} | tier={tier}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "REFINED definitional-structure match fixing the 3 operationalization flaws defmatch_v1's VET found: "
            "(R1) KEEP the concept label as a scored candidate alongside the definitional predicates (v1 dropped "
            "it); (R2) tie-pool IDF specificity weighting over the filler distribution across the n=128 tie set "
            "so generic hubs (water/energy/object/push) cannot dominate; (R3) non-lossy monotone aggregation -- "
            "per candidate discriminating-score = specificity*relevance, best candidate decides (more true facts "
            "add more discriminating candidates -> oracle>=auto). Two backends: GROUNDED (specificity*cosine, "
            "encoder held CONSTANT vs GloVe arms = structure is the one var) and SYMBOLIC (GloVe-free rarity-"
            "weighted lexical overlap). Everything else IMPORTED UNCHANGED: leak-free arms + n=128 tie pool + "
            "controls from powered_v1 (build_pool, mcnemar) + v1 (retrieval, autonomous loop, scramble) + "
            "defmatch_v1 (trust-gate glass-box def-profile). Reused ARM0/FLOOR/ARM1(GloVe oracle)/ARM2(GloVe "
            "auto)/ARM3within/ARM3global reproduce powered EXACT (positive control 128/48/51/68/60/47). "
            "HARD CAN-FAIL BAR (decisive, VET-mandated): the refined match must LIFT OVER SCRAMBLE ON THE "
            "CHALLENGE SPLIT (n=44) -- primary gate = per-split Challenge McNemar RDEF_AUTO vs RDEF_SCR p<0.05 "
            "AND right direction. HARD_PASS => definitional grounding REAL, greenlight build B; HONEST_NEG => "
            "Challenge collapses to scramble => definitional/taxonomic grounding genuinely dead, B DISCONFIRMED, "
            "route to a different grounding (saves the B investment). Reports per-split (Challenge+Easy) McNemar "
            "vs scramble AND vs GloVe ARM2/ARM1; oracle>=auto sanity; IDF up/down-weighted tokens (glass-box). "
            "Anti-leak: acquisition answer-agnostic; IDF from objects/labels only; match uses stem+profile+label "
            "never the answer; correct_index only in tally. HELD-OUT ARC; rules not from test labels. NOTE: "
            "grounded arms use the GloVe encoder to GROUND predicate text (structure is the one variable, not "
            "the encoder); SYMBOLIC is the GloVe-free companion. VET-PENDING; no atom banking."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_sample_per_split": n_sample, "seed": seed, "rules_path": RULES_PATH,
                   "n_rules": len(rows), "base_mode": BASE_MODE, "gap_modes": GAP_MODES,
                   "prefer_mode": PREFER_MODE, "tiebreak_mode": TIEBREAK_MODE, "k_facts": K_FACTS,
                   "store_dim": STORE_DIM, "heldout_pct": HELDOUT_PCT,
                   "pool_source": "exp_intrinsic_foundation_loop_tie_gaps_powered_v1.build_pool (IMPORTED)",
                   "reused_arms_source": "exp_intrinsic_foundation_loop_tie_gaps_v1 (IMPORTED UNCHANGED)",
                   "def_profile_source": "exp_intrinsic_foundation_loop_tie_gaps_defmatch_v1.build_def_profile (IMPORTED)",
                   "the_refinements": "R1 keep label as candidate; R2 tie-pool IDF specificity; R3 specificity*relevance monotone-max (non-lossy)",
                   "grounded_backend": "specificity(idf-sum)*cosine(encode(pred),stem) -- encoder constant, structure is the one var",
                   "symbolic_backend": "sum idf over content(pred) INTERSECT content(stem) -- GloVe-free rarity-weighted overlap",
                   "decisive_gate": "CHALLENGE-split McNemar RDEF_AUTO vs RDEF_SCR p<0.05 AND right direction",
                   "progress_logging": "heartbeat jsonl + stdout flush per stage/20-unit"},
        "n_pool": len(per_tie), "pool_detection": pool_meta["detect"],
        "positive_control": positive_control,
        "arms": arms, "deltas": d, "deltas_challenge": d_challenge,
        "mcnemar_full": mc, "mcnemar_by_split": mc_by_split,
        "oracle_ge_auto_sanity": oracle_ge_auto,
        "idf_glassbox": idf_glassbox,
        "breakdown_by_arity": by_arity, "breakdown_by_split": by_split, "breakdown_by_mode": by_mode,
        "breakdown_by_heldout_concept": by_heldout,
        "coverage": coverage,
        "acquisition": {"source": "WorldTree tablestore (parse_tablestore_typed, ALL relations)",
                        "n_facts": len(facts), "n_concept_keys": len(index),
                        "trust_gate": "hd_fact_store.HDFactStore (WorldTree=TRUST_HIGH)",
                        "totals": rep["consolidation_totals"]},
        "gold_only_preserved": round(go_preserved, 4), "gold_only_checked": go_checked,
        "preregistered_bands": bands, "n_bands_pass": sum(1 for vv in bands.values() if vv),
        "bands_definition": {
            "hard_pass": ("CHALLENGE-split McNemar RDEF_AUTO vs RDEF_SCR p<0.05 AND rdef_auto>rdef_scr on "
                          "Challenge (n=44) -- with gold_only preserved + positive-control reproduces powered "
                          "=> definitional grounding REAL, greenlight build B"),
            "honest_neg": ("Challenge RDEF_AUTO does NOT significantly beat scramble (collapses) => "
                           "definitional/taxonomic grounding genuinely dead, B DISCONFIRMED, route elsewhere; "
                           "saves the B investment"),
            "middle_band": ("lift on FULL pool or EASY but Challenge collapses (not decisive), OR Challenge "
                            "significant in the WRONG direction (investigate)"),
        },
        "feed_b": {
            "concept_role_slot_profiles": feed_b_profiles,
            "concept_heldout_side": concept_side,
            "n_concepts_with_profile": len(feed_b_profiles),
            "heldout_pct": HELDOUT_PCT,
            "note": ("per-concept definitional role-slot profile {relation:[objects]} + deterministic sha256 "
                     "held-out split; B learns to predict grounded features for held-out concepts"),
        },
        "per_tie": per_tie,
        "REQUIRED_FIELDS": ["verdict", "tier", "n_pool", "positive_control", "arms", "deltas_challenge",
                            "mcnemar_by_split", "oracle_ge_auto_sanity", "idf_glassbox", "preregistered_bands",
                            "gold_only_preserved", "coverage", "breakdown_by_split",
                            "breakdown_by_heldout_concept", "feed_b"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== REFINED DEFINITIONAL-STRUCTURE MATCH (v2) RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"bands: {bands} -> tier={tier}", flush=True)
    print(f"CHALLENGE McNemar rdefauto_vs_rdefscr: {ch_mc['rdefauto_vs_rdefscr']}", flush=True)
    print(f"CHALLENGE McNemar rdefauto_vs_arm2:    {ch_mc['rdefauto_vs_arm2']}", flush=True)
    print(f"CHALLENGE McNemar rdefauto_vs_arm1:    {ch_mc['rdefauto_vs_arm1']}", flush=True)
    print(f"oracle_ge_auto: {oracle_ge_auto}", flush=True)
    print(f"positive_control: {pc_ok} {reused_counts}", flush=True)
    print(f"by_split: {by_split}", flush=True)
    print(f"IDF down-weighted (hubs): {[x['word'] for x in down_weighted[:10]]}", flush=True)
    print(f"IDF up-weighted (discrim): {[x['word'] for x in up_weighted[:10]]}", flush=True)
    return metrics


# ===========================================================================
# self-test (real code path: planted REFINED discriminator + tie-pool IDF + REAL HDFactStore + REAL imports)
# ===========================================================================
def _self_test() -> None:
    print("[self-test] refined definitional-structure match v2 ...", flush=True)
    exercised = set()

    # planted 2-choice tie with near-synonym labels (the GloVe-collapse case). The discriminating signal lives
    # in a RARE definitional predicate word; a GENERIC HUB word ('water') is present in BOTH profiles to test
    # that the tie-pool IDF suppresses it (R2) and the refined aggregation still fires (R3), label kept (R1).
    stem = "which substance is the dissolved material spread evenly throughout a solution"
    gold_pred = "the dissolved solute substance"       # rare discriminator 'solute'/'dissolved'
    dist_pred = "the surrounding liquid water"          # 'water' is the generic hub
    hub_pred = "found in water"                          # both choices also carry the hub word
    vocab_words = _content_set(stem)
    for t in (gold_pred, dist_pred, hub_pred, "solute", "solvent"):
        vocab_words |= _content_set(t)
    vocab = {w: i for i, w in enumerate(sorted(vocab_words))}

    def enc(text: str) -> np.ndarray:
        v = np.zeros(len(vocab), dtype=np.float32)
        for w in arc._content_words(text, min_len=v1.MIN_LEN):
            if w in vocab:
                v[vocab[w]] += 1.0
        return v

    stem_vec = v1._l2(np.asarray(enc(stem), dtype=np.float32))
    stem_content = _content_set(stem)
    valid = [{"choice_index": 0, "choice_text": "solute"},     # gold (near-synonym label of the distractor)
             {"choice_index": 1, "choice_text": "solvent"}]    # distractor

    # planted tie-pool IDF: 'water' is a generic hub (high dfc -> low idf); 'dissolved'/'solute' rare (high idf).
    n_bags = 50
    dfc = {"water": 40, "liquid": 30, "substance": 25, "found": 20, "solution": 22,
           "dissolved": 2, "solute": 1, "surrounding": 8, "spread": 6, "evenly": 5, "material": 7, "solvent": 3}
    idf = {w: math.log((1.0 + n_bags) / (1.0 + dfc[w])) for w in dfc}
    assert idf["water"] < idf["dissolved"], "R2: generic hub 'water' must be down-weighted below 'dissolved'"
    assert idf["water"] < idf["solute"], "R2: generic hub 'water' must be down-weighted below 'solute'"
    exercised.add("build_tiepool_idf")

    g = lambda txt, rel="": grounded_pred_score(txt, stem_vec, enc, idf, n_bags)
    s = lambda txt, rel="": symbolic_pred_score(txt, stem_content, idf, n_bags)

    # (1) refined match FIRES: with the rare discriminating predicate present for gold, gold wins (label kept,
    #     hub suppressed). Both choices carry the hub_pred; only gold carries the rare 'dissolved solute'.
    prof_right = {0: [("KINDOF", gold_pred), ("PROP", hub_pred)],
                  1: [("KINDOF", dist_pred), ("PROP", hub_pred)]}
    pick_g = decide_by_refined_def(valid, prof_right, g)
    pick_s = decide_by_refined_def(valid, prof_right, s)
    assert pick_g == 0, f"R3 grounded: rare discriminating predicate must pick gold(0), got {pick_g}"
    assert pick_s == 0, f"R3 symbolic: rare discriminating predicate must pick gold(0), got {pick_s}"
    exercised.add("decide_by_refined_def")
    exercised.add("grounded_pred_score")
    exercised.add("symbolic_pred_score")

    # (2) CAN-FAIL: scramble the discriminating predicates across choices -> must NOT still pick gold.
    prof_scr = {0: [("KINDOF", dist_pred), ("PROP", hub_pred)],
                1: [("KINDOF", gold_pred), ("PROP", hub_pred)]}
    scr_g = decide_by_refined_def(valid, prof_scr, g)
    assert scr_g != 0, f"scrambled predicate must NOT pick gold (non-discriminating), got {scr_g}"
    print(f"[self-test] refined match fires: grounded->{pick_g} symbolic->{pick_s} scrambled->{scr_g}", flush=True)

    # (3) HUB-ONLY does not discriminate (both choices share the hub predicate + label reduces to floor):
    prof_hub = {0: [("PROP", hub_pred)], 1: [("PROP", hub_pred)]}
    _ = decide_by_refined_def(valid, prof_hub, g)  # deterministic; both driven by label+hub -> no crash

    # (4) gold_only guardrail: a SINGLE valid choice returned UNCHANGED
    solo = [{"choice_index": 2, "choice_text": "the only derivable answer"}]
    assert decide_by_refined_def(solo, {2: [("KINDOF", "irrelevant")]}, g) == 2, \
        "single valid choice must be returned unchanged (gold_only preserved)"
    exercised.add("gold_only_preserved")

    # (5) specificity weight monotone in rarity: rarer predicate text has higher specificity
    assert specificity("dissolved solute", idf, n_bags) > specificity("water liquid", idf, n_bags), \
        "R2 specificity: rare predicate must outweigh generic-hub predicate"
    exercised.add("specificity")

    # (6) REAL HDFactStore ingest -> glass-box role-slot profile round-trip (the trust-gate path)
    prof = build_def_profile(
        [{"uid": "u1", "relation": "KINDOF", "arg0": "solute", "arg1": "dissolved substance in a solution",
          "text": "solute dissolved substance in a solution"}], seed=7)
    assert len(prof) == 1 and prof[0][0] == "KINDOF" and "dissolved" in prof[0][1], prof
    exercised.add("build_def_profile")

    # (7) reused arms + pool builder are the imported objects; real acquisition index builds a real profile
    for fn in ("build_pool", "mcnemar"):
        assert hasattr(powered, fn), f"powered missing reused {fn}"
    for fn in ("decide_by_meaning", "retrieve_fact_ids", "_select_facts", "autonomous_facts",
               "scramble_facts", "build_acq_index", "_valid_choices"):
        assert hasattr(v1, fn), f"v1 missing reused {fn}"
    exercised.add("reused_imports")
    idx, facts = v1.build_acq_index()
    assert len(facts) > 1000, f"real acquisition index must load many facts, got {len(facts)}"
    fids = v1.retrieve_fact_ids(idx, "condensation", wn=None, use_syn=False)
    real_prof = build_def_profile(v1._select_facts(facts, fids, K_FACTS), seed=3)
    assert len(real_prof) >= 1, "must build a real role-slot profile for 'condensation'"
    exercised.add("real_code_path")
    assert os.path.exists(arc._EASY_TEST) and os.path.exists(arc._CHAL_TEST), "ARC Easy+Challenge must exist"
    print(f"[self-test] real profile(condensation)={real_prof[:2]} n_facts={len(facts)}", flush=True)

    need = {"build_tiepool_idf", "decide_by_refined_def", "grounded_pred_score", "symbolic_pred_score",
            "gold_only_preserved", "specificity", "build_def_profile", "reused_imports", "real_code_path"}
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

    n_sample = args.n if args.mode == "smoke" else 0
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
