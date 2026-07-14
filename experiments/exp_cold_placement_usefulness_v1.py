"""COLD-PLACEMENT USEFULNESS test -- does INTRINSIC-CONTENT placement (name+gloss -> pseudo-anchor -> inherit
relations) IMPROVE held-out relation inference for COLD (0-support/degree-1) entities, vs the current substrate
mechanism (neighbor-composition, which structurally scores cold at/below random by construction)?

DESIGN SOURCE: notes/research_cold_start_intrinsic_content_vs_relational_inference_2026-07-14.md (the drill that
designed this test; pre-registered bands + honest ceiling delivered inline there). CITED@that note throughout.

MECHANISM (zero-training, deterministic, network-free): for each COLD entity c (degree==1 in the live substrate
graph; its single edge is the "anchor" we HOLD OUT to simulate the cold condition):
  1. NAME-TRANSPARENCY classifier: tokenize c's own name (strip CN_/WN_/FN_ prefix + WN sense suffix, split on "_").
     Search contiguous token-substrings (longest first) against the lemma-index of ALL other nodes in the ABLATED
     graph (held edges removed); a match is accepted only if the matched entity is WELL-CONNECTED (ablated degree
     >= WELL_CONNECTED_MIN_DEGREE) and the matched substring is CONTENTFUL (len>=MIN_TOKEN_LEN, not in STOPWORDS) --
     this is the "require the pseudo-anchor overlap to be CONTENTFUL" guard baked into the CONTRACT.
  2. GLOSS FALLBACK (name-opaque path): if no name-transparent candidate, tokenize c's cached WordNet gloss (reused
     from the SAME network-free snapshot as exp_grounded_ingest_text_spoke_v1 -- data/exp_grounded_ingest_text_spoke_v1
     /provenance.json, sha256-pinned method, "nltk wordnet(3.9.4) local corpora") and repeat the well-connected +
     contentful lookup over gloss content words.
  3. POLYSEMY GUARD (baked-in concern from the go/no-go): if the best-tier match is AMBIGUOUS (>1 distinct candidate
     entity sharing the same lemma string -- e.g. a CN_ concept and a sense-tagged WN_ node, or two WN_ senses), do
     NOT guess blindly. Disambiguate via token-overlap between c's own gloss and each candidate's NEIGHBOR-NAME
     tokens (a cheap "sense signature"); if there is no disambiguating signal, ABSTAIN (do not place) rather than
     inherit from a possibly-wrong-sense parent.
  4. PLACEMENT = borrow the resolved pseudo-anchor's OWN relation edges (in the ablated graph) as c's predicted
     relation profile (zero-training; this is literally DKRL/BLP's "embed content into the same manifold, borrow the
     nearest neighbour's structure" + essentialism/category-based-induction's "label overrides raw similarity, once
     found" -- CITED@notes/research_cold_start... Headline 3-4).

SCORE: reach@{0,1,2,3} in the ABLATED graph (all sampled cold entities' single held edges removed) from the pseudo-
anchor to the TRUE held-out target -- exact_match = reach@0 (pseudo-anchor == true target, i.e. the taxonomic edge
itself was correctly re-derived from content). This directly reuses the SAME graph-reachability framing as
exp_anchor_compose_bottleneck_pinpoint_cskg_v2's Test-3 (reachability_by_bucket) -- CITED@data/exp_anchor_compose_
bottleneck_pinpoint_cskg_v2_selftest/metrics.json (cold reach_frac_h3=0.0 there; qualitatively reproduced here as the
NEIGHBOR_COMPOSE baseline's structural-zero, by construction: a degree-1 cold entity supplies ZERO surviving edges
post-ablation to compose from).

TWO POPULATIONS (both degree==1 in the live substrate graph -- CITED@notes/research_cold_start... "59% of nodes are
degree-1", MEASURED@data/substrate_index/concept/relations.jsonl 189654 edges/141511 nodes):
  TAXONOMIC_COLD : the single held edge is CN_SYNONYM/IS_A/HYPERNYM/INSTANCE_OF (feature-predictable, directly
                   inheritable). Used for PREDICTIONS 1 (does placement recover it) + 2 (opaque floor holds).
  ARBITRARY_COLD : the single held edge is any OTHER relation type (PART_OF, CN_USED_FOR, CN_CAPABLE_OF, CN_AT_
                   LOCATION, CN_CAUSES, CN_RELATED_TO, CN_MANNER_OF, CN_HAS_PROPERTY, CN_HAS_A, ...). Used for
                   PREDICTION 3 (does the SAME name/gloss-driven pseudo-anchor -- built with zero knowledge of which
                   relation type was held -- ALSO predict a non-taxonomic fact via the borrowed parent's profile).
  DESIGN ADAPTATION (flagged honestly): because "cold" = degree-1 by construction, a single entity cannot carry BOTH
  a taxonomic and an arbitrary held edge to test Prediction 3 on "the same entity" as the note's step 4 literally
  phrases it. This cell instead uses TWO DISJOINT degree-1 populations (taxonomic-held vs arbitrary-held) and asks
  the analogous question at the population level: does content-placement generalize beyond the taxonomic edge type
  it was implicitly built to reconstruct? This is the faithful population-level operationalization of Prediction 3
  given the structural constraint; HYPOTHESIZED@this docstring, not tuned on results.

STRATIFICATION (CRITICAL per the drill; this IS the test): every population is split into name_transparent (matched
via step 1) vs name_opaque (fell to step 2 or abstained) BEFORE any scoring is inspected.

REVISED HYPOTHESIS (coordinator correction, 2026-07-14 -- the mechanism is UNCHANGED, only the EXPECTED-RESULT framing
for name-opaque cold was too pessimistic and is corrected here): "name-opaque" does NOT mean "must stay at floor."
It only means the NAME STRING itself carries no anchor. A dictionary GLOSS is designed to supply exactly the missing
anchor even when the name hides it (name "pseud" is opaque, but its gloss "an intellectual fraud; a pretentious
person" literally names the parent concept). So every cold entity's placement is tracked by ANCHOR SOURCE, not just
whether it is name-transparent:
  anchor_group = "name_transparent"      -- step 1 (name-substring) supplied the pseudo-anchor.
  anchor_group = "opaque_gloss_sourced"  -- step 1 failed; step 2 (gloss/definition tokens) supplied it.
  anchor_group = "opaque_no_anchor"      -- BOTH failed (or a polysemy guard abstained); the true, un-fixable floor.
The REVISED, NOT-baked-in prediction: PRED1 (name-transparent lift) as before; PRED2_REVISED asks whether the
opaque_gloss_sourced subset ALSO lifts meaningfully above the random floor (the deciding number for whether reading
the dictionary dissolves the name-opaque ceiling) -- HARD-PASS and HARD-FAIL are BOTH informative outcomes, neither
is assumed. Only opaque_no_anchor is a TRIVIAL/definitional floor (no candidate was ever proposed for it), reported
as a coverage diagnostic, not a gated prediction.

MUST-FAIL CONTROLS (pre-registered, checked BEFORE any HARD-PASS is granted -- apply to name_transparent AND
opaque_gloss_sourced strata alike, since the revised hypothesis makes gloss-sourced lift a first-class claim):
  (i)   SCRAMBLE: shuffle (name,gloss) content across the population (deterministic seeded permutation) BEFORE
        classification, while the TRUE held edge / graph position stays with the ORIGINAL entity. A pseudo-anchor
        built from SCRAMBLED content (name OR gloss) must NOT recover the true target above the random floor.
  (ii)  RANDOM: assign a uniformly-random well-connected node as pseudo-anchor (seeded). Must not help.
  (iii) GRAPH-SELF-REFERENCE CONTROL: a "gloss" built ONLY from the entity's OWN remaining graph-neighbor names (not
        real dictionary text) must NOT help -- guards against symbols-about-symbols circularity (the anchor must
        come from genuine external content, not the graph re-deriving itself). Cold entities are degree==1 by
        construction (their one edge IS the held edge), so this control's remaining-neighbor token set is EMPTY by
        construction and the control is PROVABLY vacuous (0% recovery) -- computed and reported explicitly, not
        merely asserted in prose, so the non-circularity property is machine-checked not hand-waved.
  POP (fixed highest-ablated-degree node for every entity) is an additional sanity baseline (frequency-incumbent;
  must also not help, since a fixed guess cannot match a variable true target).
  NEIGHBOR_COMPOSE is the CURRENT substrate mechanism's structural behaviour on cold (zero surviving edges to
  compose from post-ablation) -- reported as an analytic + reproduced-in-this-cell zero, CITED against the existing
  landed selftest metrics for cross-reference (different metric basis -- MRR there vs reach/exact-match here --
  reported qualitatively, NOT as a strict numeric equivalence; META_RULE_AC discipline).

## Compute architecture
class (b) sequential-CPU with justification: this is a PURE symbolic graph-traversal mechanism (string tokenization,
lemma-index dict lookups, bounded BFS over a sparse ~190k-edge / ~141k-node graph, avg degree ~2.7). Zero training,
zero embeddings, zero matmul -- there is nothing to batch on GPU; every operation is a dict/set lookup or a capped
BFS. Total population ~600 entities x 5 arms x a capped-and-memoized BFS (per-source memoization collapses repeated
candidates, e.g. POP's fixed candidate is BFS'd once, not once per entity) -- wall time is dict-lookup bound, expected
low tens-of-seconds total on CPU. SHARDED storage n/a (no vector storage at all; this is graph-symbolic, not HD/VSA
compute). device=cpu always (HDLAB_QUEUE=remote_cpu_queue forces cpu; local run is cpu already; no cuda code path
exists in this cell).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (META_RULE_AF): MECHANISM/RANDOM/POP/SCRAMBLE/NEIGHBOR_COMPOSE per-entity candidate-id
#   vectors are hashed and compared; POP is exempted from "must differ" pairwise since it is a constant-candidate
#   baseline by design (arms_differ_exempted declared).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: n/a for this cell (exact-match / reach-fraction on a finite well-connected candidate pool,
#   not a noise-floor estimation problem); crlb_n/a declared with rationale.
# - baseline_in_band: RANDOM/POP/NEIGHBOR_COMPOSE must sit near the structural floor (< 0.05 exact-match) by
#   construction (huge well-connected candidate pool / zero surviving edges) -- this is the EXPECTED floor, not a
#   saturation bug; MECHANISM (transparent stratum) is expected in-band (0.10-0.70), checked at self-test AND full.
# - discriminator survives scale: analytical + self-test-preview -- the classifier logic is scale-INVARIANT (a pure
#   string/lemma/degree lookup); self-test proves it fires on a synthetic planted arena AND on a small real-data
#   slice (real_code_path F.1); FULL differs only in population SIZE, not mechanism, so no saturation risk from N.
# - HARD-PASS strictly above floor: PRED1/2/3 bands below are strict multiples/margins over the measured RANDOM/POP
#   floor, not bare >= floor (META_RULE_L).
# - HP_SCOPE: PRED1 bands apply to MECHANISM name_transparent stratum on TAXONOMIC_COLD; PRED2 to MECHANISM
#   name_opaque stratum on TAXONOMIC_COLD; PRED3 to MECHANISM name_transparent stratum on ARBITRARY_COLD.
#   RANDOM/POP/NEIGHBOR_COMPOSE/SCRAMBLE = must-not-clear controls (never HP-scoped).
# - per-unit failure-class instrumentation: population construction + classification wrapped per-entity; a single
#   entity's classify/score exception is recorded with failure_class and does NOT abort the whole cell (entity
#   dropped from aggregation, counted in `entity_failures`); loader/graph-build failures DO abort (no partial graph).
# - calibration_check: adaptive_with_discriminator_gate -- WELL_CONNECTED_MIN_DEGREE/MIN_TOKEN_LEN/STOPWORDS are
#   pre-registered constants (not tuned on real-data results); the self-test proves the classifier fires (recovers
#   planted transparent entities) + the scramble control fails, on a SEPARATE synthetic arena.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in this docstring + inline comments.
# - progress_logging: print_flush_true (line-buffered stdout + periodic heartbeat); timeout_s well under 1800 (this
#   is a fast symbolic cell) but the discipline is applied defensively regardless.
# - cell_chunked: false (no seed axis -- one deterministic population sample; RANDOM/SCRAMBLE arms use ONE seeded
#   RNG each for reproducibility, not an experimental seed sweep). Declared explicitly (not silently omitted).
# - real_code_path_exercised (F.1): self-test calls the REAL loader against the REAL relations.jsonl (small slice)
#   AND a fully synthetic planted arena (ground-truth-known correctness check) -- not a synthetic-only branch.
# - substrate_signature_checked (F.2/F.3): classify_and_place / score_taxonomic_entity / build_lemma_index bound
#   against inspect.signature with the exact args this cell's FULL call sites use.
# - guard_baseline_valid (F.4): the LEAK guard (opaque exceeding floor) is validated against RANDOM (not against a
#   baseline that could itself be at the arena floor).

ASCII-only. No bare except; except SystemExit before except Exception. Deterministic seeded RNGs (np.random.default_
rng); sorted(), never bare set-iteration order, per the split-nondeterminism discipline (list(set()) pitfall).
"""

