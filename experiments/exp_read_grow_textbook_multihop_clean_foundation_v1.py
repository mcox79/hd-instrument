# CELL: read_grow_textbook_multihop_clean_foundation_v1
# QUESTION (the pivot's decisive phase-2 reasoning test): the extraction-wall arc (v2-v4) PROVED
#   glass-box HAND-RULES extraction (~0.385 honest edge precision) is structurally insufficient to
#   feed trustworthy 0.70 multi-hop is-a closure -- v4 localized CLOSURE AMPLIFICATION (composed
#   precision plateaus ~0.409 honest). But v4's edges were STILL hand-rules-extracted. The pivot
#   (USER-authorized) says the FOUNDATION may be built with ANY high-precision tool; glass-box is the
#   RUNTIME REASONING invariant. So the untested, decisive question:
#
#     Feed the SAME reasoning machinery (transitive closure + honest relation-verifying oracle) a
#     CLEAN is-a foundation -- does held-out multi-hop composed precision clear the 0.70 trustworthy
#     floor (edge precision WAS the constraint; clean foundation UNLOCKS glass-box reasoning = pivot
#     validated), or does it STILL fail (closure-amplification / is-a-transitivity specificity-decay
#     is INTRINSIC to the reasoning machinery, NOT extraction -- a MAJOR localization)?
#
# THE ONE EXPERIMENTAL VARIABLE = the EDGE SOURCE (nothing else changes):
#   NOISY  = the v4 hand-rules genus extractor's edges (the v2-v4 regime; must-beat baseline).
#   CLEAN  = the SAME glossary edges FILTERED to only those the honest relation-verifying oracle
#            (WN hypernym path + VERIFIED structure-license + per-pair curated) confirms TRUE. This
#            is the idealized clean foundation: edge precision = 1.0 (honest) BY CONSTRUCTION. Using
#            WN/curation to build a clean foundation is a FOUNDATION-BUILD (pivot-authorized clean
#            tool), NOT a runtime-reasoning-glass-box violation. No external LLM at inference.
#   The closure + honest-oracle SCORING machinery is IDENTICAL for both arms (v4's harness, reused).
#
# NON-CIRCULARITY (the design's load-bearing subtlety, surfaced in metrics): filtering LOCAL edges to
#   honest-true does NOT force COMPOSED pairs true, because the honest oracle is NOT transitively
#   closed -- wn_path uses per-term senses, so honest_true(A,B) AND honest_true(B,C) do NOT imply
#   honest_true(A,C) when the sense of B reached from A differs from the sense of B that reaches C
#   (sense-shift), or when B is a generic hub. The cell MEASURES + LEDGERS every composed CLEAN pair
#   that is honest-FALSE despite EVERY constituent edge being honest-TRUE. That count > 0 both proves
#   the test is non-circular AND is the direct measurement of intrinsic closure amplification.
#
# GUARD (brain + logic): is-a is NOT always transitively valid across abstraction jumps (poodle->dog->
#   mammal OK; cell->unit-of-life->concept degrades). The honest oracle scores each composed pair
#   INDEPENDENTLY for a genuine verified is-a (WN won't credit a non-hypernym endpoint), so the gold
#   RESPECTS valid transitivity only -- un-transitive chains are NOT scored as gold. If clean closure
#   fails PURELY because is-a transitivity is semantically bounded, THAT is the finding (specificity-
#   decay ceiling), distinct from an edge-noise failure -- reported as such.
#
# DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
#   (1) REAL baseline: NOISY_V4_COMPOSE (the v4 regime; reproduces v4's landed honest 0.409 at FULL,
#       Gate-D positive control) + non-compositional DIRECT_LOOKUP / FREQUENCY / RANDOM. NOT abstain/blank.
#   (2) CAN-FAIL: HARD_PASS iff clean composed precision (honest) >= 0.70 AND clean spec_hard >= 0.50
#       AND decisive lift over noisy (>= 0.15). MIDDLE_BAND_CEILING (BOUND PROVEN, FIRST-CLASS) iff clean
#       plateaus below 0.70 EVEN with edge precision 1.0 -- reported honestly, NOT tortured toward pass.
#   (3) DIFFICULTY-ON: fixed universe of multi-hop composables (dist in [2,DMAX], NO direct edge in
#       clean OR noisy graph, WN-checkable), HONEST-oracle valid-transitivity labels, with hard negatives.
#   (4) ONE variable = edge SOURCE (raw v4 extraction vs oracle-cleaned-to-truth). Closure+scoring identical.
#
# TRUSTWORTHY FLOOR JUSTIFICATION (0.70, pre-registered, consistent with the v2-v4 arc): 0.70 = the
#   minimum composed precision at which a multi-hop is-a inference is usable as a FOUNDATION fact without
#   per-fact human verification; below 0.70 the closure emits >30% false is-a claims = not trustworthy for
#   downstream reasoning. spec_hard floor 0.50 = the clean arm must reject >= half the hard false paths.
#
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic seeding only (FIXED int random.Random(seed); no salted-builtin seed / set-order dedupe)
# - arms_differ verified (clean graph drops >= min_removed_edges vs noisy; distinct edge sets)
# - all bands tagged HYPOTHESIZED@ (pre-reg) then confirmed MEASURED@ at run
#
# Compute architecture: (b) sequential-CPU. Justification: glass-box regex / NLTK POS-tag / WordNet /
#   symbolic graph closure -- no matmul, no substrate vectors, no GPU speedup. Diagnostic reasoning-value
#   cell (compute-proportionality: cheapest decisive method). Wall < few min (v4 prototype ~15s). RUN INLINE.
# calibration_check: "default_ok_for_this_regime" (symbolic oracle thresholds inherited from v4; measured at run).
# crlb_n/a: "no continuous noise floor; discriminator is symbolic composed-path precision vs WN-verified is-a."
# progress_logging: "print_flush_true" (cell wall << 30min; flush on every progress line).
# real_code_path: self_test constructs graph/clean-filter/closure/query-universe/verdict on a synthetic
#   textbook + exercises clean_gloss + the non-circularity ledger + honest_true (no synthetic-only branch).
# storage_strategy: no_storage (symbolic is-a graph; no vector store / composition of vectors).

