# Pre-registration: exp_propara_bridging_distilled_kb_endtoend_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator CULMINATION -- the decisive
end-to-end glass-box comprehension test on real prose with a BUILT knowledge foundation (07-14
pivot). Everything else validated (loop uses facts +0.106; generic verb->effect lexicon works;
controls airtight; ConceptNet reuse NO-GO -> BUILD). This cell builds + tests the one missing
component: a distilled process-physics co-participation KB.

## Prior-work check (SUBSTRATE-KB)
Same arc (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct culmination of the
bridging sub-arc; novelty inherited.

## Pipeline (extract structure + distilled process-KB typed facts + retrieve-validate loop)
- STEP 1 (offline, tools/benchmark_trap_check/build_propara_process_physics_kb_v1.py): a DISTILLED
  process-physics co-participation KB. 18 GENERAL type-level science process rules
  (process -> {signature, consumes, produces, moves}) authored from public middle-school science +
  ProPara TRAIN topics, NEVER from TEST gold grids, NO per-paragraph (participant,step,effect)
  tuples. Carries a 10-fact HAND-VET (each independently-verifiable general science).
- STEP 2 (in-cell, no gold): MATCH process type(s) per paragraph by signature-keyword overlap;
  MAP each participant to a role (consumes/produces/moves) by lexical (singular/plural-normalized)
  overlap; SOURCE (effect, trigger_verb_class) facts (consumes->DESTROY, produces->CREATE,
  moves->MOVE).
- STEP 3: re-run the SAME retrieve-validate loop WITH_distilled vs WITHOUT vs WITH_oracle vs
  prior_lesion in one run, unmentioned subset, official metric.

## Decisive measurement
DISTILLED SURVIVAL FRACTION = distilled_lift / oracle_lift (oracle +0.106 reproduced in-run).

## Leak-safety (paramount -- the KB is agent/LLM-distilled)
- HELD-OUT: process types from TRAIN topics; test on held-out TEST paragraphs.
- NO-LEAK (critical): WITH_distilled must stay < LEAK_CEILING=0.95 AND must NOT approach the oracle
  (>= oracle - LEAK_ORACLE_MARGIN=0.02) -> if it does, the KB leaked per-instance answers -> FLAG +
  reject (HARD_FAIL_KB_LEAKED_ANSWERS). Bounded by the ~0.73 cueless cap.
- ABLATION: WITHOUT must still collapse (< 0.60, else void). prior-lesion as before.
- The 10-fact HAND-VET is surfaced in metrics for audit (general science vs ProPara answers).

Residual oracle dependency (flagged): event-COUNT budget only (all arms). Distilled bridge FACTS
are 100% from the general KB + no-gold text mapping.

## HARD-PASS / HARD-FAIL bands (pre-registered BEFORE running)
- `SURVIVAL_HARD_PASS = 0.50`: distilled recovers >= 50% of the oracle lift AND ablation collapses
  AND NO leak AND facts hand-verified general -> **HARD_PASS_END_TO_END_PIPELINE_VALIDATED**
  (extract structure + distilled process-KB typed facts + retrieve-validate loop = the validated
  end-to-end glass-box comprehension pipeline on real prose with a BUILT foundation; a direct
  positive test of the 07-14 foundation thesis).
- `SURVIVAL_HARD_FAIL = 0.25`: survival < 0.25 OR distilled_lift < 0.02 -> **HARD_FAIL_residual**
  (even a built KB does not carry it; report WHY: distillation quality / process-mapping /
  role-mapping / the ~0.73 cueless cap).
- LEAK -> HARD_FAIL_KB_LEAKED_ANSWERS (reject).
- MIDDLE_BAND = partial (0.25-0.50).
- Infra gates: arms_differ, decode >= 0.99 all four arms.

## HP_SCOPE
`{distilled_kb: [survival_material, ablation_collapses, no_leak, facts_general_hand_vet]}`.

## Cell-template mandates
arms_differ (asserted self-test + recorded); final_metrics_atomicity tmp_replace; except SystemExit
before except Exception (grep-verified); crlb_n/a; calibration_check default_ok; deterministic_seeding;
progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: KB built offline; cell loads the small JSON + reuses the diagnostic
precompute (spaCy parse + coref) + distilled mapping + firing + FHRR decode. No batching. MEASURED
self-test ~2s. Expect smoke ~40-70s, full ~50-100s. Run INLINE/LOCALLY foreground.

## Self-test findings (real code path)
**MEASURED@..._metrics.json (self_test):** 18-process KB, 10-fact hand-VET present. On a synth
fossilization paragraph, "plants" (unmentioned at burial/conversion steps) mapped to the
fossilization/hydrocarbon CONSUMES role -> DESTROY fact sourced (no gold); WITH_distilled placed
DESTROY correctly; decode 1.0; 4 verdict-logic unit checks correct (hard_pass HARD_PASS / leak
HARD_FAIL / no_go HARD_FAIL / void HARD_FAIL, incl. the leak-when-distilled~=oracle guard).

## Smoke findings (DEV)
**MEASURED@..._smoke/metrics.json (dev):** distilled survival 0.081 (top-2 process match) /
0.033 (top-1). top-1 was WORSE, confirming the bottleneck is NOT process-mapping breadth. Reverted
to top-2. distilled_pair_recall ~0.24-0.26, precision ~0.07; ablation collapsed, no leak. -> low
survival on DEV; the residual is not the process/role mapping. Bar pinned before TEST.

## Full findings (TEST) -- the end-to-end verdict: NO-GO (survival 0.18); residual = TRIGGER-LOCALIZATION, not missing knowledge
**MEASURED@data/exp_propara_bridging_distilled_kb_endtoend_v1/metrics.json (test, unmentioned
subset n=1119; run_mode=full, cardinality_ok, arms_differ True, decode 1.0 all four arms). Verdict:
HARD_FAIL_DISTILLED_KB_SURVIVAL_LOW_residual.**

UNMENTIONED macro-F1: prior_lesion 0.318, WITHOUT 0.356, **with_distilled 0.376**, with_oracle 0.463.
- **DISTILLED_SURVIVAL = 0.182** (distilled_lift +0.0194 / oracle_lift +0.106). distilled_minus_
  prior_lesion = +0.058 (distilled DOES beat the floor and the ablation, but far short of the 0.50 bar).
- **NO LEAK** (critical, passed): with_distilled 0.376 sits well below oracle 0.463 -> the KB did
  NOT leak per-instance answers (it's general knowledge, bounded below the oracle as required).
- ABLATION collapsed (WITHOUT 0.356 < 0.60). arms differ, decode 1.0.

**HAND-VET of the distilled facts (10 surfaced in metrics):** all independently-verifiable GENERAL
science (combustion consumes fuel+oxygen -> CO2+ash; photosynthesis consumes CO2+water -> glucose+
oxygen; fossilization consumes buried organisms -> fossils/oil; erosion consumes rock -> sediment;
igneous cycle magma->rock; etc.). NONE are ProPara per-instance answers. 52/54 TEST paragraphs
matched a process type; 193 role hits. The KB's science is correct + general -- NOT the bottleneck.

**WHY the survival is low (the deep, honest residual -- confirmed, not speculative):**
- distilled fact pair_recall 0.247 / precision 0.091. The distilled KB correctly identifies
  co-participation EFFECTS (p is consumed/produced/moved) but the (effect, TRIGGER_verb_class) PAIR
  matches oracle only 25% -- because the KB supplies a GENERIC trigger for the effect, which
  mismatches the ACTUAL surface verb-class at p's specific unmentioned step.
- distilled survival 0.18 is COMPARABLE to generic SRL (0.22) and ConceptNet (0.22) -- all three
  real-sourcing approaches hit the SAME ~0.2 ceiling, far below the oracle +0.106's 0.50 bar. Even
  BUILDING the KB did not beat REUSE, because the bottleneck is not knowledge coverage (which the
  built KB improves) but TRIGGER-LOCALIZATION.
- **The reframing (corrects the oracle diagnostic's optimism):** the oracle bridging lift (+0.106)
  came SUBSTANTIALLY from the oracle supplying the ACTUAL surface-trigger verb-class at p's
  unmentioned step -- an instance-specific LOCALIZATION cue, not general world-knowledge. General
  co-participation knowledge (from ANY real source: SRL, ConceptNet, or a hand-built process-physics
  KB) supplies the EFFECT (largely REDUNDANT with the already-granted event-COUNT budget) but NOT
  the instance-specific trigger-localization. So all real sources recover only ~0.2 of the oracle
  lift. **The true residual is TRIGGER-LOCALIZATION** -- determining WHICH unmentioned step a known
  co-participation effect lands on -- which is a READING/EXTRACTION problem (linking p to the
  specific verb at that step), NOT a missing-world-knowledge problem.

**Official (context):** with_distilled 0.673 ~= without 0.671 ~= oracle 0.677, below prior_lesion
0.722 -- lift concentrated in the unmentioned residual, as throughout.

**END-TO-END VERDICT: NO-GO on the built-KB culmination (survival 0.18 < 0.50).** The 07-14
foundation thesis is NOT validated on ProPara's unmentioned-bridging by this route: a correct,
general, leak-safe distilled process-physics KB does NOT carry the bridge -- not because its science
is wrong (it isn't) but because the oracle's bridging value was substantially an instance-specific
TRIGGER-LOCALIZATION cue that no general KB supplies, and the co-participation EFFECT it does supply
is redundant with the granted budget. This is the honest, decisive residual for the whole bridging
sub-arc: the remaining wall on real prose is READING/EXTRACTION (localizing an unmentioned change to
its step by linking the participant to the specific surface verb), which loops back to the
extraction wall the arc has circled -- NOT a missing knowledge foundation. Recommended next
direction: attack trigger-localization directly (co-participation-aware reading that binds an
unmentioned participant to the specific verb at its change step), rather than investing further in
KB sourcing.