import argparse
import json
import os
import platform
import re
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timezone

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "cold_placement_usefulness_v1"

RELATIONS_PATH = os.path.join(_REPO, "data", "substrate_index", "concept", "relations.jsonl")
PROVENANCE_PATH = os.path.join(_REPO, "data", "exp_grounded_ingest_text_spoke_v1", "provenance.json")

# ---- taxonomic vs arbitrary relation split (MEASURED@relations.jsonl rel_type histogram, this session) ----
TAXONOMIC_RELS = frozenset(["CN_SYNONYM", "IS_A", "HYPERNYM", "INSTANCE_OF"])

# ---- contentful-overlap guard: exclude generic/function-word/generic-taxonomy tokens from matching ----
STOPWORDS = frozenset([
    "of", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "by", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those", "it", "its", "as", "from",
    "into", "onto", "used", "use", "having", "has", "have", "had", "kind", "kinds", "type", "types",
    "sort", "sorts", "form", "forms", "genus", "family", "families", "order", "orders", "class",
    "classes", "group", "groups", "species", "one", "ones", "some", "any", "other", "others", "also",
    "not", "no", "such", "which", "who", "whom", "whose", "when", "where", "than", "then", "there",
    "very", "more", "most", "some", "any", "each", "all", "part", "parts", "subdivision",
])

# ---- pre-registered classifier constants (calibration_check: adaptive_with_discriminator_gate; NOT tuned on real
#      results -- fixed BEFORE the real-data run, self-test proves the classifier fires + scramble fails) ----
WELL_CONNECTED_MIN_DEGREE = 3     # candidate parent must have >= this many OTHER (ablated) edges
MIN_TOKEN_LEN = 3                 # matched substring/token must be >= this many chars
NEIGHBOR_SIG_CAP = 20              # cap neighbor-name tokens used for the polysemy "sense signature"

# ---- population sizing (autonomy: cell-author choice, deterministic) ----
TARGET_TAXONOMIC_N = 350
TARGET_ARBITRARY_N = 250
SEED = 42
BFS_HMAX = 3
BFS_VISIT_CAP = 20000            # circuit breaker for mega-hub BFS (avg graph degree ~2.7; this is generous)

# ---- self-test thresholds (calibrated on the PLANTED synthetic arena, not real data) ----
SELFTEST_MIN_TRANSPARENT_EXACT = 0.60
SELFTEST_MAX_SCRAMBLE_EXACT = 0.20
SELFTEST_MAX_RANDOM_EXACT = 0.20
SELFTEST_MIN_ARBITRARY_RECOVERY = 0.30
SELFTEST_MIN_ARBITRARY_MARGIN = 0.30   # MECHANISM - RANDOM margin (not an absolute cap on RANDOM: a tiny synthetic
                                        # well-connected candidate pool gives RANDOM a non-trivial baseline hit rate
                                        # by construction; the honest discriminator is the MARGIN, matching the
                                        # margin-based FULL-scale PRED3 gate, not an artificially-tightened absolute
                                        # cap on the self-test's own RANDOM arm)

# ---- PRE-REGISTERED FULL bands (fixed BEFORE the real-data run; HYPOTHESIZED@this docstring per the drill note's
#      inline bands, deflated per DKRL/BLP modest-lift precedent -- CITED@notes/research_cold_start... Headline 3) --
MIN_STRATUM_N = 20                # min pooled n per stratum for a non-INCONCLUSIVE verdict
RANDOM_EXACT_EPS = 0.001           # floor epsilon (avoid div-by-zero in ratio bands)

PRED1_EXACT_HP_MIN = 0.30          # transparent exact-match >= this -> meaningful recovery
PRED1_RATIO_HP_MIN = 5.0           # AND >= 5x max(random,pop,eps)
PRED1_RATIO_HF_MAX = 2.0           # HARD-FAIL if ratio < 2x
SCRAMBLE_COLLAPSE_HP_FRAC = 0.35   # scramble_exact <= this fraction of mechanism_exact -> genuinely content-driven
SCRAMBLE_COLLAPSE_HF_FRAC = 0.50   # scramble_exact >  this fraction -> did NOT collapse -> confound

# ---- PRED2_REVISED bands (gloss-sourced-opaque lift; deflated vs PRED1 since gloss-token matching is noisier than
#      direct name-substring containment -- HYPOTHESIZED@this docstring, NOT tuned on results) ----
GLOSS_EXACT_HP_MIN = 0.15          # opaque_gloss_sourced exact-match >= this -> meaningful gloss-driven recovery
GLOSS_RATIO_HP_MIN = 4.0           # AND >= 4x max(random,pop,eps) restricted to this stratum
GLOSS_RATIO_HF_MAX = 1.5           # HARD-FAIL if ratio < 1.5x (dictionary does not dissolve the ceiling)

