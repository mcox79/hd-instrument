# Pre-registration: exp_propara_bridging_real_kb_sourcing_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator go/no-go follow-up to the oracle
bridging diagnostic (exp_propara_bridging_knowledge_vs_mechanism_v1, HARD_PASS: WITH 0.463 /
WITHOUT 0.356 on the unmentioned subset, +0.106 load-bearing, no leak). Decides the bridging-KB
foundation investment.

## Prior-work check (SUBSTRATE-KB)
Same arc (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct go/no-go follow-up on
the diagnostic's own landed result; novelty inherited.

## The question
How much of the +0.106 oracle-knowledge lift SURVIVES when the bridge facts are sourced from a
REAL non-oracle KB instead of gold? That survival fraction is the go/no-go on building a real
bridging KB foundation.

## One clean variable
oracle bridge facts -> REAL-KB-sourced bridge facts. The loop + ALL controls (WITHOUT ablation,
prior-lesion, no-leak ceiling, unmentioned subset, official metric, oracle event-COUNT budget
granted to all arms) are IMPORTED VERBATIM from the diagnostic cell. Both with_oracle and
with_real are computed in ONE run so survival is measured on the identical split.

## Real-KB sourcing of the typed (effect_type, trigger_verb_class) facts -- NO gold
1. VERB-CLASS -> EFFECT semantics (generic, VerbNet/FrameNet-style, hand-curated rule on the SAME
   v3 verb-class lexicon): DESTROY-class verb -> patient DESTROYED; CREATE-class verb -> object/
   product CREATED and (for "become"-type conversion X->Y) subject/precursor DESTROYED; MOVE-class
   verb -> theme MOVES.
2. PARTICIPANT BINDING via spaCy dep-parse SRL-lite (patient/theme argument = affected
   participant) + fastcoref alias resolution (argument noun incl. pronouns -> participant via its
   coref cluster). NOT oracle participant->effect.
Real-KB fact for p = {(effect, verb_class) : some verb of that class has an affected argument (by
role) that binds to p (exact-name or coref-alias)}. ConceptNet affordances NOT used in v1
(flagged; gap-filler if survival is low + binding is the bottleneck).

## Residual oracle dependency (flagged)
The event-COUNT budget is still oracle-granted to ALL arms (same as the diagnostic; that
extraction cost was measured in ARM2). The bridge FACTS in the with_real arm are 100% real-sourced
(no gold effect/label/step). No other oracle dependency.

## Metric + decisive measurement
PRIMARY = per-step 4-way change-label macro-F1 on the UNMENTIONED subset (trap-check proxy,
mentioned==False; dev n=770 / test n=1119). **SURVIVAL FRACTION = (with_real - without) /
(with_oracle - without)**, self-contained on the run. Reported: with_real / with_oracle / without /
prior_lesion unmentioned-F1; real_lift; oracle_lift; survival; fact-coverage (real vs oracle pair
precision/recall + participant binding coverage -- localizes which piece sourced what); official
metric (context).

## Survival bar (pre-registered BEFORE running)
- `SURVIVAL_HARD_PASS = 0.50`: real-KB recovers >= 50% of the oracle lift AND real_lift >= 0.05
  (load-bearing) AND real ablation collapses (WITHOUT < 0.60) AND no leak (with_real < 0.95) ->
  **HARD_PASS_REAL_KB_SOURCES_THE_BRIDGE (GO on the KB foundation)** = extract-structure +
  source-typed-causal-knowledge-from-a-real-KB + loop -> genuine implicit-bridging comprehension on
  real prose = the validated END-TO-END pipeline.
- `SURVIVAL_HARD_FAIL = 0.25`: survival < 0.25 OR real_lift < 0.02 -> **HARD_FAIL_REAL_KB_DOES_NOT_
  SOURCE (NO-GO)**; report WHICH piece didn't source (verb-class->effect coverage vs
  participant-binding vs participant-role world-knowledge) to localize the sourcing wall.
- MIDDLE_BAND = partial survival (0.25-0.50).
- Guards (same as diagnostic): ablation must collapse (else void), no-leak ceiling, arms_differ,
  decode >= 0.99 all four arms.

## HP_SCOPE
`{real_kb: [survival_fraction_material, real_ablation_collapses, real_no_leak]}`.

## Cell-template mandates
arms_differ (asserted self-test + recorded); final_metrics_atomicity tmp_replace; except SystemExit
before except Exception (grep-verified); crlb_n/a; calibration_check default_ok; deterministic_seeding
(hashlib-seeded rng, no Python hash()/list(set())); progress_logging print_flush_true.

## Compute architecture
Sequential-CPU, justified: reuses the diagnostic precompute (spaCy parse + coref) + real-KB SRL
sourcing (spaCy parse again) + discrete firing + FHRR decode. No batching. MEASURED self-test 0.6s.
Expect smoke ~40-70s, full ~50-100s. Run INLINE/LOCALLY foreground.

