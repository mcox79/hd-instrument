# Pre-reg: crutch_retrieval_coverage_diag_v1 (RETRIEVAL COVERAGE diagnosis)

Filed by: exp_dev (Sonnet). Task per Director spawn prompt "Run the RETRIEVAL COVERAGE diagnosis
for the crutch-fade Social IQa arc" + `notes/design_retrieval_coverage_diagnosis_crutch_2026-08-10.md`
(the authoritative design note). This is a DIAGNOSIS: it decides build-vs-supply, not a capability
ship. Does not touch the validated 9-arm consolidation cell.

Prior-work check (`bash tools/substrate_query.sh "spreading activation multi-hop retrieval coverage
CSKG mechanism-miss genuine-gap"`, cosine ranked): top hits (1) `research_to_testbed_FINDINGS_14...`
multi-hop-retrieval capability history (cosine 0.328, historical status log, not a cell) and (2)
`research_drill_optimal_shard_granularity_5x` (cosine 0.322, sharding-strategy note, cross-shard
cost of multi-hop, not directly on point). Read both -- neither is a prior cell on THIS question.
Additionally checked (topically closer, cosine 0.303) `ppr_spreading_activation_cpu_v1`: HARD_FAIL,
recall=0.217 (floor 0.55), a bare PPR random-walk with no hub control, different graph. Also pulled
the closer sibling-domain cell `arc_retrieval_multicue_ppr_discriminative_v1` (ARC/WorldTree, not
CSKG/SIQa, idf-weighted multi-cue PPR + discriminative re-rank): RETRIEVAL_MIDDLE_BAND twice
(recall lift +0.0998 and +0.1030, both in the [0.05,0.15) middle band; shuffled-graph control did
NOT fully collapse toward baseline in either run, D-A~=-0.28 vs wanted <=0.03 -- partial structural
confound; hub-dilution ablation E only marginally load-bearing, C-E~=+0.005). VERDICT: genuinely
novel question for THIS graph (CSKG/SIQa) and THIS objective (mechanism-miss/genuine-gap
classification is new; no prior cell asked "does a path exist" as opposed to "does ranking find
it"), but the sibling MIDDLE_BAND history means the spreading-activation coverage-RECOVERY number
should be treated as a secondary/exploratory measurement calibrated to a realistic (not decisive)
prior, while the primary decisive deliverable is the graph-reachability split itself (a cleaner,
more robust question than end-to-end recall lift). Bands below reflect this.

## What this cell measures (one sentence)

Of the CSKG crutch's 1-hop coverage misses on SIQa dev (74% of dev is gap-flagged, only ~25% of
those are 1-hop-covered per 593fe79b0), how many of the misses have a reachable <=3-hop CSKG path
to the gold answer (MECHANISM-MISS, a retrieval-cue problem) vs no path at all (GENUINE-GAP, a
knowledge-supply problem) vs no grounding at all (SIQa words never map to a CSKG node), and does a
hub-capped spreading-activation multi-hop pull-in (+ the owned CA3 attractor as competitive
readout) recover coverage that is REAL (survives a scrambled-context control) and converts to
comprehension on the newly-covered subset.

## Reconciling the two committed coverage numbers (design note item 1)