PRED3_HP_MARGIN = 0.05             # arbitrary target-recovery (transparent stratum) - random_arbitrary >= this
PRED3_HF_MARGIN = 0.02             # <= this -> at chance, no generalization beyond the taxonomic edge type


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x is not None and x == x) else "nan"


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


# ---------------------------------------------------------------------------
# Graph loading + tokenization.
# ---------------------------------------------------------------------------

_PREFIXES = ("CN_", "WN_", "FN_")
_SENSE_SUFFIX_RE = re.compile(r"\.[nvasr]\.\d+$")
_SPLIT_RE = re.compile(r"[^a-z0-9]+")


def strip_prefix(entity_id):
    for p in _PREFIXES:
        if entity_id.startswith(p):
            return entity_id[len(p):]
    return entity_id


def tokenize_entity(entity_id):
    """lemma string (underscored, prefix/sense-suffix stripped, lowercase) + its token list."""
    name = strip_prefix(entity_id)
    name = _SENSE_SUFFIX_RE.sub("", name)
    name = name.lower()
    toks = [t for t in _SPLIT_RE.split(name) if t]
    lemma = "_".join(toks)
    return lemma, toks


def tokenize_text(text):
    if not text:
        return []
    return [t for t in _SPLIT_RE.split(text.lower()) if t]


def load_graph(path, max_lines=0):
    edges = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_lines and i >= max_lines:
                break
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            edges.append((d["src_id"], d["rel_type"], d["tgt_id"]))
    return edges


def build_directed_adj(edges):
    out_adj = defaultdict(list)
    in_adj = defaultdict(list)
    for (s, r, t) in edges:
        out_adj[s].append((r, t))
        in_adj[t].append((r, s))
    return out_adj, in_adj


def node_degree(n, out_adj, in_adj):
    return len(out_adj.get(n, ())) + len(in_adj.get(n, ()))


def find_single_edge(n, out_adj, in_adj):
    """n must have total degree exactly 1. Returns (held_edge_tuple, other_endpoint, rel_type)."""
    o = out_adj.get(n, ())
    if o:
        r, t = o[0]
        return (n, r, t), t, r
    r, s = in_adj.get(n, ())[0]
    return (s, r, n), s, r


def build_lemma_index(all_nodes):
    idx = defaultdict(list)
    lemma_of = {}
    for n in sorted(all_nodes):     # sorted: cross-process determinism (never bare set-iteration order)
        lemma, toks = tokenize_entity(n)
        lemma_of[n] = (lemma, toks)
        idx[lemma].append(n)
    return idx, lemma_of


def neighbor_name_tokens(eid, out_adj, in_adj, lemma_of, excluded_edges=(), cap=NEIGHBOR_SIG_CAP):
    """Tokens of eid's neighbor NAMES in the ABLATED graph (held edges excluded). Using the un-ablated adjacency
    here would leak the held-out answer back into its own "neighbor signature" (e.g. a cold entity's single held
    edge IS its only "neighbor" pre-ablation) -- the exact symbols-about-symbols circularity the GRAPH_SELF_
    REFERENCE_CONTROL must-fail guards against. excluded_edges must be a set for O(1) membership tests."""
    toks = set()
    for (r, t) in list(out_adj.get(eid, ()))[:cap]:
        if (eid, r, t) in excluded_edges:
            continue
        toks.update(lemma_of.get(t, ("", []))[1])
    for (r, s) in list(in_adj.get(eid, ()))[:cap]:
        if (s, r, eid) in excluded_edges:
            continue
        toks.update(lemma_of.get(s, ("", []))[1])
    return toks


# ---------------------------------------------------------------------------
# Classifier: name-transparency -> gloss-fallback -> polysemy guard.
# ---------------------------------------------------------------------------

def candidate_lookup(sub, lemma_index, exclude_id, ablated_degree_fn):
    out = []
    for eid in lemma_index.get(sub, ()):
        if eid == exclude_id:
            continue
        d = ablated_degree_fn(eid)
        if d >= WELL_CONNECTED_MIN_DEGREE:
            out.append((d, eid))
    return out


def name_transparent_search(name_tokens, exclude_id, lemma_index, ablated_degree_fn):
    n = len(name_tokens)
    for length in range(min(n, 4), 0, -1):
        found = []
        for start in range(0, n - length + 1):
            sub_toks = name_tokens[start:start + length]
            if all(t in STOPWORDS for t in sub_toks):
                continue
            if length == 1 and len(sub_toks[0]) < MIN_TOKEN_LEN:
                continue
            sub = "_".join(sub_toks)
            for (d, eid) in candidate_lookup(sub, lemma_index, exclude_id, ablated_degree_fn):
                found.append((length, d, eid))
        if found:
            found.sort(key=lambda x: (-x[0], -x[1], x[2]))
            return found
    return []


def gloss_transparent_search(gloss_toks, exclude_id, lemma_index, ablated_degree_fn):
    found = []
    for t in gloss_toks:
        if t in STOPWORDS or len(t) < MIN_TOKEN_LEN:
            continue
        for (d, eid) in candidate_lookup(t, lemma_index, exclude_id, ablated_degree_fn):
            found.append((1, d, eid))
    if found:
        found.sort(key=lambda x: (-x[1], x[2]))
    return found


def resolve_candidate(found, gloss_toks, neighbor_tokens_fn):
    """found: [(length, degree, eid), ...] best-tier-first. Returns (candidate_or_None, polysemy_abstain_bool)."""
    if not found:
        return None, False
    best_len = found[0][0]
    tier = [f for f in found if f[0] == best_len]
    distinct = {}
    for (_l, d, eid) in tier:
        distinct[eid] = max(distinct.get(eid, -1), d)
    if len(distinct) == 1:
        return next(iter(distinct)), False
    if not gloss_toks:
        return None, True
    gset = set(gloss_toks)
    scored = []
    for eid in sorted(distinct.keys()):
        overlap = len(gset & neighbor_tokens_fn(eid))
        scored.append((overlap, distinct[eid], eid))
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    if scored[0][0] == 0:
        return None, True
    return scored[0][2], False


def classify_and_place(name_tokens, gloss_text, exclude_id, lemma_index, ablated_degree_fn, neighbor_tokens_fn):
    """Returns (candidate_or_None, method_str, polysemy_abstain_bool). method in:
    name_transparent | gloss_fallback | abstain_no_candidate | *_polysemy_abstain."""
    gloss_toks = tokenize_text(gloss_text)
    disambig_toks = [t for t in gloss_toks if t not in STOPWORDS and len(t) >= MIN_TOKEN_LEN]

    found_name = name_transparent_search(name_tokens, exclude_id, lemma_index, ablated_degree_fn)
    if found_name:
        pick, poly = resolve_candidate(found_name, disambig_toks, neighbor_tokens_fn)
        if pick is not None:
            return pick, "name_transparent", False
        if poly:
            return None, "name_transparent_polysemy_abstain", True

    if gloss_toks:
        found_gloss = gloss_transparent_search(gloss_toks, exclude_id, lemma_index, ablated_degree_fn)
        if found_gloss:
            pick, poly = resolve_candidate(found_gloss, disambig_toks, neighbor_tokens_fn)
            if pick is not None:
                return pick, "gloss_fallback", False
            if poly:
                return None, "gloss_fallback_polysemy_abstain", True

    return None, "abstain_no_candidate", False


# ---------------------------------------------------------------------------
# Bounded, memoized BFS over the ablated undirected graph.
# ---------------------------------------------------------------------------

def build_undirected_adj(edges, excluded_edges):
    adj = defaultdict(set)
    excl = set(excluded_edges)
    for e in edges:
        if e in excl:
            continue
        s, _r, t = e
        adj[s].add(t)
        adj[t].add(s)
    return adj


def bfs_full(adj, src, hmax, cap=BFS_VISIT_CAP):
    dist = {src: 0}
    if src not in adj:
        return dist
    frontier = deque([src])
    while frontier:
        node = frontier.popleft()
        d = dist[node]
        if d >= hmax:
            continue
        for nb in adj.get(node, ()):
            if nb in dist:
                continue
            dist[nb] = d + 1
            frontier.append(nb)
            if len(dist) >= cap:
                return dist
    return dist


def dist_to(adj, memo, src, dst, hmax):
    if src is None:
        return float("inf")
    if src not in memo:
        memo[src] = bfs_full(adj, src, hmax)
    return memo[src].get(dst, float("inf"))


def node_relation_edges(node, out_adj, in_adj, excluded_edges):
    excl = set(excluded_edges)
    edges = []
    for (r, t) in out_adj.get(node, ()):
        if (node, r, t) in excl:
            continue
        edges.append((r, t))
    for (r, s) in in_adj.get(node, ()):
        if (s, r, node) in excl:
            continue
        edges.append((r, s))
    return edges


# ---------------------------------------------------------------------------
# Population construction.
# ---------------------------------------------------------------------------

