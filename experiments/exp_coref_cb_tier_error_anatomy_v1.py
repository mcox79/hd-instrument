"""ORGAN 4 / E3 PHASE 1: what ARE the 25 of 89 competitive errors the Cb tier makes?

PRE-REGISTRATION: preregs/2026-08-14_coref_cb_tier_error_anatomy_v1.md (committed 5f31c838f,
BEFORE any arm was run). Categories, precedence order, discriminators and bands are fixed there.

NO MECHANISM IS PROPOSED OR CHANGED HERE. This cell replays hdlab.coreference_resolver's
run_principle_b byte-identically and records, per competitive decision, whether a gold-coreferent
entity was in the pool the pick actually ranks over (RANKING failure) or was not (RETRIEVAL
failure), plus the Cb-tier outcome and a fixed set of descriptors. Every number is an exact count
over a finite decision set; nothing is hand-scored and there is no tuning surface.

REUSE: registry, name branch, Principle-B filter, Cb pick, gn_compatible, mention_link_wrong and
build_mention_stream all imported from hdlab UNCHANGED; the competitive subset and the scoring
harness imported from the v1 ACT-R cell UNCHANGED, so the 89 decisions are the same 89.

CELL-TEMPLATE MANDATORY: no bare/BaseException except; SystemExit re-raised first; atomic
tmp+os.replace; start marker; crash diagnostic; sorted(set()) ordering; no RNG anywhere.

ASCII-only. Pure symbolic; numpy only for descriptive tallies.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.coreference_resolver import (  # noqa: E402
    SUBJECT_LIKE_ROLES,
    TrackedEntity,
    _mention_geometry,
    _observe_nominal,
    _observe_pronoun,
    _principle_b_filter,
    _resolve_name_branch,
    gn_compatible,
    mention_link_wrong,
    run_principle_b,
    run_strict_cb,
)
from experiments.exp_coref_cue_based_retrieval_actr_activation_v1 import (  # noqa: E402
    DATASETS,
    competitive_mask,
    load_passages,
    streams_for,
)

ANCHOR = "coref_cb_tier_error_anatomy_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
SMOKE_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR + "_smoke")

PREREG = "preregs/2026-08-14_coref_cb_tier_error_anatomy_v1.md"
PREREG_COMMIT = "5f31c838f"

# Cited, not re-measured here. MEASURED@data/exp_coref_actr_tiebreak_under_centering_v2/metrics.json
CITED_BASE_P = 0.7191011235955056
CITED_FLOOR_MOST_RECENT = 0.5280898876404494
CITED_FLOOR_SINGLETON = 0.0
EXPECTED_N_COMPETITIVE = 89
EXPECTED_N_ERRORS = 25

BANDS = {
    "ranking_headroom_licensing_delta": 0.05,   # P_ceiling_ranking - 0.7191 must clear this
    "top_cause_share_pinned_min": 0.32,         # < this -> DIFFUSE_UNPINNED
    "min_fixable_decisions_for_phase2": 5,      # < this -> underpowered on this corpus
}

CAUSES = (
    "RETRIEVAL_pb_filter_removed_gold",
    "RETRIEVAL_agreement_filter_removed_gold",
    "RETRIEVAL_no_gold_entity_in_registry",
    "RANKING_cb_unique_wrong",
    "RANKING_cb_tied_wrong",
    "RANKING_cb_none_wrong",
)
RETRIEVAL_CAUSES = tuple(c for c in CAUSES if c.startswith("RETRIEVAL_"))


# ---------------------------------------------------------------------------
# Cb-tier outcome, read off the SAME computation _pick_strict_cb performs.
# ---------------------------------------------------------------------------
def _cb_outcome(pool: List[TrackedEntity], cur_clause: int) -> Tuple[str, TrackedEntity]:
    """Returns (cb_unique | cb_tied | cb_none, pick). Pick is byte-identical to _pick_strict_cb."""
    scored = [(e, e.most_recent_subject_clause(cur_clause)) for e in pool]
    with_subject = [(e, c) for e, c in scored if c is not None]
    if with_subject:
        best_c = max(c for _, c in with_subject)
        tied = [e for e, c in with_subject if c == best_c]
        pick = max(tied, key=lambda e: e.last_pos)
        return ("cb_tied" if len(tied) >= 2 else "cb_unique"), pick
    return "cb_none", max(pool, key=lambda e: e.last_pos)


def _gold_correct_ids(assigned_positions: Dict[int, List[int]], stream: List[dict],
                      gold_i: str) -> set:
    """Entity ids whose MOST RECENT prior mention is gold-coreferent with the current mention.

    This is exactly the antecedent mention_link_wrong accepts, so 'a gold-correct entity was in the
    pool' and 'choosing it scores correct' are the same statement by construction."""
    out = set()
    for eid, poss in assigned_positions.items():
        if poss and stream[max(poss)]["gold_entity"] == gold_i:
            out.add(eid)
    return out


