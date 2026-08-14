"""ORGAN 4 / E3: coreference as COMPETITIVE CUE-BASED RETRIEVAL, not a positional heuristic.

PRE-REGISTRATION: preregs/2026-08-14_coref_cue_based_retrieval_actr_activation_v1.md
(committed 1544d7e2a, BEFORE any arm was run). Bands, arms, discriminators and the floor
correction are fixed there; this file must not restate them differently.

TOP FIDELITY GAP BEING FIXED (audit in the prereg, section 1):
  hdlab/coreference_resolver.py:192 == hdlab/state_of_mind.py:247
      salience = count + OVERLAY_BETA * exp(-OVERLAY_TIEBREAK_LAMBDA * (now - last_pos))
      with OVERLAY_BETA = 0.5, OVERLAY_TIEBREAK_LAMBDA = 0.1.
  `count` is an INTEGER and the recency term lies in (0, 0.5]. Therefore
      count_a >= count_b + 1  =>  salience_a >= count_b + 1 > count_b + 0.5 >= salience_b.
  The recency term can NEVER overturn a count gap of 1. Our "Centering salience" is exactly
  `argmax count, ties broken by recency` -- a pure FREQUENCY rule. D2 machine-checks this.

  The brain's operation is ACT-R base-level activation, B_i = ln(sum_k (t - t_k)^-d) with d = 0.5
  PINNED (Anderson & Schooler 1991; Lewis & Vasishth 2005 use this form for exactly this task),
  plus cue-weighted match with a FAN term S_ji = S - ln(fan_j) that produces similarity-based
  interference (Jaeger, Engelmann & Vasishth 2017). ln-of-sum-of-power-law-decays puts frequency and
  recency on ONE commensurate scale, so a recent single mention CAN outrank an old frequent one --
  structurally impossible under our arithmetic.

REUSE: this cell reuses hdlab.coreference_resolver's registry, its name/nominal branch, its
gn_compatible, its bcubed and its mention_link_wrong UNCHANGED. cleanup_family / iterative_attractor
/ dg_pattern_separation were checked and judged does-not-serve (they are numpy hypervector-codebook
cleanup; this competition is over a symbolic registry with discrete cues and a temporal trace --
routing through them would insert a lossy vector channel carrying none of the base-level/fan math).

GLASS-BOX: pure symbolic; numpy only for the bootstrap. No torch, no network, no external coref tool.
ASCII-only.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import random
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.coreference_resolver import (  # noqa: E402
    SUBJECT_LIKE_ROLES,
    TrackedEntity,
    _observe_nominal,
    _observe_pronoun,
    _mention_geometry,
    _pick_strict_cb,
    _principle_b_filter,
    _resolve_name_branch,
    bcubed,
    build_mention_stream,
    gn_compatible,
    mention_link_wrong,
    run_match_or_allocate,
    run_principle_b,
    run_strict_cb,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR = "coref_cue_based_retrieval_actr_activation_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
SMOKE_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR + "_smoke")

GOLD_DIR = os.path.join(REPO, "data", "eval_gold_mention_role_mcguffey_v1")
DATASETS = {
    "powered": os.path.join(GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl"),
    "g5g6_reviewed": os.path.join(GOLD_DIR, "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl"),
}

# ACT-R parameters. d is PINNED by the literature; W and S are NOT pinned for this task and are
# ACT-R defaults -- see prereg section 2. Only (W=1.0, S=1.5) is eligible to set the headline; the
# S sweep below is reported as SENSITIVITY and may not be used to reach a band.
ACTR_D = 0.5
ACTR_W = 1.0
ACTR_S = 1.5
S_SENSITIVITY = (1.0, 1.5, 2.0)

BOOTSTRAP_N = 10000
BOOTSTRAP_SEED = 12345
SCRAMBLE_SEED = 12345

BANDS = {
    "hard_pass_delta": 0.05,
    "pass_delta": 0.02,
    "fail_delta": -0.02,
    "hard_fail_delta": -0.05,
    "d1_vacuity_min": 10,
}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load_passages(path: str) -> List[dict]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def streams_for(passages: List[dict]) -> List[List[dict]]:
    return [build_mention_stream(p) for p in passages]


# ---------------------------------------------------------------------------
# ACT-R entity: adds the TRACE HISTORY the current TrackedEntity discards (fidelity gap #5).
# ---------------------------------------------------------------------------
class ActrEntity(TrackedEntity):
    __slots__ = ("presentations",)

    def __init__(self, eid: int) -> None:
        super().__init__(eid)
        self.presentations: List[int] = []

    def base_level(self, now: int, d: float = ACTR_D) -> float:
        """ACT-R base-level activation B_i = ln(sum_k (now - t_k + 1)^-d). +1 keeps t=now finite."""
        if not self.presentations:
            return -30.0
        s = 0.0
        for t in self.presentations:
            s += (now - t + 1.0) ** (-d)
        return math.log(s)


def _cue_matches(e: ActrEntity, gender: Optional[str], number: Optional[str],
                 cur_clause: int) -> Tuple[int, int, int]:
    """Per-cue boolean match of entity e against the pronoun's posted cues.

    Returns (gender_match, number_match, cb_subject_match). An entity whose attribute is UNKNOWN
    (None) does not match -- it simply receives no boost, and is NOT excluded. That is the
    parallel-retrieval fidelity fix: no candidate is ever filtered out of the pool."""
    g_ok = int(gender is not None and e.gender is not None
               and (gender == "any" or e.gender == "any" or gender == e.gender))
    n_ok = int(number is not None and e.number is not None and number == e.number)
    cb_ok = int(e.clause_role.get(cur_clause - 1) in SUBJECT_LIKE_ROLES)
    return g_ok, n_ok, cb_ok


def _actr_activations(entities: List[ActrEntity], gender: Optional[str], number: Optional[str],
                      cur_clause: int, now: int, s_param: float,
                      w_param: float = ACTR_W) -> Tuple[List[float], List[int]]:
    """A_i = B_i + sum_j W_j*(S - ln(fan_j))*match_ij, W_j = W/n_cues, fan_j = #entities matching j.

    Returns (activations, fans) where fans = [fan_gender, fan_number, fan_cb]."""
    matches = [_cue_matches(e, gender, number, cur_clause) for e in entities]
    fans = [sum(m[j] for m in matches) for j in range(3)]
    n_cues = 3
    w_j = w_param / n_cues
    acts = []
    for e, m in zip(entities, matches):
        a = e.base_level(now)
        for j in range(n_cues):
            if m[j] and fans[j] > 0:
                a += w_j * (s_param - math.log(fans[j]))
        acts.append(a)
    return acts, fans


# ---------------------------------------------------------------------------
# Arms. Arms 4-8 share the name/nominal branch byte-identically (hdlab _resolve_name_branch).
# No arm abstains (every baseline runs at flag_unresolved=False), so abstention policy is held
# constant and is NOT the variable under test -- margins are recorded as a diagnostic only.
# ---------------------------------------------------------------------------
def arm_floor_most_recent(stream: List[dict]) -> List[int]:
    """TRIVIAL FLOOR 1: a pronoun takes the entity of the IMMEDIATELY PRECEDING mention.
    Names match by exact normalised surface string (no mechanism). 'Just pick the most recent
    mention' -- the floor a real coreference organ must beat."""
    assigned: List[int] = []
    by_surface: Dict[str, int] = {}
    next_id = 0
    for rec in stream:
        if rec["is_pronoun"] and assigned:
            assigned.append(assigned[-1])
            continue
        key = rec["mention_text"].lower().strip(".,'\"!?;:()")
        if key not in by_surface:
            by_surface[key] = next_id
            next_id += 1
        assigned.append(by_surface[key])
    return assigned


