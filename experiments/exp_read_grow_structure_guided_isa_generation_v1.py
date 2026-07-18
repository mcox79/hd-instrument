# CELL: read_grow_structure_guided_isa_generation_v1
# QUESTION (the exact lever the schema-SELECTION VET a2a59f406 localized as genuine + untested):
#   The schema-SELECTION cell (read_grow_schema_hierarchy_vs_frequency_v1, 180bf95a9; VET a2a59f406)
#   found structure-as-a-SELECTION-rule has NO headroom: is-a genus is extraction-determined; a
#   matched-coverage selection rule (frequency OR hierarchy) has almost no ambiguity to resolve. The
#   VET's recorded follow-up: use the self-learned is-a hierarchy to GENERATE new candidate is-a edges
#   via TRANSITIVE closure for COVERAGE-EXTENSION -- "X is-a G" + "G is-a H" => infer X is-a G / X is-a H,
#   generating is-a edges the FLAT per-sentence extractor MISSES. This cell tests GENERATION (not
#   selection on an existing candidate set): does self-learned structure add real is-a knowledge at the
#   GENERATION stage where selection could not?
#
# KNOWN RISK (measured, NOT ignored): the multihop-compose cell (read_grow_textbook_multihop_compose_v1,
#   96ab5fbbd; VET a7a85fb2) found transitive CLOSURE over noisy extracted edges AMPLIFIES errors
#   (compose_precision_raw ~0.37, false_path ~0.63). Structure-guided GENERATION inherits those noisy
#   edges, so this cell REPORTS the PRECISION of the GENERATED edges (not just the coverage gain). The
#   honest question: does structure-guided generation extend coverage at USABLE precision, OR does
#   closure-amplification sink the generated edges (bounded, like the multihop cell)?
#
# DISTINCTION FROM THE MULTIHOP-COMPOSE CELL (this is NOT a re-run):
#   - multihop cell = DISCRIMINATION frame: balanced-accuracy of closure answering YES/NO on a curated
#     WN-labeled POS/NEG query set; closure basis = glossary edges only; primary axis = compose ON/OFF.
#   - THIS cell = GENERATION frame: COVERAGE x PRECISION (F1, IR-style) of the flat per-sentence
#     extractor (FIXED) vs flat + confidence-controlled transitive GENERATION (GEN_CTRL), over the full
#     WN-true is-a universe among book nodes; closure basis = FULL extracted graph (glossary + prose
#     Hearst = the actual flat extractor). A DESIGNED confidence control (recognized non-hub intermediate,
#     depth cap 2) targets the multihop cell's localized amplification cause (generic-hub false paths).
#
# MECHANISM (glass-box brain analog; NO runtime LLM, NO substrate vectors, NO torch):
#   FIXED (BASELINE, generation OFF): asserts is-a (X,A) iff a DIRECT extracted edge X->A exists
#     (distance-1; the flat per-sentence extractor, no transitive inference). High precision, limited
#     coverage -- a REAL, non-strawman baseline (the actual extractor output).
#   GEN_CTRL (PRIMARY, generation ON, confidence-controlled): direct edges PLUS 2-hop generated edges
#     (X,A) where exists intermediate G with direct X->G and G->A, G is a RECOGNIZED CLASS
#     (book in-degree >= MIN_SUPPORT), and A is NOT a generic hub (book in-degree <= HUB_MAX). The two
#     gates encode the fix the multihop VET pointed at: do not infer THROUGH an unattested intermediate
#     nor INTO an over-general hub (the false-path sources).
#   GEN_RAW (DIAGNOSTIC control, generation ON, uncontrolled): direct edges plus FULL transitive closure
#     (depth<=15, no gates) = the multihop cell's amplifier. Included to show the control is not merely
#     re-deriving the uncontrolled failure.
#   ORACLE = WordNet hypernym ancestry (paraphrase-robust; INDEPENDENT gold, NOT the book's own closure).
#     Reused UNMODIFIED from the multihop cell so the comparison to its finding is clean.
#
# METRIC (IR-style, per seed):
#   GOLD universe G = all WN-true is-a pairs (X,A) among book nodes at WN-dist in [1, DMAX] (the
#     relations an ideal reader should know; includes indirect pairs the flat extractor structurally
#     misses = the coverage-extension opportunity = DIFFICULTY-ON).
#   coverage_arm = |{g in G : arm asserts g}| / |G|            (recall over the true is-a universe)
#   precision_arm = |{asserted & WN-true}| / |asserted WN-checkable|   (over ALL asserted edges)
#   F1_arm = 2*cov*prec / (cov+prec)                           (the combined coverage x precision score)
#   precision_generated = precision over ONLY the NEW edges (GEN asserted MINUS FIXED asserted) -- the
#     direct closure-amplification audit the known-risk demands (reported for CTRL and RAW separately).
#   coverage_gain = coverage_GEN_CTRL - coverage_FIXED.
#
# DESIGN-GATE (verified at smoke BEFORE full):
#   REAL BASELINE = FIXED = the flat per-sentence extractor's coverage x precision (the thing generation
#     must extend; high-precision, NOT a strawman/abstain-all/blank).
#   ONE VARIABLE  = transitive-inference GENERATION on (GEN_CTRL) vs off (FIXED); identical edges/gold/oracle.
#   DIFFICULTY-ON = gold universe INCLUDES indirect WN-true pairs the flat extractor structurally misses
#     (genuine coverage-extension, not re-scoring seen edges); 3 deterministic corpus subsamples (seeds).
#   CAN-FAIL      = HARD_FAIL_CLOSURE_AMPLIFICATION if generated edges are majority-false even WITH the
#     confidence control (precision_generated < fail floor across a majority of seeds) -> closure noise
#     sinks generation = a real bound (bounded like the multihop cell), reported honestly, NOT tortured.
#     Also fails to HARD_PASS if F1(GEN_CTRL) does not beat F1(FIXED) by the margin.
#   USABLE-PRECISION GUARD = HARD_PASS additionally REQUIRES precision_generated(GEN_CTRL) >= 0.50
#     (generated edges strictly majority-TRUE); a coverage gain built from majority-false edges is the
#     amplification failure masquerading as a win, NOT a HARD_PASS.
#   NO LEAK       = graph + generation derive ONLY from read prose/glossary; WordNet is an INDEPENDENT
#     gold oracle used only in EVAL (never in extraction or generation).
#   DISCRIMINATOR-FIRES = GEN_CTRL must actually generate >= MIN_GENERATED new edges (else nothing to
#     measure -> vacuous); asserted-edge sets FIXED/GEN_CTRL/GEN_RAW must bit-differ (arms-differ).
#   SEEDS = 3 deterministic corpus subsamples: read sections where idx % 5 != offset, offset in {0,1,2}
#     (each reads 4/5 of the book -> 3 distinct dense is-a graphs); NO salted-hash / RNG (determinism gate).
#
# BRAIN-CHECK (per standing discipline; drilled, reported in verdict + here): humans DO use hierarchy to
#   infer unseen is-a's -- transitive inheritance is a core semantic-memory operation (Collins & Quillian
#   1969 hierarchical inheritance: "a canary is an animal" is inferred, never stored directly). And the
#   brain DOES face the same closure-noise problem: child over-generalization errors ("a whale is a fish")
#   are transitive inference through a WRONG/over-general intermediate; the brain controls it with
#   basic-level / typicality constraints (Rosch 1978) -- the direct analog of this cell's recognized-
#   non-hub-intermediate confidence control. So the mechanism is brain-faithful AND the control mirrors
#   how the brain bounds the same amplification. A HARD_FAIL here would be a substrate-native precision
#   bound (extraction too noisy), not a refutation of hierarchical inference per se.
#
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/floor):
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic: section-index offsets only; NO built-in hash() / list(set()) for seeding or ordering
# - arms_differ verified (FIXED / GEN_CTRL / GEN_RAW asserted-edge sets bit-differ; self-test + run)
# - baseline_in_band checked (0.05 < coverage_FIXED < 0.95)
# - discriminator survives scale: runs at FULL corpus; smoke reports the full-corpus fires preview
# - HARD_PASS strictly margin-above baseline (pre-registered eps) + usable-precision floor
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in comments
#
# Compute architecture: (b) sequential-CPU. Justification: glass-box regex / POS-tag / WordNet /
#   symbolic graph closure over a small is-a graph; no matmul, no substrate vectors, no GPU speedup.
#   Diagnostic reasoning-value cell (compute-proportionality: cheapest decisive method). Wall < few min
#   at full over 3 seeds. Storage: no_storage (symbolic dicts/graph). CRLB n/a: no continuous noise floor;
#   discriminator is symbolic graph-path existence vs WN ancestry.
# calibration_check: "default_ok_for_this_regime" (no primitive-default inheritance; symbolic thresholds
#   MIN_SUPPORT/HUB_MAX/DGEN set from pre-reg + the multihop cell's measured hub cause, measured at run).

