# exp_dev hand-off — research: self-improving reader multi-round learning curve

**Filed-by:** research (Opus synthesis over 2 parallel Sonnet lit-scan sub-agents), 2026-07-21.
**Trigger:** `notes/research_self_improving_reader_learning_curve_drill_2026-07-21.md` — read that note in full
before designing any cell; it contains the brain + ML mechanism citations, the dedup verdict vs atoms 29386/89,
and the exact HARD-PASS/HARD-FAIL bands and 5-arm design below.
**Pause state:** respect `data/orchestrator_paused.flag` if present — do not ship without checking.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off gives anchor pointers and why-now context, NOT
a prescribed line-by-line implementation. exp_dev owns cell design, pre-reg, smoke gate, and dispatch — though
note the research note's falsifiable-predictions section already contains pre-registerable HARD-PASS/HARD-FAIL
numbers exp_dev may use directly (loosen only with a stated reason).

## Anchor candidates (rank-ordered)

1. **Multi-round GATED-vs-UNGATED-vs-RANDOM-vs-INVERTED-vs-PASSIVE self-correction curve, built as an outer
   round-loop wrapper around the EXISTING `experiments/exp_active_learning_loop_gap_detect_lookup_revise_v2.py`
   machinery.** This is a REVIVAL/EXTENSION of atoms 29386/29389, not a new architecture: reuse the calibration
   pool, gap-detect gate, coherence check, and provenance-revise unchanged; the two new pieces are (a) an outer
   loop over 5 rounds re-evaluating the same held-out eval set after each round's revisions, and (b) replacing
   the binary `accept = coherent and rel_score >= RELIABILITY_THRESHOLD` cutoff with a continuous per-item rate
   (`rate = reliability_score` when coherent, else 0) that scales how strongly that round's revision is written.
   Tier hint: LOW-MEDIUM effort (additive wrapper + one-line binary-to-continuous substitution, no new corpus,
   no new gate math). Why now: this is the first test of the reader's Step-3 "flexible/improving" north star
   that was previously only proven as single-step wiring (29386/89) or single-pass consolidation weighting
   (`research_brain_confidence_weighted_learning_consolidation_2026-07-20.md`) — never as an actual
   accuracy-vs-round-number trajectory.
2. **Mandatory precondition: extraction-vs-decision error partition, run BEFORE any round-loop compute.**
   Partition the round-0 logged-error/abstain batch (from the metacognition/abstain signal, atom 29367) into
   EXTRACTION-class (wrong span/argument identified) vs DECISION-class (right info, wrong role assignment)
   using the already-existing parser arc-margin (AUC 0.807) and completeness signal. This is a zero-new-compute
   re-bucketing of already-existing signals and should run FIRST as a free precondition check — if fewer than
   ~15-20% of round-0 errors are resolvable via internal-retrieve/external-lookup at all (see research note's
   HARD-FAIL precondition-gate), that is a kill-before-full-run signal, not a build blocker to work around.
3. **The two adversarial/null arms (RANDOM-CONFIDENCE shuffled-rate, INVERTED-CONFIDENCE) are the load-bearing
   must-fail controls** — do not treat them as optional extras. The research note's core NEW claim beyond
   29386/89's existing single-step "ungated hurts" result is that the GATED-vs-UNGATED gap must WIDEN with
   round count (a compounding, not one-time, signature) — this requires all 5 arms run to the same round depth
   with logged per-round accuracy, not just an endpoint comparison.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_self_improving_reader_learning_curve_drill_2026-07-21.md` (this drill's full note — mechanism
  citations, dedup table vs 29386/89, cheap decisive test, HARD-PASS/HARD-FAIL bands, cross-thread synthesis)
- `experiments/exp_active_learning_loop_gap_detect_lookup_revise_v2.py` (the machinery being wrapped/extended;
  note `band10_learning_curve` at line ~1056/1155 is the OLD two-point occ1-vs-occ2 metric, not the new curve —
  do not confuse the two)
- `experiments/exp_active_learning_loop_gap_detect_lookup_revise_v1.py` (v1, superseded by v2's three fixes;
  read only for the original construction-crutch history if needed)
- `notes/research_brain_confidence_weighted_learning_consolidation_2026-07-20.md` (sibling single-pass
  continuous-rate design + its must-fail controls: shuffled/inverted/oracle-ceiling — this cell's RANDOM/
  INVERTED arms are the direct multi-round extension of that note's controls)
- `notes/research_brain_active_learning_curiosity_lookup_revision_2026-07-20.md` (the gap-detect/retrieve/
  lookup mechanism being reused per-round, with its own HARD-PASS/HARD-FAIL bands for the single-pass version)
- `experiments/exp_metacog_abstain_conformal_transfer_v1.py` and
  `experiments/exp_metacog_abstain_readout_signal_thresholding_v1.py` (atom 29367 lineage — source of the
  per-round error/abstain batch and the reliability score used for the continuous rate)

## Contract

- exp_dev authors + smokes locally, returns the exact `queue_add.sh` dispatch command; orchestrator ships +
  REMOTE VERIFIES post-ship, per locked ship policy.
- Pre-register per envelope-fail-bands; the HARD-PASS/HARD-FAIL numbers in the research note's "Falsifiable
  predictions" section are usable verbatim as pre-reg thresholds.
- Run the extraction-vs-decision precondition re-bucketing (anchor 2) BEFORE authoring the full 5-arm round
  loop — it is a free, zero-new-compute kill/scope signal per the design-gate discipline.
- ONE variable differs across the 5 arms: the per-round rate function (GATED continuous / UNGATED=1.0 /
  RANDOM shuffled / INVERTED=1-rate / PASSIVE=no-revision). Corpus, seeds, eval set, and loop wiring held fixed.

## Autonomy declaration

exp_dev owns: exact cell architecture for the round-loop wrapper, smoke design (recommend 2-round smoke before
committing to full 5-round/7-seed), whether to report the extraction-vs-decision partition as two separate
curves or a single stratified metric, and whether the free precondition re-bucketing (anchor 2) shows enough
resolvable error mass to warrant the full build at all (a low-resolvable-fraction result is itself a valid,
reportable kill decision through the normal verdict path, not a failure to fix).
