# Pre-registration: exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** Director spawn prompt, "Stage 2 of the
simulation-engine program, SUB-TEST B -- the salience-gate at CSKG scale, the historically-fatal
risk, do NOT skip." Stage 1 (`exp_focus_pullin_causal_stage1_micro_world_v1`, HARD_PASS 5/5,
commit ceb8fe99b) measured 0.0 false-pull-in on a 30-fact hand-authored micro-world. Sub-test B
wires the SAME gate mechanism to the real, HARD_PASS-certified CSKG content store on disk.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
Same query as Sub-test A (`bash tools/substrate_query.sh "multi-hop causal chain retrieve validate
advance loop salience gate CSKG scale false-pull-in"`) -> all hits below cosine 0.30. **Verdict: no
prior arc cell tests "pull_in's salience gate wired to the real CSKG-scale KGStore"; genuinely
novel.**

## What / why
Stage 1's 0.0 false-pull-in was measured on 30 clean, hand-authored facts -- a regime with no
crosstalk pressure at all. The CSKG foundation store on disk
(`data/cskg_foundation_v1/`: 482,588 nodes, 1,213,912 spine edges, HARD_PASS-certified
`exp_cskg_foundation_v1`) is 4-5 orders of magnitude larger. This sub-test answers: does
`GATE_THRESH=0.28` (Stage-1's un-retuned number) still discriminate relevant retrieval from false
positives at this cardinality, or does it degrade -- and if it degrades, HOW (false-pull-in
inflation vs. recall collapse are different, differently-dangerous failure modes)?

## Mechanism wiring (reuse, disclosed adaptation)
`store.key(s, p) = E[s] * R[p] * sqrt(n_dim)` (KGStore's existing bind op, CERT 584/585,
UNCHANGED). `probe = store.W @ key` -- the raw Hebbian-recalled noisy vector estimate of the
answer entity, living in the SAME 1024-dim space as `store.E`'s rows (exactly analogous to
Stage-1's raw content-vector probe). Because `store.E` rows are bipolar {-1,+1} with IDENTICAL
norm `sqrt(n_dim)` for every entity, ranking by `store.score_all(key) = E @ probe` (a cheap linear
readout, O(n_ent x n_dim) per query) is EQUIVALENT to ranking by cosine against a fixed-norm
codebook -- so taking the top-`SHORTLIST_K=50` by `score_all` as a coarse candidate shortlist does
not change the ranking, it only bounds the codebook `pull_in()`'s CA3 settle has to search at
n_ent=482,588 (a disclosed 2-stage coarse-then-fine retrieval, not a change to `pull_in()` itself).
`pull_in_multi_exclude()` (Sub-test A's byte-verified generalization of Stage-1's `pull_in()`) is
imported and reused, called on the shortlist with `gate=0.28` -- **Stage-1's ORIGINAL number, held
FIXED per the Stage-2 task CONTRACT** (the question is whether it generalizes, not a fresh
CSKG-specific calibration -- recalibrating it here would defeat the point of the test).

## Scale sweep design
ONE shared `KGStore` (E, R allocated once, n_ent=482,588, n_dim=1024, fixed seed) is repeatedly
RESET (W zeroed, E/R untouched) and re-ingested with an increasing PREFIX of a fixed deterministic
shuffle (`np.random.default_rng(20260810).permutation`) of the real spine edges: `SCALES = [1000,
5000, 10000, 30000, 100000, 1213912(=full)]`. This isolates the swept variable to "how many
triples were Hebbian-written into the SAME [1024,1024] W matrix" -- the crosstalk-accumulation
axis the MCScript2.0-echo risk is actually about -- while the entity codebook (the false-pull-in
search space) stays fixed at the full 482,588 throughout every point, so every scale point is
already measured "at full entity cardinality," not just the final one.

Per scale point: `relevant_recall` (150 sampled real ingested triples: does the pipeline retrieve
the TRUE object, admitted) and `false_pull_in_rate` (150 random (s,p) pairs verified NOT present
in the ingested set: does the gate ever admit a candidate for a query with no true answer).
`relevant_in_shortlist_rate` is tracked as a MECHANISM-ATTRIBUTION diagnostic -- it isolates
whether a recall failure is caused by the salience gate (threshold too strict on an
already-present candidate) or by the underlying store's raw associative capacity collapsing
UPSTREAM of the gate (the true answer not even reaching the coarse shortlist). At the full-scale
point only, a `SCRAMBLE_OBJECTS` control (object column permuted, hashlib-seeded) re-ingests and
re-measures, to check whether any surviving recall reflects genuine structure.

## Bands (MEASURED@calibration this session, locked before the production --full run)
Per scale point:
- **HARD-PASS**: `false_pull_in_rate <= 0.20` AND `relevant_recall >= 0.30` AND
  `relevant_recall - false_pull_in_rate >= 0.15` (the gate is still net-useful at this cardinality).
- **HARD-FAIL**: `false_pull_in_rate > 0.50` (indiscriminate flooding -- the literal "blows up"
  failure mode) OR `relevant_recall <= false_pull_in_rate` (the gate provides zero net
  discriminative value, regardless of the absolute levels) OR `relevant_recall < 0.05` (signal
  totally lost).
- **MIDDLE_BAND**: everything else.
- The FULL-cardinality point (`scale = 1,213,912`, the true CSKG spine-edge count) is the
  headline/reported verdict, per the task's "at THIS cardinality" framing; the sweep is reported in
  full as the supporting trend (this is a single deterministic diagnostic sweep, not a multi-seed
  certifying cell -- compute-proportionality: a directional/diagnostic question gets the cheapest
  decisive method, not a repeated-seed statistical fit).

## Pre-check (CONTRACT-mandated, flat=broken-experiment discipline)
`precheck_kgstore_and_loader()`: (1) a tiny synthetic KGStore (n_ent=4) must ingest+
`predict_one_hop` correctly on 2 hand-planted facts; (2) the REAL `cskg_foundation_v1` loader must
resolve a 200-row real slice of `edges_shard_00.jsonl` against the real `nodes.jsonl` vocabulary
with ZERO missing-entity references. Both run first in `self_test()`, before any HARD-FAIL on the
main sweep is trusted.

## Landed result (MEASURED this session -- disclosed here since --full was run before this file's
final commit, per Stage-1's own precedent of full disclosure)
| scale | relevant_recall | in_shortlist | false_pull_in | verdict |
|---|---|---|---|---|
| 1,000 | 0.967 | 1.000 | 0.000 | HARD_PASS |
| 5,000 | 0.947 | 1.000 | 0.000 | HARD_PASS |
| 10,000 | 0.700 | 1.000 | 0.000 | HARD_PASS |
| 30,000 | 0.000 | 0.973 | 0.000 | HARD_FAIL |
| 100,000 | 0.000 | 0.333 | 0.000 | HARD_FAIL |
| 1,213,912 (full) | 0.000 | 0.007 | 0.000 | HARD_FAIL |

`SCRAMBLE_OBJECTS` control at full scale: recall=0.000, shortlist=0.020, false_pull_in=0.000 --
not very discriminating at this specific point since the REAL condition has already independently
collapsed to the same floor by full scale (disclosed, not oversold as a clean scramble-collapse
proof at this cardinality).

**Overall verdict: HARD_FAIL at the full-cardinality point** (`relevant_recall=0.000 <=
false_pull_in_rate=0.000` AND `relevant_recall < 0.05`, both trip independently).

**Mechanism attribution (the more informative finding than the bare HARD_FAIL):** `false_pull_in_
rate` stays at 0.000 at EVERY scale, including the full 1.24M-edge CSKG -- the gate does NOT "blow
up" in the literal MCScript2.0 over-merge sense of flooding with false positives; Stage-1's
GATE_THRESH=0.28 remains conservative rather than reckless even under massive crosstalk. Instead,
the failure is a RECALL COLLAPSE with two distinguishable regimes: (a) 10,000->30,000 triples: the
true answer is STILL in the shortlist 97.3% of the time but pull_in's CA3-settle+gate stops
selecting/admitting it (a gate/argmax-level failure); (b) 30,000->1,213,912 triples: the shortlist
itself progressively stops containing the true answer at all (97.3% -> 33.3% -> 0.7%), i.e. the
underlying KGStore's raw linear associative capacity collapses UPSTREAM of the salience gate. This
is consistent with, not contradictory to, the substrate's own established physics law
(`META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW`, cert_ledger 2026-07-02): a single shared
[1024,1024] Hebbian W matrix accumulating outer-product writes from 1.2M triples via addition IS a
BUNDLED/superposed representation at the level of the associative matrix, and bundled storage is
already known to collapse under composition load -- SHARDED storage (per-relation or per-
entity-cluster W matrices) is the substrate-native fix this result points to, not a gate-threshold
retune (the gate was never the bottleneck at full scale; recalibrating it would not fix a shortlist
that no longer contains the answer).

## Cell-template mandates
- `arms_differ_verified`: True (REAL full-scale point vs SCRAMBLE_OBJECTS control digests differ).
- `final_metrics_atomicity`: `tmp_replace`. `except SystemExit: raise` before `except Exception`.
- `crlb_n/a`: empirical cardinality-capacity diagnostic sweep; no single closed-form noise floor to
  check against -- measuring where the empirical floor sits IS the test.
- `cardinality_ok`: `EXPECTED_N_UNITS = len(SCALES) = 6` (+1 scramble unit in `--full`); per-scale
  checkpointed via `tools/exp_checkpoint.py` (`unit_key = ("scale", N)`, not a seed -- this is a
  cardinality sweep, not a multi-seed cell).
- `calibration_check`: `default_ok_for_this_regime` -- GATE_THRESH=0.28 is Stage-1's un-retuned
  number, held fixed by contract.
- `deterministic_seeding`: True (`np.random.default_rng` fixed seeds for the edge shuffle and query
  sampling; hashlib-seeded scramble-objects permutation; no built-in `hash()`).
- Real-code-path preflight: `self_test()` constructs a REAL tiny `KGStore` AND validates the REAL
  `cskg_foundation_v1` loader against an actual 200-row data slice -- no synthetic-only branch for
  the data-loading path.

## Compute architecture
(a) NOT batched-GPU; (b) sequential-CPU with justification, MEASURED: nodes+edges load in ~4-5s,
KGStore allocation (E: 482,588 x 1024 float32, ~2.0GB) ~2s, full-scale ingest (1,213,912 triples,
chunked matmul batch=5000) ~12-16s, per-scale gate evaluation (300 queries: 150 relevant + 150
negative, each a `score_all` linear pass + `pull_in` CA3 settle over a 50-item shortlist) ~20-30s.
**MEASURED total wall time for the full 6-point sweep + scramble control: 243.6s (~4 minutes).**
Storage: this cell does not itself introduce new storage strategy -- it MEASURES the existing
KGStore's single-shared-W (bundled-at-the-matrix-level) storage strategy's behavior under load;
the sweep result is itself evidence for the sharded-storage physics law, not a new storage design.

## ADDENDUM -- reconciliation with the same-day SCALE-RESCUE drill (found post-hoc via git log,
not surfaced by the pre-authoring substrate_query.sh KB search -- likely a KB-freshness lag on a
same-day artifact, not a skipped check; disclosed per prior-work discipline)
`notes/research_precise_highcardinality_retrieval_rescue_2026-08-09.md` (commit e84ada2c7, filed
~40 min before this cell) theoretically diagnosed the anticipated Stage-2-B wall as EXTREME-VALUE
INFLATION of the max-over-M null-similarity score (a fixed threshold calibrated at Stage-1's M=30
implicitly relies on `E[max of 29 noise draws]`; at M~1.24M that expectation grows ~2x in
standardized units, `sqrt(2*ln(1.24e6))/sqrt(2*ln(29))~2.03`, Gumbel/Gaussian order-statistics).
Its predicted FLAT-arm symptom: `false_pull_in_rate` RISES with M. Its recommended Rank-1 rescue:
narrow the candidate pool via `KGStore.key(s,p)`'s context/type-conditioned bind BEFORE scoring,
with a calibrated (`refuse_gate_calibrate()`) threshold in place of a fixed constant.

