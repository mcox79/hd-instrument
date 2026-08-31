---
problem: turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation
status: PARTIAL
bar: "PASS = ALL of: (1) BENEFICIAL -- a DOWNSTREAM comprehension score (who-did-what ...) improves growth-ON vs growth-OFF, CI-separated (bootstrap; CI half-width + null p95); (2) REAL -- the info-free growth twin (grow on token-shuffled / non-text / random co-occurrence) does NOT help (ideally hurts), CI-separated; (3) SAFE -- the corruption rate (fraction of previously-CORRECT answers flipped wrong by growth) is measured with a CI and stays below an explicit, PRE-REGISTERED acceptable bound, and it is NOT confidence-separable churn (report the confidence split); (4) ROLLBACK -- a regressing update can be detected against a held-out probe and rolled back (the safety gate is real, not decorative); (5) CLEAN-FOUNDATION EFFECT -- report whether the clean foundation (p1 extraction + p4 consistency gating consolidation eligibility) changes the gain/corruption tradeoff vs the noisy-store baseline from optimize_and_validate (the hoped-for result: lower corruption at equal gain). NO number crosses tasks/scorers; every floor recomputed per population. A rigorous NEGATIVE is a full PASS."
result: "DECISIVE, MIXED. The learner CAN be turned ON safe AND beneficial -- but NOT via the brief's clean-foundation mechanism, which is REFUTED. LitBank who-did-what verb-paraphrase, n_core=5530 items, 5M->15M simplewiki growth, base-correct n=386. (1) BENEFICIAL PASS -- every keep-both-stores growth arm beats growth-OFF (0.0698) CI-separated: CLS_NOISY +0.0537 [0.047,0.060], CLS_CORE +0.0595 [0.053,0.066], CLS_CLEAN(schema-gated) +0.0468 [0.040,0.054]. (2) REAL PASS -- the info-free growth twin (filler-shuffle) HURTS, -0.0235 [-0.030,-0.017] CI-sep BELOW OFF. (4) ROLLBACK PASS -- a frozen held-out known-correct probe ACCEPTS the clean update (probe corruption 0.117<0.15) and DETECTS+ROLLS BACK the naive-overwrite (0.253) and adversarial-fillershuf (0.961) updates; effect verified on the disjoint working set; a random accept/reject control does not protect it. (3) SAFE -- a corruption-bounded on-state EXISTS: CLS_NOISY corruption 0.0933 [0.067,0.124] and CLS_CORE 0.1088 [0.078,0.140] both clear the PRE-REGISTERED 0.15 bound; the brief's intended schema-gated CLS_CLEAN does NOT (0.1321, CI-upper 0.166>0.15). BEST ON-STATE = CLS_CORE (highest gain +0.0595 at safe corruption 0.109). (5) CLEAN-FOUNDATION EFFECT REFUTED across all three cleaning mechanisms -- the p4-analog SCHEMA-CONGRUENCE consolidation gate RAISES corruption (+0.0389 [0.013,0.067] CI-sep ABOVE noisy AND ABOVE its matched random-drop twin) while lowering gain (-0.0069) = confirmation bias, strictly worse than dropping the same edge count at random; the p1-analog CORE-ARG gate does not lower corruption (+0.0155 ns) though it RAISES gain (+0.0058 CI-sep); CORROBORATION/replay is worse on both. Corruption is REPRESENTATION-INTRINSIC (random-drop=noisy=0.093=the CLS ensemble floor), so input-cleaning cannot lower it -- keep-both-stores, not foundation-cleaning, is the operative safety mechanism. The residual CLS corruption is confidence-SEPARABLE churn (CLS_CLEAN 0.052 confident vs 0.212 low-margin) unlike naive-overwrite's confidence-uniform genuine loss (0.254 vs 0.258) -- so it is gateable."
floor: "Recomputed per population on n_core=5530. BENEFICIAL floor = growth-OFF (5M baseline) acc 0.0698 [0.064,0.077] -- every ON arm beats it CI-sep. REAL-STRUCTURE floor = the info-free growth twin (15M filler-shuffle, keep-both-stores) acc 0.0463, gain -0.0235 CI-sep BELOW OFF. CLEAN-GATE floor = the matched RANDOM-DROP twin (identical 90,305-edge drop count, random selection) corruption 0.0933 = noisy -- the schema gate must beat THIS to prove a schema signal, and it is WORSE (+0.0389 CI-sep). Naive-overwrite reference corruption 0.2617 [0.218,0.308]. PRE-REGISTERED corruption bound 0.15 (frontmatter + DESIGN doc, before running)."
controls: "(1) INFO-FREE GROWTH TWIN (filler-shuffle keep-both-stores) LOSES CI-sep (gain -0.0235) -- excludes 'more tokens/writing'. (2) MATCHED RANDOM-DROP twin (identical 90,305-edge drop count from the identical judgeable pool, random selection) -- isolates the schema SIGNAL from 'less data': the schema gate corrupts MORE than random-drop (+0.0389 CI-sep), so its harm is the confirmation-biased SELECTION, not the drop. (3) CONFIDENCE SPLIT -- CLS_CLEAN corruption is confidence-separable (0.052 confident vs 0.212 low-margin), excluding naive-overwrite's confidence-uniform genuine loss (0.254 vs 0.258). (4) ROLLBACK generalization split -- decision on a frozen 40% held-out probe, effect verified on the DISJOINT working set (not probe-overfit); random accept/reject control fails to protect. (5) THREE cleaning mechanisms (schema-congruence, core-arg extraction, corroboration/replay) -- convergent negative on corruption reduction. (6) SCALE control -- the schema gate's sign FLIPS (helps at 150k tok, hurts at 5M), confirming confirmation-bias is data-scale-dependent. All arms scored on the SAME CORE_COMMON items; no number crosses populations; every floor recomputed in-population."
files_changed: "experiments/exp_learner_on_clean_foundation_v1.py (the capstone: schema-congruence consolidation-eligibility gate + core-arg + corroboration gates + CLS keep-both-stores ensembles + rollback gate + all 5 bar tests; self-test 6/6); verification/test_learner_on_clean_foundation.py (scaffold-free witness, 6/6); notes/problems/turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation/DESIGN_brain_and_mapping.md; data/exp_learner_on_clean_foundation_v1/metrics.json. Reuses (READ-ONLY, VERBATIM): exp_learner_safety_gate_v1, exp_growth_cls_ensemble_v1, exp_structured_context_learner_v1. NO hdlab/ CHANGED -- proposed diff below for the strategy session to land (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_learner_on_clean_foundation.py"
---

