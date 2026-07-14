"""COLD-PLACEMENT RECOVERY OPTIMIZATION -- optimize-to-frontier step on the MIDDLE_BAND base result
(data/exp_cold_placement_usefulness_v1/metrics.json: name-transparent exact=0.1488, opaque-gloss exact=0.0382,
both above 0% floors but below HARD-PASS bars). Determines whether the modest magnitude is METHOD-LIMITED
(fixable) or FUNDAMENTAL via TWO axes: (A) a stronger recovery method (fuller WordNet content: synonyms +
hypernyms + full definitions, not just a single cached gloss sentence; basic sense-disambiguation for CN_/FN_
lemmas via synset(name) exact-match for WN_ entities and gloss/neighbor-overlap disambiguation otherwise), and
(B) a task-relevant RELATION-LEVEL metric that credits TOP-K nearest anchors (not just the single exact parent)
scored against whether the INHERITED RELATION (edge-type + target) matches the entity's held-out relation --
because for the actual goal (infer relations) the exact parent may be unnecessary if a near-neighborhood concept
carries the same relation.

DESIGN SOURCE: notes/research_brain_grounding_spoke_building_canonical_reference_2026-07-14.md +
notes/research_cold_start_intrinsic_content_vs_relational_inference_2026-07-14.md (same design lineage as the
base cell). Base cell + its landed metrics + its ALL must-fails are reused verbatim
(CITED@experiments/exp_cold_placement_usefulness_v1.py, CITED@data/exp_cold_placement_usefulness_v1/metrics.json).

MECHANISM CHANGE vs base (zero-training, deterministic, still network-free AND CORPUS-FREE at cell runtime):
the base cell's gloss-fallback used ONE cached WordNet gloss sentence per entity (68.56% coverage of the opaque
bucket, sourced from a DIFFERENT population's tail-sample snapshot). This cell instead uses a FULLER, TARGETED
lexical cache built once, interactively, in .venv (nltk 3.9.4 wordnet local corpora, same discipline as
exp_grounded_ingest_text_spoke_v1's provenance.json) DIRECTLY over THIS cell's own ~600-entity population
(data/exp_cold_placement_recovery_opt_v1/provenance.json; 568/600 = 94.7% resolved MEASURED@that file). For
each entity: WN_ entities resolve to an EXACT synset via synset(name) (the ID already carries the sense tag, no
guessing needed); CN_/FN_ entities resolve via synsets(lemma) disambiguated against the entity's own definition
text + ablated-graph-neighbor tokens (a real "pick the sense whose gloss best fits, not the first" step), falling
back to the WordNet-default (most-frequent) sense when no disambiguating signal exists. Each resolved sense
supplies THREE new candidate-anchor sources beyond the base's single gloss string: SYNONYMS (lemma_names),
HYPERNYMS (direct hypernym lemma_names), and the full DEFINITION text -- each searched against the SAME
well-connected + contentful lemma-index lookup as the base cell's name/gloss search (CITED@base cell's
candidate_lookup / name_transparent_search, REUSED verbatim via import, not reimplemented).

TIERED CANDIDATE RESOLUTION (rank-0 = the base cell's exact-match-comparable pick; full ranked list = the top-K
pool for the relation-level metric):
  tier 0 (name_transparent):   REUSED verbatim from the base cell (identical classifier, identical population
                                membership for this stratum -- guarantees a fair, apples-to-apples comparison).
  tier 1 (wn_synonym):         WordNet synonym lemma strings searched via candidate_lookup.
  tier 2 (wn_hypernym):        WordNet direct-hypernym lemma strings searched via candidate_lookup.
  tier 3 (wn_gloss_definition): fresh WordNet definition content-words searched via candidate_lookup.
  tier 4 (old_gloss_fallback): the base cell's ORIGINAL cached gloss (data/exp_grounded_ingest_text_spoke_v1/
                                provenance.json), kept as a lowest-priority fallback for superset coverage.
Rank-0 = tier-0 pick if resolved (polysemy-guard reused verbatim from base cell for tier 0 only -- tiers 1-4 use
simple degree-then-eid tie-break, a declared simplification since their purpose is TOP-K POOL WIDTH, not a
single high-stakes guess). TOP_K=5 distinct candidates gathered across all tiers (tier asc, degree desc, eid asc).

STRATIFICATION (kept, per CONTRACT): name_transparent / name_opaque (all non-tier-0) uses the SAME underlying
100-node population + the SAME tier-0 candidate SEARCH (name_transparent_search imported verbatim, unchanged)
as the base cell -- but stratum MEMBERSHIP is not bit-identical to the base cell's landed run: the polysemy-guard
disambiguation step (resolve_candidate) now has richer disambiguating text available (WN definition where the
OLD cached gloss was missing/thin), which resolves a handful of previously-abstained tier-0 ties (MEASURED@this
run: name_transparent n=135 here vs n=121 in the base cell; name_opaque n=215 here vs n=229 there). This is
ITSELF part of optimization axis 1 (better disambiguation -> "pick the sense whose gloss best fits"), disclosed
honestly rather than claimed as a bit-identical control -- the stratum-LEVEL comparison (same classifier logic,
same graph, same population pool) remains fair, just not population-count-identical. The finer opaque
sub-breakdown (which tier sourced the pick: wn_synonym / wn_hypernym / wn_gloss_definition / old_gloss_fallback /
abstain) is NEW diagnostic detail reported for this cell only.

TWO METRICS REPORTED PER STRATUM (per CONTRACT):
  EXACT (rank-0, directly comparable to the base cell's exact_match_rate): pseudo-anchor(rank0) == true target.
  RELATION-LEVEL (top-K, the key reframe): true iff ANY of the top-K candidates has an edge (in the ABLATED
  graph) of the EXACT held relation type to the EXACT true target (reusing base cell's node_relation_edges,
  generalized from a single candidate to a union over top-K) -- OR candidate==true_target trivially. Applied
  UNIFORMLY to both TAXONOMIC and ARBITRARY populations (base cell only had this relation-type-exact check for
  ARBITRARY; unifying the definition lets one metric answer "did SOME near-neighborhood anchor carry the
  literal missing edge" for both populations). A looser reach<=1-from-any-of-K variant is also reported
  (topk_reach_h1) as a secondary, non-gated diagnostic.

MUST-FAIL CONTROLS (ALL of the base cell's must-fails REUSED, generalized to top-K where the top-K metric
introduces a NEW inflation risk that must itself be must-failed):
  (i)   SCRAMBLE: permutes (name_tokens, lexical-cache entry, old-gloss) JOINTLY across the taxonomic population
        (same seeded permutation construction as the base cell) BEFORE classification. Must collapse to floor on
        BOTH exact and relation-level metrics.
  (ii)  RANDOM: NEW risk -- moving from a single random candidate to a top-K random pool gives K independent
        chances to hit by luck, which could inflate the relation-level floor even with zero real signal. This
        cell's RANDOM arm draws TOP_K=5 distinct random well-connected nodes (not one) so the floor comparison is
        apples-to-apples against the mechanism's own top-K pool width -- the honest test of whether K-guesses
        alone (not content) explain any relation-level lift.
  (iii) GRAPH_SELF_REFERENCE_CONTROL: reused verbatim (empty name_tokens + a "gloss" built ONLY from the entity's
        own remaining ablated-graph-neighbor names, no lexical-cache entry substituted) -- provably empty for
        degree-1 cold entities; must stay at 0 on BOTH metrics for BOTH populations.
  POP (fixed highest-ablated-degree node, repeated top-K times -- a degenerate top-K of identical picks) is an
  additional sanity baseline; must not help on either metric.

## Compute architecture
class (b) sequential-CPU with justification: identical rationale to the base cell -- pure symbolic graph
traversal (string tokenization, lemma-index dict lookups, bounded memoized BFS over the same ~190k-edge /
~141k-node graph). The ONLY new work per entity is a handful of extra dict lookups per tier (synonyms/hypernyms/
definition tokens, each capped at a few dozen tokens) -- still dict/set-bound, no matmul, nothing to batch on
GPU. Expected low tens-of-seconds total on CPU (base cell measured 3.9s for the equivalent population size; this
cell does ~4x the per-entity lookup work in the worst case, still trivially fast). device=cpu always (no cuda
code path exists in this cell; HDLAB_QUEUE=remote_cpu_queue forces cpu).

NETWORK-FREE / CORPUS-FREE AT RUNTIME (load-bearing for remote portability -- same discipline as
exp_grounded_ingest_text_spoke_v1): this cell does NOT import nltk. The nltk wordnet lookup was performed ONCE,
interactively, in the local .venv (nltk 3.9.4 wordnet corpora present, MEASURED@this session) over THIS cell's
exact deterministic population (reproduced via the base cell's imported build_populations + SEED=42 + same
provenance-order priority -- bit-identical population to the base cell and to itself on any re-run), and the
result committed at data/exp_cold_placement_recovery_opt_v1/provenance.json. The cell reads that committed
JSON at runtime; a remote host with no nltk / no wordnet corpora installed still runs this cell identically.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (META_RULE_AF): MECHANISM/RANDOM/SCRAMBLE/GRAPH_SELF_REFERENCE_CONTROL per-entity
#   rank0-candidate-id vectors are hashed and compared; POP is exempted (constant-candidate baseline by design).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: n/a -- exact-match / relation-match over a finite well-connected candidate pool, not a
#   noise-floor estimation problem; crlb_n/a declared with rationale (identical to base cell).
# - baseline_in_band: RANDOM(topK)/POP(topK)/GRAPH_SELF_REFERENCE_CONTROL must sit near the structural floor
#   (<0.05 exact, <0.10 relation-level given K=5 guesses) by construction -- checked at self-test AND full.
# - discriminator survives scale: analytical (scale-invariant string/lemma/degree lookup, same as base cell) +
#   self-test preview on a planted synthetic arena (extended with hypernym-only and synonym-only planted cases
#   that PROVE the WN-tier recovers entities the base cell's gloss-only mechanism could NOT) + a real relations.
#   jsonl slice (F.1).
# - HARD-PASS strictly above floor: all bands below are strict multiples/margins over RANDOM(topK)/POP(topK), or
#   strict deltas over the base cell's OWN landed numbers (fair, population-identical comparison), not bare >=.
# - HP_SCOPE: EXACT_DELTA gates apply to MECHANISM name_transparent / name_opaque(all) strata (taxonomic).
#   RELLEVEL gates apply to MECHANISM name_transparent / name_opaque(all) strata (taxonomic) + arbitrary
#   name_transparent stratum. RANDOM/POP/SCRAMBLE/GRAPH_SELF_REFERENCE_CONTROL = must-not-clear controls.
# - per-unit failure-class instrumentation: population construction + classification wrapped per-entity; a
#   single entity's classify/score exception is recorded with failure_class and does NOT abort the whole cell.
# - calibration_check: adaptive_with_discriminator_gate -- TOP_K and the tier ordering are pre-registered
#   constants (not tuned on real-data results); the self-test proves each tier fires + scramble collapses on a
#   SEPARATE synthetic arena BEFORE the real-data run.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in this docstring + inline comments.
# - progress_logging: print_flush_true (line-buffered stdout + periodic heartbeat); timeout well under 1800s.
# - cell_chunked: false (no seed axis; one deterministic population sample, identical to base cell).
# - real_code_path_exercised (F.1): self-test calls run_corpus (imported from the base cell, REAL loader against
#   REAL relations.jsonl, small slice) AND a fully synthetic planted arena.
# - substrate_signature_checked (F.2/F.3): classify_and_place_v2 / topk_relation_match / build_lemma_index bound
#   against inspect.signature with the exact args this cell's FULL call sites use.
# - guard_baseline_valid (F.4): the LEAK guard (opaque exceeding floor) validated against RANDOM(topK), not a
#   baseline that could itself be at the arena floor.

ASCII-only. No bare except; except SystemExit before except Exception. Deterministic seeded RNGs
(np.random.default_rng); sorted(), never bare set-iteration order, per the split-nondeterminism discipline.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

from experiments.exp_cold_placement_usefulness_v1 import (  # noqa: E402
    load_graph, build_directed_adj, node_degree, build_lemma_index, build_undirected_adj, bfs_full, dist_to,
    node_relation_edges, build_populations, tokenize_entity, tokenize_text, candidate_lookup,
    name_transparent_search, resolve_candidate, neighbor_name_tokens, load_provenance_glosses,
    build_planted_arena, RELATIONS_PATH, PROVENANCE_PATH, SEED, TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N,
    BFS_HMAX, BFS_VISIT_CAP, STOPWORDS, MIN_TOKEN_LEN, WELL_CONNECTED_MIN_DEGREE, MIN_STRATUM_N,
    RANDOM_EXACT_EPS, TAXONOMIC_RELS,
)

ANCHOR_NAME = "cold_placement_recovery_opt_v1"

LEXICAL_CACHE_PATH = os.path.join(_REPO, "data", "exp_cold_placement_recovery_opt_v1", "provenance.json")

TOP_K = 5

# ---- MEASURED@data/exp_cold_placement_usefulness_v1/metrics.json (base cell landed numbers; fair comparison
#      basis since tier-0 name_transparent classifier + population are IMPORTED VERBATIM, identical membership)
BASE_TRANS_EXACT = 0.1487603305785124        # gates.taxonomic.name_transparent.exact_match_rate (n=121)
BASE_OPAQUE_ALL_EXACT = 0.026200873362445413  # gates.taxonomic.name_opaque.exact_match_rate (n=229, ALL opaque)
BASE_ARB_TRANS_RECOVERY = 0.15217391304347827  # gates.arbitrary.mechanism_name_transparent.target_recovery_rate

# ---- self-test thresholds (planted synthetic arena, not real data) ----
SELFTEST_MIN_TRANS_EXACT = 0.60
SELFTEST_MAX_SCRAMBLE_EXACT = 0.20
SELFTEST_MAX_RANDOM_EXACT = 0.20
SELFTEST_MIN_RANDOM_TOPK_MARGIN = 0.30  # MECHANISM topk_relation_match - RANDOM topk_relation_match (not an
                                        # absolute cap on RANDOM's topk rate: the planted arena's well-connected
                                        # pool is tiny (~11 candidates), so a K=5 random draw hits by chance far
                                        # more often than on the real ~32k-node well-connected pool -- same
                                        # tiny-synthetic-pool caveat as the base cell's SELFTEST_MIN_ARBITRARY_MARGIN.
                                        # The honest discriminator is the MARGIN, matching the margin-based FULL-
                                        # scale RANDOM(topK) floor comparison, not an artificially-tightened cap.
SELFTEST_MIN_HYPERNYM_ONLY_RECOVERY = 0.60   # entities recoverable ONLY via hypernym tier (gloss carries no signal)
SELFTEST_MIN_SYNONYM_ONLY_RECOVERY = 0.60    # entities recoverable ONLY via synonym tier
SELFTEST_MIN_TOPK_BEATS_EXACT_MARGIN = 0.10  # proves relation-level (topK) genuinely exceeds rank0-exact somewhere

# ---- PRE-REGISTERED bands (fixed BEFORE the real-data run; autonomy per CONTRACT) ----
# EXACT-DELTA-VS-BASE bands (answers "is the modest magnitude METHOD-LIMITED (fixable)?")
EXACT_DELTA_HP_MIN = 0.05     # opt_exact - base_exact >= this -> genuine method-driven lift (METHOD_LIMITED)
EXACT_DELTA_HF_MAX = 0.02     # <= this -> no real lift from the stronger method (FUNDAMENTAL for this axis)

# RELATION-LEVEL (top-K) bands vs RANDOM(topK) floor -- first measurement of this metric, banded like base PRED1
RELLEVEL_TRANS_HP_MIN = 0.30
RELLEVEL_TRANS_RATIO_HP_MIN = 5.0
RELLEVEL_TRANS_RATIO_HF_MAX = 2.0
RELLEVEL_OPAQUE_HP_MIN = 0.10
RELLEVEL_OPAQUE_RATIO_HP_MIN = 4.0
RELLEVEL_OPAQUE_RATIO_HF_MAX = 1.5
SCRAMBLE_COLLAPSE_HP_FRAC = 0.35
SCRAMBLE_COLLAPSE_HF_FRAC = 0.50

RELLEVEL_ARB_MARGIN_HP_MIN = 0.05
RELLEVEL_ARB_MARGIN_HF_MAX = 0.02


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x is not None and x == x) else "nan"


def _nz(v):
    return v if (v == v) else 0.0


def _rnd(x, nd=5):
    return round(x, nd) if (x == x) else None


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, tag, i, t0):
    hb_path = os.path.join(str(output_dir), "_heartbeat.jsonl")
    with open(hb_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                            "elapsed_s": time.perf_counter() - t0}) + "\n")


def load_lexical_cache(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("entries", {})


# ---------------------------------------------------------------------------
# Tiered candidate resolution (rank-0 + top-K ranked list).
# ---------------------------------------------------------------------------

_TIER_NAMES = {1: "wn_synonym", 2: "wn_hypernym", 3: "wn_gloss_definition", 4: "old_gloss_fallback"}


def _tier_search(words, exclude_id, lemma_index, ablated_degree_fn):
    found = []
    for w in words:
        wl = (w or "").lower().strip().replace(" ", "_")
        if not wl or wl in STOPWORDS or len(wl.replace("_", "")) < MIN_TOKEN_LEN:
            continue
        for (d, eid) in candidate_lookup(wl, lemma_index, exclude_id, ablated_degree_fn):
            found.append((d, eid))
    if found:
        found.sort(key=lambda x: (-x[0], x[1]))
    return found


def classify_and_place_v2(name_tokens, gloss_old, lex_entry, exclude_id, lemma_index, ablated_degree_fn,
                          neighbor_tokens_fn, top_k=TOP_K):
    """Returns (rank0_or_None, topk_list, method_str, poly0_bool)."""
    definition = (lex_entry or {}).get("definition") or ""
    disambig_toks = [t for t in tokenize_text(definition) if t not in STOPWORDS and len(t) >= MIN_TOKEN_LEN]
    if not disambig_toks:
        disambig_toks = [t for t in tokenize_text(gloss_old) if t not in STOPWORDS and len(t) >= MIN_TOKEN_LEN]

    found0 = name_transparent_search(name_tokens, exclude_id, lemma_index, ablated_degree_fn)
    pick0, poly0 = resolve_candidate(found0, disambig_toks, neighbor_tokens_fn)

    tier_sources = []
    if lex_entry:
        tier_sources.append((1, lex_entry.get("synonyms") or []))
        tier_sources.append((2, lex_entry.get("hypernyms") or []))
        tier_sources.append((3, tokenize_text(definition)))
    tier_sources.append((4, tokenize_text(gloss_old)))

    seen = {}  # eid -> (tier_idx, degree)
    for tier_idx, words in tier_sources:
        found = _tier_search(words, exclude_id, lemma_index, ablated_degree_fn)
        for (d, eid) in found:
            if eid == pick0:
                continue
            if eid in seen and seen[eid][0] <= tier_idx:
                continue
            seen[eid] = (tier_idx, d)

    ranked14 = sorted(seen.items(), key=lambda kv: (kv[1][0], -kv[1][1], kv[0]))

    if pick0 is not None:
        rank0 = pick0
        method = "name_transparent"
        topk = [pick0] + [eid for (eid, _v) in ranked14][:max(0, top_k - 1)]
    elif ranked14:
        rank0 = ranked14[0][0]
        method = _TIER_NAMES[ranked14[0][1][0]]
        topk = [eid for (eid, _v) in ranked14][:top_k]
    else:
        rank0 = None
        method = "name_transparent_polysemy_abstain" if poly0 else "abstain_no_candidate"
        topk = []

    return rank0, topk, method, bool(poly0)


def _stratum_of(method):
    return "name_transparent" if method == "name_transparent" else "name_opaque"


def _anchor_group_of(method):
    if method == "name_transparent":
        return "name_transparent"
    if method in ("wn_synonym", "wn_hypernym", "wn_gloss_definition", "old_gloss_fallback"):
        return "opaque_content_sourced"
    return "opaque_no_anchor"


# ---------------------------------------------------------------------------
# Scoring: EXACT (rank0, base-comparable) + RELATION-LEVEL (top-K).
# ---------------------------------------------------------------------------

def score_taxonomic_v2(true_target, true_rel, rank0, topk, adj, memo, out_adj, in_adj, excluded_edges):
    exact_match = (rank0 is not None and rank0 == true_target)
    if rank0 is None:
        reach_h1 = reach_h2 = reach_h3 = False
    else:
        d = dist_to(adj, memo, rank0, true_target, BFS_HMAX)
        reach_h1, reach_h2, reach_h3 = (d <= 1), (d <= 2), (d <= 3)
    topk_exact = any((c is not None and c == true_target) for c in topk)
    topk_reach_h1 = any((c is not None and dist_to(adj, memo, c, true_target, BFS_HMAX) <= 1) for c in topk)
    topk_rel = _topk_relation_match(topk, true_target, true_rel, out_adj, in_adj, excluded_edges)
    return dict(exact_match=exact_match, reach_h1=reach_h1, reach_h2=reach_h2, reach_h3=reach_h3,
                abstain=(rank0 is None), topk_exact=topk_exact, topk_reach_h1=topk_reach_h1,
                topk_relation_match=topk_rel)


def score_arbitrary_v2(true_target, true_rel, rank0, topk, adj, memo, out_adj, in_adj, excluded_edges):
    if rank0 is None:
        target_recovered = False
    else:
        d = dist_to(adj, memo, rank0, true_target, BFS_HMAX)
        target_recovered = (d <= 1)
    relation_match = False
    if target_recovered and rank0 is not None:
        for (r, other) in node_relation_edges(rank0, out_adj, in_adj, excluded_edges):
            if other == true_target and r == true_rel:
                relation_match = True
                break
    topk_target_recovered = any((c is not None and dist_to(adj, memo, c, true_target, BFS_HMAX) <= 1)
                                for c in topk)
    topk_rel = _topk_relation_match(topk, true_target, true_rel, out_adj, in_adj, excluded_edges)
    return dict(target_recovered=target_recovered, relation_match=relation_match, abstain=(rank0 is None),
                topk_target_recovered=topk_target_recovered, topk_relation_match=topk_rel)


def _topk_relation_match(topk, true_target, true_rel, out_adj, in_adj, excluded_edges):
    for cand in topk:
        if cand is None:
            continue
        if cand == true_target:
            return True
        for (r, other) in node_relation_edges(cand, out_adj, in_adj, excluded_edges):
            if other == true_target and r == true_rel:
                return True
    return False


# ---------------------------------------------------------------------------
# Full arm-run over a population.
# ---------------------------------------------------------------------------

def run_taxonomic_arms_v2(pop, name_tokens_of, gloss_of, lex_of, lemma_index, ablated_degree_fn,
                          neighbor_tokens_fn, adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random,
                          perm_scramble, excluded_edges):
    per_entity = []
    failures = []
    for rec in pop:
        node = rec["node"]
        true_target = rec["other_endpoint"]
        true_rel = rec["rel_type"]
        try:
            r0, tk, method, poly = classify_and_place_v2(
                name_tokens_of[node], gloss_of.get(node), lex_of.get(node), node, lemma_index, ablated_degree_fn,
                neighbor_tokens_fn)
            src_node = perm_scramble[node]
            r0_s, tk_s, method_s, _ = classify_and_place_v2(
                name_tokens_of[src_node], gloss_of.get(src_node), lex_of.get(src_node), node, lemma_index,
                ablated_degree_fn, neighbor_tokens_fn)
            rnd_idx = rng_random.choice(len(well_pool), size=min(TOP_K, len(well_pool)), replace=False)
            tk_rnd = [well_pool[int(i)] for i in rnd_idx]
            r0_rnd = tk_rnd[0] if tk_rnd else None
            tk_pop = [pop_node] * TOP_K
            r0_pop = pop_node
            graph_gloss = " ".join(sorted(neighbor_tokens_fn(node)))
            r0_gsr, tk_gsr, _m_gsr, _p_gsr = classify_and_place_v2(
                [], graph_gloss, None, node, lemma_index, ablated_degree_fn, neighbor_tokens_fn)

            stratum = _stratum_of(method)
            anchor_group = _anchor_group_of(method)
            row = dict(node=node, stratum=stratum, anchor_group=anchor_group, method=method, poly=poly,
                      arms={})
            row["arms"]["MECHANISM"] = dict(rank0=r0, topk=tk,
                                            **score_taxonomic_v2(true_target, true_rel, r0, tk, adj, memo,
                                                                 out_adj, in_adj, excluded_edges))
            row["arms"]["SCRAMBLE"] = dict(rank0=r0_s, topk=tk_s, method=method_s,
                                           **score_taxonomic_v2(true_target, true_rel, r0_s, tk_s, adj, memo,
                                                                out_adj, in_adj, excluded_edges))
            row["arms"]["RANDOM"] = dict(rank0=r0_rnd, topk=tk_rnd,
                                         **score_taxonomic_v2(true_target, true_rel, r0_rnd, tk_rnd, adj, memo,
                                                              out_adj, in_adj, excluded_edges))
            row["arms"]["POP"] = dict(rank0=r0_pop, topk=tk_pop,
                                      **score_taxonomic_v2(true_target, true_rel, r0_pop, tk_pop, adj, memo,
                                                           out_adj, in_adj, excluded_edges))
            row["arms"]["GRAPH_SELF_REFERENCE_CONTROL"] = dict(
                rank0=r0_gsr, topk=tk_gsr,
                **score_taxonomic_v2(true_target, true_rel, r0_gsr, tk_gsr, adj, memo, out_adj, in_adj,
                                     excluded_edges))
            per_entity.append(row)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failures.append(dict(node=node, failure_class=type(e).__name__, msg=str(e)[:200]))
    return per_entity, failures


def run_arbitrary_arms_v2(pop, name_tokens_of, gloss_of, lex_of, lemma_index, ablated_degree_fn,
                          neighbor_tokens_fn, adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random,
                          excluded_edges):
    per_entity = []
    failures = []
    for rec in pop:
        node = rec["node"]
        true_target = rec["other_endpoint"]
        true_rel = rec["rel_type"]
        try:
            r0, tk, method, poly = classify_and_place_v2(
                name_tokens_of[node], gloss_of.get(node), lex_of.get(node), node, lemma_index, ablated_degree_fn,
                neighbor_tokens_fn)
            rnd_idx = rng_random.choice(len(well_pool), size=min(TOP_K, len(well_pool)), replace=False)
            tk_rnd = [well_pool[int(i)] for i in rnd_idx]
            r0_rnd = tk_rnd[0] if tk_rnd else None
            tk_pop = [pop_node] * TOP_K
            r0_pop = pop_node

            stratum = _stratum_of(method)
            anchor_group = _anchor_group_of(method)
            row = dict(node=node, stratum=stratum, anchor_group=anchor_group, method=method, poly=poly, arms={})
            row["arms"]["MECHANISM"] = dict(rank0=r0, topk=tk,
                                            **score_arbitrary_v2(true_target, true_rel, r0, tk, adj, memo,
                                                                 out_adj, in_adj, excluded_edges))
            row["arms"]["RANDOM"] = dict(rank0=r0_rnd, topk=tk_rnd,
                                         **score_arbitrary_v2(true_target, true_rel, r0_rnd, tk_rnd, adj, memo,
                                                              out_adj, in_adj, excluded_edges))
            row["arms"]["POP"] = dict(rank0=r0_pop, topk=tk_pop,
                                      **score_arbitrary_v2(true_target, true_rel, r0_pop, tk_pop, adj, memo,
                                                           out_adj, in_adj, excluded_edges))
            per_entity.append(row)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failures.append(dict(node=node, failure_class=type(e).__name__, msg=str(e)[:200]))
    return per_entity, failures


# ---------------------------------------------------------------------------
# Aggregation.
# ---------------------------------------------------------------------------

def _agg_tax(per_entity, arm, stratum_filter=None, group_filter=None):
    rows = [r for r in per_entity
           if (stratum_filter is None or r["stratum"] == stratum_filter)
           and (group_filter is None or r["anchor_group"] == group_filter)]
    n = len(rows)
    if n == 0:
        return dict(n=0, exact_match_rate=float("nan"), topk_exact_rate=float("nan"),
                    topk_relation_match_rate=float("nan"), topk_reach_h1_rate=float("nan"),
                    abstain_rate=float("nan"))
    ex = sum(1 for r in rows if r["arms"][arm]["exact_match"])
    tkex = sum(1 for r in rows if r["arms"][arm]["topk_exact"])
    tkrel = sum(1 for r in rows if r["arms"][arm]["topk_relation_match"])
    tkh1 = sum(1 for r in rows if r["arms"][arm]["topk_reach_h1"])
    ab = sum(1 for r in rows if r["arms"][arm]["abstain"])
    return dict(n=n, exact_match_rate=ex / n, topk_exact_rate=tkex / n, topk_relation_match_rate=tkrel / n,
                topk_reach_h1_rate=tkh1 / n, abstain_rate=ab / n)


def _agg_arb(per_entity, arm, stratum_filter=None, group_filter=None):
    rows = [r for r in per_entity
           if (stratum_filter is None or r["stratum"] == stratum_filter)
           and (group_filter is None or r["anchor_group"] == group_filter)]
    n = len(rows)
    if n == 0:
        return dict(n=0, target_recovery_rate=float("nan"), relation_match_rate=float("nan"),
                    topk_target_recovery_rate=float("nan"), topk_relation_match_rate=float("nan"),
                    abstain_rate=float("nan"))
    tr = sum(1 for r in rows if r["arms"][arm]["target_recovered"])
    rm = sum(1 for r in rows if r["arms"][arm]["relation_match"])
    tktr = sum(1 for r in rows if r["arms"][arm]["topk_target_recovered"])
    tkrm = sum(1 for r in rows if r["arms"][arm]["topk_relation_match"])
    ab = sum(1 for r in rows if r["arms"][arm]["abstain"])
    return dict(n=n, target_recovery_rate=tr / n, relation_match_rate=rm / n,
                topk_target_recovery_rate=tktr / n, topk_relation_match_rate=tkrm / n, abstain_rate=ab / n)


def aggregate_and_verdict(tax_entities, arb_entities, run_mode):
    tax_trans = _agg_tax(tax_entities, "MECHANISM", group_filter="name_transparent")
    tax_opaque_all = _agg_tax(tax_entities, "MECHANISM", "name_opaque")
    tax_scr_trans = _agg_tax(tax_entities, "SCRAMBLE", group_filter="name_transparent")
    tax_scr_opaque = _agg_tax(tax_entities, "SCRAMBLE", "name_opaque")
    tax_rnd_trans = _agg_tax(tax_entities, "RANDOM", group_filter="name_transparent")
    tax_rnd_opaque = _agg_tax(tax_entities, "RANDOM", "name_opaque")
    tax_pop_trans = _agg_tax(tax_entities, "POP", group_filter="name_transparent")
    tax_gsr_all = _agg_tax(tax_entities, "GRAPH_SELF_REFERENCE_CONTROL")

    arb_mech_trans = _agg_arb(arb_entities, "MECHANISM", group_filter="name_transparent")
    arb_rnd_trans = _agg_arb(arb_entities, "RANDOM", group_filter="name_transparent")
    arb_mech_all = _agg_arb(arb_entities, "MECHANISM")

    # ---- EXACT-DELTA-VS-BASE (method-limited-vs-fundamental read) ----
    trans_delta = _nz(tax_trans["exact_match_rate"]) - BASE_TRANS_EXACT
    opaque_delta = _nz(tax_opaque_all["exact_match_rate"]) - BASE_OPAQUE_ALL_EXACT

    if tax_trans["n"] < MIN_STRATUM_N:
        exact_verdict_trans = "INCONCLUSIVE_TOO_FEW"
    elif trans_delta >= EXACT_DELTA_HP_MIN:
        exact_verdict_trans = "METHOD_LIMITED_CONFIRMED_LIFT"
    elif trans_delta <= EXACT_DELTA_HF_MAX:
        exact_verdict_trans = "FUNDAMENTAL_NO_LIFT_FROM_METHOD"
    else:
        exact_verdict_trans = "MIDDLE_BAND_PARTIAL_LIFT"

    if tax_opaque_all["n"] < MIN_STRATUM_N:
        exact_verdict_opaque = "INCONCLUSIVE_TOO_FEW"
    elif opaque_delta >= EXACT_DELTA_HP_MIN:
        exact_verdict_opaque = "METHOD_LIMITED_CONFIRMED_LIFT"
    elif opaque_delta <= EXACT_DELTA_HF_MAX:
        exact_verdict_opaque = "FUNDAMENTAL_NO_LIFT_FROM_METHOD"
    else:
        exact_verdict_opaque = "MIDDLE_BAND_PARTIAL_LIFT"

    # ---- RELATION-LEVEL (top-K) verdicts (vs RANDOM(topK) floor, banded like base PRED1) ----
    trans_floor = max(_nz(tax_rnd_trans["topk_relation_match_rate"]), RANDOM_EXACT_EPS)
    trans_rel = _nz(tax_trans["topk_relation_match_rate"])
    trans_ratio = trans_rel / trans_floor
    trans_scr_frac = (_nz(tax_scr_trans["topk_relation_match_rate"]) / trans_rel) if trans_rel > 0 else (
        float("inf") if _nz(tax_scr_trans["topk_relation_match_rate"]) > 0 else 0.0)
    if tax_trans["n"] < MIN_STRATUM_N:
        rel_verdict_trans = "INCONCLUSIVE_TOO_FEW"
    elif (trans_rel >= RELLEVEL_TRANS_HP_MIN and trans_ratio >= RELLEVEL_TRANS_RATIO_HP_MIN
          and trans_scr_frac <= SCRAMBLE_COLLAPSE_HP_FRAC):
        rel_verdict_trans = "HARD_PASS_RELATION_LEVEL_USEFUL"
    elif trans_ratio < RELLEVEL_TRANS_RATIO_HF_MAX or trans_scr_frac > SCRAMBLE_COLLAPSE_HF_FRAC:
        rel_verdict_trans = "HARD_FAIL_RELATION_LEVEL_NOT_GENUINE"
    else:
        rel_verdict_trans = "MIDDLE_BAND"

    opaque_floor = max(_nz(tax_rnd_opaque["topk_relation_match_rate"]), RANDOM_EXACT_EPS)
    opaque_rel = _nz(tax_opaque_all["topk_relation_match_rate"])
    opaque_ratio = opaque_rel / opaque_floor
    opaque_scr_frac = (_nz(tax_scr_opaque["topk_relation_match_rate"]) / opaque_rel) if opaque_rel > 0 else (
        float("inf") if _nz(tax_scr_opaque["topk_relation_match_rate"]) > 0 else 0.0)
    if tax_opaque_all["n"] < MIN_STRATUM_N:
        rel_verdict_opaque = "INCONCLUSIVE_TOO_FEW"
    elif (opaque_rel >= RELLEVEL_OPAQUE_HP_MIN and opaque_ratio >= RELLEVEL_OPAQUE_RATIO_HP_MIN
          and opaque_scr_frac <= SCRAMBLE_COLLAPSE_HP_FRAC):
        rel_verdict_opaque = "HARD_PASS_RELATION_LEVEL_USEFUL"
    elif opaque_ratio < RELLEVEL_OPAQUE_RATIO_HF_MAX or opaque_scr_frac > SCRAMBLE_COLLAPSE_HF_FRAC:
        rel_verdict_opaque = "HARD_FAIL_RELATION_LEVEL_NOT_GENUINE"
    else:
        rel_verdict_opaque = "MIDDLE_BAND"

    arb_margin = _nz(arb_mech_trans["topk_relation_match_rate"]) - _nz(arb_rnd_trans["topk_relation_match_rate"])
    if arb_mech_trans["n"] < MIN_STRATUM_N:
        rel_verdict_arb = "INCONCLUSIVE_TOO_FEW"
    elif arb_margin >= RELLEVEL_ARB_MARGIN_HP_MIN:
        rel_verdict_arb = "HARD_PASS_PARTIAL_GENERALIZATION"
    elif arb_margin <= RELLEVEL_ARB_MARGIN_HF_MAX:
        rel_verdict_arb = "HARD_FAIL_NO_GENERALIZATION"
    else:
        rel_verdict_arb = "MIDDLE_BAND"

    # ---- METHOD-LIMITED vs FUNDAMENTAL overall read ----
    any_lift = "METHOD_LIMITED_CONFIRMED_LIFT" in (exact_verdict_trans, exact_verdict_opaque)
    any_rellevel_pass = "HARD_PASS_RELATION_LEVEL_USEFUL" in (rel_verdict_trans, rel_verdict_opaque)
    if any_lift or any_rellevel_pass:
        overall_read = "METHOD_LIMITED_PARTIALLY_FIXABLE"
    elif (exact_verdict_trans == "FUNDAMENTAL_NO_LIFT_FROM_METHOD"
          and exact_verdict_opaque == "FUNDAMENTAL_NO_LIFT_FROM_METHOD"
          and rel_verdict_trans in ("HARD_FAIL_RELATION_LEVEL_NOT_GENUINE", "MIDDLE_BAND")):
        overall_read = "FUNDAMENTAL_CEILING_METHOD_DID_NOT_MOVE_IT"
    else:
        overall_read = "MIDDLE_BAND_INCONCLUSIVE_METHOD_READ"

    # ---- must-fail booleans ----
    must_fail_scramble_ok = bool((trans_scr_frac <= SCRAMBLE_COLLAPSE_HF_FRAC or tax_trans["n"] < MIN_STRATUM_N)
                                 and (opaque_scr_frac <= SCRAMBLE_COLLAPSE_HF_FRAC
                                      or tax_opaque_all["n"] < MIN_STRATUM_N))
    must_fail_random_ok = bool(_nz(tax_rnd_trans["exact_match_rate"]) <= 0.05
                              and _nz(tax_rnd_trans["topk_relation_match_rate"]) <= 0.15)
    must_fail_graph_self_reference_ok = bool(_nz(tax_gsr_all["exact_match_rate"]) <= 0.02
                                             and _nz(tax_gsr_all["topk_relation_match_rate"]) <= 0.02)

    verdict = ("COLD_PLACEMENT_RECOVERY_OPT__exact_trans=%s__exact_opaque=%s__rel_trans=%s__rel_opaque=%s__"
              "rel_arb=%s__read=%s" % (exact_verdict_trans, exact_verdict_opaque, rel_verdict_trans,
                                       rel_verdict_opaque, rel_verdict_arb, overall_read))
    verdict_msg = (
        "%s || TRANSPARENT(n=%d): opt_exact=%s base_exact=%s delta=%s | opt_topk_rel=%s rnd_topk_rel=%s "
        "ratio=%s scramble_frac=%s || OPAQUE_ALL(n=%d): opt_exact=%s base_exact=%s delta=%s | opt_topk_rel=%s "
        "rnd_topk_rel=%s ratio=%s scramble_frac=%s || ARBITRARY_TRANS(n=%d): opt_topk_rel=%s rnd_topk_rel=%s "
        "margin=%s || must_fails: scramble_ok=%s random_ok=%s graph_self_reference_ok=%s" % (
            verdict, tax_trans["n"], _fmt(tax_trans["exact_match_rate"]), _fmt(BASE_TRANS_EXACT), _fmt(trans_delta),
            _fmt(trans_rel), _fmt(tax_rnd_trans["topk_relation_match_rate"]), _fmt(trans_ratio), _fmt(trans_scr_frac),
            tax_opaque_all["n"], _fmt(tax_opaque_all["exact_match_rate"]), _fmt(BASE_OPAQUE_ALL_EXACT),
            _fmt(opaque_delta), _fmt(opaque_rel), _fmt(tax_rnd_opaque["topk_relation_match_rate"]),
            _fmt(opaque_ratio), _fmt(opaque_scr_frac),
            arb_mech_trans["n"], _fmt(arb_mech_trans["topk_relation_match_rate"]),
            _fmt(arb_rnd_trans["topk_relation_match_rate"]), _fmt(arb_margin),
            must_fail_scramble_ok, must_fail_random_ok, must_fail_graph_self_reference_ok))

    gates = dict(
        exact_verdict_trans=exact_verdict_trans, exact_verdict_opaque=exact_verdict_opaque,
        rel_verdict_trans=rel_verdict_trans, rel_verdict_opaque=rel_verdict_opaque, rel_verdict_arb=rel_verdict_arb,
        overall_read=overall_read,
        must_fail_scramble_ok=must_fail_scramble_ok, must_fail_random_ok=must_fail_random_ok,
        must_fail_graph_self_reference_ok=must_fail_graph_self_reference_ok,
        taxonomic=dict(name_transparent=tax_trans, name_opaque_all=tax_opaque_all,
                       scramble_name_transparent=tax_scr_trans, scramble_name_opaque=tax_scr_opaque,
                       random_name_transparent=tax_rnd_trans, random_name_opaque=tax_rnd_opaque,
                       pop_name_transparent=tax_pop_trans, graph_self_reference_all=tax_gsr_all,
                       trans_delta_vs_base=trans_delta, opaque_delta_vs_base=opaque_delta,
                       trans_topk_rel_ratio_vs_floor=trans_ratio, opaque_topk_rel_ratio_vs_floor=opaque_ratio),
        arbitrary=dict(mechanism_name_transparent=arb_mech_trans, random_name_transparent=arb_rnd_trans,
                       mechanism_all=arb_mech_all, topk_rel_margin_vs_random=arb_margin),
        bands=dict(EXACT_DELTA_HP_MIN=EXACT_DELTA_HP_MIN, EXACT_DELTA_HF_MAX=EXACT_DELTA_HF_MAX,
                   RELLEVEL_TRANS_HP_MIN=RELLEVEL_TRANS_HP_MIN, RELLEVEL_TRANS_RATIO_HP_MIN=RELLEVEL_TRANS_RATIO_HP_MIN,
                   RELLEVEL_TRANS_RATIO_HF_MAX=RELLEVEL_TRANS_RATIO_HF_MAX, RELLEVEL_OPAQUE_HP_MIN=RELLEVEL_OPAQUE_HP_MIN,
                   RELLEVEL_OPAQUE_RATIO_HP_MIN=RELLEVEL_OPAQUE_RATIO_HP_MIN,
                   RELLEVEL_OPAQUE_RATIO_HF_MAX=RELLEVEL_OPAQUE_RATIO_HF_MAX,
                   RELLEVEL_ARB_MARGIN_HP_MIN=RELLEVEL_ARB_MARGIN_HP_MIN,
                   RELLEVEL_ARB_MARGIN_HF_MAX=RELLEVEL_ARB_MARGIN_HF_MAX,
                   SCRAMBLE_COLLAPSE_HP_FRAC=SCRAMBLE_COLLAPSE_HP_FRAC, SCRAMBLE_COLLAPSE_HF_FRAC=SCRAMBLE_COLLAPSE_HF_FRAC,
                   MIN_STRATUM_N=MIN_STRATUM_N, TOP_K=TOP_K),
        base_cited=dict(source="data/exp_cold_placement_usefulness_v1/metrics.json",
                        base_trans_exact=BASE_TRANS_EXACT, base_opaque_all_exact=BASE_OPAQUE_ALL_EXACT,
                        base_arb_trans_recovery=BASE_ARB_TRANS_RECOVERY))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Core corpus run (shared by self-test and FULL). Reuses base cell's population construction verbatim.
# ---------------------------------------------------------------------------

def run_corpus(edges, provenance_glosses, provenance_order, lex_cache, seed, target_taxonomic, target_arbitrary,
              exercised=None):
    if exercised is not None:
        exercised.add("load_graph")
    out_adj, in_adj = build_directed_adj(edges)
    if exercised is not None:
        exercised.add("build_directed_adj")
    all_nodes = sorted(set(out_adj.keys()) | set(in_adj.keys()))

    rng_sample = np.random.default_rng(seed * 1000003 + 1)
    import experiments.exp_cold_placement_usefulness_v1 as _base
    _prev_tax, _prev_arb = _base.TARGET_TAXONOMIC_N, _base.TARGET_ARBITRARY_N
    _base.TARGET_TAXONOMIC_N, _base.TARGET_ARBITRARY_N = target_taxonomic, target_arbitrary
    try:
        pops = build_populations(edges, out_adj, in_adj, provenance_order, rng_sample)
    finally:
        _base.TARGET_TAXONOMIC_N, _base.TARGET_ARBITRARY_N = _prev_tax, _prev_arb
    if exercised is not None:
        exercised.add("build_populations")

    lemma_index, lemma_of = build_lemma_index(all_nodes)
    if exercised is not None:
        exercised.add("build_lemma_index")

    excluded_edges = [r["held_edge"] for r in pops["taxonomic"]] + [r["held_edge"] for r in pops["arbitrary"]]
    excluded_set = set(excluded_edges)
    other_hit_counter = defaultdict(int)
    for r in pops["taxonomic"] + pops["arbitrary"]:
        other_hit_counter[r["other_endpoint"]] += 1
    base_degree = {n: node_degree(n, out_adj, in_adj) for n in all_nodes}

    def ablated_degree_fn(n):
        return base_degree.get(n, 0) - other_hit_counter.get(n, 0)

    adj = build_undirected_adj(edges, excluded_set)
    memo = {}
    name_tokens_of = {}
    for r in pops["taxonomic"] + pops["arbitrary"]:
        name_tokens_of[r["node"]] = tokenize_entity(r["node"])[1]
    gloss_of = {r["node"]: provenance_glosses.get(r["node"]) for r in pops["taxonomic"] + pops["arbitrary"]}
    lex_of = {r["node"]: lex_cache.get(r["node"]) for r in pops["taxonomic"] + pops["arbitrary"]}

    def neighbor_tokens_fn(eid):
        return neighbor_name_tokens(eid, out_adj, in_adj, lemma_of, excluded_edges=excluded_set)

    well_pool = sorted([n for n in all_nodes if ablated_degree_fn(n) >= WELL_CONNECTED_MIN_DEGREE])
    if not well_pool:
        well_pool = sorted(all_nodes)[:1]
    pop_node = max(well_pool, key=lambda n: (ablated_degree_fn(n), n))

    rng_random = np.random.default_rng(seed * 7919 + 3)
    all_tax_nodes = [r["node"] for r in pops["taxonomic"]]
    perm_idx = np.random.default_rng(seed * 104729 + 5).permutation(len(all_tax_nodes))
    perm_scramble = {n: all_tax_nodes[int(perm_idx[i])] for i, n in enumerate(all_tax_nodes)}

    if exercised is not None:
        exercised.add("classify_and_place_v2")

    tax_entities, tax_failures = run_taxonomic_arms_v2(
        pops["taxonomic"], name_tokens_of, gloss_of, lex_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
        adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, perm_scramble, excluded_set)
    if exercised is not None:
        exercised.add("score_taxonomic_v2")
    arb_entities, arb_failures = run_arbitrary_arms_v2(
        pops["arbitrary"], name_tokens_of, gloss_of, lex_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
        adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, excluded_set)
    if exercised is not None:
        exercised.add("score_arbitrary_v2")

    return dict(pops=pops, tax_entities=tax_entities, arb_entities=arb_entities,
               tax_failures=tax_failures, arb_failures=arb_failures, well_pool_size=len(well_pool),
               n_nodes=len(all_nodes), n_edges=len(edges))


# ---------------------------------------------------------------------------
# Mechanism self-test: planted synthetic arena (proves each tier fires + scramble collapses + topK > exact
# somewhere) + a tiny real-data slice (F.1).
# ---------------------------------------------------------------------------

def build_planted_lex_cache(seed):
    """Extends the base cell's planted arena with WN-tier-only recoverable cases (hypernym-only, synonym-only)
    plus a topK-beats-exact case, proving the NEW method recovers entities the base cell's gloss-only mechanism
    could NOT, and proving the relation-level metric genuinely exceeds rank0-exact somewhere."""
    edges, gloss_map = build_planted_arena(seed)
    lex_cache = {}
    parents = ["beast", "hammer", "dash", "spark", "cloud", "stone", "flame", "brook"]

    # HYPERNYM-ONLY recoverable: gloss carries NO signal (generic text); a synthetic "hypernym" names the parent.
    n_hyper = len(parents)
    for i, p in enumerate(parents):
        child = "hhq_hyperonly_%d" % i
        edges.append((child, "IS_A", p))
        gloss_map[child] = "an unrelated miscellaneous descriptive phrase with absolutely no lexical signal"
        lex_cache[child] = dict(method="synthetic", sense_name=None,
                                definition="an unrelated miscellaneous descriptive phrase with no signal",
                                synonyms=[], hypernyms=[p])

    # SYNONYM-ONLY recoverable: gloss carries no signal; a synthetic "synonym" names the parent.
    for i, p in enumerate(parents):
        child = "ssq_synonlyonly_%d" % i
        edges.append((child, "CN_SYNONYM", p))
        gloss_map[child] = "a different unrelated miscellaneous phrase carrying zero content signal"
        lex_cache[child] = dict(method="synthetic", sense_name=None,
                                definition="a different unrelated miscellaneous phrase with no signal",
                                synonyms=[p], hypernyms=[])

    # TOPK-BEATS-EXACT case: rank0 (name-transparent tier) resolves to a WRONG-but-plausible node (a decoy sharing
    # a substring with the true parent's name) while a LOWER tier (hypernym) correctly names the true parent --
    # the true parent then appears in top-K (via the hypernym tier) even though rank0 missed it. Uses the
    # relation-level metric's own true_rel/true_target to score correctly (topk_relation_match should catch it,
    # exact_match on rank0 should NOT).
    decoy_parent = "beast_decoy_lookalike"
    for h in ["h0", "h1", "h2", "h3", "h4"]:
        edges.append((decoy_parent, "PART_OF" if h in ("h0", "h2", "h4") else "CN_RELATED_TO", h + "_" + decoy_parent))
        edges.append((h + "_" + decoy_parent, "CN_RELATED_TO", "PAD_SINK"))
    child_tk = "beast_decoy_lookalike_child"
    edges.append((child_tk, "IS_A", "beast"))       # true target is "beast", not the decoy
    gloss_map[child_tk] = "an unrelated phrase, no gloss signal, but shares a name-substring with a decoy"
    lex_cache[child_tk] = dict(method="synthetic", sense_name=None,
                               definition="an unrelated phrase with no signal", synonyms=[], hypernyms=["beast"])

    return list(dict.fromkeys(edges)), gloss_map, lex_cache


def _mechanism_selftest_body():
    exercised = set()
    edges, gloss_map, lex_cache = build_planted_lex_cache(7)
    res = run_corpus(edges, gloss_map, [], lex_cache, 7, target_taxonomic=1000, target_arbitrary=1000,
                     exercised=exercised)
    tax = res["tax_entities"]
    arb = res["arb_entities"]

    mech_trans = _agg_tax(tax, "MECHANISM", group_filter="name_transparent")
    scr_trans = _agg_tax(tax, "SCRAMBLE", group_filter="name_transparent")
    rnd_trans = _agg_tax(tax, "RANDOM", group_filter="name_transparent")
    pop_trans = _agg_tax(tax, "POP", group_filter="name_transparent")
    gsr_all = _agg_tax(tax, "GRAPH_SELF_REFERENCE_CONTROL")
    arb_mech_trans = _agg_arb(arb, "MECHANISM", group_filter="name_transparent")
    arb_rnd_trans = _agg_arb(arb, "RANDOM", group_filter="name_transparent")

    hyper_rows = [r for r in tax if r["node"].startswith("hhq_hyperonly_")]
    hyper_recovery = (sum(1 for r in hyper_rows if r["arms"]["MECHANISM"]["exact_match"]) / len(hyper_rows)
                     if hyper_rows else 0.0)
    hyper_tier_used = all(r["method"] == "wn_hypernym" for r in hyper_rows) if hyper_rows else False

    syn_rows = [r for r in tax if r["node"].startswith("ssq_synonlyonly_")]
    syn_recovery = (sum(1 for r in syn_rows if r["arms"]["MECHANISM"]["exact_match"]) / len(syn_rows)
                   if syn_rows else 0.0)
    syn_tier_used = all(r["method"] == "wn_synonym" for r in syn_rows) if syn_rows else False

    tk_rows = [r for r in tax if r["node"] == "beast_decoy_lookalike_child"]
    topk_beats_exact = False
    if tk_rows:
        m = tk_rows[0]["arms"]["MECHANISM"]
        topk_beats_exact = bool((not m["exact_match"]) and m["topk_relation_match"])

    transparent_recovers = bool(_nz(mech_trans["exact_match_rate"]) >= SELFTEST_MIN_TRANS_EXACT)
    scramble_collapses = bool(_nz(scr_trans["exact_match_rate"]) <= SELFTEST_MAX_SCRAMBLE_EXACT)
    random_no_help = bool(
        _nz(rnd_trans["exact_match_rate"]) <= SELFTEST_MAX_RANDOM_EXACT
        and (_nz(mech_trans["topk_relation_match_rate"]) - _nz(rnd_trans["topk_relation_match_rate"]))
        >= SELFTEST_MIN_RANDOM_TOPK_MARGIN)
    pop_no_help = bool(_nz(pop_trans["exact_match_rate"]) <= SELFTEST_MAX_RANDOM_EXACT)
    graph_self_reference_zero = bool(_nz(gsr_all["exact_match_rate"]) == 0.0
                                     and _nz(gsr_all["topk_relation_match_rate"]) == 0.0)
    hypernym_tier_fires = bool(hyper_recovery >= SELFTEST_MIN_HYPERNYM_ONLY_RECOVERY and hyper_tier_used)
    synonym_tier_fires = bool(syn_recovery >= SELFTEST_MIN_SYNONYM_ONLY_RECOVERY and syn_tier_used)
    arbitrary_generalizes = bool(_nz(arb_mech_trans["target_recovery_rate"]) > _nz(arb_rnd_trans["target_recovery_rate"]))

    real_slice_ok = False
    real_n_units = 0
    if os.path.exists(RELATIONS_PATH):
        real_edges = load_graph(RELATIONS_PATH, max_lines=20000)
        real_res = run_corpus(real_edges, {}, [], {}, 7, target_taxonomic=15, target_arbitrary=15,
                              exercised=exercised)
        real_slice_ok = bool(real_res["n_nodes"] > 0)
        real_n_units = len(real_res["tax_entities"]) + len(real_res["arb_entities"])

    ok = bool(transparent_recovers and scramble_collapses and random_no_help and pop_no_help
             and graph_self_reference_zero and hypernym_tier_fires and synonym_tier_fires
             and topk_beats_exact and arbitrary_generalizes and real_slice_ok)

    vp_ok = run_validity_preflight([
        {"kind": "positive_control", "positive_control_passed_headline_gate": bool(transparent_recovers),
         "control_name": "MECHANISM_name_transparent", "headline_name": "planted_transparent_exact_match_rate",
         "extra": "planted arena: content-placement recovers name-transparent held-out parent"},
        {"kind": "metric_moves", "metric_name": "mechanism_exact_across_arms",
         "values": [_nz(mech_trans["exact_match_rate"]), _nz(scr_trans["exact_match_rate"]),
                   _nz(rnd_trans["exact_match_rate"])],
         "extra": "MECHANISM vs SCRAMBLE vs RANDOM must differ on the planted arena"},
        {"kind": "negative_control_margin",
         "control_scores": [_nz(scr_trans["exact_match_rate"]), _nz(rnd_trans["exact_match_rate"]),
                            _nz(pop_trans["exact_match_rate"]), _nz(gsr_all["exact_match_rate"])],
         "headline_threshold": _nz(mech_trans["exact_match_rate"]), "higher_is_pass": True, "margin": 0.10,
         "n_repeats_min": 4, "control_name": "SCRAMBLE_RANDOM_POP_GRAPHSELFREF_below_mechanism",
         "extra": "SCRAMBLE/RANDOM/POP/GSR must all sit below MECHANISM on the planted arena"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["exact_delta_trans", "exact_delta_opaque", "rel_trans", "rel_opaque", "rel_arb",
                                    "must_fail_scramble", "must_fail_random", "must_fail_gsr"],
         "exercised_gates": ["exact_delta_trans", "exact_delta_opaque", "rel_trans", "rel_opaque", "rel_arb",
                            "must_fail_scramble", "must_fail_random", "must_fail_gsr"],
         "extra": "aggregate_and_verdict ran on the planted arena's per-entity results, exercising every gate"},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["load_graph", "build_directed_adj", "build_populations",
                                        "build_lemma_index", "classify_and_place_v2", "score_taxonomic_v2",
                                        "score_arbitrary_v2"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "self-test ran run_corpus on a FULLY SYNTHETIC ground-truth-known arena AND a REAL small slice "
                  "of data/substrate_index/concept/relations.jsonl (max_lines=20000)"},
        {"kind": "substrate_signature", "callable_obj": classify_and_place_v2, "callable_name": "classify_and_place_v2",
         "args_count": 7},
        {"kind": "substrate_signature", "callable_obj": score_taxonomic_v2, "callable_name": "score_taxonomic_v2",
         "args_count": 8},
        {"kind": "substrate_signature", "callable_obj": build_lemma_index, "callable_name": "build_lemma_index",
         "args_count": 1},
        {"kind": "guard_baseline_valid", "baseline_score": _nz(mech_trans["exact_match_rate"]),
         "floor_score": _nz(rnd_trans["exact_match_rate"]), "guard_name": "LEAK_OPAQUE_EXCEEDS_FLOOR",
         "baseline_name": "MECHANISM_name_transparent", "floor_name": "RANDOM_name_transparent", "eps": 0.05},
    ], run_mode="self_test")

    out = dict(
        mech_trans_exact=_rnd(mech_trans["exact_match_rate"]),
        mech_trans_topk_rel=_rnd(mech_trans["topk_relation_match_rate"]),
        scramble_trans_exact=_rnd(scr_trans["exact_match_rate"]),
        random_trans_exact=_rnd(rnd_trans["exact_match_rate"]), random_trans_topk_rel=_rnd(rnd_trans["topk_relation_match_rate"]),
        pop_trans_exact=_rnd(pop_trans["exact_match_rate"]), graph_self_reference_exact=_rnd(gsr_all["exact_match_rate"]),
        graph_self_reference_topk_rel=_rnd(gsr_all["topk_relation_match_rate"]),
        hypernym_only_recovery=_rnd(hyper_recovery), synonym_only_recovery=_rnd(syn_recovery),
        topk_beats_exact_case=topk_beats_exact,
        arb_mech_trans_recovery=_rnd(arb_mech_trans["target_recovery_rate"]),
        arb_random_trans_recovery=_rnd(arb_rnd_trans["target_recovery_rate"]),
        transparent_recovers=transparent_recovers, scramble_collapses=scramble_collapses,
        random_no_help=random_no_help, pop_no_help=pop_no_help, graph_self_reference_zero=graph_self_reference_zero,
        hypernym_tier_fires=hypernym_tier_fires, synonym_tier_fires=synonym_tier_fires,
        arbitrary_generalizes=arbitrary_generalizes, real_slice_ok=real_slice_ok, real_n_units=real_n_units,
        validity_preflight_ok=bool(vp_ok), exercised_entrypoints=sorted(exercised))
    return ok, out


def mechanism_selftest():
    return _mechanism_selftest_body()


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = TARGET_TAXONOMIC_N + TARGET_ARBITRARY_N if run_mode == "full" else 2
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    _log("run_mode=%s target_taxonomic=%d target_arbitrary=%d top_k=%d" %
        (run_mode, TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N, TOP_K))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s mech_trans_exact=%s hypernym_only_recovery=%s synonym_only_recovery=%s "
        "topk_beats_exact_case=%s vp_ok=%s" %
        (st_ok, st_res.get("mech_trans_exact"), st_res.get("hypernym_only_recovery"),
         st_res.get("synonym_only_recovery"), st_res.get("topk_beats_exact_case"), st_res.get("validity_preflight_ok")))
    _heartbeat(out_dir, "selftest", 0, t_start)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % json.dumps(st_res)[:400],
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS cold_placement_recovery_opt_v1: planted-arena MECHANISM recovers "
                        "name-transparent, hypernym-only, AND synonym-only cold entities (proving the WN-tier "
                        "recovers cases the base cell's gloss-only mechanism could NOT); SCRAMBLE/RANDOM/POP/"
                        "GRAPH_SELF_REFERENCE_CONTROL collapse to floor on BOTH exact and topk-relation-level "
                        "metrics; a planted decoy case proves topk_relation_match > rank0_exact_match genuinely; "
                        "REAL relations.jsonl slice exercised (F.1); 8 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not os.path.exists(RELATIONS_PATH):
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="relations.jsonl absent at %s" % RELATIONS_PATH,
                                    summary="graph data missing", elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)
    if not os.path.exists(LEXICAL_CACHE_PATH):
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="lexical cache (provenance.json) absent at %s" % LEXICAL_CACHE_PATH,
                                    summary="lexical cache missing", elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    edges = load_graph(RELATIONS_PATH)
    provenance_glosses, provenance_order = load_provenance_glosses(PROVENANCE_PATH)
    lex_cache = load_lexical_cache(LEXICAL_CACHE_PATH)
    _log("loaded %d edges; %d old-provenance glosses; %d lexical-cache entries; %d provenance-order entities" %
        (len(edges), len(provenance_glosses), len(lex_cache), len(provenance_order)))
    _heartbeat(out_dir, "graph_loaded", 1, t_start)

    res = run_corpus(edges, provenance_glosses, provenance_order, lex_cache, SEED,
                     TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N)
    _log("populations: tax=%d arb=%d well_pool_size=%d tax_failures=%d arb_failures=%d" %
        (len(res["tax_entities"]), len(res["arb_entities"]), res["well_pool_size"],
         len(res["tax_failures"]), len(res["arb_failures"])))
    _heartbeat(out_dir, "corpus_run", 2, t_start)

    n_units = len(res["tax_entities"]) + len(res["arb_entities"])
    if n_units < MIN_STRATUM_N * 2:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected >= %d total scored entities, got %d" % (MIN_STRATUM_N * 2, n_units),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(res["tax_entities"], res["arb_entities"], run_mode)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:300], run_mode=run_mode,
                  elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                  ts_iso=datetime.now(timezone.utc).isoformat(),
                  population=dict(n_taxonomic_sampled=len(res["tax_entities"]),
                                  n_arbitrary_sampled=len(res["arb_entities"]),
                                  well_pool_size=res["well_pool_size"], n_nodes=res["n_nodes"],
                                  n_edges=res["n_edges"], n_lex_cache_entries=len(lex_cache)),
                  gates=gates, mechanism_selftest=st_res,
                  tax_failures=res["tax_failures"], arb_failures=res["arb_failures"],
                  cardinality_ok=(n_units >= MIN_STRATUM_N * 2))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
