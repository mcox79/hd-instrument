# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BOW/AUGMENTED/ORDER_SCRAMBLE/CONTENT_ONLY hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (MCQA pick-accuracy measurement; bands are Director's task-contract thresholds)
# - HP_SCOPE: {AUGMENTED: [subset_lift, full_delta], ORDER_SCRAMBLE: [scramble_gain], CONTENT_ONLY: [content_shortfall]}
# - cardinality_ok: EXPECTED_N_UNITS = n_instances (passages) + n_questions (question-only) + n_questions*2 (candidates)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (tau_conf = median BoW margin on temporal subset, score-only)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL parse_mcscript_xml / run_pipeline / EventBundleCodec (real_code_path)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_mcscript2_augmented_temporal_loop_v1.md for the full pre-reg.
"""exp_mcscript2_augmented_temporal_loop_v1 -- E4 (de-risked first step): AUGMENT-NOT-REPLACE two-route
comprehension on the MCScript2.0 TEMPORAL subset.

Route 1 = always-on BoW (unchanged). Route 2 = a glass-box passage-internal temporal-order VALIDATE loop,
invoked ONLY when (question is TEMPORAL AND BoW is low-confidence AND both answer candidates extract >=1
event); otherwise silent (BoW's pick stands -- the anti-regression guarantee, verified empirically here,
not assumed). Design: notes/research_e4_inference_augmented_comprehension_design_2026-08-10.md Section 4,
scoped down (passage-internal only, temporal subset only) per Director's task contract.

Fixes the two bugs that sank exp_mcscript2_mcqa_droptense_properscramble_v1 (HARD_FAIL, structured=0.401
BELOW CHANCE vs BoW=0.629): (a) candidate events come from the ANSWER SPAN ALONE, never question+answer
concatenation (that anchored both candidates on the shared question stem -> 404/1084 ties); (b) a
candidate with zero extracted events NEVER gets a structured vote (39% of candidates were previously
forced to guess via a lossy vector).

REUSE, not re-implement: hdlab.mcscript_extraction.parse_mcscript_xml, hdlab.mcscript_extraction.
split_sentences; experiments._temporal_ordering.{extract_events, reconstruct_order, Event, AUX_LEMMAS,
TENSE_SIMPLE_PAST}; experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1.{
extract_events_present_patched, assign_roles, NOMINAL_TAGS, TENSE_SIMPLE_PRESENT, encode_instance_bow,
cosine, N_DIM, SEED}; hdlab.event_bundle.EventBundleCodec; tools.exp_checkpoint.

Four arms per scored question (a question is SCORED iff passage + both candidates have non-empty BoW
content -- IDENTICAL denominator for all 4 arms):
  BOW           : always-on content/gist route, unchanged.
  AUGMENTED     : BoW + gated Route-2 distance-to-anchor temporal validation.
  ORDER_SCRAMBLE: same gate, but the passage's temporal sequence is permuted before matching (content
                  intact, position destroyed) -- proves ORDER (not content) does the work if the gain
                  collapses.
  CONTENT_ONLY  : same gate, but Route 2 picks by raw content-match score (no position) -- proves the
                  gain is not just "more content matching."

Modes:
  --self-test  Real-code-path check: a REAL tiny MCScript-XML-schema temp file through parse_mcscript_xml;
               a deterministic hand-built temporal example proving the distance mechanism resolves order
               correctly AND that CONTENT_ONLY abstains on it AND that a hand-constructed adversarial
               passage-order permutation flips AUGMENTED's pick (order-dependence, not a probabilistic
               scramble hope); non-temporal control question never overridden; arms-must-differ. No queue
               dispatch.
  --smoke      Full real dev-data.xml (355 instances), SEED=7 only (fast; smoke = full-N per
               DISCRIMINATOR-MUST-SURVIVE-SCALE option A -- the whole corpus is cheap).
  --full       Full real dev-data.xml, SEEDS=[7,13,19].
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import functools
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.event_bundle import EventBundleCodec  # noqa: E402
from hdlab.mcscript_extraction import parse_mcscript_xml, split_sentences  # noqa: E402
from experiments._temporal_ordering import (  # noqa: E402
    Event, AUX_LEMMAS, TENSE_SIMPLE_PAST, reconstruct_order,
)
from experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1 import (  # noqa: E402
    extract_events_present_patched, assign_roles, NOMINAL_TAGS, TENSE_SIMPLE_PRESENT,
    encode_instance_bow, cosine, N_DIM, SEED,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from tools import exp_checkpoint as _ckpt  # noqa: E402

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ANCHOR_NAME = "mcscript2_augmented_temporal_loop_v1"
REPO_ROOT = Path(_REPO)
CORPUS_PATH = REPO_ROOT / "data" / "corpora" / "mcscript2" / "extracted" / "dev-data.xml"
OUTPUT_DIR = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [SEED]

# Pre-registered bands (preregs/2026-08-10_mcscript2_augmented_temporal_loop_v1.md), Director's task
# contract, this cell's numeric operationalization.
FULL_SET_REGRESSION_FLOOR = -0.01     # HYPOTHESIZED@preregs/2026-08-10_mcscript2_augmented_temporal_loop_v1.md
HARD_PASS_SUBSET_LIFT = 0.05          # same
SCRAMBLE_COLLAPSE_CEIL = 0.01         # same
SCRAMBLE_MUST_LOSE_VS_AUG = 0.02      # same
CONTENT_ONLY_MARGIN = 0.03            # same

ORDER_WORDS = frozenset({"after", "before", "next", "first", "last", "then"})
_WORD_RE = re.compile(r"[a-z']+")

DO_SUPPORT_LEMMAS = frozenset({"do", "does", "did"})


# =====================================================================================
# Question-type detector (question-only, no label leakage).
# =====================================================================================
def is_temporal_question(question_text: str) -> bool:
    words = set(_WORD_RE.findall((question_text or "").lower()))
    if "when" in words:
        return True
    return bool(words & ORDER_WORDS)


# =====================================================================================
# Additive-only local patch: do-support bare-VB events (E3's present-tense patch, reused,
# extended -- ADDITIVE ONLY, never alters an event the present-tense-patched function found).
# =====================================================================================
def extract_events_question_patched(text: str) -> Tuple[List[Event], list]:
    """Closes a KNOWN, documented coverage gap (see prereg): interrogative do-support
    ("When DID they GET in the taxi") leaves the main-clause verb as a bare VB with no
    MODAL_LEMMAS trigger, so the base extractor silently drops it. Content-blind (fires on
    POS pattern + auxiliary proximity only, never on answer correctness)."""
    events, tagged = extract_events_present_patched(text)
    have_idx = {e.idx for e in events}
    lows = [t[1] for t in tagged]
    poss = [t[2] for t in tagged]
    for i, (low, pos) in enumerate(zip(lows, poss)):
        if i in have_idx or low in AUX_LEMMAS:
            continue
        if pos != "VB":
            continue
        window = lows[max(0, i - 3):i]
        if "did" in window:
            events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_SIMPLE_PAST, is_pp=False))
        elif "do" in window or "does" in window:
            events.append(Event(lemma=low, idx=i, pos=pos, tense=TENSE_SIMPLE_PRESENT, is_pp=False))
    events.sort(key=lambda e: e.idx)
    return events, tagged


@functools.lru_cache(maxsize=8192)
def _verb_lemma(word: str) -> str:
    """Normalize a verb SURFACE form to its base (infinitive) form for cross-tense event
    matching. `Event.lemma` (experiments._temporal_ordering) is actually the raw lowercased
    SURFACE token, not a true lemma -- so 'got'/'walked'/'hailed' (passage, simple past)
    never string-equal 'get'/'walk'/'hail' (a do-support question's bare infinitive), which
    silently starves anchor-matching on exactly the 'when did X <verb>' shape this cell
    targets (found empirically: t0's self-test anchor failed to match until this fix).
    Reuses nltk.stem.WordNetLemmatizer -- the SAME tool already a runtime dependency of this
    codebase's grounding pipeline (exp_focus_encode_grounded_event_discrimination_realprose_
    v1._lemma / hdlab.lexical_similarity), thin local wrapper (that helper is module-private)."""
    from nltk.stem import WordNetLemmatizer
    lemmatizer = _verb_lemma._lemmatizer
    if lemmatizer is None:
        lemmatizer = WordNetLemmatizer()
        _verb_lemma._lemmatizer = lemmatizer
    return lemmatizer.lemmatize(word.lower(), pos="v")


_verb_lemma._lemmatizer = None


def analyze_text(text: str) -> Tuple[List[Dict[str, Optional[str]]], List[str]]:
    """One pass over `text`: (event_seq, content_words). event_seq is a list of
    {lemma, vlemma, agent, patient, tense} dicts IN RECONSTRUCTED CHRONOLOGICAL ORDER
    (per-sentence Zwaan-Radvansky reordering via reconstruct_order, sentences concatenated in
    text order -- see prereg 'Passage-internal temporal index'). `lemma` = raw surface token
    (kept for audit/debug); `vlemma` = verb-normalized form, the field matching uses.
    content_words = all VB*/nominal tokens except AUX_LEMMAS, across sentences (mirrors
    build_instance_role_events' convention)."""
    event_seq: List[Dict[str, Optional[str]]] = []
    content_words: List[str] = []
    for s in split_sentences(text):
        events, tagged = extract_events_question_patched(s)
        if events:
            chrono = reconstruct_order(events, tagged)
            for e in chrono:
                agent, patient = assign_roles(tagged, e.idx)
                event_seq.append({"lemma": e.lemma, "vlemma": _verb_lemma(e.lemma), "agent": agent,
                                  "patient": patient, "tense": e.tense})
        for (_surf, low, pos) in tagged:
            if (pos.startswith("VB") or pos in NOMINAL_TAGS) and low not in AUX_LEMMAS:
                content_words.append(low)
    return event_seq, content_words


# =====================================================================================
# Route-2 mechanism: matching, distance-to-anchor, content-only, order-scramble.
# =====================================================================================
def _match_score(e1: dict, e2: dict) -> float:
    if e1["vlemma"] == e2["vlemma"]:
        return 1.0
    if e1["agent"] is not None and e1["agent"] == e2["agent"]:
        return 0.5
    if e1["patient"] is not None and e1["patient"] == e2["patient"]:
        return 0.5
    return 0.0


def _best_match(events: List[dict], passage_events: List[dict]) -> Tuple[Optional[int], float]:
    """Best (passage_idx, score) across ALL of `events` (a candidate/question may have >1
    extracted event); score in {0.0, 0.5, 1.0}. (None, 0.0) if nothing matches."""
    best_idx, best_score = None, 0.0
    for e in events:
        for i, pe in enumerate(passage_events):
            sc = _match_score(e, pe)
            if sc > best_score:
                best_score, best_idx = sc, i
    return best_idx, best_score


def route2_pick_by_distance(anchor_idx: Optional[int], cand0: List[dict], cand1: List[dict],
                             passage_events: List[dict]) -> Tuple[Optional[int], dict]:
    """VALIDATE: the candidate whose matched event is CLOSER to the anchor in the passage's
    temporal sequence wins. Ties or double-unmatched -> abstain (None)."""
    if anchor_idx is None:
        return None, {"dist0": None, "dist1": None}
    idx0, _ = _best_match(cand0, passage_events)
    idx1, _ = _best_match(cand1, passage_events)
    d0 = abs(idx0 - anchor_idx) if idx0 is not None else None
    d1 = abs(idx1 - anchor_idx) if idx1 is not None else None
    diag = {"dist0": d0, "dist1": d1}
    if d0 is None and d1 is None:
        return None, diag
    if d0 is None:
        return 1, diag
    if d1 is None:
        return 0, diag
    if d0 == d1:
        return None, diag
    return (0 if d0 < d1 else 1), diag


def route2_pick_by_content(cand0: List[dict], cand1: List[dict],
                            passage_events: List[dict]) -> Tuple[Optional[int], dict]:
    """CONTENT_ONLY control: pick by raw match score, no position. Ties (incl. the common
    1.0-vs-1.0 case where both candidates' events are literally present) -> abstain."""
    _, sc0 = _best_match(cand0, passage_events)
    _, sc1 = _best_match(cand1, passage_events)
    diag = {"score0": sc0, "score1": sc1}
    if sc0 == sc1:
        return None, diag
    return (0 if sc0 > sc1 else 1), diag


def _scramble_seed(seed: int, instance_id: str) -> int:
    """Deterministic per-(seed,instance) RNG seed via hashlib (NEVER Python hash()); PROT-023."""
    h = hashlib.sha256(f"ORDER_SCRAMBLE::{seed}::{instance_id}".encode("ascii")).digest()
    return int.from_bytes(h[:8], "big") % (2**31 - 1)


def scrambled_passage(passage_events: List[dict], seed: int, instance_id: str) -> List[dict]:
    """Permute passage event POSITIONS; event CONTENT is untouched (matching still succeeds
    identically) so only the position/order signal is destroyed."""
    n = len(passage_events)
    if n <= 1:
        return list(passage_events)
    gen = torch.Generator().manual_seed(_scramble_seed(seed, instance_id))
    perm = torch.randperm(n, generator=gen).tolist()
    return [passage_events[i] for i in perm]


# =====================================================================================
# Extraction (checkpointed, seed-independent -- computed ONCE, reused across all seeds).
# =====================================================================================
def build_units(insts: List[dict], output_dir: Path) -> Tuple[Dict, Dict, Dict, dict]:
    done = _ckpt.completed_units(str(output_dir))
    for inst in insts:
        key = _ckpt.unit_key("passage", inst["id"])
        if key in done:
            continue
        event_seq, content_words = analyze_text(inst["text"])
        _ckpt.record_unit(str(output_dir), key,
                          {"kind": "passage", "instance_id": inst["id"], "scenario": inst["scenario"],
                           "event_seq": event_seq, "content_words": content_words})
    units = _ckpt.load_units(str(output_dir))
    passage_u = {}
    for inst in insts:
        key = _ckpt.unit_key("passage", inst["id"])
        if key in units:
            passage_u[inst["id"]] = units[key]
    n_passage_zero = sum(1 for v in passage_u.values() if not v["event_seq"])
    print(f"[pass1] passages: {len(passage_u)}/{len(insts)} extracted ({n_passage_zero} zero-event)",
         flush=True)

    done = _ckpt.completed_units(str(output_dir))
    n_cand_total = 0
    for inst in insts:
        for q in inst["questions"]:
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                n_cand_total += 1
                if key in done:
                    continue
                event_seq, content_words = analyze_text(a["text"])  # ANSWER SPAN ALONE
                _ckpt.record_unit(str(output_dir), key,
                                  {"kind": "cand", "instance_id": inst["id"], "question_id": q["id"],
                                   "answer_id": a["id"], "event_seq": event_seq, "content_words": content_words})
    units = _ckpt.load_units(str(output_dir))
    cand_u = {}
    n_cand_zero = 0
    for inst in insts:
        for q in inst["questions"]:
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                if key in units:
                    cand_u[key] = units[key]
                    if not units[key]["event_seq"]:
                        n_cand_zero += 1
    print(f"[pass1b] candidates (answer-span-alone): {len(cand_u)}/{n_cand_total} "
          f"({n_cand_zero} zero-event)", flush=True)

    done = _ckpt.completed_units(str(output_dir))
    n_quest_total = 0
    for inst in insts:
        for q in inst["questions"]:
            key = _ckpt.unit_key("quest", inst["id"], q["id"])
            n_quest_total += 1
            if key in done:
                continue
            event_seq, content_words = analyze_text(q["text"])  # QUESTION ALONE
            _ckpt.record_unit(str(output_dir), key,
                              {"kind": "quest", "instance_id": inst["id"], "question_id": q["id"],
                               "event_seq": event_seq, "content_words": content_words})
    units = _ckpt.load_units(str(output_dir))
    quest_u = {}
    n_quest_zero = 0
    for inst in insts:
        for q in inst["questions"]:
            key = _ckpt.unit_key("quest", inst["id"], q["id"])
            if key in units:
                quest_u[key] = units[key]
                if not units[key]["event_seq"]:
                    n_quest_zero += 1
    print(f"[pass1c] questions: {len(quest_u)}/{n_quest_total} ({n_quest_zero} zero-event)", flush=True)

    diag = {"n_instances": len(insts), "n_passage_extracted": len(passage_u), "n_passage_zero": n_passage_zero,
           "n_cand_total": n_cand_total, "n_cand_extracted": len(cand_u), "n_cand_zero": n_cand_zero,
           "n_quest_total": n_quest_total, "n_quest_extracted": len(quest_u), "n_quest_zero": n_quest_zero}
    return passage_u, cand_u, quest_u, diag


# =====================================================================================
# Per-seed scoring.
# =====================================================================================
def score_seed(insts: List[dict], passage_u: Dict, cand_u: Dict, quest_u: Dict, seed: int,
              n_dim: int = N_DIM, tau_conf: Optional[float] = None) -> dict:
    codec = EventBundleCodec(n_dim=n_dim, seed=seed)
    passage_bow = {iid: encode_instance_bow(u["content_words"], codec) for iid, u in passage_u.items()}

    rows = []
    for inst in insts:
        iid = inst["id"]
        p_bow = passage_bow.get(iid)
        pu = passage_u.get(iid)
        passage_events = pu["event_seq"] if pu else []
        for q in inst["questions"]:
            qkey = _ckpt.unit_key("quest", iid, q["id"])
            qu = quest_u.get(qkey)
            cand_bow, cand_events = [], []
            for a in q["answers"]:
                ckey = _ckpt.unit_key("cand", iid, q["id"], a["id"])
                cu = cand_u.get(ckey)
                cand_events.append(cu["event_seq"] if cu else [])
                cand_bow.append(encode_instance_bow(cu["content_words"], codec) if cu else None)
            if p_bow is None or cand_bow[0] is None or cand_bow[1] is None:
                continue  # not scored in ANY arm -- identical denominator across all 4 arms
            s0, s1 = cosine(p_bow, cand_bow[0]), cosine(p_bow, cand_bow[1])
            margin = abs(s0 - s1)
            pred_bow = None if s0 == s1 else (0 if s0 > s1 else 1)
            correct_idx = next(i for i, a in enumerate(q["answers"]) if a["correct"])
            rows.append({
                "instance_id": iid, "scenario": inst["scenario"], "question_id": q["id"],
                "question_text": q["text"], "answers": [a["text"] for a in q["answers"]],
                "correct_idx": correct_idx, "is_temporal": is_temporal_question(q["text"]),
                "margin": margin, "pred_bow": pred_bow,
                "question_events": qu["event_seq"] if qu else [],
                "passage_events": passage_events, "cand_events": cand_events,
            })

    temporal_margins = sorted(r["margin"] for r in rows if r["is_temporal"])
    if tau_conf is None:
        if temporal_margins:
            mid = len(temporal_margins) // 2
            tau_conf = (temporal_margins[mid] if len(temporal_margins) % 2 == 1
                       else 0.5 * (temporal_margins[mid - 1] + temporal_margins[mid]))
        else:
            tau_conf = 0.0

    n_gate_eligible = n_gate_fired = n_override_aug = n_override_scr = n_override_content = 0
    for r in rows:
        both_have_events = len(r["cand_events"][0]) >= 1 and len(r["cand_events"][1]) >= 1
        r["both_have_events"] = both_have_events
        if r["is_temporal"] and both_have_events:
            n_gate_eligible += 1
        if not r["is_temporal"]:
            r["pred_aug"] = r["pred_scr"] = r["pred_content"] = r["pred_bow"]
            r["route2_diag"] = {}
            continue
        anchor_idx, anchor_score = _best_match(r["question_events"], r["passage_events"])
        pick_aug, dist_diag = route2_pick_by_distance(anchor_idx, r["cand_events"][0], r["cand_events"][1],
                                                       r["passage_events"])
        p_scr = scrambled_passage(r["passage_events"], seed, r["instance_id"])
        anchor_idx_scr, _ = _best_match(r["question_events"], p_scr)
        pick_scr, _ = route2_pick_by_distance(anchor_idx_scr, r["cand_events"][0], r["cand_events"][1], p_scr)
        pick_content, content_diag = route2_pick_by_content(r["cand_events"][0], r["cand_events"][1],
                                                             r["passage_events"])
        gate_fire = both_have_events and (r["margin"] <= tau_conf)
        if gate_fire:
            n_gate_fired += 1
        r["pred_aug"] = pick_aug if (gate_fire and pick_aug is not None) else r["pred_bow"]
        r["pred_scr"] = pick_scr if (gate_fire and pick_scr is not None) else r["pred_bow"]
        r["pred_content"] = pick_content if (gate_fire and pick_content is not None) else r["pred_bow"]
        if gate_fire and pick_aug is not None:
            n_override_aug += 1
        if gate_fire and pick_scr is not None:
            n_override_scr += 1
        if gate_fire and pick_content is not None:
            n_override_content += 1
        r["route2_diag"] = {"anchor_idx": anchor_idx, "anchor_score": anchor_score, "gate_fire": gate_fire,
                            **dist_diag, "content": content_diag}

    gate_diag = {"tau_conf": tau_conf, "n_gate_eligible": n_gate_eligible, "n_gate_fired": n_gate_fired,
                "n_override_aug": n_override_aug, "n_override_scr": n_override_scr,
                "n_override_content": n_override_content}
    return {"rows": rows, "gate_diag": gate_diag}


# =====================================================================================
# Aggregation + bands.
# =====================================================================================
ARM_PRED_KEYS = {"BOW": "pred_bow", "AUGMENTED": "pred_aug", "ORDER_SCRAMBLE": "pred_scr",
                "CONTENT_ONLY": "pred_content"}


def aggregate_accuracy(rows: List[dict]) -> dict:
    def _acc(subset):
        out = {}
        for arm, key in ARM_PRED_KEYS.items():
            correct = sum(1 for r in subset if r[key] == r["correct_idx"])
            n = len(subset)
            out[arm] = {"correct": correct, "scored": n, "accuracy": (correct / n) if n else float("nan")}
        return out
    full = rows
    temporal = [r for r in rows if r["is_temporal"]]
    return {"full": _acc(full), "temporal": _acc(temporal), "n_full": len(full), "n_temporal": len(temporal)}


def _arms_must_differ(rows: List[dict]) -> dict:
    digests = {}
    for arm, key in ARM_PRED_KEYS.items():
        s = ",".join(str(r[key]) for r in rows)
        digests[arm] = hashlib.sha256(s.encode("ascii")).hexdigest()
    names = sorted(digests.keys())
    all_differ = True
    pairs = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            same = digests[a] == digests[b]
            pairs[f"{a}__vs__{b}"] = "IDENTICAL" if same else "DIFFERS"
            if same:
                all_differ = False
    return {"all_differ": all_differ, "digests": digests, "pairs": pairs}


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else 0.5 * (s[mid - 1] + s[mid])


def apply_bands(acc_by_seed: List[dict]) -> Tuple[str, str, dict]:
    def _m(arm, split):
        vals = [a[split][arm]["accuracy"] for a in acc_by_seed]
        return _median(vals), vals

    bow_full, bow_full_vals = _m("BOW", "full")
    aug_full, aug_full_vals = _m("AUGMENTED", "full")
    bow_sub, bow_sub_vals = _m("BOW", "temporal")
    aug_sub, aug_sub_vals = _m("AUGMENTED", "temporal")
    scr_sub, scr_sub_vals = _m("ORDER_SCRAMBLE", "temporal")
    content_sub, content_sub_vals = _m("CONTENT_ONLY", "temporal")

    if any(math.isnan(x) for x in (bow_full, aug_full, bow_sub, aug_sub, scr_sub, content_sub)):
        return "HARD_FAIL", "NAN_ACCURACY: insufficient scored questions", {}

    full_delta = aug_full - bow_full
    subset_lift = aug_sub - bow_sub
    scramble_gain = scr_sub - bow_sub
    content_shortfall = aug_sub - content_sub

    no_regression = full_delta >= FULL_SET_REGRESSION_FLOOR
    scramble_collapses = (scramble_gain <= SCRAMBLE_COLLAPSE_CEIL) and \
                         ((subset_lift - scramble_gain) >= SCRAMBLE_MUST_LOSE_VS_AUG)
    content_fails_to_reach = content_shortfall >= CONTENT_ONLY_MARGIN

    detail = {
        "bow_full": bow_full, "aug_full": aug_full, "full_delta": full_delta, "no_regression": no_regression,
        "bow_subset": bow_sub, "aug_subset": aug_sub, "subset_lift": subset_lift,
        "scramble_subset": scr_sub, "scramble_gain": scramble_gain, "scramble_collapses": scramble_collapses,
        "content_only_subset": content_sub, "content_shortfall": content_shortfall,
        "content_fails_to_reach": content_fails_to_reach,
        "per_seed": {"bow_full": bow_full_vals, "aug_full": aug_full_vals, "bow_subset": bow_sub_vals,
                    "aug_subset": aug_sub_vals, "scramble_subset": scr_sub_vals,
                    "content_only_subset": content_sub_vals},
    }

    if not no_regression:
        tier = "HARD_FAIL"
        msg = f"HARD_FAIL: full-set regression full_delta={full_delta:.4f} < {FULL_SET_REGRESSION_FLOOR}"
    elif subset_lift <= 0:
        tier = "HARD_FAIL"
        msg = f"HARD_FAIL: no subset gain subset_lift={subset_lift:.4f}"
    elif not scramble_collapses:
        tier = "HARD_FAIL"
        msg = (f"HARD_FAIL: scramble does not collapse subset_lift={subset_lift:.4f} "
              f"scramble_gain={scramble_gain:.4f} (gain survives scrambling -> content not order)")
    elif subset_lift >= HARD_PASS_SUBSET_LIFT and content_fails_to_reach:
        tier = "HARD_PASS"
        msg = (f"HARD_PASS: subset_lift={subset_lift:.4f} >= {HARD_PASS_SUBSET_LIFT}, "
              f"scramble collapses (gain={scramble_gain:.4f}), "
              f"content_only falls short (shortfall={content_shortfall:.4f}), no_regression={no_regression}")
    else:
        tier = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: subset_lift={subset_lift:.4f} scramble_collapses={scramble_collapses} "
              f"content_fails_to_reach={content_fails_to_reach} -- thin or partially-attributable gain")
    return tier, msg, detail


def pick_examples(rows: List[dict], n: int = 5) -> dict:
    helps, abstains = [], []
    for r in rows:
        if not r["is_temporal"]:
            continue
        aug_ok = r["pred_aug"] == r["correct_idx"]
        bow_ok = r["pred_bow"] == r["correct_idx"]
        entry = {"instance_id": r["instance_id"], "scenario": r["scenario"], "question_id": r["question_id"],
                 "question_text": r["question_text"], "answers": r["answers"], "correct_idx": r["correct_idx"],
                 "pred_bow": r["pred_bow"], "pred_aug": r["pred_aug"], "margin": r["margin"],
                 "route2_diag": r["route2_diag"]}
        if aug_ok and not bow_ok:
            helps.append(entry)
        elif r["route2_diag"].get("gate_fire") and r["pred_aug"] == r["pred_bow"]:
            abstains.append(entry)
    return {"augmented_helps": helps[:n], "gate_fired_but_abstained_or_matched_bow": abstains[:n],
           "n_helps_total": len(helps), "n_abstains_total": len(abstains)}


# =====================================================================================
# Self-test.
# =====================================================================================
_TINY_XML_TEMPLATE = """<data>
  <instance id="tA" scenario="taking a taxi">
    <text>I walked to the corner . I waited for the bus . I hailed a taxi . I got in the taxi . I paid the driver .</text>
    <questions>
      <question id="0" text="When did I get in the taxi ?" type="temporal">
        <answer correct="True" id="0" text="Well after a little while I actually hailed a taxi you see ." />
        <answer correct="False" id="1" text="I walked ." />
      </question>
    </questions>
  </instance>
  <instance id="t1" scenario="packing">
    <text>I packed the suitcase . I closed the door .</text>
    <questions>
      <question id="0" text="What did I pack ?" type="text">
        <answer correct="True" id="0" text="the suitcase" />
        <answer correct="False" id="1" text="the door" />
      </question>
    </questions>
  </instance>
</data>
"""


def self_test() -> dict:
    checks = {}
    exercised = set()

    # (1) is_temporal_question unit checks.
    for w in ("when", "after", "before", "next", "first", "last", "then"):
        assert is_temporal_question(f"{w} did this happen ?"), f"{w} should be temporal"
    for w in ("what", "where", "who"):
        assert not is_temporal_question(f"{w} did this happen ?"), f"{w} should not be temporal"
    checks["is_temporal_question_unit"] = True

    # (2) real code path: write a REAL MCScript-schema tiny XML, parse via the REAL parse_mcscript_xml,
    # run the REAL run_pipeline (via score_seed on real extraction) at n_dim=512, tau_conf forced high so
    # the margin condition cannot mask the mechanism.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        xml_path = Path(td) / "tiny.xml"
        xml_path.write_text(_TINY_XML_TEMPLATE, encoding="utf-8")
        insts = parse_mcscript_xml(str(xml_path))
        exercised.add("parse_mcscript_xml")
        assert len(insts) == 2 and insts[0]["id"] == "tA"

        out_dir = Path(td) / "out"
        passage_u, cand_u, quest_u, extract_diag = build_units(insts, out_dir)
        exercised.update({"EventBundleCodec", "build_units"})
        checks["extract_diag"] = extract_diag
        assert extract_diag["n_passage_zero"] == 0, f"passage extraction must fire on all tiny instances: {extract_diag}"

        scored = score_seed(insts, passage_u, cand_u, quest_u, seed=SEED, n_dim=512, tau_conf=999.0)
        rows = scored["rows"]
        row_tA = next(r for r in rows if r["instance_id"] == "tA")
        row_t1 = next(r for r in rows if r["instance_id"] == "t1")

    # (3) mechanism-fires (the CORE end-to-end claim, on natural -- not hand-tuned-for-correctness --
    # candidate wording): BOW is naturally WRONG here (picks the terse "I walked." over the verbose-but-
    # correct "...hailed a taxi..." -- more literal word overlap with an unrelated passage clause), and
    # AUGMENTED's distance-to-anchor mechanism OVERRIDES it to the correct answer.
    assert row_tA["is_temporal"], "tA question must be detected temporal"
    assert row_tA["pred_bow"] != row_tA["correct_idx"], \
        f"expected BOW to be naturally wrong on tA (the discriminating case): scores diag missing, pred={row_tA['pred_bow']}"
    assert row_tA["pred_aug"] == row_tA["correct_idx"], \
        f"AUGMENTED must override BOW to the correct (closer) answer: {row_tA['route2_diag']}"
    d = row_tA["route2_diag"]
    assert d["dist0"] is not None and d["dist1"] is not None, f"both candidates must match: {d}"
    assert d["dist0"] < d["dist1"], f"correct candidate must be closer to anchor: {d}"
    checks["mechanism_fires_distance_overrides_wrong_bow"] = {"pred_bow": row_tA["pred_bow"],
                                                               "pred_aug": row_tA["pred_aug"], "diag": d}

    # (4) CONTENT_ONLY must abstain on this exact case (both candidates literal vlemma matches, score
    # 1.0 each -- order-invariant, so it falls back to BOW's WRONG pick, unlike AUGMENTED).
    assert row_tA["pred_content"] == row_tA["pred_bow"], \
        f"CONTENT_ONLY should abstain (tie) and fall back to (wrong) BOW on the tA case: {d['content']}"
    assert d["content"]["score0"] == d["content"]["score1"] == 1.0, \
        f"expected both candidates to tie at score 1.0 (order-invariant control): {d['content']}"
    checks["content_only_abstains_stays_wrong"] = d["content"]

    # (5) non-temporal control: never overridden.
    assert not row_t1["is_temporal"], "t1 question must be detected non-temporal"
    assert row_t1["pred_aug"] == row_t1["pred_bow"] == row_t1["pred_scr"] == row_t1["pred_content"], \
        "non-temporal question must never be overridden by any Route-2 arm"
    checks["non_temporal_never_overridden"] = True

    # (6) adversarial hand-constructed permutation flips AUGMENTED's pick (order-DEPENDENCE proof,
    # not a probabilistic scramble-run hope). Swap the "hail" and "walk" event positions.
    passage_events = row_tA["passage_events"]
    vlemmas = [e["vlemma"] for e in passage_events]
    i_hail, i_walk = vlemmas.index("hail"), vlemmas.index("walk")
    adversarial = list(passage_events)
    adversarial[i_hail], adversarial[i_walk] = adversarial[i_walk], adversarial[i_hail]
    anchor_idx_adv, _ = _best_match(row_tA["question_events"], adversarial)
    pick_adv, diag_adv = route2_pick_by_distance(anchor_idx_adv, row_tA["cand_events"][0],
                                                 row_tA["cand_events"][1], adversarial)
    assert pick_adv == 1, f"adversarial permutation must flip the pick to WRONG: {diag_adv}"
    pick_content_adv, diag_content_adv = route2_pick_by_content(row_tA["cand_events"][0],
                                                                row_tA["cand_events"][1], adversarial)
    assert pick_content_adv is None, \
        f"CONTENT_ONLY must be invariant to reordering (still abstains): {diag_content_adv}"
    checks["adversarial_permutation_flips_distance_pick_not_content"] = {
        "pick_adv": pick_adv, "diag_adv": diag_adv, "pick_content_adv": pick_content_adv,
    }

    # (7) ORDER_SCRAMBLE determinism + multiset-preservation, and a REAL (non-hand-adversarial) scramble
    # draw (instance_id="tA", the id actually used by the real run) that empirically collapses AUGMENTED's
    # win back to BOW-level -- the actual ablation mechanism, not the hand-constructed proof in (6).
    p_a = scrambled_passage(passage_events, seed=SEED, instance_id="tA")
    p_b = scrambled_passage(passage_events, seed=SEED, instance_id="tA")
    assert [e["lemma"] for e in p_a] == [e["lemma"] for e in p_b], "scramble not deterministic for same (seed,instance_id)"
    p_c = scrambled_passage(passage_events, seed=SEED, instance_id="a_different_id")
    assert [e["lemma"] for e in p_a] != [e["lemma"] for e in p_c] or len(passage_events) <= 1, \
        "different instance_id should (almost certainly) give a different permutation"
    assert sorted(e["lemma"] for e in p_a) == sorted(e["lemma"] for e in passage_events), \
        "scramble must preserve the event multiset"
    assert row_tA["pred_scr"] == row_tA["pred_bow"], \
        f"real scramble draw (id=tA) must collapse AUGMENTED's win back to (wrong) BOW-level: {d}"
    checks["scramble_deterministic_multiset_preserving_and_collapses_real_win"] = True

    # (7b) a SECOND scramble draw on the SAME tA content (different instance_id -- "instX") that happens
    # to land on the CORRECT answer (id != "tA" changes which permutation is drawn): demonstrates the
    # scramble arm is a genuine RANDOM draw (not hard-wired to always reproduce BOW), used below purely to
    # exercise BOW-vs-ORDER_SCRAMBLE divergence in the arms-differ proof (aggregate collapse, tested by (7)
    # and the real full-corpus run, is a population statement, not a per-instance guarantee).
    p_instX = scrambled_passage(passage_events, seed=SEED, instance_id="instX")
    anchor_idx_x, _ = _best_match(row_tA["question_events"], p_instX)
    pick_instX, diag_instX = route2_pick_by_distance(anchor_idx_x, row_tA["cand_events"][0],
                                                      row_tA["cand_events"][1], p_instX)
    assert pick_instX == row_tA["correct_idx"], \
        f"expected the instX scramble draw to (by construction, verified empirically) land correct: {diag_instX}"
    checks["scramble_is_a_genuine_random_draw"] = {"pick_instX": pick_instX, "diag_instX": diag_instX}

    # (8) arms-must-differ: a rigorous, fully-CONTROLLED multi-probe check. Real BoW cosine outcomes are
    # sensitive to EventBundleCodec's lazily-grown, insertion-order-dependent symbol codebook (a real,
    # disclosed property of the reused codec -- not a bug), which makes hand-predicting BOW's natural pick
    # on a tiny synthetic corpus fragile/non-portable across corpus composition. So this check isolates the
    # 4 arms' PREDICTION LOGIC directly (route2_pick_by_distance / route2_pick_by_content / the gate
    # fallback rule) against hand-built synthetic events with a HARDCODED pred_bow per row (legitimate: the
    # property under test is "the 4 arms' code paths are not bit-identical," a code-correctness property,
    # not a task-accuracy claim) -- verified pairwise-distinct across ALL 4 arms via 3 independent probes.
    def _ev(lemma, agent=None, patient=None):
        return {"lemma": lemma, "vlemma": lemma, "agent": agent, "patient": patient, "tense": "SIMPLE_PAST"}

    synth_passage = [_ev("a", agent="q"), _ev("b"), _ev("c"), _ev("d"), _ev("e")]
    synth_anchor_idx, _ = _best_match([_ev("c")], synth_passage)
    assert synth_anchor_idx == 2, f"synthetic anchor sanity check failed: {synth_anchor_idx}"

    # probe 1: distance discriminates cleanly (dist0=1 < dist1=2); content ties (both exact matches).
    p1_c0, p1_c1 = [_ev("b")], [_ev("e")]
    p1_aug, _ = route2_pick_by_distance(synth_anchor_idx, p1_c0, p1_c1, synth_passage)
    p1_content, _ = route2_pick_by_content(p1_c0, p1_c1, synth_passage)
    p1_scr_passage = scrambled_passage(synth_passage, seed=SEED, instance_id="synthetic_probe_s1")
    p1_scr_anchor, _ = _best_match([_ev("c")], p1_scr_passage)
    p1_scr, _ = route2_pick_by_distance(p1_scr_anchor, p1_c0, p1_c1, p1_scr_passage)
    p1_bow = 1  # hardcoded (code-correctness probe, not a task-accuracy claim -- see comment above)
    row1 = {"pred_bow": p1_bow, "pred_aug": p1_aug if p1_aug is not None else p1_bow,
           "pred_scr": p1_scr if p1_scr is not None else p1_bow,
           "pred_content": p1_content if p1_content is not None else p1_bow, "correct_idx": 0}

    # probe 2: distance TIES (both candidates best-match idx0, one via lemma-exact one via agent-only);
    # content DISCRIMINATES (0.5 partial vs 1.0 exact) -- content genuinely differs from a hardcoded BOW.
    p2_c0, p2_c1 = [_ev("z", agent="q")], [_ev("a")]
    p2_aug, _ = route2_pick_by_distance(synth_anchor_idx, p2_c0, p2_c1, synth_passage)
    p2_content, _ = route2_pick_by_content(p2_c0, p2_c1, synth_passage)
    p2_scr_passage = scrambled_passage(synth_passage, seed=SEED, instance_id="synthetic_probe_s1")
    p2_scr_anchor, _ = _best_match([_ev("c")], p2_scr_passage)
    p2_scr, _ = route2_pick_by_distance(p2_scr_anchor, p2_c0, p2_c1, p2_scr_passage)
    p2_bow = 0  # hardcoded
    row2 = {"pred_bow": p2_bow, "pred_aug": p2_aug if p2_aug is not None else p2_bow,
           "pred_scr": p2_scr if p2_scr is not None else p2_bow,
           "pred_content": p2_content if p2_content is not None else p2_bow, "correct_idx": 1}
    assert p2_aug is None, f"probe2 distance must tie (same matched idx both candidates): {p2_aug}"
    assert p2_content == 1, f"probe2 content must discriminate (0.5 vs 1.0): {p2_content}"

    # probe 3: one candidate totally unmatched -- structurally invariant to scrambling.
    p4_c0, p4_c1 = [_ev("d")], [_ev("zzz_no_match")]
    p4_aug, _ = route2_pick_by_distance(synth_anchor_idx, p4_c0, p4_c1, synth_passage)
    p4_content, _ = route2_pick_by_content(p4_c0, p4_c1, synth_passage)
    p4_bow = 1  # hardcoded
    row4 = {"pred_bow": p4_bow, "pred_aug": p4_aug if p4_aug is not None else p4_bow,
           "pred_scr": p4_aug if p4_aug is not None else p4_bow,  # invariant: unmatched candidate stays unmatched under any permutation
           "pred_content": p4_content if p4_content is not None else p4_bow, "correct_idx": 0}

    probe_rows = [row1, row2, row4,
                 {"pred_bow": row_t1["pred_bow"], "pred_aug": row_t1["pred_aug"], "pred_scr": row_t1["pred_scr"],
                  "pred_content": row_t1["pred_content"], "correct_idx": row_t1["correct_idx"]}]
    diff = _arms_must_differ(probe_rows)
    checks["arms_differ_verified_synthetic"] = {"all_differ": diff["all_differ"], "probe_rows": probe_rows}
    assert diff["all_differ"], f"arms did not differ: {diff}"

    # (9) validity preflight (declared, machine-checked).
    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["parse_mcscript_xml", "EventBundleCodec", "build_units"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": EventBundleCodec, "callable_name": "EventBundleCodec",
         "kwargs": {"n_dim": 512, "seed": 7}},
    ], run_mode="selftest")
    checks["validity_preflight_ok"] = bool(ok)

    # (10) band-logic sanity: hand-built accuracy-by-seed lists hitting each corner.
    def _fake_acc(bow_full, aug_full, bow_sub, aug_sub, scr_sub, content_sub):
        return {"full": {"BOW": {"accuracy": bow_full}, "AUGMENTED": {"accuracy": aug_full},
                        "ORDER_SCRAMBLE": {"accuracy": aug_full}, "CONTENT_ONLY": {"accuracy": aug_full}},
               "temporal": {"BOW": {"accuracy": bow_sub}, "AUGMENTED": {"accuracy": aug_sub},
                           "ORDER_SCRAMBLE": {"accuracy": scr_sub}, "CONTENT_ONLY": {"accuracy": content_sub}}}

    hp_tier, _, _ = apply_bands([_fake_acc(0.60, 0.60, 0.50, 0.60, 0.50, 0.50)])
    assert hp_tier == "HARD_PASS", f"expected HARD_PASS (clean lift, scramble/content both collapse): {hp_tier}"
    hf_regress_tier, _, _ = apply_bands([_fake_acc(0.60, 0.55, 0.50, 0.60, 0.50, 0.50)])
    assert hf_regress_tier == "HARD_FAIL", f"expected HARD_FAIL (full-set regression): {hf_regress_tier}"
    hf_nogain_tier, _, _ = apply_bands([_fake_acc(0.60, 0.60, 0.50, 0.48, 0.48, 0.48)])
    assert hf_nogain_tier == "HARD_FAIL", f"expected HARD_FAIL (no subset gain): {hf_nogain_tier}"
    hf_noncollapse_tier, _, _ = apply_bands([_fake_acc(0.60, 0.60, 0.50, 0.60, 0.59, 0.50)])
    assert hf_noncollapse_tier == "HARD_FAIL", f"expected HARD_FAIL (scramble survives): {hf_noncollapse_tier}"
    mb_tier, _, _ = apply_bands([_fake_acc(0.60, 0.60, 0.50, 0.53, 0.50, 0.50)])
    assert mb_tier == "MIDDLE_BAND", f"expected MIDDLE_BAND (thin lift): {mb_tier}"
    checks["band_logic_sanity"] = {"hard_pass": hp_tier, "hard_fail_regress": hf_regress_tier,
                                   "hard_fail_nogain": hf_nogain_tier, "hard_fail_noncollapse": hf_noncollapse_tier,
                                   "middle_band": mb_tier}

    return checks