def analyse_passage(stream: List[dict], mask: List[bool], preds: List[int],
                    passage_id: str, dataset: str) -> List[dict]:
    """Replay run_principle_b, emitting one record per COMPETITIVE decision.

    The replay must reproduce `preds` exactly; the caller asserts it (REPLAY_DRIFT guard)."""
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    assigned_positions: Dict[int, List[int]] = {}
    records: List[dict] = []

    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                pool, pb_action = _principle_b_filter(compat, cur_clause, cur_role)
                cb_state, best = _cb_outcome(pool, cur_clause)
                if mask[pos]:
                    records.append(_make_record(
                        stream, pos, rec, entities, compat, pool, best, cb_state, pb_action,
                        assigned_positions, cur_clause, passage_id, dataset, preds))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            assigned_positions.setdefault(best.eid, []).append(pos)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
        assigned_positions.setdefault(best.eid, []).append(pos)

    if assigned != preds:
        raise ValueError("REPLAY_DRIFT: diagnostic replay diverged from run_principle_b on "
                         "passage %r" % passage_id)
    return records


def _make_record(stream, pos, rec, entities, compat, pool, best, cb_state, pb_action,
                 assigned_positions, cur_clause, passage_id, dataset, preds) -> dict:
    gold_i = rec["gold_entity"]
    gold_ids = _gold_correct_ids(assigned_positions, stream, gold_i)
    reg_ids = {e.eid for e in entities}
    compat_ids = {e.eid for e in compat}
    pool_ids = {e.eid for e in pool}

    gold_in_registry = bool(gold_ids & reg_ids)
    gold_in_compat = bool(gold_ids & compat_ids)
    gold_in_pool = bool(gold_ids & pool_ids)
    correct = not mention_link_wrong(pos, stream, preds)

    if gold_in_pool:
        cause = {"cb_unique": "RANKING_cb_unique_wrong", "cb_tied": "RANKING_cb_tied_wrong",
                 "cb_none": "RANKING_cb_none_wrong"}[cb_state]
    elif gold_in_compat:
        cause = "RETRIEVAL_pb_filter_removed_gold"
    elif gold_in_registry:
        cause = "RETRIEVAL_agreement_filter_removed_gold"
    else:
        cause = "RETRIEVAL_no_gold_entity_in_registry"

    gold_pool_ents = [e for e in pool if e.eid in gold_ids]
    gold_ent = max(gold_pool_ents, key=lambda e: e.last_pos) if gold_pool_ents else None
    known_genders = sorted({e.gender for e in pool if e.gender is not None})
    n_known_gender = sum(1 for e in pool if e.gender is not None)

    prior_gold = [j for j in range(pos) if stream[j]["gold_entity"] == gold_i]
    clause_dist_gold = (cur_clause - stream[max(prior_gold)]["clause"]) if prior_gold else None

    most_recent_in_pool = max(pool, key=lambda e: e.last_pos)

    return {
        "dataset": dataset, "passage_id": passage_id, "pos": pos, "clause": cur_clause,
        "mention_text": rec["mention_text"], "pron_gender": rec["gender"],
        "pron_number": rec["number"], "pron_role": rec.get("role"),
        "gold_entity": gold_i, "correct": bool(correct), "cause": cause,
        "cb_state": cb_state, "pb_action": pb_action,
        "n_compat": len(compat), "n_pool": len(pool),
        "gold_in_registry": gold_in_registry, "gold_in_compat": gold_in_compat,
        "gold_in_pool": gold_in_pool,
        "same_gender_all_pool": bool(n_known_gender >= 2 and len(known_genders) == 1),
        "n_known_gender_in_pool": n_known_gender,
        "dist_chosen": pos - best.last_pos,
        "dist_gold": (pos - gold_ent.last_pos) if gold_ent is not None else None,
        "clause_dist_gold": clause_dist_gold,
        "gold_is_prev_clause_subject": (
            gold_ent.clause_role.get(cur_clause - 1) in SUBJECT_LIKE_ROLES
            if gold_ent is not None else None),
        "chosen_is_prev_clause_subject": best.clause_role.get(cur_clause - 1) in SUBJECT_LIKE_ROLES,
        "gold_ever_subject": (
            gold_ent.most_recent_subject_clause(cur_clause) is not None
            if gold_ent is not None else None),
        "chosen_ever_subject": best.most_recent_subject_clause(cur_clause) is not None,
        "gold_is_most_recent_in_pool": (
            most_recent_in_pool.eid in gold_ids if pool else False),
        "chosen_eid": best.eid,
    }


