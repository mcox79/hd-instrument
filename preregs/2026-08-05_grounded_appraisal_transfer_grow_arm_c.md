# Pre-registration: grow eval + arm_c (context-sensitive valence extractor) for
# exp_grounded_appraisal_transfer_to_text_v1

Filed 2026-08-05 (exp_dev), per Director's corrected-diagnosis routing
(`notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`, "[CYCLE -- CORRECTED DIAGNOSIS, 08-05]"):
the measured bottleneck is CONTEXTUAL VALENCE EXTRACTION (`resolve_valence_blind` in
`exp_grounded_structure_phase0_probe_v1.py:133`), not grounded reasoning. Grounded reasoning
(arm_a, oracle-fed) already works (CAUSAL 1.000, IRONY 0.667 at the prior n=4/6). This revision
(1) grows the eval for statistical power, (2) adds arm_c = a learned, context-sensitive valence
reader, reusing hdlab/learner (ruleind + estimation plugins, MDL auto-selected) rather than a new
parallel engine.

## Prior-work check (substrate-KB, MANDATORY before authoring)
`bash tools/substrate_query.sh "contextual valence extraction learned reader irony sentiment
context"` -- top hits cosine=0.3828, all generic word/entity nodes ("context"/"Context"/"CONTEXT"
in wordnet + scattered note mentions), not substantive prior cells on this exact question.
`tools/capability_registry_query.py --serves "context"` = 0 matches; `--serves "valence"` = 1
match (`grounded_appraisal_sim_earned`, the REASONING organ this cell already reuses, not an
extraction organ). Verdict: genuinely novel within this arc, not a rediscovery.

## Eval growth (item 1 of the hand-off contract)
Sourced NEW real citations from the same 4 public-domain novels already in
`data/corpora/*/cleaned/*.clean.txt` (never previously used at these line ranges), honestly
labeled, `director_reviewed` field records provenance + self-verification against the corpus file.
No answer-field leakage (true_blocker_agent / true_intent_valence are never read by any arm).
- CAUSAL: 4 -> 7 items (+3: `grapp_mcca_006/007/008`, tom_sawyer ch20 anatomy-book tear + 2x
  anne_of_green_gables false-confession/blame-reversal scenes -- both classic "confessed suspect
  is not the true cause" structures, a different real surface pattern than the trial-scene items
  already in the file).
- IRONY: 6 -> 10 items (+4: 2 new irony/sincere matched pairs from anne_of_green_gables, chosen so
  the narrator's sarcasm-tag word ("said Marilla sarcastically") sits INSIDE the given line_range
  but OUTSIDE the eval file's trimmed `surface_span.text` -- a genuine test of whether wider-context
  extraction recovers a cue a bag-of-words read of the stored span text structurally cannot see).
- BENEFICIARY: held at 5 (per hand-off instruction -- honest capability GAP, not grown, not forced).

## arm_c mechanism: hdlab/learner REUSE (plugin-selection), not a new engine
`fit_arm_c_hypothesis()` in the cell calls `hdlab.learner.registry.learn()` with
`candidate_plugins=["ruleind","estimation"]` over a DETERMINISTIC, exhaustively-enumerated 72-cell
training grid (3 blind-lexicon-vote classes x 3 tone classes x 2 negation x 2 contrast x 2 quote).
Labels come from one pre-declared appraisal rule (sarcasm and negation each invert the blind
lexicon vote; contrast-marker and quote-wrapping are DISTRACTOR features that do NOT determine the
label -- mirroring `exp_parser_ruleinduction_cls_ppattach_v1`'s own XOR-plus-topic-magnet positive
control, so a fitted rule is provably non-trivial, not a lookup table sized to the eval). MDL
auto-selects between the two plugins (`hdlab.learner.core.mdl_select`); no new plugin module was
needed -- this is the exact "reuse across a task the source cells never ran on" use case the
learner module's own docstring describes. At eval time, `context_features()` computes the blind
vote (unchanged `resolve_valence_blind` over the span alone) plus 4 context cues scanned over a
window pulled from the raw corpus text via `get_corpus_context(novel, line_range)` -- the SAME
GIVEN `line_range` field arm_a/arm_b already use for rec-ordering, never an answer field.

## Pre-registered bands (declared in code BEFORE `--full` was run; see
`aggregate_and_verdict()` in the cell, comment block "PRE-REGISTERED ARM-C BANDS")
- `ARM_C_PROVEN`: causal gap-closure `(arm_c-arm_b)/(arm_a-arm_b) >= 0.5` AND irony
  `arm_c > max(surface, chance)`.
- `ARM_C_NULL`: causal gap-closure `< 0.2` AND irony `arm_c <= max(surface, chance)`.
- `ARM_C_PARTIAL`: anything strictly between (mechanism fires on one category, not the other --
  reported honestly per-category, not aggregated into a single misleading number).
- Real baselines present for every category: arm_b (blind lexicon), recency (causal), surface
  (irony), chance=0.5. Difficulty is on (multi-candidate causal attribution + irony-vs-sincere
  minimal pairs, not saturated). One variable changed vs the landed run: the extraction mechanism
  (arm_c added; arm_a/arm_b/theta/bridge code paths byte-for-byte unchanged).

## Contamination self-test extension
`self_test()` now asserts, in addition to the pre-existing theta-reuse-digest check: (1)
`fit_arm_c_hypothesis()` is deterministic across two independent calls (same plugin + hypothesis
digest); (2) arm_a/arm_b/arm_c causal predictions are not all bit-identical (META_RULE_AF); (3)
every causal and irony row's `used_contamination` dict declares
`reads_true_blocker_agent_label`/`reads_true_intent_valence_label` = False for arm_c too; (4)
`resolve_valence_context`'s parameter surface is structurally limited to
`(chosen_name, hypothesis, span_text, context_text)` -- it cannot see any `true_*`/`distractor_*`
field even if a future edit tried to pass one in without changing the signature.

## KNOWN PRE-EXISTING ISSUE surfaced by this revision (not caused by arm_c)
`reconstruct_full_theta(seed, TRAIN_CFG)` no longer reproduces the historical landed digest
(`f52b435fc62d1388` for seed 0) in this environment, even with ZERO code changes -- confirmed by
reconstructing straight from `exp_grounded_appraisal_sim_earned_v1` alone (bypassing this cell
entirely). Same host (`FrameworkMPC`), same torch version (2.8.0+cpu), single git commit for that
file since 2026-08-03 (unmodified), internally deterministic within this environment (3 separate
process launches all agree with each other, just disagree with the historical value). Root cause
not identified (likely BLAS/MKL reduction-order drift across a library/OS update in the ~36h
window); flagged for Director/Testbed as a separate, higher-priority finding -- it silently breaks
the "theta reuse, not retrain" contamination proof for EVERY cell built on top of this earned
theta, not just this one. `HARD_FAIL_THETA_NOT_REUSED_DIGEST_MISMATCH` fired honestly (existing
gate, unmodified) rather than being masked.