## Self-test findings (real code path)
**MEASURED@..._metrics.json (self_test, 0.6s):** real-KB sourced seed facts {CREATE:[CREATE],
DESTROY:[DESTROY]} from "A seed appears" + "the fire consumes the seed" (seed = patient of consume
-> DESTROY via generic semantics, no gold); WITH-real placed [CREATE, NONE, DESTROY, NONE]
correctly; decode 1.0; 4 verdict-logic unit checks correct (go HARD_PASS / no_go HARD_FAIL / middle
MIDDLE_BAND / void HARD_FAIL).

## Smoke findings (DEV)
**MEASURED@..._smoke/metrics.json (dev):** survival 0.134 (real_lift +0.010 / oracle_lift +0.075);
with_real 0.334 / without 0.324; real_pair_recall 0.143, binding_cov 0.677; ablation collapsed, no
leak. -> NO-GO on DEV. Bars pinned before TEST.

## Full findings (TEST) -- the go/no-go: NO-GO on generic-lexicon sourcing; wall = PARTICIPANT-ROLE WORLD-KNOWLEDGE
**MEASURED@data/exp_propara_bridging_real_kb_sourcing_v1/metrics.json (test, unmentioned subset
n=1119; run_mode=full, cardinality_ok, arms_differ True, decode 1.0 all four arms). Verdict:
HARD_FAIL_REAL_KB_DOES_NOT_SOURCE_NO_GO.**

UNMENTIONED-subset macro-F1: prior_lesion 0.318, WITHOUT 0.356, **with_real_kb 0.380**, with_oracle
0.463.
- oracle_lift (with_oracle - without) = **+0.106** (reproduces the diagnostic exactly on the same split)
- real_lift (with_real - without) = **+0.023**
- **SURVIVAL FRACTION = 0.221** (< 0.50 GO bar, < 0.25 -> NO-GO). real_minus_prior_lesion = +0.062
  (real DOES beat the random floor, modestly, and ablation collapses + no leak -- the real facts
  are weakly load-bearing, just far short of the oracle lift).

**WHICH PIECE DIDN'T SOURCE (real-KB (effect,trigger) facts vs oracle facts):**
- participant_binding_coverage = **0.661** (39/59 oracle-fact participants got SOME real fact) --
  SRL-lite dep-parse + coref binding is PARTIAL but not the primary failure.
- pair_recall = **0.235**, pair_precision = **0.096** (pair_f1 0.136) -- the real-KB recovers only
  23% of the needed (effect, trigger) pairs and floods with ~90% off-target facts.
- **Root cause (structural, honest):** SRL binds a participant only where it is a syntactic
  argument -- i.e. on MENTIONED steps. But an UNMENTIONED state-change's trigger is BY DEFINITION a
  verb about ANOTHER entity (the participant is absent from that sentence's arguments), so
  SRL+coref cannot source "this process (about X) ALSO affects unmentioned participant p." The
  generic verb-class->effect semantics is fine (same lexicon); the participant binding reaches 66%
  on mentioned involvements; the MISSING piece is PARTICIPANT-ROLE / CO-PARTICIPATION
  WORLD-KNOWLEDGE (which processes consume/produce/move which unmentioned participants) -- the
  optional ConceptNet component #3, NOT used in v1.

**Official (full set, context not claim):** with_real 0.669 ~= without 0.671 ~= with_oracle 0.677,
all below the oracle-budget random-monotonic prior_lesion (0.722) -- the bridging lift is
concentrated in the unmentioned residual (a minority of cells), consistent with the diagnostic.

**GO/NO-GO DECISION:** NO-GO on the CHEAP path (generic VerbNet-style verb-class->effect + SRL +
coref). Only ~22% of the oracle bridging lift survives that sourcing. The result PRECISELY
localizes the sourcing wall: it is NOT the mechanism (the diagnostic proved the loop uses facts),
NOT the generic verb-class->effect lexicon (adequate), and NOT primarily the SRL binding (66%
coverage). It IS deep PARTICIPANT-ROLE / CO-PARTICIPATION world-knowledge -- the thing that links
an unmentioned participant to a process whose surface arguments are other entities. A bridging-KB
foundation is the right lever ONLY IF it supplies that co-participation knowledge (ConceptNet
HasA/UsedFor/MadeOf, ATOMIC/process frames, or a distilled process-physics KB). CAUTION carried
forward: CSKG/ConceptNet was measured WEAK on ProPara's scientific-process domain in the earlier
WIQA arc, so a domain-appropriate co-participation KB is not guaranteed to exist off-the-shelf --
the next step is a bounded probe (add ConceptNet co-participation roles, re-measure survival)
BEFORE committing to a full bridging-KB build. The generic-lexicon shortcut is a confirmed NO-GO.