import os
import sys
import json
import time
import random
import argparse
import traceback
import importlib.util
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

ANCHOR_NAME = "read_grow_textbook_multihop_clean_foundation_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(
    REPO, "data", "corpora", "textbook_concepts_biology", "cleaned",
    "concepts_biology.clean.txt",
)
V4_PATH = os.path.join(REPO, "experiments", "exp_read_grow_textbook_multihop_genus_head_v4.py")

# Reuse the v4 REAL code path: v4 genus extractor, honest relation-verifying oracle, closure,
# compose_precision, edge_precision, arm_scores, build_query_universe, graph build (via V3), V1 parse.
_spec4 = importlib.util.spec_from_file_location("_isa_v4_clean", V4_PATH)
V4 = importlib.util.module_from_spec(_spec4)
_spec4.loader.exec_module(V4)
V3 = V4.V3
V1 = V4.V1

DMAX_WN = V4.DMAX_WN
TOP_HUB_K = V4.TOP_HUB_K
RNG_SEED = 20260719          # FIXED deterministic seed (never a salted-builtin digest)

# v4's landed honest composed precision -- Gate-D positive-control reproduction target (FULL only).
V4_LANDED_COMPOSE_HONEST = 0.40876   # CITED@data/exp_read_grow_textbook_multihop_genus_head_v4/metrics.json:compose_prec.v4.prec_honest

