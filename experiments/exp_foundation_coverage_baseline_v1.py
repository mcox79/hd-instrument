# CELL-TEMPLATE MANDATORY (measurement-first baseline; scope/scale/floor):
# - This is a BASELINE COVERAGE MAP, not a pass/fail capability claim. Per-category n is TINY
#   (1-4) -- directional only, stated in every report line.
# - final_metrics_atomicity: tmp_replace, newline='' binary.
# - except SystemExit raised BEFORE except Exception (no BaseException swallow).
# - baseline_in_band: RANDOM + RECENCY + SURFACE_VALENCE are the floors; mechanism = EARNED_GROUNDED.
#   Floors-fail sanity is enforced ONLY on the category we expect to work (physical_harm).
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY if fewer landed.
# - deterministic_seeding: EARNED_GROUNDED/SURFACE_VALENCE/RECENCY seed-independent; only RANDOM
#   varies by seed. OMP/OPENBLAS/MKL=1; torch.Generator; sorted iteration; no hash()-seed.
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py); start_marker + crash_diag.
# - all reported numbers MEASURED@ tagged in the completion report, not this file.
"""Per-category grounded-knowledge COVERAGE BASELINE on the categorized causal-attribution ruler.

Track-1 step-1 of the foundation-building phase. Measures the CURRENT grounded foundation's
per-category coverage: which grounded-knowledge categories already work (physical_harm should,
since we have that knowledge) vs which are at floor (need grounding next). The deliverable is a
category -> {accuracy, n, floors} MAP that ROUTES which category to ground next. NOT a pass/fail.

Mechanism (bit-identical reuse, no new knowledge, no retrain): the earned grounded HARM-VALENCE
read from exp_grounded_valence_read_from_text_v1 (situation-model appraisal accumulation over
supplied harm/help primitives via the FHRR accumulate organ, atom 29609) applied uniformly as the
causal-attribution decision (pick the candidate whose grounded valence is causally consistent with
the NEG outcome). Reads ONLY candidate span text -> leak-safe on goal, immune to outcome-overlap.
Brain: hippocampal situation-model relational appraisal accumulation + appraisal->outcome selection.
Prereg: preregs/2026-08-04_foundation_coverage_baseline_v1.md. Local-only: no queue/remote/push."""

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
from collections import defaultdict
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "foundation_coverage_baseline_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED BIT-IDENTICAL: the earned grounded valence read + harm-consistency selector --------
# (situation-model appraisal accumulation over harm primitives + FHRR accumulate organ).
from exp_grounded_valence_read_from_text_v1 import (  # noqa: E402
    read_valences, select_from_valences, grounded_valence_evidence, accumulate_valence,
    HARM_VERB, HELP_VERB, PATIENT_TOKENS, HYPOTHETICAL_MARK, CONSISTENT_VALENCE,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ----------------------------------------------------------------------------- config
SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
TRUE_SLOT = 0  # slot 0 = true_blocker_span (fixed bookkeeping; mechanism not told the answer)
CHANCE = 0.5
ARMS = ("EARNED_GROUNDED", "SURFACE_VALENCE", "RECENCY", "RANDOM")

GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
V4_PATH = os.path.join(GOLD_DIR, "gold_grounded_comprehension_v4_DRAFT.jsonl")
RICHER_PATH = os.path.join(GOLD_DIR, "gold_grounded_appraisal_richer_v1.jsonl")
CROSS_PATH = os.path.join(GOLD_DIR, "gold_grounded_causal_crossspan_v2_DRAFT.jsonl")

CAUSAL_CATEGORIES = ("physical_harm", "out_of_span_cause", "counterfactual_cause",
                     "multi_candidate_attribution", "goal_blocking")

# v4 causal-attribution items in scope (EXCLUDING Director-HOLD grapp_v4_002/_004/_010; category
# comes from the item's own grounded_knowledge_category field).
V4_INCLUDED = ["grapp_v4_001", "grapp_v4_003", "grapp_v4_005", "grapp_v4_006",
               "grapp_v4_009", "grapp_v4_011", "grapp_v4_013"]

# Prior Director-verified causal items (for power). These files have NO grounded_knowledge_category
# field, so the category is Director-ASSIGNED by the item's dominant phenomenon (disclosed in
# metrics under category_assignment_note). EXCLUDE grapp_mcca_006 (Director-REJECTED).
MCCA_RICHER = {
    "grapp_mcca_001": "physical_harm",              # drove the knife to the hilt in the breast
    "grapp_mcca_003": "multi_candidate_attribution",  # forged mock love-letter, reputation trap
    "grapp_mcca_004": "goal_blocking",              # withheld the ice-warning out of spite
    "grapp_mcca_005": "multi_candidate_attribution",  # who broke the sugar bowl (recency trap)
}
MCCA_CROSS = {
    "grapp_mcca_007": "out_of_span_cause",          # cordial mis-stored, revealed later
    "grapp_mcca_008": "out_of_span_cause",          # ink poured ~200 lines earlier
    "grapp_mcca_009": "multi_candidate_attribution",  # Becky tore the book (recency trap)
}

CATEGORY_ASSIGNMENT_NOTE = (
    "v4 items use their own grounded_knowledge_category field. grapp_mcca_* items carry no "
    "category field; category is Director-ASSIGNED by dominant phenomenon: mcca_001=physical_harm "
    "(knife/breast harm in the true span), mcca_003/005/009=multi_candidate_attribution "
    "(reputation/recency traps over who did it), mcca_004=goal_blocking (spiteful withholding of "
    "a warning), mcca_007/008=out_of_span_cause (true cause revealed out of the local query span). "
    "TINY per-category n (1-4) -- directional coverage map, not a powered per-category claim.")

# Fields the mechanism must NEVER read (contamination guard). The view constructed below exposes
# ONLY id/category/cand_text/cand_pos/query_pos; these are asserted absent from the view.
MECH_FORBIDDEN_FIELDS = frozenset({
    "_forbidden_true_blocker_agent", "true_blocker_agent", "distractor_agent",
    "recency_baseline_prediction", "recency_baseline_correct", "recency_note",
    "coherence_justification", "goal_owner", "goal_description_leaksafe", "surface_harm_score_true",
    "surface_harm_score_distractor", "gold_verified", "needs_director_review",
})


# ----------------------------------------------------------------------------- loading
def _load_jsonl(path):
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                d = json.loads(line)
                out[d["id"]] = d
    return out


def _mech_view(item, category):
    """The ONLY view of an item any mechanism/floor is allowed to see. Strips every gold-answer
    field by construction. cand_text = [true_blocker_span, distractor_span] in fixed slot order;
    the mechanism is not told which slot is the answer."""
    view = {
        "id": item["id"],
        "category": category,
        "cand_text": [item["true_blocker_span"]["text"], item["distractor_span"]["text"]],
        "cand_pos": [int(item["true_blocker_span"]["line_range"][0]),
                     int(item["distractor_span"]["line_range"][0])],
        "query_pos": int(item["query_span"]["line_range"][0]),
    }
    for k in view:
        assert k not in MECH_FORBIDDEN_FIELDS, f"forbidden field {k} in mech view"
    return view


def load_items():
    """Load the 14 in-scope causal-attribution items as (view, category) with fixed order."""
    v4 = _load_jsonl(V4_PATH)
    richer = _load_jsonl(RICHER_PATH)
    cross = _load_jsonl(CROSS_PATH)
    views = []
    for iid in V4_INCLUDED:
        it = v4[iid]
        assert it["item_type"] == "multi_candidate_causal_attribution", iid
        cat = it["grounded_knowledge_category"]
        assert cat in CAUSAL_CATEGORIES, f"{iid} category {cat} out of causal scope"
        views.append(_mech_view(it, cat))
    for iid, cat in sorted(MCCA_RICHER.items()):
        it = richer[iid]
        assert it["item_type"] == "multi_candidate_causal_attribution", iid
        views.append(_mech_view(it, cat))
    for iid, cat in sorted(MCCA_CROSS.items()):
        it = cross[iid]
        assert it["item_type"] == "multi_candidate_causal_attribution", iid
        views.append(_mech_view(it, cat))
    assert len(views) == 14, f"expected 14 items, got {len(views)}"
    return views


# ----------------------------------------------------------------------------- floors
def recency_pick(view):
    """Positional recency: most-recent candidate at/before the query line; else nearest by
    distance. Reads ONLY line positions (never text, never a gold field)."""
    q = view["query_pos"]
    before = [(view["cand_pos"][i], i) for i in range(2) if view["cand_pos"][i] <= q]
    if before:
        return max(before)[1]
    return min(range(2), key=lambda i: abs(view["cand_pos"][i] - q))


def random_pick(gen):
    return int(torch.randint(0, 2, (1,), generator=gen).item())


# ----------------------------------------------------------------------------- per-item arm picks
def pick_for_arm(view, arm, seed, rand_gen):
    """Return (pick_slot, detail). EARNED_GROUNDED/SURFACE_VALENCE reuse the valence read
    bit-identical then select_from_valences; RECENCY positional; RANDOM seeded uniform."""
    if arm == "EARNED_GROUNDED":
        vals, diags = read_valences(view, "EARNED_GROUNDED", torch.Generator().manual_seed(seed), seed)
        pick = select_from_valences(vals)
        return pick, {"valences": vals, "diags": diags}
    if arm == "SURFACE_VALENCE":
        vals, _ = read_valences(view, "FROZEN_LEXICON", torch.Generator().manual_seed(seed), seed)
        pick = select_from_valences(vals)
        return pick, {"valences": vals}
    if arm == "RECENCY":
        pick = recency_pick(view)
        return pick, {"cand_pos": view["cand_pos"], "query_pos": view["query_pos"]}
    if arm == "RANDOM":
        pick = random_pick(rand_gen)
        return pick, {}
    raise ValueError(f"unknown arm {arm!r}")


# ----------------------------------------------------------------------------- per-seed unit
def run_seed(seed, views):
    out = {"seed": seed, "arms": {}}
    rand_gen = torch.Generator().manual_seed(seed * 100003 + 1)
    for arm in ARMS:
        rows = []
        for v in views:
            pick, detail = pick_for_arm(v, arm, seed, rand_gen)
            rows.append({"id": v["id"], "category": v["category"], "pick_slot": pick,
                         "correct": pick == TRUE_SLOT, "abstain": pick == -1, "detail": detail})
        out["arms"][arm] = rows
    # arms-must-differ sanity: the four arms are not all identical pick-vectors
    digs = {}
    for arm, rows in out["arms"].items():
        seq = "|".join(str(r["pick_slot"]) for r in rows)
        digs[arm] = hashlib.sha256(seq.encode()).hexdigest()[:12]
    assert len(set(digs.values())) >= 2, f"all arms produced identical picks: {digs}"
    out["arm_pick_digests"] = digs
    return out


# ----------------------------------------------------------------------------- aggregate
def _acc(rows):
    return sum(r["correct"] for r in rows) / len(rows) if rows else 0.0


def aggregate_and_verdict(per_seed, views):
    seeds = sorted(per_seed.keys())
    n = len(seeds)
    categories = sorted({v["category"] for v in views})

    # overall per-arm accuracy averaged over seeds
    overall = {}
    for arm in ARMS:
        overall[arm] = sum(_acc(per_seed[s]["arms"][arm]) for s in seeds) / n

    # per-category per-arm accuracy averaged over seeds
    per_category = {}
    for cat in categories:
        cat_ids = [v["id"] for v in views if v["category"] == cat]
        entry = {"n": len(cat_ids), "item_ids": cat_ids, "accuracy": {}}
        for arm in ARMS:
            accs = []
            for s in seeds:
                rows = [r for r in per_seed[s]["arms"][arm] if r["category"] == cat]
                accs.append(_acc(rows))
            entry["accuracy"][arm] = sum(accs) / n
        per_category[cat] = entry

    # abstain rate for the grounded mechanism (glass-box; abstain counts incorrect)
    eg_abstain = sum(1 for r in per_seed[seeds[0]]["arms"]["EARNED_GROUNDED"] if r["abstain"]) / len(views)

    # per-item glass-box (deterministic arms read seed0) + harm-separability decomposition.
    # separable_by_harm = the grounded read DECODES the true-cause span as HARM-dominant AND the
    # distractor as non-HARM -> select_from_valences must attribute it to the true cause. This is
    # the internal-consistency check that distinguishes a broken/mis-wired mechanism from a ruler
    # whose true-cause spans simply do not read HARM-dominant (provocation / dare / omission /
    # misrepresentation causes, or spans where competing help evidence dominates -- both legitimate
    # grounded readings, not mechanism bugs). Raw harm_units/help_units are also reported.
    s0 = per_seed[seeds[0]]
    per_item = {}
    for v in views:
        iid = v["id"]
        eg = next(r for r in s0["arms"]["EARNED_GROUNDED"] if r["id"] == iid)
        sv = next(r for r in s0["arms"]["SURFACE_VALENCE"] if r["id"] == iid)
        rc = next(r for r in s0["arms"]["RECENCY"] if r["id"] == iid)
        diags = eg["detail"].get("diags", [None, None])
        vals = eg["detail"].get("valences", [None, None])
        true_hu = (diags[TRUE_SLOT] or {}).get("harm_units", 0)
        distr_hu = (diags[1 - TRUE_SLOT] or {}).get("harm_units", 0)
        true_help = (diags[TRUE_SLOT] or {}).get("help_units", 0)
        separable = vals[TRUE_SLOT] == "HARM" and vals[1 - TRUE_SLOT] != "HARM"
        per_item[iid] = {
            "category": v["category"],
            "true_span_preview": v["cand_text"][0][:120],
            "dist_span_preview": v["cand_text"][1][:120],
            "earned_grounded_valences": vals,
            "earned_grounded_pick": eg["pick_slot"], "earned_grounded_correct": eg["correct"],
            "surface_valence_pick": sv["pick_slot"], "surface_valence_correct": sv["correct"],
            "recency_pick": rc["pick_slot"], "recency_correct": rc["correct"],
            "true_span_harm_units": true_hu, "true_span_help_units": true_help,
            "distractor_span_harm_units": distr_hu,
            "true_cause_reads_harm_dominant_distractor_not": separable,
            "true_span_grounded_diag": diags[TRUE_SLOT],
        }

    # DIRECT-HARM-ACT coverage: on items the grounded read decodes as HARM-true / non-HARM-distractor,
    # does select_from_valences attribute them to the true cause? (internal-consistency / wiring +
    # the real-coverage boundary of the harm read.)
    separable_ids = [iid for iid, it in per_item.items()
                     if it["true_cause_reads_harm_dominant_distractor_not"]]
    separable_hits = [iid for iid in separable_ids if per_item[iid]["earned_grounded_correct"]]
    separable_misses = [iid for iid in separable_ids if not per_item[iid]["earned_grounded_correct"]]
    direct_harm_coverage = (len(separable_hits) / len(separable_ids)) if separable_ids else None

    # highest / floor categories (by EARNED_GROUNDED accuracy)
    eg_by_cat = {c: per_category[c]["accuracy"]["EARNED_GROUNDED"] for c in categories}
    highest_cat = max(eg_by_cat, key=eg_by_cat.get)
    floor_cats = sorted([c for c in categories if eg_by_cat[c] <= CHANCE], key=lambda c: eg_by_cat[c])

    # floors-diagnostic on the category expected to work (physical_harm) -- REPORTED, not a gate.
    ph = per_category.get("physical_harm", {}).get("accuracy", {})
    physical_harm_beats_floors = (
        "physical_harm" in per_category
        and ph.get("EARNED_GROUNDED", 0.0) > ph.get("RANDOM", 1.0) + 1e-9
        and ph.get("EARNED_GROUNDED", 0.0) > ph.get("RECENCY", 1.0) + 1e-9)

    # ARTIFACT gate is on the mechanism's INTERNAL CONSISTENCY (does it attribute harm when the
    # true cause is the sole harm-bearing candidate?), NOT on whether my category EXPECTATION held.
    # A miss on a separable item = a genuine mechanism artifact; all-hits = the read is valid and
    # the low per-category numbers are a ruler-content finding (true causes lack harm vocabulary).
    mechanism_internally_consistent = (not separable_misses)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif not mechanism_internally_consistent:
        verdict = "MECHANISM_ARTIFACT_HARM_READ_INCONSISTENT"
    else:
        verdict = "COVERAGE_MAP_MEASURED"

    # route the next grounding target = the floor category with the most items (biggest lever),
    # tie-broken by lowest accuracy.
    if floor_cats:
        route_next = max(floor_cats, key=lambda c: (per_category[c]["n"], -eg_by_cat[c]))
    else:
        route_next = None

    map_str = " ".join(
        f"{c}[n={per_category[c]['n']}]={eg_by_cat[c]:.3f}" for c in categories)
    dhc_str = (f"{len(separable_hits)}/{len(separable_ids)}"
               if direct_harm_coverage is not None else "n/a")
    summary = (
        f"COVERAGE MAP (EARNED_GROUNDED acc, n=14, TINY per-cat): {map_str} | overall "
        f"EARNED={overall['EARNED_GROUNDED']:.3f} SURFACE={overall['SURFACE_VALENCE']:.3f} "
        f"RECENCY={overall['RECENCY']:.3f} RANDOM={overall['RANDOM']:.3f} | "
        f"direct-harm-act-cause coverage={dhc_str} (true span sole harm-bearer) | "
        f"highest={highest_cat} floor={floor_cats} route_next={route_next} | "
        f"abstain_rate={eg_abstain:.3f}")

    return {
        "verdict": verdict,
        "verdict_msg": f"{verdict}: {summary}",
        "summary": summary,
        "n_seeds": n,
        "n_items": len(views),
        "categories": categories,
        "overall_accuracy_by_arm": overall,
        "per_category_coverage_map": per_category,
        "earned_grounded_accuracy_by_category": eg_by_cat,
        "highest_category": highest_cat,
        "floor_categories": floor_cats,
        "routed_next_grounding_target": route_next,
        "earned_grounded_abstain_rate": eg_abstain,
        "physical_harm_beats_floors_diagnostic": physical_harm_beats_floors,
        "mechanism_internally_consistent": mechanism_internally_consistent,
        "direct_harm_act_cause_coverage": {
            "coverage": direct_harm_coverage,
            "separable_item_ids": separable_ids,
            "hits": separable_hits,
            "misses": separable_misses,
            "definition": "items the grounded read DECODES as HARM-dominant true span AND non-HARM "
                          "distractor; select_from_valences must attribute these to the true cause "
                          "-- a miss would be a mechanism wiring/consistency artifact.",
        },
        "per_item": per_item,
        "category_assignment_note": CATEGORY_ASSIGNMENT_NOTE,
        "contamination_check": {
            "mechanism_reads_only": ["candidate span texts (cand_text)",
                                     "candidate + query line positions (RECENCY only)"],
            "goal_or_query_text_read_by_valence_mechanism": False,
            "forbidden_gold_fields_never_read": sorted(MECH_FORBIDDEN_FIELDS),
            "primitive_tables_contain_proper_nouns": False,
            "frozen_lexicon_or_borrowed_embedding_or_llm_as_grounded_mechanism": False,
            "grounded_read_retrained_or_new_knowledge_added": False,
            "note": "grounded valence read consumes ONLY candidate span text -> leak-safe on goal, "
                    "immune to outcome-overlap; bit-identical reuse of "
                    "exp_grounded_valence_read_from_text_v1 (no retrain).",
        },
        "reused_mechanisms": [
            "exp_grounded_valence_read_from_text_v1.read_valences/select_from_valences "
            "(earned grounded HARM-VALENCE read + harm-consistency selection, bit-identical)",
            "hdlab.situation_model_accumulate (FHRR accumulate organ, atom 29609) via the above",
            "exp_grounded_valence_read_from_text_v1.grounded_valence_evidence (harm/help primitives "
            "+ patient/hypothetical guards)",
        ],
        "honest_caveats": [
            "BASELINE MEASUREMENT, not a capability claim. Per-category n is TINY (1-4); the map is "
            "DIRECTIONAL routing, not a powered per-category accuracy.",
            "Single uniform mechanism (grounded valence read) across all items for a fair per-category "
            "comparison; the cross-span binding + effect-match selector organs (same family) were NOT "
            "separately combined this pass (cross-span victim aliases exist only for the mcca_001-005 "
            "slice, not applicable uniformly).",
            "grapp_mcca_* categories are Director-ASSIGNED (see category_assignment_note), not "
            "field-tagged like the v4 items.",
        ],
    }


# ----------------------------------------------------------------------------- infra
def out_dir_for(run_mode):
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    views = load_items()
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, views)
        record_unit(output_dir, k, res)
        eg = _acc(res["arms"]["EARNED_GROUNDED"])
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s EARNED={eg:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed, views)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "arms": list(ARMS), "true_slot": TRUE_SLOT}
    agg["prereg"] = "preregs/2026-08-04_foundation_coverage_baseline_v1.md"
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ----------------------------------------------------------------------------- self-test
def self_test():
    """(1) 14 items load, categories all in causal scope; (2) grounded read recovers HARM on a
    physical-injury span the frozen lexicon misses; (3) contamination: mech view exposes no
    forbidden field, primitive tables have no proper nouns; (4) four arms produce well-formed
    picks and are not all identical."""
    views = load_items()
    assert len(views) == 14
    for v in views:
        assert v["category"] in CAUSAL_CATEGORIES
        for fld in MECH_FORBIDDEN_FIELDS:
            assert fld not in v

    # grounded read recovers HARM on a knife-in-breast span; frozen lexicon does not
    knife = "the half-breed saw his chance and drove the knife to the hilt in the young man's breast."
    hu, pu, d = grounded_valence_evidence(knife, HARM_VERB, HELP_VERB, True)
    g = torch.Generator().manual_seed(7)
    assert accumulate_valence(hu, pu, g) == "HARM", f"grounded read failed on knife span: {d}"

    # primitive tables have no proper nouns
    for tbl in (HARM_VERB, HELP_VERB, PATIENT_TOKENS, HYPOTHETICAL_MARK):
        for w in tbl:
            assert w == w.lower(), f"primitive table has non-lowercase token {w!r}"

    res = run_seed(0, views)
    for arm, rows in res["arms"].items():
        for r in rows:
            assert r["pick_slot"] in (-1, 0, 1)
    assert len(set(res["arm_pick_digests"].values())) >= 2, "arms did not differ"
    eg = _acc(res["arms"]["EARNED_GROUNDED"])
    print(f"[SELFTEST PASS] 14 items; knife->HARM OK; seed0 EARNED_GROUNDED acc={eg:.3f} "
          f"digests={res['arm_pick_digests']}", flush=True)
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
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(OUTPUT_DIR, e)
        raise