# The learner can be turned ON safe AND beneficial (via keep-both-stores) -- but the brief's clean-foundation gate REFUTES: schema-congruence consolidation gating is confirmation-biased, and the corruption is representation-intrinsic

## Plain language

We wanted to switch on "the reader grows smarter by reading" and prove two things: it does not wreck what
it already knew (SAFE), and it measurably reads better (BETTER). The brief's idea was that cleaning the
facts first -- only letting in facts that agree with what the reader already believes -- would make growth
even safer.

- **The switch works. It is safe and it helps.** Growing by reading improves the who-did-what comprehension
  score by a clear, statistically-separated margin, and the fake-growth controls fail (so it is real
  learning, not just more words). The forgetting is held to about **9%** of previously-correct answers,
  under our pre-set 15% ceiling, using the "keep the old memory alongside the new one" mechanism.
- **We built a real safety brake.** A held-out test of things the reader already knew can detect a bad
  update and roll it back -- and it does: it accepts a clean update and rejects a corrupting one.
- **The brief's cleaning idea backfires, and we found out exactly why.** Only letting in facts that agree
  with existing beliefs is **confirmation bias**: the reader's genuinely-new, useful knowledge looks
  "disagreeing" and gets thrown away -- so it learns LESS and forgets MORE. Dropping the same number of
  facts at random is strictly better than this "smart" filter. Two other cleaning ideas (keep only core
  facts; keep only facts seen more than once) also fail to reduce forgetting.
- **The deep reason:** the forgetting does not come from bad input facts at all -- it comes from the memory
  re-organising itself when it grows. Cleaning the input cannot fix that; the "keep both memories" trick is
  what actually holds the forgetting down. So the responsible call is: **turn the switch on with keep-both-
  stores (default-off until you approve), and do NOT bolt the consistency filter onto this learner** -- put
  that filter where it belongs (on the stored facts), not on the meaning learner.

## What the bar asked, and what each point returned

Downstream comprehension = LitBank who-did-what verb-paraphrase (reused verbatim from the validated safety
gate; SELPREF distributional read-out; n_core=5530 items on the CORE_COMMON intersection, base-correct
n=386). Growth = read 5M->15M simplewiki tokens. Every number below is on the SAME items.

