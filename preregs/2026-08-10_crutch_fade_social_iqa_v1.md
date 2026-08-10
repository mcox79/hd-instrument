# Pre-reg: crutch_fade_social_iqa_v1 -- the decisive Social IQa fade-curve test

Filed by: exp_dev (Sonnet). Cell design per Director spawn prompt (STEP 3 of the crutch-that-fades
program) + `notes/research_crutch_fade_benchmark_and_test_2026-08-10.md` (DRILL 4, authoritative
design) + `notes/research_crutch_design_and_generalization_2026-08-10.md` (DRILL 1),
`notes/research_brain_scaffolding_that_fades_2026-08-10.md` (DRILL 2),
`notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md` (DRILL 3).

Prior-work check: `bash tools/substrate_query.sh` on "Social IQa fade curve crutch gap-driven
external knowledge consolidation ATOMIC CSKG" -> top hit cosine=0.2764 ("consolidation", a generic
concept node), NONE at cosine>0.30. No prior cell tests this. Genuinely novel, not a rediscovery.

## What this cell tests (one sentence)

As the substrate reads more of Social IQa's train stream, does the CRUTCH (live CSKG query) fire
LESS on repeat need for the SAME knowledge (fade), while held-out dev comprehension RISES above a
measured BoW baseline, and does a SCRAMBLED-content crutch fail to reproduce the gain (proving real
knowledge, not retrieval-machinery, does the work)?

## Pieces composed (all owned; reused, not rebuilt)

- **CRUTCH**: `data/cskg_foundation_v1/edges_shard_*.jsonl` (1,238,686 typed spine edges,
  ATOMIC-dominant, HARD_PASS-certified `exp_cskg_foundation_v1`). Queried as a **plain symbolic
  concept-pair index** (Python dict, NOT `kg_traversal.KGStore`'s Hebbian single-W substrate) --
  see "Deviation from drill 4's literal wording" below.
- **LIBRARY (native promotion)**: `hdlab/grounding_acquisition_loop.py::Library` +
  `consolidation_pass(..., native_store=...)` + `hdlab/hd_fact_store.py::HDFactStore` -- the
  connector Test-A cleared (`experiments/exp_crutch_fade_bank_native_promotion_test_a_v1.py`,
  commit 07339e9c6, MIDDLE_BAND-but-substantively-clears: promote 5/5, guard 0/12 leaks,
  scramble-context escalates). Reused UNMODIFIED, module defaults (MIN_CONFIRM=4,
  PROMOTE_MIN_EXPOSURE=8, PROMOTE_MIN_CONSISTENCY=0.75, schema_thresh=0.10).
- **FLAG**: a predictive_coding-style RELATIVE-margin gate (same SHAPE as
  `hdlab/predictive_coding.py::relative_threshold_gate` -- residual vs a baseline, thresholded) but
  purpose-built for a scalar BoW-margin rather than a bipolar-vector residual (predictive_coding's
  function operates on `observed`/`predicted` np arrays via bit-mismatch fraction; a 3-candidate
  lexical-overlap margin is a different representation shape -- SHAPE-MATCH conceptually, not a
  literal import, disclosed per META_RULE gate C).
- **GENERALIZATION (Level 2, MDL/CA3-DG)**: explicitly NOT wired this cell -- see scoping decision
  below.

## Deviation from drill 4's literal wording (disclosed, justified)

Drill 4 Section 2a names `kg_traversal.KGStore` / `cleanup_family.iterative_attractor` as the
crutch's retrieval engine. This cell instead queries `data/cskg_foundation_v1` as a **plain
symbolic dict** keyed by normalized concept-pair (`canon(token)` on both sides, same
canonicalization the foundation build itself used). Reasons, all from the drills' own text:
1. `kg_traversal.KGStore`'s single-`[1024,1024]`-Hebbian-W substrate is the SAME store that
   Stage-2 sub-test B (2026-08-10) HARD_FAILED at CSKG cardinality (relevant_recall 0.967 at 1K ->
   0.000 by 30K). CSKG has 1.24M edges. Running the fade-test's crutch through that store would
   confound this test's result with an unrelated, already-known, unresolved scale wall -- exactly
   what drill 4 Section 2b/4 names as an open risk to actively AVOID conflating.
2. Drill 4 Section 2b's own scale guard explicitly recommends, for the LIBRARY cache specifically,
   "a plain dict/hash keyed by cue text with cosine-similarity lookup, no Hebbian binding at all...
   the cheaper, lower-risk choice." The same reasoning applies with equal force to the CRUTCH's own
   retrieval when the crutch is a typed-edge KB being queried for exact/near-exact structural
   matches (not a fuzzy-recall task) -- CSKG's edges are already typed and exact; a symbolic lookup
   is the MORE faithful operationalization of "query a knowledge base," not a lesser one.
3. Per compute-proportionality (exp_dev canonical checklist): this is a DIRECTIONAL/DIAGNOSTIC
   question (does crutch-fire-rate drop, does accuracy rise), not a claim about the Hebbian
   substrate's associative-retrieval fidelity -- the cheapest DECISIVE method is the right one.

## Deviation: Level-1-only (item/pair trust-promotion), NOT Level-2 (MDL construction-cue
generalization to unseen classes)