# Pre-registered bands (HYPOTHESIZED@ this file; confirmed MEASURED@ at run)
BANDS = {
    "hp_compose_prec_floor": 0.70,   # HARD_PASS: clean composed multi-hop precision (HONEST) trustworthy
    "hp_spec_hard_floor": 0.50,      # HARD_PASS: clean arm rejects >= half the false paths
    "hp_material_lift": 0.15,        # HARD_PASS: clean beats noisy v4 composed precision decisively
    "min_pos": 20,                   # vacuous-n guard: need >= 20 composable honest-true positives
    "min_neg_hard": 10,              # need >= 10 false-path hard negatives to audit spec_hard
    "min_clean_props": 20,           # clean foundation must emit >= 20 composed proposals to test closure
    "min_removed_edges": 20,         # arms-differ: clean must drop >= 20 edges vs noisy
    "pos_control_tol": 0.05,         # NOISY arm must reproduce v4's landed honest 0.409 at FULL
}

# ------------------------- error-checking scaffolds -------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "{}: {}".format(type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: {}".format(type(exc).__name__),
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


# ==================================================================================
# THE ONE VARIABLE: clean the glossary edges to only honest-oracle-verified is-a facts
# ==================================================================================

def clean_gloss(gloss_noisy):
    """Idealized clean foundation: keep only edges the honest relation-verifying oracle confirms TRUE.
       Edge precision = 1.0 (honest) BY CONSTRUCTION. Returns (clean_gloss, kept, removed)."""
    clean = defaultdict(set)
    kept = removed = 0
    for c, ps in gloss_noisy.items():
        for p in ps:
            if c == p:
                continue
            if V4.honest_true(c, p)[0]:
                clean[c].add(p)
                kept += 1
            else:
                removed += 1
    return clean, kept, removed


def shortest_path(adj, src, dst, maxd=12):
    """Shortest is-a path src->...->dst over adj (BFS). Returns node list or None."""
    if src == dst:
        return None
    prev = {src: None}
    d = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        if d[u] >= maxd:
            continue
        for v in adj.get(u, ()):
            if v not in prev:
                prev[v] = u
                d[v] = d[u] + 1
                if v == dst:
                    path = [v]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return list(reversed(path))
                q.append(v)
    return None


def clean_composed_ledger(gloss_clean, reach_clean, direct_clean, limit=30):
    """The non-circularity + closure-amplification measurement: composed CLEAN pairs (dist>=2, not
       direct, WN-checkable) that are honest-FALSE despite EVERY constituent edge being honest-TRUE."""
    props = [(a, c) for a in reach_clean for c, bd in reach_clean[a].items()
             if bd >= 2 and (a, c) not in direct_clean and V3.wn_checkable(a, c)]
    n_props = len(props)
    n_false = 0
    ledger = []
    all_edges_true_confirmed = 0
    for (a, c) in sorted(props):
        if not V4.honest_true(a, c)[0]:
            n_false += 1
            path = shortest_path(gloss_clean, a, c)
            edges_true = None
            if path and len(path) >= 3:
                edges_true = all(V4.honest_true(path[i], path[i + 1])[0]
                                 for i in range(len(path) - 1))
                if edges_true:
                    all_edges_true_confirmed += 1
            if len(ledger) < limit:
                ledger.append({"pair": [a, c], "path": path,
                               "all_edges_honest_true": edges_true})
    return {
        "n_clean_proposals": n_props,
        "n_clean_composed_false": n_false,
        "false_path_rate": round(n_false / n_props, 5) if n_props else 0.0,
        "n_false_via_all_true_edges_confirmed": all_edges_true_confirmed,
        "examples": ledger,
    }


# ------------------------- top-level measurement -------------------------

