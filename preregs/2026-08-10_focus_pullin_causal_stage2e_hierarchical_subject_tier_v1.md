# Pre-registration: exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** Director spawn prompt ("STAGE-2E: add a HIERARCHICAL
(nested) 2nd routing tier keyed by SUBJECT to the oversized source-shards, composed with the DG/CA3 sparse
within-shard coding already built in Stage-2D"). Autonomy declaration: exp_dev owns all parameters (leaf
sweep values, tier count, hash scheme, per-family leaf counts, DG_DIM, both threshold bands, seeds,
local-vs-queue, anchor name, ETA); the task-shape + pointers + one VET correction are the Director's only
inputs.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "hierarchical subject tier sharded store DG CA3 sparse capacity cliff
CSKG"` -> top hit `hierarchical_subshard_kg_cpu_v1` cosine=0.2949 (already known: HARD_PASS, smoke,
1-seed, relation-then-subject 1.000 vs 0.735, N=8192 synthetic ~300-entity toy) -- below the 0.30
novelty threshold, and it is the SAME cell the task prompt itself already cites as prior evidence, not a
new discovery. **Verdict: genuinely novel.** No prior cell composes (source-tier1 + subject-tier2 +
DG/CA3 sparse coding) at CSKG's real 1.2M-edge, 482,588-entity, AT/VG/CN-skewed scale -- the nearest
neighbors in the KB are all smoke-only synthetic-toy scale (`hierarchical_subshard_kg_cpu_v1`,
`community_of_communities_nested_retrieval_v2` FULL but synthetic V<=48,000) or a different mechanism
family (`P4: Hierarchical capacity scaling`, `MULTI-LEVEL HIERARCHICAL CAPACITY PREDICTION` notes,
cosine<=0.29, general capacity-scaling commentary not this specific composition).

## What / why
Stage-2D (`data/exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1/metrics.json`,
MIDDLE_BAND) moved KGStore's write-side crosstalk collapse wall 30K -> past 100K by sharding on CSKG's
own `source` provenance field (K=7), but re-collapsed at the full 1,213,912-edge corpus:
`ARM_SHARDED_SPARSE.relevant_recall` 0.547 (100K) -> 0.053 (1,213,912); `false_pull_in_rate` 0.173 ->
0.400; scramble margin 0.200 (100K) -> 0.053 (1,213,912), both below the 0.30 target. Root cause
(measured, not assumed): 3 of the 7 shards are themselves oversized single Hebbian leaves at full scale
(AT=696,152/57.4%, VG=257,130/21.2%, CN=214,890/17.7% edges each in ONE `[dg_dim,dg_dim]` W), and the
shard key (relation-majority family) is only an approximate query-time proxy (23/33 relations pure,
10/33 mixed), giving a weak scramble margin even before the AT/VG/CN overload. SUBJECT is a
query-time-EXACT key (unlike relation): a query `(s,p)->o` always knows its true subject `s`, so
`hash(subject) mod K_family` can ALWAYS route to the correct leaf if that subject's edges were grouped
there at write time -- fixing BOTH weaknesses (skew, via splitting the 3 oversized families into
right-sized leaves; weak key, via an exact rather than approximate 2nd-tier routing signal) at once.

This composes Stage-2D's own already-built `SparseHeteroShardStore` / `ingest_from_triples` /
`eval_gate_sparse_shard` / `_batched_score_settle` / `build_relation_majority_shard` /
`scramble_labels_for_prefix` machinery (disk-read this session, not re-transcribed) with the corpus's own
already-certified 2-tier routing precedent: `exp_hierarchical_subshard_kg_cpu_v1` (HARD_PASS, smoke,
relation-then-subject 1.000 vs per-relation-only 0.735 -- SAME 2-tier-with-subject-as-2nd-key pattern,
different key names) and `exp_community_of_communities_nested_retrieval_v2` (HARD_PASS, FULL, 3 seeds,
N=8192, up to V=48,000 -- a 2nd routing tier holds fidelity 1.000 flat while single-tier collapses to
0.012, `nested_v_invariance_spread=0.000` -- decode load depends on PER-LEAF load only, not total V; both
read directly this session, `data/exp_hierarchical_subshard_kg_cpu_v1/metrics.json` and
`data/exp_community_of_communities_nested_retrieval_v2/metrics.json`).