# ---------------------------------------------------------------------------
# Tallies
# ---------------------------------------------------------------------------
def _rate(recs: List[dict], pred) -> dict:
    sel = [r for r in recs if pred(r)]
    err = [r for r in sel if not r["correct"]]
    return {"n": len(sel), "n_err": len(err),
            "err_rate": (len(err) / len(sel)) if sel else None}


def tally(recs: List[dict]) -> dict:
    errs = [r for r in recs if not r["correct"]]
    by_cause_all = {c: sum(1 for r in recs if r["cause"] == c) for c in CAUSES}
    by_cause_err = {c: sum(1 for r in errs if r["cause"] == c) for c in CAUSES}
    by_cb_all = {s: sum(1 for r in recs if r["cb_state"] == s)
                 for s in ("cb_unique", "cb_tied", "cb_none")}
    by_cb_err = {s: sum(1 for r in errs if r["cb_state"] == s)
                 for s in ("cb_unique", "cb_tied", "cb_none")}
    n_ret_err = sum(by_cause_err[c] for c in RETRIEVAL_CAUSES)

    strata = {
        "same_gender_all_pool": _rate(recs, lambda r: r["same_gender_all_pool"]),
        "mixed_or_unknown_gender_pool": _rate(recs, lambda r: not r["same_gender_all_pool"]),
        "pool_size_2": _rate(recs, lambda r: r["n_pool"] == 2),
        "pool_size_3plus": _rate(recs, lambda r: r["n_pool"] >= 3),
        "pb_filter_fired": _rate(recs, lambda r: r["pb_action"] == "fired"),
        "pb_filter_abstained": _rate(recs, lambda r: r["pb_action"] != "fired"),
        "gold_is_most_recent_in_pool": _rate(recs, lambda r: r["gold_is_most_recent_in_pool"]),
        "gold_is_NOT_most_recent_in_pool": _rate(recs, lambda r: not r["gold_is_most_recent_in_pool"]),
        "gold_is_prev_clause_subject": _rate(recs, lambda r: r["gold_is_prev_clause_subject"] is True),
        "gold_not_prev_clause_subject": _rate(recs, lambda r: r["gold_is_prev_clause_subject"] is False),
        "gold_ever_subject_true": _rate(recs, lambda r: r["gold_ever_subject"] is True),
        "gold_ever_subject_false": _rate(recs, lambda r: r["gold_ever_subject"] is False),
        "clause_dist_gold_0": _rate(recs, lambda r: r["clause_dist_gold"] == 0),
        "clause_dist_gold_1": _rate(recs, lambda r: r["clause_dist_gold"] == 1),
        "clause_dist_gold_2plus": _rate(
            recs, lambda r: r["clause_dist_gold"] is not None and r["clause_dist_gold"] >= 2),
        "pron_role_agent": _rate(recs, lambda r: r["pron_role"] in SUBJECT_LIKE_ROLES),
        "pron_role_nonagent": _rate(
            recs, lambda r: r["pron_role"] is not None and r["pron_role"] not in SUBJECT_LIKE_ROLES),
        "pron_role_unknown": _rate(recs, lambda r: r["pron_role"] is None),
    }
    by_surface: Dict[str, dict] = {}
    for surf in sorted({r["mention_text"].lower() for r in recs}):
        by_surface[surf] = _rate(recs, lambda r, s=surf: r["mention_text"].lower() == s)

    return {
        "n_competitive": len(recs), "n_errors": len(errs),
        "primary_cause_counts_ALL_decisions": by_cause_all,
        "primary_cause_counts_ERRORS_ONLY": by_cause_err,
        "cb_state_counts_ALL_decisions": by_cb_all,
        "cb_state_counts_ERRORS_ONLY": by_cb_err,
        "n_retrieval_errors": n_ret_err,
        "n_ranking_errors": len(errs) - n_ret_err,
        "strata_error_rates_with_base_rates": strata,
        "by_pronoun_surface": by_surface,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _write_start_marker(out_dir: str, mode: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR, "run_mode": mode, "expected_n_units": 2,
              "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_crash_metrics(out_dir: str, exc: Exception) -> None:
    os.makedirs(out_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED", "anchor_name": ANCHOR,
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def self_test() -> int:
    fails: List[str] = []
    import inspect
    # (F.2) bind against the LIVE signatures of every substrate callable this cell drives.
    for fn, kwargs in ((run_principle_b, {"stream": []}),
                       (_principle_b_filter, {"compat": [], "cur_clause": 0, "cur_role": None})):
        try:
            inspect.signature(fn).bind(**kwargs)
        except TypeError as e:
            fails.append("signature drift on %s: %s" % (fn.__name__, e))

    ps = load_passages(DATASETS["g5g6_reviewed"])
    sts = streams_for(ps)

    # (1) REPLAY_DRIFT guard: the diagnostic replay must reproduce run_principle_b byte-identically.
    #     This is the load-bearing check -- every category is meaningless without it.
    for k, st in enumerate(sts):
        preds = run_principle_b(st)[0]
        mask = competitive_mask(st)
        try:
            analyse_passage(st, mask, preds, "selftest_%d" % k, "g5g6_reviewed")
        except ValueError as e:
            fails.append(str(e))
            break

    # (2) _cb_outcome's pick must equal hdlab's _pick_strict_cb on constructed pools, and the three
    #     states must all be reachable (range by construction, not asserted).
    from hdlab.coreference_resolver import _pick_strict_cb
    a, b, c = TrackedEntity(0), TrackedEntity(1), TrackedEntity(2)
    a.last_pos, b.last_pos, c.last_pos = 1, 2, 3
    a.clause_role = {1: "agent"}
    b.clause_role = {1: "agent"}
    c.clause_role = {}
    states = set()
    for pool in ([a, c], [a, b], [c]):
        st_, pick = _cb_outcome(pool, 5)
        states.add(st_)
        if pick is not _pick_strict_cb(pool, 5):
            fails.append("_cb_outcome pick diverged from hdlab _pick_strict_cb")
    if states != {"cb_unique", "cb_tied", "cb_none"}:
        fails.append("cb states not all reachable in the self-test: %s" % sorted(states))

    # (3) the gold-correct test must agree with mention_link_wrong on a constructed case: choosing a
    #     gold-correct entity scores correct, choosing a non-gold one scores wrong.
    stream = [{"gold_entity": "A"}, {"gold_entity": "B"}, {"gold_entity": "A"}]
    if mention_link_wrong(2, stream, [0, 1, 0]):
        fails.append("mention_link_wrong called a gold-correct link wrong")
    if not mention_link_wrong(2, stream, [0, 1, 1]):
        fails.append("mention_link_wrong called a non-gold link correct")

    # (4) determinism: no RNG in this cell; two runs must be identical.
    r1 = analyse_passage(sts[0], competitive_mask(sts[0]), run_principle_b(sts[0])[0], "p", "d")
    r2 = analyse_passage(sts[0], competitive_mask(sts[0]), run_principle_b(sts[0])[0], "p", "d")
    if r1 != r2:
        fails.append("analyse_passage non-deterministic")

    # (5) every emitted record must carry exactly one of the six pre-registered causes.
    for r in r1:
        if r["cause"] not in CAUSES:
            fails.append("record carries an unregistered cause %r" % r["cause"])
            break

    for f in fails:
        print("SELF-TEST FAIL:", f, flush=True)
    if fails:
        return 1
    print("SELF-TEST PASS (5 checks + live-signature bind: replay reproduces run_principle_b "
          "byte-identically on every g5g6 passage, _cb_outcome matches _pick_strict_cb with all "
          "three states reachable, gold-correct test agrees with mention_link_wrong both ways, "
          "determinism, causes are the pre-registered six)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def run(mode: str, out_dir: str, timeout_s: float) -> dict:
    t0 = time.time()
    ds_names = sorted(set(DATASETS.keys()))
    recs: List[dict] = []
    per_dataset: Dict[str, dict] = {}
    n_passages = 0
    strict_cb_errs = 0

    for name in ds_names:
        ps = load_passages(DATASETS[name])
        if mode == "smoke":
            ps = ps[:6]
        n_passages += len(ps)
        sts = streams_for(ps)
        d_recs: List[dict] = []
        for p, st in zip(ps, sts):
            preds = run_principle_b(st)[0]
            mask = competitive_mask(st)
            d_recs.extend(analyse_passage(st, mask, preds, p.get("passage_id", "?"), name))
            scb = run_strict_cb(st)
            for i in range(len(st)):
                if mask[i] and mention_link_wrong(i, st, scb):
                    strict_cb_errs += 1
        per_dataset[name] = tally(d_recs)
        recs.extend(d_recs)
        print("[progress] %s: %d competitive decisions, %d errors"
              % (name, len(d_recs), sum(1 for r in d_recs if not r["correct"])), flush=True)

    t = tally(recs)
    n_comp, n_err = t["n_competitive"], t["n_errors"]
    P = (n_comp - n_err) / n_comp if n_comp else float("nan")
    n_ret = t["n_retrieval_errors"]
    P_ceiling = (n_comp - n_ret) / n_comp if n_comp else float("nan")
    headroom = P_ceiling - P

    err_causes = t["primary_cause_counts_ERRORS_ONLY"]
    top_cause = max(sorted(CAUSES), key=lambda c: err_causes[c])
    top_share = (err_causes[top_cause] / n_err) if n_err else float("nan")
    fixable_causes = {c: v for c, v in err_causes.items() if c.startswith("RANKING_")}
    top_fixable = max(sorted(fixable_causes), key=lambda c: fixable_causes[c]) if fixable_causes else None
    n_top_fixable = fixable_causes[top_fixable] if top_fixable else 0

    drift = (mode == "full" and (n_comp != EXPECTED_N_COMPETITIVE or n_err != EXPECTED_N_ERRORS))
    licensed = headroom >= BANDS["ranking_headroom_licensing_delta"]
    pinned = top_share >= BANDS["top_cause_share_pinned_min"]
    powered = n_top_fixable >= BANDS["min_fixable_decisions_for_phase2"]

    if drift:
        verdict = "REPLAY_DRIFT"
        msg = ("REPLAY_DRIFT: expected %d competitive decisions / %d errors, got %d / %d. "
               "Categories are not reportable." % (EXPECTED_N_COMPETITIVE, EXPECTED_N_ERRORS,
                                                   n_comp, n_err))
    elif not licensed:
        verdict = "RETRIEVAL_DOMINATED"
        msg = ("RETRIEVAL_DOMINATED: %d of %d errors are RETRIEVAL failures (the gold antecedent "
               "was not in the pool the pick ranks over). A perfect ranking rule caps at "
               "P=%.4f, only +%.4f over the current %.4f -- below the %.2f licensing delta. "
               "No Phase-2 ranking cell is dispatched; the defect is the POOL, not the PICK."
               % (n_ret, n_err, P_ceiling, headroom, P,
                  BANDS["ranking_headroom_licensing_delta"]))
    elif not pinned:
        verdict = "DIFFUSE_UNPINNED"
        msg = ("DIFFUSE_UNPINNED: ranking headroom exists (+%.4f to P=%.4f) but the largest single "
               "pre-registered cause is %s at %d of %d errors (%.2f < %.2f). No cause is large "
               "enough to aim one brain-faithful mechanism at; PARKED rather than invented."
               % (headroom, P_ceiling, top_cause, err_causes[top_cause], n_err, top_share,
                  BANDS["top_cause_share_pinned_min"]))
    elif not powered:
        verdict = "PINNED_BUT_UNDERPOWERED"
        msg = ("PINNED_BUT_UNDERPOWERED: largest fixable cause %s carries only %d decisions "
               "(< %d). A perfect fix moves P by %.4f, which will not separate from zero on a "
               "%d-passage paired bootstrap. Characterised, not dispatched."
               % (top_fixable, n_top_fixable, BANDS["min_fixable_decisions_for_phase2"],
                  n_top_fixable / n_comp, n_passages))
    else:
        verdict = "RANKING_DOMINATED"
        msg = ("RANKING_DOMINATED: %d of %d errors are RANKING failures; a perfect ranking rule "
               "reaches P=%.4f (+%.4f over %.4f). Largest fixable cause %s at %d decisions "
               "(%.2f of errors). Phase-2 ranking cell LICENSED against that cause."
               % (n_err - n_ret, n_err, P_ceiling, headroom, P, top_fixable, n_top_fixable,
                  top_share))

    return {
        "anchor_name": ANCHOR, "verdict": verdict,
        "verdict_msg": msg + (" | PRIMARY metric = link-level pronoun accuracy on the COMPETITIVE "
                              "subset (>=2 gn-compatible candidates), pooled over both gold sets. "
                              "SAME-RUN FLOORS ON THIS METRIC: most_recent 0.5281 / singleton "
                              "0.0000. The 0.5614 / 0.3860 / oracle 0.9298 triple belongs to "
                              "exp_wire_coref_accumulate_situation_model_v1 on identity-demanding "
                              "QUERY accuracy and is NOT comparable to these arm scores."),
        "run_mode": mode, "elapsed_s": time.time() - t0, "timeout_s": timeout_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pid": os.getpid(),
        "summary": verdict,
        "prereg": PREREG, "prereg_commit": PREREG_COMMIT,
        "bands": BANDS,
        "datasets": {n: DATASETS[n] for n in ds_names},
        "n_passages": n_passages,
        "P_competitive_base_principle_b_recomputed": P,
        "P_competitive_base_principle_b_CITED": CITED_BASE_P,
        "floors_same_run_this_metric": {"floor_most_recent": CITED_FLOOR_MOST_RECENT,
                                        "floor_singleton": CITED_FLOOR_SINGLETON},
        "other_run_context_NOT_COMPARABLE": {
            "source": "exp_wire_coref_accumulate_situation_model_v1",
            "metric": "identity-demanding query accuracy, 36 McGuffey passages",
            "resolver": 0.7193, "earned": 0.6842, "oracle": 0.9298,
            "floor_recency": 0.5614, "floor_singleton": 0.3860},
        "discriminators": {
            "D1_n_errors": n_err,
            "D1_expected": EXPECTED_N_ERRORS,
            "D2_P_ceiling_ranking": P_ceiling,
            "D2_ranking_headroom": headroom,
            "D3_top_cause": top_cause, "D3_top_cause_share": top_share,
            "D4_n_cb_unique_wrong": err_causes["RANKING_cb_unique_wrong"],
        },
        "retrieval_vs_ranking": {
            "n_retrieval_errors": n_ret, "n_ranking_errors": n_err - n_ret,
            "retrieval_share_of_errors": (n_ret / n_err) if n_err else float("nan")},
        "strict_cb_competitive_errors_crosscheck": strict_cb_errs,
        "tally_pooled": t,
        "per_dataset": per_dataset,
        "error_records": [r for r in recs if not r["correct"]],
        "all_competitive_records": recs,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--timeout", type=float, default=600.0)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    out_dir = SMOKE_DIR if args.mode == "smoke" else OUTPUT_DIR
    _write_start_marker(out_dir, args.mode)
    m = run(args.mode, out_dir, args.timeout)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(m["verdict_msg"], flush=True)
    print("elapsed_s=%.2f" % m["elapsed_s"], flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
