"""exp_intrinsic_foundation_loop_tie_gaps_v1 -- does the INTRINSIC FOUNDATION LOOP, instantiated on the
composed reasoner's OWN tie-gaps, actually RESOLVE the ties end-to-end (not just "it ran")?

THE LOOP (compose banked pieces; do NOT rebuild them): (1) GAP DETECTION -- the reasoner's OWN 44 GENUINE
lemma ties (both gold + a distractor co-derive; the substrate's answer-agnostic "can't decide" flag), exactly
reproduced from exp_arc_reasoner_link_precision_tie_prune_v1 via its own eval_config/classify functions.
(2) ACQUISITION (ANSWER-AGNOSTIC) -- for the CONCEPTS in each tied CHOICE (never the answer), retrieve
discriminating definitional/propositional facts from the WorldTree tablestore (parse_tablestore_typed, ALL
relations: KINDOF/SYNONYMY/CAUSE/USEDFOR/CHANGE/IFTHEN/...). (3) CONSOLIDATION -- ingest through the
hd_fact_store.py trust-gate (WorldTree = TRUST_HIGH) + a sleep pass that keeps definitional facts EPISODIC
(assignment-lookup, MDL compression=1). (4) RE-DECIDE -- among the CO-DERIVABLE valid choices, pick the one
whose acquired-meaning best matches the question stem by a GENERAL text meaning-match (SemanticHDEncoder
cosine), NOT a hand-wired fact->choice map.

CAN-FAIL LADDER (leak-controlled; the whole point):
  ARM0  BASELINE / POSITIVE CONTROL: the reasoner's legacy node-combiner tie-break on the 44 ties. MUST
        reproduce 29570 EXACT (correct_after acc = 15/44 = 0.3409).
  FLOOR INSTRUMENT-FLOOR: the text meaning-match tie-break with NO acquired facts (choice-text vs stem).
        Isolates "does the scorer swap alone help?" so ARM1's lift is attributable to FACTS (one variable).
  ARM1  ORACLE-ACQUISITION CEILING (the decisive diagnostic): widest answer-agnostic retrieval (choice
        content-words + lemmas + WordNet single-token synonyms) hands the meaning-match the concept's facts.
        If even the oracle fact cannot break ties over thin GloVe meaning-match (ARM1 ~ ARM0) -> HONEST KILL,
        routes to deeper grounding. If ARM1 shows headroom -> acquisition-precision is the (tractable) lever.
  ARM2  AUTONOMOUS LOOP (the real number): the substrate detects the gap, retrieves ITS OWN way (content-words
        + lemmas, NO synonym oracle), INGESTS each fact through the hd_fact_store trust-gate, sleep-consolidates
        (KEEP_EPISODIC), QUERIES the facts back by glass-box unbind, and re-decides. answerKey NEVER seen.
        ARM2 vs ARM1 = acquisition/retrieval-precision gap (WN-synonym coverage ARM1 has, ARM2 earns or not).
  ARM3  SCRAMBLE MUST-FAIL: ARM1's per-choice fact sets are shuffled ACROSS the tied choices -> if the RIGHT
        acquired meaning drove the gain it MUST collapse toward FLOOR (proves it was the fact, not "more text").

ANTI-LEAK (hard): acquisition keyed on CHOICE/STEM content-words, NEVER correct_index; tie-break is a general
  meaning-match (augmented-choice vs stem cosine), not a fact->choice map; the tie-break touches ONLY questions
  with >=2 valid choices (single-valid gold_only decisions are returned UNCHANGED in every arm -> gold_only
  @1.00 preserved by construction + asserted); held-out ARC-Challenge test; science rules NOT from test labels.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic (fixed seed,
  numpy default_rng, sorted iteration); repo .venv. VET-PENDING (skunkworks owns landed-VET); NO atom banking.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no bare/BaseException); atomic
  metrics (tmp+os.replace); start-marker; crash-diagnostic; heartbeat; self-test builds the REAL instrument +
  REAL HDFactStore round-trip over a planted discriminating tie (GloVe-free fake encoder) and asserts the
  tie-break CAN FIRE (right fact -> gold; scrambled/wrong fact -> not gold = can-fail). All numbers MEASURED@.
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
from hdlab.typed_rule_parser import parse_tablestore_typed
from hdlab.hd_fact_store import HDFactStore
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean
from experiments import exp_arc_reasoner_link_precision_tie_prune_v1 as tp

ANCHOR_NAME = "intrinsic_foundation_loop_tie_gaps_v1"
SEED = 20260725
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")
TIE_DETAIL_REF = os.path.join(_REPO, "data", "exp_arc_reasoner_link_precision_tie_prune_v1",
                              "tie_transition_detail.json")

BASE_MODE = "lemma_syn"          # defines the ties (VET baseline)
GAP_MODE = "lemma"               # the gap set = GENUINE ties still tied at the tighter lemma config
TIEBREAK_MODE = "legacy"         # ARM0 uses the reasoner's own legacy node-combiner tie-break
MIN_LEN = 3                      # content-word length floor for acquisition keys + choice lookup
K_FACTS = 8                      # max acquired facts per choice (bounds the augmented-text length)
STORE_DIM = 4096                 # HDFactStore dimensionality (ARM2 trust-gate ingest)

# ---- POSITIVE-CONTROL target (MEASURED@ tie_transition_detail.json lemma GENUINE ties) ----
ARM0_TARGET = 15.0 / 44.0        # 0.34090909... reproduces 29570 exactly
ARM0_TARGET_CORRECT = 15         # exact integer correct_after count over the 44 GENUINE lemma ties
N_GENUINE_EXPECTED = 44

# ---- pre-registered HARD-PASS / HARD-FAIL bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned) ----
HP_ARM1_MINUS_ARM0 = 0.15        # oracle ceiling must beat the deployed baseline by >= this
HP_ARM1_MINUS_FLOOR = 0.10       # ... and the lift must be attributable to FACTS (not the scorer swap)
HP_SCRAMBLE_MAX_OVER_FLOOR = 0.05  # ARM3 must collapse to within this of FLOOR (right-fact-drove-it)
HF_ARM1_MINUS_ARM0 = 0.05        # <= this: oracle fact CANNOT break ties over thin GloVe -> HONEST KILL
GOLD_ONLY_FLOOR = 1.0            # single-valid decisions unchanged (preserved by construction)

_T0 = [time.perf_counter()]


# ===========================================================================
# atomic metrics / start-marker / crash-diag / heartbeat
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
# ACQUISITION: concept -> definitional/propositional facts index (from the WorldTree tablestore)
# ===========================================================================
def _fact_text(rel: str, arg0: str, arg1: str) -> str:
    """Natural-language surface of a typed fact for the meaning-match (relation verb dropped: the
    discriminating content is the two arguments; relation is kept in provenance, not the match text)."""
    return f"{arg0} {arg1}".strip()


def build_acq_index(min_len: int = MIN_LEN) -> Tuple[Dict[str, List[int]], List[dict]]:
    """concept content-word (raw + lemma) -> list of fact ids; plus the fact table. ANSWER-AGNOSTIC:
    a fact is indexed by the content-words of its OWN arguments, nothing about any question/answer."""
    u = parse_tablestore_typed()
    facts: List[dict] = []
    for uid in sorted(u):
        d = u[uid]
        if not (d["confident"] and d["arg0"].strip() and d["arg1"].strip()):
            continue
        facts.append({"uid": uid, "relation": d["relation"],
                      "arg0": d["arg0"].strip(), "arg1": d["arg1"].strip(),
                      "text": _fact_text(d["relation"], d["arg0"].strip(), d["arg1"].strip())})
    index: Dict[str, set] = defaultdict(set)
    for fid, f in enumerate(facts):
        words = set(arc._content_words(f["arg0"], min_len=min_len)) | \
                set(arc._content_words(f["arg1"], min_len=min_len))
        for w in words:
            index[w].add(fid)
    return {k: sorted(v) for k, v in index.items()}, facts


def _wn_syns(wn, lem: str) -> set:
    """TIGHT same-synset single-token alpha-lower synonyms (rock->stone). Mirrors reasoner._wn_synonyms."""
    if wn is None:
        return set()
    out: set = set()
    try:
        for s in wn.synsets(lem):
            for l in s.lemmas():
                nm = l.name()
                if nm.isalpha() and nm.islower():
                    out.add(nm)
    except Exception:
        pass  # never let a WordNet hiccup crash acquisition
    out.discard(lem)
    return out


def retrieve_fact_ids(index: Dict[str, List[int]], text: str, wn, use_syn: bool,
                      min_len: int = MIN_LEN) -> List[int]:
    """Answer-agnostic retrieval of fact ids for a CHOICE/CONCEPT text.
    use_syn=True (ARM1 oracle): content-words + lemmas + WordNet single-token synonyms (widest net).
    use_syn=False (ARM2 autonomous): content-words + lemmas only (the substrate's own narrower reach)."""
    keys: set = set()
    for w in arc._content_words(text, min_len=min_len):
        keys.add(w)
        keys.add(clean._lemma(w, wn))
        if use_syn:
            for syn in _wn_syns(wn, clean._lemma(w, wn)):
                keys.add(syn)
    fids: set = set()
    for k in keys:
        fids |= set(index.get(k, ()))
    return sorted(fids)


def _select_facts(facts: List[dict], fids: List[int], k: int = K_FACTS) -> List[dict]:
    """Deterministically pick <=k facts: shortest surface first (most definitional), uid tiebreak."""
    ranked = sorted(fids, key=lambda i: (len(facts[i]["text"]), facts[i]["uid"]))
    return [facts[i] for i in ranked[:k]]


# ===========================================================================
# the MEANING-MATCH tie-break instrument (general; NOT a fact->choice map)
# ===========================================================================
def _l2(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def mm_score(encode: Callable[[str], np.ndarray], choice_text: str,
             fact_texts: List[str], stem_vec: np.ndarray) -> float:
    """Cosine of the AUGMENTED choice meaning (choice text + acquired fact texts) against the stem.
    General meaning-match: no per-question fact->choice wiring; the same scorer for every choice."""
    aug = choice_text + " " + " ".join(fact_texts) if fact_texts else choice_text
    cv = _l2(np.asarray(encode(aug), dtype=np.float32))
    return float(cv @ stem_vec)


def decide_by_meaning(valid: List[dict], facts_per_choice: Dict[int, List[str]],
                      encode: Callable[[str], np.ndarray], stem_vec: np.ndarray) -> int:
    """Pick the valid choice whose augmented meaning best matches the stem. GUARDRAIL: with exactly one
    valid choice (gold_only) return it UNCHANGED (identical to legacy) -> gold_only@1.00 preserved."""
    if len(valid) == 1:
        return valid[0]["choice_index"]
    scored = []
    for c in valid:
        ci = c["choice_index"]
        s = mm_score(encode, c["choice_text"], facts_per_choice.get(ci, []), stem_vec)
        scored.append((-s, ci))          # higher score first; lower index breaks exact ties (deterministic)
    scored.sort()
    return scored[0][1]


# ===========================================================================
# ARM2 autonomous loop: detect -> ingest through trust-gate -> sleep-consolidate -> query back
# ===========================================================================
def autonomous_facts(valid: List[dict], index: Dict[str, List[int]], facts: List[dict], wn,
                     seed: int) -> Tuple[Dict[int, List[str]], dict]:
    """For each valid (tied) choice: retrieve autonomously (content+lemma, NO synonym oracle), INGEST each
    fact through the hd_fact_store trust-gate, sleep-consolidate (definitional=KEEP_EPISODIC), then QUERY the
    live facts back by glass-box unbind. Returns per-choice recovered fact texts + a consolidation log."""
    per_choice: Dict[int, List[str]] = {}
    log = {"n_ingested": 0, "n_live_recovered": 0, "n_clean_store": 0, "n_conflict": 0,
           "consolidation": "KEEP_EPISODIC (definitional=assignment-lookup; MDL compression=1)"}
    for c in valid:
        ci = c["choice_index"]
        fids = retrieve_fact_ids(index, c["choice_text"], wn, use_syn=False)
        chosen = _select_facts(facts, fids, K_FACTS)
        # fresh per-choice store; WorldTree = curated TRUST_HIGH.
        store = HDFactStore(n_dim=STORE_DIM, seed=seed)
        for f in chosen:
            res = store.store(f["arg0"], f["relation"], f["arg1"], "worldtree", "TRUST_HIGH")
            log["n_ingested"] += 1
            if res.detected_conflict:
                log["n_conflict"] += 1
            else:
                log["n_clean_store"] += 1
        # sleep-consolidate + glass-box recover the LIVE facts (unbind, no plaintext read).
        recovered: List[str] = []
        for rec in store.live_facts():
            rf = store.recover_fact(rec.vec)
            if rf["subject"] and rf["object"]:
                recovered.append(f"{rf['subject']} {rf['object']}")
        log["n_live_recovered"] += len(recovered)
        per_choice[ci] = recovered
    return per_choice, log


def scramble_facts(valid: List[dict], oracle_facts: Dict[int, List[str]], seed: int) -> Dict[int, List[str]]:
    """MUST-FAIL control: shuffle the per-choice fact sets ACROSS the tied choices (derangement when
    possible) so no choice keeps its own facts. If the RIGHT fact drove the gain, this collapses it."""
    idxs = [c["choice_index"] for c in valid]
    rng = np.random.default_rng(seed)
    if len(idxs) < 2:
        return {ci: list(oracle_facts.get(ci, [])) for ci in idxs}
    perm = list(idxs)
    for _ in range(8):
        rng.shuffle(perm)
        if all(perm[i] != idxs[i] for i in range(len(idxs))):  # derangement: nobody keeps own facts
            break
    return {idxs[i]: list(oracle_facts.get(perm[i], [])) for i in range(len(idxs))}


# ===========================================================================
# reproduce the gap set (POSITIVE CONTROL, reuse the exact prior functions) + evaluate the ladder
# ===========================================================================
def _valid_choices(per_choice: List[dict]) -> List[dict]:
    return [c for c in per_choice if c["derivable"] and not c["rejected_by_ci"]]


def evaluate_loop(reasoner: DerivationReasoner, questions: List[dict], output_dir: str,
                  index: Dict[str, List[int]], facts: List[dict], wn,
                  encode: Callable[[str], np.ndarray], seed: int) -> dict:
    """Reproduce the 44 GENUINE-lemma ties from the tie-prune functions, then run the full arm ladder."""
    scratch = os.path.join(output_dir, "_reproduce_scratch")
    base_cfg = tp.eval_config(reasoner, questions, scratch, BASE_MODE)     # lemma_syn: defines the ties
    gap_cfg = tp.eval_config(reasoner, questions, scratch, GAP_MODE)       # lemma: the gap config
    _heartbeat(output_dir, "configs_evaluated",
               {"tie_n_lemma_syn": base_cfg["tie"]["n"], "tie_n_lemma": gap_cfg["tie"]["n"],
                "gold_only_n_lemma": gap_cfg["gold_only"]["n"]})

    tie_qids_syn = sorted(qid for qid, r in base_cfg["per_q"].items() if r["subset"] == "tie")
    trans = tp.classify_tie_transitions(base_cfg["per_q"], gap_cfg["per_q"], tie_qids_syn)
    genuine_qids = sorted(d["qid"] for d in trans["detail"] if d["class"] == "GENUINE")
    gold_only_qids = sorted(qid for qid, r in gap_cfg["per_q"].items() if r["subset"] == "gold_only")

    # ARM0 positive control: the reasoner's own legacy tie-break correctness on the 44 (== correct_after).
    arm0_correct = sum(gap_cfg["per_q"][qid]["correct"] for qid in genuine_qids)
    n_gap = len(genuine_qids)
    arm0_acc = arm0_correct / n_gap if n_gap else 0.0

    qmap = {q["qid"]: q for q in questions}
    reasoner.link_mode = GAP_MODE
    reasoner.tiebreak_mode = TIEBREAK_MODE

    # ---- PASS 1: per-tie context (valid choices, stem vec, oracle + autonomous facts) ----
    contexts: List[dict] = []
    consolidation_totals = {"n_ingested": 0, "n_live_recovered": 0, "n_conflict": 0}
    for qi, qid in enumerate(genuine_qids):
        q = qmap[qid]
        ci = q["correct_index"]
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        valid = [{"choice_index": c["choice_index"], "choice_text": c["choice_text"]}
                 for c in _valid_choices(res["per_choice"])]
        stem_vec = _l2(np.asarray(encode(q["stem"]), dtype=np.float32))
        # ARM1 oracle: widest answer-agnostic retrieval (content+lemma+WN synonyms).
        oracle_facts = {}
        for c in valid:
            fids = retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
            oracle_facts[c["choice_index"]] = [f["text"] for f in _select_facts(facts, fids, K_FACTS)]
        # ARM2 autonomous loop: detect -> ingest(trust-gate) -> consolidate -> query back.
        auto_facts, clog = autonomous_facts(valid, index, facts, wn, seed + qi)
        for k in consolidation_totals:
            consolidation_totals[k] += clog[k]
        contexts.append({"qid": qid, "ci": ci, "valid": valid, "stem_vec": stem_vec,
                         "oracle_facts": oracle_facts, "auto_facts": auto_facts})
        if (qi + 1) % 15 == 0:
            _heartbeat(output_dir, "tie_progress", {"done": qi + 1, "total": n_gap})

    # global fact pool for ARM3b: every valid choice's oracle fact-set, tagged by source qid.
    global_pool = [(ctx["qid"], fts) for ctx in contexts for fts in ctx["oracle_facts"].values() if fts]

    # ---- PASS 2: decisions for every arm (incl. within-question + GLOBAL scramble) ----
    per_tie: List[dict] = []
    tallies = {"floor": 0, "arm1": 0, "arm2": 0, "arm3_within": 0, "arm3_global": 0}
    n_valid_multi = 0
    grng = np.random.default_rng(seed * 101 + 5)
    for ctx in contexts:
        qid, ci, valid, stem_vec = ctx["qid"], ctx["ci"], ctx["valid"], ctx["stem_vec"]
        oracle_facts, auto_facts = ctx["oracle_facts"], ctx["auto_facts"]
        no_facts = {c["choice_index"]: [] for c in valid}
        floor_pick = decide_by_meaning(valid, no_facts, encode, stem_vec)
        arm1_pick = decide_by_meaning(valid, oracle_facts, encode, stem_vec)
        arm2_pick = decide_by_meaning(valid, auto_facts, encode, stem_vec)
        # ARM3 within-question scramble (design-note spec: shuffle facts across the tied choices).
        arm3_within_pick = decide_by_meaning(valid, scramble_facts(valid, oracle_facts, seed + len(per_tie)),
                                             encode, stem_vec)
        # ARM3b GLOBAL scramble (robust must-fail: each choice gets a fact-set from a DIFFERENT question ->
        # concept->fact binding fully broken; challenges gold specifically even for multi-way ties).
        other = [fts for (sq, fts) in global_pool if sq != qid]
        gscr = {}
        for c in valid:
            gscr[c["choice_index"]] = list(other[int(grng.integers(len(other)))]) if other else []
        arm3_global_pick = decide_by_meaning(valid, gscr, encode, stem_vec)

        if len(valid) >= 2:
            n_valid_multi += 1
        tallies["floor"] += int(floor_pick == ci)
        tallies["arm1"] += int(arm1_pick == ci)
        tallies["arm2"] += int(arm2_pick == ci)
        tallies["arm3_within"] += int(arm3_within_pick == ci)
        tallies["arm3_global"] += int(arm3_global_pick == ci)
        per_tie.append({
            "qid": qid, "correct_index": ci, "n_valid": len(valid),
            "valid_indices": [c["choice_index"] for c in valid],
            "arm0_pick": gap_cfg["per_q"][qid]["chosen"], "arm0_correct": gap_cfg["per_q"][qid]["correct"],
            "floor_pick": floor_pick, "arm1_pick": arm1_pick, "arm2_pick": arm2_pick,
            "arm3_within_pick": arm3_within_pick, "arm3_global_pick": arm3_global_pick,
            "arm1_correct": int(arm1_pick == ci), "arm2_correct": int(arm2_pick == ci),
            "n_oracle_facts": sum(len(v) for v in oracle_facts.values()),
            "n_auto_facts": sum(len(v) for v in auto_facts.values()),
        })

    # gold_only preservation: single-valid decisions unchanged under the meaning-match tie-break.
    go_preserved = 1.0
    go_checked = 0
    for qid in gold_only_qids:
        q = qmap[qid]
        ci = q["correct_index"]
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        valid = _valid_choices(res["per_choice"])
        stem_vec = _l2(np.asarray(encode(q["stem"]), dtype=np.float32))
        oracle = {}
        for c in valid:
            fids = retrieve_fact_ids(index, c["choice_text"], wn, use_syn=True)
            oracle[c["choice_index"]] = [f["text"] for f in _select_facts(facts, fids, K_FACTS)]
        pick = decide_by_meaning(valid, oracle, encode, stem_vec)
        go_checked += 1
        if len(valid) == 1 and pick != valid[0]["choice_index"]:
            go_preserved = 0.0
    reasoner.link_mode = BASE_MODE

    acc = {k: (tallies[k] / n_gap if n_gap else 0.0) for k in tallies}

    # 2-way (clean gold<->distractor swap) vs multi-way decomposition -- the within-question scramble is
    # a clean control ONLY on 2-way; the global scramble is the robust control across all arity.
    def _sub_acc(rows: List[dict], key: str) -> float:
        return sum(r[key] for r in rows) / len(rows) if rows else 0.0
    two = [t for t in per_tie if t["n_valid"] == 2]
    multi = [t for t in per_tie if t["n_valid"] > 2]
    def _pick_acc(rows, pk):
        return round(sum(int(r[pk] == r["correct_index"]) for r in rows) / len(rows), 4) if rows else 0.0
    decomp = {}
    for name, rows in (("two_way", two), ("multi_way", multi)):
        decomp[name] = {"n": len(rows),
                        "arm0": round(_sub_acc(rows, "arm0_correct"), 4),
                        "floor": _pick_acc(rows, "floor_pick"), "arm1": _pick_acc(rows, "arm1_pick"),
                        "arm2": _pick_acc(rows, "arm2_pick"),
                        "arm3_within": _pick_acc(rows, "arm3_within_pick"),
                        "arm3_global": _pick_acc(rows, "arm3_global_pick")}

    return {
        "n_gap": n_gap, "genuine_qids": genuine_qids,
        "arm0_acc": round(arm0_acc, 4), "arm0_correct": arm0_correct,
        "floor_acc": round(acc["floor"], 4),
        "arm1_acc": round(acc["arm1"], 4), "arm2_acc": round(acc["arm2"], 4),
        "arm3_within_acc": round(acc["arm3_within"], 4), "arm3_global_acc": round(acc["arm3_global"], 4),
        "n_valid_multi": n_valid_multi, "decomp_by_arity": decomp,
        "gold_only_preserved": round(go_preserved, 4), "gold_only_checked": go_checked,
        "consolidation_totals": consolidation_totals,
        "tie_n_lemma_syn": base_cfg["tie"]["n"], "tie_n_lemma": gap_cfg["tie"]["n"],
        "gold_only_n_lemma": gap_cfg["gold_only"]["n"],
        "per_tie": per_tie,
    }


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", N_GENUINE_EXPECTED)
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})

    rows = tp._load_rules(RULES_PATH)
    _heartbeat(output_dir, "rules_loaded", {"n_rules": len(rows)})

    index, facts = build_acq_index()
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

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_eval": len(questions)})

    rep = evaluate_loop(reasoner, questions, output_dir, index, facts, wn, encode, seed)
    _heartbeat(output_dir, "ladder_done",
               {"arm0": rep["arm0_acc"], "floor": rep["floor_acc"], "arm1": rep["arm1_acc"],
                "arm2": rep["arm2_acc"], "arm3_within": rep["arm3_within_acc"],
                "arm3_global": rep["arm3_global_acc"]})

    # ---- POSITIVE CONTROL (Gate D): the reproduced gap set + ARM0 must match 29570 EXACT ----
    smoke_run = (n_sample != 0)
    # exact integer-count comparison (rounded acc would trip a false mismatch at the 4th decimal).
    pc_ok = (rep["n_gap"] == N_GENUINE_EXPECTED and rep["arm0_correct"] == ARM0_TARGET_CORRECT)
    positive_control = {
        "n_gap_reproduced": rep["n_gap"], "n_gap_expected": N_GENUINE_EXPECTED,
        "arm0_acc": rep["arm0_acc"], "arm0_target": round(ARM0_TARGET, 4),
        "reproduces_29570": bool(pc_ok),
        "note": ("full-set only; smoke uses a question subset so the gap set is NOT the canonical 44"
                 if smoke_run else "full ARC-Challenge test set"),
    }

    # ---- deltas ----
    d_arm1_arm0 = round(rep["arm1_acc"] - rep["arm0_acc"], 4)
    d_arm1_floor = round(rep["arm1_acc"] - rep["floor_acc"], 4)
    d_arm2_arm0 = round(rep["arm2_acc"] - rep["arm0_acc"], 4)
    d_arm2_arm1 = round(rep["arm2_acc"] - rep["arm1_acc"], 4)
    # GLOBAL scramble is the robust must-fail (concept->fact binding fully broken across arity).
    d_arm3g_floor = round(rep["arm3_global_acc"] - rep["floor_acc"], 4)
    d_arm3w_floor = round(rep["arm3_within_acc"] - rep["floor_acc"], 4)
    ceiling_captured = round((d_arm2_arm0 / d_arm1_arm0), 4) if d_arm1_arm0 > 1e-9 else None

    bands = {
        "arm1_beats_arm0_ge_0.15": d_arm1_arm0 >= HP_ARM1_MINUS_ARM0,
        "arm1_beats_floor_ge_0.10": d_arm1_floor >= HP_ARM1_MINUS_FLOOR,
        "global_scramble_collapses_within_0.05": d_arm3g_floor <= HP_SCRAMBLE_MAX_OVER_FLOOR,
        "gold_only_preserved": rep["gold_only_preserved"] >= GOLD_ONLY_FLOOR,
    }
    hard_kill = (d_arm1_arm0 <= HF_ARM1_MINUS_ARM0)

    # ---- verdict (pre-registered, can-fail) ----
    if not pc_ok and not smoke_run:
        tier, verdict = "POSITIVE_CONTROL_FAIL", "REPRODUCE_29570_MISMATCH"
    elif all(bands.values()):
        tier, verdict = "HARD_PASS", "INTRINSIC_LOOP_RESOLVES_TIES"
    elif hard_kill:
        tier, verdict = "HONEST_NEG", "ORACLE_FACT_CANNOT_BREAK_TIES_OVER_THIN_GLOVE"
    else:
        tier, verdict = "MIDDLE_BAND", "PARTIAL_TIE_RESOLUTION"

    summary = (f"INTRINSIC LOOP on {rep['n_gap']} GENUINE ties | ARM0(legacy)={rep['arm0_acc']:.3f} "
               f"FLOOR(mm,no-fact)={rep['floor_acc']:.3f} ARM1(oracle)={rep['arm1_acc']:.3f} "
               f"ARM2(autonomous)={rep['arm2_acc']:.3f} ARM3within={rep['arm3_within_acc']:.3f} "
               f"ARM3global={rep['arm3_global_acc']:.3f} | d(ARM1-ARM0)={d_arm1_arm0:+.3f} "
               f"d(ARM1-FLOOR)={d_arm1_floor:+.3f} d(ARM2-ARM0)={d_arm2_arm0:+.3f} "
               f"d(ARM3global-FLOOR)={d_arm3g_floor:+.3f} | 2way(n={rep['decomp_by_arity']['two_way']['n']}): "
               f"arm1={rep['decomp_by_arity']['two_way']['arm1']:.3f} "
               f"arm3within={rep['decomp_by_arity']['two_way']['arm3_within']:.3f} | "
               f"gold_only_preserved={rep['gold_only_preserved']:.2f} | "
               f"repro_29570={positive_control['reproduces_29570']} | tier={tier}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "Intrinsic foundation loop instantiated on the composed reasoner's OWN 44 GENUINE lemma tie-gaps "
            "(exactly reproduced from exp_arc_reasoner_link_precision_tie_prune_v1 via its own eval_config/"
            "classify functions -- positive control ARM0=15/44=0.3409 reproduces 29570). Ladder: ARM0 legacy "
            "node-combiner tie-break / FLOOR text meaning-match no facts / ARM1 ORACLE-acquisition ceiling "
            "(widest answer-agnostic retrieval: choice content+lemma+WordNet synonyms from the WorldTree "
            "tablestore) / ARM2 AUTONOMOUS loop (substrate detects the tie, retrieves its own way, INGESTS "
            "through the hd_fact_store trust-gate, sleep-consolidates KEEP_EPISODIC, queries facts back by "
            "glass-box unbind, re-decides; answerKey never seen) / ARM3 SCRAMBLE must-fail (oracle facts "
            "shuffled across tied choices [within-question], plus a ROBUST GLOBAL scramble that fully breaks "
            "concept->fact binding across all questions -- the within-question control is clean only on 2-way "
            "ties, the global control challenges gold even for multi-way ties). ANTI-LEAK: acquisition keyed on "
            "choice/stem content-words never the answer; tie-break is a general meaning-match (augmented-choice "
            "vs stem cosine), not a fact->choice map; single-valid gold_only decisions returned unchanged "
            "(preserved @1.00 by construction). "
            "HELD-OUT ARC-Challenge; science rules not from test labels. DECISIVE DIAGNOSTIC = ARM1: if the "
            "oracle fact cannot break ties over thin-GloVe meaning-match (d(ARM1-ARM0)<=0.05) the loop cannot "
            "work over this rep -> HONEST KILL routing to deeper grounding; if ARM1 shows headroom the bottleneck "
            "is acquisition-precision (tractable). NOTE: meaning-match is still thin GloVe (SemanticHDEncoder) -- "
            "the honestly-expected outcome is MIDDLE/HONEST-NEG. VET-PENDING; no atom banking."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "seed": seed,
                   "rules_path": RULES_PATH, "n_rules": len(rows), "base_mode": BASE_MODE,
                   "gap_mode": GAP_MODE, "tiebreak_mode": TIEBREAK_MODE, "min_len": MIN_LEN,
                   "k_facts": K_FACTS, "store_dim": STORE_DIM,
                   "meaning_match": "SemanticHDEncoder text cosine (thin GloVe; INTERIM, HONEST caveat)",
                   "one_variable_floor_to_arm1": "acquired-fact augmentation (scorer identical)",
                   "one_variable_arm1_to_arm2": "retrieval reach (oracle WN-synonyms vs autonomous+trust-gate)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "positive_control": positive_control,
        "acquisition": {"source": "WorldTree tablestore (parse_tablestore_typed, ALL relations)",
                        "n_facts": len(facts), "n_concept_keys": len(index),
                        "trust_gate": "hd_fact_store.HDFactStore (WorldTree=TRUST_HIGH)",
                        "consolidation": "sleep KEEP_EPISODIC (definitional=assignment-lookup; MDL comp=1)",
                        "totals": rep["consolidation_totals"]},
        "gap_set": {"n_gap": rep["n_gap"], "tie_n_lemma_syn": rep["tie_n_lemma_syn"],
                    "tie_n_lemma": rep["tie_n_lemma"], "gold_only_n_lemma": rep["gold_only_n_lemma"],
                    "n_valid_multi": rep["n_valid_multi"]},
        "arms": {"arm0_legacy_combiner": rep["arm0_acc"], "floor_mm_no_facts": rep["floor_acc"],
                 "arm1_oracle_ceiling": rep["arm1_acc"], "arm2_autonomous_loop": rep["arm2_acc"],
                 "arm3_scramble_within": rep["arm3_within_acc"], "arm3_scramble_global": rep["arm3_global_acc"]},
        "decomp_by_arity": rep["decomp_by_arity"],
        "deltas": {"arm1_minus_arm0": d_arm1_arm0, "arm1_minus_floor": d_arm1_floor,
                   "arm2_minus_arm0": d_arm2_arm0, "arm2_minus_arm1": d_arm2_arm1,
                   "arm3_global_minus_floor": d_arm3g_floor, "arm3_within_minus_floor": d_arm3w_floor,
                   "ceiling_fraction_captured_by_arm2": ceiling_captured},
        "gold_only_preserved": rep["gold_only_preserved"], "gold_only_checked": rep["gold_only_checked"],
        "preregistered_bands": bands, "n_bands_pass": sum(1 for v in bands.values() if v),
        "hard_kill_triggered": bool(hard_kill),
        "bands_definition": {
            "arm1_beats_arm0": f">= {HP_ARM1_MINUS_ARM0} (oracle ceiling beats deployed baseline)",
            "arm1_beats_floor": f">= {HP_ARM1_MINUS_FLOOR} (lift attributable to FACTS not scorer swap)",
            "global_scramble_collapses": (f"ARM3global - FLOOR <= {HP_SCRAMBLE_MAX_OVER_FLOOR} "
                                          "(concept-specific fact drove it; robust across arity)"),
            "gold_only_preserved": f">= {GOLD_ONLY_FLOOR}",
            "hard_fail_kill": f"d(ARM1-ARM0) <= {HF_ARM1_MINUS_ARM0} -> honest kill, route to deeper grounding",
        },
        "per_tie": rep["per_tie"],
        "REQUIRED_FIELDS": ["verdict", "tier", "positive_control", "arms", "deltas",
                            "preregistered_bands", "gold_only_preserved", "acquisition"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== INTRINSIC FOUNDATION LOOP (tie-gaps) RESULT =====", flush=True)
    print(summary, flush=True)
    print(f"bands: {bands} -> {metrics['n_bands_pass']}/4 | hard_kill={hard_kill} | tier={tier}", flush=True)
    print(f"positive_control: {positive_control}", flush=True)
    return metrics


# ===========================================================================
# self-test (real code path: REAL instrument + REAL HDFactStore round-trip, GloVe-free fake encoder)
# ===========================================================================
def _bow_encoder(vocab: Dict[str, int]) -> Callable[[str], np.ndarray]:
    """Deterministic GloVe-free stand-in: L2-normalized bag-of-content-words one-hot. cosine ~ token overlap.
    Exercises the REAL mm_score / decide_by_meaning path without loading GloVe."""
    def enc(text: str) -> np.ndarray:
        v = np.zeros(len(vocab), dtype=np.float32)
        for w in arc._content_words(text, min_len=MIN_LEN):
            if w in vocab:
                v[vocab[w]] += 1.0
        return v
    return enc


def _self_test() -> None:
    print("[self-test] instrument + HDFactStore round-trip (GloVe-free) ...", flush=True)
    exercised = set()

    # ---- (1) meaning-match instrument FIRES: right fact -> gold; scrambled fact -> not gold (CAN-FAIL) ----
    # planted 2-choice tie: stem describes "heat removed cooling"; both choice words are bare + symmetric,
    # the DISCRIMINATING signal lives only in the acquired fact.
    stem = "what process happens when heat is removed and vapor cooling occurs"
    vocab_words = set(arc._content_words(stem, min_len=MIN_LEN))
    gold_fact = "condensation vapor becomes liquid cooling heat removed"       # aligns with stem
    dist_fact = "evaporation liquid becomes vapor heating warming energy added"  # does not
    for t in (gold_fact, dist_fact, "condensation process", "evaporation process"):
        vocab_words |= set(arc._content_words(t, min_len=MIN_LEN))
    vocab = {w: i for i, w in enumerate(sorted(vocab_words))}
    encode = _bow_encoder(vocab)
    stem_vec = _l2(np.asarray(encode(stem), dtype=np.float32))
    valid = [{"choice_index": 0, "choice_text": "condensation process"},   # gold
             {"choice_index": 1, "choice_text": "evaporation process"}]     # distractor

    no_facts = {0: [], 1: []}
    floor_pick = decide_by_meaning(valid, no_facts, encode, stem_vec)
    with_facts = {0: [gold_fact], 1: [dist_fact]}
    right_pick = decide_by_meaning(valid, with_facts, encode, stem_vec)
    assert right_pick == 0, f"right fact must pick gold(0), got {right_pick}"
    exercised.add("decide_by_meaning")
    # scramble (swap the facts) -> the discriminator MUST NOT still pick gold (can-fail proof).
    swapped = {0: [dist_fact], 1: [gold_fact]}
    scr_pick = decide_by_meaning(valid, swapped, encode, stem_vec)
    assert scr_pick != 0, f"scrambled fact must NOT pick gold; instrument would be non-discriminating (got {scr_pick})"
    print(f"[self-test] instrument fires: floor={floor_pick} right_fact->{right_pick} scrambled->{scr_pick}",
          flush=True)

    # scramble_facts derangement helper: nobody keeps their own facts.
    scr = scramble_facts(valid, with_facts, seed=1)
    assert scr[0] != with_facts[0] and scr[1] != with_facts[1], f"derangement failed: {scr}"
    exercised.add("scramble_facts")

    # ---- (2) gold_only guardrail: a SINGLE valid choice is returned UNCHANGED in every arm ----
    solo = [{"choice_index": 2, "choice_text": "the only derivable answer"}]
    assert decide_by_meaning(solo, {2: ["irrelevant fact tokens"]}, encode, stem_vec) == 2, \
        "single valid choice must be returned unchanged (gold_only preserved by construction)"
    exercised.add("gold_only_preserved")

    # ---- (3) REAL HDFactStore ingest -> glass-box recover round-trip (the ARM2 trust-gate path) ----
    store = HDFactStore(n_dim=STORE_DIM, seed=7)
    store.store("condensation", "CHANGE", "gas to liquid decreasing heat", "worldtree", "TRUST_HIGH")
    live = store.live_facts()
    assert len(live) == 1, f"expected 1 live fact, got {len(live)}"
    rf = store.recover_fact(live[0].vec)
    assert rf["subject"] == "condensation" and rf["object"] == "gas to liquid decreasing heat", rf
    assert rf["trust"] == "TRUST_HIGH", rf
    exercised.add("hd_fact_store_roundtrip")
    print(f"[self-test] HDFactStore glass-box recover: {rf['subject']} -> {rf['object']}", flush=True)

    # ---- (4) autonomous_facts loop runs end-to-end over a tiny real index slice ----
    mini_facts = [
        {"uid": "u1", "relation": "CHANGE", "arg0": "condensation",
         "arg1": "gas to liquid cooling", "text": "condensation gas to liquid cooling"},
        {"uid": "u2", "relation": "CAUSE", "arg0": "evaporation",
         "arg1": "water to decrease", "text": "evaporation water to decrease"},
    ]
    mini_index: Dict[str, List[int]] = defaultdict(list)
    for fid, f in enumerate(mini_facts):
        for w in set(arc._content_words(f["arg0"], MIN_LEN)) | set(arc._content_words(f["arg1"], MIN_LEN)):
            mini_index[w].append(fid)
    auto, log = autonomous_facts(valid, dict(mini_index), mini_facts, wn=None, seed=3)
    assert log["n_ingested"] >= 1 and log["n_live_recovered"] >= 1, f"autonomous loop must ingest+recover: {log}"
    assert any("condensation" in " ".join(v) for v in auto.values()), f"autonomous must recover a fact: {auto}"
    exercised.add("autonomous_facts")
    print(f"[self-test] autonomous loop: ingested={log['n_ingested']} recovered={log['n_live_recovered']}",
          flush=True)

    # ---- (5) real acquisition index builds + retrieves a known concept fact (real_code_path) ----
    idx, facts = build_acq_index()
    assert len(facts) > 1000, f"real acquisition index must load many facts, got {len(facts)}"
    fids = retrieve_fact_ids(idx, "condensation", wn=None, use_syn=False)
    assert len(fids) >= 1, "must retrieve at least one fact about 'condensation' from the tablestore"
    exercised.add("build_acq_index")
    exercised.add("retrieve_fact_ids")
    print(f"[self-test] acquisition index: n_facts={len(facts)} condensation_hits={len(fids)}", flush=True)

    need = {"decide_by_meaning", "scramble_facts", "gold_only_preserved", "hd_fact_store_roundtrip",
            "autonomous_facts", "build_acq_index", "retrieve_fact_ids"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised entrypoints {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=250, help="smoke sample size (full ignores this)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = args.n if args.mode == "smoke" else 0   # full = all test questions (canonical 44 gap set)
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
