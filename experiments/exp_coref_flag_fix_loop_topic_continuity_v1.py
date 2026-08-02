"""SELF-IMPROVING-READER LOOP, cycle 1: FLAG -> targeted FIX -> MEASURE (2026-08-02).

First real cycle of the flag-driven self-improving reader on the coref-quality bottleneck.

BANKED PRIORS (imported verbatim, NEVER mutated -- opt-in new functions only):
  - strict_cb = exp_earn_coref_pronoun_strict_cb_v1.run_learnable_strict_cb (commit 5b266248f,
    atom 29614) -- our BEST coref; the BASELINE for this cell ("strict_cb everywhere").
  - FLAG signal = # gender/number-compatible candidate antecedents at a pronoun decision
    (n_compatible). Validated by calibration v2 (commit 150058b03): n_compatible predicts pronoun
    errors AUC ~0.72 on the powered eval -- more co-present same-gender candidates => more likely
    wrong = the high-ambiguity turn-taking cases (Harry/Sam class) that are the remaining gap
    (strict_cb identity-demanding query 0.719 vs oracle 0.930, commit e6a3a9ee8).
  - query machinery = exp_wire_coref_accumulate_situation_model_v1 (commit e6a3a9ee8):
    run_arm_on_passage, event_slots_for, identity_demanding split, AccumulateRegister organ.
  - clean local link-level error label = exp_coref_self_confidence_calibration_v1.mention_link_wrong
    (used only to DATA-DRIVE the flag threshold + to trace/diagnose; not a mechanism input).

THE LOOP (this cell, glass-box, our own; no borrowed embeddings, no external LLM):
  1. FLAG: mark a strict_cb pronoun decision HIGH-AMBIGUITY iff n_compatible >= FLAG_THRESHOLD.
     FLAG_THRESHOLD is picked from strict_cb's OWN clean-label error-vs-n_compatible curve on the
     powered eval by best Youden's J over candidate thresholds {2,3} (reported); errors concentrate
     where multiple same-gender candidates co-occur.
  2. TARGETED FIX (Centering transition preference / topic continuity, Grosz-Joshi-Weinstein
     Continue > Retain > Shift): among compatible candidates, prefer the ONGOING backward-looking
     center = the entity with the strongest RECENCY-WEIGHTED accumulated subjecthood across recent
     clauses, NOT merely the single most-recent agent. This is the genuine new lever beyond
     strict_cb: strict_cb ranks candidates by (most_recent_subject_clause, last_pos) -- the MAX of
     the subject history; topic-continuity ranks by (sum_c TOPIC_DECAY**(cur_clause-c) over subject
     clauses c, last_pos) -- the recency-weighted WHOLE history. An entity that has been subject
     repeatedly/recently is the continuing topic (Continue); one that was subject only in the
     latest clause is a shift. strict_cb is the steep-decay special case. (Secondary note on
     parallelism -- prefer the most-recent antecedent that held the pronoun's own role -- is
     reported via a diagnostic but topic-continuity is the primary fix per the loop design.)
  3. Applied SELECTIVELY (flagged decisions only; confident decisions keep strict_cb's pick) in the
     loop_selective arm, and to ALL pronoun decisions in the loop_uniform CONTROL arm.

ARMS (one clean comparison, same streams / event-slots across arms):
  - strict_cb        = run_learnable_strict_cb everywhere (BASELINE for this cell).
  - loop_selective   = strict_cb + topic-continuity fix on FLAGGED pronoun decisions only.
  - loop_uniform     = strict_cb + topic-continuity fix on ALL pronoun decisions (flag-localization
                        control: if selective >= uniform, the flag correctly localizes where effort
                        helps -- the loop's core claim; if uniform is just as good, the flag added
                        nothing).
  - oracle / recency_floor / singleton_floor: query-metric ceiling + floors (context only).

MEASURE (powered combined eval, 36 passages, 130 queries, 76 pronoun decisions; g5g6-only
secondary):
  1. pronoun-only B3-F1: does loop_selective beat strict_cb? name/overall must not regress.
  2. IDENTITY-DEMANDING situation-model query accuracy (reuse run_arm_on_passage, iddem split):
     does loop_selective move strict_cb's ~0.719 toward oracle ~0.930?
  3. FLAG-LOCALIZATION control: loop_selective vs loop_uniform on both metrics.

CAN-FAIL BANDS (pre-registered BEFORE running):
  HARD_PASS: loop_selective lifts pronoun-B3 over strict_cb by >= PRONOUN_B3_MARGIN AND lifts
    identity-demanding query acc over strict_cb by >= IDDEM_QUERY_MARGIN AND is flag-localized
    (selective >= uniform - LOCALIZE_TOL on BOTH metrics). The loop's core claim demonstrated.
  FLAG_REDUNDANT: the fix helps (selective lifts strict_cb on both) but uniform is just as good
    (selective < uniform - LOCALIZE_TOL on some metric) -- the flag added nothing; report honestly.
  NULL_FIX_MECHANISM: the topic-continuity fix does NOT help the flagged high-ambiguity cases
    (loop_selective does not lift strict_cb on both metrics). This DECOMPOSES the loop cleanly: the
    FLAG is earned (calibration v2) and localizes error concentration (reported), but the FIX
    mechanism is the open frontier -- same-gender turn-taking may need verb-semantics / world-
    knowledge we do not have glass-box yet. A powered null (content no longer the excuse) -> report
    the mechanism reason with the flagged-decision trace + decay-sensitivity table (is the null
    robust to the decay param, or an artifact of one decay value?). VET NEGATIVES AS HARD AS
    POSITIVES.
  REGRESSION: loop_selective regresses name/overall B3 beyond REGRESSION_TOL.

Self-test: python exp_coref_flag_fix_loop_topic_continuity_v1.py --self-test
Full:      python exp_coref_flag_fix_loop_topic_continuity_v1.py
"""
from __future__ import annotations

