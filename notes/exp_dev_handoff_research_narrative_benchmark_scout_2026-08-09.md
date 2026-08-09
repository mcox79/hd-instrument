# exp_dev hand-off — research: narrative comprehension benchmark scout

**Filed by:** research, 2026-08-09.
**Trigger:** `notes/research_narrative_benchmark_scout_2026-08-09.md` — benchmark-selection drill for
the grounded self-growing narrative comprehension program. Recommends MCScript2.0 as PRIMARY
benchmark, Story Commonsense as SECONDARY, MCTACO as a tertiary held-out cross-domain probe;
ROCStories/Story Cloze and bAbI explicitly flagged AVOID (artifact-poisoned / solved-toy).

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time — if present, this hand-off
still stands but Stage 0 (a download/availability check, not an experiment ship) can proceed
regardless of pause state; Stages 1-3 (harness runs) should respect the pause gate.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names the benchmark ANCHOR +
POINTERS + staged test structure only. exp_dev designs ALL of: exact harness code, exact
architecture-hookup points, seed counts, exact threshold numerics beyond what's pre-registered in
the research note, queue choice, smoke profile, FULL profile.

---

## Why now

This is the gating "WHERE" decision for the grounded narrative comprehension program: which public
benchmark demonstrates the compounding-grounding property (comprehension improves with exposure,
generalizes to held-out, false-consolidation guard holds) on REAL narrative text, not toy material.
The acquisition-loop engine (`hdlab/grounding_acquisition_loop.py`) and the script-bridge grounding
mechanism are both proven at toy scale; this benchmark is the natural next rung.

## Anchor candidates (rank-ordered)

### 1. MCScript2.0 Stage 0 — availability/download confirmation (BLOCKING, do first)

- **Anchor pointer:** `notes/research_narrative_benchmark_scout_2026-08-09.md`, "Cheap decisive
  test" Stage 0.