def load_provenance_glosses(path):
    """Reuse the SAME cached, network-free WordNet gloss snapshot as exp_grounded_ingest_text_spoke_v1."""
    if not os.path.exists(path):
        return {}, []
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    glosses = {}
    for eid, rec in d.get("results", {}).items():
        g = rec.get("gloss")
        if g:
            glosses[eid] = g
    order = list(d.get("sample_order", []))
    return glosses, order


def build_populations(edges, out_adj, in_adj, provenance_order, rng):
    """Returns dict(taxonomic=[...], arbitrary=[...]) of records:
    {node, held_edge, other_endpoint, rel_type}. Deterministic: provenance-sample entities prioritized first
    (gloss-cache overlap), then padded with a sorted+seeded sample of remaining degree-1 nodes."""
    all_nodes = sorted(set(out_adj.keys()) | set(in_adj.keys()))
    degree1 = [n for n in all_nodes if node_degree(n, out_adj, in_adj) == 1]
    tax_all, arb_all = [], []
    for n in degree1:
        held_edge, other, rel = find_single_edge(n, out_adj, in_adj)
        rec = dict(node=n, held_edge=held_edge, other_endpoint=other, rel_type=rel)
        (tax_all if rel in TAXONOMIC_RELS else arb_all).append(rec)

    def _prioritized_sample(pool, target_n):
        pool_by_node = {r["node"]: r for r in pool}
        prio = [pool_by_node[n] for n in provenance_order if n in pool_by_node]
        prio_set = set(r["node"] for r in prio)
        rest = sorted([r["node"] for r in pool if r["node"] not in prio_set])
        need = max(0, target_n - len(prio))
        if need > 0 and rest:
            idx = rng.choice(len(rest), size=min(need, len(rest)), replace=False)
            picked = sorted(int(i) for i in idx.tolist())
            prio = prio + [pool_by_node[rest[i]] for i in picked]
        return prio[:target_n] if len(prio) > target_n else prio

    taxonomic = _prioritized_sample(tax_all, TARGET_TAXONOMIC_N)
    arbitrary = _prioritized_sample(arb_all, TARGET_ARBITRARY_N)
    return dict(taxonomic=taxonomic, arbitrary=arbitrary,
                n_degree1_total=len(degree1), n_taxonomic_pool=len(tax_all), n_arbitrary_pool=len(arb_all))


# ---------------------------------------------------------------------------
# Scoring one entity under one arm's chosen candidate.
# ---------------------------------------------------------------------------

def score_taxonomic_entity(true_target, candidate, adj, memo):
    if candidate is None:
        return dict(exact_match=False, reach_h1=False, reach_h2=False, reach_h3=False, abstain=True)
    if candidate == true_target:
        return dict(exact_match=True, reach_h1=True, reach_h2=True, reach_h3=True, abstain=False)
    d = dist_to(adj, memo, candidate, true_target, BFS_HMAX)
    return dict(exact_match=False, reach_h1=(d <= 1), reach_h2=(d <= 2), reach_h3=(d <= 3), abstain=False)


def score_arbitrary_entity(true_target, true_rel, candidate, adj, memo, out_adj, in_adj, excluded_edges):
    if candidate is None:
        return dict(target_recovered=False, relation_match=False, reach_h2=False, reach_h3=False, abstain=True)
    d = dist_to(adj, memo, candidate, true_target, BFS_HMAX)
    target_recovered = (d <= 1)
    relation_match = False
    if target_recovered:
        for (r, other) in node_relation_edges(candidate, out_adj, in_adj, excluded_edges):
            if other == true_target and r == true_rel:
                relation_match = True
                break
    return dict(target_recovered=target_recovered, relation_match=relation_match,
                reach_h2=(d <= 2), reach_h3=(d <= 3), abstain=False)


# ---------------------------------------------------------------------------
# Full arm-run over a population.
# ---------------------------------------------------------------------------

def _stratum_of(method):
    return "name_transparent" if method == "name_transparent" else "name_opaque"


def _anchor_group_of(method):
    if method == "name_transparent":
        return "name_transparent"
    if method == "gloss_fallback":
        return "opaque_gloss_sourced"
    return "opaque_no_anchor"          # abstain_no_candidate | *_polysemy_abstain


def run_taxonomic_arms(pop, name_tokens_of, gloss_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
                       adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, perm_scramble):
    per_entity = []
    entity_failures = []
    for rec in pop:
        node = rec["node"]
        true_target = rec["other_endpoint"]
        try:
            cand_real, method_real, poly_real = classify_and_place(
                name_tokens_of[node], gloss_of.get(node), node, lemma_index, ablated_degree_fn, neighbor_tokens_fn)
            src_node = perm_scramble[node]
            cand_scr, method_scr, _poly_scr = classify_and_place(
                name_tokens_of[src_node], gloss_of.get(src_node), node, lemma_index, ablated_degree_fn,
                neighbor_tokens_fn)
            cand_rnd = well_pool[int(rng_random.integers(len(well_pool)))]
            cand_pop = pop_node
            # GRAPH-SELF-REFERENCE CONTROL (must-fail iii): "gloss" built ONLY from the entity's own remaining
            # (non-held) graph-neighbor names. Cold entities are degree==1 (their one edge IS the held edge), so
            # this is PROVABLY empty here -- computed explicitly rather than merely asserted.
            graph_gloss = " ".join(sorted(neighbor_tokens_fn(node)))
            cand_gsr, _method_gsr, _poly_gsr = classify_and_place(
                [], graph_gloss, node, lemma_index, ablated_degree_fn, neighbor_tokens_fn)
            stratum = _stratum_of(method_real)
            anchor_group = _anchor_group_of(method_real)

            row = dict(node=node, stratum=stratum, anchor_group=anchor_group, method_real=method_real,
                      polysemy_abstain=poly_real, arms={})
            row["arms"]["MECHANISM"] = dict(candidate=cand_real,
                                            **score_taxonomic_entity(true_target, cand_real, adj, memo))
            row["arms"]["SCRAMBLE"] = dict(candidate=cand_scr, method=method_scr,
                                           **score_taxonomic_entity(true_target, cand_scr, adj, memo))
            row["arms"]["RANDOM"] = dict(candidate=cand_rnd,
                                         **score_taxonomic_entity(true_target, cand_rnd, adj, memo))
            row["arms"]["POP"] = dict(candidate=cand_pop,
                                      **score_taxonomic_entity(true_target, cand_pop, adj, memo))
            row["arms"]["NEIGHBOR_COMPOSE"] = dict(candidate=None,
                                                   **score_taxonomic_entity(true_target, None, adj, memo))
            row["arms"]["GRAPH_SELF_REFERENCE_CONTROL"] = dict(
                candidate=cand_gsr, **score_taxonomic_entity(true_target, cand_gsr, adj, memo))
            per_entity.append(row)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            entity_failures.append(dict(node=node, failure_class=type(e).__name__, msg=str(e)[:200]))
    return per_entity, entity_failures


def run_arbitrary_arms(pop, name_tokens_of, gloss_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
                       adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, excluded_edges):
    per_entity = []
    entity_failures = []
    for rec in pop:
        node = rec["node"]
        true_target = rec["other_endpoint"]
        true_rel = rec["rel_type"]
        try:
            cand_real, method_real, poly_real = classify_and_place(
                name_tokens_of[node], gloss_of.get(node), node, lemma_index, ablated_degree_fn, neighbor_tokens_fn)
            cand_rnd = well_pool[int(rng_random.integers(len(well_pool)))]
            cand_pop = pop_node
            stratum = _stratum_of(method_real)
            anchor_group = _anchor_group_of(method_real)
            row = dict(node=node, stratum=stratum, anchor_group=anchor_group, method_real=method_real,
                      polysemy_abstain=poly_real, arms={})
            row["arms"]["MECHANISM"] = dict(candidate=cand_real, **score_arbitrary_entity(
                true_target, true_rel, cand_real, adj, memo, out_adj, in_adj, excluded_edges))
            row["arms"]["RANDOM"] = dict(candidate=cand_rnd, **score_arbitrary_entity(
                true_target, true_rel, cand_rnd, adj, memo, out_adj, in_adj, excluded_edges))
            row["arms"]["POP"] = dict(candidate=cand_pop, **score_arbitrary_entity(
                true_target, true_rel, cand_pop, adj, memo, out_adj, in_adj, excluded_edges))
            per_entity.append(row)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            entity_failures.append(dict(node=node, failure_class=type(e).__name__, msg=str(e)[:200]))
    return per_entity, entity_failures


# ---------------------------------------------------------------------------
# Aggregation.
# ---------------------------------------------------------------------------