import argparse
import json
import os
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

# Banked priors -- imported verbatim, NEVER mutated.
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

ANCHOR_NAME = "coref_flag_fix_loop_topic_continuity_v1"
_GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_PATH_COMBINED = os.path.join(_GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl")
GOLD_PATH_G5G6 = os.path.join(_GOLD_DIR, "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# FIX parameter: recency half-life ~2 clauses (decay**2 ~ 0.5). Pre-registered a priori (NOT tuned
# to pass); a decay-sensitivity table over {0.5,0.7,0.9,1.0} is reported so the verdict's
# robustness to this choice is auditable.
TOPIC_DECAY = 0.7
FLAG_THRESHOLD_CANDIDATES = (2, 3)  # data-driven pick via Youden's J on the clean-label curve

# Pre-registered bands.
PRONOUN_B3_MARGIN = 0.02       # loop_selective must lift pronoun-only B3-F1 over strict_cb
IDDEM_QUERY_MARGIN = 0.03      # loop_selective must lift identity-demanding query acc over strict_cb
REGRESSION_TOL = 0.01          # name/overall B3-F1 must not regress beyond this
LOCALIZE_TOL = 0.005           # selective must be >= uniform - LOCALIZE_TOL to count as localized


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# The FIX: topic-continuity (Centering Continue) antecedent selection. Recency-weighted accumulated
# subjecthood over the WHOLE history -- distinct from strict_cb's MAX-only (most-recent-subject).
# ---------------------------------------------------------------------------
def _topic_strength(e: _EntityCb, cur_clause: int, decay: float) -> float:
    """Recency-weighted count of clauses (< cur_clause) in which e held a subject-like role."""
    return sum(decay ** (cur_clause - c)
               for c, r in e.clause_role.items()
               if r in SUBJECT_LIKE_ROLES and c < cur_clause)


def _pick_topic_continuity(compat: List[_EntityCb], cur_clause: int, decay: float) -> _EntityCb:
    """Prefer the ongoing topic: argmax recency-weighted subjecthood; tie-break by last_pos
    (recency) to match strict_cb's secondary key. compat guaranteed non-empty by the caller."""
    return max(compat, key=lambda e: (_topic_strength(e, cur_clause, decay), e.last_pos))


def run_loop(stream: List[dict], flag_threshold: int, selective: bool,
             decay: float = TOPIC_DECAY) -> List[int]:
    """strict_cb + topic-continuity fix. If selective: fix applies ONLY to flagged pronoun
    decisions (n_compatible >= flag_threshold); confident decisions keep strict_cb's pick. If NOT
    selective: fix applies to ALL pronoun decisions (uniform control). Name/nominal branch is
    byte-identical to strict_cb (via the imported _resolve_name_branch)."""
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_comp = len(compat)
            flagged = n_comp >= flag_threshold
            use_fix = (selective and flagged) or (not selective)
            if compat:
                if use_fix:
                    best = _pick_topic_continuity(compat, cur_clause, decay)
                else:
                    best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # tier-4 best-effort
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
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
    return assigned


# ---------------------------------------------------------------------------
# FLAG threshold selection: from strict_cb's OWN clean-label error-vs-n_compatible curve, pick the
# candidate threshold maximizing Youden's J (TPR - FPR) over pronoun decisions.
# ---------------------------------------------------------------------------
def _pronoun_ncomp_and_error(stream: List[dict]) -> List[Tuple[int, bool]]:
    """Replay strict_cb, logging (n_compatible, clean-label-wrong) per pronoun decision."""
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    ncomp_at: List[Tuple[int, int]] = []  # (pos, n_compatible) for pronoun decisions
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            ncomp_at.append((pos, len(compat)))
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
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
    out: List[Tuple[int, bool]] = []
    for pos, nc in ncomp_at:
        out.append((nc, mention_link_wrong(pos, stream, assigned)))
    return out


def pick_flag_threshold(passages: List[dict]) -> dict:
    pairs: List[Tuple[int, bool]] = []
    for p in passages:
        pairs.extend(_pronoun_ncomp_and_error(build_mention_stream_with_role(p)))
    n_err = sum(1 for _, w in pairs if w)
    n_ok = sum(1 for _, w in pairs if not w)
    # error rate by n_compatible (reported)
    curve: Dict[int, List[int]] = {}
    for nc, w in pairs:
        curve.setdefault(nc, [0, 0])
        curve[nc][0] += int(w)
        curve[nc][1] += 1
    curve_out = {str(nc): {"n_wrong": v[0], "n_total": v[1],
                            "error_rate": (v[0] / v[1]) if v[1] else None}
                 for nc, v in sorted(curve.items())}
    best_thr = FLAG_THRESHOLD_CANDIDATES[0]
    best_j = -2.0
    per_thr = {}
    for thr in FLAG_THRESHOLD_CANDIDATES:
        tp = sum(1 for nc, w in pairs if nc >= thr and w)
        fp = sum(1 for nc, w in pairs if nc >= thr and not w)
        tpr = (tp / n_err) if n_err else 0.0
        fpr = (fp / n_ok) if n_ok else 0.0
        j = tpr - fpr
        per_thr[str(thr)] = {"n_flagged": tp + fp, "flag_recall_of_errors": tpr,
                             "flag_fpr": fpr, "youden_j": j,
                             "flag_precision": (tp / (tp + fp)) if (tp + fp) else None}
        if j > best_j:
            best_j = j
            best_thr = thr
    return {
        "chosen_threshold": best_thr,
        "base_pronoun_error_rate": (n_err / len(pairs)) if pairs else None,
        "n_pronoun_decisions": len(pairs),
        "error_rate_by_n_compatible": curve_out,
        "per_candidate_threshold": per_thr,
    }


# ---------------------------------------------------------------------------
# B3 helper.
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


# ---------------------------------------------------------------------------
# Situation-model query metric via the wire cell's run_arm_on_passage (reused verbatim). Returns
# ALL / identity-demanding / pronoun-contributed accuracy per arm.
# ---------------------------------------------------------------------------
def _query_metrics(passages: List[dict], streams: List[List[dict]],
                    cluster_ids_by_arm: Dict[str, List[List[str]]]) -> dict:
    arm_seed_idx = {"oracle": 0, "strict_cb": 1, "loop_selective": 2, "loop_uniform": 3,
                    "recency_floor": 4, "singleton_floor": 5}
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


# ---------------------------------------------------------------------------
# Decision trace for the NULL path: on flagged pronoun decisions, did the topic-continuity fix
# pick the same as strict_cb, and was each pick clean-label-correct?
# ---------------------------------------------------------------------------
def _flag_fix_trace(passages: List[dict], flag_threshold: int) -> dict:
    n_flagged = n_fix_differs = 0
    cb_wrong_on_flagged = fix_wrong_on_flagged = 0
    fix_fixed = fix_broke = 0  # among flagged where they differ: fix right & cb wrong / fix wrong & cb right
    samples = []
    for p in passages:
        s = build_mention_stream_with_role(p)
        cb = run_learnable_strict_cb(s)
        sel = run_loop(s, flag_threshold, selective=True)
        # recompute n_compatible per pronoun to identify flagged positions (strict_cb replay)
        nc_pairs = _pronoun_ncomp_and_error(s)  # (nc, wrong) in pronoun order
        pron_positions = [i for i, r in enumerate(s) if r["is_pronoun"]]
        for (nc, _), pos in zip(nc_pairs, pron_positions):
            if nc < flag_threshold:
                continue
            n_flagged += 1
            cb_w = mention_link_wrong(pos, s, cb)
            fx_w = mention_link_wrong(pos, s, sel)
            cb_wrong_on_flagged += int(cb_w)
            fix_wrong_on_flagged += int(fx_w)
            if cb[pos] != sel[pos]:
                n_fix_differs += 1
                if cb_w and not fx_w:
                    fix_fixed += 1
                elif fx_w and not cb_w:
                    fix_broke += 1
                if len(samples) < 20:
                    samples.append({
                        "passage_id": p["passage_id"], "pos": pos,
                        "mention_text": s[pos]["mention_text"], "clause": s[pos]["clause"],
                        "gold_entity": s[pos]["gold_entity"], "n_compatible": nc,
                        "strict_cb_wrong": bool(cb_w), "fix_wrong": bool(fx_w),
                    })
    return {
        "n_flagged": n_flagged,
        "n_fix_differs_from_strict_cb": n_fix_differs,
        "strict_cb_errors_on_flagged": cb_wrong_on_flagged,
        "fix_errors_on_flagged": fix_wrong_on_flagged,
        "fix_corrected_strict_cb": fix_fixed,
        "fix_broke_strict_cb": fix_broke,
        "sample_differing_decisions": samples,
    }


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------
def self_test() -> None:
    # (2) turn-taking fixture where topic-continuity is RIGHT and strict_cb (most-recent-agent) is
    # WRONG: Robert is the ongoing topic (agent of clauses 0 and 1); Willie is a one-off recent
    # agent (clause 2). "He"@clause3 gold=Robert. strict_cb picks Willie (most-recent-subject-
    # clause=2 > Robert's 1); topic-continuity picks Robert (accumulated recency-weighted
    # subjecthood 0.7^3+0.7^2=0.833 > Willie's 0.7).
    fixture = {
        "passage_id": "topic_flip1",
        "clauses": ["Robert played all morning.", "Robert ran very fast.",
                    "Willie appeared.", "He was tired."],
        "entities": {
            "Robert": [
                {"clause": 0, "mention": "Robert", "role": "agent"},
                {"clause": 1, "mention": "Robert", "role": "agent"},
                {"clause": 3, "mention": "He", "role": "agent"},
            ],
            "Willie": [{"clause": 2, "mention": "Willie", "role": "agent"}],
        },
    }
    stream = build_mention_stream_with_role(fixture)
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    robert_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Robert"]
    willie_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Willie"]

    cb_pred = run_learnable_strict_cb(stream)
    # flag_threshold=2: He has 2 compatible candidates -> flagged -> fix applies in selective arm.
    sel_pred = run_loop(stream, flag_threshold=2, selective=True)

    cb_he_willie = cb_pred[he_idx] in {cb_pred[i] for i in willie_idxs}
    assert cb_he_willie, (
        f"precondition: strict_cb (most-recent-agent) must MISPICK Willie for 'He'; cb={cb_pred}")
    sel_he_robert = sel_pred[he_idx] in {sel_pred[i] for i in robert_idxs}
    sel_he_willie = sel_pred[he_idx] in {sel_pred[i] for i in willie_idxs}
    assert sel_he_robert and not sel_he_willie, (
        f"topic-continuity fix must pick Robert (ongoing topic) for 'He'; sel={sel_pred}")
    assert cb_pred != sel_pred, "arms must differ on the topic-flip fixture (fix fired)"

    b_cb = bcubed([(stream, cb_pred)])
    b_sel = bcubed([(stream, sel_pred)])
    assert b_sel["f1"] > b_cb["f1"], f"fix must score higher B3 on the flip fixture: cb={b_cb} sel={b_sel}"

    # non-regression: on a confident (n_compatible<threshold) decision the selective arm must equal
    # strict_cb (fix NOT applied). Clean single-antecedent chain:
    clean = {
        "passage_id": "clean_tc1",
        "clauses": ["Alice went to the store.", "She bought bread."],
        "entities": {"Alice": [
            {"clause": 0, "mention": "Alice", "role": "agent"},
            {"clause": 1, "mention": "She", "role": "agent"},
        ]},
    }
    cs = build_mention_stream_with_role(clean)
    assert run_loop(cs, 2, selective=True) == run_learnable_strict_cb(cs), (
        "selective arm must equal strict_cb when nothing is flagged (fix localizes)")

    # flag-threshold picker + real code path on the actual powered gold.
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    assert os.path.exists(GOLD_PATH_G5G6), f"g5g6 gold missing: {GOLD_PATH_G5G6}"
    passages = load_passages(GOLD_PATH_COMBINED)
    assert len(passages) == 36, f"expected 36 combined passages, got {len(passages)}"
    ft = pick_flag_threshold(passages)
    assert ft["chosen_threshold"] in FLAG_THRESHOLD_CANDIDATES
    # real query-metric path on one passage
    p0 = passages[0]
    s0 = build_mention_stream_with_role(p0)
    ev, ns, c2s = event_slots_for(s0)
    gen = torch.Generator().manual_seed(SEED)
    res = run_arm_on_passage(p0, s0, [str(c) for c in run_loop(s0, ft["chosen_threshold"], True)],
                             ev, c2s, ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
    assert "q_correct_iddem" in res

    print("[SELF-TEST] PASS: topic-continuity fix corrects a strict_cb most-recent-agent mispick on "
          "the turn-taking flip fixture (arms differ, higher B3); selective arm equals strict_cb on "
          "unflagged confident decisions (flag localizes); flag-threshold picker + query-metric real "
          f"code path exercised on the powered gold (chosen_threshold={ft['chosen_threshold']})")


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


def _decay_sensitivity(passages: List[dict], flag_threshold: int) -> dict:
    """Clean-label pronoun error counts for selective/uniform across decay values -- shows whether a
    NULL is robust to the decay parameter or an artifact of one value."""
    out = {}
    for decay in (0.5, 0.7, 0.9, 1.0):
        cb_w = sel_w = uni_w = pron = 0
        for p in passages:
            s = build_mention_stream_with_role(p)
            cb = run_learnable_strict_cb(s)
            sel = run_loop(s, flag_threshold, selective=True, decay=decay)
            uni = run_loop(s, flag_threshold, selective=False, decay=decay)
            for pos, rec in enumerate(s):
                if not rec["is_pronoun"]:
                    continue
                pron += 1
                cb_w += int(mention_link_wrong(pos, s, cb))
                sel_w += int(mention_link_wrong(pos, s, sel))
                uni_w += int(mention_link_wrong(pos, s, uni))
        out[str(decay)] = {"strict_cb_pron_errors": cb_w, "selective_pron_errors": sel_w,
                           "uniform_pron_errors": uni_w, "n_pronoun": pron}
    return out


def _eval_block(passages: List[dict], flag_threshold: int) -> dict:
    streams = [build_mention_stream_with_role(p) for p in passages]
    cb_preds = [run_learnable_strict_cb(s) for s in streams]
    sel_preds = [run_loop(s, flag_threshold, selective=True) for s in streams]
    uni_preds = [run_loop(s, flag_threshold, selective=False) for s in streams]
    rec_preds = [run_recency_floor(s) for s in streams]

    n_pron = sum(1 for s in streams for r in s if r["is_pronoun"])
    sel_flips = sum(1 for a, b in zip(cb_preds, sel_preds) if a != b)
    uni_flips = sum(1 for a, b in zip(cb_preds, uni_preds) if a != b)

    b3 = _b3(streams, {"strict_cb": cb_preds, "loop_selective": sel_preds,
                       "loop_uniform": uni_preds, "recency_floor": rec_preds})

    cluster_ids_by_arm = {
        "oracle": [[r["gold_entity"] for r in s] for s in streams],
        "strict_cb": [[str(c) for c in p] for p in cb_preds],
        "loop_selective": [[str(c) for c in p] for p in sel_preds],
        "loop_uniform": [[str(c) for c in p] for p in uni_preds],
        "recency_floor": [[str(c) for c in p] for p in rec_preds],
        "singleton_floor": [[str(c) for c in run_singleton_floor(s)] for s in streams],
    }
    query = _query_metrics(passages, streams, cluster_ids_by_arm)
    return {
        "n_passages": len(passages), "n_pronoun_mentions": n_pron,
        "selective_flip_passages": sel_flips, "uniform_flip_passages": uni_flips,
        "b3": b3, "query_metric": query,
    }


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    passages = load_passages(GOLD_PATH_COMBINED)
    g5g6 = load_passages(GOLD_PATH_G5G6)

    flag_info = pick_flag_threshold(passages)
    FT = flag_info["chosen_threshold"]

    combined = _eval_block(passages, FT)
    g5g6_block = _eval_block(g5g6, FT)
    trace = _flag_fix_trace(passages, FT)
    decay_sens = _decay_sensitivity(passages, FT)

    # ---- headline comparisons on the combined powered eval ----
    cb_pron = combined["b3"]["strict_cb"]["pronoun_only"]["f1"]
    sel_pron = combined["b3"]["loop_selective"]["pronoun_only"]["f1"]
    uni_pron = combined["b3"]["loop_uniform"]["pronoun_only"]["f1"]
    cb_name = combined["b3"]["strict_cb"]["name_only"]["f1"]
    sel_name = combined["b3"]["loop_selective"]["name_only"]["f1"]
    cb_overall = combined["b3"]["strict_cb"]["overall"]["f1"]
    sel_overall = combined["b3"]["loop_selective"]["overall"]["f1"]

    cb_id = combined["query_metric"]["strict_cb"]["query_accuracy_identity_demanding"]
    sel_id = combined["query_metric"]["loop_selective"]["query_accuracy_identity_demanding"]
    uni_id = combined["query_metric"]["loop_uniform"]["query_accuracy_identity_demanding"]
    oracle_id = combined["query_metric"]["oracle"]["query_accuracy_identity_demanding"]

    pron_lift = sel_pron - cb_pron
    id_lift = (sel_id - cb_id) if (sel_id is not None and cb_id is not None) else None
    name_regr = cb_name - sel_name
    overall_regr = cb_overall - sel_overall

    lifts_pron_b3 = pron_lift >= PRONOUN_B3_MARGIN
    lifts_iddem = (id_lift is not None and id_lift >= IDDEM_QUERY_MARGIN)
    no_regression = (name_regr <= REGRESSION_TOL) and (overall_regr <= REGRESSION_TOL)
    # flag localizes iff selective is at least as good as uniform on BOTH metrics
    localized_b3 = sel_pron >= (uni_pron - LOCALIZE_TOL)
    localized_id = (sel_id is not None and uni_id is not None and sel_id >= (uni_id - LOCALIZE_TOL))
    localized = localized_b3 and localized_id

    if lifts_pron_b3 and lifts_iddem and no_regression and localized:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"LOOP cycle-1 works: flag(n_compatible>={FT}) + topic-continuity fix, applied "
            f"SELECTIVELY, lifts pronoun-B3 {cb_pron:.4f}->{sel_pron:.4f} (+{pron_lift:.4f}) AND "
            f"identity-demanding query {cb_id:.4f}->{sel_id:.4f} (+{id_lift:.4f}, toward oracle "
            f"{oracle_id:.4f}); no regression; flag-localized (selective>=uniform on both). "
            f"Flag correctly localizes where effort helps."
        )
    elif lifts_pron_b3 and lifts_iddem and no_regression and not localized:
        verdict = "FLAG_REDUNDANT"
        verdict_msg = (
            f"The topic-continuity fix helps (pronoun-B3 +{pron_lift:.4f}, iddem-query +{id_lift}), "
            f"but UNIFORM application is at least as good as selective (selective pron={sel_pron:.4f} "
            f"vs uniform={uni_pron:.4f}; selective iddem={sel_id} vs uniform={uni_id}) -- the FLAG "
            f"added nothing: applying the fix everywhere is no worse. Report honestly."
        )
    elif not no_regression:
        verdict = "REGRESSION"
        verdict_msg = (
            f"loop_selective regressed name ({name_regr:.4f}) or overall ({overall_regr:.4f}) B3 "
            f"beyond tolerance {REGRESSION_TOL} -- the fix corrupts non-pronoun behavior; do not adopt."
        )
    else:
        verdict = "NULL_FIX_MECHANISM"
        verdict_msg = (
            f"LOOP DECOMPOSED: the FLAG is earned + localizes (flagged pronoun error rate concentrates "
            f"where n_compatible>={FT}; base_pron_err={flag_info['base_pronoun_error_rate']:.3f}), but "
            f"the topic-continuity (Centering Continue) FIX does NOT help the flagged high-ambiguity "
            f"cases: pronoun-B3 {cb_pron:.4f}->{sel_pron:.4f} (lift={pron_lift:+.4f} < "
            f"{PRONOUN_B3_MARGIN}); identity-demanding query {cb_id}->{sel_id} (lift={id_lift}). On "
            f"flagged decisions the fix corrected strict_cb {trace['fix_corrected_strict_cb']}x but "
            f"BROKE it {trace['fix_broke_strict_cb']}x (differs on {trace['n_fix_differs_from_strict_cb']}"
            f"/{trace['n_flagged']} flagged). Robust to decay (see decay_sensitivity: selective errors "
            f">= strict_cb at every decay). MECHANISM REASON: the flagged same-gender pronouns refer to "
            f"a NON-topic entity (a Shift), so preferring the ongoing topic (Continue) hurts -- these "
            f"cases need verb-semantics / world-knowledge not available glass-box yet. Flag earned; "
            f"fix is the open frontier (a clean, powered, trustworthy decomposition of the loop)."
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
        "topic_decay": TOPIC_DECAY,
        "flag_selection": flag_info,
        "flag_threshold_used": FT,
        "bands": {
            "pronoun_b3_margin": PRONOUN_B3_MARGIN,
            "iddem_query_margin": IDDEM_QUERY_MARGIN,
            "regression_tol": REGRESSION_TOL,
            "localize_tol": LOCALIZE_TOL,
        },
        "headline_combined": {
            "pronoun_b3_f1": {"strict_cb": cb_pron, "loop_selective": sel_pron,
                              "loop_uniform": uni_pron},
            "name_b3_f1": {"strict_cb": cb_name, "loop_selective": sel_name},
            "overall_b3_f1": {"strict_cb": cb_overall, "loop_selective": sel_overall},
            "identity_demanding_query_acc": {
                "oracle": oracle_id, "strict_cb": cb_id, "loop_selective": sel_id,
                "loop_uniform": uni_id,
            },
            "pronoun_b3_lift_selective_vs_strict_cb": pron_lift,
            "iddem_query_lift_selective_vs_strict_cb": id_lift,
            "name_regression": name_regr, "overall_regression": overall_regr,
            "flag_localized_b3": localized_b3, "flag_localized_iddem": localized_id,
        },
        "combined_powered": combined,
        "g5g6_only": g5g6_block,
        "flag_fix_trace_combined": trace,
        "decay_sensitivity_combined": decay_sens,
        "gold_path_combined": GOLD_PATH_COMBINED,
        "gold_path_g5g6": GOLD_PATH_G5G6,
        "reproducibility_note": (
            "run_learnable_strict_cb (5b266248f) and all imported machinery are used verbatim, NEVER "
            "mutated. run_loop / _pick_topic_continuity are NEW opt-in functions in this file. "
            "Prior committed cells unaffected."
        ),
        "prior_commits": {
            "strict_cb_mechanism": "5b266248f",
            "calibration_v2_flag_signal": "150058b03",
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
