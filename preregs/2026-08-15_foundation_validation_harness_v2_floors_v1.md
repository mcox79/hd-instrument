# Pre-reg: foundation_validation_harness_v2_floors_v1

Director task (2026-08-15, C13 re-run): the ONLY validation of the reading-grown foundation is
`data/exp_foundation_validation_harness_v1/metrics.json` (2026-08-12T14:27:19Z,
`HARD_PASS_foundation_validated`). Two problems: (1) it ran with no floor arms at all -- under the
standing gate rule ("a gate is a CI-separated margin above max(orthographic, frequency, scramble)
on the identical scorer/n/pool/gold, never a bare absolute number") that makes it NOT_EVALUABLE,
not a pass; (2) it validated `data/foundation_snapshots/reading_grounding_v1_full_20260812T142513Z/`,
frozen from `data/foundation/reading_grounding_v1/`, which is now a stale snapshot relative to
what is actually current.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "foundation validation floor orthographic frequency scramble known
answer draw spread"` -- run before design. This is a direct extension of the existing
`exp_foundation_validation_harness_v1.py` (novelty already established at that cell's own pre-reg,
`preregs/2026-08-12_foundation_validation_harness_v1.md`); this pre-reg documents the DELTA
(floor arms + known-answer arm + draw-spread), not a fresh novelty check on the base 3-claim
design. `tools/orthographic_floor_vet_v1.py` is the cited reference construction for the
orthographic floor (trigram + prefix/LCP, "strongest available zero-meaning attack" framing
reused verbatim).

## CORRECTED: which foundation snapshot is "current" (this was NOT settled before this pre-reg)
`notes/status_open_threads_c12_c13_recheck_hdi_testbed_2026-08-15.md` assumed
`reading_grounding_v5_termboundary` (latest directory mtime, Aug 12 16:29) was "current" without
opening it. **That assumption is wrong.** Fresh on-disk check this session:

- `reading_grounding_v3_definitional/`, `_v4_parsefix/`, `_v5_termboundary/` each contain ONLY a
  `definitional_facts*.jsonl` file -- raw output of a definitional-extraction pipeline STAGE, not
  an `HDFactStore` snapshot. None has a `store/` subdir or `concept_space.npz`. None is loadable
  by `hdlab.foundation_persistence.load_store`. They cannot be "the current foundation" for a
  store-validation harness because they are not stores.
- Only two directories are actual loadable store snapshots: `reading_grounding_v1/` (`store/`
  files dated Aug 12 09:46, `store_meta.json format_version: 1`) and
  `reading_grounding_v2_qualityfix/` (`store/` files dated Aug 12 13:55, `format_version: 2`).
  `v2_qualityfix` is later, a newer schema version, and its own directory name states it is a
  correction over v1.
- MEASURED@this session (`load_store` on `data/foundation/reading_grounding_v2_qualityfix/store`):
  `n_dim=2048, seed=1001`, 2146 total facts (`KNOWN_WORD=1512, GROUNDED_MEANING=634`), of the 634
  live GROUNDED_MEANING facts **0 are self-grounded** (`subject==obj`), all 634 are cross-grounded,
  315 valid no-leak 2-hop chains available.
- This independently corroborates the MEMORY.md banner correction ("self-tautology framing... was
  later found to be an ELIGIBILITY BUG, live tautology rate 0%, not 65.7%") -- v1's 65.7%
  self-grounded rate and v2_qualityfix's 0% are a direct match to the "before/after the eligibility
  fix" story already on record. **v2_qualityfix, not v1 and not v5, is treated as the current
  foundation for this re-run.** If a later snapshot supersedes v2_qualityfix by the time this is
  read, re-verify with the same check (does it have a `store/` subdir, what `format_version`) before
  trusting a directory name or mtime alone -- this is the exact "enumerate then verify contents,
  never trust a name" mistake being corrected here.

## READ-ONLY constraint
`data/foundation/` is read-only for this cell. The only write into it is `shutil.copytree` FROM
`data/foundation/reading_grounding_v2_qualityfix/` INTO a NEW directory under
`data/foundation_snapshots/<tag>_<UTC-ts>/` (the existing `--freeze-from` mechanism, unchanged from
v1). No file inside `data/foundation/` is ever opened for writing.

## What is NEW relative to v1 (the delta this pre-reg governs)
v1's 3 claims + their existing controls (decoy-chance for claim1, inter-cluster null for claim2a,
contradiction-scan for claim2b, scramble+ablation+no-leak for claim3) are REUSED UNCHANGED by
importing `experiments.exp_foundation_validation_harness_v1` as a module (wire-don't-island; no
duplicate reimplementation of already-self-tested primitives: `cooccurs`, `wilson_ci`,
`cohesion_gap`, `build_scrambled_store`, `build_two_hop_chains`, `query_single`,
`build_active_relation_map`, `find_active_contradictions`, `load_corpus_sentences`,
`_write_start_marker`, `_write_crash_metrics`, `_atomic_write` are all imported, not copy-pasted).

Four additions, one per each of the brief's four requirements:

### (1) Orthographic + frequency floors (claims 1 and 3)
Reference construction: `tools/orthographic_floor_vet_v1.py` -- character-trigram Jaccard +
length-normalized longest-common-prefix, MAX of the two ("a floor should be the strongest
available zero-meaning attack", verbatim framing reused). New functions `char_trigrams`,
`trigram_jaccard`, `lcp_ratio`, `orthographic_score = max(trigram_jaccard, lcp_ratio)`,
`predict_orthographic_best(query, candidates)` -- ZERO store/ConceptSpace signal, pure string
transform on the query and candidate strings only.

Frequency floor: `predict_frequency_mode(candidates)` -- a single constant prediction (the most
common object in the live candidate pool, by count of facts naming it), ignoring the query
entirely (the "guess the most common answer no matter the question" no-meaning floor).

**Claim 1 (CORRECTNESS):** currently has ONE floor (`chance_hat`, a random-decoy pairing checked
by the SAME `cooccurs()` read-out). v2 adds `ortho_rate` (guess = orthographically-nearest object
to the lemma, from the same live-object pool, excluding literal self-match) and `freq_rate` (guess
= the single most corpus-frequent object among live objects, constant across all lemmas), BOTH
scored by the IDENTICAL `cooccurs(lemma, guess, sentences)` function, on the IDENTICAL sampled
`(lemma, canon_obj)` pairs, IDENTICAL corpus. `floor_max = max(chance_hat, ortho_rate, freq_rate)`.

**Claim 3 (CAN-REASON):** currently has scramble + ablation as its only floors (both mechanism-side
controls: same query() mechanism, altered data). v2 adds ortho/freq as MECHANISM-BYPASSING floors
(no store.query() call at all -- pure string/frequency guess), scored by the IDENTICAL
`C_hat == C` exact-match read-out, on the IDENTICAL sampled chain questions.
`floor_max = max(scrambled_accuracy_permutation, scrambled_accuracy_derangement,
ablation_accuracy, ortho_accuracy, freq_accuracy)`.

**Claim 2 (COHERENCE):** no orthographic/frequency floor added -- 2a's read-out is cosine
similarity of `ConceptSpace` vectors, which has no string-form analog that isn't already the
orthographic floor for a DIFFERENT claim; adding one would not be testing the same functional
requirement (representational coherence, not lexical prediction). Declared `n/a_wrong_claim_shape`
rather than silently omitted.

### (2) Scramble floor, named construction, both variants, conservative one used
v1's `build_scrambled_store` (`rng.shuffle(shuffled)`, Fisher-Yates) is a **plain permutation** --
it does NOT guarantee no subject keeps its real object (fixed points are possible). v2 adds
`build_scrambled_store_derangement`: same fixed-seed shuffle, then a repair pass swapping any
`shuffled[i] == original[i]` with a later index (index i+1 mod n, walked forward on collision) to
guarantee zero fixed points -- a genuine **degree-preserving derangement**, stricter than v1's
permutation. Both are computed for claim 3; per the brief ("name which scramble construction you
use... the looser one is the more conservative floor"), the OFFICIAL claim-3 scramble floor used in
the gate is `max(scrambled_accuracy_permutation, scrambled_accuracy_derangement)` (whichever scores
higher is the more conservative, harder-to-clear floor) -- both numbers are reported regardless.

Claim 2 also gets a scramble floor it did NOT have before: `scrambled_cohesion_gap` -- rebuild
`clusters_lemmas` with canon_obj labels shuffled (SAME derangement construction, applied to the
cross-grounded subject->obj pairs), recompute `cohesion_gap` over the SAME `ConceptSpace.bundle()`
vectors (only cluster MEMBERSHIP changes, not the vectors -- this is the read-out-invariance point
below). Expectation: near 0, since real vectors under arbitrary (scrambled) membership should show
no cohesion advantage unless the vectors themselves spuriously correlate with the shuffle (they
should not, given a fixed seed unrelated to vector content).

### (3) Known-answer arm (mandatory instrument check, claim 3)
Distinct from the EXISTING self-test (`_selftest_reason_mechanism_and_controls`, which runs at
`n_dim=512` on ~3 chains -- a formula-level check, not a production-scale one). v2 adds
`run_known_answer_arm`: builds a companion `HDFactStore` at the SAME `n_dim` as the real loaded
store (2048, i.e. production scale -- this is the DISCRIMINATOR-MUST-SURVIVE-SCALE discipline
applied to the INSTRUMENT itself, not just the mechanism-under-test), plants K=20 noiseless 2-hop
chains using synthetic tokens (`__ka_subj_i` / `__ka_mid_i` / `__ka_obj_i`, guaranteed disjoint
from real vocabulary), runs the IDENTICAL `query_single` mechanism used everywhere else in the
harness. Expected accuracy: 1.0 (noiseless, by construction). **If this arm's accuracy is below
0.90, the run emits `INSTRUMENT_INVALID` and the overall verdict is forced to
`INSTRUMENT_INVALID_ABORT` regardless of what any other claim measured** -- an instrument failure
at production n_dim invalidates every other number in the run, per the brief ("a cell went VOID
tonight because its instrument failed while its floors looked fine").

### (4) Between-random-projection-draw spread (claim 3; claim 2 partial, declared)
**Claim 3:** rebuild `N_DRAWS=5` companion `HDFactStore` instances over the IDENTICAL real
`(subject, obj)` GROUNDED_MEANING pairs (`gm_map`, the actual live foundation data, not synthetic)
using `store.seed + {0,1,2,3,4}` -- i.e. the SAME facts, DIFFERENT random hyperdimensional basis
draws. For each draw, on a fixed, capped sub-sample of the real sampled chain questions
(`min(50, n_sampled)`, to bound the 5x rebuild+query cost), recompute `mechanism_accuracy`,
`ablation_accuracy`, and `scrambled_accuracy` (paired derangement scramble, same shuffle seed
scheme). Report `gap_per_draw = mechanism_accuracy - max(ablation_accuracy, scrambled_accuracy)`
across the 5 draws: mean, sd, min. **HARD_PASS additionally requires
`mean(gap_per_draw) - 2*sd(gap_per_draw) >= 0.10`** -- the pass margin must survive substrate-basis
redraw noise, not just hold for the one draw that happened to be measured. This is the literal
"between-random-projection-draw spread" the brief requires, using the store's own `seed` parameter
as the draw axis (the FHRR/bipolar basis vectors are reseeded per draw; the facts are not).

**Claim 2:** a full basis-redraw for `ConceptSpace` would require re-running the multi-hour
reading-grounding encoder loop -- out of scope for a same-session validation re-run, and would
itself mutate/require new foundation output (against the read-only constraint's spirit for this
pass). Declared `deferred_out_of_scope: concept_space_basis_redraw_requires_multihour_reencode`.
A CHEAPER partial substitute IS run and reported: `cohesion_gap`'s own `k_neg` negative-sampling
draw (`rng` argument) is re-run at 5 different seeds over the SAME real vectors, reporting sd of
`cohesion_gap` due to negative-sampling noise alone (not full basis redraw -- labelled honestly as
a narrower check).

## Read-out invariance check (done on paper, before any code was written)
For every arm below: the TRANSFORM it applies, and whether the shared read-out can "see"
(distinguish) that transform vs. the real arm.

| claim | arm | transform | read-out | invariant? |
|---|---|---|---|---|
| 1 | REAL | store's actual `canon_obj` | `cooccurs(lemma,guess,sentences)` | read-out is blind to guess provenance -- correct |
| 1 | RANDOM (existing) | random decoy object | same `cooccurs` | blind -- correct |
| 1 | ORTHOGRAPHIC (new) | string-trigram/LCP argmax, zero store signal | same `cooccurs` | blind -- correct |
| 1 | FREQUENCY (new) | constant most-frequent object | same `cooccurs` | blind -- correct |
| 2a | REAL | real canon_obj cluster membership | cosine over `ConceptSpace.bundle()` | vectors untouched; only membership varies -- correct |
| 2a | SCRAMBLE (new) | derangement-shuffled cluster membership | SAME cosine, SAME vectors | vectors untouched -- if gap collapses, real gap wasn't a vector artifact |
| 3 | REAL | real store `query()` x2 | exact match `C_hat==C` | -- |
| 3 | SCRAMBLE perm/derangement (existing/new) | shuffled obj labels, SAME query() mechanism | same exact match | mechanism fixed, data varies -- correct discriminator shape |
| 3 | ABLATION (existing) | drop 2nd hop | same exact match | correct |
| 3 | ORTHOGRAPHIC/FREQUENCY (new) | bypass query() entirely, string/const guess | same exact match | mechanism-bypassing, not data-varying -- a DIFFERENT axis than scramble/ablation, correctly labelled as such, not conflated |
| 3 | KNOWN-ANSWER (new) | noiseless planted data, production n_dim, SAME mechanism | same exact match | tests the read-out/mechanism itself, not the foundation |

No row shows the read-out able to "see" (special-case) which arm produced a guess -- every arm is
scored by the same blind function. This check would have caught a mis-design before any compute
ran; it did not find one here, so the cell below is authored as designed.

## Bands (can-fail, explicit floor margins)

**Claim 1:** `floor_max = max(chance_hat, ortho_rate, freq_rate)`. HARD_PASS:
`precision_hat - floor_max >= 0.20` AND Wilson-lo(precision) > Wilson-hi(whichever arm achieved
floor_max). HARD_FAIL: `precision_hat - floor_max < 0.05`. MIDDLE_BAND: otherwise.

**Claim 2a:** HARD_PASS: `cohesion_gap >= 0.10` AND `cohesion_gap - scrambled_cohesion_gap >= 0.08`.
HARD_FAIL: `cohesion_gap <= 0.02` OR `cohesion_gap - scrambled_cohesion_gap < 0.02`. MIDDLE_BAND:
otherwise. Negative-sampling draw-spread reported descriptively (`cohesion_gap_negsample_sd`); if
`(cohesion_gap - scrambled_cohesion_gap) < 3 * cohesion_gap_negsample_sd`, additionally flag
`NOT_ROBUST_TO_NEGSAMPLE_DRAW` (does not override the verdict, since this is the narrower
substitute check declared above, but is surfaced).

**Claim 2b:** unchanged from v1 (`active_contradiction_count == 0`).

**Claim 3:** `floor_max = max(scrambled_accuracy_permutation, scrambled_accuracy_derangement,
ablation_accuracy, ortho_accuracy, freq_accuracy)`. HARD_PASS: `mechanism_accuracy >= 0.50` AND
`mechanism_accuracy - floor_max >= 0.20` AND `leaked_count == 0` AND
`known_answer_arm_accuracy >= 0.90` AND `mean(gap_per_draw) - 2*sd(gap_per_draw) >= 0.10`.
HARD_FAIL: `leaked_count > 0` OR `mechanism_accuracy - floor_max < 0.05` OR
`mechanism_accuracy < 0.10` OR `known_answer_arm_accuracy < 0.50` (instrument invalid).
MIDDLE_BAND: otherwise.

**Overall:** `known_answer_arm_accuracy < 0.50` on ANY mode (smoke or full) forces
`INSTRUMENT_INVALID_ABORT` overriding all 3 claims. Else: `HARD_PASS_foundation_validated` iff all
3 claims HARD_PASS; `HARD_FAIL_foundation_validation_failed` if any claim HARD_FAILs; else
`MIDDLE_BAND`.

`crlb_n/a`: same reasoning as v1 -- discrete exact-match / co-occurrence gap metrics, no Gaussian
capacity floor applies to any of the new arms either (orthographic/frequency are discrete argmax
predictions, scored the same exact-match/cooccurs way).

## SCHEMA-VET gates (delta from v1; unchanged items not restated)
- `arms_differ_verified`: extended to include the new floor arms' prediction arrays (ortho picks,
  freq picks, derangement-scramble picks) in the hash-uniqueness check.
- `final_metrics_atomicity`: `tmp_replace` (unchanged).
- `deterministic_seeding`: true -- all new RNG use is `random.Random(<fixed int>)`, derangement
  repair walk is a deterministic forward-index scan (no `hash()`/`list(set())`).
- `cell_chunked`: false (unchanged; still no seed-axis sweep in the runner sense -- the 5 draws are
  an in-cell robustness sub-analysis of claim 3, not separate dispatched cells).
- `real_code_path_exercised`: [HDFactStore, ConceptSpace] (unchanged) plus the known-answer arm now
  ALSO exercises `HDFactStore` at PRODUCTION `n_dim=2048` in the self-test tier (not just 512),
  closing the "self-test never exercised production scale" gap.
- `progress_logging`: `print_flush_true` -- v1 already uses `flush=True` on all prints; v2 adds the
  same on every new print line. Full-mode wall time is estimated below; if it clears 1800s the
  MANDATORY heartbeat cadence is honored via the existing per-claim print lines (every draw / every
  ~500 units).

## Estimated wall time
v1's FULL run (7966 facts, N=150/150/all) took 125.3s. v2_qualityfix is SMALLER (2146 facts vs
7966, 634 GM vs 3544). New costs: frequency floor requires per-object corpus-frequency scan
(O(|distinct_objects| x |sentences|), distinct_objects likely low hundreds, sentences ~31k FULL --
estimated 10-40s); 5x claim-3 store rebuild at reduced N=50 sub-sample (~5x a sub-second-to-few-
second rebuild, estimated well under 30s total); derangement construction and orthographic scoring
are O(N x pool) string ops, expected seconds. **Total FULL estimate: 60-180s**, well under the
30-minute ceiling: no detached-process launch should be structurally REQUIRED, but this pre-reg
still launches via `Start-Process` per the task brief's instruction, and polls for `metrics.json`
rather than blocking synchronously, in case the estimate is wrong (self-tests/smoke will confirm or
correct this estimate before FULL is launched).

## Dispatch
`local_cpu_queue` is smoke-only per the standing rule; this IS the smoke step. FULL is launched
locally (detached `Start-Process`, per the task brief -- this is a one-off validation re-run, not
a sweep cell suited to queue_add). No origin push. No `data/foundation/` writes.
