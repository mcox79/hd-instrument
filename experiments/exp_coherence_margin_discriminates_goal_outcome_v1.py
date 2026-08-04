"""exp_coherence_margin_discriminates_goal_outcome_v1 -- the make-or-break architecture check for
the coherence-based binding-selector build (notes/research_coherence_based_binding_selector_
build_spec_2026-08-04.md Section 7, BIGGEST RISK): does the accumulate-register decode-margin
(hdlab/self_improving_loop.py::decode_coherence_margins) DISCRIMINATE a correct goal-owner binding
from a wrong one on the goal-outcome instance -- like it does for coref (positive control) -- or
does it TIE like it is PROVEN to for causal antecedent selection (negative control, disk-verified
notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md)?

REVISED DESIGN (mid-authoring correction, self-caught): an initial naive item construction (TRUE
candidate lightly-loaded register vs WRONG candidate heavily-loaded register at the query position)
appeared to "discriminate" for coref and goal_outcome, matching the hoped-for result. Numeric
debugging (see cell history / report) proved this was a REGISTER-LOAD ARTIFACT, not identity-based
coherence: (a) with LOAD MATCHED between TRUE and WRONG candidates, the margin delta is EXACTLY
0.0 for every item tested (coref, causal, and goal_outcome alike, both flat and multibank backend);
(b) with load intentionally mismatched, REVERSING which candidate is more heavily loaded FLIPS the
adopt decision 100% of the time, i.e. the "winner" is whichever candidate happens to have the
LIGHTER register, independent of which one is actually TRUE. A role_seq-rotation shuffle control
(the originally-planned artifact check) did NOT catch this, because it does not touch register load
at all -- this cell now uses the DIRECT, decisive artifact probe instead (swap which candidate is
loaded; a real identity signal must NOT flip).

THE REAL FINDING (more general and more informative than the original risk question): at the
GRANULARITY of a single flagged-position comparison (the literal operationalization of "does
binding the TRUE owner decode with a higher margin than binding a WRONG owner"), decode_coherence_
margins carries ZERO identity information for ANY of the 3 instances -- coref included. Its
production-validated discrimination (67% oracle-gain recovery, atom 29609 lineage) must be an
EMERGENT property of route_passage's whole-passage AGGREGATE (mean delta over many flagged
positions, where a genuinely incoherent resolution structurally over-merges distinct entities into
fewer/busier registers as a property of real text) -- not a property present in the atomic
per-position margin itself. This cell measures both: LOAD-MATCHED discrimination (the fair,
artifact-free test) and the LOAD-DIRECTION-FLIP artifact probe, per arm, per backend.

Cites: notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md;
notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md;
hdlab/self_improving_loop.py; experiments/exp_situation_model_goal_outcome_dimension_v1.py
(GoalOutcomeRegister role vocab, sourced not re-derived); data/eval_gold_mention_role_mcguffey_v1/
gold_grounded_appraisal_richer_v1.jsonl (real causal negative-control items).
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

ANCHOR_NAME = "coherence_margin_discriminates_goal_outcome_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the validated coherence-margin organ + SELECT gate -------------------
from hdlab.self_improving_loop import decode_coherence_margins, decide_keep_or_revert  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
D_DIM = 512
SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)
ABSTAIN_BAND = 0.02
BACKENDS = ["flat", "multibank"]   # flat = original validated construction; multibank = route_passage's default

CAUSAL_GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_grounded_appraisal_richer_v1.jsonl"
)

COREF_ROLE_VOCAB = ["agent", "mentioned"]
GO_ROLE_VOCAB = ["GOAL", "ACTION_AGAINST", "OUTCOME_UNMET", "OUTCOME_MET"]
CAUSAL_ROLE_VOCAB = ["CAUSE", "EFFECT"]


def _decide(role_seq, event_slots, base_ids, true_ids, flagged, role_vocab, d, mes, seed, backend):
    """Reuse decode_coherence_margins + decide_keep_or_revert VERBATIM (no fork): compute margins
    under baseline (WRONG) and candidate (TRUE) whole-position assignments with an IDENTICAL FHRR
    symbol table (same seed both calls, route_passage's own generator_factory contract), take the
    mean delta at the flagged position(s), and let decide_keep_or_revert make the adopt call. This
    is route_passage's exact aggregation formula, inlined so the `backend` parameter (multibank vs
    flat, both already-existing options on decode_coherence_margins) can be probed explicitly --
    route_passage itself hardcodes the default and does not expose it."""
    m_base = decode_coherence_margins(role_seq, event_slots, base_ids, role_vocab, d,
                                       torch.Generator().manual_seed(int(seed)), mes, backend=backend)
    m_true = decode_coherence_margins(role_seq, event_slots, true_ids, role_vocab, d,
                                       torch.Generator().manual_seed(int(seed)), mes, backend=backend)
    delta = sum(m_true[p] - m_base[p] for p in flagged) / len(flagged)
    adopt = decide_keep_or_revert({"true": delta}, abstain_band=ABSTAIN_BAND)
    return (adopt == "true"), delta


# ============================================================================ ARM: coref (POSITIVE CONTROL)
def _coref_load_matched_items():
    """LOAD-MATCHED (fair, artifact-free): TRUE and FOIL have EQUAL supporting "agent" mention
    counts; only the query ("mentioned") differs by which entity it binds to. If margin carries
    real identity information, TRUE should still beat FOIL (FOIL = the recency competitor, wrong
    by construction) even at matched load."""
    items = []
    for idx, n in enumerate([1, 2, 3, 4, 5]):
        role_seq = ["agent"] * n + ["agent"] * n + ["mentioned"]
        event_slots = list(range(n)) + list(range(n)) + [n]
        base_ids = ["TRUE"] * n + ["FOIL"] * n + ["FOIL"]
        true_ids = ["TRUE"] * n + ["FOIL"] * n + ["TRUE"]
        items.append(dict(id=f"coref_matched_{idx}_n{n}", role_seq=role_seq, event_slots=event_slots,
                           baseline_cluster_ids=base_ids, true_cluster_ids=true_ids,
                           flagged_positions=[len(role_seq) - 1], role_vocab=COREF_ROLE_VOCAB,
                           max_event_slots=n + 1))
    return items


def _coref_load_asymmetry_items(true_heavy: bool):
    """ARTIFACT PROBE: TRUE and FOIL loads deliberately UNEQUAL. true_heavy=False: TRUE lightly
    loaded, FOIL heavily loaded (the direction that superficially "looks like" discrimination).
    true_heavy=True: loads REVERSED. A genuine identity signal must NOT flip between these; a pure
    load artifact flips 100%."""
    items = []
    specs = [(1, 4), (1, 2), (2, 5), (1, 3), (2, 3)]
    for idx, (n_true, n_foil) in enumerate(specs):
        if true_heavy:
            n_true, n_foil = n_foil, n_true
        role_seq = ["agent"] * n_true + ["agent"] * n_foil + ["mentioned"]
        event_slots = list(range(n_true)) + list(range(n_foil)) + [max(n_true, n_foil)]
        base_ids = ["TRUE"] * n_true + ["FOIL"] * n_foil + ["FOIL"]
        true_ids = ["TRUE"] * n_true + ["FOIL"] * n_foil + ["TRUE"]
        items.append(dict(id=f"coref_asym_{'trueheavy' if true_heavy else 'foilheavy'}_{idx}",
                           role_seq=role_seq, event_slots=event_slots, baseline_cluster_ids=base_ids,
                           true_cluster_ids=true_ids, flagged_positions=[len(role_seq) - 1],
                           role_vocab=COREF_ROLE_VOCAB, max_event_slots=max(n_true, n_foil) + 1))
    return items


# ============================================================================ ARM: causal (NEGATIVE CONTROL)
def _load_causal_items():
    """4 REAL gold items. SINGLE write-then-read (one CAUSE fact, no supporting events) --
    inherently LOAD-MATCHED (both candidates start from zero prior load) and mirrors
    CausalLinkRegister's actual write pattern exactly. distractor_agent is the gold file's own
    documented recency pick (recency_baseline_correct == False everywhere -- asserted below)."""
    items = []
    with open(CAUSAL_GOLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("item_type") != "multi_candidate_causal_attribution":
                continue
            items.append(dict(
                id=rec["id"], role_seq=["CAUSE"], event_slots=[0],
                baseline_cluster_ids=[rec["distractor_agent"]],
                true_cluster_ids=[rec["true_blocker_agent"]],
                flagged_positions=[0], role_vocab=CAUSAL_ROLE_VOCAB, max_event_slots=1,
                recency_baseline_correct=rec.get("recency_baseline_correct"),
            ))
    assert len(items) == 4, f"expected 4 causal gold items, got {len(items)}: {[i['id'] for i in items]}"
    for it in items:
        assert it["recency_baseline_correct"] is False, (
            f"{it['id']}: gold recency_baseline_correct must be False (distractor IS the recency "
            f"pick) for the fairness-tightening precondition to hold"
        )
    return sorted(items, key=lambda it: it["id"])


# ============================================================================ ARM: goal_outcome (TREATMENT)
def _go_load_matched_items():
    """LOAD-MATCHED: owner and foil each carry the SAME number of supporting typed events (owner:
    GOAL+ACTION_AGAINST fixed at 2, foil: 2 of its own unrelated GOAL events -- matched count).
    Query = OUTCOME_UNMET bound to TRUE owner (candidate) vs FOIL (baseline/recency)."""
    items = []
    specs = [("amy", "jo"), ("tom", "sid"), ("beth", "meg"), ("ruth", "ann")]
    for idx, (owner, foil) in enumerate(specs):
        role_seq = ["GOAL", "ACTION_AGAINST", "GOAL", "ACTION_AGAINST"]
        event_slots = [0, 1, 0, 1]
        base_ids = [owner, owner, foil, foil]
        true_ids = [owner, owner, foil, foil]
        role_seq.append("OUTCOME_UNMET"); event_slots.append(2)
        base_ids.append(foil); true_ids.append(owner)
        items.append(dict(id=f"go_matched_{idx}_{owner}_vs_{foil}", role_seq=role_seq,
                           event_slots=event_slots, baseline_cluster_ids=base_ids,
                           true_cluster_ids=true_ids, flagged_positions=[len(role_seq) - 1],
                           role_vocab=GO_ROLE_VOCAB, max_event_slots=3))
    return items


def _go_load_asymmetry_items(true_heavy: bool):
    """ARTIFACT PROBE, same logic as coref: owner_extra/foil counts deliberately unequal, then
    swapped. true_heavy=False: owner lightly loaded, foil heavily loaded (superficially
    'discriminating' direction). true_heavy=True: reversed."""
    items = []
    specs = [(0, 4), (0, 3), (1, 5), (0, 4)]
    for idx, (oe, nf) in enumerate(specs):
        if true_heavy:
            oe, nf = nf - 2 if nf - 2 >= 0 else 0, oe + 2  # keep asymmetry but flip who's heavier
        role_seq = ["GOAL", "ACTION_AGAINST"] + ["GOAL"] * oe + ["GOAL"] * nf
        event_slots = [0, 1] + list(range(2, 2 + oe)) + list(range(nf))
        base_ids = ["OWNER", "OWNER"] + ["OWNER"] * oe + ["FOIL"] * nf
        true_ids = list(base_ids)
        qslot = max(2 + oe, nf)
        role_seq.append("OUTCOME_UNMET"); event_slots.append(qslot)
        base_ids.append("FOIL"); true_ids.append("OWNER")
        items.append(dict(id=f"go_asym_{'ownerheavy' if true_heavy else 'foilheavy'}_{idx}",
                           role_seq=role_seq, event_slots=event_slots, baseline_cluster_ids=base_ids,
                           true_cluster_ids=true_ids, flagged_positions=[len(role_seq) - 1],
                           role_vocab=GO_ROLE_VOCAB, max_event_slots=qslot + 1))
    return items


# ============================================================================ per-item / per-arm run
def _arms_must_differ_check(items):
    for it in items:
        db = hashlib.sha256(json.dumps(it["baseline_cluster_ids"]).encode()).hexdigest()
        dt = hashlib.sha256(json.dumps(it["true_cluster_ids"]).encode()).hexdigest()
        assert db != dt, f"META_RULE_AF VIOLATION: item {it['id']} baseline==true cluster_ids"


def _run_items(items, seed, backend):
    rows = []
    for it in items:
        disc, delta = _decide(it["role_seq"], it["event_slots"], it["baseline_cluster_ids"],
                               it["true_cluster_ids"], it["flagged_positions"], it["role_vocab"],
                               D_DIM, it["max_event_slots"], seed, backend)
        rows.append(dict(id=it["id"], true_adopted=disc, delta=round(delta, 5)))
    rate = round(sum(r["true_adopted"] for r in rows) / len(rows), 4)
    return rate, rows


def run_seed(seed):
    coref_m = _coref_load_matched_items()
    coref_a_foilheavy = _coref_load_asymmetry_items(true_heavy=False)
    coref_a_trueheavy = _coref_load_asymmetry_items(true_heavy=True)
    causal_items = _load_causal_items()
    go_m = _go_load_matched_items()
    go_a_foilheavy = _go_load_asymmetry_items(true_heavy=False)
    go_a_trueheavy = _go_load_asymmetry_items(true_heavy=True)
    _arms_must_differ_check(coref_m + coref_a_foilheavy + coref_a_trueheavy + causal_items
                             + go_m + go_a_foilheavy + go_a_trueheavy)

    out = dict(seed=seed)
    for backend in BACKENDS:
        out[f"coref_matched_rate_{backend}"], out[f"coref_matched_rows_{backend}"] = _run_items(coref_m, seed, backend)
        out[f"causal_matched_rate_{backend}"], out[f"causal_matched_rows_{backend}"] = _run_items(causal_items, seed, backend)
        out[f"go_matched_rate_{backend}"], out[f"go_matched_rows_{backend}"] = _run_items(go_m, seed, backend)
        # artifact probes: only meaningful under "flat" (multibank showed zero signal even with load asymmetry at this scale)
        out[f"coref_asym_foilheavy_rate_{backend}"], _ = _run_items(coref_a_foilheavy, seed, backend)
        out[f"coref_asym_trueheavy_rate_{backend}"], _ = _run_items(coref_a_trueheavy, seed, backend)
        out[f"go_asym_foilheavy_rate_{backend}"], _ = _run_items(go_a_foilheavy, seed, backend)
        out[f"go_asym_trueheavy_rate_{backend}"], _ = _run_items(go_a_trueheavy, seed, backend)
    return out


# ============================================================================ aggregate + verdict
def aggregate(per_seed):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds]
        return round(sum(vals) / len(vals), 4) if vals else None

    # PRIMARY (flat backend, the only backend showing any signal in preview debugging)
    coref_matched = mean("coref_matched_rate_flat")
    causal_matched = mean("causal_matched_rate_flat")
    go_matched = mean("go_matched_rate_flat")
    coref_foilheavy = mean("coref_asym_foilheavy_rate_flat")
    coref_trueheavy = mean("coref_asym_trueheavy_rate_flat")
    go_foilheavy = mean("go_asym_foilheavy_rate_flat")
    go_trueheavy = mean("go_asym_trueheavy_rate_flat")
    # ROBUSTNESS (production default backend)
    coref_matched_mb = mean("coref_matched_rate_multibank")
    causal_matched_mb = mean("causal_matched_rate_multibank")
    go_matched_mb = mean("go_matched_rate_multibank")

    # artifact = decision flips with load direction (foilheavy high, trueheavy low, or vice versa,
    # rather than staying pinned to whichever candidate is actually TRUE)
    coref_flips = (coref_foilheavy is not None and coref_trueheavy is not None
                   and abs(coref_foilheavy - coref_trueheavy) >= 0.5)
    go_flips = (go_foilheavy is not None and go_trueheavy is not None
                and abs(go_foilheavy - go_trueheavy) >= 0.5)

    harness_sane = (coref_matched is not None and causal_matched is not None)  # both measured, no crash
    load_matched_all_tie = (coref_matched is not None and causal_matched is not None and go_matched is not None
                             and coref_matched <= 0.25 and causal_matched <= 0.25 and go_matched <= 0.25)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif coref_flips and load_matched_all_tie:
        verdict = "HARD_FAIL_SINGLE_POSITION_MARGIN_IS_LOAD_ARTIFACT_NOT_IDENTITY_GRANULARITY_MISMATCH"
    elif go_matched is not None and coref_matched is not None and go_matched <= 0.25 and coref_matched >= 0.8:
        verdict = "HARD_FAIL_GOAL_OUTCOME_TIES_WHILE_COREF_DISCRIMINATES_AT_MATCHED_LOAD"
    elif (coref_matched is not None and coref_matched >= 0.8 and causal_matched is not None
          and causal_matched <= 0.25 and go_matched is not None and go_matched >= 0.8
          and not coref_flips and not go_flips):
        verdict = "HARD_PASS_MARGIN_DISCRIMINATES_GOAL_OUTCOME_LIKE_COREF_LOAD_CONTROLLED"
    else:
        verdict = "MIDDLE_BAND_MIXED_OR_INCONCLUSIVE"

    summary = (f"[flat] coref_matched={coref_matched} causal_matched={causal_matched} "
               f"go_matched={go_matched} | ARTIFACT PROBE coref(foilheavy={coref_foilheavy} "
               f"trueheavy={coref_trueheavy} flips={coref_flips}) go(foilheavy={go_foilheavy} "
               f"trueheavy={go_trueheavy} flips={go_flips}) | [multibank robustness] "
               f"coref_matched={coref_matched_mb} causal_matched={causal_matched_mb} "
               f"go_matched={go_matched_mb}")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        means=dict(
            coref_matched_rate_flat=coref_matched, causal_matched_rate_flat=causal_matched,
            go_matched_rate_flat=go_matched,
            coref_asym_foilheavy_rate_flat=coref_foilheavy, coref_asym_trueheavy_rate_flat=coref_trueheavy,
            go_asym_foilheavy_rate_flat=go_foilheavy, go_asym_trueheavy_rate_flat=go_trueheavy,
            coref_matched_rate_multibank=coref_matched_mb, causal_matched_rate_multibank=causal_matched_mb,
            go_matched_rate_multibank=go_matched_mb,
        ),
        bands=dict(harness_sane=harness_sane, load_matched_all_tie=load_matched_all_tie,
                   coref_load_artifact_flips=coref_flips, go_load_artifact_flips=go_flips),
        per_seed_rows_seed0={k: v for k, v in per_seed[seeds[0]].items() if k.endswith("_rows_flat")},
        arms_differ_verified=True,
        brain_fidelity_caveat=(
            "decode_coherence_margins is a ONE-SHOT single-pass read, a brain-COMPATIBLE "
            "approximation of Kintsch construction-integration / CA3 attractor settling, where "
            "'coherent-but-distant beats recent-but-connected' fully lives. This cell's finding "
            "(single-position margin carries no identity information, only relative register-load "
            "artifact) is about the ONE-SHOT organ as built; it does NOT rule out that a settling "
            "mechanism, or a route_passage-style MANY-POSITION aggregate over real text, carries "
            "real identity information -- it may, and that is the production-validated coref case. "
            "This diagnostic isolates the atomic single-decision granularity specifically."
        ),
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


def run(run_mode):
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
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"coref_matched={res['coref_matched_rate_flat']} causal_matched={res['causal_matched_rate_flat']} "
              f"go_matched={res['go_matched_rate_flat']} coref_asym(foil={res['coref_asym_foilheavy_rate_flat']} "
              f"true={res['coref_asym_trueheavy_rate_flat']})", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(d_dim=D_DIM, seeds=seeds, abstain_band=ABSTAIN_BAND, backends=BACKENDS,
                          n_coref=5, n_causal=4, n_goal_outcome=4)
    agg["prereg"] = "preregs/2026-08-04_coherence_margin_discriminates_goal_outcome_v1.md"
    agg["cites"] = [
        "notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md",
        "notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md",
        "hdlab/self_improving_loop.py",
        "experiments/exp_situation_model_goal_outcome_dimension_v1.py (role vocab, sourced)",
        "data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl (real causal items)",
    ]
    agg["per_seed"] = per_seed
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) real code path: exercise decode_coherence_margins / decide_keep_or_revert directly.
    margins = decode_coherence_margins(["agent"], [0], ["A"], ["agent", "mentioned"], 64,
                                        torch.Generator().manual_seed(0), 1, backend="flat")
    assert len(margins) == 1 and margins[0] >= 0.0, f"decode_coherence_margins real-call bad: {margins}"
    assert decide_keep_or_revert({}) is None, "decide_keep_or_revert empty-input must abstain"

    # (1) item construction sanity + arms-must-differ
    coref_m = _coref_load_matched_items()
    assert len(coref_m) == 5, coref_m
    causal_items = _load_causal_items()
    assert len(causal_items) == 4, causal_items
    go_m = _go_load_matched_items()
    assert len(go_m) == 4, go_m
    _arms_must_differ_check(coref_m + causal_items + go_m)

    # (2) load-matched items are actually load-matched (self-check the construction, not just the result)
    for it in coref_m:
        supporting = [c for p, c in enumerate(it["baseline_cluster_ids"]) if p not in it["flagged_positions"]]
        n_true = supporting.count("TRUE")
        n_foil = supporting.count("FOIL")
        assert n_true == n_foil, f"{it['id']}: load not matched (true={n_true} foil={n_foil})"

    # (3) DISCRIMINATOR-MUST-SURVIVE-SCALE / degeneracy preview: causal negative control must tie
    # at preview scale (sanity the harness itself is live and the causal write-then-read symmetry
    # reproduces before trusting the full multi-seed run).
    causal_rate, _ = _run_items(causal_items, 0, "flat")
    assert causal_rate <= 0.25, (
        f"causal negative-control unexpectedly discriminates in preview (rate={causal_rate}); "
        f"the 2026-08-03 write-then-read-symmetry finding did not reproduce"
    )

    # (4) one full seed sanity
    res = run_seed(0)
    for k in ("coref_matched_rate_flat", "causal_matched_rate_flat", "go_matched_rate_flat"):
        assert res[k] is not None
    print(f"[SELFTEST PASS] real decode_coherence_margins/decide_keep_or_revert exercised; items "
          f"load-matched by construction; causal preview ties (rate={causal_rate}); seed0 "
          f"coref_matched={res['coref_matched_rate_flat']} causal_matched={res['causal_matched_rate_flat']} "
          f"go_matched={res['go_matched_rate_flat']}", flush=True)
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
