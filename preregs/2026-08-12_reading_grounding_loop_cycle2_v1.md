# reading_grounding_loop_cycle2_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: hdi_research full-auto all-night MISSION cycle 2
("GROW THE FOUNDATION by reading -- fix the no-persistence blocker so the foundation
ACCUMULATES across cycles, then read a LARGE new batch on top"), 2026-08-12. Cycle 2 of the
resumable multi-cycle reading-to-grow effort (cycle 1: commit e38fd8454, HARD_PASS, 0->185
grounded concepts).

**Prior-work check** (`bash tools/substrate_query.sh "hd fact store persistence save reload
cumulative foundation growth across cycles"`, cosine>0.30 threshold): top hits were
`positive/negative regulation of growth` (Gene Ontology entities, cos~0.305, unrelated --
coincidental lexical overlap on "growth"), `hd_fact_store` itself (capability_registry entry,
cos=0.3047 -- confirms the module is WIRED, says nothing about persistence), and `hd_fact_store.py`
design-note mentions (cos=0.292, below threshold). **No prior cell or note implements save/reload
for HDFactStore, ConceptSpace, or the reading-grounding Library.** This is genuinely novel
infra, not a rediscovery.

## What this cell IS

Two deliverables, both additive/sidecar (no existing-module behavior changed):

1. **`hdlab/foundation_persistence.py`** (NEW module) -- deterministic save/reload for the full
   reconstructible state of one reading-loop run: `HDFactStore` (facts + the order-sensitive
   symbol codebook + the role-key/generator state that makes a reload's future symbol
   registrations continue the SAME pseudorandom stream an uninterrupted run would have used --
   see that module's docstring for why the codebook cannot merely be re-derived from `seed`),
   `ConceptSpace` (per-lemma raw context-vector accumulators), and the reading-loop `Library`'s
   PENDING items (partial-exposure evidence not yet grounded -- so a word at 3/4 exposures at
   the end of one segment can still reach `MIN_CONFIRM=4` and ground using evidence pooled
   ACROSS the save/reload boundary, the actual mechanism this mission needs). Format: one
   directory per snapshot, `np.savez_compressed` (tensors/arrays) + `json` (plaintext/config),
   matching the two existing on-disk conventions already in this codebase
   (`hdlab.additive_map`'s safetensors+json split; `hdlab.arc_parser`'s `np.savez_compressed`) --
   no new dependency, no pickle of arbitrary objects. Five self-tests, the strongest being
   `_selftest_continuation_matches_uninterrupted_run` (save -> reload -> continue-adding-facts
   produces a store BIT-IDENTICAL, `torch.equal`, to an uninterrupted run that never saved) and
   `_selftest_full_foundation_roundtrip_and_resume_grounds` (a word at 3/4 exposures survives a
   save/reload and GROUNDS on its 4th exposure fed to the reloaded state, with the
   Dumay-Gaskell intervening-pass rule staying correct across the reload via a persisted
   `next_pass_idx`). All 5 pass (see Smoke section).

2. **`experiments/exp_reading_grounding_loop_cycle2_v1.py`** -- the SEGMENTED measurement
   harness that (a) bootstraps a persisted foundation by reproducing cycle 1's exact
   `curriculum_real` run if none exists yet, (b) reads NEW, larger, harder curriculum material
   ON TOP of the loaded foundation across 4 further segments, checkpointing the grown
   foundation to disk after each, (c) runs an independent scramble-context control branch from
   the SAME bootstrap point to verify the mechanism still discriminates real context from
   scrambled at this larger scale, and (d) finalizes into one `metrics.json` with a verdict.

## Segments (each ONE CLI invocation; the persisted foundation IS the resume checkpoint --
a materially stronger resumability model than cycle 1's "cheaply recompute everything from
chunk 0" note, now retired in favor of real state carry-over)

| segment | new material | n_sentences | purpose |
|---|---|---|---|
| `bootstrap` | Ele[0:50]+Int[50:100]+science (IDENTICAL to cycle 1's pool) | 4640 | reconstruct + persist cycle 1's foundation; also writes a FROZEN control-copy snapshot the scramble probe branches from |
| `ele_cont` | OneStopEnglish Elementary, files [50:189] (unused by cycle 1) | 4623 | continue the easiest tier |
| `int_cont` | OneStopEnglish Intermediate, files [0:50]+[100:189] (unused by cycle 1) | 4952 | fill in + continue the middle tier |
| `adv_new` | OneStopEnglish Advanced, WHOLE tier [0:189] (new rung, harder register) | 7408 | next curriculum rung |
| `bio_new` | `data/corpora/textbook_concepts_biology` (OpenStax "Concepts of Biology", modern, CC-licensed) | 11332 | next SCIENCE rung beyond `process_articles_v1` |
| `scramble_probe` | same pool as `ele_cont`, but each occurrence's context window is an unrelated sentence (deterministic RNG draw) -- CAN-FAIL discriminator control, branched from the FROZEN post-bootstrap copy (independent of the growing foundation) | 4623 | verify real-vs-scramble discrimination survives at cycle-2 scale/volume |
| `finalize` | (no new text) | -- | aggregate all segment summaries + re-run persistence self-tests + write verdict |

Total NEW material read this cycle (excluding the `bootstrap` reproduction and the
`scramble_probe` control, which reads the `ele_cont` pool a second time under a different
condition): 4623 + 4952 + 7408 + 11332 = **28,315 sentences** (~6.1x cycle 1's entire pool).

`data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt` is Markdown; the
new `load_biology_sentences()` loader strips heading lines (`^#`) and list-marker prefixes
(`^[-*]\s+`, `^\d+\.\s+`) before applying the SAME `clean_sentences` regex cycle 1 already uses
(verbatim reuse, imported from `experiments.exp_reading_grounding_loop_cycle1_v1`). MEASURED:
11332 sentences, mean length 122.7 chars, 213/11332 (1.9%) are sub-15-char fragments (mostly
`clean_sentences`' own known "U.S." -> "U"/"S" split artifact, identical failure mode already
present -- and accepted -- in cycle 1's corpus cleaning; `content_words`' `len(w) > 2` filter
already screens these at the word level, so no additional filtering is added here).

## Corpus deviation note (inherited from cycle 1, still in force)

Per the standing USER directive (`feedback_stop_mcguffey_use_modern_sources_USER_2026-08-08`),
McGuffey-derived corpora are NOT used. All 5 new-material segments above are the MODERN sources
the cycle-2 task itself named (OneStopEnglish continuation tiers, `textbook_concepts_biology`).

## Genuinely NEW code in the harness (beyond the persistence module)

- `grounded_lemmas_in_store(store) -> List[str]`: the CORRECT cross-segment "foundation size"
  metric. Cycle 1 counted grounded lemmas by scanning `Library.items` for
  `status.startswith("GROUNDED")` -- valid only within one process's lifetime. Since PENDING
  Library items are persisted but terminal GROUNDED items are (by design, see the persistence
  module's disclosed scope decision) NOT re-populated into a reloaded Library, that scan would
  silently UNDER-COUNT after every reload. This function instead counts distinct subjects with
  a live `MEANING_RELATION` fact in `store.live_facts()` -- the store is genuinely the source of
  truth and survives reloads by construction, so this metric is correct across any number of
  save/reload boundaries. This is the single most important correctness fix this cell makes
  beyond the persistence module itself.
- `load_biology_sentences()`, `load_ele_continuation()`, `load_int_continuation()`,
  `load_adv_new()`: new corpus-slice loaders (thin wrappers over cycle 1's reused
  `load_onestop_level`/`clean_sentences`, or in the biology case a new Markdown-stripping
  loader).
- The segment-runner functions (`run_bootstrap`, `run_continuation_segment`,
  `run_scramble_probe`, `run_finalize`) -- new orchestration; every substrate call inside them
  (`process_sentence`, `checkpoint`, `HDFactStore`, `GapDetector` via `foundation_persistence`)
  is REUSED verbatim from cycle 1's own harness / `hdlab.reading_grounding_loop`.

## Pass-index continuity across reloads (a correctness risk this pre-reg calls out explicitly)

`consolidation_pass`'s Dumay-Gaskell intervening-pass rule requires an item survive to a pass
LATER than the one on which it first reached `MIN_CONFIRM`. If every segment restarted
`pass_idx` at 0, a PENDING item carried over from an earlier segment (whose
`first_min_confirm_pass` was recorded against that EARLIER segment's own 0-based numbering)
would have its intervening-pass check silently misapplied. `foundation_persistence.py`'s
manifest persists `next_pass_idx`; every continuation segment's checkpoints start numbering
from that value, not from 0, so cross-segment pass-index semantics stay identical to a single
uninterrupted run. Verified directly by `_selftest_full_foundation_roundtrip_and_resume_grounds`
(MEASURED: PASS, see Smoke section).

## Disclosed scope decision: ESCALATED Library items are not persisted

A word that hit `PATIENCE_MAX` (incoherent evidence) in one segment is NOT carried forward as
"permanently given up on" -- it is simply absent from the reloaded (empty) Library, so a new
occurrence in a later segment starts a fresh PENDING item for it. This is a disclosed
simplification, not an oversight (see `hdlab/foundation_persistence.py` module docstring for the
full rationale): it does not affect the FOUNDATION's grounded-concept count (the mission's
actual measured quantity), only whether a specific incoherent word gets a second chance.

## Envelope-fail-bands

**Gate 1 (mechanical, binary): PERSISTENCE ROUND-TRIP.** `foundation_persistence`'s 5 self-tests
(store round-trip, continuation-matches-uninterrupted-run, ConceptSpace round-trip, Library
pending round-trip, full-foundation round-trip + cross-reload grounding) must ALL pass, both at
`--mode self_test` time (pre-dispatch gate) AND re-verified live inside `finalize` (so the
verdict's evidence is MEASURED at verdict time, not merely "passed earlier"). Any failure here
is an automatic HARD_FAIL regardless of growth numbers -- a foundation that "grows" via silent
non-determinism or corruption is not a real win.

**Gate 2 (growth): CUMULATIVE FOUNDATION GROWTH.**
`foundation_size_cycle2_end = len(grounded_lemmas_in_store(final store))` (MEASURED at
`finalize`, read directly off disk, not accumulated in-process) vs
`foundation_size_cycle2_start` (the `bootstrap` segment's own grounded count, expected close to
cycle 1's MEASURED 185 -- reported as a diagnostic `bootstrap_matches_cycle1_exactly` field,
not itself gated, since exact cross-process/cross-torch-version RNG bit-reproduction is a nice-
to-have, not the mission's actual claim).

**Gate 3 (controls, each individually reported + jointly gating HARD_PASS):**
- `no_leak_ok`: zero grounded lemmas are members of `known_seed` across every continuation
  segment (structural + a metrics-time set-membership check).
- `monotone_ok`: `foundation_size_in_store`, recorded at every checkpoint across ALL segments
  concatenated (`growth_curve_all`), is non-decreasing end to end (structural by construction --
  `HDFactStore` never deletes a live fact -- verified, not merely assumed).
- `scramble_ratio = n_newly_grounded(scramble_probe) / n_newly_grounded(ele_cont)` (both over the
  IDENTICAL 4623-sentence pool from the IDENTICAL bootstrap starting point) must discriminate:
  real growth from real context must substantially exceed growth from scrambled context, at the
  larger cycle-2 scale/volume (repeats cycle 1's own CAN-FAIL discriminator, since volume/
  register was exactly the axis cycle 1's own calibration amendment worried about).

**HARD_PASS**: Gate 1 all-pass AND
`foundation_size_cycle2_end - foundation_size_cycle2_start >= 20` AND `no_leak_ok` AND
`monotone_ok` AND (`scramble_ratio is None` (zero real growth on the probe pool, degenerate) is
EXCLUDED from this branch -- see HARD_FAIL) `scramble_ratio < 0.5`.

**MIDDLE_BAND**: Gate 1 passes AND foundation grows (`> 0` but `< 20` new concepts this cycle),
OR Gate 1 passes and growth clears 20 but `scramble_ratio` lands in `[0.5, 0.8)` (present but
weaker discrimination than cycle 1's own 0.286 -- degraded, not collapsed).

**HARD_FAIL**: Gate 1 fails (ANY persistence self-test fails) OR
`foundation_size_cycle2_end <= foundation_size_cycle2_start` (no cumulative growth -- the core
mission claim is false) OR `scramble_ratio >= 0.8` (mechanism no longer discriminates real
context from scrambled at this volume -- the 2026-07-18 wall recurs at scale).

`discriminator_reachability`: TRUE. `crlb_n/a`: "no continuous-noise-floor discriminator; the
growth/discrimination gates are discrete counts over real corpora, not a capacity-bound signal,
identical justification to cycle 1's pre-reg." `bracket_includes_discriminating_band`: n/a for
the same reason (not a swept-parameter cell).

## Compute architecture

(b) sequential-CPU with justification: identical justification to cycle 1 (regex tokenization +
hashlib-seeded D=256 numpy bipolar bundles + small CA3 attractor matmuls, no GPU-batchable dense
workload). Per-segment wall time estimated from cycle 1's MEASURED throughput
(4640 sentences / 110.82s = ~42 sentences/s, MEASURED@data/exp_reading_grounding_loop_cycle1_v1/
metrics.json:results_by_condition.curriculum_real): `bootstrap`~110s, `ele_cont`~110s,
`int_cont`~118s, `adv_new`~176s, `bio_new`~270s, `scramble_probe`~110s, `finalize`<5s. Every
segment individually fits well inside a single foreground Bash call under the INLINE-LOCAL
mandate's 10-minute cap; segments are dispatched as SEPARATE sequential foreground calls (never
backgrounded) specifically so the newly-built persistence layer is the thing carrying state
across calls, not in-process memory -- this is a deliberate exercise of the actual deliverable,
not a workaround. Storage strategy: sharded (unchanged from cycle 1 -- every grounded fact is
its own `HDFactStore` entry).

## Functional requirements

- Persist + exactly reconstruct a live `HDFactStore` (incl. the order-sensitive symbol codebook
  and RNG continuation) -> NEW `hdlab/foundation_persistence.py` (no existing primitive covers
  this; `hdlab.additive_map.save/load` and `hdlab.token_vocab.save/load` are the closest
  precedents but neither's target class has this module's order-dependent-codebook-plus-live-
  generator-state shape).
- Persist + reconstruct `ConceptSpace` (canonicalization comparison pool) -> NEW, same module.
- Persist partial (PENDING) multi-exposure evidence so cross-cycle accumulation is genuine, not
  merely a bigger single run wearing a "cycle 2" label -> NEW, same module.
- Correctly COUNT the cumulative foundation size across reload boundaries ->
  `grounded_lemmas_in_store` (this cell; existing `Library`-scan approach is process-lifetime-
  scoped and would silently undercount).
- Everything else (FLAG/GATE/CONSOLIDATE/CANONICALIZE/PROMOTE mechanism) -> unchanged reuse of
  cycle 1's `hdlab.reading_grounding_loop` + `hdlab.grounding_acquisition_loop` +
  `hdlab.gap_detector`.

## Schema-VET fields

- `cell_chunked`: true (chunk = 150 sentences within a segment, per cycle 1's convention; PLUS a
  SEGMENT-level chunking layer, a disclosed adaptation of the per-seed chunking convention to
  this persistence-driven use case -- each segment is independently resumable/idempotent via a
  `segment_done|<name>` unit key in `tools/exp_checkpoint`, and re-invoking an already-completed
  segment is a safe no-op).
- `cardinality_ok`: n/a in the traditional swept-axis sense (no sweep parameter); the analogous
  guard here is `finalize` refusing to run (`RuntimeError`, loud) if any of the 6 prerequisite
  segments' `segment_done` unit is missing from `units.jsonl`.
- `final_metrics_atomicity`: "tmp_replace" for the cell's own `metrics.json`; every
  `foundation_persistence` write (store/concept-space/library-pending/manifest) is independently
  atomic via `.tmp` + `os.replace` (META_RULE_AH, applied at BOTH layers).
- `arms_differ_verified`: true -- `finalize` asserts `ele_cont`'s newly-grounded lemma set and
  `scramble_probe`'s newly-grounded lemma set are NOT identical (verified in Smoke section).
- `except SystemExit / except Exception` ordering: enforced (grep-gated in this cell's own
  self-test, identical pattern to cycle 1; `foundation_persistence.py` contains no bare/
  BaseException catches either -- its two `except AssertionError` blocks in the cell's
  `run_finalize`, not the module itself, are the only non-bare catches, both SPECIFIC classes
  per META_RULE_J).
- `calibration_check`: "default_ok_for_this_regime" -- `SCHEMA_THRESH=0.25`, `MIN_CONFIRM=4`,
  `GAP_FLOOR=0.625` are ALL reused verbatim from cycle 1's OWN disclosed calibration amendment
  (not re-tuned), per the cycle-2 task's explicit instruction to keep the calibrated threshold.
- `progress_logging`: "print_flush_true" -- every chunk within every segment prints one flushed
  progress line (`elapsed_s < 1800` per segment so the `>=1800s` mandatory rule does not strictly
  apply, but included anyway for observability across a multi-call sequence).

## Dispatch

INLINE-LOCAL, foreground, no queue/remote/push (per the cycle-2 task's explicit constraint).
Sequence: `--mode self_test`, then `--mode smoke` (exercises the full segmented pipeline at
tiny scale + a fresh smoke-scoped foundation dir, never touching the real one), then
`--mode full --segment bootstrap`, `ele_cont`, `int_cont`, `adv_new`, `bio_new`,
`scramble_probe`, `finalize` -- 7 SEPARATE sequential foreground Bash calls, each well under the
10-minute cap per the Compute-architecture section's per-segment estimates.
