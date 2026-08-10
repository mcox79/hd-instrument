# Pre-reg: crutch_discriminative_selection_multicue_v1 (DISCRIMINATIVE selection over the crutch
# spreading-activation candidate set)

Filed by: exp_dev (Sonnet). Task per Director spawn prompt "Build + run the DISCRIMINATIVE
selection over the crutch spreading-activation candidate set for the crutch-fade Social IQa arc"
(`notes/design_crutch_discriminative_selection_multicue_convergence_2026-08-10.md`), SHARPENED by an
in-flight coordinator refinement (2026-08-10): the coverage diagnosis's "94% reachable" was
ORACLE-TARGETED (path to the KNOWN gold answer); at k3 even SCRAMBLE reaches gold 53% of the time,
so raw reachability is nearly content-free -- ALL the discriminative signal must be in HOW the
answer is reached, not WHETHER, and the discriminator MUST run NO-ORACLE (choose among SIQa's 3
candidates without ever touching the gold label at scoring time; gold is used only for accuracy
measurement and for fitting Arm C's weights on TRAIN).

Prior-work check (`bash tools/substrate_query.sh "multi-cue convergence discriminator spreading
activation coincidence detection knowledge graph"`, cosine ranked): top hits all cosine<=0.334 and
topically unrelated (channel-orchestration coincidence-detection-window note, a convergence-
acceleration DFT lemma, an unrelated confidence-continuous drill) -- NONE is a prior cell on this
question. Additionally reused the SAME check the coverage-diag cell already ran and disclosed:
`arc_retrieval_multicue_ppr_discriminative_v1` (ARC/WorldTree sibling, idf-weighted multi-cue PPR +
discriminative re-rank) landed RETRIEVAL_MIDDLE_BAND twice with the shuffled-graph control NOT
fully collapsing (D-A~=-0.28 vs wanted <=0.03) -- this is the calibration bar this cell's scramble
control must clear to be taken as decisive, not the mechanism to blindly port (its code is
ARC/WorldTree/SemanticHDEncoder-specific and not directly importable; the REUSED IDEA is
idf/specificity-weighted convergence + discriminative re-rank over a pool, adapted natively here).
VERDICT: genuinely novel cell for CSKG/SIQa; not a rediscovery.

## What this cell measures (one sentence)

Given the coverage diagnosis's finding that spreading-activation RETRIEVAL over the CSKG reaches
almost any candidate within 2-3 hops (including under a scrambled-context control), does a
multi-cue CONVERGENCE / coincidence-detection DISCRIMINATOR -- augmented with question-type
relation-gating (Arm B) and a learned combination of graph-structural features (Arm C) -- pick the
RIGHT reached candidate better than BoW on the crutch-covered subset, WITHOUT the win surviving on a
scrambled CSKG (the decisive control; the raw argmax prototype failed exactly here).

## Owned organs reused (wire-don't-island; read-only imports, no edits)

From `experiments/exp_crutch_fade_social_iqa_v1.py` (validated 9-arm cell, untouched):
`canon, content_words, pair_key, _edge_weight, _hub_penalty, load_cskg_index,
cskg_node_set_from_index, compute_node_degree, relation_family, extract_concepts, load_siqa,
bow_scores, bow_margin, argmax_tiebreak, label_idx, crutch_candidate_scores, _scramble_partner,
scramble_crutch_candidate_scores, HUB_DEGREE_THRESH, CSKG_DIR, SIQA_DIR`.

From `experiments/exp_crutch_retrieval_coverage_diag_v1.py` (coverage diagnosis, untouched):
`build_adjacency, spreading_activation_scores, MAX_VISITED_SAFETY_CAP`.

`arc_retrieval_multicue_ppr_discriminative_v1`'s `discriminative_rerank` margin-scoring IDEA
(top-choice-cos minus 2nd-choice-cos) is the conceptual ancestor of this cell's "strict top1>top2"
firing gate -- adapted, not code-imported (different graph representation: bipartite fact-term PPR
vs typed CSKG concept-pair BFS).

**"Stage-2A retrieve-VALIDATE loop" pointed to by the Director's design note could not be located**
by name in `hdlab/`, `notes/`, `preregs/`, or `experiments/` (grepped all four; zero hits). Per
WIRE-DON'T-ISLAND "read the code not the label" discipline, this cell does NOT import a phantom
organ. The abductive/context-coherence feature Director asked to fold in "if cheap" is instead
implemented NATIVELY (see Feature 4 below) by calling the SAME owned `spreading_activation_scores`
primitive in the REVERSE direction (candidate-seeded backward pass toward context) -- zero new
graph-traversal code, matching the organ's own reuse spirit without trusting an unverified label.

## Mechanism (the new piece)

Evidence-gathering (retrieval) is UNCHANGED across all 3 arms -- ONE VARIABLE = how the SAME
per-cue evidence is COMBINED into a selection. Per dev/train item, per side (real / scramble):

1. **Multi-cue seed selection**: `select_cues` takes the item's grounded context+question concepts,
   dedupes, sorts by ASCENDING node-degree (most specific/least-hub first, since specificity is
   informative and CUES_PER_ITEM=5 must keep the best ones under the compute cap), caps at
   `CUES_PER_ITEM=5`.
2. **Per-cue HOP-1 pass** (relation-typed): for each selected cue, `crutch_candidate_scores([cue],
   ans_concepts_list, idx, "hub_penalized", node_degree)` -- reused UNMODIFIED, called with a
   SINGLETON cue list, giving that cue's own direct-edge score + driving pair_key per candidate.
   `relation_family(idx, pair_key)` recovers the relation type of that specific piece of evidence.
3. **Per-cue MULTI-HOP pass** (k<=2, sharpened per coordinator framing -- k3 lets even scrambled
   cues small-world-bridge to gold, per the coverage diagnosis's own k2-vs-k3 finding, so k<=2 is
   the honest, load-bearing hop budget here): `spreading_activation_scores([cue], ans_concepts_list,
   adjacency, idx, node_degree, hub_thresh=HUB_DEGREE_THRESH, max_hops=2, decay=0.4)` -- reused
   unmodified, singleton-cue-seeded.
4. **Backward abductive/coherence pass** (candidate explains context, not just gets reached by it):
   for candidates with forward convergence >0 only (compute-bounding), call
   `spreading_activation_scores(ans_concepts_list[cand], [ctx_concepts_used], adjacency, idx,
   node_degree, hub_thresh, 2, 0.4)[0][0]` -- SAME primitive, SEEDS and TARGET swapped (candidate's
   own concepts seed the spread, the context concept bundle is the single target group).

Four GRAPH-STRUCTURAL features per candidate (NO lexical/surface features -- the WIQA overfit
guard; every feature is a count/sum/delta over graph reachability, computed identically whether the
item is real content or scrambled):
- `F_conv` = count of distinct cues whose multi-hop score > 0 for this candidate (coincidence
  detection -- the core convergence signal).
- `F_path` = sum of those cues' multi-hop activation values (activation already decays with hop
  count and edge trust, so this sum is inherently a path-directness/specificity score: a cue
  reaching a candidate via a short, high-trust, non-hub path contributes MORE than one reaching via
  a long detour -- reuses the existing decay/trust math rather than inventing new path-enumeration
  code, per compute-proportionality).