def arm_floor_singleton(stream: List[dict]) -> List[int]:
    """TRIVIAL FLOOR 2: every mention is its own entity (no coreference at all)."""
    return list(range(len(stream)))


def arm_floor_chain_all(stream: List[dict]) -> List[int]:
    """Existing hdlab floor: chain every mention into one cluster."""
    return [0] * len(stream)


def arm_base_salience(stream: List[dict]) -> List[int]:
    return run_match_or_allocate(stream)


def arm_base_strict_cb(stream: List[dict]) -> List[int]:
    return run_strict_cb(stream)


def arm_base_principle_b(stream: List[dict]) -> List[int]:
    return run_principle_b(stream)[0]


def _run_actr(stream: List[dict], parallel: bool, s_param: float = ACTR_S) -> Tuple[List[int], List[dict]]:
    """ACT-R resolver. parallel=False -> ONE variable vs base_salience (hard gn filter retained,
    argmax over base-level activation only). parallel=True -> additionally drops the hard filter and
    scores all entities by fan-weighted parallel cues. Name branch identical to every hdlab arm."""
    entities: List[ActrEntity] = []
    next_id = 0
    assigned: List[int] = []
    trace: List[dict] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if parallel:
                pool = entities
            else:
                pool = compat if compat else entities
            if pool:
                if parallel:
                    acts, fans = _actr_activations(pool, gender, number, cur_clause, pos, s_param)
                else:
                    acts = [e.base_level(pos) for e in pool]
                    fans = [0, 0, 0]
                order = sorted(range(len(pool)), key=lambda i: (-acts[i], -pool[i].last_pos))
                best = pool[order[0]]
                margin = (acts[order[0]] - acts[order[1]]) if len(order) > 1 else float("inf")
                trace.append({"pos": pos, "n_compat": len(compat), "fan_gender": fans[0],
                              "margin": margin})
            else:
                best = ActrEntity(next_id)
                next_id += 1
                entities.append(best)
                best.gender, best.number = gender, number
                trace.append({"pos": pos, "n_compat": 0, "fan_gender": 0, "margin": float("inf")})
            _observe_pronoun(best, pos, cur_clause, cur_role)
            best.presentations.append(pos)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        prev_n = len(entities)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        if len(entities) > prev_n:  # _resolve_name_branch allocated a plain TrackedEntity
            promoted = ActrEntity(best.eid)
            promoted.tokens, promoted.gender, promoted.number = best.tokens, best.gender, best.number
            promoted.count, promoted.last_pos = best.count, best.last_pos
            promoted.clause_role = best.clause_role
            entities[-1] = promoted
            best = promoted
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        best.presentations.append(pos)
        assigned.append(best.eid)
    return assigned, trace