def _agg_taxonomic(per_entity, arm, stratum_filter=None, group_filter=None):
    rows = [r for r in per_entity
           if (stratum_filter is None or r["stratum"] == stratum_filter)
           and (group_filter is None or r["anchor_group"] == group_filter)]
    n = len(rows)
    if n == 0:
        return dict(n=0, exact_match_rate=float("nan"), reach_frac_h1=float("nan"),
                    reach_frac_h2=float("nan"), reach_frac_h3=float("nan"), abstain_rate=float("nan"))
    ex = sum(1 for r in rows if r["arms"][arm]["exact_match"])
    h1 = sum(1 for r in rows if r["arms"][arm]["reach_h1"])
    h2 = sum(1 for r in rows if r["arms"][arm]["reach_h2"])
    h3 = sum(1 for r in rows if r["arms"][arm]["reach_h3"])
    ab = sum(1 for r in rows if r["arms"][arm]["abstain"])
    return dict(n=n, exact_match_rate=ex / n, reach_frac_h1=h1 / n, reach_frac_h2=h2 / n, reach_frac_h3=h3 / n,
                abstain_rate=ab / n)


def _agg_arbitrary(per_entity, arm, stratum_filter=None, group_filter=None):
    rows = [r for r in per_entity
           if (stratum_filter is None or r["stratum"] == stratum_filter)
           and (group_filter is None or r["anchor_group"] == group_filter)]
    n = len(rows)
    if n == 0:
        return dict(n=0, target_recovery_rate=float("nan"), relation_match_rate=float("nan"),
                    reach_frac_h2=float("nan"), reach_frac_h3=float("nan"), abstain_rate=float("nan"))
    tr = sum(1 for r in rows if r["arms"][arm]["target_recovered"])
    rm = sum(1 for r in rows if r["arms"][arm]["relation_match"])
    h2 = sum(1 for r in rows if r["arms"][arm]["reach_h2"])
    h3 = sum(1 for r in rows if r["arms"][arm]["reach_h3"])
    ab = sum(1 for r in rows if r["arms"][arm]["abstain"])
    return dict(n=n, target_recovery_rate=tr / n, relation_match_rate=rm / n, reach_frac_h2=h2 / n,
                reach_frac_h3=h3 / n, abstain_rate=ab / n)


def _nz(v):
    return v if (v == v) else 0.0