## CRITICAL VET CORRECTION (Director-mandated, addressed BEFORE any full-scale compute)
The mining drill note (`notes/research_existing_sharding_corpus_mining_skew_and_scaling_2026-08-10.md`)
recommended a "~30-65 triples/leaf" capacity target derived from `exp_skewed_shard_capacity_cpu_v1` -- an
UNRELATED flat-bundle-superposition mechanism, already dismissed at cosine=0.2881 by Stage-2D's own
prior-work check, and this number directly CONTRADICTS Stage-2B's own measured KGStore curve (0.967
recall @ 1,000 triples, 0.700 @ 10,000 -- 30-65 triples would never have survived that collapse point).
Per the Director's explicit instruction, this number is NOT used. Instead,
`experiments/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1.py` was authored and run THIS
session (foreground, disk-verified, `data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/
metrics.json`, `elapsed_s=566.4`) to EMPIRICALLY measure the real per-leaf cliff of THIS store (KGStore-
shaped for dense; `SparseHeteroShardStore` with `n_shards=1` for sparse -- i.e. the ACTUAL substrate
objects/functions the main gate uses, real_code_path, not a synthetic reimplementation), on an ISOLATED
single leaf holding only real AT-family edges (in the SAME deterministic full-corpus shuffle order
Stage-2B/2D use, so results are directly comparable at matching occupancy).

**Measured curve (AT-isolated, single leaf):**
```
n_triples   dense_recall   sparse_recall
  57,000        0.000          0.693      <- only point clearing 0.50
 150,000        0.000          0.227
 300,000        0.000          0.053
 500,000        0.000          0.013
 696,152        0.000          0.013
```
Plus single full-family-count isolated points: VG (257,130) dense=0.000/sparse=0.013; CN (214,890)
dense=0.000/sparse=0.093.

**Interpretation (deflated, honest):** DENSE recall is 0.000 at EVERY tested point, including the
smallest (57,000) -- the dense-Hopfield cliff sits well BELOW 57,000, consistent with (not contradicting)
Stage-2B's own known dense degradation curve, which was already declining sharply by 10,000-30,000; dense
was not swept finer because it is not this cell's composed-arm substrate (the DG/CA3 sparse regime is,
per Stage-2D's own established primary lever) and a finer dense sweep would not change this cell's
design decision. SPARSE shows a SHARP cliff bracketed between 57,000 (0.693, comfortable 0.193 margin
above the 0.50 gate) and 150,000 (0.227, well below) -- not finely bisected (a genuinely open gap,
disclosed, not hidden) but `SAFE_LEAF_SIZE_SPARSE=57,000` is a CONSERVATIVE choice (the largest
CLEARLY-safe measured point, not a borderline one), which is the correct direction to err for sizing
`K_family` (under-provisioning K, i.e. picking too-large a leaf size, is the worse failure mode for the
main gate; a conservative SAFE_LEAF_SIZE only costs a few more shards, which is cheap).