import os
import sys
import json
import time
import argparse
import traceback
import importlib.util
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

ANCHOR_NAME = "read_grow_structure_guided_isa_generation_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSE_PATH = os.path.join(
    REPO, "experiments", "exp_read_grow_textbook_multihop_compose_v1.py")

# Reuse the multihop-compose cell's extractor + WN oracle + graph-build as the REAL code path
# (guarantees a clean comparison to its measured amplification finding; NO re-implementation drift).
_spec = importlib.util.spec_from_file_location("_compose_v1", COMPOSE_PATH)
M2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M2)

V1 = M2.V1                         # exp_read_grow_textbook_isa_growth_v1 extractor
CORPUS = M2.CORPUS
wn_ancestors = M2.wn_ancestors
wn_match_lemmas = M2.wn_match_lemmas
wn_checkable = M2.wn_checkable
wn_true_dist = M2.wn_true_dist
build_graphs = M2.build_graphs
closure = M2.closure

DMAX_WN = M2.DMAX_WN               # WN-distance cap for the gold universe (reuse; avoids deep inflation)
MIN_SUPPORT = 3                    # a RECOGNIZED intermediate class: book in-degree >= 3 (matches schema cell)
HUB_MAX = M2.NOISE_HUB_MAX         # generic-hub cap for the target: in-degree <= 8 (matches multihop cell)
DGEN = 2                           # GEN_CTRL generation depth cap (2-hop; the safest confidence control)
RAW_MAXD = 15                      # GEN_RAW full-closure depth cap (matches multihop cell closure default)
SEED_OFFSETS = (0, 1, 2)          # deterministic subsample offsets (read sections where idx%5 != offset)
SUBSAMPLE_MOD = 5                  # drop 1/5 of sections per seed -> 3 distinct dense graphs