Drill 1 (`research_crutch_design_and_generalization_2026-08-10.md`) distinguishes Level 1
(per-item/per-fact banking, Pinker's "irregular/memorize" pathway) from Level 2 (MDL rule
induction generalizing to a whole UNSEEN class via construction cues, "regular/rule" pathway).
Drill 4's own pre-registered bands (Section 3, reproduced below) test whether **item-level
exposure+consistency-driven trust promotion** (Level 1) produces a real fade+comprehension curve --
they do NOT require whole-class generalization to concept-pairs never directly observed. This cell
therefore wires FLAG + CRUTCH + LIBRARY (Level 1, hd_fact_store trust-promotion) + GUARD, and does
**NOT** additionally wire `hdlab.learner`'s MDL gate or `script_grain_acquisition_loop`'s CA3/DG
clustering (Level 2). This is a scoped, honest choice under the Director's autonomy grant, not an
omission of the letter of the task -- Level 2 is the natural next build if this test clears.

## Mechanism (concrete)

**Concept extraction**: tokenize (`[a-z']+`), stopword-filter, `canon()` each token (byte-identical
normalization to the one `exp_cskg_foundation_v1.py` used to build the store: lowercase, collapse
non-alnum runs to `_`, strip), keep tokens present in the CSKG node set (derived from the union of
all concept-pair-index endpoints -- no separate `nodes.jsonl` parse needed).

**BoW baseline** (arm 1, measured fresh -- Stage-0 discipline): for each of the 3 candidates,
overlap score = `|content_words(context+question) ∩ content_words(candidate)| / (|content_words(candidate)| + 1)`.
Predict argmax; deterministic tie-break to candidate A.

**CRUTCH score** (candidate c): sum over (ctx_concept, c_concept) pairs of
`trust_weight(pair)` (TRUST_HIGH=1.0, TRUST_MID=0.6) for every CSKG spine edge connecting them
(direction-agnostic sorted-pair key). Predict argmax; zero-signal candidates abstain from crutch.

**GAP-FLAG**: `margin = (top1_bow - top2_bow) / (top1_bow + top2_bow + eps)`. Flagged (needs help)
iff `margin == 0` (a TIE, including the all-zero case -- uninformative regardless of magnitude) OR
`margin < GATE_THRESH`. `GATE_THRESH` = median of the STRICTLY-POSITIVE dev margins, computed
fresh at run start (adaptive_with_discriminator_gate calibration_check), logged. **MEASURED@smoke
2026-08-10** (SMOKE_TRAIN_CAP=3000/DEV_CAP=250): >=50% of dev items have a tied top-2 BoW score
(SIQa answers are short non-extractive phrases -- lexical overlap ties often, frequently at zero
for all 3 candidates); a naive median-of-ALL-margins threshold degenerates to exactly 0.0 in this
regime and silently disables margin-based flagging (only the explicit tie/all-zero case still
fires) -- caught by smoke as a harness bug (constant crutch-fire-rate across every checkpoint),
fixed by (a) always flagging ties and (b) calibrating the threshold from the non-tied margins only.

**LIBRARY key**: `pair_key = "min(a,b)::max(a,b)"` (concept-pair identity, relation-agnostic --
disclosed: this drops the specific ATOMIC/ConceptNet relation label from the promoted fact's
identity, storing only "these two concepts are known-linked," which is the exact granularity the
answer-disambiguation task needs and avoids a circular relation-guessing step at query time).
`native_store.store(pair_key, "OUTCOME_POLARITY", "POS", "cskg_crutch", trust_sym)` on promotion.