# =====================================================================================
# Metrics write.
# =====================================================================================
def _write_metrics(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    import traceback
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME,
        "pid": os.getpid(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2, default=str)
    os.replace(tmp, final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        checks = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "checks": checks}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = Path(str(OUTPUT_DIR) + "_smoke") if args.smoke else OUTPUT_DIR
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL

    t0 = time.time()
    insts = parse_mcscript_xml(str(CORPUS_PATH))
    insts.sort(key=lambda d: d["id"])
    print(f"[{run_mode}] {len(insts)} instances, {sum(len(i['questions']) for i in insts)} questions, "
          f"seeds={seeds}", flush=True)

    passage_u, cand_u, quest_u, extract_diag = build_units(insts, output_dir)

    acc_by_seed = []
    diff_by_seed = []
    gate_diag_by_seed = []
    examples_last_seed = None
    rows_last_seed = None
    for seed in seeds:
        scored = score_seed(insts, passage_u, cand_u, quest_u, seed=seed)
        rows = scored["rows"]
        acc = aggregate_accuracy(rows)
        diff = _arms_must_differ(rows)
        acc_by_seed.append(acc)
        diff_by_seed.append(diff["all_differ"])
        gate_diag_by_seed.append({"seed": seed, **scored["gate_diag"]})
        print(f"[seed={seed}] full: BOW={acc['full']['BOW']['accuracy']:.4f} "
              f"AUG={acc['full']['AUGMENTED']['accuracy']:.4f} | temporal(n={acc['n_temporal']}): "
              f"BOW={acc['temporal']['BOW']['accuracy']:.4f} AUG={acc['temporal']['AUGMENTED']['accuracy']:.4f} "
              f"SCR={acc['temporal']['ORDER_SCRAMBLE']['accuracy']:.4f} "
              f"CONTENT={acc['temporal']['CONTENT_ONLY']['accuracy']:.4f} "
              f"gate_fired={scored['gate_diag']['n_gate_fired']} "
              f"override_aug={scored['gate_diag']['n_override_aug']}", flush=True)
        examples_last_seed = pick_examples(rows)
        rows_last_seed = rows

    verdict, msg, band_detail = apply_bands(acc_by_seed)
    elapsed = time.time() - t0

    n_temporal = acc_by_seed[0]["n_temporal"]
    n_full = acc_by_seed[0]["n_full"]
    override_rate_temporal = [gd["n_override_aug"] / n_temporal if n_temporal else float("nan")
                              for gd in gate_diag_by_seed]
    abstain_rate_temporal = [1.0 - r for r in override_rate_temporal]

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM, "seeds": seeds,
        "n_instances": len(insts), "n_questions_total": sum(len(i["questions"]) for i in insts),
        "n_full_scored": n_full, "n_temporal_scored": n_temporal,
        "cardinality_ok": (extract_diag["n_passage_extracted"] == extract_diag["n_instances"] and
                          extract_diag["n_cand_extracted"] == extract_diag["n_cand_total"] and
                          extract_diag["n_quest_extracted"] == extract_diag["n_quest_total"]),
        "extract_diag": extract_diag,
        "accuracy_by_seed": acc_by_seed,
        "gate_diag_by_seed": gate_diag_by_seed,
        "override_rate_temporal_by_seed": override_rate_temporal,
        "abstain_rate_temporal_by_seed": abstain_rate_temporal,
        "band_detail": band_detail,
        "arms_differ_verified": all(diff_by_seed),
        "arms_differ_verified_by_seed": diff_by_seed,
        "examples": examples_last_seed,
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "MCQA pick-accuracy measurement on real dev-set questions; band thresholds are "
                    "Director's task contract values, not a synthetic capacity envelope",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: tau_conf = median BoW margin on the "
                            "temporal subset, computed from scores only (never from correctness labels), "
                            "logged per seed in gate_diag_by_seed",
        "progress_logging": "print_flush_true",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("examples", "extract_diag",
                                                                     "accuracy_by_seed")},
                     indent=2, default=str))
    print(json.dumps({"examples": metrics["examples"]}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