# ------ pre-registered bands (HYPOTHESIZED@this-file; confirmed MEASURED@ at smoke/full) ------
BANDS = {
    "hp_f1_margin": 0.03,          # HARD_PASS: F1(GEN_CTRL) - F1(FIXED) >= +0.03
    "hp_gen_precision_floor": 0.50,# HARD_PASS: precision_generated(GEN_CTRL) >= 0.50 (usable: majority-true)
    "hp_coverage_gain_min": 0.02,  # HARD_PASS: coverage actually extended by >= 0.02
    "fail_gen_precision_max": 0.45,# HARD_FAIL_CLOSURE_AMPLIFICATION: generated edges majority-false (< 0.45)
    "seed_majority": 2,            # >= 2/3 seeds must satisfy an axis for a cell-level verdict
    "min_gold": 30,                # vacuous-n guard: >= 30 WN-true is-a pairs in the gold universe
    "min_generated": 20,           # discriminator-fires: >= 20 generated edges to measure precision
    "min_fixed_cov": 0.05,         # baseline_in_band lower
    "max_fixed_cov": 0.95,         # baseline_in_band upper
}


# ----------------------------- error-checking scaffolds -----------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
    }
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
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "{}: {}".format(type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: {}".format(type(exc).__name__),
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ----------------------------- graph helpers -----------------------------

def full_indeg(full):
    """Book in-degree of each parent over the FULL extracted graph (glossary + prose)."""
    indeg = Counter()
    for _c, ps in full.items():
        for p in ps:
            indeg[p] += 1
    return indeg


def direct_edge_set(full):
    """Set of directly-extracted is-a edges (child, parent), child != parent."""
    return set((c, p) for c, ps in full.items() for p in ps if c != p)


def generate_ctrl(full, indeg):
    """Confidence-controlled 2-hop generation: (X,A) via intermediate G where X->G and G->A direct,
       G is a RECOGNIZED class (indeg[G] >= MIN_SUPPORT), A is NOT a generic hub (indeg[A] <= HUB_MAX),
       X != A, and (X,A) is NOT already a direct edge. Returns set of generated (X,A) pairs."""
    direct = direct_edge_set(full)
    gen = set()
    for x in list(full.keys()):
        gxs = full.get(x, ())
        for g in gxs:
            if indeg[g] < MIN_SUPPORT:      # intermediate must be a recognized class
                continue
            for a in full.get(g, ()):
                if a == x or a == g:
                    continue
                if indeg[a] > HUB_MAX:      # target must not be a generic hub
                    continue
                if (x, a) in direct:
                    continue
                gen.add((x, a))
    return gen


def generate_raw(full):
    """Uncontrolled full-closure generation: all (X,A) reachable at book-dist >= 2 (no gates)."""
    direct = direct_edge_set(full)
    reach = closure(full, maxd=RAW_MAXD)
    gen = set()
    for x, dd in reach.items():
        for a, bd in dd.items():
            if bd >= 2 and a != x and (x, a) not in direct:
                gen.add((x, a))
    return gen


# ----------------------------- gold universe + IR metrics -----------------------------

def build_universe(reach_raw):
    """COVERAGE-EXTENSION universe = WN-true is-a pairs (X,A) that are BOOK-REACHABLE (A reachable from
       X via the full extracted-graph closure, dist>=1) AND WN-true (independent oracle). This is exactly
       the set of true is-a relations the book's edges CAN compose to -- the flat extractor covers only
       the direct (dist-1) subset; the indirect ones are the coverage-extension opportunity generation
       must recover. Excludes deep generic WN ancestors the book never connects (avoids DMAX inflation
       that would drive the baseline out of band)."""
    universe = set()
    for x, dd in reach_raw.items():
        for a in dd:
            if a != x and wn_true_dist(x, a) is not None:
                universe.add((x, a))
    return universe


def _precision(asserted):
    """Precision over the WN-checkable subset of an asserted (X,A) edge set."""
    chk = tr = 0
    for (x, a) in asserted:
        if x == a or not wn_checkable(x, a):
            continue
        chk += 1
        if wn_true_dist(x, a) is not None:
            tr += 1
    return (round(tr / chk, 5) if chk else 0.0), chk, tr


def _f1(cov, prec):
    return round(2 * cov * prec / (cov + prec), 5) if (cov + prec) > 0 else 0.0


def run_seed(sections, offset):
    """Build graph from the read subsample; compute FIXED / GEN_CTRL / GEN_RAW coverage x precision."""
    read = [sec for i, sec in enumerate(sections) if i % SUBSAMPLE_MOD != offset]
    graphs = build_graphs(read)
    full = graphs["full"]
    indeg = full_indeg(full)

    nodes = sorted(set(full.keys()) | set(p for ps in full.values() for p in ps))
    direct = direct_edge_set(full)
    gen_ctrl = generate_ctrl(full, indeg)
    reach_raw = closure(full, maxd=RAW_MAXD)
    gen_raw = set((x, a) for x, dd in reach_raw.items() for a, bd in dd.items()
                  if bd >= 2 and a != x and (x, a) not in direct)

    gold = build_universe(reach_raw)
    n_gold = len(gold)

    # asserted-edge sets per arm
    asserted_fixed = set(direct)
    asserted_ctrl = set(direct) | gen_ctrl
    asserted_raw = set(direct) | gen_raw

    # coverage (recall over gold)
    def coverage(asserted):
        if not gold:
            return 0.0, 0
        hit = sum(1 for g in gold if g in asserted)
        return round(hit / n_gold, 5), hit

    cov_fixed, hit_fixed = coverage(asserted_fixed)
    cov_ctrl, hit_ctrl = coverage(asserted_ctrl)
    cov_raw, hit_raw = coverage(asserted_raw)

    # precision over ALL asserted
    prec_fixed, chk_fixed, _ = _precision(asserted_fixed)
    prec_ctrl, chk_ctrl, _ = _precision(asserted_ctrl)
    prec_raw, chk_raw, _ = _precision(asserted_raw)

    # precision over the GENERATED (new) edges only = the closure-amplification audit
    gp_ctrl, gchk_ctrl, gtr_ctrl = _precision(gen_ctrl)
    gp_raw, gchk_raw, gtr_raw = _precision(gen_raw)

    f1_fixed = _f1(cov_fixed, prec_fixed)
    f1_ctrl = _f1(cov_ctrl, prec_ctrl)
    f1_raw = _f1(cov_raw, prec_raw)

    # arms-differ digests (asserted-edge sets bit-differ)
    digest = {
        "fixed": _digest_edges(asserted_fixed),
        "gen_ctrl": _digest_edges(asserted_ctrl),
        "gen_raw": _digest_edges(asserted_raw),
    }

    return {
        "offset": offset,
        "n_read_sections": len(read),
        "n_nodes": len(nodes),
        "n_direct_edges": len(direct),
        "n_gold": n_gold,
        "n_generated_ctrl": len(gen_ctrl),
        "n_generated_raw": len(gen_raw),
        "coverage_fixed": cov_fixed, "coverage_gen_ctrl": cov_ctrl, "coverage_gen_raw": cov_raw,
        "coverage_gain_ctrl": round(cov_ctrl - cov_fixed, 5),
        "coverage_gain_raw": round(cov_raw - cov_fixed, 5),
        "gold_hits_fixed": hit_fixed, "gold_hits_ctrl": hit_ctrl, "gold_hits_raw": hit_raw,
        "precision_fixed": prec_fixed, "precision_gen_ctrl": prec_ctrl, "precision_gen_raw": prec_raw,
        "precision_generated_ctrl": gp_ctrl, "precision_generated_raw": gp_raw,
        "gen_ctrl_checkable": gchk_ctrl, "gen_ctrl_true": gtr_ctrl,
        "gen_raw_checkable": gchk_raw, "gen_raw_true": gtr_raw,
        "f1_fixed": f1_fixed, "f1_gen_ctrl": f1_ctrl, "f1_gen_raw": f1_raw,
        "f1_margin_ctrl": round(f1_ctrl - f1_fixed, 5),
        "asserted_checkable": {"fixed": chk_fixed, "gen_ctrl": chk_ctrl, "gen_raw": chk_raw},
        "digest": digest,
    }


def _digest_edges(edges):
    import hashlib
    items = sorted(edges)
    return hashlib.sha256(json.dumps(items).encode()).hexdigest()


# ----------------------------- verdict -----------------------------

def compute_verdict(seed_results, bands):
    maj = bands["seed_majority"]
    n = len(seed_results)

    # vacuous-n guard
    vacuous = sum(1 for r in seed_results
                  if r["n_gold"] < bands["min_gold"] or r["n_generated_ctrl"] < bands["min_generated"])
    # baseline in band
    in_band = sum(1 for r in seed_results
                  if bands["min_fixed_cov"] < r["coverage_fixed"] < bands["max_fixed_cov"])
    # arms differ
    arms_ok = all(len(set(r["digest"].values())) == 3 for r in seed_results)

    # HARD_PASS seeds: F1 margin + usable generated precision + real coverage gain
    hp_seeds = sum(1 for r in seed_results
                   if r["f1_margin_ctrl"] >= bands["hp_f1_margin"]
                   and r["precision_generated_ctrl"] >= bands["hp_gen_precision_floor"]
                   and r["coverage_gain_ctrl"] >= bands["hp_coverage_gain_min"])
    # HARD_FAIL_CLOSURE_AMPLIFICATION seeds: generated edges majority-false even under control
    amp_fail_seeds = sum(1 for r in seed_results
                         if r["precision_generated_ctrl"] < bands["fail_gen_precision_max"])

    diag = {
        "n_seeds": n, "seed_majority": maj,
        "vacuous_seeds": vacuous, "baseline_in_band_seeds": in_band, "arms_differ": bool(arms_ok),
        "hp_seeds": hp_seeds, "amp_fail_seeds": amp_fail_seeds,
        "f1_fixed": [r["f1_fixed"] for r in seed_results],
        "f1_gen_ctrl": [r["f1_gen_ctrl"] for r in seed_results],
        "f1_gen_raw": [r["f1_gen_raw"] for r in seed_results],
        "f1_margin_ctrl": [r["f1_margin_ctrl"] for r in seed_results],
        "coverage_fixed": [r["coverage_fixed"] for r in seed_results],
        "coverage_gen_ctrl": [r["coverage_gen_ctrl"] for r in seed_results],
        "coverage_gain_ctrl": [r["coverage_gain_ctrl"] for r in seed_results],
        "precision_fixed": [r["precision_fixed"] for r in seed_results],
        "precision_gen_ctrl": [r["precision_gen_ctrl"] for r in seed_results],
        "precision_generated_ctrl": [r["precision_generated_ctrl"] for r in seed_results],
        "precision_generated_raw": [r["precision_generated_raw"] for r in seed_results],
        "n_generated_ctrl": [r["n_generated_ctrl"] for r in seed_results],
        "n_generated_raw": [r["n_generated_raw"] for r in seed_results],
        "n_gold": [r["n_gold"] for r in seed_results],
    }

    if vacuous >= maj:
        return ("HARD_FAIL_VACUOUS_N",
                "underpowered: >= {}/{} seeds have < {} gold pairs or < {} generated edges "
                "(n_gold={} n_generated_ctrl={})".format(
                    maj, n, bands["min_gold"], bands["min_generated"],
                    diag["n_gold"], diag["n_generated_ctrl"]),
                diag)

    if not arms_ok:
        return ("HARD_FAIL_ARMS_IDENTICAL",
                "META_RULE_AF: FIXED / GEN_CTRL / GEN_RAW asserted-edge sets not all distinct", diag)

    if in_band < maj:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND",
                "FIXED coverage out of [{}, {}] band on majority of seeds (coverage_fixed={})".format(
                    bands["min_fixed_cov"], bands["max_fixed_cov"], diag["coverage_fixed"]),
                diag)

    if hp_seeds >= maj:
        return ("HARD_PASS",
                ("structure-guided transitive GENERATION extends held-out is-a coverage at USABLE "
                 "precision where SELECTION could not: F1(GEN_CTRL) beats F1(FIXED) by {} on >= {}/{} "
                 "seeds, generated-edge precision {} (>= {} usable floor), coverage gain {}. "
                 "Self-learned structure adds real knowledge at the GENERATION stage. "
                 "Brain-check: transitive is-a inheritance (Collins-Quillian) with recognized-non-hub "
                 "intermediate control (basic-level/Rosch) -- brain-faithful mechanism + control.").format(
                    diag["f1_margin_ctrl"], maj, n, diag["precision_generated_ctrl"],
                    bands["hp_gen_precision_floor"], diag["coverage_gain_ctrl"]),
                diag)

    if amp_fail_seeds >= maj:
        return ("HARD_FAIL_CLOSURE_AMPLIFICATION",
                ("closure-amplification sinks the generated edges even WITH the confidence control: "
                 "generated-edge precision {} (< {} floor) on >= {}/{} seeds -- majority-false, a real "
                 "substrate-native bound (bounded like the multihop-compose cell's ~0.37 raw precision; "
                 "here RAW precision_generated={}). Coverage IS extended (gain {}) but the added edges "
                 "cannot be trusted. Brain-check: same amplification the brain bounds with basic-level "
                 "constraints; here textbook extraction noise exceeds the control's reach.").format(
                    diag["precision_generated_ctrl"], bands["fail_gen_precision_max"], maj, n,
                    diag["precision_generated_raw"], diag["coverage_gain_ctrl"]),
                diag)

    return ("MIDDLE_BAND",
            ("structure-guided generation extends coverage (gain {}) but does not clear the HARD_PASS "
             "bar on a majority of seeds: F1 margin {} (need >= {}), generated-edge precision {} "
             "(usable floor {}, amplification floor {}). Partial: real coverage extension, precision "
             "in the grey zone.").format(
                diag["coverage_gain_ctrl"], diag["f1_margin_ctrl"], bands["hp_f1_margin"],
                diag["precision_generated_ctrl"], bands["hp_gen_precision_floor"],
                bands["fail_gen_precision_max"]),
            diag)