**Vote-margin/consistency note (disclosed)**: every exposure trace this cell flags is POS-only (a
CSKG edge either exists for a pair or it is never flagged at all -- there is no noisy NEG channel
for a deterministic symbolic fact). Consequently `_vote_margin` is trivially 1.0 for every item
that reaches the bank branch, and `PROMOTE_MIN_CONSISTENCY=0.75` is automatically satisfied. The
two gates that actually discriminate here are (a) **EXPOSURE** (>=8 distinct-context recurrences of
the same concept-pair) and (b) **SCHEMA-COHERENCE** (split-half cosine >= 0.10 across the differing
real narrative contexts the pair recurred in -- this DOES discriminate: a pair whose recurrence
contexts are thematically incoherent will fail to bank). This is a legitimate adaptation of the
connector to a different fact-type (existence-of-relation vs directional-polarity), disclosed per
META_RULE_AC, not hidden.

**Resolution order (GAP-DRIVEN arm)**: BoW-confident -> BOW_RESOLVED. Else: query LIBRARY
(`hd_fact_store.query(pair_key, "OUTCOME_POLARITY")` for every (ctx_concept, candidate_concept)
pair) -> if any candidate has a live LIBRARY hit -> LIBRARY_RESOLVED (predict that candidate;
record the winning `pair_key` as `driving_pair`). Else: query live CRUTCH -> if nonzero signal ->
CRUTCH_RESOLVED (predict argmax; record `driving_pair`; emit an exposure-style episode for that pair
so repeated future confirmation can promote it). Else: ABSTAIN -> fall back to BoW's own argmax
(augment-not-replace, no-regression floor).

**SCRAMBLE-CRUTCH arm**: identical gap-flag schedule. Wherever GAP-DRIVEN would consult the crutch
(same items, same order), this arm instead looks up a deterministically-selected (hashlib-seeded,
not built-in `hash()`) OTHER concept unrelated to the true cue, and treats ITS edges as the "crutch
result." Its own separate Library/HDFactStore is fed the same way during exposure. Must fail to
beat BoW at every checkpoint (Section 3 band 3).

**ALWAYS-CRUTCH-AT-INFERENCE arm**: bypasses gap-flag, queries live CRUTCH on every item at every
checkpoint (diagnostic ceiling, charter-violating, NOT the deployment target). Static across
checkpoints (no library, no exposure-dependence) -- computed once, reported at every checkpoint row
for table uniformity.

**NEVER-CRUTCH arm**: BoW-only, permanently. Its own Library/HDFactStore exists but is NEVER
`flag()`-ed (crutch pull-in disabled) -- confirms it stays empty (leak check) at every checkpoint.
Static across checkpoints.

## Exposure + checkpoints

Source: `data/corpora/social_iqa/hf_dataset/train.jsonl` (33,410 rows, `context` field only,
stripped of question/answers/label -- "texts not labels"). Deterministic order = file order (no
`hash()`, no `list(set())`). Checkpoints at cumulative fractions [0.0, 0.10, 0.25, 0.50, 1.00] of
the (possibly capped, for smoke) exposure stream. At each checkpoint boundary: process the NEW
incremental slice (concept-pair co-occurrence-within-context flags into GAP-DRIVEN's and
SCRAMBLE's own separate Library instances), run 3 `consolidation_pass` sleep-passes (globally
monotonic pass_idx across the whole run), then evaluate the FULL, FROZEN dev set
(`data/corpora/social_iqa/hf_dataset/validation.jsonl`, 1,954 rows, never exposed) for all 5 arms.

## Per-item telemetry

Every dev item, every checkpoint, every arm: `{tag: BOW_RESOLVED|LIBRARY_RESOLVED|CRUTCH_RESOLVED|ABSTAINED,
pred_idx, correct, driving_pair: Optional[str]}`.
`crutch_fire_rate(checkpoint) = count(CRUTCH_RESOLVED)/total`.
`library_resolved_rate(checkpoint) = count(LIBRARY_RESOLVED)/total`.

## NEW (coordinator refinement, mid-build) -- RE-ENCOUNTER FADE RATE

The AGGREGATE crutch-firing-rate can stay flat even with working storage, because dev's 1,954
items are diverse and only a subset's driving concept-pairs will ever recur >=8x in the 33,410-item
train stream (a long tail of pairs legitimately never promotes). Aggregate flatness in that case
would misread a WORKING fade mechanism as a failed one. Measured separately, alongside the two
main curves:

