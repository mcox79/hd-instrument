"""ORGAN 4 / E3 PHASE 2: restore literal Centering Cb -- previous-utterance window + ranked Cf.

PRE-REGISTRATION: preregs/2026-08-14_coref_cb_literal_centering_window_and_cf_rank_v1.md
(committed 36a2a68aa, BEFORE any arm was run). Arms, headline, controls, CF_RANK map and bands are
fixed there and are not restated differently here.

PHASE 1 (preregs/2026-08-14_coref_cb_tier_error_anatomy_v1.md, commit 5f31c838f) measured that
ZERO of the errors are RETRIEVAL failures -- the gold antecedent was in the pool on every single
competitive decision -- and that 21 of 25 (14 of 16 deduped) are RANKING_cb_unique_wrong. So the
defect is the PICK KEY, and only the pick key changes here.

ONE VARIABLE PER ARM, off the same base (hdlab run_principle_b):
  A  lookback window restricted to the immediately preceding clause  (Cb over Cf(U_n-1))
  B  binary agent tier replaced by the graded Cf rank               (SUBJ > DOBJ > IOBJ)
  C  BOTH -- the textbook Cb. DECLARED HEADLINE, not revisable.
Controls: Cb tier removed entirely (pure recency inside the same pipeline), two trivial floors,
and a scrambled-order control on the headline.

HARNESS FIX DISCLOSED IN THE PREREG: the two gold sets overlap (g5g6_reviewed is a STRICT SUBSET of
powered, 18 of 36 passages double-counted by every prior cell). PRIMARY corpus here is the DEDUPED
set; the legacy pooled view is reported as SECONDARY and may not set a band.

REUSE: registry, name branch, Principle-B filter, agreement filter, mention_link_wrong, bcubed and
build_mention_stream imported from hdlab UNCHANGED; competitive subset, floors, scoring and paired
bootstrap imported from the v1 ACT-R cell UNCHANGED.

ASCII-only. Pure symbolic; numpy only for the bootstrap.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.coreference_resolver import (  # noqa: E402
    SUBJECT_LIKE_ROLES,
    TrackedEntity,
    _mention_geometry,
    _observe_nominal,
    _observe_pronoun,
    _pick_strict_cb,
    _principle_b_filter,
    _resolve_name_branch,
    gn_compatible,
    run_principle_b,
)
from experiments.exp_coref_cue_based_retrieval_actr_activation_v1 import (  # noqa: E402
    BOOTSTRAP_SEED,
    DATASETS,
    arm_floor_most_recent,
    arm_floor_singleton,
    competitive_mask,
    load_passages,
    paired_bootstrap,
    scramble_streams,
    score_arm,
    streams_for,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR = "coref_cb_literal_centering_window_and_cf_rank_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
SMOKE_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR + "_smoke")

PREREG = "preregs/2026-08-14_coref_cb_literal_centering_window_and_cf_rank_v1.md"
PREREG_COMMIT = "36a2a68aa"
PHASE1_METRICS = "data/exp_coref_cb_tier_error_anatomy_v1/metrics.json"

# PRIMARY corpus is the DEDUPED superset alone; g5g6_reviewed is a strict subset of it.
CORPORA = {
    "PRIMARY_deduped": ["powered"],
    "SECONDARY_legacy_pooled_DUPLICATED": ["g5g6_reviewed", "powered"],
}
PRIMARY = "PRIMARY_deduped"

# CF_RANK: literature-fixed (Brennan/Friedman/Pollard 1987 SUBJ > DOBJ > IOBJ > OTHER) mapped onto
# this gold's complete thematic-role vocabulary. NOT a tuning surface; NOT swept.
# AMENDED before any arm ran (prereg section 5 amendment): 'addressee' and 'possessor' were missing
# from the first draft -- the self-test coverage check caught it. addressee -> IOBJ ("said unto the
# man"), possessor -> OTHER (genitive specifier). Assigned from the same literature ordering, with
# no arm result in hand.
CF_RANK = {"agent": 3, "experiencer": 3, "patient": 2, "theme": 2,
           "recipient": 1, "addressee": 1, "possessor": 0}
# Declared SENSITIVITY only. NOT headline-eligible (prereg section 5).
CF_RANK_ALT = {"agent": 3, "patient": 2, "theme": 2, "experiencer": 1,
               "recipient": 1, "addressee": 1, "possessor": 0}
CF_TIERS = (3, 2, 1, 0)

HEADLINE_ARM = "arm_C_cb_literal_centering"
BASE_ARM = "base_principle_b"

BANDS = {"hard_pass_delta": 0.05, "pass_delta": 0.02, "fail_delta": -0.02,
         "hard_fail_delta": -0.05, "d1_vacuity_min": 10}


# ---------------------------------------------------------------------------
# Pick rules. Each takes (pool, cur_clause) and returns the chosen entity.
# ---------------------------------------------------------------------------
def _msc_tier(e: TrackedEntity, rank: int, cur_clause: int, rank_map: Dict[str, int]) -> int:
    """Most recent clause < cur_clause at which e held a role of EXACTLY this Cf rank, else -1."""
    cands = [c for c, r in e.clause_role.items()
             if c < cur_clause and rank_map.get(r, -1) == rank]
    return max(cands) if cands else -1


def pick_base(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    """hdlab _pick_strict_cb, unchanged. Positive control."""
    return _pick_strict_cb(pool, cur_clause)


def pick_A_window(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    """ARM A -- ONE VARIABLE: the lookback window. Subject history counts ONLY at cur_clause - 1
    (Centering's Cb is defined over Cf(U_n-1)). Tier stays BINARY agent; ties and no-history fall
    back to last_pos exactly as the base does."""
    with_subject = [e for e in pool
                    if e.clause_role.get(cur_clause - 1) in SUBJECT_LIKE_ROLES]
    if with_subject:
        return max(with_subject, key=lambda e: e.last_pos)
    return max(pool, key=lambda e: e.last_pos)


def _pick_B_graded(pool: List[TrackedEntity], cur_clause: int,
                   rank_map: Dict[str, int]) -> TrackedEntity:
    """ARM B -- ONE VARIABLE: tier granularity. The lookback stays UNBOUNDED; the single agent tier
    becomes the graded Cf ranking, compared lexicographically from the top tier down, with last_pos
    still the final tiebreak. This is a strict REFINEMENT of the base ordering: entities the base
    separated on the top tier are separated identically; entities the base lumped together as
    'no subject history' are now ordered by the next Cf tier instead of by raw recency."""
    def key(e: TrackedEntity) -> tuple:
        return tuple(_msc_tier(e, r, cur_clause, rank_map) for r in CF_TIERS) + (e.last_pos,)
    return max(pool, key=key)


def pick_B_graded(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    return _pick_B_graded(pool, cur_clause, CF_RANK)


def pick_B_graded_alt(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    return _pick_B_graded(pool, cur_clause, CF_RANK_ALT)


def _pick_C_literal(pool: List[TrackedEntity], cur_clause: int,
                    rank_map: Dict[str, int]) -> TrackedEntity:
    """ARM C -- HEADLINE, declared composition of A and B: literal Centering Cb. Take the most
    recent clause in which ANY candidate was realized; among the candidates realized there, take the
    highest Cf rank; break remaining ties by last_pos. No candidate with any history -> last_pos."""
    realized = [max([c for c in e.clause_role if c < cur_clause], default=-1) for e in pool]
    c_star = max(realized)
    if c_star < 0:
        return max(pool, key=lambda e: e.last_pos)
    here = [e for e, c in zip(pool, realized) if c == c_star]
    return max(here, key=lambda e: (rank_map.get(e.clause_role.get(c_star), -1), e.last_pos))


def pick_C_literal(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    return _pick_C_literal(pool, cur_clause, CF_RANK)


def pick_C_literal_alt(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    return _pick_C_literal(pool, cur_clause, CF_RANK_ALT)


def pick_ctrl_recency(pool: List[TrackedEntity], cur_clause: int) -> TrackedEntity:
    """CONTROL -- the Cb tier removed entirely from the same pipeline. If arm A merely equals this,
    the window 'fix' is recency in disguise and the Cb tier contributes nothing."""
    return max(pool, key=lambda e: e.last_pos)


# ---------------------------------------------------------------------------
# run_principle_b with a PLUGGABLE pick. Everything else byte-identical to hdlab's.
# ---------------------------------------------------------------------------
def run_pb_picked(stream: List[dict],
                  pick: Callable[[List[TrackedEntity], int], TrackedEntity]) -> List[int]:
    entities: List[TrackedEntity] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                pool, _action = _principle_b_filter(compat, cur_clause, cur_role)
                best = pick(pool, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    return assigned


PICKS = {
    BASE_ARM: pick_base,
    "arm_A_cb_window_prev_clause": pick_A_window,
    "arm_B_cf_graded_rank": pick_B_graded,
    "arm_C_cb_literal_centering": pick_C_literal,
    "ctrl_cb_off_pure_recency": pick_ctrl_recency,
    "sens_arm_B_CF_RANK_ALT_NOT_HEADLINE": pick_B_graded_alt,
    "sens_arm_C_CF_RANK_ALT_NOT_HEADLINE": pick_C_literal_alt,
}
ARMS: Dict[str, Callable[[List[dict]], List[int]]] = {
    name: (lambda st, _p=p: run_pb_picked(st, _p)) for name, p in PICKS.items()
}
ARMS["floor_most_recent"] = arm_floor_most_recent
ARMS["floor_singleton"] = arm_floor_singleton
ARM_ORDER = sorted(set(ARMS.keys()))
BAND_ELIGIBLE = tuple(a for a in ARM_ORDER if not a.startswith("sens_"))


# ---------------------------------------------------------------------------
# Discriminators
# ---------------------------------------------------------------------------
def discriminators(streams: List[List[dict]], masks: List[List[bool]]) -> dict:
    d1 = {a: 0 for a in ARM_ORDER if a != BASE_ARM}
    d2 = 0
    d3 = 0
    digests: Dict[str, "hashlib._Hash"] = {a: hashlib.sha256() for a in ARM_ORDER}
    for stream, mask in zip(streams, masks):
        preds = {a: ARMS[a](stream) for a in ARM_ORDER}
        for a in ARM_ORDER:
            digests[a].update(bytes(str(preds[a]), "ascii"))
        base = preds[BASE_ARM]
        for i in range(len(stream)):
            if not mask[i]:
                continue
            for a in d1:
                if preds[a][i] != base[i]:
                    d1[a] += 1
        d2_p, d3_p = _bite_counts(stream, mask)
        d2 += d2_p
        d3 += d3_p
    hexes = {a: digests[a].hexdigest() for a in ARM_ORDER}
    dup = [(a, b) for a in ARM_ORDER for b in ARM_ORDER if a < b and hexes[a] == hexes[b]]
    return {"D1_differing_competitive_decisions_vs_base": d1,
            "D2_window_can_bite": d2, "D3_grading_can_bite": d3,
            "D4_arm_assignment_sha256": hexes,
            "D4_bit_identical_arm_pairs": [list(p) for p in dup]}


def _bite_counts(stream: List[dict], mask: List[bool]) -> Tuple[int, int]:
    """Replay the base registry and count decisions where each variable CAN change the outcome.

    D2: the base's winning most_recent_subject_clause reached back past the previous clause.
    D3: the most recent clause any candidate was realized in carries >=2 distinct Cf ranks."""
    entities: List[TrackedEntity] = []
    next_id = 0
    d2 = d3 = 0
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                pool, _a = _principle_b_filter(compat, cur_clause, cur_role)
                if mask[pos] and pool:
                    best = _pick_strict_cb(pool, cur_clause)
                    msc = best.most_recent_subject_clause(cur_clause)
                    if msc is not None and msc < cur_clause - 1:
                        d2 += 1
                    realized = [max([c for c in e.clause_role if c < cur_clause], default=-1)
                                for e in pool]
                    c_star = max(realized)
                    if c_star >= 0:
                        ranks = sorted({CF_RANK.get(e.clause_role.get(c_star), -1)
                                        for e, c in zip(pool, realized) if c == c_star})
                        if len(ranks) >= 2:
                            d3 += 1
                best = _pick_strict_cb(pool, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            continue
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
    return d2, d3


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _write_start_marker(out_dir: str, mode: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR, "run_mode": mode,
              "expected_n_units": len(CORPORA) * (len(ARM_ORDER) + 2), "host": platform.node()}
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
    for fn, kwargs in ((run_principle_b, {"stream": []}),
                       (_principle_b_filter, {"compat": [], "cur_clause": 0, "cur_role": None}),
                       (_resolve_name_branch, {"entities": [], "next_id": 0, "gender": None,
                                               "number": None, "toks": set(),
                                               "has_determiner": False})):
        try:
            inspect.signature(fn).bind(**kwargs)
        except TypeError as e:
            fails.append("signature drift on %s: %s" % (fn.__name__, e))

    ps = load_passages(DATASETS["powered"])
    sts = streams_for(ps)

    # (1) POSITIVE CONTROL: the keyed harness at the BASE pick must reproduce hdlab's
    #     run_principle_b byte-identically. Without this, no arm delta is interpretable.
    for st in sts:
        if run_pb_picked(st, pick_base) != run_principle_b(st)[0]:
            fails.append("HARNESS_DRIFT: keyed harness != hdlab run_principle_b at pick_base")
            break

    # (2) the CF_RANK map must cover exactly the corpus's role vocabulary (no silent -1 bucket).
    roles = sorted({m.get("role") for p in ps for ms in p["entities"].values() for m in ms
                    if m.get("role") is not None})
    missing = [r for r in roles if r not in CF_RANK]
    if missing:
        fails.append("CF_RANK does not cover corpus roles %s" % missing)
    if sorted(set(CF_RANK.values())) != sorted(set(CF_TIERS)):
        fails.append("CF_TIERS does not match the distinct ranks in CF_RANK")

    # (3) each pick rule must be a genuinely DIFFERENT function on constructed pools (META_RULE_AF
    #     at the mechanism level, before the assignment-hash check at run time).
    old_subj, recent_obj = TrackedEntity(0), TrackedEntity(1)
    old_subj.clause_role, old_subj.last_pos = {2: "agent"}, 2
    recent_obj.clause_role, recent_obj.last_pos = {9: "patient"}, 9
    pool = [old_subj, recent_obj]
    if pick_base(pool, 10) is not old_subj:
        fails.append("base pick did not prefer the ancient subject (premise of the fidelity gap)")
    if pick_A_window(pool, 10) is not recent_obj:
        fails.append("arm A did not fall back to recency when nobody was a prev-clause subject")
    if pick_B_graded(pool, 10) is not old_subj:
        fails.append("arm B did not preserve the base top-tier ordering (must be a REFINEMENT)")
    if pick_C_literal(pool, 10) is not recent_obj:
        fails.append("arm C did not take the most recently realized clause")
    if pick_ctrl_recency(pool, 10) is not recent_obj:
        fails.append("recency control is not pure recency")

    # (4) arm B must actually REFINE, not reorder: two entities the base cannot separate (neither
    #     ever an agent) get ordered by the next Cf tier instead of by raw recency.
    obj_old, iobj_new = TrackedEntity(2), TrackedEntity(3)
    obj_old.clause_role, obj_old.last_pos = {3: "patient"}, 3
    iobj_new.clause_role, iobj_new.last_pos = {8: "recipient"}, 8
    p2 = [obj_old, iobj_new]
    if pick_base(p2, 10) is not iobj_new:
        fails.append("base did not use raw recency when neither candidate has agent history")
    if pick_B_graded(p2, 10) is not obj_old:
        fails.append("arm B did not order the base's undifferentiated group by the next Cf tier")

    # (5) determinism (no RNG in any pick).
    if run_pb_picked(sts[0], pick_C_literal) != run_pb_picked(sts[0], pick_C_literal):
        fails.append("headline arm is non-deterministic")

    # (6) the floors must behave as declared, on real data.
    if arm_floor_singleton(sts[0]) != list(range(len(sts[0]))):
        fails.append("singleton floor is not one-cluster-per-mention")

    # (7) the corpora declaration must be true: g5g6_reviewed is a STRICT SUBSET of powered.
    gid = {json.loads(l)["passage_id"] for l in open(DATASETS["g5g6_reviewed"], encoding="utf-8")
           if l.strip()}
    pid = {p["passage_id"] for p in ps}
    if not gid < pid:
        fails.append("prereg claims g5g6_reviewed is a strict subset of powered; it is not")

    for f in fails:
        print("SELF-TEST FAIL:", f, flush=True)
    if fails:
        return 1
    print("SELF-TEST PASS (7 checks + live-signature bind: keyed harness reproduces "
          "run_principle_b byte-identically on all 36 powered passages, CF_RANK covers the corpus "
          "role vocabulary exactly, five pick rules differ as designed on constructed pools, arm B "
          "refines rather than reorders, headline determinism, floors, subset claim verified)",
          flush=True)
    return 0


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def _band(delta: float, boot: dict, P: Dict[str, float], d1: int) -> Tuple[str, str]:
    ci_excl0 = (boot["ci_lo"] > 0) or (boot["ci_hi"] < 0)
    beats = (P[HEADLINE_ARM] > P["floor_most_recent"]
             and P[HEADLINE_ARM] > P["floor_singleton"])
    if d1 < BANDS["d1_vacuity_min"]:
        return "VACUOUS", ("VACUOUS: headline differs from base on only %d competitive decisions "
                           "(< %d). Arms that barely disagree cannot be compared."
                           % (d1, BANDS["d1_vacuity_min"]))
    if not beats:
        return "FAIL", ("FAIL (floor breach): headline P=%.4f does not beat both trivial floors "
                        "(most_recent=%.4f, singleton=%.4f)."
                        % (P[HEADLINE_ARM], P["floor_most_recent"], P["floor_singleton"]))
    ci = "CI[%.4f,%.4f]" % (boot["ci_lo"], boot["ci_hi"])
    if delta <= BANDS["hard_fail_delta"] and ci_excl0:
        return "HARD_FAIL", "HARD_FAIL: delta=%.4f %s" % (delta, ci)
    if delta <= BANDS["fail_delta"]:
        return "FAIL", "FAIL: delta=%.4f <= %.2f %s" % (delta, BANDS["fail_delta"], ci)
    if delta >= BANDS["hard_pass_delta"] and ci_excl0:
        return "HARD_PASS", "HARD_PASS: delta=%.4f %s" % (delta, ci)
    if delta >= BANDS["pass_delta"] and ci_excl0:
        return "PASS", "PASS: delta=%.4f %s" % (delta, ci)
    return "MIDDLE_BAND", ("MIDDLE_BAND: delta=%.4f %s -- direction measured, magnitude NOT "
                           "resolvable on this corpus (52 decisions / 36 passages; +0.05 is 2.6 "
                           "decisions). Pre-registered as the most likely honest outcome even if "
                           "the mechanism is right. Not a win, not a refutation."
                           % (delta, ci))


def run(mode: str, out_dir: str, timeout_s: float) -> dict:
    t0 = time.time()
    done = completed_units(out_dir)
    per_corpus: Dict[str, dict] = {}

    for corpus in sorted(CORPORA):
        sts: List[List[dict]] = []
        n_pass = 0
        for ds in CORPORA[corpus]:
            ps = load_passages(DATASETS[ds])
            if mode == "smoke":
                ps = ps[:8]
            n_pass += len(ps)
            sts.extend(streams_for(ps))
        masks = [competitive_mask(s) for s in sts]

        for arm in ARM_ORDER:
            k = unit_key(corpus, arm)
            if k not in done:
                record_unit(out_dir, k, score_arm(sts, masks, ARMS[arm]))
        k = unit_key(corpus, "_scrambled_headline")
        if k not in done:
            sc = scramble_streams(sts)
            record_unit(out_dir, k, score_arm(sc, [competitive_mask(s) for s in sc],
                                              ARMS[HEADLINE_ARM]))
        k = unit_key(corpus, "_discriminators")
        if k not in done:
            record_unit(out_dir, k, discriminators(sts, masks))
        per_corpus[corpus] = {"n_passages": n_pass}
        print("[progress] %s: %d passages scored" % (corpus, n_pass), flush=True)

    units = load_units(out_dir)
    out: Dict[str, dict] = {}
    for corpus in sorted(CORPORA):
        arms = ARM_ORDER + ["_scrambled_headline"]
        P = {a: units[unit_key(corpus, a)]["P_competitive"] for a in arms}
        disc = units[unit_key(corpus, "_discriminators")]
        pp = {a: units[unit_key(corpus, a)]["per_passage"] for a in arms}
        boots = {a: paired_bootstrap(pp[a], pp[BASE_ARM], seed=BOOTSTRAP_SEED)
                 for a in arms if a != BASE_ARM}
        boots["headline_vs_scrambled"] = paired_bootstrap(
            pp[HEADLINE_ARM], pp["_scrambled_headline"], seed=BOOTSTRAP_SEED)
        boots["arm_A_vs_ctrl_cb_off"] = paired_bootstrap(
            pp["arm_A_cb_window_prev_clause"], pp["ctrl_cb_off_pure_recency"], seed=BOOTSTRAP_SEED)
        delta = P[HEADLINE_ARM] - P[BASE_ARM]
        verdict, msg = _band(delta, boots[HEADLINE_ARM], P,
                             disc["D1_differing_competitive_decisions_vs_base"][HEADLINE_ARM])
        out[corpus] = {
            "n_passages": per_corpus[corpus]["n_passages"],
            "n_competitive_decisions": units[unit_key(corpus, BASE_ARM)]["n_competitive"],
            "n_pronoun_decisions": units[unit_key(corpus, BASE_ARM)]["n_pronoun"],
            "P_competitive_by_arm": P,
            "pronoun_link_acc_by_arm": {a: units[unit_key(corpus, a)]["pronoun_link_acc"]
                                        for a in arms},
            "b3_pronoun_f1_by_arm": {a: units[unit_key(corpus, a)]["b3_pronoun_f1"] for a in arms},
            "delta_headline_vs_base": delta,
            "verdict": verdict, "verdict_msg": msg,
            "discriminators": disc, "paired_bootstrap": boots,
        }

    prim = out[PRIMARY]
    dup_pairs = prim["discriminators"]["D4_bit_identical_arm_pairs"]
    verdict, msg = prim["verdict"], prim["verdict_msg"]
    if dup_pairs:
        interesting = [p for p in dup_pairs if not (p[0].startswith("sens_") or p[1].startswith("sens_"))]
        if interesting:
            msg += (" | NOTE META_RULE_AF: bit-identical band-eligible arm pairs %s -- these arms "
                    "do not differ on this corpus." % interesting)

    return {
        "anchor_name": ANCHOR, "verdict": verdict, "summary": verdict,
        "verdict_msg": msg + (
            " | HEADLINE = %s, declared in the prereg before the run. PRIMARY = deduped 36-passage "
            "corpus; the legacy pooled view double-counts 18 passages and is SECONDARY. PRIMARY "
            "metric P = link-level pronoun accuracy on the COMPETITIVE subset (>=2 gn-compatible "
            "candidates). SAME-RUN, SAME-CORPUS, SAME-METRIC FLOORS: most_recent %.4f / singleton "
            "%.4f. Phase-1 measured ranking ceiling on this subset = 1.0000 (zero retrieval "
            "failures). The 0.5614 / 0.3860 / oracle 0.9298 triple belongs to "
            "exp_wire_coref_accumulate_situation_model_v1 on identity-demanding QUERY accuracy and "
            "is NOT comparable to these arm scores. CAVEAT: the gold supplies THEMATIC roles and "
            "Centering's Cf is over GRAMMATICAL functions; a negative here refutes THIS mapping, "
            "not Centering's Cf ordering."
            % (HEADLINE_ARM, prim["P_competitive_by_arm"]["floor_most_recent"],
               prim["P_competitive_by_arm"]["floor_singleton"])),
        "run_mode": mode, "elapsed_s": time.time() - t0, "timeout_s": timeout_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pid": os.getpid(),
        "prereg": PREREG, "prereg_commit": PREREG_COMMIT, "phase1_metrics": PHASE1_METRICS,
        "bands": BANDS, "headline_arm": HEADLINE_ARM, "primary_corpus": PRIMARY,
        "band_eligible_arms": list(BAND_ELIGIBLE),
        "cf_rank_HEADLINE": CF_RANK, "cf_rank_ALT_NOT_HEADLINE_ELIGIBLE": CF_RANK_ALT,
        "corpora": {c: [DATASETS[d] for d in CORPORA[c]] for c in sorted(CORPORA)},
        "by_corpus": out,
        "P_competitive_by_arm": prim["P_competitive_by_arm"],
        "n_competitive_decisions": prim["n_competitive_decisions"],
        "n_passages": prim["n_passages"],
        "discriminators": prim["discriminators"],
        "paired_bootstrap": prim["paired_bootstrap"],
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