def measure(sections, rng):
    # Build the NOISY graph exactly as v4 (the one-variable contrast partner = the v2-v4 regime).
    g_noisy = V3.build_gloss_graph(sections, V4.genus_head_v4)
    gloss_noisy = g_noisy["gloss"]

    # THE ONE VARIABLE: clean = same edges filtered to honest-oracle-verified is-a (edge prec 1.0 honest).
    gloss_clean, kept, removed = clean_gloss(gloss_noisy)

    edge_list_noisy = g_noisy["edge_list"]
    edge_list_clean = [(c, p) for c, ps in gloss_clean.items() for p in ps]

    direct_noisy = {(c, p) for c, ps in gloss_noisy.items() for p in ps}
    direct_clean = {(c, p) for c, ps in gloss_clean.items() for p in ps}

    reach_noisy = V3.closure(gloss_noisy)
    reach_clean = V3.closure(gloss_clean)

    nodes = sorted(set(gloss_noisy) | {p for ps in gloss_noisy.values() for p in ps}
                   | set(gloss_clean) | {p for ps in gloss_clean.values() for p in ps})

    edge_prec = {"noisy": V4.edge_precision(edge_list_noisy),
                 "clean": V4.edge_precision(edge_list_clean)}
    comp_prec = {"noisy": V4.compose_precision(gloss_noisy),
                 "clean": V4.compose_precision(gloss_clean)}

    # fixed HONEST-labeled query universe over pairs reachable in CLEAN or NOISY graph (dist [2,DMAX]).
    pos, neg_hard, neg_easy = V4.build_query_universe(
        nodes, reach_clean, reach_noisy, direct_clean, direct_noisy, rng)
    top_hubs = set(p for p, _ in g_noisy["parent_freq"].most_common(TOP_HUB_K))
    base_rate = len(pos) / max(1, len(pos) + len(neg_hard) + len(neg_easy))

    arms = {}
    arms["NOISY_V4_COMPOSE"] = V4.arm_scores(pos, neg_hard, neg_easy, reach_noisy, direct_noisy,
                                             top_hubs, base_rate, random.Random(RNG_SEED + 13), "COMPOSE")
    arms["CLEAN_COMPOSE"] = V4.arm_scores(pos, neg_hard, neg_easy, reach_clean, direct_clean,
                                          top_hubs, base_rate, random.Random(RNG_SEED + 15), "COMPOSE")
    arms["DIRECT_LOOKUP"] = V4.arm_scores(pos, neg_hard, neg_easy, reach_clean, direct_clean,
                                          top_hubs, base_rate, random.Random(RNG_SEED + 19), "DIRECT_LOOKUP")
    arms["FREQUENCY"] = V4.arm_scores(pos, neg_hard, neg_easy, reach_clean, direct_clean,
                                      top_hubs, base_rate, random.Random(RNG_SEED + 23), "FREQUENCY")
    arms["RANDOM"] = V4.arm_scores(pos, neg_hard, neg_easy, reach_clean, direct_clean,
                                   top_hubs, base_rate, random.Random(RNG_SEED + 7), "RANDOM")

    ledger = clean_composed_ledger(gloss_clean, reach_clean, direct_clean)

    return {
        "n_nodes": len(nodes),
        "n_direct_edges_noisy": len(direct_noisy), "n_direct_edges_clean": len(direct_clean),
        "n_edge_list_noisy": len(edge_list_noisy), "n_edge_list_clean": len(edge_list_clean),
        "clean_edges_kept": kept, "clean_edges_removed": removed,
        "n_pos": len(pos), "n_neg_hard": len(neg_hard), "n_neg_easy": len(neg_easy),
        "base_rate": round(base_rate, 5),
        "edge_prec": edge_prec, "compose_prec": comp_prec, "arms": arms,
        "clean_composed_ledger": ledger,
        "top_hubs_noisy": sorted(top_hubs),
        "top_parents_clean": [p for p, _ in Counter(
            [p for ps in gloss_clean.values() for p in ps]).most_common(12)],
    }


# ------------------------- verdict -------------------------