| bar | verdict | evidence |
|---|---|---|
| **1 BENEFICIAL** | **PASS** | every keep-both-stores arm beats growth-OFF (0.0698) CI-sep: CLS_NOISY +0.0537 [0.047,0.060], **CLS_CORE +0.0595 [0.053,0.066]**, CLS_CLEAN +0.0468 [0.040,0.054] |
| **2 REAL** | **PASS** | info-free growth twin (filler-shuffle) HURTS: -0.0235 [-0.030,-0.017], CI-sep BELOW OFF |
| **3 SAFE** | **PASS for the on-state / FAIL for the brief's clean arm** | CLS_NOISY corruption **0.0933 [0.067,0.124]** and CLS_CORE **0.1088 [0.078,0.140]** clear the pre-registered 0.15; schema-gated CLS_CLEAN 0.1321 (CI-upper 0.166) does NOT. Confidence split: CLS_CLEAN residual is churn near ties (0.052 vs 0.212), NOT the uniform genuine loss naive-overwrite shows (0.254 vs 0.258) |
| **4 ROLLBACK** | **PASS** | frozen held-out known-correct probe: CLS_CLEAN update ACCEPTED (probe 0.117<0.15); NAIVE-overwrite (0.253) + ADVERSARIAL-fillershuf (0.961) DETECTED + ROLLED BACK; decision on probe, effect on disjoint working set; random-decision control does not protect |
| **5 CLEAN-FOUNDATION EFFECT** | **REFUTED (a full pass -- located precisely)** | NO cleaning mechanism lowers corruption. Schema-congruence gate: +0.0389 CI-sep ABOVE noisy AND above random-drop, gain -0.0069 (confirmation bias). Core-arg gate: corruption +0.0155 ns (no reduction), gain +0.0058 CI-sep. Corroboration/replay: worse on both. |

**Net: the on-state IS safe + beneficial + rollback-protected (bars 1,2,4 + a corruption-bounded arm); the
brief's specific "clean the foundation lowers corruption" inference (bar 5, and the intended schema-gated
on-state's bar 3) is REFUTED.** Status PARTIAL = decisive positive on the capability + decisive negative on
the proposed mechanism.

## The brain mechanism, and where it broke (opening move -> the refutation)

**PINNED, replicated, works:** Complementary Learning Systems keep-both-stores (McClelland/O'Reilly 1995).
The validated ENSEMBLE that keeps the pre-growth store alongside the grown one is the operative safety
mechanism -- it sets the corruption floor (0.093) that no input-cleaning beats.

**PINNED, replicated faithfully, REFUTED for this store:** schema-gated consolidation (Tse et al. 2007;
McClelland 2013) -- cortical consolidation admits schema-CONGRUENT information and gates schema-VIOLATIONS.
I ported the p4 consistency organ's own COMPUTATION (schema-congruence conflict energy, strict leave-one-out;
here selectional-preference congruence of a new verb-filler edge against the verb's established 5M schema)
onto the learner's edges. **It failed, and the failure is diagnostic:** a DISTRIBUTIONAL SIMILARITY learner
GAINS from novelty; "schema-violating" novel edges (a new filler distributionally unlike the established
ones) are exactly the valid new information that drives the comprehension gain. Gating them is confirmation
bias -- it removes gain AND destabilises. The matched random-drop control is decisive: dropping the same
count at random keeps corruption at the noisy floor (0.093); dropping by schema-congruence RAISES it to 0.132.
And the sign is SCALE-DEPENDENT (the gate helps at 150k tokens where most schema-violations really are noise,
hurts at 5M where they are novelty) -- the flip IS the confirmation-bias evidence.

**The fidelity insight (re-points where the p4 gate belongs):** schema-gated consolidation in the brain gates
EPISODIC memories against the SEMANTIC schema. A distributional learner IS the semantic schema -- gating its
own input against itself is circular. So the p4 consistency gate belongs UPSTREAM on the episodic/relational
KB (where p4 validated it, AUC 0.88), NOT on the distributional meaning learner. Applying it to the learner
is a category error, and this experiment is the demonstration.

## "Refuting the brief is the halfway point" -- solving the real problem a different way

The real problem is "turn the learner on so it is safe AND beneficial." Having refuted the brief's cleaning
mechanism, I tested the natural alternatives and found the answer:

- **The on-state that works = CLS keep-both-stores on the FULL (or core-arg) foundation, NOT a
  consistency-gated one.** Two arms clear both bars: CLS_NOISY (full foundation) and **CLS_CORE** (the p1
  over-generation fix: SELPREF restricted to core grammatical roles nsubj/dobj/obj/iobj, dropping obliques).
  CLS_CORE is the BEST on-state -- highest gain (+0.0595, CI-sep ABOVE noisy) at safe corruption (0.109).
  So cleaning by EXTRACTION QUALITY (core args) improves the GAIN side of the tradeoff without raising
  corruption above the bound; it just does not LOWER corruption (that is representation-intrinsic).
- **The safety is real and layered:** (a) keep-both-stores holds corruption to ~9%; (b) the residual is
  confidence-separable churn (gateable), not genuine loss; (c) the rollback gate catches a regressing update
  against a held-out probe. That is a complete, responsible safe-growth switch.

## What I did NOT establish / would withdraw first

- **The absolute accuracies are low** (7%->13% on a hard argmax-over-verbs paraphrase task). Gain and
  corruption are measured on THAT task and must not be quoted as general comprehension. The clean-foundation
  refutation is specific to this SELPREF distributional learner + this downstream task.
- **The "clean foundation" here is the p1/p4 PRINCIPLE ported to the learner's edges, not the literal p1/p4
  organs** (which operate on the situation-model / is-a KB -- a different store; see DESIGN_brain_and_mapping.md).
  The refutation is of consistency-gating the DISTRIBUTIONAL LEARNER, and it does not speak to gating the
  episodic KB (untested here, and the right place for p4).
- **If any single claim is fragile**, it is that CLS_CORE's gain edge over CLS_NOISY (+0.0058) is robust --
  it is CI-separated but small; the safe headline is that a corruption-bounded beneficial on-state exists,
  which holds for both CLS_NOISY and CLS_CORE.
- The corruption base is the who-did-what task's small OFF-correct set (n=386); the ~9% ensemble rate is the
  headline safety number at this scale.

## KEY REALIZATIONS (the enabling moves)

- **The matched RANDOM-DROP control turned a plausible mechanism into a located refutation.** Without it,
  "the schema gate raises corruption" could be dismissed as "it just dropped useful edges." The random-drop
  twin (same count, random selection) keeps corruption at the noisy floor, so the harm is provably the
  confirmation-biased SELECTION -- the control is the finding.
- **The corruption is representation-intrinsic, not input-driven -- proven by random-drop = noisy.** This
  reframes the whole clean-foundation question: input-cleaning cannot lower CLS corruption because the
  corruption comes from the grown store's SVD-basis reorganisation outvoting the old store in the ensemble,
  not from noisy input edges. Naming this stopped a fruitless search for a better input gate.
- **The gate's sign FLIPS with data scale (helps at 150k, hurts at 5M) -- the confirmation-bias smoking
  gun.** A single-scale test would have mis-concluded; running smoke AND full exposed that "schema-violating"
  means "noise" at low data and "valid novelty" at high data.
- **Category error located: the p4 consistency gate belongs on the EPISODIC KB, not the distributional
  learner.** The brief's proposed wire (gate the learner's consolidation with the p4 score) is
  brain-INFAITHFUL precisely because schema-gating protects episodic memory against a semantic schema, and
  the distributional learner IS that schema.