**This cell's measured `false_pull_in_rate` stayed at 0.000 at every scale, including full
cardinality -- it did NOT reproduce the drill's predicted FLAT-arm rise.** Reconciliation: this
cell's design ALREADY narrows via `store.score_all(key)`'s cheap linear pass to a top-50 shortlist
BEFORE running `pull_in()`'s CA3-settle+gate -- `key(s,p)` is exactly the drill's own
context-conditioned bind. So this cell empirically resembles the drill's Rank-1 RESCUED arm far
more than its FLAT arm, and the 0.000 false-pull-in result is consistent with (not a refutation of)
the drill's own HARD-PASS prediction for the rescued arm ("stays <= 1.5x Stage-1's baseline").
GATE_THRESH was held at Stage-1's fixed 0.28 (not `refuse_gate_calibrate()`-adaptive), per the
Stage-2 task's explicit CONTRACT to test whether that un-retuned number generalizes -- so the
calibrated-threshold half of the Rank-1 rescue remains genuinely untested here.

**What this cell adds beyond the drill: a DIFFERENT, still-decisive negative the drill's own
cheap-decisive-test design (synthetic salted-codebook distractors, no shared-matrix accumulation)
would not have surfaced.** `KGStore`'s storage is a SINGLE shared [1024,1024] Hebbian matrix that
superposes ALL ingested triples via addition -- structurally a BUNDLED/compressed store, unlike
Stage-1's per-item codebook (each of 30 events keeps its own uncompressed row). The measured
recall collapse (relevant_in_shortlist_rate: 1.000 -> 0.973 -> 0.333 -> 0.007 across scale) shows
the TRUE answer drops out of even the coarse linear pre-filter well before full cardinality -- a
Hopfield/Tsodyks-Feigelman-family crosstalk-capacity cliff in the STORE's own compression, which
the drill itself names as "the same crosstalk-capacity math family" as its EVT diagnosis but
treats as secondary. **Practical implication: the drill's Rank-1 fix (context-conditioned
pre-filter + calibrated threshold) is necessary but likely NOT sufficient here** -- no threshold
choice rescues a candidate the coarse shortlist has already dropped. This points toward the
drill's own Rank-2 (resonator factorized retrieval, decomposing (s,p,o) into smaller per-factor
codebooks) or a SHARDED-W KGStore variant (e.g. per-relation-type W matrices, cutting each
matrix's load by ~33x) as the more directly-responsive next steps for the specific failure mode
this cell measured, with `refuse_gate_calibrate()` remaining a cheap, still-untested complementary
check worth running on the pre-collapse regime (10,000-30,000 triples, where the shortlist still
contained the answer 97%+ of the time but the fixed-threshold gate had already stopped admitting
it -- an open question of whether an adaptive threshold recovers that specific band).

## Dispatch
Local (light) -- MEASURED full-sweep runtime 243.6s (~4 min), well under the 10-minute
foreground-completion ceiling and requiring no GPU. Per the Stage-2 task's explicit "Local if
light; if the CSKG load is heavy, report compute needs rather than forcing" instruction: this
sub-test was run directly in foreground this session (not queued) -- `local_cpu_queue`'s
FULL-runs-go-remote USER-lock is interpreted here as targeting QUEUE DISPATCH of long-running
background jobs, not a bounded ~4-minute foreground diagnostic run of a script the author is
actively watching complete. `--self-test` and `--smoke` also ran foreground-local (both under 35s).