def compute_verdict(res, bands, run_mode):
    ep = res["edge_prec"]
    cp = res["compose_prec"]
    clean_arm = res["arms"]["CLEAN_COMPOSE"]
    noisy_arm = res["arms"]["NOISY_V4_COMPOSE"]
    n_pos, n_neg_hard = res["n_pos"], res["n_neg_hard"]
    removed = res["clean_edges_removed"]
    led = res["clean_composed_ledger"]

    cp_clean = cp["clean"]["prec_honest"]
    cp_noisy = cp["noisy"]["prec_honest"]
    lift = round(cp_clean - cp_noisy, 5)
    n_clean_props = cp["clean"]["n_proposals"]

    pos_control_ok = None
    if run_mode == "full":
        pos_control_ok = bool(abs(cp_noisy - V4_LANDED_COMPOSE_HONEST) <= bands["pos_control_tol"])

    diag = {
        "edge_prec_noisy_honest": ep["noisy"]["prec_honest"],
        "edge_prec_clean_honest": ep["clean"]["prec_honest"],
        "compose_prec_noisy_honest": cp_noisy, "compose_prec_clean_honest": cp_clean,
        "compose_prec_clean_wn_path": cp["clean"]["prec_wn_path"],
        "compose_prec_lift_clean_minus_noisy": lift,
        "clean_arm_precision": clean_arm["precision"], "clean_arm_spec_hard": clean_arm["spec_hard"],
        "noisy_arm_precision": noisy_arm["precision"], "noisy_arm_spec_hard": noisy_arm["spec_hard"],
        "n_clean_proposals": n_clean_props,
        "n_clean_composed_false": led["n_clean_composed_false"],
        "clean_false_path_rate": led["false_path_rate"],
        "n_false_via_all_true_edges_confirmed": led["n_false_via_all_true_edges_confirmed"],
        "clean_edges_kept": res["clean_edges_kept"], "clean_edges_removed": removed,
        "n_pos": n_pos, "n_neg_hard": n_neg_hard,
        "pos_control_target_v4_honest": V4_LANDED_COMPOSE_HONEST,
        "pos_control_ok": pos_control_ok,
    }

    # guards
    if n_pos < bands["min_pos"] or n_neg_hard < bands["min_neg_hard"]:
        return ("HARD_FAIL_VACUOUS_N",
                "underpowered: n_pos={} n_neg_hard={} (need {}/{})".format(
                    n_pos, n_neg_hard, bands["min_pos"], bands["min_neg_hard"]), diag)
    if removed < bands["min_removed_edges"]:
        return ("HARD_FAIL_ARMS_IDENTICAL",
                "clean dropped only {} edges vs noisy (< {}); one-variable contrast vacuous".format(
                    removed, bands["min_removed_edges"]), diag)
    if n_clean_props < bands["min_clean_props"]:
        return ("HARD_FAIL_VACUOUS_CLEAN_COMPOSE",
                "clean foundation emits only {} composed proposals (< {}); too sparse to test closure".format(
                    n_clean_props, bands["min_clean_props"]), diag)

    # HARD_PASS: EDGE PRECISION WAS THE CONSTRAINT -- clean foundation unlocks trustworthy closure.
    if (cp_clean >= bands["hp_compose_prec_floor"] and clean_arm["spec_hard"] >= bands["hp_spec_hard_floor"]
            and lift >= bands["hp_material_lift"]):
        return ("HARD_PASS",
                ("EDGE PRECISION WAS THE CONSTRAINT: clean foundation UNLOCKS trustworthy glass-box "
                 "multi-hop closure. Clean composed precision (HONEST)={:.3f} >= {:.2f} AND spec_hard="
                 "{:.3f} >= {:.2f} AND decisive lift over noisy v4 ({:.3f} vs {:.3f}, +{:.3f}). Pivot core "
                 "validated: feeding clean facts to the SAME reasoning machinery composes trustworthily.").format(
                    cp_clean, bands["hp_compose_prec_floor"], clean_arm["spec_hard"], bands["hp_spec_hard_floor"],
                    cp_clean, cp_noisy, lift), diag)

    # MIDDLE_BAND_CEILING: clean composed precision PLATEAUS below 0.70 despite edge precision 1.0.
    # CLOSURE AMPLIFICATION IS INTRINSIC (not extraction). MAJOR localization -- reported honestly.
    if cp_clean < bands["hp_compose_prec_floor"]:
        return ("MIDDLE_BAND_CEILING",
                ("CLEAN FACTS ARE NOT SUFFICIENT; CLOSURE IS MACHINERY-BOUND. Even with edge precision "
                 "{:.3f} (honest, 1.0 by construction -- every local edge a verified is-a), composed multi-hop "
                 "precision (honest)={:.3f} < {:.2f} trustworthy floor (clean spec_hard={:.3f}). {} of {} clean "
                 "composed pairs are honest-FALSE ({:.1%} false-path rate); {} confirmed reached via a path of "
                 "EVERY-edge-honest-TRUE = INTRINSIC closure amplification / is-a-transitivity specificity-decay "
                 "(sense-shift + hub-bridging), NOT edge noise. Clean still beats noisy v4 (+{:.3f}: {:.3f} vs "
                 "{:.3f}) but does not reach trustworthy. Localizes the bound to the REASONING MACHINERY.").format(
                    ep["clean"]["prec_honest"], cp_clean, bands["hp_compose_prec_floor"], clean_arm["spec_hard"],
                    led["n_clean_composed_false"], n_clean_props, led["false_path_rate"],
                    led["n_false_via_all_true_edges_confirmed"], lift, cp_clean, cp_noisy), diag)

    # clean clears 0.70 but not decisively (low spec_hard or thin lift) = boundary.
    return ("MIDDLE_BAND",
            ("BOUNDARY: clean composed precision (honest)={:.3f} clears the {:.2f} floor but spec_hard="
             "{:.3f} (< {:.2f}) or lift +{:.3f} (< {:.2f}) is not decisive; clean helps but the trustworthy "
             "claim is not clean.").format(
                cp_clean, bands["hp_compose_prec_floor"], clean_arm["spec_hard"], bands["hp_spec_hard_floor"],
                lift, bands["hp_material_lift"]), diag)