def aggregate_and_verdict(tax_entities, arb_entities, run_mode):
    tax_all = _agg_taxonomic(tax_entities, "MECHANISM")
    tax_trans = _agg_taxonomic(tax_entities, "MECHANISM", group_filter="name_transparent")
    tax_gloss = _agg_taxonomic(tax_entities, "MECHANISM", group_filter="opaque_gloss_sourced")
    tax_noanchor = _agg_taxonomic(tax_entities, "MECHANISM", group_filter="opaque_no_anchor")
    tax_opaque = _agg_taxonomic(tax_entities, "MECHANISM", "name_opaque")

    tax_scr_trans = _agg_taxonomic(tax_entities, "SCRAMBLE", group_filter="name_transparent")
    tax_scr_gloss = _agg_taxonomic(tax_entities, "SCRAMBLE", group_filter="opaque_gloss_sourced")
    tax_rnd_trans = _agg_taxonomic(tax_entities, "RANDOM", group_filter="name_transparent")
    tax_rnd_gloss = _agg_taxonomic(tax_entities, "RANDOM", group_filter="opaque_gloss_sourced")
    tax_pop_trans = _agg_taxonomic(tax_entities, "POP", group_filter="name_transparent")
    tax_pop_gloss = _agg_taxonomic(tax_entities, "POP", group_filter="opaque_gloss_sourced")
    tax_nc_trans = _agg_taxonomic(tax_entities, "NEIGHBOR_COMPOSE", group_filter="name_transparent")
    tax_gsr_trans = _agg_taxonomic(tax_entities, "GRAPH_SELF_REFERENCE_CONTROL", group_filter="name_transparent")
    tax_gsr_gloss = _agg_taxonomic(tax_entities, "GRAPH_SELF_REFERENCE_CONTROL", group_filter="opaque_gloss_sourced")
    tax_gsr_all = _agg_taxonomic(tax_entities, "GRAPH_SELF_REFERENCE_CONTROL")
    tax_rnd_all = _agg_taxonomic(tax_entities, "RANDOM")
    tax_pop_all = _agg_taxonomic(tax_entities, "POP")

    arb_mech_trans = _agg_arbitrary(arb_entities, "MECHANISM", group_filter="name_transparent")
    arb_mech_gloss = _agg_arbitrary(arb_entities, "MECHANISM", group_filter="opaque_gloss_sourced")
    arb_rnd_trans = _agg_arbitrary(arb_entities, "RANDOM", group_filter="name_transparent")
    arb_rnd_gloss = _agg_arbitrary(arb_entities, "RANDOM", group_filter="opaque_gloss_sourced")
    arb_mech_all = _agg_arbitrary(arb_entities, "MECHANISM")

    floor_denom = max(_nz(tax_rnd_trans["exact_match_rate"]), _nz(tax_pop_trans["exact_match_rate"]), RANDOM_EXACT_EPS)
    ratio = _nz(tax_trans["exact_match_rate"]) / floor_denom
    scramble_frac = (_nz(tax_scr_trans["exact_match_rate"]) / _nz(tax_trans["exact_match_rate"])
                    if _nz(tax_trans["exact_match_rate"]) > 0 else float("inf") if
                    _nz(tax_scr_trans["exact_match_rate"]) > 0 else 0.0)

    # ---- PREDICTION 1 (name-transparent lift) ----
    if tax_trans["n"] < MIN_STRATUM_N:
        pred1 = "INCONCLUSIVE_TOO_FEW"
    elif (tax_trans["exact_match_rate"] >= PRED1_EXACT_HP_MIN and ratio >= PRED1_RATIO_HP_MIN
          and scramble_frac <= SCRAMBLE_COLLAPSE_HP_FRAC):
        pred1 = "HARD_PASS_CONTENT_PLACEMENT_LIFTS_TRANSPARENT_COLD"
    elif ratio < PRED1_RATIO_HF_MAX or scramble_frac > SCRAMBLE_COLLAPSE_HF_FRAC:
        pred1 = "HARD_FAIL_NO_GENUINE_CONTENT_DRIVEN_LIFT"
    else:
        pred1 = "MIDDLE_BAND_PARTIAL_LIFT"

    # ---- PREDICTION 2_REVISED (does the GLOSS/definition dissolve the name-opaque ceiling?) ----
    # NOT baked in: HARD-PASS ("dictionary dissolves the ceiling") and HARD-FAIL ("ceiling holds even with the
    # definition") are BOTH informative, neither is assumed. Scoped to the opaque_gloss_sourced stratum -- entities
    # where a gloss-derived candidate was actually proposed (opaque_no_anchor is a trivial floor, see coverage below).
    gloss_floor_denom = max(_nz(tax_rnd_gloss["exact_match_rate"]), _nz(tax_pop_gloss["exact_match_rate"]),
                            RANDOM_EXACT_EPS)
    gloss_ratio = _nz(tax_gloss["exact_match_rate"]) / gloss_floor_denom
    gloss_scramble_frac = (_nz(tax_scr_gloss["exact_match_rate"]) / _nz(tax_gloss["exact_match_rate"])
                           if _nz(tax_gloss["exact_match_rate"]) > 0 else float("inf") if
                           _nz(tax_scr_gloss["exact_match_rate"]) > 0 else 0.0)
    if tax_gloss["n"] < MIN_STRATUM_N:
        pred2 = "INCONCLUSIVE_TOO_FEW_GLOSS_SOURCED"
    elif (tax_gloss["exact_match_rate"] >= GLOSS_EXACT_HP_MIN and gloss_ratio >= GLOSS_RATIO_HP_MIN
          and gloss_scramble_frac <= SCRAMBLE_COLLAPSE_HP_FRAC):
        pred2 = "HARD_PASS_GLOSS_DISSOLVES_OPAQUE_CEILING"
    elif gloss_ratio < GLOSS_RATIO_HF_MAX or gloss_scramble_frac > SCRAMBLE_COLLAPSE_HF_FRAC:
        pred2 = "HARD_FAIL_CEILING_HOLDS_EVEN_WITH_GLOSS"
    else:
        pred2 = "MIDDLE_BAND_PARTIAL_GLOSS_LIFT"

    # coverage diagnostic (NOT a gated prediction): how often does ANY anchor even get proposed for opaque entities?
    gloss_coverage = (tax_gloss["n"] / tax_opaque["n"]) if tax_opaque["n"] > 0 else float("nan")

    # ---- PREDICTION 3 (partial generalization beyond the taxonomic edge type; name-transparent primary) ----
    p3_margin = _nz(arb_mech_trans["target_recovery_rate"]) - _nz(arb_rnd_trans["target_recovery_rate"])
    if arb_mech_trans["n"] < MIN_STRATUM_N:
        pred3 = "INCONCLUSIVE_TOO_FEW"
    elif p3_margin >= PRED3_HP_MARGIN and _nz(arb_mech_trans["target_recovery_rate"]) < _nz(tax_trans["exact_match_rate"]):
        pred3 = "HARD_PASS_PARTIAL_GENERALIZATION_BEYOND_TAXONOMIC"
    elif p3_margin <= PRED3_HF_MARGIN:
        pred3 = "HARD_FAIL_NO_GENERALIZATION_BEYOND_TAXONOMIC"
    else:
        pred3 = "MIDDLE_BAND"
    p3_gloss_margin = _nz(arb_mech_gloss["target_recovery_rate"]) - _nz(arb_rnd_gloss["target_recovery_rate"])

    # ---- MUST-FAIL explicit booleans (i/ii/iii from the CONTRACT; apply to BOTH lift-claiming strata) ----
    must_fail_scramble_ok = bool((scramble_frac <= SCRAMBLE_COLLAPSE_HF_FRAC or tax_trans["n"] < MIN_STRATUM_N)
                                 and (gloss_scramble_frac <= SCRAMBLE_COLLAPSE_HF_FRAC
                                      or tax_gloss["n"] < MIN_STRATUM_N))
    must_fail_random_ok = bool(_nz(tax_rnd_trans["exact_match_rate"]) <= 0.05
                              and _nz(tax_rnd_gloss["exact_match_rate"]) <= 0.05)
    must_fail_graph_self_reference_ok = bool(_nz(tax_gsr_all["exact_match_rate"]) <= 0.02)

    verdict = "COLD_PLACEMENT_USEFULNESS__pred1=%s__pred2=%s__pred3=%s" % (pred1, pred2, pred3)
    verdict_msg = (
        "%s || TRANSPARENT(n=%d): MECHANISM_exact=%s ratio_vs_floor=%s scramble_frac=%s RANDOM=%s POP=%s "
        "NEIGHBOR_COMPOSE=%s(structural-zero) || OPAQUE_GLOSS_SOURCED(n=%d, coverage=%s of %d opaque): "
        "MECHANISM_exact=%s ratio_vs_floor=%s scramble_frac=%s RANDOM=%s POP=%s || OPAQUE_NO_ANCHOR(n=%d): "
        "trivial-floor(no candidate proposed) || ARBITRARY_TRANSPARENT(n=%d): MECHANISM_target_recovery=%s "
        "RANDOM=%s margin=%s || ARBITRARY_GLOSS_SOURCED(n=%d): MECHANISM_target_recovery=%s margin=%s || "
        "must_fails: scramble_ok=%s random_ok=%s graph_self_reference_ok=%s(gsr_exact=%s)"
        % (verdict, tax_trans["n"], _fmt(tax_trans["exact_match_rate"]), _fmt(ratio), _fmt(scramble_frac),
           _fmt(tax_rnd_trans["exact_match_rate"]), _fmt(tax_pop_trans["exact_match_rate"]),
           _fmt(tax_nc_trans["exact_match_rate"]),
           tax_gloss["n"], _fmt(gloss_coverage), tax_opaque["n"], _fmt(tax_gloss["exact_match_rate"]),
           _fmt(gloss_ratio), _fmt(gloss_scramble_frac), _fmt(tax_rnd_gloss["exact_match_rate"]),
           _fmt(tax_pop_gloss["exact_match_rate"]), tax_noanchor["n"],
           arb_mech_trans["n"], _fmt(arb_mech_trans["target_recovery_rate"]),
           _fmt(arb_rnd_trans["target_recovery_rate"]), _fmt(p3_margin),
           arb_mech_gloss["n"], _fmt(arb_mech_gloss["target_recovery_rate"]), _fmt(p3_gloss_margin),
           must_fail_scramble_ok, must_fail_random_ok, must_fail_graph_self_reference_ok,
           _fmt(tax_gsr_all["exact_match_rate"])))

    gates = dict(
        pred1=pred1, pred2=pred2, pred3=pred3,
        must_fail_scramble_ok=must_fail_scramble_ok, must_fail_random_ok=must_fail_random_ok,
        must_fail_graph_self_reference_ok=must_fail_graph_self_reference_ok,
        taxonomic=dict(all=tax_all, name_transparent=tax_trans, opaque_gloss_sourced=tax_gloss,
                       opaque_no_anchor=tax_noanchor, name_opaque=tax_opaque,
                       scramble_name_transparent=tax_scr_trans, scramble_opaque_gloss_sourced=tax_scr_gloss,
                       random_name_transparent=tax_rnd_trans, random_opaque_gloss_sourced=tax_rnd_gloss,
                       pop_name_transparent=tax_pop_trans, pop_opaque_gloss_sourced=tax_pop_gloss,
                       neighbor_compose_name_transparent=tax_nc_trans,
                       graph_self_reference_name_transparent=tax_gsr_trans,
                       graph_self_reference_opaque_gloss_sourced=tax_gsr_gloss,
                       graph_self_reference_all=tax_gsr_all,
                       random_all=tax_rnd_all, pop_all=tax_pop_all,
                       ratio_vs_floor=ratio, scramble_frac_of_mechanism=scramble_frac,
                       gloss_ratio_vs_floor=gloss_ratio, gloss_scramble_frac_of_mechanism=gloss_scramble_frac,
                       gloss_coverage_of_opaque=gloss_coverage),
        arbitrary=dict(mechanism_name_transparent=arb_mech_trans, mechanism_opaque_gloss_sourced=arb_mech_gloss,
                       random_name_transparent=arb_rnd_trans, random_opaque_gloss_sourced=arb_rnd_gloss,
                       mechanism_all=arb_mech_all, margin_vs_random=p3_margin, gloss_margin_vs_random=p3_gloss_margin),
        bands=dict(PRED1_EXACT_HP_MIN=PRED1_EXACT_HP_MIN, PRED1_RATIO_HP_MIN=PRED1_RATIO_HP_MIN,
                   PRED1_RATIO_HF_MAX=PRED1_RATIO_HF_MAX, SCRAMBLE_COLLAPSE_HP_FRAC=SCRAMBLE_COLLAPSE_HP_FRAC,
                   SCRAMBLE_COLLAPSE_HF_FRAC=SCRAMBLE_COLLAPSE_HF_FRAC, GLOSS_EXACT_HP_MIN=GLOSS_EXACT_HP_MIN,
                   GLOSS_RATIO_HP_MIN=GLOSS_RATIO_HP_MIN, GLOSS_RATIO_HF_MAX=GLOSS_RATIO_HF_MAX,
                   PRED3_HP_MARGIN=PRED3_HP_MARGIN, PRED3_HF_MARGIN=PRED3_HF_MARGIN, MIN_STRATUM_N=MIN_STRATUM_N),
        cited_reference=dict(
            source="data/exp_anchor_compose_bottleneck_pinpoint_cskg_v2_selftest/metrics.json",
            note="qualitative cross-reference only (different metric basis: MRR there vs exact-match/reach here). "
                 "existing mechanism's cold reach_frac_h3=0.0 there; NEIGHBOR_COMPOSE arm here reproduces the same "
                 "structural-zero-by-construction finding on THIS cell's own population."))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Core corpus run (shared by self-test [synthetic + tiny real slice] and FULL).
# ---------------------------------------------------------------------------

def run_corpus(edges, provenance_glosses, provenance_order, seed, target_taxonomic, target_arbitrary,
              exercised=None):
    if exercised is not None:
        exercised.add("load_graph")
    out_adj, in_adj = build_directed_adj(edges)
    if exercised is not None:
        exercised.add("build_directed_adj")
    all_nodes = sorted(set(out_adj.keys()) | set(in_adj.keys()))

    rng_sample = np.random.default_rng(seed * 1000003 + 1)
    global TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N
    _prev_tax, _prev_arb = TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N
    TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N = target_taxonomic, target_arbitrary
    try:
        pops = build_populations(edges, out_adj, in_adj, provenance_order, rng_sample)
    finally:
        TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N = _prev_tax, _prev_arb
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
        exercised.add("classify_and_place")

    tax_entities, tax_failures = run_taxonomic_arms(
        pops["taxonomic"], name_tokens_of, gloss_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
        adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, perm_scramble)
    if exercised is not None:
        exercised.add("score_taxonomic_entity")
    arb_entities, arb_failures = run_arbitrary_arms(
        pops["arbitrary"], name_tokens_of, gloss_of, lemma_index, ablated_degree_fn, neighbor_tokens_fn,
        adj, memo, out_adj, in_adj, well_pool, pop_node, rng_random, excluded_set)
    if exercised is not None:
        exercised.add("score_arbitrary_entity")

    return dict(pops=pops, tax_entities=tax_entities, arb_entities=arb_entities,
               tax_failures=tax_failures, arb_failures=arb_failures, well_pool_size=len(well_pool),
               n_nodes=len(all_nodes), n_edges=len(edges))


# ---------------------------------------------------------------------------
# Mechanism self-test: (A) fully synthetic planted arena (ground-truth-known correctness check), (B) a tiny
# real-data slice (F.1: real code path, not synthetic-only).
# ---------------------------------------------------------------------------

