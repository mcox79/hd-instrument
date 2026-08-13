# STATUS

AS OF: 2026-08-12T~23:50Z (testbed compaction-prep) | branch dataprep/mcguffey-graded-corpus |
commit 7a708eff3 (local; origin a37b8abeb, 41 ahead, not pushed)

Rewritten in place every session; never append -- if it doesn't fit in 6KB, it's an evidence-doc
claim with a pointer.

LEDGER: `notes/ledger_grounding_quality_2026-08-12.md` -- refreshed this pass, current through
the readout-fix wiring below.

## WHAT IS TRUE NOW (sourced -- follow the pointer, don't trust this summary)
- **Read-out fix landed-VET (`notes/landed_vet_readout_fix_v1_2026-08-12.md`, 8de3a9a20):
  verdict OVERSTATED -- read the disposition, not the headline.**
  F3 (frozen anchor space) **CONFIRMED, stronger than claimed**: -0.168 at matched retention,
  survives retention pushed above baseline, moves `flip_all` -0.0603 (a selection effect can't
  do that), field-size confound refuted -> WIRE default-OFF.
  F2 (frequency-corrected pool) **REFUTED as a retention artifact** -- -0.004 FIXED / **+0.032
  HURTS** GROWING at matched retention -> SHELVED.
  F1 (z-gate): stability selector only (-0.048 at equal retention), NEVER an informativeness
  gate (AUC 0.5067, refuted). Best config = F1+F3, F2 off, GROWING 0.3602. **No quality claim
  licensed -- flip stability only.**
  -> WIRED default-OFF, additive (192521a7f: `operating_readout()`+`make_pbv_fns
  (freeze_epoch_fn=)`; 8e6c574c5: metrics-key regime mislabel fixed, values always correct;
  7a708eff3: `release_episodes()` closes an O(epochs-seen) F3 memory leak found while sizing
  the run below, before dispatch).
- **Context vector is NOT noise:** real flip 0.7830 [0.7646,0.8003] vs scramble 0.9984,
  D=+0.2155 (79c7521cd, 59479cf82). Defect is downstream in the READ-OUT -- why the arc above
  exists.
- Delegation audit: `notes/director_delegation_audit_2026-08-12.md` (untracked) -- blocking
  dropped only after the 4th protocol edit (~4.5h); verbosity trended worse (median reply
  4.8x longer) even as tool-blocking improved.
- Definitional v5 term-boundary fix: **HARD_PASS**, 64% MEANINGFUL/12% RELATED/24% NOISE on
  2092 facts vs >=52% bar. Rungs 8->38->40->64; v4 "ceiling" was term corruption (16.1%), not
  structural. -> `notes/director_handscore_b3_v5_termboundary_2026-08-12.md` (untracked).
- Context-conditioned sense selection v2: **HARD_FAIL** both indexes -- subject 0.4809 vs floor
  0.4634; head_lemma 0.4449 vs floor 0.4401. -> `notes/context_conditioned_sense_selection_v2_
  2026-08-12.md`, dd58dcf69.
- **PBV: settled HARD_FAIL, not in-progress.** P1 abandon-on-wrong 0.286 (need >=0.60), P3
  separation 0.071 (need >=0.30) -> `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`, a28cf3b45.
- Foundation-validation audit: **OVERSTATED**, plumbing proven, meaning not -- 65.7% of
  "grounded concepts" are self-tautologies `(X,GROUNDED_MEANING,X)`; 2/4 HARD_PASS band
  conditions couldn't fail by construction. -> `notes/landed_vet_foundation_validation_2026-08-
  12.md`; docs fixed in 3340df8d5.
- Corpus: 117,642 sentences (exact re-sum), 5 OpenStax titles, CC BY-NC-SA 4.0, 7c26d429c.
  **NOT ingested; growth still paused.**
- Registry: 123 rows (WIRED 65/TRAPPED_SHARED 28/ISLAND 28/SHELVED 2). Concurrency race on the
  WIRE-or-SHELVE gate fixed, 67ffc6998 (`RegistryLock` in `tools/capability_registry_audit.py`,
  witness `verification/test_capability_registry_concurrency.py`). `pytest verification/` 269/3.

## WHAT IS RUNNING -- TOP OPEN ITEM
**Nothing.** The F1+F3 quality run (`experiments/exp_grounding_quality_readout_v1.py`, prereg
`preregs/2026-08-12_grounding_quality_readout_v1.md`) was **dispatched three times and never
completed** -- confirmed this pass: cell file absent on disk (no git hit, no untracked file),
no `data/exp_grounding_quality_readout_v1/` output dir, no live process. Prereg is filed+sound
(2 arms x 5 segments, PBV_BASE vs PBV_F1F3, HARD_PASS delta>=+0.20 & F1F3>=0.25, NULL
|delta|<0.08 pre-declared acceptable, S1-S8 gates, detached local dispatch, timeout_s 21600).
**Must be authored+dispatched detached before anything else in this arc moves.**

## NEXT (ordered)
1. Author + detach-dispatch `exp_grounding_quality_readout_v1.py`; produces two UNSCORED
   50-row samples (PBV_BASE, PBV_F1F3), blind-shuffled.
2. Director hand-scores both against the same rubric as the 64% v5 baseline. 64% is a CEILING
   REFERENCE ONLY (prereg refuses scoring against it); real comparator is v2 DIST's 8%.
3. Growth stays PAUSED regardless of this cell's outcome until grounding quality holds.
4. Noun-only structural gap (0 verb definitions in 2092 facts, all 5 patterns NP-headed) --
   UNSOLVED, unscheduled.
5. Syntactic bootstrapping note (17eeb72e9) -- concurrent-session-owned, do not touch.

## DO NOT REDO (unmissable -- do not re-propose)
- Intersection-over-argmax: refuted, argmax already propose-then-verify shaped.
- The "40% ceiling": was term corruption, now 64% (v5 term-boundary fix).
- Syntactic bootstrapping as a *next step*: no verbs in extracted data (0/2092), blocked on the
  noun-only extractor gap, not ready to build on.
- F2 (frequency-corrected pool): refuted as a retention artifact, SHELVED; revival needs a
  retention-matched arm >=0.05 residual, none measured.
- Same-sentence cosine / PMI as grounding-quality signals; FHRR superposition to move the
  50-pair audit (invariant to storage rep); "route through PBV" (HARD_FAILed).
- `background:`/`isolation:` agent frontmatter keys -- tested, ignored by the harness.
- Scoring the quality-readout cell against v5's 64% -- refused in its own prereg; comparator 8%.

## BLOCKED / DO NOT TOUCH
- `hdlab/reading_grounding_loop.py`, `hdlab/grounding_acquisition_loop.py`,
  `experiments/exp_pbv_hypothesis_v1.py` -- concurrent session (verify still true before edit).
- Untracked notes owned by other agents, all `notes/*_2026-08-12.md`: `corpus_composition_audit`,
  `director_delegation_audit`, `director_handscore_b3_{def_vs_control,v4_parsefix,v5_termboundary}`,
  `foundation_backup` -- not this role's to commit.
- `data/foundation/reading_grounding_v1`+`v2_qualityfix` (22+23MB), one disk only, not backed up.