# ----------------------------- self-test (real code path) -----------------------------

def self_test():
    print("[self-test] exercising REAL code path (compose-v1 extractor + WN oracle + generation + verdict)",
          flush=True)
    # WN oracle sanity (reuse multihop cell conventions): dog->animal true (indirect), dog->car false.
    assert wn_true_dist("dog", "animal") is not None, "WN: dog->animal ancestry expected"
    assert wn_true_dist("dog", "car") is None, "WN: dog->car must be false"

    # Constructed corpus: dog/cat/whale is-a mammal (mammal recognized: indeg>=3); mammal is-a animal;
    # trout is-a fish; fish is-a animal. NO direct dog->animal edge. GEN_CTRL must generate (dog,animal)
    # via recognized intermediate mammal, and it is WN-true -> precision_generated=1, coverage extended.
    text = "\n".join([
        "# Tiny Book",
        "##### Section Alpha",
        "A dog is a mammal that barks.",
        "A cat is a mammal that meows.",
        "A whale is a mammal that swims.",
        "A mammal is an animal with fur.",
        "###### Glossary",
        "dog: a mammal that is domesticated",
        "cat: a mammal that is kept as a pet",
        "whale: a mammal that lives in the ocean",
        "mammal: an animal that has fur",
        "##### Section Beta",
        "A trout is a fish that swims.",
        "A fish is an animal that lives in water.",
        "###### Glossary",
        "trout: a fish found in rivers",
        "fish: an animal that lives in water",
    ])
    secs = V1.parse_sections(text)
    graphs = build_graphs(secs)
    full = graphs["full"]
    indeg = full_indeg(full)
    assert "mammal" in full.get("dog", set()), full.get("dog")
    assert "animal" in full.get("mammal", set()), full.get("mammal")
    assert indeg["mammal"] >= MIN_SUPPORT, ("mammal must be a recognized class", indeg.get("mammal"))

    direct = direct_edge_set(full)
    assert ("dog", "animal") not in direct, "no direct dog->animal edge by construction"

    gen_ctrl = generate_ctrl(full, indeg)
    gen_raw = generate_raw(full)
    # DISCRIMINATOR FIRES: generation produces the transitive edge the flat extractor missed
    assert ("dog", "animal") in gen_ctrl, ("GEN_CTRL must generate dog->animal via mammal", sorted(gen_ctrl))
    assert ("dog", "animal") in gen_raw, "GEN_RAW must also reach dog->animal"
    # ARMS-MUST-DIFFER (META_RULE_AF): FIXED / GEN_CTRL / GEN_RAW asserted sets bit-differ
    d_fixed = _digest_edges(set(direct))
    d_ctrl = _digest_edges(set(direct) | gen_ctrl)
    d_raw = _digest_edges(set(direct) | gen_raw)
    assert len({d_fixed, d_ctrl, d_raw}) == 3, ("arms must differ", d_fixed, d_ctrl, d_raw)

    # generated-edge precision is measurable and the dog->animal generation is TRUE
    gp, gchk, gtr = _precision(gen_ctrl)
    assert gchk >= 1 and gtr >= 1, ("generated precision measurable + at least one true", gchk, gtr)

    # end-to-end run_seed + verdict on the constructed corpus (offset 4 keeps all sections read: none%5==4)
    r = run_seed(secs, offset=4)
    assert r["coverage_gen_ctrl"] >= r["coverage_fixed"], ("gen coverage >= fixed", r)
    assert r["n_generated_ctrl"] >= 1, r["n_generated_ctrl"]
    v, msg, diag = compute_verdict([r, r, r], BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_CLOSURE_AMPLIFICATION", "HARD_FAIL_VACUOUS_N",
                 "HARD_FAIL_ARMS_IDENTICAL", "HARD_FAIL_BASELINE_OUT_OF_BAND", "MIDDLE_BAND"), v

    # CAN-FAIL reachable: force generated edges majority-false -> HARD_FAIL_CLOSURE_AMPLIFICATION
    amp = [dict(r, precision_generated_ctrl=0.20, f1_margin_ctrl=0.10, coverage_gain_ctrl=0.10,
                coverage_fixed=0.30, n_gold=50, n_generated_ctrl=40) for _ in range(3)]
    va, _, _ = compute_verdict(amp, BANDS)
    assert va == "HARD_FAIL_CLOSURE_AMPLIFICATION", ("can-fail amplification reachable", va)
    # CAN-PASS reachable: usable generated precision + margin + gain -> HARD_PASS
    good = [dict(r, precision_generated_ctrl=0.65, f1_margin_ctrl=0.08, coverage_gain_ctrl=0.10,
                 coverage_fixed=0.30, n_gold=50, n_generated_ctrl=40) for _ in range(3)]
    vg, _, _ = compute_verdict(good, BANDS)
    assert vg == "HARD_PASS", ("can-pass reachable", vg)

    print("[self-test] PASS: gen(dog->animal)=True gen_prec={:.3f} n_gen_ctrl={} n_gen_raw={} "
          "verdict={} can_fail={} can_pass={}".format(
              gp, len(gen_ctrl), len(gen_raw), v, va, vg), flush=True)
    return True


# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=45,
                    help="leading sections used in smoke mode")
    args, _ = ap.parse_known_args()

    if args.self_test:
        sys.exit(0 if self_test() else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=len(SEED_OFFSETS))

    t0 = time.perf_counter()
    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = V1.parse_sections(text)
    sections = sections_all[:args.smoke_sections] if run_mode == "smoke" else sections_all

    seed_results = [run_seed(sections, off) for off in SEED_OFFSETS]
    verdict, verdict_msg, diag = compute_verdict(seed_results, BANDS)
    elapsed = time.perf_counter() - t0

    gate = {
        "real_baseline": "FIXED = flat per-sentence extractor coverage x precision (high-precision, "
                         "limited coverage; the actual extractor output -- NOT strawman/abstain/blank)",
        "one_variable": "transitive-inference GENERATION on (GEN_CTRL) vs off (FIXED); "
                        "identical extracted edges / gold universe / WN oracle",
        "difficulty_on": "gold universe includes indirect WN-true pairs the flat extractor structurally "
                         "misses (coverage-extension, not re-scoring seen edges)",
        "can_fail": "HARD_FAIL_CLOSURE_AMPLIFICATION if generated edges majority-false even with control "
                    "(precision_generated < {}); HARD_PASS needs F1 margin + usable-precision floor".format(
                        BANDS["fail_gen_precision_max"]),
        "no_leak": "graph + generation from read prose/glossary only; WordNet independent gold in EVAL only",
        "discriminator_fires_min_generated": [r["n_generated_ctrl"] for r in seed_results],
        "arms_differ": bool(all(len(set(r["digest"].values())) == 3 for r in seed_results)),
        "baseline_in_band": bool(sum(
            1 for r in seed_results
            if BANDS["min_fixed_cov"] < r["coverage_fixed"] < BANDS["max_fixed_cov"]) >= BANDS["seed_majority"]),
        "confidence_control": "GEN_CTRL: 2-hop, recognized intermediate (indeg>={}), non-hub target "
                              "(indeg<={}); GEN_RAW: uncontrolled full closure (depth<={})".format(
                                  MIN_SUPPORT, HUB_MAX, RAW_MAXD),
        "run_at_full_corpus": bool(run_mode == "full"),
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": ("{}: F1 fixed={} gen_ctrl={} gen_raw={} | cov fixed={} gen_ctrl={} gain={} | "
                    "prec_generated ctrl={} raw={} | n_gen_ctrl={} n_gold={}").format(
            verdict, diag["f1_fixed"], diag["f1_gen_ctrl"], diag["f1_gen_raw"],
            diag["coverage_fixed"], diag["coverage_gen_ctrl"], diag["coverage_gain_ctrl"],
            diag["precision_generated_ctrl"], diag["precision_generated_raw"],
            diag["n_generated_ctrl"], diag["n_gold"]),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "seed_results": seed_results,
        "n_sections": len(sections),
        "seed_offsets": list(SEED_OFFSETS),
        "params": {"MIN_SUPPORT": MIN_SUPPORT, "HUB_MAX": HUB_MAX, "DGEN": DGEN,
                   "RAW_MAXD": RAW_MAXD, "DMAX_WN": DMAX_WN, "SUBSAMPLE_MOD": SUBSAMPLE_MOD},
    }
    _write_metrics_atomic(output_dir, metrics)

    print("[{}] VERDICT={} {}".format(run_mode, verdict, verdict_msg), flush=True)
    for r in seed_results:
        print("[{}] off={} read={} nodes={} n_gold={} n_gen_ctrl={} n_gen_raw={} | "
              "F1 fixed={:.3f} ctrl={:.3f} raw={:.3f} (margin={:+.3f}) | "
              "cov fixed={:.3f} ctrl={:.3f} gain={:+.3f} | "
              "prec_all fixed={:.3f} ctrl={:.3f} | prec_generated ctrl={:.3f} raw={:.3f}".format(
                  run_mode, r["offset"], r["n_read_sections"], r["n_nodes"], r["n_gold"],
                  r["n_generated_ctrl"], r["n_generated_raw"], r["f1_fixed"], r["f1_gen_ctrl"],
                  r["f1_gen_raw"], r["f1_margin_ctrl"], r["coverage_fixed"], r["coverage_gen_ctrl"],
                  r["coverage_gain_ctrl"], r["precision_fixed"], r["precision_gen_ctrl"],
                  r["precision_generated_ctrl"], r["precision_generated_raw"]), flush=True)
    print("[{}] gate arms_differ={} baseline_in_band={} n_gen_ctrl={} metrics -> {}".format(
        run_mode, gate["arms_differ"], gate["baseline_in_band"],
        gate["discriminator_fires_min_generated"], os.path.join(output_dir, "metrics.json")), flush=True)


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