- **Substrate-product reading:** before any harness or acquisition-loop work is scheduled, confirm
  a live, gold-labeled MCScript2.0 train/dev/test package (Ostermann, Roth & Pinkal, *SEM 2019,
  ACL Anthology S19-1012 / arXiv:1905.09531) is actually obtainable. The research lit-scan could
  NOT confirm current download availability — it's not on Hugging Face `datasets` as a standalone
  entry, not listed on the one active third-party mirror found (which only serves MCScript v1), and
  only appears indirectly repackaged inside the "Natural Instructions" collection
  (`task165_mcscript_question_answering_commonsense`, `task164_mcscript_question_answering_text` —
  version unconfirmed). Check the official SFB1102 (Saarland University) project page first
  (sfb1102.uni-saarland.de), then the Natural Instructions repackaging as a fallback source (if
  version-confirmed as 2.0, not v1), then contact-the-authors as a last resort.
  If a working MCScript2.0 package cannot be obtained within a bounded effort (exp_dev's call on
  how bounded): fall back to MCScript v1 (Ostermann et al., LREC 2018, S18-1119/arXiv:1803.05223,
  confirmed live via a third-party mirror linked from Ashutosh Modi's personal datasets page)
  filtered to ONLY its commonsense/script-labeled subset (~3,914 of 13,939 questions, per the
  paper's own validated item-type labels) — weaker (marginal script-relevance per the v1 authors'
  own later admission) but usable as a degraded Plan B.
- **Tier:** local/analyzer-only — no compute, just a download + format check.
- **Why now:** this is THE blocking gate; nothing else in this hand-off should be scheduled ahead
  of it.

### 2. MCScript2.0 Stage 1 — zero-exposure harness calibration

- **Anchor pointer:** research note, "Cheap decisive test" Stage 1; exact baseline table
  reproduced there (Logistic Regression 61% overall/56% script/67% text; Attentive Reader 65%/63%/
  68%; TriAN+ConceptNet 72%/67%/78%; Human 97%; majority 50%).
- **Substrate-product reading:** run the EXISTING (pre-acquisition-loop, zero grown grounding)
  narrative-comprehension architecture on the MCScript2.0 test set as-is. HARD-PASS band: 50-65%
  overall (comparable to the published LR/Attentive-Reader band, confirms harness fidelity).
  HARD-FAIL band: <45% (parsing/harness bug) or >72% with zero exposure (test-leakage or the
  "zero-exposure" condition isn't actually zero — investigate before proceeding).
- **Tier:** likely CPU (single architecture pass, no training).
- **Why now:** cheapest possible sanity gate before trusting any acquisition-loop delta; mirrors the
  DesireDB Stage-1 calibration pattern from the 2026-08-08 sibling drill.

### 3. MCScript2.0 Stage 2 — the real compounding-grounding test

- **Anchor pointer:** research note, "Acquisition-loop mapping" + "Cheap decisive test" Stage 2 +
  "Falsifiable predictions" Stage 2.
- **Substrate-product reading:** wire `hdlab/grounding_acquisition_loop.py` (Library, Trace,
  consolidation_pass, schema_consistency_split_half, surprise_order — the flag-not-understood ->
  library -> consolidate -> bank -> grow loop with the escalate-don't-commit guard) over the
  2,500-text / 14,191-question MCScript2.0 TRAIN split as the exposure corpus. Report held-out TEST
  accuracy (3,610q / 632 texts, disjoint by TEXT) broken out by the dataset's OWN pre-existing
  script-based / text-based / text-or-script item-type label — this label is the free,
  dataset-native ablation the research note identifies as the key mechanism-isolating discriminator
  (same pattern class as DesireDB's But-Present ablation). Run at multiple exposure checkpoints
  (e.g. 0%/25%/50%/100% of TRAIN texts processed) to get a compounding CURVE, not just an endpoint.
  HARD-PASS: script-based-subset TEST accuracy improves >=5pp vs. Stage-1 baseline AND improves
  measurably more than the text-based subset. HARD-FAIL: no script-vs-text differential, or no
  movement beyond +/-2pp noise as exposure grows — per the "flat learning result = broken
  experiment, not a ceiling" discipline, this triggers a DIAGNOSE response (not-learning /
  no-genuinely-new-content / underpowered exposure), not a conclusion of intrinsic ceiling.
- **Tier:** likely GPU or remote CPU depending on acquisition-loop cost at this corpus scale
  (2,500 texts is larger than prior toy-scale runs) — exp_dev's call.
- **Why now:** this IS the program's central compounding-property demonstration; everything upstream
  (toy-scale proofs, the acquisition loop engine) has been building toward exactly this test on real
  text.

### 4. MCScript2.0 Stage 3 — pairscramble false-consolidation guard

- **Anchor pointer:** research note, "Cheap decisive test" Stage 3 + "Falsifiable predictions"
  Stage 3.
- **Substrate-product reading:** re-run Stage 2 with exposure-text internal event order
  pair-scrambled (reuses the pairscramble-must-collapse discipline already established elsewhere in
  this program — no new methodology to invent). HARD-PASS: scrambled-exposure gain is substantially
  smaller than ordered-exposure gain (near zero) on the script-based subset. HARD-FAIL: scrambled
  exposure produces the SAME gain — signals the acquisition loop is banking something real but not
  script-structural; per the loop's own escalate-don't-commit guard, this should block promotion of
  whatever got banked during Stage 2.
- **Tier:** same as Stage 2 (reruns the same pipeline with one input permuted).
- **Why now:** sequenced last because it's a control condition on Stage 2's result, not a
  standalone experiment — only meaningful once Stage 2 has produced a positive result to guard.

### Stretch candidate (if bandwidth allows after the 4 above)

5. **Story Commonsense (Rashkin et al. 2018, ACL P18-1213) harness stand-up** — SECONDARY benchmark,
   dense multi-label glass-box output (5 Maslow + 19 Reiss + 8 Plutchik categories per
   character-line), clean 10k/2.5k/2.5k story-level split, shares ROCStories-family exposure-corpus
   infrastructure. Baseline to beat: Rashkin's own TF-IDF (Maslow F1 24.88/Reiss F1 19.46/Plutchik
   F1 21.90) at the floor, best published (Maslow ~35/Reiss ~24.5/Plutchik ~30) as the target, with
   Paul & Frank 2019's knowledge-injected follow-up (Reiss F1 32.96-39.44, Maslow F1 56.69-61.72) as
   a stretch target proving the residual is genuinely knowledge-shaped. Report broken out by
   category (per the research note's Honest-risks #5, the easy categories are lexically anchored —
   the diagnostic value is in the harder Reiss/rare cells).

---

## Context pointers (pointers, not summaries)

- `notes/research_narrative_benchmark_scout_2026-08-09.md` — the full drill this hand-off is based
  on; read it end-to-end before designing Stage 0-3 harness code, especially the "Honest risks"
  section (MCScript2.0 has NO external artifact audit — run your own answer-only/passage-only
  baseline, Kaushik & Lipton EMNLP 2018 methodology, on the script-based subset before trusting any
  exposure-driven gain as genuine, since MCScript v1's own "script-based" label was later shown to
  be largely spurious by the same author group).
- `hdlab/grounding_acquisition_loop.py` — the acquisition loop engine to wire (Library, Trace,
  consolidation_pass, schema_consistency_split_half, surprise_order, self_test).
- `notes/research_desiredb_hard_residual_prior_art_2026-08-08.md` — sibling drill; DesireDB/
  Chaturvedi-lineage benchmarks are noise-capped/lexically-driven, confirmed weaker fit than
  MCScript2.0/Story Commonsense for THIS specific grounded-script-knowledge claim (though DesireDB
  remains relevant to the separate `goal_achievement.py` thread).
- `notes/prior_art_modern_neurosymbolic_narrative_2026-08-06.md` — broader landscape scan; confirms
  no existing system unifies glass-box + goal-tracking + outcome-verification, i.e. no off-the-shelf
  system to adopt instead of building/testing this program's own mechanism.

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands stated above
  are the research-level pre-registration; exp_dev refines into exact numeric thresholds/smoke
  profile before shipping Stage 1+.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance for Stages 2-3 (acquisition-loop runs are stochastic —
  surprise_order/consolidation_pass have randomness).
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via the queue_add.sh exit code.
- status_log entry per stage with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact harness/hookup code, exact numeric threshold refinement beyond the
research note's HARD-PASS/HARD-FAIL bands, seed count, queue choice (Tier A/B/C), ETA, smoke
profile, FULL profile, and whether/when to invoke the MCScript v1 fallback if Stage 0 fails. If
exp_dev's own Stage-0 check finds a materially different availability picture than this hand-off
describes (e.g., MCScript2.0 turns out to be trivially available, or turns out entirely unobtainable
even via the Natural Instructions repackaging), that's exp_dev's call to adjust sequencing —
including promoting Story Commonsense to de-facto primary if MCScript2.0 is a dead end.