`coverage_audit.coverage_rate` (593fe79b0) = 0.2465 = n_covered/n_gap_flagged (1-hop gold-reachable
among ALL 1440 gap-flagged dev items, 74% of the 1954-item dev set -- "gap-flagged" = BoW top-2
margin tied or below the adaptive GATE_THRESH). `retrieval_hit_rate` (e9ee736ec) = 0.446-0.538 =
hit-rate CONDITIONAL on the crutch actually firing as gap_driven's resolving path (i.e. LIBRARY
tier did not already resolve first) -- a strictly smaller, later-stage population than the 1440.
This cell reports BOTH denominators explicitly for every new number (`coverage_denominators` block:
whole-dev fraction of 1954, and gap-flagged-conditional fraction of 1440) to remove the ambiguity.
"Hit" = literal pair_key(ctx_concept, gold_answer_concept) has >=1 CSKG edge (exactly
`dev_crutch_covered`'s existing definition, score_mode=hub_penalized to match the shipped FULL
config) -- reproduced fresh here as an implicit Gate-D positive control (must land within 0.02 abs
of 0.2465 or the harness's own coverage machinery is not being faithfully reproduced).

## Owned organs reused (wire-don't-island; do NOT rebuild)

- `experiments/exp_crutch_fade_social_iqa_v1.py` (IMPORTED, not modified): `canon`, `content_words`,
  `pair_key`, `_edge_weight`, `_hub_penalty`, `load_cskg_index`, `cskg_node_set_from_index`,
  `compute_node_degree`, `extract_concepts`, `load_siqa`, `bow_scores`, `bow_margin`,
  `argmax_tiebreak`, `label_idx`, `crutch_candidate_scores`, `_scramble_partner`,
  `scramble_crutch_candidate_scores`, `HUB_DEGREE_THRESH`, `CSKG_DIR`, `SIQA_DIR`. Zero edits to
  that file -- the validated 9-arm consolidation cell is untouched, satisfying the design note's
  "extend the audit, do not disturb the validated consolidation arms" via a sibling script that
  imports rather than in-place edits (lower blast radius than editing a 1845-line certified file).
- `hdlab/cleanup_family.py::iterative_attractor` (imported, unmodified) -- the CA3/DG attractor
  completion readout, used as an alternative competitive-dynamics decision rule over the
  spreading-activation evidence bundle (query = activation-weighted sum of reached-concept vectors,
  codebook = each candidate's own concept-vector bundle), cross-checked against the raw
  argmax-over-activation rule. Concept vectors are deterministic seeded (hashlib digest, PROT-023 /
  F.5 compliant -- no Python `hash()`), so re-runs are bit-reproducible.
- `HUB_DEGREE_THRESH=500` (from the fade cell, Fault-2-diagnosed) reused unmodified as the
  hub-no-bridge threshold for BFS/activation traversal (see "Hub-bridge control" below) -- same
  constant, same rationale, extended from single-hop scoring to multi-hop traversal.

## New mechanism (the one thing actually built)

1. `build_adjacency(idx)`: node -> list[neighbor] from the existing pair_key-keyed CSKG index (O(E),
   ~1.24M edges).
2. `bfs_classify(ctx_concepts, gold_concepts, adjacency, node_degree, hub_thresh=500, max_hops=3)`:
   multi-source BFS from ctx_concepts. **Hub-bridge control**: ctx_concepts (literal grounded
   context words) are always valid seeds even if they are hub nodes (can't discard real content),
   but a node is only used to EXPAND FURTHER (hop h -> h+1) if its own degree <= hub_thresh -- a hub
   reached at hop h is a dead end for propagation past it (matches Fault-2's finding: hubs are fine
   as endpoints, dangerous as bridges). Classifies each 1-hop miss as GROUNDING_FAILURE (ctx or gold
   concepts empty) / MECHANISM_MISS_K2 / MECHANISM_MISS_K3 / GENUINE_GAP (unreachable at k<=3, not a
   grounding failure).
3. `spreading_activation_scores(...)`: hub-capped weighted BFS, MAX-aggregation (not SUM, avoids the
   same path-count-inflation pathology `_edge_weight`'s `max_trust` fix already addressed for the
   1-hop case) with per-hop `decay=0.4` and per-edge trust weight (`_edge_weight(edges,
   "max_trust")`). Produces a per-candidate score comparable in kind to `crutch_candidate_scores`'s
   1-hop score, usable as a drop-in swap.
4. `ca3_readout(...)`: builds the query/codebook bundle described above and calls
   `iterative_attractor` (temp=4.0 default, matching that module's own documented calibration for
   random Gaussian codebooks) -- reports agreement with the raw argmax rule and accuracy delta.

## Compute architecture

Sequential-CPU, justified by (c) genuine sequential dependency (BFS per dev item) + (b) light total
cost: CSKG load ~1.24M edges (existing harness measures this at low tens of seconds), adjacency
build O(E) once, then per-item bounded BFS (median CSKG degree=1.0, hub-capped expansion keeps
frontiers small) over <=1954 dev items, plus small (D<=256) numpy ops for the CA3 cross-check.
Estimated wall time for FULL: a few minutes (the certified 3-tier FULL cell, which does far more --
5 checkpoints x exposure x 9-arm dev eval with live consolidation state -- lands in 340s; this cell
does a SINGLE pass with no consolidation loop and no checkpoint replication, strictly cheaper).
Storage strategy: no_storage (read-only graph traversal over the existing CSKG index; no new
persisted store). Per compute-proportionality (USER 2026-07-14): a diagnostic reachability
classification does not warrant GPU batching or a multi-hour training fit -- CPU foreground-to-
completion is the cheapest decisive method here.

## Modes

- `--self-test`: tiny synthetic CSKG index with planted 1-hop / 2-hop / 3-hop / disconnected /
  hub-bridge-should-be-blocked / grounding-failure cases; constructs the REAL `iterative_attractor`
  call (real_code_path_exercised) at trivial scale; asserts each case classifies correctly and the
  hub-bridge control actually blocks a planted hub shortcut.
- `--smoke`: full real CSKG index (1.24M edges, same as production -- the graph IS the discriminator,
  cannot be shrunk without invalidating the reachability question) + a capped dev sample (300 items)
  to verify the mechanism fires (n_mechanism_miss > 0, spreadact coverage differs from 1-hop
  coverage, scramble stays low) before committing to the full 1954-item population.
- `--full`: all 1954 dev items (matches the certified harness's population exactly, for direct
  comparability with the committed 0.2465 coverage number).

## HARD-PASS / informational bands (diagnosis framing -- decides routing, not a capability cert)

**Primary (decisive, high-confidence expected -- pure graph reachability, not ranking):**
- `mechanism_miss_fraction` = (n_mechanism_miss_k2 + n_mechanism_miss_k3) / (n_1hop_miss -
  n_grounding_failure). >= 0.50 -> mechanism-miss dominates -> retrieval-cue problem, build case
  strengthens. < 0.50 -> genuine-gap dominates -> knowledge-supply problem.
- `grounding_failure_fraction` = n_grounding_failure / n_1hop_miss, reported independently
  regardless of the above split (a large fraction here means a lemmatizer/stemmer upgrade is a
  distinct, cheap, supplementary fix -- `_stem_variants` is a disclosed non-lemmatizer fallback).

**Secondary (exploratory, calibrated against the ARC-sibling MIDDLE_BAND prior -- do not over-claim
a HARD_PASS here even if the split above is decisive):**
- Coverage recovery real-and-clean: `spreadact_coverage_rate` (gap-flagged denominator) materially
  above 0.2465 AND `scramble_spreadact_coverage_rate` stays within +0.05 abs of
  `scramble_1hop_coverage_rate` (scramble does not spike -- the load-bearing anti-hub-pollution
  control per the design note).
- Comprehension conversion: `newly_covered_spreadact_accuracy` (raw-argmax rule, on the
  covered-by-spreadact-but-not-1hop subset) exceeds `newly_covered_bow_accuracy` on the same subset
  by >0.05 abs, AND `scramble_newly_covered_accuracy` stays within +0.05 abs of scramble's own BoW
  floor on its analogous subset (comprehension gain is real knowledge, not hub-mediated noise).
- Given the ARC-sibling history (MIDDLE_BAND twice, D-control not fully collapsing, hub-ablation
  only marginally load-bearing), a MIDDLE_BAND outcome here (coverage recovers some but scramble is
  not perfectly flat, or comprehension conversion is positive-but-small) is an INFORMATIVE, expected
  result, not a design failure -- report honestly, do not force a HARD_PASS framing.

**Routing recommendation logic** (written to `routing_recommendation` in metrics.json):
- `mechanism_miss_fraction >= 0.50` AND coverage-recovery-real-and-clean AND comprehension-converts
  -> `BUILD_SPREADING_ACTIVATION_RETRIEVAL`.
- `mechanism_miss_fraction >= 0.50` but coverage recovery is thin/confounded (ARC-sibling pattern)
  -> `BUILD_SPREADING_ACTIVATION_RETRIEVAL_WITH_CAUTION` (mechanism-miss says the knowledge is
  there; this prototype's specific recovery method needs iteration, e.g. discriminative re-rank
  per the ARC cell's arm C, before it is decisive).
- `mechanism_miss_fraction < 0.50` -> `SUPPLY_KNOWLEDGE` (broader/other KB; better retrieval cannot
  find a path that structurally does not exist).
- `grounding_failure_fraction >= 0.20` (independent axis) -> additionally flag
  `IMPROVE_GROUNDING_LEMMATIZATION` regardless of the primary route.

## SCHEMA-VET fields

```yaml
cell_chunked: false                     # single cell, no per-seed axis; dev-item loop is the unit
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
arms_differ_verified: true              # real vs scramble 1-hop/spreadact/ca3 digests must differ
deterministic_seeding: true             # hashlib-seeded concept vectors, sorted() iteration, no hash()
progress_logging: print_flush_true      # expected wall time low minutes, but declared defensively
calibration_check: default_ok_for_this_regime  # HUB_DEGREE_THRESH/decay reused verbatim from the
  # certified fade cell (Fault-2), not re-tuned on this data -- avoids p-hacking the coverage number
crlb_n/a: "symbolic graph reachability classification; no capacity/noise-floor discriminator applies"
discriminator_reachability: true        # self-test's planted 2-hop/3-hop cases prove the classes
  # are reachable in principle before the real-data run
compute_architecture: sequential-CPU justification above
storage_strategy: no_storage
real_code_path_exercised: [load_cskg_index, extract_concepts, crutch_candidate_scores,
  iterative_attractor]
substrate_signature_checked: [iterative_attractor]
guard_baseline_valid: n/a (no control-beats-baseline break-guard in this cell)
positive_control_arms: [{arm: coverage_1hop_reproduce, cited_prior_atom: "593fe79b0 coverage_audit",
  cited_prior_metric: 0.2465, tolerance: 0.02}]
functional_requirements:
  - requirement: "classify each 1-hop miss as mechanism-miss vs genuine-gap vs grounding-failure"
    primitive: new bfs_classify (graph-native, no existing primitive covers reachability classing)
  - requirement: "recover coverage via multi-hop retrieval, real not hub-polluted"
    primitive: new spreading_activation_scores + owned iterative_attractor (CA3) + HUB_DEGREE_THRESH
```

## Guardrails (per Director spawn)

Branch `dataprep/mcguffey-graded-corpus` (not main/origin). Targeted commits only (churner active;
never `git add -A`). Resumable per-unit not required (single foreground pass, no multi-hour state to
checkpoint, expected wall time low minutes). Real held-out dev (the certified 1954-item validation
split, no leakage change from the parent cell). VET on disk; scramble is the load-bearing control.