def arm_actr_base(stream: List[dict]) -> List[int]:
    return _run_actr(stream, parallel=False)[0]


def arm_actr_parallel(stream: List[dict]) -> List[int]:
    return _run_actr(stream, parallel=True)[0]


ARMS = {
    "floor_most_recent": arm_floor_most_recent,
    "floor_singleton": arm_floor_singleton,
    "floor_chain_all": arm_floor_chain_all,
    "base_salience": arm_base_salience,
    "base_strict_cb": arm_base_strict_cb,
    "base_principle_b": arm_base_principle_b,
    "actr_base": arm_actr_base,
    "actr_parallel": arm_actr_parallel,
}
ARM_ORDER = sorted(set(ARMS.keys()))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def competitive_mask(stream: List[dict]) -> List[bool]:
    """True at pronoun mentions facing >=2 gn-compatible tracked candidates, replaying the SAME
    registry growth every hdlab resolver uses (so the subset is arm-independent by construction)."""
    entities: List[TrackedEntity] = []
    next_id = 0
    mask: List[bool] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            mask.append(len(compat) >= 2)
            if compat:
                best = max(compat, key=lambda e: e.salience(pos))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
            _observe_pronoun(best, pos, cur_clause, cur_role)
            continue
        mask.append(False)
        toks, has_determiner = _mention_geometry(rec)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
    return mask


