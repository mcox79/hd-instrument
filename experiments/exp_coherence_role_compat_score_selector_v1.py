"""exp_coherence_role_compat_score_selector_v1 -- MINIMAL role-compatibility SCORE selector for
role-content relational binding (goal-owner attribution), NOT iterative constraint-satisfaction
settling (Director refinement, folded into notes/research_coherence_constraint_satisfaction_
settling_selector_design_spec.md's Henry test: that test is SINGLE-PASS-SOLVABLE -- one
application of the role-compat table separates true owner from foil; the spec's own iterative
relaxation only adds winner-take-all sharpening, which decide_keep_or_revert already provides).
MECHANISM-CAPACITY probe, NOT a capability claim -- see SCOPE_LABEL below.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF; hash-test on the 4 item variants)
- final_metrics_atomicity: tmp_replace (single-shot; os.replace pattern)
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
- crlb_n/a: deterministic symbolic score, no decoded/noisy signal -- CRLB does not apply
- baseline_in_band n/a: substituted by the anti-recency-baseline-is-wrong-by-construction check
- discriminator survives scale: N/A (fixed small symbolic table, no scale axis)
- HARD_PASS strictly above floor (margin >= 1.0 for positive control, >> abstain_band=0.02)
- HP_SCOPE: role_compat arm only; positive_control arm exempt from the negative-discrimination gates
- cardinality_ok: EXPECTED_N_UNITS = 5 seeds (no sweep axis beyond seed)
- per-unit failure-class instrumentation: no bare except in per-seed loop
- calibration_check: default_ok_for_this_regime (w-table values are the SUPPLIED structure
  under test, not calibrated to any distribution)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg
- self-test constructs REAL hdlab.situation_model_accumulate.AccumulateRegister objects at
  tiny scale (real_code_path); role LABELS are read symbolically for scoring, NOT via decode()
  (that is the entire point -- decode()/cosine is what's already proven role-content-blind,
  data/exp_coherence_role_conflict_crosstalk_v1/metrics.json shuffled_reproduces=True)

THE MECHANISM (see notes/prereg_coherence_role_compat_score_selector_v1_2026-08-04.md for the
full pre-reg): for a GOAL_OWNER query at outcome-event E_out contested between two candidate
entities (true owner, foil), score(E) = sum over E's OTHER established (role-type) propositions
of a SUPPLIED symbolic w(role-type) lookup (no FHRR cosine, no event-count term, no vector
geometry anywhere). Established-proposition NODES are pulled from a real AccumulateRegister
(constructed + populated for real -- genuine situation-model reuse for node PROVENANCE) but the
SCORE reads role-type labels symbolically from the same construction data, not via decode().
SELECT: hdlab.self_improving_loop.decide_keep_or_revert, reused verbatim.

THE 4 ITEM VARIANTS (all built from the same Henry/old_gentleman 2-candidate frame):
  ORIGINAL (load-matched, Control 1): true owner established=[AGENT_OF_ATTEMPT,
    EXPERIENCER_OF_OUTCOME] (score=2.0), foil established=[AGENT_OF_UNRELATED,
    EXPERIENCER_OF_UNRELATED] (score=0.0). Node COUNT equal (2==2), only role-TYPE differs.
  ANTI_RECENCY (Control 3): same role-content, event-slot positions reordered so the foil's
    (score=0.0) props are nearest E_out (a recency-keyed baseline would pick the foil) -- the
    role-compat score must still pick Henry (position-invariant by construction).
  SCRAMBLE (Control 2, the decisive control): same item as ORIGINAL, w replaced by a fixed
    involution swap (W_SCRAMBLED) of the table's VALUES, node set/count/positions UNCHANGED.
    A genuine role-content mechanism must COLLAPSE (margin flips, wrong pick). If the margin
    survives unchanged, the "win" is a structural/count/position artifact (the
    shuffled_reproduces=True signature already caught twice this session under other machinery).
  POSITIVE_CONTROL: foil has ZERO established props (score=0.0 by construction, not by w
    lookup); true owner keeps score=2.0. Pipeline sanity gate before trusting any negative.

Not dispatched remote: LOCAL/CPU only (local_cpu_queue, or direct .venv invocation if paused),
<10s wall time expected (deterministic symbolic mechanism, no vector geometry, no sweep) --
exempt from Section 17 print-progress-flushing (timeout_s << 1800).
Self-test: python exp_coherence_role_compat_score_selector_v1.py --self-test
Smoke:     python exp_coherence_role_compat_score_selector_v1.py --smoke
Full:      python exp_coherence_role_compat_score_selector_v1.py --full
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "coherence_role_compat_score_selector_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL --------------------------------------------------------------------
from hdlab.self_improving_loop import decide_keep_or_revert  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)
ABSTAIN_BAND = 0.02
REG_D = 64  # tiny register dim; scoring never reads FHRR values, only add_event provenance

TRUE_OWNER = "Henry"
FOIL = "old_gentleman"

# Trabasso-taxonomy-derived combined role/event-type labels -- the supplied symbolic role_vocab.
ROLE_TYPES = [
    "AGENT_OF_ATTEMPT",         # entity is AGENT of an ATTEMPT event elsewhere
    "EXPERIENCER_OF_OUTCOME",   # entity is EXPERIENCER of an OUTCOME event elsewhere
    "AGENT_OF_UNRELATED",       # AGENT of an episode with NO causal link to E_out
    "EXPERIENCER_OF_UNRELATED",  # EXPERIENCER of an episode with NO causal link to E_out
]

# SUPPLIED w(GOAL_OWNER, role-type) table (spec Section 3 item 2): causal-chain adjacency
# (GOAL->ATTEMPT, GOAL->OUTCOME/REACTION) = +1; orthogonal (no causal link) = 0. No cosine, no
# event-count term, no vector geometry.
W_GOAL_OWNER = {
    "AGENT_OF_ATTEMPT": 1.0,
    "EXPERIENCER_OF_OUTCOME": 1.0,
    "AGENT_OF_UNRELATED": 0.0,
    "EXPERIENCER_OF_UNRELATED": 0.0,
}

# Control 2: fixed involution swap of the table's VALUES (node set/counts/positions UNCHANGED
# in the item construction -- only the SUPPLIED table's content is scrambled).
W_SCRAMBLED = {
    "AGENT_OF_ATTEMPT": 0.0,
    "EXPERIENCER_OF_OUTCOME": 0.0,
    "AGENT_OF_UNRELATED": 1.0,
    "EXPERIENCER_OF_UNRELATED": 1.0,
}

SCOPE_LABEL = (
    "MECHANISM-CAPACITY proof over SUPPLIED role-structure: the substrate can USE a supplied "
    "symbolic role-compatibility table to discriminate GOAL_OWNER role-content where "
    "decode_coherence_margins gave EXACTLY 0.0 (data/exp_coherence_role_conflict_crosstalk_v1/"
    "metrics.json). Does NOT prove iterative settling is needed (single-pass sufficed here), "
    "NOR that role-structure can be EARNED from raw text (supplied here, not learned). N=1 "
    "existence proof (one candidate-pair item family, 4 controlled variants, 5 seeds for "
    "determinism-robustness of the register-construction plumbing, not for statistical "
    "variance -- the score itself is deterministic given the supplied structure)."
)


# ============================================================================ item construction
def _build_item(event_slot_true: int, event_slot_foil: int, event_slot_out: int,
                 foil_established: bool = True) -> dict:
    """One item: TRUE_OWNER's established props = [AGENT_OF_ATTEMPT, EXPERIENCER_OF_OUTCOME]
    at (event_slot_true, event_slot_true+1); FOIL's established props = [AGENT_OF_UNRELATED,
    EXPERIENCER_OF_UNRELATED] at (event_slot_foil, event_slot_foil+1) unless foil_established
    is False (POSITIVE_CONTROL: foil gets zero established props). E_out is a separate event
    slot (event_slot_out) that neither entity's OTHER established props occupy -- score() never
    reads E_out's own slot, only the OTHER established (role, slot) facts.
    """
    established = {
        TRUE_OWNER: [
            ("AGENT_OF_ATTEMPT", event_slot_true),
            ("EXPERIENCER_OF_OUTCOME", event_slot_true + 1),
        ],
    }
    if foil_established:
        established[FOIL] = [
            ("AGENT_OF_UNRELATED", event_slot_foil),
            ("EXPERIENCER_OF_UNRELATED", event_slot_foil + 1),
        ]
    else:
        established[FOIL] = []
    return dict(
        established=established, event_slot_out=event_slot_out,
        event_slot_true=event_slot_true, event_slot_foil=event_slot_foil,
    )


def _load_match_assert(item: dict) -> None:
    """Control 1: established-node COUNT must be equal pre-scoring -- rules out load as the
    explanation for any margin (mirrors exp_coherence_role_conflict_crosstalk_v1.py ~line 164).
    Crashes (does not silently pass) on violation, per contract discipline."""
    n_true = len(item["established"][TRUE_OWNER])
    n_foil = len(item["established"][FOIL])
    assert n_true == n_foil, (
        f"LOAD MISMATCH true_owner={n_true} foil={n_foil} -- Control 1 load-match assertion "
        f"FAILED (item must have equal established-node counts, only role-TYPE may differ)"
    )


def _recency_baseline_pick(item: dict) -> str:
    """The implicit recency baseline this mechanism must overturn on ANTI_RECENCY: whichever
    entity's LAST established event_slot is nearest E_out wins (a purely positional heuristic,
    no role-content read at all)."""
    out = item["event_slot_out"]

    def last_dist(entity):
        slots = [s for _, s in item["established"][entity]]
        if not slots:
            return float("inf")
        return min(abs(out - s) for s in slots)

    d_true, d_foil = last_dist(TRUE_OWNER), last_dist(FOIL)
    return TRUE_OWNER if d_true < d_foil else FOIL


def _populate_register(item: dict, seed: int) -> AccumulateRegister:
    """REAL AccumulateRegister construction + population (genuine situation-model reuse for
    node PROVENANCE) -- role_vocab = the 4 Trabasso-taxonomy combined labels. add_event is
    called for real; the register is NOT decoded for scoring (decode()/cosine is the
    already-proven role-content-blind path this cell exists to route around)."""
    gen = torch.Generator().manual_seed(30260806 + seed)
    reg = AccumulateRegister(ROLE_TYPES, REG_D, gen, max_event_slots=256)
    for entity, props in item["established"].items():
        for role, slot in props:
            reg.add_event(entity, role, slot)
    return reg


def _role_compat_score(established_props: list, w_table: dict) -> float:
    """The genuinely-new SCORE fn: sum of w(role-type) over an entity's established props.
    Plain symbolic dict lookup + sum -- no FHRR cosine, no event-count term, no vector
    geometry anywhere."""
    return float(sum(w_table.get(role, 0.0) for role, _slot in established_props))


def _score_item(item: dict, w_table: dict) -> dict:
    score_true = _role_compat_score(item["established"][TRUE_OWNER], w_table)
    score_foil = _role_compat_score(item["established"][FOIL], w_table)
    margin = score_true - score_foil
    decision = decide_keep_or_revert({"role_compat": margin}, abstain_band=ABSTAIN_BAND)
    picks_true_owner = decision == "role_compat"
    return dict(score_true=score_true, score_foil=score_foil, margin=margin,
                decision=decision, picks_true_owner=picks_true_owner)


def _arms_must_differ_check(item_dicts: list) -> dict:
    """META_RULE_AF: the 4 item variants must not be byte-identical to each other."""
    digests = {}
    for name, d in item_dicts:
        b = json.dumps(d, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: items {a!r} and {b!r} bit-identical "
                f"(hash={digests[a]})"
            )
    return digests


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    # event-slot numbering reseeded per seed (robustness of the register-construction plumbing
    # across arbitrary slot indices; role-CONTENT assignment is fixed by design, the score
    # itself is deterministic given the supplied structure -- seeds test plumbing, not variance)
    g = torch.Generator().manual_seed(90210 + seed)
    base = int(torch.randint(0, 20, (1,), generator=g).item())

    item_orig = _build_item(event_slot_true=base, event_slot_foil=base + 10,
                             event_slot_out=base + 20, foil_established=True)
    _load_match_assert(item_orig)

    # ANTI_RECENCY: foil's established props placed NEAR E_out, true owner's placed FAR --
    # recency baseline would pick foil; role-compat score must still pick true owner.
    item_anti = _build_item(event_slot_true=base + 100, event_slot_foil=base + 21,
                             event_slot_out=base + 20, foil_established=True)
    _load_match_assert(item_anti)
    assert _recency_baseline_pick(item_anti) == FOIL, (
        "ANTI_RECENCY construction bug: recency baseline does not actually favor the foil here "
        "-- the control is vacuous unless the recency baseline is independently wrong"
    )

    item_pos_control = _build_item(event_slot_true=base, event_slot_foil=base + 10,
                                    event_slot_out=base + 20, foil_established=False)

    # provenance: real AccumulateRegister constructed + populated for each item (not decoded)
    for it in (item_orig, item_anti, item_pos_control):
        _populate_register(it, seed)

    _arms_must_differ_check([
        ("orig", item_orig), ("anti_recency", item_anti), ("positive_control", item_pos_control),
    ])

    r_orig = _score_item(item_orig, W_GOAL_OWNER)
    r_anti = _score_item(item_anti, W_GOAL_OWNER)
    r_scramble = _score_item(item_orig, W_SCRAMBLED)  # Control 2: same item, scrambled table
    r_pos = _score_item(item_pos_control, W_GOAL_OWNER)

    return dict(
        seed=seed,
        orig_margin=r_orig["margin"], orig_picks_true_owner=r_orig["picks_true_owner"],
        anti_recency_margin=r_anti["margin"],
        anti_recency_picks_true_owner=r_anti["picks_true_owner"],
        scramble_margin=r_scramble["margin"],
        scramble_picks_true_owner=r_scramble["picks_true_owner"],
        positive_control_margin=r_pos["margin"],
        positive_control_picks_true_owner=r_pos["picks_true_owner"],
        load_match_assertion_held=True,  # crashed above otherwise, never silently passed
        recency_baseline_wrong_on_anti_recency=True,  # asserted above
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds]
        return round(sum(vals) / len(vals), 6) if vals else None

    def all_true(key):
        return all(per_seed[s][key] for s in seeds)

    orig_all = all_true("orig_picks_true_owner")
    anti_all = all_true("anti_recency_picks_true_owner")
    scramble_collapses_all = all(not per_seed[s]["scramble_picks_true_owner"] for s in seeds)
    scramble_reproduces_any = any(per_seed[s]["scramble_picks_true_owner"] for s in seeds)
    positive_fires_all = all(
        per_seed[s]["positive_control_picks_true_owner"]
        and per_seed[s]["positive_control_margin"] >= 1.0
        for s in seeds
    )

    orig_margin_mean = mean("orig_margin")
    anti_margin_mean = mean("anti_recency_margin")
    scramble_margin_mean = mean("scramble_margin")
    pos_margin_mean = mean("positive_control_margin")

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif not positive_fires_all:
        verdict = "HARNESS_DEAD_POSITIVE_CONTROL_FAILED"
    elif not (orig_all and anti_all):
        verdict = "HARD_FAIL_DOES_NOT_DISCRIMINATE_UNDER_LOADMATCH_OR_ANTIRECENCY"
    elif scramble_reproduces_any:
        verdict = "HARD_FAIL_ROLE_TABLE_SCRAMBLE_REPRODUCES_ARTIFACT_NOT_CONTENT"
    elif orig_all and anti_all and scramble_collapses_all and positive_fires_all:
        verdict = "HARD_PASS_ROLE_COMPAT_SCORE_MECHANISM_CAPACITY_EXISTENCE_PROOF_N1"
    else:
        verdict = "MIDDLE_BAND_N1_INCONCLUSIVE"

    summary = (
        f"SCOPE=[{SCOPE_LABEL}] || "
        f"ORIG(load-matched) picks_true_owner_all_seeds={orig_all} margin_mean={orig_margin_mean} | "
        f"ANTI_RECENCY picks_true_owner_all_seeds={anti_all} margin_mean={anti_margin_mean} | "
        f"CONTROL2_SCRAMBLE collapses_all_seeds={scramble_collapses_all} "
        f"reproduces_any={scramble_reproduces_any} margin_mean={scramble_margin_mean} | "
        f"POSITIVE_CONTROL fires_all_seeds={positive_fires_all} margin_mean={pos_margin_mean}"
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        scope_label=SCOPE_LABEL,
        means=dict(orig_margin=orig_margin_mean, anti_recency_margin=anti_margin_mean,
                   scramble_margin=scramble_margin_mean, positive_control_margin=pos_margin_mean),
        bands=dict(
            orig_picks_true_owner_all_seeds=orig_all,
            anti_recency_picks_true_owner_all_seeds=anti_all,
            scramble_collapses_all_seeds=scramble_collapses_all,
            scramble_reproduces_any=scramble_reproduces_any,
            positive_control_fires_all_seeds=positive_fires_all,
        ),
        load_match_assertion_held=True,
        settling_deferred_note=(
            "Iterative constraint-satisfaction settling explicitly NOT built -- Director "
            "refinement: this item is single-pass-solvable (one score application separates "
            "true owner from foil); the spec's relaxation loop only adds winner-take-all "
            "sharpening, already provided by decide_keep_or_revert's abstain gate. A future "
            "globally-coherent-but-locally-ambiguous case that single-pass cannot solve would "
            "justify building the loop next -- not testable at this N=1 scope."
        ),
        per_seed=per_seed,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    _write_json(os.path.join(output_dir, "metrics.json"), diag)


def run(run_mode: str) -> dict:
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    _write_json(os.path.join(out_dir, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS})

    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.3f}s "
              f"orig_margin={res['orig_margin']} anti_margin={res['anti_recency_margin']} "
              f"scramble_margin={res['scramble_margin']} pos_margin={res['positive_control_margin']}",
              flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        seeds=seeds, abstain_band=ABSTAIN_BAND, role_types=ROLE_TYPES,
        w_goal_owner=W_GOAL_OWNER, w_scrambled=W_SCRAMBLED, reg_d=REG_D,
    )
    agg["prereg"] = "notes/prereg_coherence_role_compat_score_selector_v1_2026-08-04.md"
    agg["design_spec"] = (
        "notes/research_coherence_constraint_satisfaction_settling_selector_design_spec.md "
        "(commit 70eb5d817) WITH Director single-pass refinement (minimal score, no settling loop)"
    )
    agg["cites"] = [
        "hdlab/self_improving_loop.py (decide_keep_or_revert, reused verbatim)",
        "hdlab/situation_model_accumulate.py (AccumulateRegister, constructed+populated for "
        "real -- node provenance; role labels read symbolically for scoring, NOT via decode())",
        "experiments/exp_coherence_role_conflict_crosstalk_v1.py (load-match assertion pattern "
        "reused; the shuffled_reproduces=True artifact signature this cell's Control 2 is "
        "designed to catch)",
        "notes/research_coherence_constraint_satisfaction_settling_selector_design_spec.md "
        "(commit 70eb5d817, the w-table design + 3 mandatory controls)",
    ]
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.3f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) real code path: decide_keep_or_revert exercised directly
    assert decide_keep_or_revert({"a": 0.5}, abstain_band=0.02) == "a"
    assert decide_keep_or_revert({"a": 0.01}, abstain_band=0.02) is None
    assert decide_keep_or_revert({}, abstain_band=0.02) is None

    # (1) real AccumulateRegister construction + population + decode (real object, real calls;
    # exercised here ONLY to prove the register plumbing works -- the cell's own SCORE never
    # calls decode(), by design)
    gen = torch.Generator().manual_seed(1)
    reg = AccumulateRegister(ROLE_TYPES, 16, gen, max_event_slots=8)
    reg.add_event("X", "AGENT_OF_ATTEMPT", 0)
    reg.add_event("X", "EXPERIENCER_OF_OUTCOME", 1)
    role, _scores = reg.decode("X", 0)
    assert role == "AGENT_OF_ATTEMPT", f"AccumulateRegister real decode() sanity failed: {role}"

    # (2) item construction: load-match holds, node counts equal
    item = _build_item(event_slot_true=0, event_slot_foil=10, event_slot_out=20)
    _load_match_assert(item)
    assert len(item["established"][TRUE_OWNER]) == 2
    assert len(item["established"][FOIL]) == 2

    # (3) positive control: foil has zero established props by construction
    item_pos = _build_item(event_slot_true=0, event_slot_foil=10, event_slot_out=20,
                            foil_established=False)
    assert item_pos["established"][FOIL] == []

    # (4) role-compat score: true owner beats foil under W_GOAL_OWNER, ties/loses under W_SCRAMBLED
    r_orig = _score_item(item, W_GOAL_OWNER)
    assert r_orig["margin"] == 2.0, f"expected margin=2.0, got {r_orig['margin']}"
    assert r_orig["picks_true_owner"] is True
    r_scr = _score_item(item, W_SCRAMBLED)
    assert r_scr["margin"] == -2.0, f"expected scrambled margin=-2.0, got {r_scr['margin']}"
    assert r_scr["picks_true_owner"] is False

    # (5) anti-recency: recency baseline must independently be wrong on the constructed item
    item_anti = _build_item(event_slot_true=100, event_slot_foil=21, event_slot_out=20)
    assert _recency_baseline_pick(item_anti) == FOIL
    r_anti = _score_item(item_anti, W_GOAL_OWNER)
    assert r_anti["picks_true_owner"] is True, "role-compat score failed to overturn recency"

    # (6) arms-must-differ real exercise
    _arms_must_differ_check([("orig", item), ("pos", item_pos), ("anti", item_anti)])

    # (7) one full seed sanity (all pieces run to completion)
    res = run_seed(0)
    for k in ("orig_margin", "anti_recency_margin", "scramble_margin", "positive_control_margin"):
        assert res[k] is not None, f"{k} missing"
    assert res["orig_picks_true_owner"] is True
    assert res["anti_recency_picks_true_owner"] is True
    assert res["scramble_picks_true_owner"] is False
    assert res["positive_control_picks_true_owner"] is True

    print(f"[SELFTEST PASS] orig_margin={r_orig['margin']} scrambled_margin={r_scr['margin']} "
          f"anti_recency_picks_true_owner={r_anti['picks_true_owner']} "
          f"seed0_orig_margin={res['orig_margin']} seed0_scramble_margin={res['scramble_margin']}",
          flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        if args.smoke:
            run("smoke")
            raise SystemExit(0)
        run("full")
        raise SystemExit(0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise


if __name__ == "__main__":
    main()