**K_FAMILY derivation:** `K_family = ceil(family_full_occupancy / SAFE_LEAF_SIZE_SPARSE)`, then +1 margin
for AT/VG/CN based on a subject fan-out check (this session, `np.bincount` over real AT/VG/CN subject
arrays, `data/cskg_foundation_v1`): AT is extremely hash-friendly (23,799 distinct subjects, max
single-entity fan-out=96, top-5-share=0.06% -- no mega-hub risk, a uniform hash split should balance
tightly). VG (6,118 distinct subjects, max fan-out=2,456, top-5-share=3.36%) and CN (40,341 distinct
subjects, max fan-out=6,081, top-5-share=4.25%) have modest hub concentration, so their K gets +1 margin
over the raw `ceil()` value. **Final: `K_FAMILY = {AT: 14, VG: 6, CN: 5, WD: 1, FN: 1, WN: 1, CN|WN: 1}`**
(small families already safely below 57,000 at full scale, unchanged from Stage-2D's single-leaf-per-
family). Average per-leaf occupancy: AT=49,725, VG=42,855, CN=42,978 -- all comfortably below
`SAFE_LEAF_SIZE_SPARSE`. Total physical shards: 14+6+5+1+1+1+1=**29** (up from Stage-2D's flat 7).

## Mechanism (why subject-tier fixes BOTH Stage-2D weaknesses)
Tier-1 (family/source) routing is Stage-2D's EXACT, UNCHANGED mechanism -- ingest uses the true `source`
label (honest, write-time-known); query uses `build_relation_majority_shard` (Stage-2D's imported,
unmodified function -- an approximate proxy, since a query does not know a fact's true source before
knowing whether/where the fact exists). This is NOT touched by this cell -- the task's ONE new variable
is tier-2, and Stage-2D's own weak 0.20 margin at 100K stays attributable to tier-1 alone.

Tier-2 (subject) routing for the 3 oversized families: a deterministic, PYTHONHASHSEED-INDEPENDENT
vectorized avalanche hash (`_vectorized_entity_hash`, SplitMix64-style finalizer over numpy uint64 arrays
-- explicitly NOT Python's built-in `hash()`, per gate F.5/PROT-023) of `(subject_id, family_salt)` mod
`K_family`. Both ingest (which knows the true subject at write time -- honest, not an oracle) and query
(which ALWAYS knows its own subject `s`, since a query is literally `(s,p)->o` -- also honest, not an
oracle) use the IDENTICAL formula for the REAL/composed arm, so tier-2 routing is correct BY
CONSTRUCTION -- the mechanism's entire benefit is reduced per-leaf occupancy (crosstalk), which the
leaf-capacity sweep above measures directly, not routing accuracy per se.

`CONTROL_SCRAMBLED_TIER2` (the mandatory pairscramble-must-collapse control, per task contract):
scrambles ONLY the WRITE-side tier-2 assignment -- for each scale rung independently, a fresh permutation
(seeded `SCRAMBLE_SEED + scale + family-specific salt`, Stage-2D's own `scramble_labels_for_prefix`
methodology applied one level deeper) of the TRUE tier-2-local-index multiset within each oversized
family's ingested prefix, preserving the EXACT per-leaf-size histogram the real arm produces. QUERY-side
routing for the SCRAMBLE arm is IDENTICAL to the real arm (the "would-be-correct" `hash(subject)`
formula) -- ONLY ingest differs. This creates a genuine write/read MISMATCH: a subject's own edges are
scattered to essentially random leaves at write time, but a query for that subject only checks the ONE
leaf its true hash points to, so recall should collapse toward roughly `1/K_family` if grouping-by-
subject (not merely "having more shards") is what actually mattered. Tier-1 is IDENTICAL between the
composed and scrambled arms (both reuse the SAME `rel_majority_family_idx` table and the SAME true-source
ingest routing) -- isolates tier-2 as the one active variable, per the contract's "ONE primary new
variable" requirement.

## Reuse contract (imports, not re-transcription)
- `hdlab.kg_traversal.KGStore` -- entity/relation codebook generation.
- `experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1`: `load_entity_vocab`,
  `precheck_kgstore_and_loader`, `QUERY_SEED`/`DATA_SEED`/`SHORTLIST_K`/`N_QUERY` (bit-identical reuse).
- `experiments.exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1`:
  `load_spine_edges_with_source`, `SparseHeteroShardStore`, `build_relation_majority_shard`,
  `scramble_labels_for_prefix`, `build_dg_projections`, `precompute_dg_val_codebook`,
  `_batched_score_settle`, `eval_gate_sparse_shard`, `precheck_source_field`, `DG_DIM`, `DG_SPARSITY`,
  `SCRAMBLE_SEED`, `REC_THRESH_SPARSE`, `FP_THRESH`, `REPRO_TOLERANCE` -- ALL imported unmodified; the
  hierarchical arm's store IS a `SparseHeteroShardStore` with more shards and a different shard-label
  computation, not a new store class.
- `experiments.exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1.refuse_gate_calibrate_from_
  scores` -- identical DG-space tau calibration Stage-2D's SPARSE/SCRAMBLED arms already use.
- `tools.exp_checkpoint`: per-scale resumable checkpointing (MANDATORY, CLAUDE.md multi-unit rule).
**New code in this cell (disclosed):** `_vectorized_entity_hash` (deterministic avalanche hash, NOT
`hash()`); `build_family_shard_layout`/`compute_ingest_shard_ids_real`/
`compute_ingest_shard_ids_scrambled`/`compute_query_shard_ids` (the 2-tier routing logic itself, the
cell's actual novel contribution); `eval_gate_hierarchical` (generalizes `eval_gate_sparse_shard`'s exact
calibration/admission convention to 2-step routing + per-family recall breakdown, reusing
`_batched_score_settle` unchanged).

## Design: 2 scales (exactly the task contract's required gate points) + 1 cheap repro spot-check
`SCALES_FULL = [100000, 1213912]`. **Compute-proportionality (disclosed):** Stage-2D's own
`deterministic_seeding: true` (confirmed on disk) means its FLAT/DENSE/ARM_SHARDED_SPARSE/
CONTROL_SCRAMBLED_SHARD_KEY numbers at 100K/1,213,912 are CITED
(`MEASURED@data/exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1/metrics.json`) rather than
re-executing ~693s of unchanged compute -- re-deriving deterministic, already-landed numbers would
violate compute-proportionality. This cell instead spends compute on (a) a fresh SPOT-CHECK reproduction
of the tier-1-only `ARM_SHARDED_SPARSE`/`CONTROL_SCRAMBLED_SHARD_KEY` arms at ONE cheap scale (10,000,
`REPRO_TOLERANCE=0.05` absolute -- extends Stage-2D's own FLAT-only spot-check convention to the SPARSE
arms this cell directly builds on) to confirm the reused machinery is genuinely bit-identical before
trusting the citation, and (b) the two genuinely NEW arms (`ARM_HIERARCHICAL_SPARSE`,
`CONTROL_SCRAMBLED_TIER2`) at the two scales the task's bands require.

**ARM_HIERARCHICAL_SPARSE**: `SparseHeteroShardStore(n_shards=29)`, ingest via
`compute_ingest_shard_ids_real`, query via `compute_query_shard_ids` (both TRUE-subject-hash-based).

**CONTROL_SCRAMBLED_TIER2**: identical store class/shard-count, ingest via
`compute_ingest_shard_ids_scrambled` (tier-2 only), query via the SAME `compute_query_shard_ids` as the
real arm (creates the write/read mismatch described above).

**Stage-2D tier-1-only repro spot-check** (scale=10,000 only, NOT a gated unit): fresh
`SparseHeteroShardStore(n_shards=7)` runs, identical to Stage-2D's own `ARM_SHARDED_SPARSE`/
`CONTROL_SCRAMBLED_SHARD_KEY` construction, compared against Stage-2D's landed 10,000-scale numbers.

## Pre-registered bands (declared here BEFORE running --full)
All bands apply to `ARM_HIERARCHICAL_SPARSE` ("composed arm") vs `CONTROL_SCRAMBLED_TIER2` at BOTH
`scale=100,000` AND `scale=1,213,912` unless stated otherwise. Operationalization note (disclosed): the
task's HARD-FAIL text ("composed arm < 0.10 at 1.2M ... OR scramble ties it") is scoped to the 1.2M point
specifically (the hardest, most-contested scale, where Stage-2D's tier-1-only arm collapsed to 0.053) --
this is the literal reading and the gating condition below follows it; the 100,000-scale margin/tie is
ALSO computed and reported for transparency but does not itself gate HARD-FAIL (matching the task's own
wording, which does not scope the tie-check to both scales the way it scopes the recall bands).

- **HARD-PASS** (ALL required):
  1. `ARM_HIERARCHICAL_SPARSE.relevant_recall >= 0.50` AND `<= false_pull_in_rate 0.20` at BOTH 100,000
     AND 1,213,912.
  2. `(ARM_HIERARCHICAL_SPARSE.relevant_recall - CONTROL_SCRAMBLED_TIER2.relevant_recall) >= 0.30` at
     BOTH 100,000 AND 1,213,912 (the scramble-margin discriminator).
  3. `arms_differ_verified == True` (composed vs scrambled per-probe outcome digests differ at both
     scales) AND `cardinality_ok == True` (both expected scale units landed) AND the Stage-2D tier-1-only
     repro spot-check `ok == True` (comparison basis trustworthy).
- **HARD-FAIL** (either triggers):
  1. `ARM_HIERARCHICAL_SPARSE.relevant_recall < 0.10` at `scale=1,213,912` (the hierarchical rescue does
     not work on REAL CSKG structure even at the largest, most-skewed scale -- skew still wins).
  2. `(ARM_HIERARCHICAL_SPARSE.relevant_recall - CONTROL_SCRAMBLED_TIER2.relevant_recall) < 0.10` at
     `scale=1,213,912` (routing artifact -- the composed arm's win, if any, is not attributable to
     subject-based grouping specifically).
  3. The Stage-2D tier-1-only repro spot-check fails (`ok == False`) -- the comparison basis cannot be
     trusted.
- **MIDDLE_BAND**: everything else -- e.g. the composed arm clears 100K but not 1.2M (partial rescue,
  same shape as Stage-2D's own outcome one scale point later); recall clears but the margin does not
  (routing-artifact risk without full HARD-FAIL certainty); or `false_pull_in_rate` alone breaches 0.20
  while recall/margin otherwise clear.

## Compute architecture
(b) sequential/batched-CPU with justification (NOT GPU-batched) -- SAME justification as Stage-2D
(identical code paths reused): `_batched_score_settle`'s coarse DG-space scoring is batched PER SHARD
(amortizes streaming `DG_VAL_CODEBOOK`, ~3.95GB at `n_ent=482,588`/`DG_DIM=2048`, once per shard per
scale rather than once per query); the fine settle+admission step stays a cheap per-query loop
(`shortlist_k=50` rows). `ingest_from_triples` streams DG-key-projection in bounded chunks (never
materializes a `[n_triples, DG_DIM]` array for the full 1,213,912-row set -- Stage-2D's own memory-safety
fix, reused unchanged). This cell adds NO new GPU-batching opportunity over Stage-2D's own justification
(same primitive math, only the shard-label computation differs) and does not change `DG_DIM=2048` (same
resource-constrained choice Stage-2D already disclosed and measured; a larger `DG_DIM` would give more
Willshaw-class headroom per leaf but the leaf-capacity sweep above shows `DG_DIM=2048` already clears the
0.50 bar comfortably at the chosen `SAFE_LEAF_SIZE_SPARSE=57,000`, so raising it is not required to hit
the pre-registered bands -- disclosed, not hidden, trade-off). Storage strategy: SHARDED (29 physical
leaves, per META_RULE STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW, same as Stage-2D).
`OMP_NUM_THREADS=8` (matches Stage-2D; tolerance-based comparisons do not require bit-exact summation
order).

## Cell-template mandates
- `arms_differ_verified`: True -- composed vs scrambled per-scale outcome digest (SHA256, META_RULE_AF)
  must differ at both scales (self-test additionally verifies this at tiny scale, closed-form).
- `final_metrics_atomicity`: `tmp_replace` (top-level) + per-scale-unit resumable checkpointing via
  `tools/exp_checkpoint.py` (`unit_key("scale", scale)`; a unit holds BOTH the composed and scrambled
  arms' results for that scale).
- `except SystemExit: raise` before `except Exception` (no bare `except:`/`except BaseException:` --
  grep-gated, confirmed clean before self-test).
- `crlb_n/a`: empirical hierarchical shard-capacity diagnostic; the per-leaf safe size is MEASURED (leaf
  capacity sweep diagnostic, isolated real-AT-edge single-leaf `SparseHeteroShardStore`), not a
  closed-form floor -- measuring it IS the design input this cell's K_FAMILY choice depends on.
- `HP_SCOPE`: `{hierarchical_sparse: [relevant_recall, false_pull_in_rate, scramble_margin]}`.
- `cardinality_ok`: `EXPECTED_N_UNITS = len(SCALES_FULL) = 2` (100,000 and 1,213,912; the 10,000-scale
  Stage-2D repro spot-check is NOT a gated cardinality unit, run once per invocation, own try/except).
- per-unit failure-class instrumentation (no bare except; repro spot-check catches `Exception`
  specifically and records `failure_class`, non-fatal to the main gate).
- `calibration_check`: `adaptive_with_discriminator_gate` for both new arms (DG-space `tau` via
  `refuse_gate_calibrate_from_scores`, per-scale, IDENTICAL mechanism to Stage-2D's own SPARSE/SCRAMBLED
  arms -- not re-tuned for this cell).
- `deterministic_seeding`: True -- `_vectorized_entity_hash` is a fixed-formula SplitMix64-style
  finalizer over numpy uint64 arithmetic (NOT Python's built-in `hash()`, no PYTHONHASHSEED dependency,
  gate F.5/PROT-023); scramble permutations seeded `SCRAMBLE_SEED + scale + family-salt*100003`; family
  order via `sorted(source_to_idx.keys())`; no bare `list(set(...))` ordering anywhere in this cell.
- `cell_chunked`: False (single script; per-scale checkpointing per above).
- `start_marker_written`/`crash_diagnostic_present`/`heartbeat_present`: True.
- `progress_logging`: `print_flush_true` (declared; estimated wall time for `--full` may approach or
  exceed 1800s given the double-ingest-per-scale sweep + DG_VAL_CODEBOOK precompute, so this is
  MANDATORY per §17).
- Real-code-path preflight (`self_test()`): constructs the REAL `KGStore` (via
  `precheck_kgstore_and_loader`), the REAL `load_spine_edges_with_source`/`precheck_source_field` against
  a real CSKG slice, a REAL tiny `SparseHeteroShardStore` (dg_dim=256, n_shards=4) over a synthetic
  BIGFAM(K=3)/SMALLFAM(K=1) corpus, verifies the 2-tier routing functions' ingest/query agreement
  (closed-form) and the SCRAMBLE-degrades-recall mechanism (stochastic, end-to-end), plus a
  hash-determinism + hash-distribution unit check.

## Estimated wall time (disclosed BEFORE running --full)
Leaf-capacity-sweep diagnostic (already run, not part of `--full`): 566.4s measured. DG_VAL_CODEBOOK
precompute: ~40-50s per invocation (measured in Stage-2D and the leaf-sweep run this session). Per-scale
double-ingest (composed + scrambled, same total edge count as Stage-2D's single SPARSE arm, routed to
more shards -- expected similar order of cost, not more, since total accumulate FLOPs is
shard-count-independent): scale=100,000 ~35s combined (Stage-2D's own single-arm SPARSE ingest+eval at
100K was 11.4s+6.0s=17.4s; x2 for composed+scrambled ~35s); scale=1,213,912 ~320-330s combined (Stage-2D's
single-arm SPARSE ingest+eval at full scale was 155.8s+7.1s=162.9s; x2 ~326s). Stage-2D repro spot-check
at scale=10,000: ~20-30s (two cheap tier-1-only SPARSE-class runs). `--smoke` (scale=[1,213,912] only,
DISCRIMINATOR-MUST-SURVIVE-SCALE option A -- smoke AT the hardest full-N point directly, since that is
the ONE point Stage-2D catastrophically failed and a smaller-scale smoke would not exercise the mechanism
this cell exists to test): estimated ~50+326=~376s (~6.3 min). `--full` (both scales + repro
spot-check): estimated ~50+35+326+25=~436s (~7.3 min). Both comfortably fit a single 10-minute
foreground Bash call; some recompute duplication of the 1,213,912 unit between `--smoke` and `--full` is
accepted (disclosed) per the discriminator-must-survive-scale discipline's own stated cost/benefit
tradeoff, since absolute cost is minutes not hours.

## Dispatch
Local, foreground-to-completion (per Director's Ops instruction: "Finish FOREGROUND to completion -- do
NOT spawn nested sub-agents, do NOT wait on background work"). `--self-test` completed in 0.94s (measured,
this session). `--smoke` and `--full` are each expected to complete within a single foreground Bash call
(10-minute cap) per the wall-time estimate above; the per-scale checkpointing makes a 2-call split safe if
needed (not expected to be necessary based on the estimate, disclosed as a contingency per Stage-2D's own
precedent).
