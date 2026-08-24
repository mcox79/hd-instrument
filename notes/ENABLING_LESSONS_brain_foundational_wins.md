# ENABLING LESSONS FROM BRAIN-FOUNDATIONAL WINS -- the meta-lessons, grounded in real cases

**A standing focus, opened by owner 2026-08-24:** *"extract the most important enabling lessons from
brain-foundational successful implementations -- the key realizations that made it possible, and the
lazy things we did without thinking that sent us down wrong directions."*

This doc is the consolidated home for that focus. Every lesson is tied to an actual win/refutation on
disk (a `notes/problems/<slug>/SOLVED.md`), judged against the project's own bar (CI-separated over the
strongest floor actually run, on the item's own population; the info-free twin must lose; no number
crosses scorers or populations). **It does not restate lessons already captured in `CLAUDE.md` /
`STATUS_LESSONS.md` -- those are pointer-only below.** The value here is (a) the seven not recorded
anywhere durable, and (b) the honest capability-vs-construction labels.

---

## (A) THE REALIZATIONS THAT ENABLED THE WINS -- most load-bearing first

1. **Recompute the floor in the SAME harness, population, and representation as your arm; never paste a number across.** (`the_gate_cannot_measure_its_own_floor` proved harness identity to 1e-9 before accepting a floor; `flat_store` used the *strongest* floor 0.3242, not the one it beat.) *[captured: MEMORY bar, CLAUDE 1110]*
2. **Build the STRONGEST honest version before declaring a route dead, and add a could-it-succeed ceiling.** (`does_learning_from_reading...`: PPMI arm clears spelling floor 15-40x where 16 prior `+=` losses had not; `store_survives_a_partial_cue` built an ORACLE_UNION that clears, proving no info cap.) *[captured: MEMORY "fair test of a WEAK impl"]*
3. **Cross-modal AGREEMENT is the label-free learning signal -- let one channel TEACH another, don't concatenate or weight.** (`where_does_a_meaning_signal_come_from_without_labels`: grounded hub teaches text direction, AUC 0.865 vs twin p95 0.716, no gold.) *[partially captured]*
4. **Hold everything downstream byte-identical, swap ONE variable, copy the OPERATION not the PARAMETER.** (`the_live_meaning_organ...`: swap only store representation -> explicit separable store 0.865, d=256 dense bundle fails its own twin. "Worst arm copied a number; best copied an operation.") *[abstract lesson captured; this concrete one is NEW -- see below #7]*
5. **Score against a gold cleaned of the shortcut the mechanism can exploit.** (`the_bundle...`/`the_gate...`: ~78% of the spelling floor was morphological leakage; strip stems 0.0867->0.0193 and the read-out flips from losing to winning.) *[NEW -- see below #1]*
6. **Separate exact-key (recite) from partial-cue (recognise); lead with the collapse.** (`flat_store`: 0.9954 exact-key -> 0.1399 held-out.) *[captured: STATUS_LESSONS, MEMORY partial-cue cap]*
7. **Combine, don't substitute -- a hub beats either channel alone; watch the dominant-prior-swamps-the-weaker-correct-channel failure.** (`the_bundle...` FUSE_BASE_GROUNDED best on fair gold; `reader_meaning_channel`: fixed-weight mix, channel alone 0.4811 > chance, channel+prior 0.1415 < chance.) *[NEW as a positive rule -- see below #3]*
8. **A control written as code and PROVEN to fire beats a caution in prose.** (`the_gate...` guard shown firing on the wrong constant; `certification_gate_hangs` a sleep(100000) fixture proves the timeout verdict fires.) *[captured: STATUS_LESSONS 1094-1117]*
9. **Ask whether the experiment COULD have succeeded before asking why it didn't; verify with a positive control, not an absence check.** *[captured: STATUS_LESSONS x3, MEMORY]*
10. **A wall is a fidelity divergence, not a ceiling -- name the missing FUNCTION.** *[captured: MEMORY anchors]*

## (B) THE LAZY DEFAULTS THAT SENT WORK WRONG -- most load-bearing first

1. **Pasting a floor/number from a different harness/scorer/population because it "looks like the same task."** (the entire point of `the_gate_cannot_measure_its_own_floor`.)
2. **Mistaking an isolation / exact-key / construction-proof win for a capability.** (`flat_store` ranked priority-1 on a 0.9954 number that collapses to 0.1399.)
3. **Generalizing a fair test of a WEAK implementation into "the idea is dead."** (`does_learning_from_reading...`.)
4. **Trusting a benchmark whose gold or candidate pool is shaped by the shortcut under test.** (WordNet spelling leakage; co-occurrence-drawn candidate pool; a bank whose majority class IS the answer the organ can't give.)
5. **Reaching for the convenient mechanism the brief NAMED instead of the one the brain uses.** (`wire_the_refuse_gate` said "threshold confidence" -- the working signal was cue FAMILIARITY; `reader_meaning_channel` said "supply a modality" -- the miss was architecture; `store_survives_a_partial_cue` said "better store format" -- the miss was a control network. The named recipe would have shipped the wrong fix THREE times.)
6. **Quoting a headline measured on a filtered/easy subset without asking what a dumb baseline scores on the SAME items.** (`the_grow_by_reading...`: 0.90 on the kept third; a 2-line rule scores 0.83 there.)
7. **"I re-ran it and it matched" as verification** -- when the re-run REPLAYS a cached answer (0 units, 0.004s) and silently re-dates the metrics. (`harness_cannot_recompute`.) *[captured: reproduction_check]*
8. **Collapsing "abstained / I can't tell" into "wrong."** (`score_counts_abstention_as_error`.)
9. **Copying a brain PARAMETER tuned to a constraint we don't share instead of the brain COMPUTATION.** (d=256 -- `the_live_meaning_organ...`.) *[captured: MEMORY anchor]*
10. **Reading "flat CPU + no output" as frozen; quoting counts from stale notes.** (`certification_gate_hangs`: slow disk, not a deadlock.)

---

## THE EIGHT NOT RECORDED ANYWHERE DURABLE -- highest value, ranked (recorded HERE)

1. **Morphological leakage in WordNet-style gold: score against a stem-stripped gold, or the "we lose to a spell-checker" verdict is an artifact.** Live as board Q117; already flipped a steering conclusion (0.0867->0.0193; read-out went losing->winning). Cites: `the_bundle...`, `the_gate...`.
2. **Oracle-clears-but-no-unsupervised-arm-reaches-it => the miss is a per-item CONTROL / reliability-weighting network, not missing information.** THREE briefs converge on this (`store_survives_a_partial_cue`, `reader_meaning_channel`, `teach_the_self_built...`) -- the single most-pointed-at build target. Build the ORACLE_UNION as routine when a mechanism floors.
3. **"Combine, don't substitute" as a positive rule + its failure mode** (hub-and-spoke fusion beats either channel alone; a fixed-weight mix lets a dominant prior swamp the weaker-but-correct channel).
4. **Cue FAMILIARITY vs ACCESSIBILITY -- "how it knows it doesn't know" is a membership check on the CUE, not a confidence threshold on the ANSWER.** Cite: `wire_the_refuse_gate...`.
5. **Task-type transfer discipline: a mechanism that wins a SIMILARITY task can actively HURT a PREDICTION/retrieval task** (more teaching = monotonically worse). Cite: `teach_the_self_built...`.
6. **A scorer/floor fix must be direction-neutral or make results HARDER to publish -- a fix that lifts the headline is a laundered failure.** Cites: `score_counts_abstention...` (headline byte-identical), `the_gate...` (made results harder to publish).
7. **The store REPRESENTATION is the lever -- keep memories separable, don't superpose into a fixed small vector** (the cleanest proven instance of "copy the operation, not the parameter d=256"). Cite: `the_live_meaning_organ...`.
8. **A distilled direction can be INDUCTIVE while its one orientation BIT is irreducibly TRANSDUCTIVE to the candidate population.** A taught similarity read-out is label-free but BATCH-dependent: orient the sign over the presented pairs against the teacher (a single pair inverts, scoring the sign-flipped image, 0.16 vs 0.84). No label-free proxy batch recovers the sign; only the presented candidates do. Found while landing the meaning organ as a live capability. Cite: `the_live_meaning_organ...` integration; `hdlab/distributional_meaning_channel.py`.

---

## HONEST CAPABILITY-VS-CONSTRUCTION LABELS (against the bar)

- **Genuine capability:** `where_does_a_meaning_signal...` (label-free; margin over twin MAX is thin, over p95 comfortable; transductive + supplied teacher); `the_live_meaning_organ...` (one-variable, but measured in a live-*faithful* harness, not the literal live organ); `does_learning_from_reading...` (on word-sim benchmarks; does NOT transfer to substitutability); `the_bundle...` grounded-fusion sub-win (fair gold).
- **Hygiene / instrument / construction:** `the_gate`, `wire_the_refuse_gate` (0.999 is true-by-construction), `harness_cannot_recompute`, `certification_gate_hangs`, `score_counts_abstention`, `eval_bank_too_small`, `the_grow_by_reading` (the fancy machinery's +0.07 over a 2-line rule is NOT separated).
- **Valuable refutations:** `flat_store`, `store_survives_a_partial_cue`, `teach_the_self_built`, `aimed_reading`, `reader_meaning_channel`.

---

## HOW FUTURE SUBMISSIONS FEED THIS FOCUS

Per owner 2026-08-24, `notes/problems/README.md` now (a) urges every brief toward the RIGHT
brain-foundational solution up front, and (b) asks every `SOLVED.md` for a `## KEY REALIZATIONS`
section. The strategy session harvests those sections into this file at integration -- so future wins
self-document their enabling insight instead of being mined back out.