- `gate_delta` = `F_conv_gated - F_conv`, where `F_conv_gated` (Arm B only) drops a cue's
  contribution when its HOP-1 relation is KNOWN and NOT in the question-type's relevant relation-
  family set (`classify_question_type(question)` -- pure keyword match on the QUESTION TEXT ONLY,
  never touches context/answers/gold; `RELEVANT_RELATIONS[qtype]` maps FEELING/DESCRIPTION/
  MOTIVATION/PREREQUISITE/NEXT_ACTION/EFFECT/OTHER to CSKG relation-family subsets, e.g. FEELING ->
  {xreact, oreact, xattr, hasproperty, mayhaveproperty}; OTHER -> empty set, so gating degrades
  gracefully to no-op on unclassified questions). HYPOTHESIZED@author-design map, not tuned on
  labels.
- `F_coh` = the backward abductive score (0.0 for candidates with F_conv=0, by construction).

## Three arms (retrieval/evidence UNCHANGED; only the combiner varies)

- **A (pure convergence)**: primary score = `(F_conv, F_path)` lexicographic.
- **B (+relation-gating)**: primary score = `(F_conv_gated, F_path_gated)` lexicographic, where
  `F_path_gated` sums only the un-gated cues' activations.
- **C (learned)**: primary score = `w . [F_conv, F_path, gate_delta, F_coh]` (linear, shared weight
  vector across candidates -- a pointwise learning-to-rank setup, NOT a 3-way classifier, since
  candidate identity A/B/C is not semantically meaningful). Fit by full-batch gradient descent
  (numpy, `np.random.default_rng(seed)` init, softmax cross-entropy over the 3 candidates' scores)
  on TRAIN's gap-flagged + covered (n_covered>=2) items, capped `TRAIN_FIT_CAP` items in fixed file
  order (deterministic, no `hash()`/shuffle). Evaluated on HELD-OUT dev -- gold labels are used ONLY
  to fit `w` and to measure accuracy, never inside the feature functions themselves (no-oracle
  discipline holds for feature computation; supervised fitting of a combiner is standard ML and not
  an oracle leak at inference). **3 seeds {7, 13, 19}** report weight-vector + prediction stability.
  **Critical guard (WIQA lesson)**: the REAL-graph-trained `w` is applied AS-IS to features computed
  on the SCRAMBLE graph at dev-eval time (never retrained on scramble) -- if it still discriminates
  there, it memorized a structural artifact, not real content, and this is reported as an explicit
  fault regardless of the real-side number.
- **Per-feature ablation** (Arm C, seed=7 only, scoped diagnostic): 4 refits each dropping one
  feature (zeroed at both train and eval), reporting covered-subset accuracy delta vs full-feature
  Arm C -- answers "which feature carries the discrimination."

## Augment-not-replace abstain gate (shared across all 3 arms, no-regression by construction)

`covered[cand] = F_conv[cand] > 0` (shared definition across arms so the "covered subset" denominator
is comparable arm-to-arm). `n_covered = count(covered)`. An arm FIRES on an item only if
`n_covered >= 2` (real 3-way competition exists) AND its own primary score has a STRICT top1>top2
winner (parameter-free confidence gate, no magic threshold -- mirrors `argmax_tiebreak`'s existing
tie convention elsewhere in this codebase). Otherwise: ABSTAIN -> BoW prediction (`bow_scores` +
`argmax_tiebreak`, tag=BOW_RESOLVED). BoW is ALWAYS-ON underneath every arm.

## Compute architecture

Sequential-CPU, justified: (a) the retrieval stage IS the coverage-diag's own hub-capped BFS,
already measured at 500s wall for a full 1954-item bundled-cue pass; (b) genuine sequential
per-item dependency (checkpointed via `tools/exp_checkpoint.py`, unit_key=(side, item_idx), per
CLAUDE.md's mandatory multi-unit resumability rule); (c) this cell issues MORE BFS calls per item
(CUES_PER_ITEM singleton passes + a bounded backward pass) than the coverage diag's ONE bundled
pass, so wall time is measured at smoke scale FIRST and the FULL timeout is computed from that
measurement via the standard `1.5 * smoke_wall_s * (FULL_N/smoke_N)` formula -- see "Dispatch"
below. No GPU: pure dict/set BFS over a symbolic graph, not a matmul-heavy primitive; GPU batching
does not apply (same class as the coverage-diag cell it extends). Storage strategy: no_storage
(read-only graph traversal + a tiny in-memory 4-feature linear fit; no new persisted store).

## Modes

- `--self-test`: tiny synthetic CSKG index (~20 nodes) with THREE planted cases: (1) a genuine
  2-cue-convergence candidate vs a 1-cue and a 0-cue candidate (verifies `F_conv`/argmax picks the
  multi-cue-converged one); (2) a relation-gating FLIP case -- candidate A reached by 2 cues via an
  IRRELEVANT relation (wins Arm A on raw count) vs candidate B reached by 1 cue via a RELEVANT
  relation for the planted question type (wins Arm B once gated) -- proves gating changes the
  decision, not just the number; (3) a tiny (~30-row) synthetic Arm-C training set with a clear
  feature->label pattern, verifying GD converges and generalizes to a held-out planted row. Also
  verifies: abstain fires when n_covered<2, arms-differ (A/B/C prediction-vector digests pairwise
  differ on a mixed synthetic dev set), no bare except, SystemExit/KeyboardInterrupt ordering,
  atomic metrics, deterministic (hashlib) seeding.
- `--smoke`: FULL real CSKG index (graph is the discriminator, can't be shrunk) + capped dev
  (`SMOKE_DEV_CAP`) + capped train-fit population (`SMOKE_TRAIN_FIT_CAP`) -- discriminator-preview
  per DISCRIMINATOR-MUST-SURVIVE-SCALE option (A). Verifies: BoW baseline reproduces the base
  cell's own BoW accuracy at this population; each arm fires at a non-trivial rate (n_covered_A/B/C
  each >0 items); real margin and scramble margin both computable and reported; arms differ.
- `--full`: all 1954 dev items (matches the base/coverage-diag cells' population exactly) x 2 sides
  (real, scramble); TRAIN fit population capped `TRAIN_FIT_CAP` (compute-bounding, not a benchmark
  population -- disclosed).

## HARD-PASS / MIDDLE_BAND / HARD-FAIL bands (pre-registered before any full run; per-arm, never
aggregated into one verdict)

Let `CoveredAcc_real(arm)` = accuracy of arm's fired (non-abstained) predictions on the REAL-side
covered subset; `BowAcc_real(subset)` = BoW's own accuracy on that SAME subset. Same notation with
`_scramble` for the scrambled-graph side (subset defined identically on the scramble side using
scramble-computed features). `margin_real(arm) = CoveredAcc_real(arm) - BowAcc_real(subset)`;
`margin_scramble(arm)` analogously.

**HARD_PASS** (arm) requires ALL of:
1. `margin_real(arm) >= +0.05` (real, meaningful lift on the covered subset).
2. `margin_scramble(arm) <= +0.03` (near-chance collapse -- the decisive, load-bearing gate; the raw
   prototype failed exactly here, per the coverage diagnosis).
3. `overall_accuracy(arm, with abstain gate) >= bow_only_overall_accuracy - 0.005` (no-regression;
   augment-not-replace should guarantee this structurally, verified empirically for tie-break edge
   cases).
4. `n_covered_real >= 0.05 * n_dev` (mechanism fires at a non-trivial rate; not a 3-item fluke, per
   META_RULE_K discriminator-fires gate).

**MIDDLE_BAND** (arm) if `margin_real(arm) in [+0.02, +0.05)` AND `margin_scramble(arm) <= +0.03`
AND no-regression holds AND gate 4 holds -- "a scramble-CLEAN win of ANY size is the meaningful
result" per the design note (discrimination on dense commonsense graphs is known-hard; the ARC
sibling never got past MIDDLE_BAND with a non-collapsing control).

**HARD_FAIL** (arm) if ANY of:
- `margin_scramble(arm) > margin_real(arm) - 0.02` (scramble nearly as discriminative as real ->
  non-discriminative; this IS the raw-prototype's exact failure mode from the coverage diagnosis,
  where scramble's own newly-covered accuracy exceeded real's).
- `margin_real(arm) < 0` (arm actively hurts on its own covered subset).
- no-regression fails.
- gate 4 fails (n_covered_real < 0.05*n_dev -- vacuous, never really fires).

Top-level `verdict` (for the queue/dashboard schema) = best across the 3 arms (HARD_PASS if any arm
HARD_PASS, else MIDDLE_BAND if any arm MIDDLE_BAND, else HARD_FAIL); `verdict_msg` spells out each
arm's individual tier + the decisive real/scramble margins per arm -- the per-arm detail in
metrics.json is authoritative, the top-level field is a routing signal only (VET per-axis, never
aggregate).

## Positive control (Gate D)

`positive_control_1hop_coverage`: reproduce `crutch_candidate_scores`'s own 1-hop coverage_rate on
this cell's loaded CSKG index + dev population -- must land within 0.02 abs of the committed
0.2465 (593fe79b0) / re-measured-here value, proving this cell's data loading is faithful before
trusting any downstream number.

## Dispatch (per exp_dev role: local smoke, hand off remote FULL)

Self-test + smoke run LOCAL foreground (`.venv`, `--self-test` then `--smoke`). FULL timeout
computed from the MEASURED smoke wall time via `ceil(1.5 * smoke_wall_s * (1954/SMOKE_DEV_CAP) *
(TRAIN_FIT_CAP/SMOKE_TRAIN_FIT_CAP adjustment))`, reported in the completion hand-off. Per
USER-LOCKED 2026-07-01 ("SMOKE ONLY on local_cpu_queue"), FULL routes to `remote_cpu_queue`
(CPU-only cell, no GPU primitive) -- exp_dev returns the exact `queue_add.sh` command; does not
SCP-ship it.

## SCHEMA-VET fields

```yaml
cell_chunked: true                       # per-(side,item_idx) unit; tools/exp_checkpoint.py
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
arms_differ_verified: true               # A/B/C prediction-vector digests pairwise differ on smoke
deterministic_seeding: true              # hashlib-seeded scramble draws + np.random.default_rng(int
  # seed) for Arm C GD init; sorted() node_list; no hash(), no list(set())
progress_logging: print_flush_true
calibration_check: adaptive_with_discriminator_gate  # GATE_THRESH = median(bow_margin) over dev,
  # computed fresh at run start, applied uniformly to train+dev gap-flagging; RELEVANT_RELATIONS map
  # is HYPOTHESIZED@author-design (relation vocabulary only, never fit on labels)
crlb_n/a: "discrete 3-way classification accuracy on a real benchmark; no capacity/noise-floor
  discriminator threshold applies"
discriminator_reachability: true         # self-test's planted convergence + gating-flip cases prove
  # the mechanism can, in principle, produce the intended discrimination before real-data run
compute_architecture: sequential-CPU justification above
storage_strategy: no_storage
real_code_path_exercised: [load_cskg_index, extract_concepts, crutch_candidate_scores,
  spreading_activation_scores]
substrate_signature_checked: n/a (no KGStore/fit-module live-signature dependency; pure
  function-level reuse of the two owned cells' module-level functions)
guard_baseline_valid: n/a (no control-beats-baseline break-guard in this cell; scramble-collapse
  IS the control, handled by the HARD_FAIL gate above, not a separate break-guard)
positive_control_arms: [{arm: positive_control_1hop_coverage, cited_prior_atom: "593fe79b0
  coverage_audit", cited_prior_metric: 0.2465, tolerance: 0.02}]
functional_requirements:
  - requirement: "score how many DISTINCT context cues converge on each candidate (coincidence
    detection)"
    primitive: new per-cue calls to the OWNED spreading_activation_scores (singleton-seeded)
  - requirement: "gate convergence by question-type relation-relevance"
    primitive: new classify_question_type + RELEVANT_RELATIONS map, gating F_conv via the OWNED
    relation_family lookup
  - requirement: "does the candidate best EXPLAIN the context (abductive), not just get reached"
    primitive: new backward call to the SAME OWNED spreading_activation_scores, seeds/target swapped
  - requirement: "learn the combination weighting from data, held out"
    primitive: new small numpy softmax-GD fit over the 4 graph-structural features (no existing
    primitive covers pointwise LTR over these features)
```

## Guardrails (per Director spawn)

Branch `dataprep/mcguffey-graded-corpus` (not main/origin). ONE variable (the discriminator/combiner
stage; retrieval/evidence-gathering unchanged across arms). Real held-out dev (the certified
1954-item validation split). Targeted commits only (churner active; never `git add -A`). Resumable
per-unit via `tools/exp_checkpoint.py`. VET every arm on disk AS HARD AS a positive, per-axis never
aggregated; scramble-collapse is the load-bearing control for all 3 arms independently.