# ------------------------- self-test (real code path) -------------------------

def self_test():
    print("[self-test] exercising REAL code path (clean_gloss + closure + ledger + honest oracle + verdict)",
          flush=True)

    # clean_gloss keeps only honest-true edges (the one variable)
    gn = defaultdict(set)
    gn["dog"].add("mammal")          # honest-true (WN)
    gn["dog"].add("car")             # honest-FALSE -> dropped
    gn["mammal"].add("animal")       # honest-true (WN)
    gn["basal angiosperm"].add("group")   # honest-FALSE (generic hub, no WN path) -> dropped
    gc, kept, removed = clean_gloss(gn)
    assert "mammal" in gc.get("dog", set()) and "car" not in gc.get("dog", set()), dict(gc)
    assert removed >= 2, ("clean must drop honest-false edges", kept, removed)
    # edge precision of the cleaned graph must be 1.0 honest by construction (over checkable edges)
    ec = V4.edge_precision([(c, p) for c, ps in gc.items() for p in ps])
    assert ec["prec_honest"] >= 0.99, ("clean edge precision must be 1.0 honest", ec)

    # shortest_path + non-circularity ledger structure
    reach_c = V3.closure(gc)
    direct_c = {(c, p) for c, ps in gc.items() for p in ps}
    assert reach_c.get("dog", {}).get("animal") == 2, ("dog->animal composed dist 2", reach_c.get("dog"))
    sp = shortest_path(gc, "dog", "animal")
    assert sp == ["dog", "mammal", "animal"], sp
    led = clean_composed_ledger(gc, reach_c, direct_c)
    assert "n_clean_proposals" in led and "false_path_rate" in led, led

    # honest oracle sanity (inherited from v4): verified relations only, no blanket credit
    assert V4.honest_true("dog", "animal")[0] is True
    assert V4.honest_true("dog", "car")[0] is False

    # tiny synthetic textbook -> full measure/verdict end-to-end (real path, no synthetic-only branch)
    text = "\n".join([
        "# Tiny Book", "##### Section Alpha", "###### Glossary",
        "dog: a mammal that is domesticated", "mammal: an animal that has fur",
        "trout: a fish found in rivers", "fish: an animal that lives in water",
        "basal angiosperm: a group of plants that branched early",
        "plant: an organism that photosynthesizes",
        "##### Section Beta", "###### Glossary",
        "poodle: a dog bred for companionship", "salmon: a fish that migrates",
        "car: a mammal that drives fast",   # v4 extracts genus 'mammal'; car->mammal honest-FALSE -> dropped
    ])
    secs = V1.parse_sections(text)
    rng = random.Random(RNG_SEED)
    res = measure(secs, rng)
    # arms must differ: clean edges != noisy edges
    assert res["clean_edges_removed"] >= 1, res["clean_edges_removed"]
    assert res["edge_prec"]["clean"]["prec_honest"] >= res["edge_prec"]["noisy"]["prec_honest"], res["edge_prec"]
    v, msg, diag = compute_verdict(res, BANDS, "smoke")
    assert v in ("HARD_PASS", "MIDDLE_BAND", "MIDDLE_BAND_CEILING", "HARD_FAIL_VACUOUS_N",
                 "HARD_FAIL_ARMS_IDENTICAL", "HARD_FAIL_VACUOUS_CLEAN_COMPOSE"), v
    print("[self-test] PASS: nodes={} edge_noisy_honest={:.2f} edge_clean_honest={:.2f} verdict={}".format(
        res["n_nodes"], res["edge_prec"]["noisy"]["prec_honest"],
        res["edge_prec"]["clean"]["prec_honest"], v), flush=True)
    return True