**PRIMARY (natural re-encounter, from dev's fixed-across-checkpoints structure)**: dev is
frozen and re-evaluated at every checkpoint, so the SAME item is a natural repeat-probe.
`cohort0` = dev items GAP-DRIVEN-arm-tagged `CRUTCH_RESOLVED` at checkpoint 0% (genuinely needed
live lookup with zero exposure). For each later checkpoint T, `promoted_pairs(T)` = the set of
`pair_key`s live in GAP-DRIVEN's HDFactStore as of T (`{f.subject for f in store.live_facts()}`).
`eligible(T)` = cohort0 items whose checkpoint-0 `driving_pair` is in `promoted_pairs(T)`.
`re_encounter_fade_rate(T) = count(eligible(T) items tagged LIBRARY_RESOLVED at T) / len(eligible(T))`.
Should climb toward 1.0 as T increases, among the `eligible` cohort -- this is the diagnostic that
isolates a genuine storage/consolidation fault (crutch still fires on ALREADY-PROMOTED knowledge)
from the irreducible long tail (crutch fires on knowledge that never recurred enough to promote).

**FALLBACK (constructed probe), triggered only if `len(eligible(100%)) < 20`** (natural
re-encounters too sparse to read): sample up to 200 `pair_key`s from GAP-DRIVEN's final promoted
set; for each, reuse the FIRST real train context that produced it (`pair_example_context`,
recorded once per pair during exposure) as a synthetic 2-candidate probe (candidate_correct = the
pair's own second concept; candidate_distractor = a deterministically-drawn unrelated concept), run
through GAP-DRIVEN's final-checkpoint resolution state, report
`native_answer_rate = fraction tagged LIBRARY_RESOLVED`. Reported as a clearly-labeled supplementary
mechanism check, not mixed into dev accuracy.

## Leakage audit (Stage-0 item c, drill 4 Section 4)

Sample 100 dev items (deterministic: first 100 by file order). For each, check whether the GOLD
answer's concepts have a DIRECT CSKG spine edge to a context/question concept (checkpoint-0
ALWAYS-CRUTCH-style raw lookup). Report `leakage_rate`. If > 0.30, report the leakage-excluded
subset's curves as the primary read per drill 4's own guidance (disclosed, not silently dropped).

## Pre-registered CAN-FAIL bands (verbatim from drill 4 Section 3 -- the authoritative bands)

**HARD-PASS (all four required):**
1. `crutch_fire_rate` drops checkpoint-0% -> checkpoint-100% by >= 30% relative OR >= 10pp
   absolute (whichever reached first), roughly steep-then-tail (no more than one
   checkpoint-to-checkpoint uptick > 3pp). A roughly linear drop is MIDDLE_BAND-grade even if the
   aggregate threshold clears (shape reported explicitly per-checkpoint, not just endpoint delta).
2. GAP-DRIVEN dev accuracy at 100% beats BoW by >= +0.05 absolute, AND never falls below
   BoW-minus-0.02 at any checkpoint.
3. SCRAMBLE-CRUTCH stays within +/-0.02 of BoW at every checkpoint.
4. Consolidation-fidelity: `LIBRARY_RESOLVED` accuracy >= `CRUTCH_RESOLVED` accuracy - 0.03, at
   every checkpoint where both categories have >= 20 items.

**HARD-FAIL (any one):** `crutch_fire_rate` flat (no drop beyond +/-3pp noise band) AND
`re_encounter_fade_rate` also flat/near-zero on the eligible cohort (this cell's own added
diagnostic: if `crutch_fire_rate` is flat SOLELY because of a healthy long tail, but
`re_encounter_fade_rate` climbs, that is NOT a HARD-FAIL on this criterion -- report both, see
verdict logic); OR comprehension flat/no rise over BoW by 100%; OR SCRAMBLE ties/beats GAP-DRIVEN
at any checkpoint; OR LIBRARY_RESOLVED accuracy collapses relative to CRUTCH_RESOLVED.

**MIDDLE_BAND**: partial per drill 4 Section 3 (efficiency-only, accuracy-only, shape-only), OR
(this cell's addition) aggregate `crutch_fire_rate` flat but `re_encounter_fade_rate` clearly rises
(>= 0.3 absolute from its first measurable checkpoint to 100%) -- report as "storage/promotion
mechanism works; aggregate flatness is the long-tail, not a fault," a genuinely different and more
favorable finding than a flat aggregate alone would suggest, narrowed accordingly.

## CELL-TEMPLATE MANDATORY (SCHEMA-VET checklist)

- `arms_differ_verified`: 5-arm per-checkpoint prediction-vector hash-differ (META_RULE_AF)
- `final_metrics_atomicity`: tmp_replace (os.replace)
- `except SystemExit: raise` BEFORE `except Exception` (no bare except, no `except BaseException`)
- `deterministic_seeding`: hashlib-seeded scramble draws only; file-order exposure stream; no
  `hash()`, no `list(set())`
- `crlb_n/a`: symbolic KB-lookup + vote-count pipeline; no argmax/capacity noise-floor discriminator
  applies (3-way discrete classification accuracy on a real benchmark, not a substrate-primitive
  capacity sweep)
- `HP_SCOPE`: `{dev_checkpoint_eval: [fire_rate_drop, comprehension_lift, scramble_control,
  consolidation_fidelity]}` -- ALWAYS-CRUTCH and NEVER-CRUTCH arms are diagnostic/floor references,
  not gated by these bands themselves
- `cardinality_ok`: `EXPECTED_N_CHECKPOINTS = 5`; `EXPECTED_N_ARMS = 5`
- Per-unit failure-class instrumentation: no bare except; per-item scoring exceptions recorded with
  a failure_class, degraded-scoring budget 2%
- `calibration_check`: adaptive_with_discriminator_gate (GATE_THRESH = median BoW-margin, computed
  fresh, logged, not hand-tuned for a pass)
- `real_code_path_exercised`: self-test constructs the REAL `Library`, `consolidation_pass`,
  `HDFactStore` (imported from `hdlab.grounding_acquisition_loop` / `hdlab.hd_fact_store`, not
  reimplemented) at reduced scale (N~16 synthetic pairs), not a synthetic-only branch
- `substrate_signature_checked`: `consolidation_pass` / `HDFactStore.__init__` / `HDFactStore.store`
  / `HDFactStore.query` calls bind against the live signature (base/portable kwargs only)
- `progress_logging`: `print_flush_true` (checkpoint-boundary progress lines; declared regardless
  of whether the run clears the 1800s mandatory threshold, since exact wall-time is unknown until
  smoke measures it)
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ throughout the cell docstring

## Compute architecture

Class (b) sequential-CPU with justification: this is a symbolic KB-lookup + vote-counting pipeline
(Python dict operations on ~1.2M CSKG edges + ~35K SIQa items), not a substrate-primitive
matmul workload -- no GPU batching applies. Per-item cost is O(concepts^2) dict lookups
(bounded, small k). HYPOTHESIZED wall time (pre-smoke): low single-digit minutes for the full
5-checkpoint x 5-arm sweep over 1,954 dev items + 33,410 exposure items; to be MEASURED at smoke
and confirmed before FULL is run. Storage strategy: `no_composition` / sharded-by-construction
(the CSKG index and HDFactStore are both flat/keyed lookups, no chained multi-hop composition in
this cell's mechanism).

## Dispatch

Given the light CPU-only profile (expected minutes, not hours), FULL is run directly
foreground-to-completion (not queued to local/remote_cpu_queue) per the "light compute -> run fast
in foreground" guidance -- avoids occupying queue infra for a workload with no GPU/remote benefit.
Smoke gates first (capped exposure/dev subsets) to verify correctness + measure real wall-time
before commit to FULL.

## ADDENDUM (2026-08-10, post-crash diagnosis + fix -- filed BEFORE the diagnostic/FULL runs below)

Context: the prior exp_dev cycle's default `--smoke` (SMOKE_TRAIN_CAP=3000/DEV_CAP=250)
HARD_FAILED with a fully FLAT result (0 promotions the entire run -- `promote_min_exposure=8` never
reached at that exposure scale). An ad hoc larger diagnostic (`train_cap=15000/dev_cap=400`,
undisclosed at the time, output `data/exp_crutch_fade_social_iqa_v1_promocheck/metrics.json`) then
showed a REAL-BUT-SMALL scramble-clean signal (25 promotions by 100%, gap_driven 0.3975 vs bow
0.3775) before the session auth-crashed pre-commit. This addendum pre-registers the diagnosis +
fix design and the bands used to interpret it -- filed before the sweep/diagnostic/FULL runs it
governs.

**Bands: UNCHANGED from the body of this pre-reg above** (verbatim HARD-PASS/HARD-FAIL/MIDDLE_BAND
criteria, same +0.05 comprehension-lift target, same fire-rate-drop / scramble-control /
consolidation-fidelity gates). This addendum does not loosen or re-tune any threshold to chase a
pass; it changes two INPUT parameters (`promote_min_exposure`, `score_mode`) and adds one
diagnostic (`retrieval_use_diagnostic`), all applied uniformly to both the real (gap_driven) and
scramble-control arms, then reads the SAME verdict logic against the result.

**FAULT 1 (promotion gated too tight) -- design:** sweep `promote_min_exposure` in {2, 3, 4, 8} via
a new `consolidation_pass(..., promote_min_exposure=N)` passthrough (both the real AND the scramble
store use the SAME N each run -- a fair control: if loosening the gate let false/scrambled pairs
promote too, that would falsify the fix). `PROMOTE_MIN_CONSISTENCY=0.75` and `schema_thresh=0.10`
(the false-memory guard) are left at module defaults, untouched, at every sweep point. Predicted
(HYPOTHESIZED, pre-sweep): because `consolidation_pass`'s promotion check only ever executes inside
the already-banked branch (`n >= MIN_CONFIRM = 4` is a hard precondition for banking to occur at
all), any `promote_min_exposure <= 4` should be mechanically EQUIVALENT to `promote_min_exposure =
4` -- MEASURED below to confirm or refute this before committing compute to a wider sweep.

**FAULT 2 (thin per-fact help) -- design:** decompose CRUTCH_RESOLVED failures into RETRIEVAL
(does ANY CSKG edge reach the GOLD answer's concepts at all, `crutch_score[gold] > 0`) vs USE
(GIVEN a gold-reaching edge exists, does argmax correctly rank it top). `retrieval_hit_rate` /
`use_quality_given_hit` computed per checkpoint for the gap_driven arm's CRUTCH_RESOLVED items
only (cheap: bounded per-item dict lookups). ONE targeted improvement is tried and MEASURED (not
assumed): initial hypothesis was an edge-COUNT-inflation bug in the legacy scoring formula
(`max(trust) * len(edges)` lets several low-trust edges outrank one high-trust edge) --
`score_mode="max_trust"` fixes this specific bug but MEASURED zero delta on real data (97% of CSKG
pairs carry exactly 1 edge; the multi-edge scenario the fix targets barely occurs). Sampling actual
retrieval-hit-but-wrong-argmax items surfaced the REAL cause instead: a handful of high-DEGREE,
SIQa-template-generic concepts (`person`, `mouth`, `want`, `next`, `need`, `baby` -- recurring
because SIQa's question templates ["How would X feel/be described?", "What will X want to do
next?"] reuse these words across unrelated items) connect to almost anything in a 1.15M-edge KB,
producing spurious or wrong-candidate-favoring scores with no real item-specific content.
`score_mode="hub_penalized"` (max_trust base / (1 + log1p(max node-degree of the driving pair)))
is the SHIPPED fix -- MEASURED delta below.

**Diagnostic scale (not the certified --smoke/--full contract):** `--diag --train-cap 15000
--dev-cap 400` (~45-110s/run incl. ~15-40s fixed CSKG-load cost) used to cheaply screen the sweep
+ score_mode A/B BEFORE committing to uncapped FULL runs. Output dirs `data/exp_crutch_fade_
social_iqa_v1_diag_*` (not committed -- superseded scratch; the FULL-scale runs below are the
evidence of record). `real_code_path_exercised` unchanged (same Library/consolidation_pass/
HDFactStore objects, only their kwargs vary); `substrate_signature_checked` extended to the new
`promote_min_exposure` kwarg on `consolidation_pass` (already part of its live signature, not a
version-drift risk). Self-test extended (not replaced) to cover: promote_min_exposure threading
(a 4-trace item promotes at threshold=4, does not at threshold=8, both against the SAME real
Library/HDFactStore/consolidation_pass), the max_trust fix's crafted count-inflation case, and the
hub_penalized fix's crafted hub-vs-specific-concept case -- all PASS (see cell self-test output).

FULL-scale decisive runs (uncapped, real `--full`/`--diag`-uncapped, no train/dev subsampling):
results + verdict reported in the exp_dev completion report, not duplicated here (per META_RULE_AC,
numbers belong tagged at their MEASURED@ source, not restated as pre-reg text after the fact).
