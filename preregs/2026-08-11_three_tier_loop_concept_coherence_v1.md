# Pre-registration: three_tier_loop_concept_coherence_v1

## Context / motivation

`exp_three_tier_loop_independence_weighted_confirm_v1` (commit 62dafbc08, HARD_PASS) solved the
count-gate: the independence-weighted confirmation score correctly separates genuine 2-3-source
corroboration (crosses) from N repeats of one source (never crosses). But it disclosed a SECOND,
newly-surfaced floor: the retain gate is a CONJUNCTION of the (now-fixed) count gate AND a separate
schema-coherence check (`hdlab.grounding_acquisition_loop.schema_consistency_split_half`), which
compares two halves' accumulated per-encounter CONTEXT VECTORS by raw cosine of a bag-of-random-
hash-words bundle. MEASURED@data/exp_three_tier_loop_independence_weighted_confirm_v1/metrics.json:
closed-form audit shows 36/36 real 2+-source gaps cross the (fixed) count gate, but end-to-end only
15/36 actually retain into the middle tier -- 21 gaps cross the count gate and then get blocked by
schema-coherence. Root cause (measured during that cell's authoring): CSKG-style and KB-role-schema-
style source text for the SAME gap share few surface words (cos=0.039 < schema_thresh=0.10) because
each source's template mentions a DIFFERENT subset of the gap's entities (CSKG: whole+material; KB:
process+material) diluted by source-specific boilerplate ("CSKG external knowledge base records
that... bridges to... via relation(s)" vs "ProPara process physics KB lists... among... terms for
process...") -- the SAME fact, worded differently by two sources, fails a literal-surface-overlap
check even when a human (or an ATL amodal-concept hub) would recognize them as clearly compatible.

This cell tests the brain-foundational fix: replace the surface-TEXT-overlap coherence check with
the OWNED graded `hdlab.lexical_similarity.concept_similarity` organ (the ATL amodal-concept-hub
analog, McRae-style shared-feature lexicon, already independently validated HARD_PASS at commit
7d0a574b4 and EXTENDED 2026-08-10 with exactly this ProPara process-physics vocabulary) so two
traces are judged coherent by MEANING (shared or near-synonymous domain concepts), not by which
random-hash boilerplate words happen to literally match.

## Design: concept-similarity-based coherence metric

Defined in THIS CELL (the organs stay generic; `schema_consistency_split_half` gets an additive
`coherence_fn` hook and knows nothing about words or concepts -- see "Organ changes" below).

```
CONCEPT_MATCH_THRESHOLD = hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD  # = 0.50, REUSED
                                                                                # VERBATIM, not
                                                                                # re-tuned by this
                                                                                # cell (that
                                                                                # organ's own
                                                                                # independently
                                                                                # pre-registered
                                                                                # near-synonym bar)
schema_thresh = 0.10   # codebase default (hdlab.grounding_acquisition_loop.consolidation_pass /
                        # hdlab.prelim_tier.PRELIM_SCHEMA_THRESH), UNCHANGED -- not tuned down to
                        # force a pass (same non-p-hacking discipline as the parent cell)
```

`concept_coherence_score(traces_a, traces_b, episode_text)`:
1. Pool each half's raw source text (via `episode_text[trace.episode_id]`), extract content words
   (`hdlab.grounding_acquisition_loop.content_words`, the same tokenizer `context_vector` uses),
   keep ONLY words that are IN the `hdlab.lexical_similarity.CONCEPT_FEATURES` lexicon (drops
   source-provenance boilerplate -- "external", "knowledge", "base", "records", "bridges", "lists",
   "among", "terms" -- none of which are scientific-domain concepts -- leaving only the substantive
   entity mentions: materials, and occasionally processes).
2. For every in-lexicon word in half A, check whether it has a MATCH in half B: literal string
   equality, OR `concept_similarity(word, other) >= CONCEPT_MATCH_THRESHOLD`. Symmetric (also check
   every B word against A).
3. Score = fraction of all pooled in-lexicon words (both halves) that found a match. Returns 0.0
   (not None) if either half has zero in-lexicon words -- "cannot judge from concept-content" is
   conservative deny, matching `concept_similarity`'s own OOV="cannot judge" contract and the
   parent cell's `CORRELATED_WEIGHT` "deny-by-default: never assume" philosophy.

**Design validated empirically BEFORE running the real pipeline** (ad hoc script, not part of the
cell, same discipline as the parent cell's own authoring-time spot-check):
- Real paraphrase case (CSKG "...cotton_candy bridges to sugar..." vs KB "...lists sugar among
  ['produces'] terms for process photosynthesis."): NEW score = 0.667 (>= 0.10, coheres); OLD raw-
  cosine score on the identical pair < 0.10 (the exact disclosed failure). in-lexicon words:
  CSKG={sugar}, KB={photosynthesis,sugar} -- "sugar" is a literal match; photosynthesis-vs-sugar
  concept_similarity=0.246 (below the 0.50 match bar, correctly NOT counted as a match on its own,
  the literal "sugar" match alone is what carries the pair over 0.10).
- Cross-domain negative (wood/ash-combustion text vs water/photosynthesis text, i.e. two
  DIFFERENT gaps' texts paired together): NEW score = 0.0 (correctly rejected).
- Same-domain DIFFERENT-material negative ("wood" vs "coal", both COMBUSTION_CONSUME_ROLE):
  concept_similarity(wood,coal)=0.450 -- BELOW the 0.50 match bar (binarizing at
  CONCEPT_MATCH_THRESHOLD is what keeps a same-role-different-specific-material pair from being
  treated as "the same fact" -- an earlier un-binarized average-cosine design scored this pair
  0.45, ABOVE schema_thresh=0.10, which would have been exactly the "merges everything" failure
  mode this pre-reg's can-fail control below is designed to catch; binarization at the ALREADY-
  validated CONCEPT_MATCH_THRESHOLD fixes it). NEW score with binarization = 0.0 (correctly
  rejected) -- this is this cell's "wrong-material pair must still be rejected" control.
- The same wood(CONSUME)/ash(PRODUCE) pair also stands in for a "wrong-fate" control (same process,
  opposite role = opposite fate direction for the SAME material family) -- also 0.0.

## Organ changes (additive only, byte-for-byte backward compatible; VERIFIED before authoring)

1. `hdlab/grounding_acquisition_loop.py::content_words` -- NEW pure function, extracted verbatim
   from `context_vector`'s own word-filter (regex + stopword + length>2 rule); `context_vector` now
   calls it internally (refactor, not a behavior change -- MEASURED: `grounding_acquisition_loop.
   self_test()` reproduces identical `coherent_score=1.0` / `scrambled_score=0.108` after the edit).
2. `hdlab/grounding_acquisition_loop.py::schema_consistency_split_half` -- new param
   `coherence_fn: Optional[Callable[[List[Trace], List[Trace]], float]] = None`. Default None
   preserves the exact prior raw-cosine computation byte-for-byte; when supplied, called on the two
   half-lists INSTEAD of the raw cosine. The `n < 2*min_half_size -> None` defer gate is unchanged
   (orthogonal to which coherence metric is used).
3. `hdlab/grounding_acquisition_loop.py::consolidation_pass` -- new kwonly param `coherence_fn`,
   threaded through unchanged to `schema_consistency_split_half`.
4. `hdlab/prelim_tier.py::update_prelim_and_generalize` -- new kwonly param `coherence_fn`, threaded
   through unchanged (this is the ACTUAL retain gate that determines middle-tier `n_middle`).

Verified before authoring this cell: `hdlab.grounding_acquisition_loop.self_test()` and
`hdlab.prelim_tier.self_test()` both pass UNCHANGED after the edits (MEASURED, run standalone).
Both self-tests were also EXTENDED with a new load-bearing check proving `coherence_fn` is actually
consulted (a sentinel function forces retain/no-retain independent of the real context, both
directions) -- not just silently accepted and ignored.

## Arms

- **W_baseline**: identical wiring to the landed parent cell's own `W_full` (independence-weighted
  count gate: `min_confirm=INDEPENDENCE_MIN_CONFIRM=2.5`, `trace_weight_fn=
  independence_weighted_trace_score`, `schema_min_half_size=1`, all imported verbatim from that
  cell), `coherence_fn=None` (OLD raw-cosine schema metric). Reproduced INSIDE this cell (fresh
  seed namespace) rather than only cited, so this cell can compute an exact per-gap RESOLVED-PK set
  to diff against the new metric -- the authoritative source for "how many of the 21 blocked gaps
  now retain."
- **W_concept**: identical to W_baseline except `coherence_fn=concept_coherence_fn` (this cell's new
  metric). The headline arm.
- **W_scramble**: same wiring as W_concept, eligibility recomputed under scrambled hop2 bridge edges
  (byte-identical scramble mechanism to the parent cell's own `W_scramble`) -- must still collapse
  to near-zero.
- **R_reference**: byte-identical reproduction of the landed `A_full` arm (`run_arm`, imported
  verbatim), UNWEIGHTED default gate, `VISITS_PER_GAP=6` templated repeats, untouched by any of
  this cell's changes -- proves the organ extensions are additive/non-destructive (core-preserved).

## Additional checks (cheap, deterministic, no full pipeline)

- **closed_form_schema_audit**: for every real eligible gap with >=2 real sources, scores its ACTUAL
  wave texts under both the OLD and NEW coherence metric directly (`schema_consistency_split_half`
  called standalone, no `ThreeTierLoop`/`TierState` needed) -- the fastest, most direct per-gap
  answer to "does the fix change the coherence VERDICT for this real gap," and lets this cell report
  `n_regressed` (any gap that WAS coherent under the old metric and is NOT under the new one; must
  be 0 or explained).
- **run_concept_control_checks**: closed-form (word-list-only) POS/NEG/wrong-material probes PLUS
  real-pipeline (actual `update_prelim_and_generalize` on a fresh `TierState`, independence-weighted
  count gate satisfied by construction with exactly 2 independent-tagged sources) POS/NEG probes:
  (POS) a genuine 2-independent-source paraphrase pair must retain WITH the new coherence_fn and
  must NOT retain WITHOUT it (old metric) -- proves the fix is real end-to-end, not just an isolated
  word-matching function; (NEG) a fabricated pair of independent-tagged traces describing two
  GENUINELY DIFFERENT facts (cross-domain) must NOT retain even though the count gate alone is
  satisfied -- the mandatory "a similarity gate that merges everything is broken" can-fail control.

## Pre-registered bands (before running)

- `concept_gate_discriminates` = closed-form POS pair scores >= schema_thresh (0.10) under the NEW
  metric AND < schema_thresh under the OLD metric on the identical pair, AND the cross-domain NEG
  pair AND the wrong-material NEG pair both score < schema_thresh under the NEW metric.
- `control_check_ok` = `concept_gate_discriminates` AND real-pipeline POS retains-with-new/does-not-
  retain-with-old AND real-pipeline NEG does not retain.
- `controls_ok` = `control_check_ok` AND `no_leak_ok` (all arms) AND `reference_reproduces_prior`
  (R_reference n_foundation within abs 15 of cited 40) AND `scramble_collapses` (W_scramble eligible
  population <=1 OR its final n_middle == 0) AND `positive_control_ok` (Gate-D arm3 reproduction
  within 0.10 of cited 0.3802) AND `n_regressed == 0` (the fix must not un-retain anything W_baseline
  already retained).
- `blocked_pks` = (real eligible 2+-source pks) minus (W_baseline's final resolved-pk set) -- the
  measured ~21 gaps.
- `newly_retained_fraction` = |blocked_pks intersect W_concept's final resolved-pk set| / |blocked_pks|.
- `end_to_end_retain_ok` = `newly_retained_fraction >= 0.30` (same 30%-of-blocked-population floor
  convention as the parent cell's own `end_to_end_retain_fraction_floor`).

**Verdict tree:**
- `controls_ok == False` AND the failure is `concept_gate_discriminates == False` (specifically a
  NEG control incorrectly coheres) -> `HARD_FAIL_concept_gate_merges_everything` (the explicit
  over-broad-similarity failure mode this drill must guard against).
- `controls_ok == False` (any other reason: real-pipeline mismatch, no-leak breach, reference
  mismatch, scramble non-collapse, positive-control miss, or a regression) ->
  `HARD_FAIL_controls_broken`.
- `controls_ok AND end_to_end_retain_ok` -> `HARD_PASS_concept_coherence_unblocks_cross_source_
  paraphrase` (the headline win: OWNED graded semantic similarity aligns genuinely-same facts
  worded differently across sources, controls hold, core preserved).
- `controls_ok AND NOT end_to_end_retain_ok` -> `MIDDLE_BAND_concept_coherence_correct_but_
  insufficient_lexicon_coverage` (the mechanism itself correctly discriminates paraphrase from
  distinct-fact -- proven by every control -- but too small a fraction of the real blocked gaps'
  materials are covered by the current 89-concept-plus-ProPara-extension lexicon to move the
  needle past 30%; an honest lexicon-coverage/grounding-wall finding, not a mechanism failure).

## Compute architecture

Class: (b) sequential-CPU with justification. Same regime as the parent cells (CSKG scan ~1.2M
rows, CauseNet scan ~197K rows at FULL only, both single streaming passes). Storage: sharded (each
gap its own item key via `pk_of_genuine`). Wall time budget: smoke ~20-40s, FULL ~90-180s (parent
cell's own FULL measured 50.4s elapsed for 3 arms + 1 closed-form audit + control checks; this cell
adds one more arm (W_baseline) and one more closed-form audit, both lightweight in-memory
operations, plus `concept_similarity` calls which reuse a CACHED feature-vector table -- no new
streaming scan).

## Dispatch

RUN LOCAL, inline, foreground (per Autonomy Declaration: origin stale+irrelevant, no queue_add, no
remote, no push). Smoke first, then self-test gate re-confirmed, then FULL. LOCAL commit, targeted
`git add` (never `git add -A`).

## Schema-vet declarations

- `arms_differ_verified`: W_baseline vs W_concept asserted (digest inequality expected -- the new
  metric should retain strictly more); W_concept vs R_reference asserted; W_concept vs W_scramble
  asserted or exempted-by-construction if scrambled population collapses to the same size class.
- `final_metrics_atomicity`: tmp_replace (single-shot).
- `except SystemExit / KeyboardInterrupt` re-raised before `except Exception` (no BaseException).
- `crlb_n/a`: discrete matched/unmatched word-fraction gate, not a Gaussian noise-floor metric;
  `discriminator_reachability=TRUE` proven both closed-form (real paraphrase pair, real cross-domain
  pair, real wrong-material pair) and via the real-pipeline control checks in self-test, not just
  hand-computed.
- `cardinality_ok`: EXPECTED checkpoints = n_waves (2 smoke / 3 full) for W_baseline/W_concept/
  W_scramble, VISITS_PER_GAP(6 full / 11 smoke) for R_reference.
- `calibration_check`: default_ok_for_this_regime -- `CONCEPT_MATCH_THRESHOLD` is REUSED verbatim
  from `hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD` (an independently pre-registered,
  already-validated constant, not invented or tuned by this cell); `schema_thresh` left at the
  codebase default 0.10, unchanged, not tuned down to force a pass.
- `progress_logging`: print_flush_true (all `print(..., flush=True)`); N/A strictly since declared
  `--timeout` is below the 1800s MANDATORY threshold, included anyway for audit parity.

## Honest disclosure (pre-registered BEFORE running, per task instruction)

If `concept_gate_discriminates` fails (the lexicon's graded similarity cannot cleanly separate
paraphrase from distinct-fact on real data), that is reported as `HARD_FAIL_concept_gate_merges_
everything` or an equivalent honest negative -- NOT papered over by tuning `CONCEPT_MATCH_THRESHOLD`
or `schema_thresh` after the fact. If the mechanism discriminates correctly but too few of the 21
blocked gaps' specific materials happen to be lexicon-covered to clear the 30% floor, that is
`MIDDLE_BAND` and is reported as a lexicon-coverage/grounding-wall finding pointing at source
expansion (more ProPara-style domain vocabulary, or a broader concept feature lexicon) as the next
lever -- not folded into a PASS.

## ADDENDUM (2026-08-11): control fix -- concept-content scramble + mechanism-isolation

Landed as `HARD_FAIL_controls_broken` (commit 7dc5b0588): `scramble_collapses=False` --
`W_scramble` retained 2/5 eligible entries, one (`igneous_rock_cycle||lava||lava_lake`) a genuine
real fact leaking through. Root cause: `W_scramble` only permuted cross-source KG BRIDGE LINKS
(recomputing eligibility), leaving every gap's real wave TEXT -- what `concept_coherence_score`
actually reads -- fully intact, so a gap surviving the link-scramble by chance still carried its
own genuine, unscrambled evidence.

**Fix**: new `scramble_wave_content(waves_by_pk, seed)` corrupts the raw TEXT content per
`(wave_idx, source_tag)` slot via a content-GROUP derangement (cyclic rotation over DISTINCT text
values, not raw pk positions -- pk-position derangement was tried first and leaked 8/21 in the
mechanism-isolation arm below via content-identical siblings, e.g. `kb_role_schema` text depends
only on `(process, material)` so `photosynthesis||sugar||cotton_candy` and
`photosynthesis||sugar||jelly_beans` share byte-identical text; group-level derangement closed
this). Structural wiring (which slots exist, source_tag identity, independence-class tagging) is
completely untouched -- only the text content changes.

**Pre-registered bands for the two new isolations (declared BEFORE the decisive run below):**
- `scramble_collapses` (ISOLATION 1): `W_scramble` final `n_foundation + n_middle == 0` (strict;
  replaces the old `n_eligible<=1 OR n_middle==0` OR-clause, no longer needed once content is also
  corrupted).
- `mechanism_isolation_collapse_ok` (ISOLATION 2, the decisive control): new arm
  `W_mechanism_isolation` -- REAL (unscrambled) eligibility, restricted to exactly the pks in
  `newly_retained_pks` (the real 21/21 recovery), concept content ONLY scrambled. Recovered
  fraction must be `<= MECH_ISO_COLLAPSE_BAND = 0.15`. HYPOTHESIZED, not measured: the domain's
  concept vocabulary is small and recycled across gaps (energy/light/water/rain/rock/moon repeat
  across many unrelated triples), so pure-chance cross-wiring could occasionally reproduce an
  accidental shared-word match; 15% (~3/21) tolerates plausible base-rate noise while still
  requiring a decisive supermajority collapse to pass. Not tuned post-hoc against the measured
  result (see next paragraph for why that would have mattered: the first real measurement came in
  at 38.1%, well above this band, and was NOT waved through).

**Measured (MEASURED@data/exp_three_tier_loop_concept_coherence_v1/metrics.json):**
- First cut of `scramble_wave_content` (pk-position derangement): ISOLATION 1 collapsed cleanly
  (`W_scramble` final 0/0). ISOLATION 2 did NOT collapse -- 8/21 (38.1%) recovered, `verdict =
  HARD_FAIL_mechanism_isolation_recovery_survives_scrambled_concepts`. Diagnosed as the duplicate-
  content-siblings leak described above (all 8 survivors were siblings sharing `(process,
  material)` with a 2-3-way `whole` family: photosynthesis/sugar x3, photosynthesis/oxygen x2,
  photosynthesis/water x2, sedimentation/rock/pluto), not a mechanism artifact.
- After the content-group-derangement fix: `content_scramble_diag.n_entries_changed = 183/183`
  (100%, zero residual duplicate-content escapes, `n_content_groups_total=85`). ISOLATION 1:
  `W_scramble` final 0/0 (collapses). ISOLATION 2 (decisive): `W_mechanism_isolation` recovered
  **0/21 (0.0%)** -- the 21/21 recovery COMPLETELY COLLAPSES when only concept content is
  scrambled and eligibility is left real. `verdict =
  HARD_PASS_concept_coherence_unblocks_cross_source_paraphrase`. All original controls hold
  (`control_check_ok`/`no_leak_ok`/`reference_reproduces_prior`/`positive_control_ok`/
  `n_regressed=0`/`baseline_reproduces_parent` all True); `pytest verification/` = 256 passed / 3
  skipped, unchanged from the commit 7dc5b0588 baseline.
