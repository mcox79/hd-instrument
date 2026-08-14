"""ORGAN 4 / E3 follow-up: keep the hard Centering/Principle-B architecture, fix ONLY the
provably-degenerate arithmetic underneath it.

PRE-REGISTRATION: preregs/2026-08-14_coref_actr_tiebreak_under_centering_v2.md (committed dd4bb4794,
BEFORE any arm was run). v1 = preregs/2026-08-14_coref_cue_based_retrieval_actr_activation_v1.md,
cell + results 277f84c36 (HARD_FAIL).

ONE VARIABLE: hdlab/coreference_resolver.py:227-236 `_pick_strict_cb` breaks Cb ties, and falls back
when no candidate has subject history, on `last_pos` = PURE RECENCY. This cell replaces ONLY that key
with ACT-R base-level activation B_i = ln(sum_k (now - t_k + 1)^-d), d = 0.5 PINNED (Anderson &
Schooler 1991). Principle B filter, Cb tier, name/nominal branch, registry and abstention policy are
byte-identical to hdlab's run_principle_b.

REUSE: imports ActrEntity and the scoring/bootstrap harness from the v1 cell; imports the registry,
name branch, gn_compatible, bcubed and mention_link_wrong from hdlab unchanged.

ASCII-only. Pure symbolic; numpy only for the bootstrap.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time
from typing import Callable, Dict, List, Tuple

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
    _principle_b_filter,
    _resolve_name_branch,
    gn_compatible,
    run_principle_b,
)
from experiments.exp_coref_cue_based_retrieval_actr_activation_v1 import (  # noqa: E402
    ACTR_D,
    BOOTSTRAP_SEED,
    DATASETS,
    ActrEntity,
    arm_floor_most_recent,
    arm_floor_singleton,
    competitive_mask,
    load_passages,
    paired_bootstrap,
    score_arm,
    streams_for,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR = "coref_actr_tiebreak_under_centering_v2"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
SMOKE_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR + "_smoke")

BANDS = {"hard_pass_delta": 0.05, "pass_delta": 0.02, "fail_delta": -0.02,
         "hard_fail_delta": -0.05, "d1_vacuity_min": 10}


# ---------------------------------------------------------------------------
# run_principle_b with a PLUGGABLE tiebreak key. Everything else byte-identical to hdlab's.
# ---------------------------------------------------------------------------
def _pick_cb_keyed(compat: List[ActrEntity], cur_clause: int, now: int,
                   key: Callable[[ActrEntity, int], float]) -> Tuple[ActrEntity, bool]:
    """hdlab _pick_strict_cb with the tiebreak/fallback key injected. Returns (pick, reached_tiebreak)
    where reached_tiebreak is True iff the Cb tier did NOT uniquely decide (>=2 tied on
    most-recent-subject-clause, or no candidate has subject history) -- i.e. iff `key` was
    load-bearing for this decision."""
    scored = [(e, e.most_recent_subject_clause(cur_clause)) for e in compat]
    with_subject = [(e, c) for e, c in scored if c is not None]
    if with_subject:
        best_c = max(c for _, c in with_subject)
        tied = [e for e, c in with_subject if c == best_c]
        return max(tied, key=lambda e: key(e, now)), len(tied) >= 2
    return max(compat, key=lambda e: key(e, now)), len(compat) >= 2


def _run_pb_keyed(stream: List[dict],
                  key: Callable[[ActrEntity, int], float]) -> Tuple[List[int], int]:
    """run_principle_b with the injected tiebreak key. Returns (assigned, n_reached_tiebreak)."""
    entities: List[ActrEntity] = []
    next_id = 0
    assigned: List[int] = []
    n_tb = 0
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                filtered, _action = _principle_b_filter(compat, cur_clause, cur_role)
                best, reached = _pick_cb_keyed(filtered, cur_clause, pos, key)
                if len(compat) >= 2 and reached:
                    n_tb += 1
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = ActrEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            best.presentations.append(pos)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        prev_n = len(entities)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        if len(entities) > prev_n:
            p = ActrEntity(best.eid)
            p.tokens, p.gender, p.number = best.tokens, best.gender, best.number
            p.count, p.last_pos, p.clause_role = best.count, best.last_pos, best.clause_role
            entities[-1] = p
            best = p
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        best.presentations.append(pos)
        assigned.append(best.eid)
    return assigned, n_tb


KEY_RECENCY = lambda e, now: float(e.last_pos)                       # noqa: E731  hdlab's own key
KEY_ACTR = lambda e, now: e.base_level(now, ACTR_D)                  # noqa: E731  the fix
KEY_SALIENCE = lambda e, now: e.salience(now)                        # noqa: E731  degenerate control


def arm_base_principle_b(stream):
    return run_principle_b(stream)[0]


def arm_pb_actr_tiebreak(stream):
    return _run_pb_keyed(stream, KEY_ACTR)[0]


def arm_pb_salience_tiebreak(stream):
    return _run_pb_keyed(stream, KEY_SALIENCE)[0]


ARMS = {
    "floor_most_recent": arm_floor_most_recent,
    "floor_singleton": arm_floor_singleton,
    "base_principle_b": arm_base_principle_b,
    "pb_actr_tiebreak": arm_pb_actr_tiebreak,
    "pb_salience_tiebreak": arm_pb_salience_tiebreak,
}
ARM_ORDER = sorted(set(ARMS.keys()))


def discriminators(streams: List[List[dict]], masks: List[List[bool]]) -> dict:
    d1 = 0
    d_tier = 0
    for stream, mask in zip(streams, masks):
        base = arm_base_principle_b(stream)
        actr, n_tb = _run_pb_keyed(stream, KEY_ACTR)
        d_tier += n_tb
        for i in range(len(stream)):
            if mask[i] and base[i] != actr[i]:
                d1 += 1
    return {"D1_actr_vs_principle_b_differing_competitive_decisions": d1,
            "D_tier_competitive_decisions_reaching_the_tiebreak": d_tier}


def self_test() -> int:
    fails = []
    ps = load_passages(DATASETS["g5g6_reviewed"])
    sts = streams_for(ps)
    # (1) HARNESS FIDELITY: with hdlab's OWN key (last_pos), the keyed reimplementation must
    #     reproduce run_principle_b byte-identically. This is the load-bearing check: it proves the
    #     only thing that differs in the treatment arm is the key.
    for st in sts:
        if _run_pb_keyed(st, KEY_RECENCY)[0] != run_principle_b(st)[0]:
            fails.append("keyed reimplementation drifted from hdlab run_principle_b at KEY_RECENCY")
            break
    # (2) the three keys must be genuinely different functions on a constructed case.
    a = ActrEntity(0); a.presentations = [0, 1, 2]; a.count, a.last_pos = 3, 2
    b = ActrEntity(1); b.presentations = [99]; b.count, b.last_pos = 1, 99
    if not (KEY_RECENCY(b, 100) > KEY_RECENCY(a, 100)):
        fails.append("recency key does not prefer the just-mentioned entity")
    if not (KEY_SALIENCE(a, 100) > KEY_SALIENCE(b, 100)):
        fails.append("salience key is not count-primary (v1 D2 says it must be)")
    if not (KEY_ACTR(b, 100) > KEY_ACTR(a, 100)):
        fails.append("ACT-R key does not prefer the recent single mention over the old frequent one")
    # (3) ACT-R base level vs hand-computed.
    e = ActrEntity(0); e.presentations = [0, 8]
    if abs(e.base_level(10) - math.log(11.0 ** -0.5 + 3.0 ** -0.5)) > 1e-12:
        fails.append("base_level != hand-computed")
    # (4) determinism.
    if arm_pb_actr_tiebreak(sts[0]) != arm_pb_actr_tiebreak(sts[0]):
        fails.append("pb_actr_tiebreak non-deterministic")
    for f in fails:
        print("SELF-TEST FAIL:", f)
    if fails:
        return 1
    print("SELF-TEST PASS (4 checks: hdlab parity at KEY_RECENCY, three keys genuinely differ, "
          "base_level vs hand-computed, determinism)")
    return 0


def run(mode: str, out_dir: str, timeout_s: float) -> dict:
    t0 = time.time()
    ds_names = sorted(set(DATASETS.keys()))
    data = {}
    for name in ds_names:
        ps = load_passages(DATASETS[name])
        if mode == "smoke":
            ps = ps[:6]
        sts = streams_for(ps)
        data[name] = (sts, [competitive_mask(s) for s in sts])

    done = completed_units(out_dir)
    for name in ds_names:
        sts, masks = data[name]
        for arm in ARM_ORDER:
            k = unit_key(name, arm)
            if k not in done:
                record_unit(out_dir, k, score_arm(sts, masks, ARMS[arm]))
        k = unit_key(name, "_discriminators")
        if k not in done:
            record_unit(out_dir, k, discriminators(sts, masks))

    units = load_units(out_dir)

    def pooled(arm: str) -> dict:
        pp = []
        for name in ds_names:
            pp.extend(units[unit_key(name, arm)]["per_passage"])
        ct = sum(p["comp_t"] for p in pp)
        pt = sum(p["pron_t"] for p in pp)
        return {"per_passage": pp,
                "P_competitive": (sum(p["comp_c"] for p in pp) / ct) if ct else float("nan"),
                "pronoun_link_acc": (sum(p["pron_c"] for p in pp) / pt) if pt else float("nan"),
                "n_competitive": ct, "n_pronoun": pt,
                "b3_pronoun_f1": float(np.mean([units[unit_key(n, arm)]["b3_pronoun_f1"]
                                                for n in ds_names]))}

    pa = {a: pooled(a) for a in ARM_ORDER}
    disc = {"D1_actr_vs_principle_b_differing_competitive_decisions": 0,
            "D_tier_competitive_decisions_reaching_the_tiebreak": 0}
    for name in ds_names:
        for k2 in disc:
            disc[k2] += units[unit_key(name, "_discriminators")][k2]

    boots = {
        "pb_actr_tiebreak_vs_base_principle_b": paired_bootstrap(
            pa["pb_actr_tiebreak"]["per_passage"], pa["base_principle_b"]["per_passage"]),
        "pb_salience_tiebreak_vs_base_principle_b": paired_bootstrap(
            pa["pb_salience_tiebreak"]["per_passage"], pa["base_principle_b"]["per_passage"]),
        "pb_actr_tiebreak_vs_pb_salience_tiebreak": paired_bootstrap(
            pa["pb_actr_tiebreak"]["per_passage"], pa["pb_salience_tiebreak"]["per_passage"]),
    }
    P = {a: pa[a]["P_competitive"] for a in ARM_ORDER}
    b = boots["pb_actr_tiebreak_vs_base_principle_b"]
    delta = P["pb_actr_tiebreak"] - P["base_principle_b"]
    ci_excl0 = (b["ci_lo"] > 0) or (b["ci_hi"] < 0)
    beats = P["pb_actr_tiebreak"] > P["floor_most_recent"] and P["pb_actr_tiebreak"] > P["floor_singleton"]

    if disc["D1_actr_vs_principle_b_differing_competitive_decisions"] < BANDS["d1_vacuity_min"]:
        verdict = "VACUOUS"
        msg = ("VACUOUS: D1=%d < %d. The Cb tier decides before the tiebreak is consulted often "
               "enough for the arms to differ; the tiebreak key is not where this resolver's signal "
               "lives. D_tier=%d of %d competitive decisions reached the tiebreak."
               % (disc["D1_actr_vs_principle_b_differing_competitive_decisions"],
                  BANDS["d1_vacuity_min"],
                  disc["D_tier_competitive_decisions_reaching_the_tiebreak"],
                  pa["base_principle_b"]["n_competitive"]))
    elif not beats:
        verdict = "FAIL"
        msg = "FAIL: pb_actr_tiebreak P=%.4f does not beat both trivial floors (%.4f / %.4f)" % (
            P["pb_actr_tiebreak"], P["floor_most_recent"], P["floor_singleton"])
    elif delta <= BANDS["hard_fail_delta"] and ci_excl0:
        verdict, msg = "HARD_FAIL", "HARD_FAIL: delta=%.4f CI[%.4f,%.4f]" % (delta, b["ci_lo"], b["ci_hi"])
    elif delta <= BANDS["fail_delta"]:
        verdict, msg = "FAIL", "FAIL: delta=%.4f <= %.2f" % (delta, BANDS["fail_delta"])
    elif delta >= BANDS["hard_pass_delta"] and ci_excl0:
        verdict, msg = "HARD_PASS", "HARD_PASS: delta=%.4f CI[%.4f,%.4f]" % (delta, b["ci_lo"], b["ci_hi"])
    elif delta >= BANDS["pass_delta"] and ci_excl0:
        verdict, msg = "PASS", "PASS: delta=%.4f CI[%.4f,%.4f]" % (delta, b["ci_lo"], b["ci_hi"])
    else:
        verdict, msg = "MIDDLE_BAND", "MIDDLE_BAND: delta=%.4f CI[%.4f,%.4f]" % (delta, b["ci_lo"], b["ci_hi"])

    return {
        "anchor_name": ANCHOR, "verdict": verdict,
        "verdict_msg": msg + (" | PRIMARY P = link-level pronoun accuracy on the COMPETITIVE subset "
                              "(>=2 gn-compatible candidates), pooled over both gold sets."),
        "run_mode": mode, "elapsed_s": time.time() - t0, "timeout_s": timeout_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pid": os.getpid(),
        "prereg": "preregs/2026-08-14_coref_actr_tiebreak_under_centering_v2.md",
        "prereg_commit": "dd4bb4794", "v1_cell_commit": "277f84c36",
        "bands": BANDS, "actr_params": {"d_PINNED": ACTR_D},
        "datasets": {n: DATASETS[n] for n in ds_names},
        "P_competitive_by_arm": P,
        "pronoun_link_acc_by_arm": {a: pa[a]["pronoun_link_acc"] for a in ARM_ORDER},
        "b3_pronoun_f1_by_arm": {a: pa[a]["b3_pronoun_f1"] for a in ARM_ORDER},
        "n_competitive_decisions": pa["base_principle_b"]["n_competitive"],
        "n_pronoun_decisions": pa["base_principle_b"]["n_pronoun"],
        "n_passages": sum(len(data[n][0]) for n in ds_names),
        "discriminators": disc, "paired_bootstrap": boots,
        "per_dataset": {n: {a: {k: v for k, v in units[unit_key(n, a)].items() if k != "per_passage"}
                            for a in ARM_ORDER} for n in ds_names},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--timeout", type=float, default=900.0)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    out_dir = SMOKE_DIR if args.mode == "smoke" else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    m = run(args.mode, out_dir, args.timeout)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(m["verdict_msg"])
    print("elapsed_s=%.2f" % m["elapsed_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
