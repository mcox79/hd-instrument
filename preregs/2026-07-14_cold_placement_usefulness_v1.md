# Pre-reg: cold_placement_usefulness_v1

Cell: `experiments/exp_cold_placement_usefulness_v1.py`
Design source: `notes/research_cold_start_intrinsic_content_vs_relational_inference_2026-07-14.md` (the drill that
designed this test; bands below are its inline bands, adapted to this cell's exact-match/reach metric and
REVISED per a coordinator correction on 2026-07-14 -- see "Revised hypothesis" below).

Prior-work check (substrate_query.sh, mandatory before authoring): query "cold start entity content placement
pseudo-anchor inheritance zero-anchor relation inference" -> top hit cosine=0.3057 ("entrancement", generic-token
match on "inherit"/"anchor" wording, not a prior cell on this test). NONE at cosine>0.30 that is a genuine
rediscovery. This cell is NOVEL (first attempt at the borrowed-parent content-placement acceptance test).

## Question
Does placing a COLD (0-support/degree-1) entity by INTRINSIC CONTENT (name substring -> pseudo-anchor; falling
back to the cached WordNet gloss/definition when the name is opaque) IMPROVE held-out relation inference, versus
the current substrate mechanism (neighbor-composition, which structurally scores cold at/below random because
cold has zero surviving neighbors to compose from)?

## Revised hypothesis (coordinator correction, 2026-07-14)
Original framing treated "name-opaque" as a fixed retrieval-only floor. CORRECTED: a dictionary GLOSS is designed
to supply exactly the anchor the name hides (e.g. "pseud" is name-opaque, but its gloss "an intellectual fraud; a
pretentious person" literally names the parent). So every placement is tracked by ANCHOR SOURCE:
- `name_transparent` -- the name-substring classifier supplied the anchor.
- `opaque_gloss_sourced` -- the name failed; the gloss/definition supplied the anchor.
- `opaque_no_anchor` -- both failed (or a polysemy guard abstained); the TRUE, un-fixable floor.
PRED2 asks whether `opaque_gloss_sourced` ALSO lifts meaningfully above random -- NOT baked in as a must-fail.

## Mechanism (zero-training, deterministic, network-free)
1. Name-transparency: tokenize the cold entity's own name (strip CN_/WN_/FN_ prefix + WN sense suffix; split on
   `_`); search contiguous token-substrings (longest first) against a lemma-index of all OTHER nodes in the
   ABLATED graph (sampled cold entities' single held edges removed); accept only WELL-CONNECTED matches (ablated
   degree >= 3) with a CONTENTFUL substring (len>=3, not in a ~50-word stopword list).
2. Gloss fallback: if step 1 fails, tokenize the entity's cached WordNet gloss (reused verbatim from
   `data/exp_grounded_ingest_text_spoke_v1/provenance.json`, the same nltk-wordnet(3.9.4) local-corpora,
   network-free, sha256-pinned snapshot) and repeat the well-connected + contentful lookup over content words.
3. Polysemy guard: if the best-tier match is ambiguous (>1 distinct candidate entity sharing the matched lemma,
   e.g. two WN_ sense-tagged nodes), disambiguate via token-overlap between the entity's gloss and each
   candidate's own neighbor-name tokens (in the ABLATED graph); abstain (no guess) if there is no disambiguating
   signal.
4. Placement = borrow the resolved pseudo-anchor's own relation edges (ablated graph) as the predicted profile.

## Score
`exact_match` = pseudo-anchor == true held-out target (the taxonomic edge itself re-derived from content).
`reach@{1,2,3}` = softer graph-distance credit (BFS, ablated graph, capped visited nodes 20000).
For the ARBITRARY-held population: `target_recovered` = true target within 1 hop of the pseudo-anchor;
`relation_match` = pseudo-anchor has an edge of the EXACT held relation type to the exact true target.

## Populations (both degree==1 in the live substrate graph; MEASURED@this run n_degree1_total=83538 of 141511
nodes = 59.0%, matching the drill's cited "59% of nodes are degree-1")
- TAXONOMIC_COLD: single held edge in {CN_SYNONYM, IS_A, HYPERNYM, INSTANCE_OF}. Target n=350 (prioritized from
  the SAME provenance.json lexical-tail sample for gloss-cache overlap, padded with a deterministic seeded sample
  of the remaining pool). MEASURED taxonomic_pool=71389.
- ARBITRARY_COLD: single held edge of any other type (PART_OF, CN_USED_FOR, CN_CAPABLE_OF, CN_AT_LOCATION,
  CN_CAUSES, CN_RELATED_TO, CN_MANNER_OF, CN_HAS_PROPERTY, CN_HAS_A, ...). Target n=250. MEASURED
  arbitrary_pool=12149. DESIGN ADAPTATION (flagged): because "cold"=degree-1 by construction, a single entity
  cannot carry both a taxonomic and an arbitrary held edge, so Prediction 3 is tested on this DISJOINT population
  rather than literally "the same entities" -- the faithful population-level operationalization given the
  structural constraint.

## Must-fail controls (checked BEFORE any HARD-PASS is granted; apply to name_transparent AND
opaque_gloss_sourced strata alike)
(i) SCRAMBLE -- shuffle (name,gloss) content across the taxonomic population (seeded permutation) before
    classification; true held edge/graph position stays with the original entity. Must collapse to floor.
(ii) RANDOM -- uniformly-random well-connected node as pseudo-anchor (seeded). Must not help.
(iii) GRAPH_SELF_REFERENCE_CONTROL -- a "gloss" built ONLY from the entity's own remaining (ablated) graph
     neighbors, not real dictionary text. Cold entities are degree==1 (their one edge IS the held edge), so this
     is PROVABLY empty and the control is computed (not merely asserted) to confirm 0% recovery -- guards against
     symbols-about-symbols circularity.
