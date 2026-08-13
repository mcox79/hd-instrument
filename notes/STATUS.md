# STATUS

AS OF: 2026-08-12T~23:59Z (refresh #2) | branch dataprep/mcguffey-graded-corpus | commit
46c32d960 (local; origin a37b8abeb, 43 ahead, not pushed)

Rewritten in place every session; never append -- if it doesn't fit in 6KB, it's an evidence-doc
claim with a pointer. LEDGER: `notes/ledger_grounding_quality_2026-08-12.md`, refreshed this pass.

## WHAT IS TRUE NOW (sourced -- follow the pointer, don't trust this summary)
- **Infra (agent frontmatter/env):** superseded here -- carried verbatim in CLAUDE.md
  "Agent-teams / frontmatter findings (2026-08-12 night)"; key rule kept in DO NOT REDO below.
- **Read-out fix landed-VET** (`notes/landed_vet_readout_fix_v1_2026-08-12.md`, 8de3a9a20):
  OVERSTATED headline. F3 (frozen anchor space) CONFIRMED stronger than claimed (-0.168 at
  matched retention, moves `flip_all` -0.0603) -> WIRE default-OFF. F2 (freq-corrected pool)
  REFUTED as retention artifact (+0.032 HURTS GROWING) -> SHELVED. F1 (z-gate): stability
  selector only, never informativeness (AUC 0.5067). Best config F1+F3, GROWING 0.3602,
  **no quality claim licensed, flip stability only**. WIRED default-OFF additive
  (192521a7f/8e6c574c5/7a708eff3, latter closes an F3 memory leak).
- **Context vector is NOT noise:** flip 0.7830 vs scramble 0.9984, D=+0.2155 (79c7521cd,
  59479cf82). Defect is downstream in the READ-OUT -- why the arc above exists.
- Definitional v5 term-boundary fix: **HARD_PASS**, 64% MEANINGFUL/12% RELATED/24% NOISE on
  2092 facts vs >=52% bar (8->38->40->64; v4 "ceiling" was term corruption not structural) ->
  `notes/director_handscore_b3_v5_termboundary_2026-08-12.md` (untracked).
- Context-conditioned sense selection v2: **HARD_FAIL** both indexes (0.4809 vs floor 0.4634;
  0.4449 vs floor 0.4401) -> dd58dcf69.
- **PBV: settled HARD_FAIL.** P1 0.286 (need >=0.60), P3 0.071 (need >=0.30) ->
  `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`, a28cf3b45.
- Foundation-validation: **OVERSTATED**, plumbing proven/meaning not -- 65.7% self-tautologies
  `(X,GROUNDED_MEANING,X)` -> `notes/landed_vet_foundation_validation_2026-08-12.md`, 3340df8d5.
- Corpus: 117,642 sentences, 5 OpenStax titles, CC BY-NC-SA 4.0, 7c26d429c. **NOT ingested;
  growth still paused.**
- Registry: 123 rows (WIRED 65/SHARED 28/ISLAND 28/SHELVED 2), concurrency race fixed
  67ffc6998. `pytest verification/` 269/3.

## WHAT IS RUNNING -- TOP OPEN ITEM
`exp_grounding_quality_readout_v1` RAN AND IS SCORED (08-13). Cell verdict
STRUCTURAL_PASS_PENDING_B3, S1-S7 all ok (S5 calibrated: BASE confirm 0.0668 vs cited 0.1006),
S8 drift -0.2383 (retention-match VOID), fact ratio 0.9609 (no sec-3.2 cap). Quality read-out =
NULL, floor-limited -- see NEXT 1 and
`notes/director_handscore_readout_v1_2026-08-13.md`.

## NEXT (ordered)
1. DONE 08-13: hand-scored 100 blind rows -> 3% M / 19% R / 78% N; delta F1F3-BASE +0.02 = NULL,
   floor-limited (3 M exist, max |delta| 0.06); S8 drift -0.238 voids retention-match. Its segment
   effect (bio 52.9% vs news 16.1%) was later REFUTED -- see DO NOT REDO.
   `notes/director_handscore_readout_v1_2026-08-13.md`. Next binding question = PROPOSER'S METRIC.
2. Growth stays PAUSED regardless of this cell's outcome until grounding quality holds.
3. Noun-only structural gap (0 verb defs in 2092 facts, all 5 patterns NP-headed) -- unscheduled.
4. Syntactic bootstrapping note (17eeb72e9) -- concurrent-session-owned, do not touch.

## DO NOT REDO (unmissable -- do not re-propose)
- Intersection-over-argmax: refuted, argmax already propose-then-verify shaped.
- The "40% ceiling": was term corruption, now 64% (v5 term-boundary fix).
- Syntactic bootstrapping as a *next step*: no verbs in extracted data (0/2092), blocked on the
  noun-only extractor gap, not ready to build on.
- F2 (frequency-corrected pool): refuted as a retention artifact, SHELVED; revival needs a
  retention-matched arm >=0.05 residual, none measured.
- Same-sentence cosine / PMI as grounding-quality signals; FHRR superposition to move the
  50-pair audit (invariant to storage rep); "route through PBV" (HARD_FAILed).
- `isolation:` agent frontmatter key -- tested, ignored. `background:` -- WORSE than ignored,
  fails the whole definition to load (see infra bullet above); still never add either.
- Scoring the quality-readout cell against v5's 64% -- refused in its own prereg; comparator 8%.
- Sensorimotor norms as a filter on the meaning read-out: SHELVED -- a filter cannot create meaning;
  coverage was never the blocker. Revival: `notes/sensorimotor_anchoring_scope_2026-08-13.md`.
- Read-out stabilization (F1+F3) as a route to better meanings -- NULL, floor-limited; grounding
  quality is the binding constraint, not read-out stability
  (`notes/director_handscore_readout_v1_2026-08-13.md`).
- **Corpus swap news->textbook as a route to grounded-meaning quality: REFUTED.** Prereg matched-N
  blind (20,394 sent/arm, 50 rows/arm): TEXTBOOK 0% M / 30% R vs NEWS 4% / 20% -> band
  MECHANISM_IS_BINDING. Prior post-hoc n=17 claim (bio 52.9% M+R vs news 16.1%, p=0.0024) did NOT
  replicate: 30.0% vs 24.0%, p=0.6529, OR 1.36. Better text buys adjacency, not meaning.
  `notes/director_handscore_text_vs_mechanism_2026-08-13.md`.

## BLOCKED / DO NOT TOUCH
- **DISCIPLINE -- SERIALIZE MEASUREMENT vs CODE CHANGE (08-13, happened 2x):** never dispatch an
  audit/witness-run/experiment while another agent may write code it depends on (incl. TRANSITIVE
  deps); a measurement racing a concurrent edit describes NO single repo state.
  `notes/measurement_layer_drift_2026-08-13.md` sec.8.
- `hdlab/reading_grounding_loop.py`, `hdlab/grounding_acquisition_loop.py`,
  `experiments/exp_pbv_hypothesis_v1.py` -- concurrent session (verify before edit).
- Untracked notes owned by others, `notes/*_2026-08-12.md`: `corpus_composition_audit`,
  `director_delegation_audit`, `director_handscore_b3_{def_vs_control,v4_parsefix,v5_termboundary}`,
  `foundation_backup` -- not this role's to commit.
- `data/foundation/reading_grounding_v1`+`v2_qualityfix` (22+23MB), one disk only, no backup.