# ------------------------- main -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=60)
    args, _ = ap.parse_known_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=1)

    t0 = time.perf_counter()
    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = V1.parse_sections(text)
    sections = sections_all[:args.smoke_sections] if run_mode == "smoke" else sections_all
    print("[{}] sections={}".format(run_mode, len(sections)), flush=True)

    rng = random.Random(RNG_SEED)
    res = measure(sections, rng)
    verdict, verdict_msg, diag = compute_verdict(res, BANDS, run_mode)
    elapsed = time.perf_counter() - t0

    ep = res["edge_prec"]
    cp = res["compose_prec"]
    clean_arm = res["arms"]["CLEAN_COMPOSE"]
    noisy_arm = res["arms"]["NOISY_V4_COMPOSE"]
    led = res["clean_composed_ledger"]

    gate = {
        "discriminator_fires": bool(res["clean_edges_removed"] >= BANDS["min_removed_edges"]
                                    and cp["clean"]["n_proposals"] >= BANDS["min_clean_props"]),
        "oracle_labeled_both_classes": bool(res["n_pos"] > 0 and res["n_neg_hard"] > 0),
        "clean_minus_noisy_edges_removed": res["clean_edges_removed"],
        "real_baselines": ["NOISY_V4_COMPOSE", "DIRECT_LOOKUP", "FREQUENCY", "RANDOM"],
        "difficulty_on": ("fixed universe: HONEST-labeled multi-hop pairs (dist in [2,{}]), NO direct edge "
                          "in clean OR noisy graph; hard-negs = honest-false but book-composable".format(DMAX_WN)),
        "one_variable": "edge SOURCE (raw v4 hand-rules extraction vs oracle-cleaned-to-honest-true)",
        "load_bearing_metric": "clean composed multi-hop precision (HONEST oracle) + spec_hard + false-path rate",
        "clean_edge_precision_honest": ep["clean"]["prec_honest"],
        "non_circularity_false_via_all_true_edges": led["n_false_via_all_true_edges_confirmed"],
        "pos_control_ok": diag["pos_control_ok"],
    }

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": ("{}: edge_prec HONEST noisy={:.3f} -> clean={:.3f} (1.0 by construction) | compose_prec "
                    "HONEST noisy={:.3f} clean={:.3f} (lift +{:.3f}) | clean_arm prec={:.3f} spec_hard={:.3f} | "
                    "clean false-path {}/{} ({:.1%}), {} via all-true-edge paths | n_pos={} n_neg_hard={} | "
                    "pos_control_ok={}").format(
            verdict, ep["noisy"]["prec_honest"], ep["clean"]["prec_honest"],
            cp["noisy"]["prec_honest"], cp["clean"]["prec_honest"],
            round(cp["clean"]["prec_honest"] - cp["noisy"]["prec_honest"], 5),
            clean_arm["precision"], clean_arm["spec_hard"],
            led["n_clean_composed_false"], led["n_clean_proposals"], led["false_path_rate"],
            led["n_false_via_all_true_edges_confirmed"], res["n_pos"], res["n_neg_hard"],
            diag["pos_control_ok"]),
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "bands": BANDS, "diag": diag, "gate": gate,
        "n_nodes": res["n_nodes"],
        "n_direct_edges_noisy": res["n_direct_edges_noisy"], "n_direct_edges_clean": res["n_direct_edges_clean"],
        "n_edge_list_noisy": res["n_edge_list_noisy"], "n_edge_list_clean": res["n_edge_list_clean"],
        "clean_edges_kept": res["clean_edges_kept"], "clean_edges_removed": res["clean_edges_removed"],
        "n_pos": res["n_pos"], "n_neg_hard": res["n_neg_hard"], "n_neg_easy": res["n_neg_easy"],
        "base_rate": res["base_rate"],
        "edge_prec": ep, "compose_prec": cp, "arms": res["arms"],
        "clean_composed_ledger": led,
        "top_hubs_noisy": res["top_hubs_noisy"], "top_parents_clean": res["top_parents_clean"],
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
    print("[{}] {}".format(run_mode, verdict_msg), flush=True)
    print("   edge_prec HONEST  noisy={:.3f} clean={:.3f}  (clean edges kept={} removed={})".format(
        ep["noisy"]["prec_honest"], ep["clean"]["prec_honest"],
        res["clean_edges_kept"], res["clean_edges_removed"]), flush=True)
    print("   compose_prec HONEST  noisy={:.3f} clean={:.3f}  (lift +{:.3f}; clean wn_path={:.3f} n_props={})".format(
        cp["noisy"]["prec_honest"], cp["clean"]["prec_honest"],
        cp["clean"]["prec_honest"] - cp["noisy"]["prec_honest"],
        cp["clean"]["prec_wn_path"], cp["clean"]["n_proposals"]), flush=True)
    for a in ["NOISY_V4_COMPOSE", "CLEAN_COMPOSE", "DIRECT_LOOKUP", "FREQUENCY", "RANDOM"]:
        m = res["arms"][a]
        print("   {:20s} prec={:.3f} recall={:.3f} spec_hard={:.3f} balacc={:.3f} yes_rate={:.3f}".format(
            a, m["precision"], m["recall"], m["spec_hard"], m["balanced_acc"], m["yes_rate"]), flush=True)
    print("   clean false-path: {}/{} composed pairs honest-FALSE ({:.1%}); {} confirmed via all-true-edge paths".format(
        led["n_clean_composed_false"], led["n_clean_proposals"], led["false_path_rate"],
        led["n_false_via_all_true_edges_confirmed"]), flush=True)
    if diag["pos_control_ok"] is not None:
        print("   pos-control (NOISY reproduces v4 landed honest {:.3f}): ok={}".format(
            V4_LANDED_COMPOSE_HONEST, diag["pos_control_ok"]), flush=True)
    print("[{}] metrics -> {}".format(run_mode, os.path.join(output_dir, "metrics.json")), flush=True)


if __name__ == "__main__":
    OUT_FOR_CRASH = os.path.join(REPO, "data", "exp_{}".format(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_FOR_CRASH, e)
        raise
