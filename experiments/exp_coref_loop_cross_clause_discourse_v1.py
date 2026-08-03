"""SELF-IMPROVING-READER LOOP, cycle 3: cross-clause discourse coref (the ~53% frontier),
BRAIN-FIRST per the fidelity audit (2026-08-02).

Audit: notes/brain_fidelity_audit_and_path_to_fully_capable_comprehension_2026-08-02.md (bd0faab3c).
Two named brain-fidelity levers, built here as ABLATABLE arms on top of strict_cb (our best coref,
commit 5b266248f; imported verbatim, NEVER mutated):

  (1) DECAY-WINDOW (audit A2 fix). strict_cb's antecedent rule is MAX-only over subject clauses (a
      hard "most-recent agent" pointer). The audit (Garrod&Sanford scenario-mapping; McKoon&Ratcliff
      resonance; ACT-R decay buffers) says referent accessibility is a recency-WEIGHTED WINDOW, not a
      hard point. This arm ranks compatible candidates by a recency-decayed salience over the last
      WINDOW clauses (sum of DECAY**(cur_clause-c) over the entity's recent mention clauses), falling
      back to strict_cb when the window has no signal.

  (2) SPEAKER/ADDRESSEE DEIXIS (audit B1 / Walker-Joshi-Prince dialogue Centering). The bulk of the
      53% frontier is dialogue-turn cases where an in-quote 3rd-person pronoun refers to the ABSENT
      third party being talked about -- neither the speaker (who would be "I") nor the addressee (who
      would be "you"). Brain-faithful deictic constraint: a 3rd-person pronoun INSIDE a quote cannot
      corefer with the current speaker or addressee. This arm detects the quotative attribution
      ("said/replied/asked NAME") per clause, tracks the addressee as the most-recent prior DIFFERENT
      speaker (alternating-turn model), and -- for a pronoun whose text position falls inside an
      actual quote span -- EXCLUDES the speaker and addressee entities from its candidate pool. Gated
      on real quote-span membership (double-quote delimited) so it fires on quoted dialogue
      (Philip/Stephen) and does NOT misfire on unquoted narration frames ("and he took the darts",
      where a post-quote 3rd-person pronoun refers back to the speaker).

  (3) DEFINITE-DESCRIPTION BRIDGING (audit B1, optional) -- DEFERRED this cycle (noted in metrics):
      "the mercurial little Frenchman" = Tonish needs a description->name category-bridge over the
      dictionary; the two Tonish cases are a small minority and the bridge interacts with the name-
      branch (not the pronoun branch these two levers target). Held for a focused follow-up.

ARMS (one clean comparison + ablation, same streams/event-slots): strict_cb (BASELINE) vs
decay_window (lever 1 alone) vs speaker_deixis (lever 2 alone) vs combined (both). oracle /
recency_floor / singleton_floor for query-metric context. Ablation isolates which lever drives lift.

OPT-IN / NEVER-MUTATE: strict_cb + helpers, the query machinery (exp_wire_coref_accumulate_
situation_model_v1, e6a3a9ee8), the clean link label (calibration v1), the principle_b cell -- all
imported verbatim. run_loop_discourse / enrich_dialogue are NEW opt-in functions here.

MEASURE (powered combined eval, 36 passages, 130 queries, 76 pronoun decisions; g5g6 secondary):
  1. pronoun-only B3-F1 (beat strict_cb ~0.703? name/overall no regression).
  2. identity-demanding situation-model query acc (reuse run_arm_on_passage; move strict_cb ~0.719
     toward oracle ~0.930?).
  3. DIRECT on the probe's flagged-wrong cases (data/probe_fix_tier_verb_semantic_ceiling_v1_cases
     .json, 17 cases; B2 cross-clause subset tagged): corrected vs broken (net), per arm, with the
     clean link label -- guarded against regressing previously-correct decisions.

CAN-FAIL (pre-registered): HARD_PASS = combined arm net-positive on pronoun-B3 (>= PRONOUN_B3_MARGIN)
AND identity-demanding query (>= IDDEM_QUERY_MARGIN), driven by the cross-clause (B2) cases, no
name/overall regression, net corrected > 0. PARTIAL = one lever lifts coref-level (B3 + corrected)
but the query metric does not move, or only one metric moves. NULL = no lift -> honest report of WHICH
sub-mechanism failed and why (VET NEGATIVES AS HARD AS POSITIVES; decision traces dumped). REGRESSION
= name/overall B3 regresses beyond tol.

Self-test: python exp_coref_loop_cross_clause_discourse_v1.py --self-test
Full:      python exp_coref_loop_cross_clause_discourse_v1.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import torch  # noqa: E402

from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    gn_compatible,
    normalize_tokens,
    run_recency_floor,
    bcubed,
)
from exp_earn_coref_pronoun_strict_cb_v1 import (  # noqa: E402
    run_learnable_strict_cb,
    _EntityCb,
    _pick_strict_cb,
    _resolve_name_branch,
    SUBJECT_LIKE_ROLES,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    build_mention_stream_with_role,
    event_slots_for,
    run_singleton_floor,
    run_arm_on_passage,
    ROLE_VOCAB,
    D,
    MAX_EVENT_SLOTS,
    SEED,
)
from exp_coref_self_confidence_calibration_v1 import mention_link_wrong  # noqa: E402

ANCHOR_NAME = "coref_loop_cross_clause_discourse_v1"
_GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_PATH_COMBINED = os.path.join(_GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl")
GOLD_PATH_G5G6 = os.path.join(_GOLD_DIR, "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl")
PROBE_CASES_PATH = os.path.join(REPO_ROOT, "data", "probe_fix_tier_verb_semantic_ceiling_v1_cases.json")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# Lever-1 params (pre-registered a priori; small sensitivity check reported).
DECAY = 0.7          # recency half-life ~2 clauses (decay**2 ~ 0.5)
WINDOW = 4           # last ~3-4 clauses (audit A2)

# Lever-2 quotative detection.
SPEECH_VERBS = (r"said|says|replied|reply|asked|answered|cried|exclaimed|whispered|shouted|"
                r"added|continued|remarked|returned|says|responded|inquired")
_SPK_AFTER = re.compile(r"\b(?:" + SPEECH_VERBS + r")\s+([A-Z][a-z]+(?:'s)?)")
_SPK_BEFORE = re.compile(r"\b([A-Z][a-z]+)\s+(?:" + SPEECH_VERBS + r")\b")
SPEAKER_WINDOW = 4   # look back this many clauses for the alternating addressee

# Pre-registered bands.
PRONOUN_B3_MARGIN = 0.02
IDDEM_QUERY_MARGIN = 0.03
REGRESSION_TOL = 0.01

# B2 (cross-clause discourse) probe-case indices, 0-indexed into the 17-case probe file:
#   dialogue-turn topic: cases 4,5,6,12,16 -> idx 3,4,5,11,15; protagonist-continuity: case 17 ->
#   idx 16; description-bridging: cases 10,11 -> idx 9,10.
B2_CASE_INDICES = frozenset({3, 4, 5, 9, 10, 11, 15, 16})


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# Lever-2 support: per-clause speaker + addressee detection, per-mention quote-span membership.
# ---------------------------------------------------------------------------
def _detect_speaker(clause_text: str) -> Optional[str]:
    m = _SPK_AFTER.search(clause_text)
    if m:
        return m.group(1)
    m = _SPK_BEFORE.search(clause_text)
    if m:
        return m.group(1)
    return None


def _quote_spans(clause_lower: str) -> List[Tuple[int, int]]:
    """Char-offset spans between paired double quotes (offsets in the LOWERCASED clause, matching
    the mention stream's text_pos convention)."""
    positions = [i for i, ch in enumerate(clause_lower) if ch == '"']
    spans = []
    for k in range(0, len(positions) - 1, 2):
        spans.append((positions[k], positions[k + 1]))
    return spans


def enrich_dialogue(passage: dict, stream: List[dict]) -> List[dict]:
    """Augment (copy) each stream record with in_quote / clause_speaker / clause_addressee. Does not
    mutate the imported builder's output semantics -- only adds inert dialogue-frame fields."""
    clauses = passage["clauses"]
    speakers = [_detect_speaker(c) for c in clauses]
    # addressee = most-recent prior clause (within SPEAKER_WINDOW) whose speaker is not None and
    # differs from this clause's speaker (alternating-turn model).
    addressees: List[Optional[str]] = [None] * len(clauses)
    for i in range(len(clauses)):
        if speakers[i] is None:
            continue
        for j in range(i - 1, max(-1, i - 1 - SPEAKER_WINDOW), -1):
            if speakers[j] is not None and speakers[j] != speakers[i]:
                addressees[i] = speakers[j]
                break
    spans_by_clause = [_quote_spans(c.lower()) for c in clauses]
    out = []
    for rec in stream:
        r = dict(rec)
        ci = rec["clause"]
        tp = rec["text_pos"]
        in_q = any(s < tp < e for (s, e) in spans_by_clause[ci]) if 0 <= ci < len(clauses) else False
        r["in_quote"] = in_q
        r["clause_speaker"] = speakers[ci] if 0 <= ci < len(clauses) else None
        r["clause_addressee"] = addressees[ci] if 0 <= ci < len(clauses) else None
        out.append(r)
    return out


def _name_matches_entity(name: str, e: _EntityCb) -> bool:
    tok = name.lower().rstrip("'s")
    return tok in e.tokens or name.lower() in e.tokens


def _deixis_filter(compat: List[_EntityCb], rec: dict) -> Tuple[List[_EntityCb], bool]:
    """Exclude the speaker + addressee entities for an in-quote 3rd-person pronoun. Returns
    (filtered, fired). Abstains (returns compat, False) unless the pronoun is in a quote span, a
    speaker is known, and excluding still leaves >= 1 candidate."""
    if not rec.get("in_quote") or not rec.get("clause_speaker"):
        return compat, False
    excl_names = [rec["clause_speaker"]]
    if rec.get("clause_addressee"):
        excl_names.append(rec["clause_addressee"])
    filtered = [e for e in compat if not any(_name_matches_entity(n, e) for n in excl_names)]
    if filtered and len(filtered) < len(compat):
        return filtered, True
    return compat, False


# ---------------------------------------------------------------------------
# Lever-1 support: recency-decayed salience window.
# ---------------------------------------------------------------------------
def _pick_decay_window(compat: List[_EntityCb], cur_clause: int, decay: float,
                       window: int) -> Optional[_EntityCb]:
    """Rank compat by recency-decayed salience over the last `window` clauses (sum of
    decay**(cur-c) over the entity's mention clauses c with 0 < cur-c <= window). Returns None if no
    candidate has any in-window signal (caller falls back to strict_cb)."""
    best = None
    best_score = 0.0
    for e in compat:
        score = sum(decay ** (cur_clause - c) for c in e.clause_role
                    if 0 < (cur_clause - c) <= window)
        if score > best_score or (score == best_score and best is not None and e.last_pos > best.last_pos):
            if score > 0.0 and (best is None or score > best_score
                                or (score == best_score and e.last_pos > best.last_pos)):
                best = e
                best_score = score
    return best


# ---------------------------------------------------------------------------
# The cross-clause discourse resolver: strict_cb + optional lever-1 (decay window) and/or lever-2
# (speaker/addressee deixis) on the PRONOUN branch. Name/nominal branch byte-identical to strict_cb.
# ---------------------------------------------------------------------------
def run_loop_discourse(stream: List[dict], use_decay: bool, use_deixis: bool,
                       decay: float = DECAY, window: int = WINDOW) -> Tuple[List[int], Dict[str, int]]:
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    actions: Dict[str, int] = {}

    def _bump(k):
        actions[k] = actions.get(k, 0) + 1

    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                pool = compat
                if use_deixis:
                    pool, fired = _deixis_filter(pool, rec)
                    _bump("deixis_fired" if fired else "deixis_abstain")
                best = None
                if use_decay:
                    best = _pick_decay_window(pool, cur_clause, decay, window)
                    _bump("decay_window_used" if best is not None else "decay_window_fallback_strict_cb")
                if best is None:
                    best = _pick_strict_cb(pool, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                _bump("no_compat_fallback")
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
                _bump("allocate_new")
            best.count += 1
            best.last_pos = pos
            if cur_role is not None:
                best.clause_role[cur_clause] = cur_role
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        if cur_role is not None:
            best.clause_role[cur_clause] = cur_role
        assigned.append(best.eid)
    return assigned, actions


# ---------------------------------------------------------------------------
# Metrics helpers.
# ---------------------------------------------------------------------------
def _b3(streams: List[List[dict]], preds_by_arm: Dict[str, List[List[int]]]) -> dict:
    out = {}
    for arm, preds in preds_by_arm.items():
        pairs = list(zip(streams, preds))
        out[arm] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }
    return out


def _query_metrics(passages: List[dict], streams: List[List[dict]],
                    cluster_ids_by_arm: Dict[str, List[List[str]]]) -> dict:
    arm_seed_idx = {"oracle": 0, "strict_cb": 1, "decay_window": 2, "speaker_deixis": 3,
                    "combined": 4, "recency_floor": 5, "singleton_floor": 6}
    results: Dict[str, dict] = {}
    for arm, cid_lists in cluster_ids_by_arm.items():
        qc = qt = qc_id = qt_id = qc_pr = qt_pr = 0
        for p_idx, (p, s, cids) in enumerate(zip(passages, streams, cid_lists)):
            event_slots, n_slots, clause_to_slot = event_slots_for(s)
            gen = torch.Generator().manual_seed(SEED + p_idx * 100 + arm_seed_idx[arm])
            res = run_arm_on_passage(p, s, cids, event_slots, clause_to_slot,
                                     ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
            qc += res["q_correct"]; qt += res["q_total"]
            qc_id += res["q_correct_iddem"]; qt_id += res["q_total_iddem"]
            qc_pr += res["q_correct_pron"]; qt_pr += res["q_total_pron"]
        results[arm] = {
            "query_accuracy_all": (qc / qt) if qt else None, "q_total": qt,
            "query_accuracy_identity_demanding": (qc_id / qt_id) if qt_id else None,
            "q_total_iddem": qt_id,
            "query_accuracy_pronoun_contributed": (qc_pr / qt_pr) if qt_pr else None,
            "q_total_pron": qt_pr,
        }
    return results


def _arm_preds(passages: List[dict], streams: List[List[dict]]) -> Dict[str, List[List[int]]]:
    cb = [run_learnable_strict_cb(s) for s in streams]
    dw = [run_loop_discourse(s, use_decay=True, use_deixis=False)[0] for s in streams]
    sd = [run_loop_discourse(s, use_decay=False, use_deixis=True)[0] for s in streams]
    cm = [run_loop_discourse(s, use_decay=True, use_deixis=True)[0] for s in streams]
    return {"strict_cb": cb, "decay_window": dw, "speaker_deixis": sd, "combined": cm}


def _corrected_broken(passages: List[dict], streams: List[List[dict]],
                      preds: Dict[str, List[List[int]]]) -> dict:
    """Clean-label corrected vs broken per arm, over ALL pronoun decisions."""
    out = {}
    cb = preds["strict_cb"]
    for arm in ("decay_window", "speaker_deixis", "combined"):
        ap = preds[arm]
        corr = broke = changed = 0
        for s, base, new in zip(streams, cb, ap):
            for pos, rec in enumerate(s):
                if not rec["is_pronoun"]:
                    continue
                if base[pos] == new[pos]:
                    continue
                changed += 1
                bw = mention_link_wrong(pos, s, base)
                nw = mention_link_wrong(pos, s, new)
                if bw and not nw:
                    corr += 1
                elif nw and not bw:
                    broke += 1
        out[arm] = {"corrected": corr, "broken": broke, "net": corr - broke, "changed": changed}
    return out


def _probe_case_report(passages_by_id: Dict[str, dict], streams_by_id: Dict[str, List[dict]],
                       preds_by_id: Dict[str, Dict[str, List[int]]]) -> dict:
    """DIRECT measurement on the probe's 17 flagged-wrong cases (B2 subset tagged): for each arm,
    how many the arm now resolves clean-label-correct (strict_cb was wrong on all 17 by
    construction), and how many it breaks elsewhere is captured separately by _corrected_broken."""
    if not os.path.exists(PROBE_CASES_PATH):
        return {"note": "probe cases file absent; direct B2 measurement skipped"}
    cases = json.load(open(PROBE_CASES_PATH, encoding="utf-8"))
    per_arm = {a: {"resolved_all": 0, "resolved_b2": 0} for a in
               ("strict_cb", "decay_window", "speaker_deixis", "combined")}
    n_b2 = 0
    details = []
    for idx, c in enumerate(cases):
        pid = c["passage_id"]
        pos = c["pos"]
        is_b2 = idx in B2_CASE_INDICES
        if is_b2:
            n_b2 += 1
        if pid not in streams_by_id:
            continue
        s = streams_by_id[pid]
        row = {"case": idx + 1, "passage_id": pid, "pron": c.get("pronoun"),
               "gold": c.get("gold_entity"), "b2": is_b2}
        for arm in per_arm:
            pred = preds_by_id[pid][arm]
            correct = not mention_link_wrong(pos, s, pred)
            row[arm] = correct
            if correct:
                per_arm[arm]["resolved_all"] += 1
                if is_b2:
                    per_arm[arm]["resolved_b2"] += 1
        details.append(row)
    return {"n_probe_cases": len(cases), "n_b2_cases": n_b2, "per_arm": per_arm, "details": details}


def _decay_sensitivity(passages: List[dict], streams: List[List[dict]]) -> dict:
    """Clean-label pronoun error counts for the decay_window arm across decay/window settings."""
    cb = [run_learnable_strict_cb(s) for s in streams]
    cb_err = sum(1 for s, p in zip(streams, cb) for pos, r in enumerate(s)
                 if r["is_pronoun"] and mention_link_wrong(pos, s, p))
    out = {"strict_cb_pron_errors": cb_err}
    for decay in (0.5, 0.7, 0.9):
        for window in (3, 4):
            dw = [run_loop_discourse(s, True, False, decay=decay, window=window)[0] for s in streams]
            err = sum(1 for s, p in zip(streams, dw) for pos, r in enumerate(s)
                      if r["is_pronoun"] and mention_link_wrong(pos, s, p))
            out[f"decay{decay}_win{window}_pron_errors"] = err
    return out


# ---------------------------------------------------------------------------
def self_test() -> None:
    # (A) DIALOGUE-TURN fixture: two alternating same-gender speakers; an in-quote 3rd-person pronoun
    # that refers to the ABSENT third party. strict_cb (most-recent agent) picks the addressee
    # (wrong); speaker-deixis excludes speaker+addressee -> forces the absent third party (right).
    dlg = {
        "passage_id": "dlg1",
        "clauses": [
            "Farmer Robertson broke the cane.",
            '"Who did it," asked Stephen.',
            '"He broke my cane," replied Philip.',
        ],
        "entities": {
            "Robertson": [{"clause": 0, "mention": "Farmer Robertson", "role": "agent"},
                          {"clause": 2, "mention": "He", "role": "agent"}],
            "Stephen": [{"clause": 1, "mention": "Stephen", "role": "agent"}],
            "Philip": [{"clause": 2, "mention": "Philip", "role": "agent"}],
        },
    }
    s = enrich_dialogue(dlg, build_mention_stream_with_role(dlg))
    he_idx = [i for i, r in enumerate(s) if r["mention_text"] == "He"][0]
    assert s[he_idx]["in_quote"], f"'He' must be detected inside a quote: {s[he_idx]}"
    assert s[he_idx]["clause_speaker"] == "Philip", s[he_idx]
    assert s[he_idx]["clause_addressee"] == "Stephen", s[he_idx]  # alternating: prev diff speaker
    robertson_idxs = [i for i, r in enumerate(s) if r["gold_entity"] == "Robertson"]
    stephen_idxs = [i for i, r in enumerate(s) if r["gold_entity"] == "Stephen"]
    cb = run_learnable_strict_cb(s)
    sd, acts = run_loop_discourse(s, use_decay=False, use_deixis=True)
    assert cb[he_idx] in {cb[i] for i in stephen_idxs}, (
        f"precondition: strict_cb must mispick the addressee Stephen for in-quote 'He'; cb={cb}")
    assert sd[he_idx] in {sd[i] for i in robertson_idxs}, (
        f"speaker-deixis must exclude speaker+addressee and force Robertson; sd={sd}")
    assert acts.get("deixis_fired", 0) >= 1, f"deixis must have fired: {acts}"
    assert cb != sd, "arms must differ on the dialogue fixture"

    # deixis must NOT fire on an OUT-OF-QUOTE pronoun (narration frame): "said Joab, and he took the
    # darts" -- 'he' outside the quote refers to the speaker; excluding the speaker would break it.
    narr = {
        "passage_id": "narr1",
        "clauses": ["Amasa stood there.", 'Then said Joab, and he took the darts.'],
        "entities": {
            "Amasa": [{"clause": 0, "mention": "Amasa", "role": "agent"}],
            "Joab": [{"clause": 1, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "he", "role": "agent"}],
        },
    }
    sn = enrich_dialogue(narr, build_mention_stream_with_role(narr))
    he2 = [i for i, r in enumerate(sn) if r["mention_text"] == "he"][0]
    assert not sn[he2]["in_quote"], "narration 'he' must NOT be flagged in-quote"
    cbn = run_learnable_strict_cb(sn)
    sdn, actsn = run_loop_discourse(sn, use_decay=False, use_deixis=True)
    assert sdn == cbn, f"deixis must not change out-of-quote decisions: cb={cbn} sd={sdn}"

    # (B) DECAY-WINDOW fixture: correct antecedent 2 clauses back (the ongoing topic), NOT the
    # most-recent 1-back agent. strict_cb picks the 1-back agent (wrong); decay-window recovers the
    # 2-back topic (right).
    dw_fix = {
        "passage_id": "dw1",
        "clauses": ["Robert played all day.", "Robert ran fast.", "Willie appeared.",
                    "He was tired."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"},
                       {"clause": 1, "mention": "Robert", "role": "agent"},
                       {"clause": 3, "mention": "He", "role": "agent"}],
            "Willie": [{"clause": 2, "mention": "Willie", "role": "agent"}],
        },
    }
    sd2 = enrich_dialogue(dw_fix, build_mention_stream_with_role(dw_fix))
    he3 = [i for i, r in enumerate(sd2) if r["mention_text"] == "He"][0]
    rob = [i for i, r in enumerate(sd2) if r["gold_entity"] == "Robert"]
    wil = [i for i, r in enumerate(sd2) if r["gold_entity"] == "Willie"]
    cb2 = run_learnable_strict_cb(sd2)
    dw2, _ = run_loop_discourse(sd2, use_decay=True, use_deixis=False)
    assert cb2[he3] in {cb2[i] for i in wil}, f"precondition: strict_cb picks 1-back Willie; cb={cb2}"
    assert dw2[he3] in {dw2[i] for i in rob}, f"decay-window must recover 2-back Robert; dw={dw2}"

    # real code path on the actual powered gold.
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    passages = load_passages(GOLD_PATH_COMBINED)
    assert len(passages) == 36, f"expected 36 combined passages, got {len(passages)}"
    p0 = passages[0]
    s0 = enrich_dialogue(p0, build_mention_stream_with_role(p0))
    cm0, _ = run_loop_discourse(s0, True, True)
    ev, ns, c2s = event_slots_for(s0)
    gen = torch.Generator().manual_seed(SEED)
    res = run_arm_on_passage(p0, s0, [str(c) for c in cm0], ev, c2s, ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
    assert "q_correct_iddem" in res

    print("[SELF-TEST] PASS: speaker-deixis fixes an in-quote 3rd-person pronoun by excluding "
          "speaker+addressee (Philip/Stephen->Robertson) and ABSTAINS on out-of-quote narration; "
          "decay-window recovers a 2-clause-back topic strict_cb misses; real query-metric path "
          "exercised on the powered gold")


# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _eval_block(passages: List[dict]) -> Tuple[dict, List[List[dict]], Dict[str, List[List[int]]]]:
    streams = [enrich_dialogue(p, build_mention_stream_with_role(p)) for p in passages]
    preds = _arm_preds(passages, streams)
    rec_preds = [run_recency_floor(s) for s in streams]

    action_totals: Dict[str, int] = {}
    for s in streams:
        _, acts = run_loop_discourse(s, True, True)
        for k, v in acts.items():
            action_totals[k] = action_totals.get(k, 0) + v

    b3 = _b3(streams, {**preds, "recency_floor": rec_preds})
    cluster_ids_by_arm = {
        "oracle": [[r["gold_entity"] for r in s] for s in streams],
        "strict_cb": [[str(c) for c in p] for p in preds["strict_cb"]],
        "decay_window": [[str(c) for c in p] for p in preds["decay_window"]],
        "speaker_deixis": [[str(c) for c in p] for p in preds["speaker_deixis"]],
        "combined": [[str(c) for c in p] for p in preds["combined"]],
        "recency_floor": [[str(c) for c in p] for p in rec_preds],
        "singleton_floor": [[str(c) for c in run_singleton_floor(s)] for s in streams],
    }
    query = _query_metrics(passages, streams, cluster_ids_by_arm)
    block = {
        "n_passages": len(passages),
        "n_pronoun_mentions": sum(1 for s in streams for r in s if r["is_pronoun"]),
        "combined_action_counts": action_totals,
        "b3": b3, "query_metric": query,
    }
    return block, streams, preds


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    passages = load_passages(GOLD_PATH_COMBINED)
    g5g6 = load_passages(GOLD_PATH_G5G6)

    combined_block, streams, preds = _eval_block(passages)
    g5g6_block, _, _ = _eval_block(g5g6)

    corr_broken = _corrected_broken(passages, streams, preds)
    passages_by_id = {p["passage_id"]: p for p in passages}
    streams_by_id = {p["passage_id"]: s for p, s in zip(passages, streams)}
    preds_by_id = {p["passage_id"]: {a: preds[a][i] for a in preds}
                   for i, p in enumerate(passages)}
    probe_report = _probe_case_report(passages_by_id, streams_by_id, preds_by_id)
    decay_sens = _decay_sensitivity(passages, streams)

    b = combined_block["b3"]
    q = combined_block["query_metric"]
    cb_pron = b["strict_cb"]["pronoun_only"]["f1"]
    cb_name = b["strict_cb"]["name_only"]["f1"]
    cb_overall = b["strict_cb"]["overall"]["f1"]
    cb_id = q["strict_cb"]["query_accuracy_identity_demanding"]
    oracle_id = q["oracle"]["query_accuracy_identity_demanding"]

    def arm_summary(arm: str) -> dict:
        return {
            "pron_b3": b[arm]["pronoun_only"]["f1"],
            "name_b3": b[arm]["name_only"]["f1"],
            "overall_b3": b[arm]["overall"]["f1"],
            "iddem_query": q[arm]["query_accuracy_identity_demanding"],
            "pron_lift": b[arm]["pronoun_only"]["f1"] - cb_pron,
            "iddem_lift": (q[arm]["query_accuracy_identity_demanding"] - cb_id)
            if (q[arm]["query_accuracy_identity_demanding"] is not None and cb_id is not None) else None,
            "name_regr": cb_name - b[arm]["name_only"]["f1"],
            "overall_regr": cb_overall - b[arm]["overall"]["f1"],
        }

    arm_sum = {a: arm_summary(a) for a in ("decay_window", "speaker_deixis", "combined")}

    cm = arm_sum["combined"]
    lifts_pron = cm["pron_lift"] >= PRONOUN_B3_MARGIN
    lifts_iddem = (cm["iddem_lift"] is not None and cm["iddem_lift"] >= IDDEM_QUERY_MARGIN)
    no_regression = (cm["name_regr"] <= REGRESSION_TOL) and (cm["overall_regr"] <= REGRESSION_TOL)
    net_pos = corr_broken["combined"]["net"] > 0

    if lifts_pron and lifts_iddem and no_regression and net_pos:
        verdict = "HARD_PASS"
    elif not no_regression:
        verdict = "REGRESSION"
    elif (lifts_pron or net_pos) and no_regression and not lifts_iddem:
        verdict = "PARTIAL_COREF_ONLY"
    elif lifts_iddem and no_regression and not (lifts_pron or net_pos):
        verdict = "PARTIAL_QUERY_ONLY"
    else:
        verdict = "NULL"

    # which lever drives it
    driver = max(("decay_window", "speaker_deixis"),
                 key=lambda a: (corr_broken[a]["net"], arm_sum[a]["pron_lift"]))

    verdict_msg = (
        f"[{verdict}] cross-clause discourse (combined) vs strict_cb (powered): pron-B3 {cb_pron:.4f}"
        f"->{cm['pron_b3']:.4f} (lift={cm['pron_lift']:+.4f}); iddem-query {cb_id}->{cm['iddem_query']} "
        f"(lift={cm['iddem_lift']}; oracle={oracle_id}); name regr={cm['name_regr']:+.4f}, overall "
        f"regr={cm['overall_regr']:+.4f}. Ablation net corrected-broken: "
        f"decay_window={corr_broken['decay_window']['net']} "
        f"(corr={corr_broken['decay_window']['corrected']}/broke={corr_broken['decay_window']['broken']}), "
        f"speaker_deixis={corr_broken['speaker_deixis']['net']} "
        f"(corr={corr_broken['speaker_deixis']['corrected']}/broke={corr_broken['speaker_deixis']['broken']}), "
        f"combined={corr_broken['combined']['net']}. Driver={driver}. "
        f"Probe B2 cases resolved (of {probe_report.get('n_b2_cases')}): "
        f"strict_cb={probe_report['per_arm']['strict_cb']['resolved_b2'] if 'per_arm' in probe_report else 'NA'}, "
        f"combined={probe_report['per_arm']['combined']['resolved_b2'] if 'per_arm' in probe_report else 'NA'}. "
        f"deixis actions: fired={combined_block['combined_action_counts'].get('deixis_fired',0)}."
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "levers": {
            "decay_window": {"decay": DECAY, "window": WINDOW, "audit_ref": "A2 / B1 lever 1"},
            "speaker_deixis": {"speaker_window": SPEAKER_WINDOW,
                               "audit_ref": "B1 dialogue Centering (Walker-Joshi-Prince)"},
            "definite_description_bridging": "DEFERRED this cycle (see docstring)",
        },
        "bands": {"pronoun_b3_margin": PRONOUN_B3_MARGIN, "iddem_query_margin": IDDEM_QUERY_MARGIN,
                  "regression_tol": REGRESSION_TOL},
        "headline_combined": {
            "strict_cb": {"pron_b3": cb_pron, "name_b3": cb_name, "overall_b3": cb_overall,
                          "iddem_query": cb_id},
            "oracle_iddem_query": oracle_id,
            "arms": arm_sum,
            "corrected_broken_all_pronouns": corr_broken,
        },
        "combined_powered": combined_block,
        "g5g6_only": g5g6_block,
        "probe_b2_direct": probe_report,
        "decay_sensitivity_combined": decay_sens,
        "driver_lever": driver,
        "gold_path_combined": GOLD_PATH_COMBINED,
        "gold_path_g5g6": GOLD_PATH_G5G6,
        "reproducibility_note": (
            "strict_cb (5b266248f) + helpers + query machinery (e6a3a9ee8) + clean label + "
            "principle_b cell all imported verbatim, NEVER mutated. run_loop_discourse / "
            "enrich_dialogue / _deixis_filter / _pick_decay_window are NEW opt-in functions here."
        ),
        "prior_commits": {
            "strict_cb_mechanism": "5b266248f",
            "loop_cycle1_topic_continuity_null": "82492af76",
            "loop_cycle2_principle_b_partial": "4cc041fcd",
            "brain_fidelity_audit": "bd0faab3c",
            "query_machinery_iddem_split": "e6a3a9ee8",
        },
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