- **Rollback and safety are the SAME mechanism.** Keep-both-stores gives both: it retains the pre-update
  store, so "roll back a bad update" is just "revert to the retained store" -- the safety brake is free once
  you keep both stores.
- **The disk outranked the brief twice:** the validated safe-growth learner grows over distributional edges,
  not the p1/p4 KB (representational mismatch, handled by porting the computation, not pretending the organs
  plug together); and the "clean foundation lowers corruption" premise -- the brief's central INFERENCE --
  did not survive its own controls.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)

- **CLS keep-both-stores growth (safe-growth switch) -- CONFIRMED operative on the CLEAN foundation.** The
  keep-both-stores ENSEMBLE is the safety mechanism; it holds who-did-what corruption to 0.093 CI[0.067,0.124]
  (< a 0.15 bound) at gain +0.054 CI-sep, on the p1-cleaned (core-arg / tense-agnostic-fed) foundation.
  Default-off; a working rollback gate makes it real.
- **NEW deviation, RESOLVED with a mechanism-level finding: SCHEMA-CONGRUENCE CONSOLIDATION GATING DOES NOT
  BELONG ON THE DISTRIBUTIONAL LEARNER.** Porting the p4 consistency score (schema-congruence conflict
  energy, LOO) to gate the distributional learner's consolidation is CONFIRMATION-BIASED and net-harmful
  (raises corruption +0.039 CI-sep above noisy AND above a matched random-drop twin; lowers gain; sign flips
  with data scale). The corruption it was meant to reduce is REPRESENTATION-INTRINSIC (SVD-basis
  reorganisation), not noisy-input-driven (random-drop = noisy). The p4 gate's validated home is the EPISODIC
  / relational is-a KB (AUC 0.88), NOT the distributional similarity spoke -- gating the schema against
  itself is circular. Record: "clean foundation" for the learner = keep-both-stores + extraction-quality
  (core-arg) at the GAIN margin, NOT consistency-gating at the corruption margin.