def score_arm(streams: List[List[dict]], masks: List[List[bool]],
              fn) -> dict:
    """Per-passage link-level correctness on the competitive subset + on all pronouns, plus B3."""
    per_passage = []
    sp = []
    for stream, mask in zip(streams, masks):
        preds = fn(stream)
        sp.append((stream, preds))
        comp_c = comp_t = pron_c = pron_t = 0
        for i in range(len(stream)):
            if not stream[i]["is_pronoun"]:
                continue
            ok = 0 if mention_link_wrong(i, stream, preds) else 1
            pron_c += ok
            pron_t += 1
            if mask[i]:
                comp_c += ok
                comp_t += 1
        per_passage.append({"comp_c": comp_c, "comp_t": comp_t, "pron_c": pron_c, "pron_t": pron_t})
    b3_pron = bcubed(sp, subset="pronoun")
    b3_all = bcubed(sp, subset=None)
    ct = sum(p["comp_t"] for p in per_passage)
    pt = sum(p["pron_t"] for p in per_passage)
    return {
        "per_passage": per_passage,
        "P_competitive": (sum(p["comp_c"] for p in per_passage) / ct) if ct else float("nan"),
        "n_competitive": ct,
        "pronoun_link_acc": (sum(p["pron_c"] for p in per_passage) / pt) if pt else float("nan"),
        "n_pronoun": pt,
        "b3_pronoun_f1": b3_pron["f1"],
        "b3_all_f1": b3_all["f1"],
    }


def paired_bootstrap(pp_a: List[dict], pp_b: List[dict], n: int = BOOTSTRAP_N,
                     seed: int = BOOTSTRAP_SEED) -> dict:
    """Paired CLUSTER bootstrap over passages of delta = P_competitive(a) - P_competitive(b).
    Arms share items, so passage indices are resampled ONCE and applied to both arms."""
    ca = np.array([p["comp_c"] for p in pp_a], dtype=np.float64)
    cb = np.array([p["comp_c"] for p in pp_b], dtype=np.float64)
    tt = np.array([p["comp_t"] for p in pp_a], dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(tt), size=(n, len(tt)))
    tot = tt[idx].sum(axis=1)
    good = tot > 0
    da = ca[idx].sum(axis=1)[good] / tot[good]
    db = cb[idx].sum(axis=1)[good] / tot[good]
    d = da - db
    return {"delta_mean": float(d.mean()), "ci_lo": float(np.percentile(d, 2.5)),
            "ci_hi": float(np.percentile(d, 97.5)), "n_resamples": int(good.sum()),
            "frac_gt0": float((d > 0).mean())}


# ---------------------------------------------------------------------------
# Discriminators
# ---------------------------------------------------------------------------
def discriminators(streams: List[List[dict]], masks: List[List[bool]]) -> dict:
    """D1 vacuity gate, D2 degeneracy witness, D3 fan activity. All have range by construction."""
    d1 = 0
    d2_agree = d2_total = 0
    d3 = 0
    for stream, mask in zip(streams, masks):
        p_sal = arm_base_salience(stream)
        p_act, trace = _run_actr(stream, parallel=True)
        tr = {t["pos"]: t for t in trace}
        for i in range(len(stream)):
            if mask[i] and p_sal[i] != p_act[i]:
                d1 += 1
            if mask[i] and i in tr and tr[i]["fan_gender"] >= 2:
                d3 += 1
        # D2: replay the salience registry and compare argmax(salience) to argmax(count)+recency.
        entities: List[TrackedEntity] = []
        next_id = 0
        for pos, rec in enumerate(stream):
            gender, number = rec["gender"], rec["number"]
            cur_clause, cur_role = rec["clause"], rec.get("role")
            if rec["is_pronoun"]:
                compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
                if len(compat) >= 2:
                    by_sal = max(compat, key=lambda e: e.salience(pos))
                    by_cnt = max(compat, key=lambda e: (e.count, e.last_pos))
                    d2_total += 1
                    d2_agree += int(by_sal.eid == by_cnt.eid)
                if compat:
                    best = max(compat, key=lambda e: e.salience(pos))
                elif entities:
                    best = max(entities, key=lambda e: e.last_pos)
                else:
                    best = TrackedEntity(next_id)
                    next_id += 1
                    entities.append(best)
                _observe_pronoun(best, pos, cur_clause, cur_role)
                continue
            toks, has_determiner = _mention_geometry(rec)
            best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks,
                                                 has_determiner)
            _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
    return {
        "D1_actr_vs_salience_differing_competitive_decisions": d1,
        "D2_salience_equals_argmax_count_fraction": (d2_agree / d2_total) if d2_total else float("nan"),
        "D2_n_multicandidate_decisions": d2_total,
        "D3_competitive_decisions_with_gender_fan_ge2": d3,
    }