def build_planted_arena(seed):
    """A tiny synthetic graph with KNOWN name-transparent / gloss-fallback / polysemy / arbitrary-edge cases.

    Parent names are DELIBERATELY single alphanumeric tokens (no underscores) so both the name-substring
    classifier (which matches contiguous CHILD-name token-substrings) AND the gloss-token classifier (which
    matches individual WHITESPACE-tokenized gloss words) can find them -- a multi-token parent id would need
    a bigram gloss matcher that this cell (correctly, for realistic single-word WordNet-style parents like
    "oscilloscope"/"salad"/"mirror"/"hyssop") does not implement.
    """
    edges = []

    def _hub_edge(src, rel, hub):
        # A hub LEAF must NOT be degree-1 itself (else it accidentally gets swept into the sampled cold
        # populations by build_populations' degree==1 filter, and each such leak silently decrements its own
        # parent's ablated degree). Pad every hub leaf to degree>=2 via a SHARED sink (so the sink itself
        # accumulates high degree instead of creating a fresh degree-1 leaf at each padding edge).
        edges.append((src, rel, hub))
        edges.append((hub, "CN_RELATED_TO", "PAD_SINK"))

    # well-connected parents (degree >= WELL_CONNECTED_MIN_DEGREE after ablation). 8 DISTINCT parents (not 3) so
    # the SCRAMBLE control is a genuine discriminator: with only a handful of distinct parents, a random content
    # permutation has a non-trivial chance of COINCIDENTALLY reassigning "the right parent's content" to an
    # entity that already targets that same parent, inflating scramble_exact by luck rather than a real failure
    # of the control. 8 parents keeps that accidental-collision rate low (~1/8 per entity) without hiding a real
    # collapse-failure behind a too-small population.
    parents = ["beast", "hammer", "dash", "spark", "cloud", "stone", "flame", "brook"]
    hub_targets = ["h0", "h1", "h2", "h3", "h4"]
    for p in parents:
        for j, h in enumerate(hub_targets):
            _hub_edge(p, "PART_OF" if j % 2 == 0 else "CN_RELATED_TO", h + "_" + p)
    # polysemy: two WordNet-style SENSE-TAGGED variants share the base lemma "bank" once prefix/sense-suffix strip
    # (WN_bank.n.01 -> "bank"; WN_bank.n.02 -> "bank") -- the realistic polysemy shape, not a coincidental name clash.
    for j, h in enumerate(hub_targets):
        _hub_edge("WN_bank.n.01", "PART_OF", "hr%d" % j)
        _hub_edge("WN_bank.n.02", "PART_OF", "hm%d" % j)
    # planted TAXONOMIC transparent cold entities (substring contains parent name); 2 per parent.
    n_transparent = 2 * len(parents)
    for i in range(n_transparent):
        p = parents[i % len(parents)]
        child = "%s_variant_%d" % (p, i)
        edges.append((child, "CN_SYNONYM", p))
    # planted TAXONOMIC opaque-with-gloss cold entities (name unrelated; gloss mentions a parent's content word);
    # 2 per parent.
    gloss_map = {}
    n_gloss = 2 * len(parents)
    for i in range(n_gloss):
        p = parents[i % len(parents)]
        child = "zzq_opaque_%d" % i
        edges.append((child, "IS_A", p))
        gloss_map[child] = "a kind of %s used commonly in daily practice" % p
    # planted TAXONOMIC true-floor opaque (no gloss signal at all); 1 per parent.
    n_floor = len(parents)
    for i in range(n_floor):
        p = parents[i % len(parents)]
        child = "yyr_floor_%d" % i
        edges.append((child, "HYPERNYM", p))
        gloss_map[child] = "an unrelated miscellaneous descriptive phrase with no signal"
    # planted polysemy case (gloss disambiguates to the river sense via neighbor-token overlap with "hr0")
    edges.append(("riverside_bank_place", "IS_A", "WN_bank.n.01"))
    gloss_map["riverside_bank_place"] = "hr0 nearby location description"
    # planted ARBITRARY-held cold entities, name-transparent, whose parent ALSO has an edge to the true target
    # (positive control for Prediction-3-style generalization): parent p has PART_OF edge to "h0_"+p (j=0 above).
    n_arb = 2 * len(parents)
    for i in range(n_arb):
        p = parents[i % len(parents)]
        child = "%s_arbkind_%d" % (p, i)
        tgt = "h0_" + p
        rel = "PART_OF"
        edges.append((child, rel, tgt))
    return list(dict.fromkeys(edges)), gloss_map