POP (fixed highest-ablated-degree node) is an additional sanity baseline. NEIGHBOR_COMPOSE (structural zero by
construction; cold entities supply zero surviving edges post-ablation) reproduces the existing substrate
mechanism's cold-bucket behaviour for cross-reference (CITED@data/exp_anchor_compose_bottleneck_pinpoint_cskg_v2_
selftest/metrics.json cold reach_frac_h3=0.0 -- qualitative cross-reference only, different metric basis).

## Pre-registered bands (fixed in the cell BEFORE the FULL run; HYPOTHESIZED, deflated per DKRL/BLP modest-lift
precedent CITED in the design-source note)
- MIN_STRATUM_N = 20 (min pooled n per stratum for a non-INCONCLUSIVE verdict).
- PRED1 (name-transparent): HARD-PASS if exact_match>=0.30 AND ratio-vs-floor>=5x AND scramble_frac<=0.35 of
  mechanism. HARD-FAIL if ratio<2x OR scramble_frac>0.50. Else MIDDLE_BAND.
- PRED2_REVISED (opaque_gloss_sourced): HARD-PASS ("gloss dissolves the ceiling") if exact_match>=0.15 AND
  ratio>=4x AND scramble_frac<=0.35. HARD-FAIL ("ceiling holds even with gloss") if ratio<1.5x OR
  scramble_frac>0.50. Else MIDDLE_BAND. Both outcomes are informative; neither is assumed.
- PRED3 (arbitrary, name-transparent primary): HARD-PASS if margin-vs-random>=0.05 AND recovery is BELOW the
  taxonomic ceiling (partial, graded generalization). HARD-FAIL if margin<=0.02 (at chance). Else MIDDLE_BAND.

## SCHEMA-VET declarations
- `cardinality_ok`: EXPECTED total scored entities >= MIN_STRATUM_N*2 (40); HARD_FAIL_CARDINALITY_BREACH_
  META_RULE_H otherwise.
- `arms_differ_verified`: per-entity candidate vectors differ across MECHANISM/RANDOM/SCRAMBLE/GRAPH_SELF_
  REFERENCE_CONTROL; POP is `arms_differ_exempted` (constant-candidate baseline by design).
- `final_metrics_atomicity`: tmp_replace (write_metrics + os.replace).
- `crlb_n/a`: exact-match/reach-fraction over a finite well-connected candidate pool is not a noise-floor
  estimation problem; no CRLB formula applies.
- `baseline_in_band`: RANDOM/POP/NEIGHBOR_COMPOSE expected near-zero exact-match by construction (huge
  well-connected pool / zero surviving edges) -- this is the expected floor, checked at self-test and FULL.
- `discriminator survives scale`: analytical (scale-invariant string/lemma/degree lookup) + self-test preview on
  a synthetic planted arena AND a small REAL relations.jsonl slice.
- `real_code_path_exercised` (F.1), `substrate_signature_checked` (F.2/F.3), `guard_baseline_valid` (F.4): all
  declared in `mechanism_selftest()`, ENFORCE mode.
- `cell_chunked`: false (no seed axis; one deterministic population sample; RANDOM/SCRAMBLE use one seeded RNG
  each for reproducibility, not an experimental seed sweep).
- `progress_logging`: print_flush_true (defensive; this cell's timeout is well under the 1800s §17 threshold).

## Self-test (landed, verified on disk before the FULL dispatch)
`data/exp_cold_placement_usefulness_v1_selftest/metrics.json`: SELFTEST_PASS. Planted synthetic arena (8 distinct
well-connected parents, single-token names to exercise BOTH the name and gloss classifiers realistically) proves:
MECHANISM recovers 100% of planted name-transparent AND 100% of planted gloss-sourced-opaque entities;
SCRAMBLE/RANDOM/POP/GRAPH_SELF_REFERENCE_CONTROL all collapse to floor (0.0-0.12) with margin; polysemy guard
fires correctly on a WordNet-sense-tagged ambiguous pair; a real (non-synthetic) slice of relations.jsonl is
exercised (F.1); 8 validity-preflight checks pass (F.1-F.4 enforce mode). Two bugs caught and fixed during
self-test iteration (both by the validity-preflight machinery, not manual inspection): (a) synthetic hub-target
leaf nodes were accidentally degree-1 and leaked into the sampled cold populations, silently corrupting parent
ablated-degree counts; (b) the neighbor-token helper used for polysemy disambiguation was reading the UN-ablated
adjacency, so the GRAPH_SELF_REFERENCE_CONTROL scored a false 1.0 (the held edge itself, i.e. the answer, was
being used as its own "neighbor token") -- fixed by threading `excluded_edges` through `neighbor_name_tokens`.

## FULL run (landed locally, deterministic CPU, per USER authorization for this cell)
`data/exp_cold_placement_usefulness_v1/metrics.json`. Verdict:
`COLD_PLACEMENT_USEFULNESS__pred1=MIDDLE_BAND_PARTIAL_LIFT__pred2=MIDDLE_BAND_PARTIAL_GLOSS_LIFT__pred3=MIDDLE_BAND`
See the exp_dev completion report for the full measured numbers and interpretation.

## Remote-CPU canonical-provenance dispatch (exp_dev cannot SCP; orchestrator ships)
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue cold_placement_usefulness_v1 experiments/exp_cold_placement_usefulness_v1.py preregs/2026-07-14_cold_placement_usefulness_v1.md 600
```
timeout_s=600: FULL measured wall time locally = 3.9s (graph load of 189654 edges + full population/classify/score
pass); 600s is a >150x safety margin for remote host variance (this is a pure-CPU, zero-training, zero-GPU cell;
no scaling risk from N since population sizes are fixed constants, not swept).