def scramble_streams(streams: List[List[dict]], seed: int = SCRAMBLE_SEED) -> List[List[dict]]:
    """CONTROL: shuffle mention order within each passage. A win that survives is not discourse."""
    rng = random.Random(seed)
    out = []
    for s in streams:
        c = [dict(r) for r in s]
        rng.shuffle(c)
        out.append(c)
    return out


# ---------------------------------------------------------------------------
# Self-test: assert measured values match expected BEFORE any full run.
# ---------------------------------------------------------------------------
def self_test() -> int:
    fails = []

    # (1) DEGENERACY, analytically: recency term is bounded in (0, 0.5], count is an integer.
    from hdlab.state_of_mind import OVERLAY_BETA, OVERLAY_TIEBREAK_LAMBDA
    assert OVERLAY_BETA == 0.5 and OVERLAY_TIEBREAK_LAMBDA == 0.1
    a = TrackedEntity(0); a.count, a.last_pos = 3, 0        # frequent but ancient
    b = TrackedEntity(1); b.count, b.last_pos = 2, 999      # rarer but just mentioned
    if not (a.salience(1000) > b.salience(1000)):
        fails.append("D2 premise: count did NOT dominate a maximal recency gap")
    if not (0.0 < OVERLAY_BETA * math.exp(-OVERLAY_TIEBREAK_LAMBDA * 0) <= 0.5):
        fails.append("recency term not bounded in (0, 0.5]")

    # (2) ACT-R base level, hand-computed. Two presentations at t=0 and t=8, now=10, d=0.5:
    #     ln((10-0+1)^-0.5 + (10-8+1)^-0.5) = ln(1/sqrt(11) + 1/sqrt(3))
    e = ActrEntity(0); e.presentations = [0, 8]
    expect = math.log(11.0 ** -0.5 + 3.0 ** -0.5)
    if abs(e.base_level(10) - expect) > 1e-12:
        fails.append("base_level != hand-computed %.12f (got %.12f)" % (expect, e.base_level(10)))

    # (3) ACT-R base level INVERTS the degenerate ordering: a recent single mention outranks an old
    #     frequent one -- the property our arithmetic makes structurally impossible.
    freq_old = ActrEntity(0); freq_old.presentations = [0, 1, 2]
    recent = ActrEntity(1); recent.presentations = [99]
    if not (recent.base_level(100) > freq_old.base_level(100)):
        fails.append("ACT-R base level failed to invert the frequency-primary ordering")

    # (4) fan term: a cue matching 4 entities must contribute strictly less than one matching 1.
    hi = ACTR_W / 3 * (ACTR_S - math.log(1))
    lo = ACTR_W / 3 * (ACTR_S - math.log(4))
    if not (lo < hi):
        fails.append("fan term did not reduce cue diagnosticity")

    # (5) HARNESS FIDELITY: baseline arms must reproduce hdlab byte-identically (no drift).
    ps = load_passages(DATASETS["g5g6_reviewed"])
    sts = streams_for(ps)
    for name, mine, theirs in (
        ("base_salience", arm_base_salience, run_match_or_allocate),
        ("base_strict_cb", arm_base_strict_cb, run_strict_cb),
        ("base_principle_b", arm_base_principle_b, lambda s: run_principle_b(s)[0]),
    ):
        for st in sts:
            if mine(st) != theirs(st):
                fails.append("arm %s drifted from hdlab" % name)
                break

    # (6) floors behave as declared.
    st = sts[0]
    if arm_floor_singleton(st) != list(range(len(st))):
        fails.append("singleton floor is not one-cluster-per-mention")
    if len(set(arm_floor_chain_all(st))) != 1:
        fails.append("chain_all floor is not one cluster")

    # (7) determinism: ACT-R arm must be reproducible.
    if arm_actr_parallel(st) != arm_actr_parallel(st):
        fails.append("actr_parallel is non-deterministic")

    for f in fails:
        print("SELF-TEST FAIL:", f)
    if fails:
        return 1
    print("SELF-TEST PASS (7 checks: degeneracy premise, base-level vs hand-computed, ordering "
          "inversion, fan monotonicity, 3 hdlab-parity arms, floors, determinism)")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
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
            if k in done:
                continue
            record_unit(out_dir, k, score_arm(sts, masks, ARMS[arm]))
        k = unit_key(name, "actr_parallel_scrambled")
        if k not in done:
            sc = scramble_streams(sts)
            record_unit(out_dir, k, score_arm(sc, [competitive_mask(s) for s in sc],
                                              arm_actr_parallel))
        k = unit_key(name, "_discriminators")
        if k not in done:
            record_unit(out_dir, k, discriminators(sts, masks))
        for s_val in S_SENSITIVITY:
            k = unit_key(name, "sens_actr_parallel_S%.1f" % s_val)
            if k in done:
                continue
            record_unit(out_dir, k, score_arm(sts, masks,
                                              lambda st, _s=s_val: _run_actr(st, True, _s)[0]))

    units = load_units(out_dir)

    def pooled(arm: str) -> dict:
        pp = []
        for name in ds_names:
            pp.extend(units[unit_key(name, arm)]["per_passage"])
        ct = sum(p["comp_t"] for p in pp)
        pt = sum(p["pron_t"] for p in pp)
        return {
            "per_passage": pp,
            "P_competitive": (sum(p["comp_c"] for p in pp) / ct) if ct else float("nan"),
            "n_competitive": ct,
            "pronoun_link_acc": (sum(p["pron_c"] for p in pp) / pt) if pt else float("nan"),
            "n_pronoun": pt,
            "b3_pronoun_f1": float(np.mean([units[unit_key(n, arm)]["b3_pronoun_f1"]
                                            for n in ds_names])),
        }

    all_arms = ARM_ORDER + ["actr_parallel_scrambled"]
    pooled_arms = {a: pooled(a) for a in all_arms}
    disc = {"D1_actr_vs_salience_differing_competitive_decisions": 0,
            "D2_n_multicandidate_decisions": 0,
            "D3_competitive_decisions_with_gender_fan_ge2": 0}
    d2a = 0.0
    for name in ds_names:
        d = units[unit_key(name, "_discriminators")]
        disc["D1_actr_vs_salience_differing_competitive_decisions"] += d[
            "D1_actr_vs_salience_differing_competitive_decisions"]
        disc["D3_competitive_decisions_with_gender_fan_ge2"] += d[
            "D3_competitive_decisions_with_gender_fan_ge2"]
        n = d["D2_n_multicandidate_decisions"]
        disc["D2_n_multicandidate_decisions"] += n
        d2a += d["D2_salience_equals_argmax_count_fraction"] * n
    disc["D2_salience_equals_argmax_count_fraction"] = (
        d2a / disc["D2_n_multicandidate_decisions"]) if disc["D2_n_multicandidate_decisions"] else float("nan")

    boots = {}
    for a in ("actr_parallel", "actr_base", "base_strict_cb", "base_salience", "floor_most_recent"):
        boots[a + "_vs_base_principle_b"] = paired_bootstrap(
            pooled_arms[a]["per_passage"], pooled_arms["base_principle_b"]["per_passage"])
    boots["actr_base_vs_base_salience"] = paired_bootstrap(
        pooled_arms["actr_base"]["per_passage"], pooled_arms["base_salience"]["per_passage"])
    boots["actr_parallel_vs_actr_base"] = paired_bootstrap(
        pooled_arms["actr_parallel"]["per_passage"], pooled_arms["actr_base"]["per_passage"])
    boots["actr_parallel_vs_scrambled"] = paired_bootstrap(
        pooled_arms["actr_parallel"]["per_passage"], pooled_arms["actr_parallel_scrambled"]["per_passage"])

    P = {a: pooled_arms[a]["P_competitive"] for a in all_arms}
    b = boots["actr_parallel_vs_base_principle_b"]
    delta = P["actr_parallel"] - P["base_principle_b"]
    ci_excl0 = (b["ci_lo"] > 0) or (b["ci_hi"] < 0)
    beats_floors = (P["actr_parallel"] > P["floor_most_recent"]
                    and P["actr_parallel"] > P["floor_singleton"])

    if disc["D1_actr_vs_salience_differing_competitive_decisions"] < BANDS["d1_vacuity_min"]:
        verdict = "VACUOUS"
        msg = ("VACUOUS: D1=%d < %d differing competitive decisions -- arms that do not disagree "
               "cannot be compared; no band awarded."
               % (disc["D1_actr_vs_salience_differing_competitive_decisions"],
                  BANDS["d1_vacuity_min"]))
    elif not beats_floors:
        verdict = "FAIL"
        msg = ("FAIL: actr_parallel P=%.4f does not beat both trivial floors "
               "(most_recent=%.4f, singleton=%.4f)."
               % (P["actr_parallel"], P["floor_most_recent"], P["floor_singleton"]))
    elif delta <= BANDS["hard_fail_delta"] and ci_excl0:
        verdict = "HARD_FAIL"
        msg = "HARD_FAIL: delta vs base_principle_b = %.4f (CI %.4f..%.4f)" % (
            delta, b["ci_lo"], b["ci_hi"])
    elif delta <= BANDS["fail_delta"]:
        verdict = "FAIL"
        msg = "FAIL: delta vs base_principle_b = %.4f <= %.2f" % (delta, BANDS["fail_delta"])
    elif delta >= BANDS["hard_pass_delta"] and ci_excl0:
        verdict = "HARD_PASS"
        msg = "HARD_PASS: delta vs base_principle_b = %.4f (CI %.4f..%.4f)" % (
            delta, b["ci_lo"], b["ci_hi"])
    elif delta >= BANDS["pass_delta"] and ci_excl0:
        verdict = "PASS"
        msg = "PASS: delta vs base_principle_b = %.4f (CI %.4f..%.4f)" % (
            delta, b["ci_lo"], b["ci_hi"])
    else:
        verdict = "MIDDLE_BAND"
        msg = "MIDDLE_BAND: delta vs base_principle_b = %.4f (CI %.4f..%.4f)" % (
            delta, b["ci_lo"], b["ci_hi"])

    sens = {}
    for name in ds_names:
        for s_val in S_SENSITIVITY:
            sens["%s_S%.1f" % (name, s_val)] = units[unit_key(
                name, "sens_actr_parallel_S%.1f" % s_val)]["P_competitive"]

    return {
        "anchor_name": ANCHOR,
        "verdict": verdict,
        "verdict_msg": msg + (" | PRIMARY P = link-level pronoun accuracy on the COMPETITIVE "
                              "subset (>=2 gn-compatible candidates), pooled over both gold sets."),
        "run_mode": mode,
        "prereg": "preregs/2026-08-14_coref_cue_based_retrieval_actr_activation_v1.md",
        "prereg_commit": "1544d7e2a",
        "elapsed_s": time.time() - t0,
        "timeout_s": timeout_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "bands": BANDS,
        "actr_params": {"d_PINNED": ACTR_D, "W_not_pinned": ACTR_W, "S_not_pinned": ACTR_S},
        "datasets": {n: DATASETS[n] for n in ds_names},
        "P_competitive_by_arm": P,
        "pronoun_link_acc_by_arm": {a: pooled_arms[a]["pronoun_link_acc"] for a in all_arms},
        "b3_pronoun_f1_by_arm": {a: pooled_arms[a]["b3_pronoun_f1"] for a in all_arms},
        "n_competitive_decisions": pooled_arms["actr_parallel"]["n_competitive"],
        "n_pronoun_decisions": pooled_arms["actr_parallel"]["n_pronoun"],
        "n_passages": sum(len(data[n][0]) for n in ds_names),
        "discriminators": disc,
        "paired_bootstrap": boots,
        "sensitivity_S_NOT_headline_eligible": sens,
        "per_dataset": {n: {a: {k: v for k, v in units[unit_key(n, a)].items() if k != "per_passage"}
                            for a in all_arms} for n in ds_names},
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