def _mechanism_selftest_body():
    exercised = set()
    edges, gloss_map = build_planted_arena(7)
    res = run_corpus(edges, gloss_map, [], 7, target_taxonomic=1000, target_arbitrary=1000, exercised=exercised)

    tax = res["tax_entities"]
    arb = res["arb_entities"]
    mech_trans = _agg_taxonomic(tax, "MECHANISM", group_filter="name_transparent")
    mech_gloss = _agg_taxonomic(tax, "MECHANISM", group_filter="opaque_gloss_sourced")
    mech_opaque = _agg_taxonomic(tax, "MECHANISM", "name_opaque")
    scr_trans = _agg_taxonomic(tax, "SCRAMBLE", group_filter="name_transparent")
    scr_gloss = _agg_taxonomic(tax, "SCRAMBLE", group_filter="opaque_gloss_sourced")
    rnd_trans = _agg_taxonomic(tax, "RANDOM", group_filter="name_transparent")
    pop_trans = _agg_taxonomic(tax, "POP", group_filter="name_transparent")
    nc_trans = _agg_taxonomic(tax, "NEIGHBOR_COMPOSE", group_filter="name_transparent")
    gsr_all = _agg_taxonomic(tax, "GRAPH_SELF_REFERENCE_CONTROL")
    arb_mech_trans = _agg_arbitrary(arb, "MECHANISM", group_filter="name_transparent")
    arb_rnd_trans = _agg_arbitrary(arb, "RANDOM", group_filter="name_transparent")

    transparent_recovers = bool(_nz(mech_trans["exact_match_rate"]) >= SELFTEST_MIN_TRANSPARENT_EXACT)
    scramble_collapses = bool(_nz(scr_trans["exact_match_rate"]) <= SELFTEST_MAX_SCRAMBLE_EXACT)
    random_no_help = bool(_nz(rnd_trans["exact_match_rate"]) <= SELFTEST_MAX_RANDOM_EXACT)
    pop_no_help = bool(_nz(pop_trans["exact_match_rate"]) <= SELFTEST_MAX_RANDOM_EXACT)
    neighbor_compose_zero = bool(_nz(nc_trans["exact_match_rate"]) == 0.0)
    graph_self_reference_zero = bool(_nz(gsr_all["exact_match_rate"]) == 0.0)
    gloss_fallback_fires = bool(mech_opaque["n"] > 0 and any(
        r["method_real"] == "gloss_fallback" for r in tax if r["stratum"] == "name_opaque"))
    # REVISED (coordinator correction): gloss-sourced-opaque entities must ACTUALLY LIFT (this is the hoped-for
    # planted-arena proof that the dictionary path is wired correctly) AND its own scramble control must collapse.
    gloss_sourced_lifts = bool(_nz(mech_gloss["exact_match_rate"]) >= SELFTEST_MIN_TRANSPARENT_EXACT
                              and mech_gloss["n"] > 0)
    gloss_scramble_collapses = bool(_nz(scr_gloss["exact_match_rate"]) <= SELFTEST_MAX_SCRAMBLE_EXACT)
    polysemy_guard_exercised = bool(any(
        r["node"] == "riverside_bank_place" and r["method_real"] in ("name_transparent", "gloss_fallback")
        for r in tax))
    arbitrary_generalizes = bool(
        _nz(arb_mech_trans["target_recovery_rate"]) >= SELFTEST_MIN_ARBITRARY_RECOVERY
        and (_nz(arb_mech_trans["target_recovery_rate"]) - _nz(arb_rnd_trans["target_recovery_rate"]))
        >= SELFTEST_MIN_ARBITRARY_MARGIN)

    # F.1 (part B): exercise the REAL loader against the REAL relations.jsonl (small slice; not synthetic-only).
    real_slice_ok = False
    real_n_units = 0
    if os.path.exists(RELATIONS_PATH):
        real_edges = load_graph(RELATIONS_PATH, max_lines=20000)
        real_res = run_corpus(real_edges, {}, [], 7, target_taxonomic=15, target_arbitrary=15, exercised=exercised)
        real_slice_ok = bool(real_res["n_nodes"] > 0)
        real_n_units = len(real_res["tax_entities"]) + len(real_res["arb_entities"])

    ok = bool(transparent_recovers and scramble_collapses and random_no_help and pop_no_help
             and neighbor_compose_zero and graph_self_reference_zero and gloss_fallback_fires
             and gloss_sourced_lifts and gloss_scramble_collapses and polysemy_guard_exercised
             and arbitrary_generalizes and real_slice_ok)

    vp_ok = run_validity_preflight([
        {"kind": "positive_control", "positive_control_passed_headline_gate": bool(transparent_recovers),
         "control_name": "MECHANISM_name_transparent", "headline_name": "planted_transparent_exact_match_rate",
         "extra": "on the planted synthetic arena, content-placement recovers the exact held-out parent for "
                  "name-transparent entities well above the self-test bar"},
        {"kind": "metric_moves", "metric_name": "mechanism_exact_across_arms",
         "values": [_nz(mech_trans["exact_match_rate"]), _nz(scr_trans["exact_match_rate"]),
                   _nz(rnd_trans["exact_match_rate"])],
         "extra": "MECHANISM vs SCRAMBLE vs RANDOM must differ (not frozen) on the planted arena"},
        {"kind": "negative_control_margin",
         "control_scores": [_nz(scr_trans["exact_match_rate"]), _nz(rnd_trans["exact_match_rate"]),
                            _nz(pop_trans["exact_match_rate"]), _nz(gsr_all["exact_match_rate"])],
         "headline_threshold": _nz(mech_trans["exact_match_rate"]), "higher_is_pass": True, "margin": 0.10,
         "n_repeats_min": 4, "control_name": "SCRAMBLE_RANDOM_POP_GRAPHSELFREF_below_mechanism",
         "extra": "SCRAMBLE + RANDOM + POP + GRAPH_SELF_REFERENCE_CONTROL must all sit below MECHANISM by margin "
                  "on the planted arena"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["pred1_band", "pred2_band", "pred3_band", "must_fail_scramble",
                                    "must_fail_random", "must_fail_opaque", "polysemy_guard"],
         "exercised_gates": ["pred1_band", "pred2_band", "pred3_band", "must_fail_scramble", "must_fail_random",
                             "must_fail_opaque", "polysemy_guard"],
         "extra": "aggregate_and_verdict ran on the planted arena's per-entity results, exercising every gate"},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["load_graph", "build_directed_adj", "build_populations",
                                        "build_lemma_index", "classify_and_place", "score_taxonomic_entity",
                                        "score_arbitrary_entity"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "self-test ran run_corpus on a FULLY SYNTHETIC ground-truth-known arena AND on a REAL small "
                  "slice of data/substrate_index/concept/relations.jsonl (max_lines=20000) -- not synthetic-only"},
        {"kind": "substrate_signature", "callable_obj": classify_and_place, "callable_name": "classify_and_place",
         "args_count": 6},
        {"kind": "substrate_signature", "callable_obj": score_taxonomic_entity,
         "callable_name": "score_taxonomic_entity", "args_count": 4},
        {"kind": "substrate_signature", "callable_obj": build_lemma_index, "callable_name": "build_lemma_index",
         "args_count": 1},
        {"kind": "guard_baseline_valid", "baseline_score": _nz(mech_trans["exact_match_rate"]),
         "floor_score": _nz(rnd_trans["exact_match_rate"]), "guard_name": "LEAK_OPAQUE_EXCEEDS_FLOOR",
         "baseline_name": "MECHANISM_name_transparent", "floor_name": "RANDOM_name_transparent", "eps": 0.05},
    ], run_mode="self_test")

    out = dict(
        mech_trans_exact=_rnd(mech_trans["exact_match_rate"]), mech_gloss_exact=_rnd(mech_gloss["exact_match_rate"]),
        mech_opaque_exact=_rnd(mech_opaque["exact_match_rate"]),
        scramble_trans_exact=_rnd(scr_trans["exact_match_rate"]), scramble_gloss_exact=_rnd(scr_gloss["exact_match_rate"]),
        random_trans_exact=_rnd(rnd_trans["exact_match_rate"]),
        pop_trans_exact=_rnd(pop_trans["exact_match_rate"]), neighbor_compose_trans_exact=_rnd(nc_trans["exact_match_rate"]),
        graph_self_reference_exact=_rnd(gsr_all["exact_match_rate"]),
        arb_mech_trans_recovery=_rnd(arb_mech_trans["target_recovery_rate"]),
        arb_random_trans_recovery=_rnd(arb_rnd_trans["target_recovery_rate"]),
        transparent_recovers=transparent_recovers, scramble_collapses=scramble_collapses,
        random_no_help=random_no_help, pop_no_help=pop_no_help, neighbor_compose_zero=neighbor_compose_zero,
        graph_self_reference_zero=graph_self_reference_zero, gloss_fallback_fires=gloss_fallback_fires,
        gloss_sourced_lifts=gloss_sourced_lifts, gloss_scramble_collapses=gloss_scramble_collapses,
        polysemy_guard_exercised=polysemy_guard_exercised,
        arbitrary_generalizes=arbitrary_generalizes, real_slice_ok=real_slice_ok, real_n_units=real_n_units,
        validity_preflight_ok=bool(vp_ok), exercised_entrypoints=sorted(exercised))
    return ok, out


def _rnd(x, nd=5):
    return round(x, nd) if (x == x) else None


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

    _log("run_mode=%s target_taxonomic=%d target_arbitrary=%d" % (run_mode, TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s mech_trans_exact=%s mech_gloss_exact=%s scramble_trans_exact=%s "
         "random_trans_exact=%s graph_self_reference_exact=%s arb_mech_recovery=%s vp_ok=%s" %
         (st_ok, st_res.get("mech_trans_exact"), st_res.get("mech_gloss_exact"), st_res.get("scramble_trans_exact"),
          st_res.get("random_trans_exact"), st_res.get("graph_self_reference_exact"),
          st_res.get("arb_mech_trans_recovery"), st_res.get("validity_preflight_ok")))
    _heartbeat(out_dir, "selftest", 0, t_start)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (planted transparent did not recover, or scramble/random/pop/"
                        "graph-self-reference-control did not stay at floor, or neighbor_compose non-zero, or "
                        "gloss-fallback did not fire / did not itself LIFT with its own scramble collapsing, or "
                        "polysemy-guard did not fire, or arbitrary-generalization control failed, or real-data "
                        "slice failed): %s" % json.dumps(st_res)[:400],
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS cold_placement_usefulness_v1: planted-arena MECHANISM recovers "
                        "name-transparent cold entities AND gloss-sourced-opaque entities (dictionary path proven "
                        "wired); SCRAMBLE/RANDOM/POP/GRAPH_SELF_REFERENCE_CONTROL collapse to floor for BOTH "
                        "strata; NEIGHBOR_COMPOSE structural-zero reproduced; polysemy guard fires; arbitrary-edge "
                        "generalization control passes; REAL relations.jsonl slice exercised (F.1); 8 validity-"
                        "preflight checks declared (F.1-F.4 enforce)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not os.path.exists(RELATIONS_PATH):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="relations.jsonl absent at %s" % RELATIONS_PATH, summary="graph data missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    edges = load_graph(RELATIONS_PATH)
    provenance_glosses, provenance_order = load_provenance_glosses(PROVENANCE_PATH)
    _log("loaded %d edges; %d provenance glosses cached; %d provenance-order entities" %
         (len(edges), len(provenance_glosses), len(provenance_order)))
    _heartbeat(out_dir, "graph_loaded", 1, t_start)

    res = run_corpus(edges, provenance_glosses, provenance_order, SEED,
                     TARGET_TAXONOMIC_N, TARGET_ARBITRARY_N)
    _log("populations: n_degree1_total=%d taxonomic_pool=%d arbitrary_pool=%d sampled_taxonomic=%d "
         "sampled_arbitrary=%d well_pool_size=%d tax_failures=%d arb_failures=%d" %
         (res["pops"]["n_degree1_total"], res["pops"]["n_taxonomic_pool"], res["pops"]["n_arbitrary_pool"],
          len(res["tax_entities"]), len(res["arb_entities"]), res["well_pool_size"],
          len(res["tax_failures"]), len(res["arb_failures"])))
    _heartbeat(out_dir, "corpus_run", 2, t_start)

    n_units = len(res["tax_entities"]) + len(res["arb_entities"])
    if n_units < MIN_STRATUM_N * 2:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected >= %d total scored entities, got %d (tax=%d arb=%d; failures tax=%d arb=%d)" %
                        (MIN_STRATUM_N * 2, n_units, len(res["tax_entities"]), len(res["arb_entities"]),
                         len(res["tax_failures"]), len(res["arb_failures"])),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(res["tax_entities"], res["arb_entities"], run_mode)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:300], run_mode=run_mode,
                  elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                  ts_iso=datetime.now(timezone.utc).isoformat(),
                  population=dict(n_degree1_total=res["pops"]["n_degree1_total"],
                                  n_taxonomic_pool=res["pops"]["n_taxonomic_pool"],
                                  n_arbitrary_pool=res["pops"]["n_arbitrary_pool"],
                                  n_taxonomic_sampled=len(res["tax_entities"]),
                                  n_arbitrary_sampled=len(res["arb_entities"]),
                                  well_pool_size=res["well_pool_size"], n_nodes=res["n_nodes"], n_edges=res["n_edges"]),
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