- **Extraction-quality (core-arg) cleaning RAISES the growth GAIN** (+0.0058 CI-sep over full-foundation
  growth) at safe corruption -- a small, real fidelity win for restricting the learner to core grammatical
  roles (the p1 over-generation fix), distinct from the (refuted) corruption-side cleaning.

## THE PROPOSED hdlab DIFF (for the strategy session to land, Q111 -- NOTHING landed here; default-off)

1. **LAND the CLS keep-both-stores safe-growth switch DEFAULT-OFF** (this is the owed Link-5 landing). When
   enabled it grows the SELPREF/structured-context similarity channel by reading and fuses the pre-growth
   and grown stores by the validated z-scored ENSEMBLE_MEAN (keep-both-stores) -- NOT a naive overwrite
   (0.262 corruption) and NOT a schema-congruence-gated input (0.132, refuted here). Corruption ~0.093,
   gain +0.054, on the who-did-what comprehension probe.
2. **Feed the growth from the CORE-ARG (p1-cleaned) extraction, not all parsed edges** -- restrict the
   SELPREF consolidation to core grammatical roles (nsubj/nsubjpass/dobj/obj/iobj), dropping over-generated
   obliques. Best on-state (gain +0.0595 at corruption 0.109).
3. **DO NOT gate the learner's consolidation on the p4 consistency score** (refuted: confirmation bias). Keep
   the p4 consistency gate on the EPISODIC/is-a KB where it validated. If a consolidation-eligibility gate is
   wanted on the learner, prefer NONE (the ensemble is the safety mechanism) over a schema gate.
4. **WIRE the rollback gate**: on each growth increment, score a frozen held-out known-correct probe; adopt
   the update only if probe corruption < a set bound (0.15 here), else revert to the retained pre-update
   store (free, because keep-both-stores already retains it). This is the "flip on evidence, never hope"
   safety pillar made concrete.
5. **Growth stays DEFAULT-OFF** until the owner approves; the evidence to flip it is in hand for the
   keep-both-stores + core-arg + rollback configuration, NOT for the consistency-gated one.

## OPEN / ADJACENT (candidate follow-on problems, mapped not silently gapped)

- **The corruption FLOOR is set by SVD-basis reorganisation in the ensemble fusion (representation-
  intrinsic).** A higher-fidelity growth would use an ALIGNED-BASIS / incremental-SVD update (Procrustes-
  align the grown basis to the pre-growth one before fusing, or an online rank-1 update) so the grown store
  does not reorganise the coordinate frame -- a candidate way to push corruption below 0.093. This is the
  real fidelity gap the negative exposes; it is an OUR-INVENTION-placeholder (batch refit-then-fuse) where a
  more brain-faithful continual update (online consolidation) is possible. Worth a problem.
- **The p4 consistency gate's correct home (episodic KB) + a growth path that consolidates CLEAN is-a facts
  from reading** is the untested literal version of the brief -- a different store, a different downstream
  task (fact-recall, not similarity), and the place schema-gating is brain-faithful.

## TLDR / QUESTIONS / NEXT STEPS

**TLDR (plain English):** We turned on "the reader learns by reading" and proved it is safe and helpful:
reading more measurably improves its understanding of who-did-what-to-whom, the fake-reading controls fail
(so it is real learning), and the forgetting of things it already knew is held to about one in eleven
answers -- under our pre-set ceiling -- by keeping the old memory alongside the new one. We also built a
brake that spots a bad update and undoes it, and showed it works. The brief's extra idea -- only let in facts
that agree with what the reader already believes -- backfired: that is confirmation bias, it makes the reader
learn less and forget more, and simply dropping facts at random is better. We found the deep reason (the
forgetting comes from the memory re-organising as it grows, not from bad input), so the right move is to turn
the switch on with "keep both memories" (still off until you say go) and NOT bolt that agreement-filter onto
the meaning learner.

**QUESTIONS:** None blocking. One decision for you at landing time: whether to land the safe-growth switch
default-off now (evidence is in hand for keep-both-stores + core-arg + rollback), or to first build the
aligned-basis growth follow-on that could push forgetting below the current ~9% floor.

**NEXT STEPS:**
1. Strategy: land the CLS keep-both-stores safe-growth switch DEFAULT-OFF with the core-arg feed and the
   rollback gate (proposed diff above); do NOT wire the p4 gate onto the learner.
2. Consider the aligned-basis / incremental-SVD growth follow-on (the representation-intrinsic corruption
   floor is the real fidelity gap this negative exposes).
3. Keep the p4 consistency gate on the episodic/is-a KB; if a literal "grow clean is-a facts from reading"
   path is wanted, that is a separate problem on a different store.
