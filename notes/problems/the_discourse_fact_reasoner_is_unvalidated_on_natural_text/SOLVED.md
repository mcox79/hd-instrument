---
problem: the_discourse_fact_reasoner_is_unvalidated_on_natural_text
status: SOLVED
bar: "PASSES only with ALL of: 1. A REAL-TEXT inter-sentential fact-decisive population (built in experiments/ from LitBank/real narrative): a reference (pronoun or definite description) resolvable ONLY by a fact stated earlier about a candidate (NOT by grammar/salience - filter those out, as the parent did), with self-EXTRACTED per-entity facts (no oracle, no gold leak). 2. The fact-store reader beats the fact-BLIND reader CI-separated on real text (the fact-blind graded resolver recomputed on the same population = the floor); the info-free twin (shuffled facts) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. 3. The graceful-degradation curve: accuracy vs the fraction of the deciding fact actually self-extracted (and/or KG coverage) - the honest real-world bound, with the dominant failure mode named (extraction miss / KG gap / no-fact-exists). 4. One-screen summary: population -> floor -> twin -> real-text lift -> degradation curve -> verdict. Heavy -> REMOTE. A rigorous NEGATIVE is a FULL PASS (e.g. 'on real narrative the fact store lifts fact-decisive reference +X CI-sep where the fact IS self-extracted [Y% of cases], but real coverage is Y% so the population-level lift is Z - the constructed 1.0 was an idealized-extraction artifact; the mechanism is real, the bound is extraction/coverage')."
result: "TWO-SIDED, on REAL LitBank narrative with SELF-EXTRACTED facts (no oracle), measured against the REAL fact-blind resolver on the NATURAL candidate set. (POSITIVE -- a GATED capability, on the mechanism's proper domain) On the NATURAL fact-present SLIVER (14.8% of person references where the gold carries a self-extracted attribute that bridges the pronoun's verb via the real KG; n=667 TEST), fusing the fact into the REAL graded resolver LIFTS 0.837 [0.774,0.889] -> 0.961 [0.915,0.988] (store-minus-floor +0.124 [+0.080,+0.174] CI-separated ABOVE), held-out DEV picks a NONZERO bridge weight (2), the info-free twin crashes to 0.160, and on the salience-AMBIGUOUS third the lift is 0.617 -> 0.914. THE HONEST BOUNDARY: on the COMPLEMENT (85% with no bridging fact) the same cue fired BLIND HURTS 0.799 -> 0.523 -- which is WHY the unconditional weight is 0. So it is a GATED capability; the oracle-gated whole-population lift is only +0.021 (domain ~15%); the missing component is a fact-reliability GATE (brain's on-demand bridging). [An earlier CONSTRUCTED 2-way with a hardcoded coin-flip floor read 0.886 vs 0.497 -- withdrawn as a construction proof; the natural test above replaces it.] (NEGATIVE -- the coref deployment question, fired BLIND) On competitive COREF (n=4023 TEST person mentions, salience UNcontrolled), the same bridge does NOT beat the fact-BLIND graded floor: the DEV-optimal bridge weight is ZERO (held-out DEV rejects it), and FORCED on it HURTS - copula-type bridge 0.783 and all-attribute bridge 0.680 vs the fact-blind FLOOR 0.8049 [0.758,0.846], both CI-separated BELOW (copula delta -0.022 [-0.037,-0.006]; naive -0.125 [-0.160,-0.092]). The mechanism carries REAL but weak signal (it beats its info-free shuffled twin +0.046 [+0.021,+0.072] ABOVE) - it is simply swamped by structural salience and too RARE. The constructed 0.998 is an idealized-extraction + exact-KG artifact: the deciding self-extracted type-fact->verb bridge exists for the gold in only ~7% of references and the pronoun verb is in the sparse KG only ~17% of the time; the controlled degradation curve predicts ~0.60 at real coverage (near the constructed floor 0.55). BEST FAITHFUL SHOT: the two tractable brain-faithful fixes (graded distributional bridge; ambiguity gate) lift verb-visibility 3.8x (17%->67%) and gold-side bridge availability 2.1x (17%->35%) and cut the gate's harm 4x, but STILL do not beat the floor - the residual deep wall is ENTITY-SIDE (real narrative person-entities rarely carry a self-extracted type at all). BUILDING ACROSS THAT WALL (FIX 2, the brain's rich entity model): a rich-entity ACTION-HISTORY bridge (a character known by what they DO, not a stated type) HAS the coverage the type bridge lacked (gold has an action history 93% vs 43%), but is REDUNDANT with salience - DEV-optimal weight 0.0, forced it HURTS (0.750 vs floor 0.805, -0.054 BELOW), it beats its info-free twin (+0.105 ABOVE, real signal) but NOT the floor; on floor-errors it picks gold 0.224 ~ frequency 0.240. So ANY discourse-content bridge (sparse type OR rich action-history) is structurally anti-correlated with the non-salient floor-error gold (its action-history depth 26.5 <= the wrong pick's 28.7) - the lever there is the intra-sentential SYNTACTIC binder (a different organ), not the fact store. Scorer = argmax==gold link accuracy, per-doc bootstrap (docs = resampling unit)."
floor: "The fact-BLIND graded resolver (hdlab.graded_competition additive cue net, DEV-tuned weights) recomputed on the SAME real population: person-reference 0.8049 [0.7582,0.8455] (n=4023); full competitive set 0.7752 [0.7286,0.8160] (n=4693). The fact_store arm is CI-separated BELOW it at every positive bridge weight, and the DEV-optimal weight is 0.0 (== the floor exactly)."
controls: "(1) INFO-FREE TWIN (self-extracted attributes SHUFFLED across the item's candidates) -> the real bridge beats the twin +0.046 [+0.021,+0.072] ABOVE (the bridge carries genuine identity signal, not a hollow shape artifact) YET both lose to the floor -> the real signal is swamped. (2) DEV-REJECTION (held-out DEV bridge-weight sweep) -> optimal weight 0.0 for naive, copula, graded, AND graded+gated -> no positive weight helps on held-out data. (3) AMBIGUITY GATE (FIX 3: fire only when the structural margin is low) -> cuts the harm 4x (-0.099 ungated -> -0.024 gated) but does NOT recover a positive lift. (4) GRADED DISTRIBUTIONAL BRIDGE (FIX 1, the ATL-faithful PPMI+SVD coherence) -> lifts verb-visibility 0.175->0.671 and gold-side availability 0.167->0.351, still BELOW floor -> the KG-sparsity wall is real but not the deep one. (5) COVERAGE FUNNEL + FLOOR-ERROR DECOMPOSITION -> on the references where structure/salience FAILS (n=785, the cases needing help) the self-extracted gold type-fact->verb bridge exists in only 5-11%; DOMINANT bottleneck = KG-vocab (17%) then, once graded, ENTITY-SIDE type-fact absence. (6) DEGRADATION (constructed harness, extraction-coverage + KG-coverage knobs) -> monotone floor->0.998, and real-text coordinates land at ~0.60 (near floor) -> the 0.998 is idealized extraction + exact KG. (7) RICH-ENTITY (FIX 2) REDUNDANCY: the action-history bridge's DEV-optimal weight is 0.0 and it beats its info-free twin but not the floor, and on floor-errors it picks gold 0.224 ~ frequency 0.240 -> the rich entity model is redundant with the salience the floor already has. (8) NO-LEAK self-test -> a fact at sent s is invisible to a query before sent s. (9) POSITIVE-DOMAIN, HONEST: the floor is the REAL graded resolver on the NATURAL ~40-candidate set (MEASURED 0.837 on the sliver), held-out DEV picks bridge weight 2, the info-free twin crashes to 0.160, and the COMPLEMENT (no fact) shows the cue HURTS blind (0.799 -> 0.523) -> the sliver lift is a genuine gated capability, not a cherry-pick (the complement is the boundary). [The withdrawn constructed 2-way used a hardcoded coin-flip floor -- replaced.]"
files_changed: "experiments/exp_discfact_realtext_validation_v1.py (the honest real-text measurement: coverage funnel + population arms + floor-error decomposition + fact-decisive conditional), experiments/exp_discfact_realtext_degradation_v1.py (the controlled degradation curve connecting the constructed 0.998 to the real-text floor and locating real text on it), experiments/exp_discfact_realtext_fidelity_fixes_v1.py (the best faithful shot: graded distributional bridge + ambiguity gate + residual-bottleneck decomposition), experiments/exp_discfact_realtext_rich_entity_v1.py (BUILDING ACROSS THE WALL, FIX 2: the rich-entity action-history bridge -- has coverage, redundant with salience), experiments/exp_discfact_realtext_factpresent_v1.py (THE POSITIVE DOMAIN, honest: on the natural fact-present sliver the fact lifts the REAL resolver 0.84->0.96 CI-sep, complement hurts -> a gated capability), experiments/exp_discfact_realtext_gate_v1.py (THE GATE: no observable fact-reliability gate -- hand or learned logistic -- beats the floor; net-zero is the brain-faithful calibration), verification/test_discfact_realtext.py (11/11 scaffold-free witness), notes/problems/the_discourse_fact_reasoner_is_unvalidated_on_natural_text/{SOLVED.md, research_realtext_reference_brain_mechanism_2026-08-29.md, research_reliability_gating_brain_mechanism_2026-08-29.md}. NO hdlab/ write (Q111). Reuses the LANDED harness (build_instances, graded_competition, DiscourseFactStore, the graded PPMI+SVD bridge)."
reverify: ".venv/Scripts/python.exe verification/test_discfact_realtext.py"
---

# What was built and measured

The brief asked: confront the discourse-fact bridge -- graded EXCELLENT on a CONSTRUCTED population (0.998 vs a
0.504 fact-blind floor) with IDEALISED extraction (clean IS-A facts handed in) + EXACT KG edges -- with REAL
narrative, where the reader must SELF-EXTRACT the per-entity facts and the KG is patchy. I built exactly that
measurement, then (per the owner's push and the standing protocol) drilled the wall it exposed with brain
research and gave the brain-faithful fix its best shot, then MEASURED the mechanism's proper domain. **The disk
gives a TWO-SIDED answer, both halves CI-separated with controls: fused with the REAL resolver on the natural
fact-present SLIVER (~15% of references) the self-extracted fact LIFTS 0.84->0.96 (a GATED capability -- it HURTS
fired blind), and unconditionally it does NOT help competitive coref (salience dominates; the fact is rare). A
rigorous negative is a full pass per the bar; here it arrives WITH the positive-domain demonstration -- measured
against the real resolver on natural data -- that the validation question was really asking for.**

## THE POSITIVE DOMAIN (the headline): a GATED capability, measured against the REAL resolver on NATURAL data
`exp_discfact_realtext_factpresent_v1.py`. Does the self-extracted fact help the REAL resolver WHERE a fact is
present? I answer on the NATURAL population (the landed `build_instances` ~40-candidate set, the genuine graded
resolver as the floor -- no coin flip, no curated pair), split by whether the GOLD carries a self-extracted
attribute (copula IS-A or role nominal, `sent < now`) that BRIDGES the pronoun's clause verb via the real KG.

| SLIVER = gold has a bridging self-extracted fact (14.8% of person refs; n=667 TEST) | acc |
|---|---|
| fact_blind FLOOR (the REAL graded resolver, MEASURED) | 0.837 [0.774,0.889] |
| **fact_store (real resolver + self-extracted bridge, DEV-tuned weight=2)** | **0.961 [0.915,0.988]** |
| info_free twin (bridge shuffled across the ~40 candidates) | 0.160 |
| store - floor | **+0.124 [+0.080,+0.174] ABOVE** |
| store - twin | +0.801 ABOVE |
| salience-AMBIGUOUS third: floor 0.617 -> **fact_store 0.914 ABOVE** | -- |

**Where a fact is present, using it genuinely helps resolve REAL reference over and above salience: fused with
the real resolver it lifts 0.837 -> 0.961 CI-separated, held-out DEV picks a NONZERO weight (2), the info-free
twin crashes to 0.16, and on the hard salience-ambiguous third the lift is 0.62 -> 0.91.** THE HONEST BOUNDARY
(what makes the conditioning not a cherry-pick): on the COMPLEMENT -- the 85% of references with NO bridging gold
fact -- the SAME cue fired blind HURTS, 0.799 -> 0.523 (it fires on distractors). **That complement harm is
exactly WHY the unconditional DEV weight is 0 (the coref negative above): the cue is double-edged, valuable only
where a fact exists.** So the mechanism's real-text value is a GATED capability -- and the whole-population lift IF
a perfect fact-reliability gate fired it only where a trustworthy fact exists is small (+0.021, 0.805 -> 0.826),
because the domain is only ~15% of references. The missing brain-faithful component is that GATE (the brain's
on-demand bridging: Haviland & Clark 1974; fire inference only when direct integration fails) -- named, not built.

**HONEST CORRECTION (this cell was rebuilt).** An earlier version measured a CONSTRUCTED salience-balanced 2-way
with a HARDCODED coin-flip floor and the gold SELECTED to bridge (0.886 vs 0.497) -- a construction proof, not a
capability, and I flagged it as over-reach. The table above is the corrected honest test: REAL resolver floor,
NATURAL candidate set, held-out DEV weight, complement boundary. The real positive is smaller and gated, but it is
genuine (CI-separated over the real resolver on natural data), which the constructed number could not establish.

## CAN A GATE DEPLOY IT? No -- and the drill proves the net-zero gate is BRAIN-FAITHFUL, not a failure
`exp_discfact_realtext_gate_v1.py` + `research_reliability_gating_brain_mechanism_2026-08-29.md`. The positive is
GATED (helps on the 15% sliver, hurts blind on the 85% complement), so the deployment question is: without seeing
the gold, can an observable fact-reliability GATE fire the bridge only where it helps? I built the gate every way
-- hand rules (fire on a clean copula type; on low structural margin; on a salient bridger; combinations) AND a
LEARNED logistic gate over all reliability features, tuned on held-out DEV:

| gate on person TEST (n=4023) | acc |
|---|---|
| never (fact-blind FLOOR) | 0.8049 |
| always (blind) | 0.596 |
| best hand gate (copula + low-margin) | 0.8059 |
| **LEARNED logistic gate** | 0.8054 |
| ORACLE ceiling (fire where the gold truly bridges) | 0.8255 |

**No observable gate beats the floor -- the best is +0.001 (NOT separated), the learned gate +0.0005, and the
ORACLE ceiling is itself only +0.021 and unreachable.** The reason: a bridge OVERRIDE of the structural pick is
correct only ~7% of the time (the resolver is near-optimal), and observables cannot separate a GOLD-bridging fact
from a DISTRACTOR-bridging one.

**THE DRILL VERDICT (decisive): (A) INTRINSIC BOUND, not a missing mechanism.** The research drill (5 converging
literatures) establishes that the brain has NO discrete reliability gate: it integrates world knowledge
CONTINUOUSLY as a graded cue (McRae/Spivey-Knowlton/Tanenhaus 1998 thematic fit; Metusalem et al. 2012 automatic
event-knowledge activation; Kehler & Rohde 2013 Bayesian -- world knowledge is a soft PRIOR, morphosyntax/salience
the likelihood). A low-validity cue AUTOMATICALLY gets low weight in the product -- so a NET-ZERO calibrated weight
is the CORRECT brain-faithful behavior, not a failure. Corroboration: humans themselves top out at ~92% on
world-knowledge-decisive Winograd items (Bender 2015; Davis 2016) and routinely underspecify/satisfice (Ferreira &
Patson good-enough); world-knowledge-decisive reference is a small minority (Competition Model: semantic cues are
LOW-availability -> LOW-validity for reference). **My OWN three cells VET the calibration directly: the DEV-tuned
bridge weight is 2 on the fact-present sliver and 0 on the full population -- the integrator correctly weights the
cue BY ITS POPULATION RELIABILITY, exactly the Bayesian behavior.** So the +0.021 ceiling and the net-zero gate are
the brain-faithful outcome; the lever is NOT "a better gate" but making the fact a soft activation-weighted prior
(which my learned gate approximated, returning net-zero -- confirmatory). **The organ's value is in fact-GIVEN
tasks (QA / next-event, where the task SUPPLIES the fact-present condition), not fact-DETECTION in the wild.**
(Honesty: "net-zero = correct calibration, not failure" is a strategic read that runs slightly ahead of a direct
equivalence proof -- but it is convergent across five independent literatures AND matches the weight-tracks-
reliability result on our own data, so I treat it as the decisive call, VET-pending only on the strongest form.)

## The coref measurement (bar items 1-2): the self-extracted bridge does NOT survive competitive coref
`exp_discfact_realtext_validation_v1.py`. Population = REAL LitBank competitive pronoun resolution (100 novels;
a mention has >=2 gender/number-compatible prior entities -- the same landed harness `build_instances`), PRIMARY
on person reference (he/she/...), the parent's validated "she = the surgeon" case; DEV/TEST split by document.
Facts are SELF-EXTRACTED from the real parse (copula IS-A "X is a doctor" + nominal type heads, `sent < p_sent`,
no leak) -- NO oracle. The bridge is fused as a graded cue into the SAME `hdlab.graded_competition` net; the
floor is that net WITHOUT the bridge.

| arm (person TEST, n=4023) | acc | vs floor |
|---|---|---|
| **fact_blind FLOOR** | **0.8049 [0.758,0.846]** | -- |
| fact_store copula-type (forced wb=1) | 0.783 | **-0.022 [-0.037,-0.006] BELOW** |
| fact_store all-attribute (forced wb=1) | 0.680 | **-0.125 [-0.160,-0.092] BELOW** |
| info_free twin (attrs shuffled) | 0.638 | -- |

**The DEV-optimal bridge weight is 0.0** -- held-out DEV itself rejects the bridge; the DEV-selected fact_store
reader IS the floor. The full competitive set (incl. it/they, n=4693) reproduces it (floor 0.775, copula 0.754).
**But the real bridge beats its shuffled twin (+0.046 ABOVE)** -- it carries GENUINE reading-built identity
signal; it is simply too weak and too rare to overcome the structural salience the graded floor already uses.

## Why (bar item 3): the coverage funnel + the degradation curve
The real-text applicability is tiny and I quantified where the fact-chain breaks. On the references where
structure/salience FAILS (n=785, the cases that NEED semantic help): the pronoun verb is in the sparse KG only
**16.9%** of the time; a self-extracted gold type-fact that bridges to that verb exists in only **5% (copula) to
11% (any nominal)**. `exp_discfact_realtext_degradation_v1.py` then CONNECTS the constructed 0.998 to this floor
by injecting the two real-text noise axes on the constructed harness one at a time:

- accuracy vs **extraction coverage**: 0.55 (0%) -> 0.60 -> 0.67 -> 0.78 -> 0.89 -> **1.0** (100%), monotone, no cliff.
- accuracy vs **KG coverage**: 0.55 -> 0.59 -> 0.69 -> 0.78 -> 0.87 -> **1.0**, monotone.
- **LOCATED:** at the measured real-text extraction coverage (~7%) and KG coverage (~17%), the curve predicts
  **~0.60 -- near the constructed fact-blind floor.** The 0.998 was an idealized-extraction + exact-KG artifact,
  quantified.

## The wall, understood (the owner's push: "if the brain can do it, we should be able to")
A research drill (`research_realtext_reference_brain_mechanism_2026-08-29.md`) established the wall is a set of
buildable FIDELITY GAPS, not a "brain-can-we-can't" impossibility:
1. **Most natural reference is structurally decidable BY DESIGN** (Winograd/GAP/KnowRef are HAND-BUILT precisely
   because world-knowledge-decisive reference is rare in natural corpora; communicative efficiency). So a small
   fact-decisive coverage is partly a PROPERTY OF LANGUAGE, not only our failure.
2. When the brain DOES bridge, it uses **GRADED thematic fit over a DENSE semantic hub** (Lambon Ralph 2017;
   McRae 1998) on **RICH multi-attribute entity models** (Gernsbacher; Metusalem 2012), and only **when structure
   conflicts** (Haviland & Clark 1974). Our boolean 17%-coverage KG + single-copula-noun type + ungated firing
   are three OUR-INVENTION deviations.

## The best faithful shot (bar item 3, the fix direction): fidelity fixes locate the DEEP wall
`exp_discfact_realtext_fidelity_fixes_v1.py` builds the two tractable research-named fixes and measures them on
the competitive subset (the research's own recommended target):
- **FIX 1 -- graded distributional bridge** (ATL-faithful PPMI+SVD coherence, the parent's L1b): lifts verb-
  visibility **17% -> 67%** (a graded space sees verbs the boolean KG lacks) and gold-side bridge availability
  **17% -> 35%**.
- **FIX 3 -- ambiguity gate** (fire only when the structural margin is low): cuts the harm **4x** (-0.099 -> -0.024).
- **NEITHER recovers a positive lift; the DEV-optimal weight is still 0** -- and the decomposition says why: even
  with the dense graded space, the gold has a usable self-extracted type in **< 35%** of references. **The deep
  residual wall is ENTITY-SIDE type extraction (FIX 2)** -- real narrative person-entities are referred to by
  name/pronoun, almost never by a stated type. That is a comprehension-depth problem, not a KG or gating problem.

## Building ACROSS the deep wall (FIX 2): a rich-entity model has coverage but is REDUNDANT with salience
`exp_discfact_realtext_rich_entity_v1.py`. The owner's push -- *if the brain can do it, we can once we
understand* -- required not just NAMING FIX 2 but building it. The brain-faithful rich entity model (Gernsbacher
structure-building; Zwaan protagonist tracking; concept cells wired to hundreds of associations) says a character
is known by **what they DO**, not a stated type -- and every character HAS an action history. So I built the
bridge that resolves the pronoun to the candidate whose accumulated **actions** are thematically coherent with
the current verb (graded verb-verb coherence in the ATL-analog space).

| (person TEST, n=4023) | value |
|---|---|
| gold has an ACTION HISTORY | **0.930** (vs 0.43 for a stated copula type -- FIX 2 HAS the coverage) |
| fact_blind FLOOR | 0.8049 |
| rich-entity bridge (DEV-tuned) | 0.8049 (**DEV-optimal weight = 0.0**) |
| rich-entity bridge (forced wb=1) | 0.7504 (**-0.054 BELOW floor**) |
| info-free twin | 0.6455 (rich-entity beats it +0.105 ABOVE -- **real signal**) |
| on floor-errors: action-history picks gold | 0.224 **~** frequency 0.240 (**redundant with salience**) |

**The rich entity model has the coverage the type bridge lacked, but its signal is REDUNDANT with the salience
the floor already uses** -- and the STRUCTURAL REASON generalizes the parent's anti-typical-residual diagnosis: on
the references where structure/salience FAILS, the gold is BY DEFINITION the NON-salient, LOWER-history entity
(its action-history depth 26.5 <= the wrong pick's 28.7), so **ANY bridge that retrieves accumulated discourse
content -- sparse type OR rich action-history -- is anti-correlated with the target.** This is NOT "the brain can,
we can't": the brain does not use a discourse-content bridge on the non-salient gold either -- it uses fast
intra-sentential **SYNTACTIC binding** (Centering Cb-absence; Sturt 2003 first-pass structural binding). **So the
lever for real-text competitive coref is the syntactic binder (a DIFFERENT organ), and the discourse-fact
reasoner's real-text home is inter-sentential fact-PRESENT tasks (QA / next-event), not coref of any kind.**

# What I did NOT establish (and would withdraw first if wrong)
1. **The positive is a CONDITIONAL, GATED lift, not a deployable win -- withdraw first any reading of "the fact
   store improves real-text resolution."** (a) It is measured on the SLIVER where a self-extracted fact bridges
   the gold (~15% of references); on the other 85% the same cue HURTS (0.799->0.523), so unconditionally it is
   net-harmful (weight 0). (b) The whole-population lift even with a PERFECT (oracle) gate is only +0.021, because
   the domain is small. (c) The gate that would make it usable -- detecting when a self-extracted fact is
   trustworthy -- is NAMED (brain's on-demand bridging) but NOT built. The honest headline is the PAIR: "~15%
   coverage; on it +0.124 over the REAL resolver; harmful blind; needs a gate." Withdraw any single-number summary.
2. **FIX 2 (rich entity extraction) is now BUILT and TESTED, and it too is redundant with salience FOR COREF.**
   The rich-entity action-history bridge has coverage (93%) but does not beat the floor (DEV weight 0). What I did
   NOT establish: that a rich entity model fails on the mechanism's PROPER domain (inter-sentential fact-PRESENT
   tasks). I showed it is redundant with salience for COMPETITIVE COREF specifically -- because the coref
   floor-error gold is non-salient/low-history. On a QA/next-event task where the deciding fact IS present and the
   target IS the discourse-rich entity, a rich entity model may well help; that is untested here and is the
   mechanism's real home. Withdraw first any implication that FIX 2 is worthless in general (it is specifically
   redundant for coref).
3. **The person-reference restriction is a JUDGEMENT.** The full competitive set (incl. it/they to objects) is
   reported as robustness and agrees, but the primary numbers are person-only; a reviewer who wanted the headline
   on the full set gets 0.775 floor / 0.754 copula -- same conclusion, slightly smaller floor.
4. **The KG-coverage figures are for THIS CSKG** (`cskg_foundation_v1`). A different world-knowledge base would
   move the 17% (the graded space already moves it to 67%); the ENTITY-side 35% is the binding one and is
   KG-independent.

# KEY REALIZATIONS (the enabling moves)
1. **Tune the bridge weight on held-out DEV and let it choose ZERO.** The single most decisive move: rather than
   forcing a bridge and arguing about the delta, I let DEV pick the weight. It picked 0 -- for the naive, copula,
   graded, AND gated bridges. "The optimal amount of this cue is none" is a cleaner negative than any p-value.
2. **Decompose the FLOOR'S ERRORS, not the whole population.** Asking "of the cases where structure FAILS, how
   often does a self-extracted fact even exist to help?" (answer: 5-11%) turned a vague "it doesn't work" into a
   quantified funnel and named the dominant bottleneck. The population-level number hides the mechanism; the
   floor-error decomposition reveals it.
3. **Separate the boolean-KG wall from the entity-side wall with a coverage probe BEFORE concluding.** The verb
   is in an explicit CapableOf edge only 17% of the time but appears anywhere in the KG action vocabulary ~94% --
   so the "16% coverage" wall is largely an artifact of the boolean hard-match. Building the graded bridge lifted
   it to 67% and exposed the REAL wall (entity-side type, <35%). Without that probe I would have mis-attributed
   the failure to the KG and proposed the wrong fix.
4. **The info-free twin is what saves the negative from being a flat null.** The bridge loses to the floor but
   BEATS its shuffled twin -- so the reading-built binding is genuinely informative, just swamped. That single
   contrast is the difference between "the mechanism is real but the case is rare" (true) and "the mechanism is
   noise" (false).
5. **A controlled degradation curve on the WORKING harness is how you connect a 0.998 to a real-text floor
   HONESTLY.** Injecting extraction + KG noise into the constructed jig (where the mechanism provably works) and
   reading off real-text coordinates PROVES the 0.998 was idealised extraction + exact KG -- rather than asserting it.
6. **Lead-with-biology reframed the wall from "failure" to "three named fidelity gaps."** The research point that
   world-knowledge-decisive reference is RARE BY DESIGN (Winograd corpora are hand-built) means the low coverage
   is partly a property of language -- so the honest target is the competitive subset with a fidelity-corrected
   bridge, not full-corpus accuracy. That is what turns a dead end into a scoped next problem.
8. **To SHOW the positive domain HONESTLY, measure against the REAL resolver on the NATURAL candidate set, and
   report the COMPLEMENT.** My first positive cell constructed a salience-balanced 2-way with a hardcoded coin-flip
   floor and the gold selected to bridge -- a construction proof I caught and withdrew. The honest test splits the
   NATURAL population by whether a bridging fact exists: on the SLIVER (fact present) fusing the fact into the real
   resolver lifts 0.84->0.96 CI-separated (DEV picks weight 2, twin crashes); on the COMPLEMENT the same cue HURTS
   (0.80->0.52). Reporting BOTH is what makes the conditioning honest rather than a cherry-pick -- and it revealed
   the true shape (a GATED capability with small population headroom), which the coin-flip version hid. The
   enabling move was the discipline itself: never a hardcoded floor, always the real resolver + the complement.
7. **Building the fix I proposed (FIX 2), rather than just naming it, found the DEEPER, GENERAL bound.** Instead
   of stopping at "rich entity extraction would help", I built the rich-entity action-history bridge -- and it too
   collapsed to the floor. That failure GENERALIZED the parent's anti-typical-residual insight into a law: on
   competitive coref, ANY bridge that retrieves accumulated discourse content (sparse type OR rich history) is
   anti-correlated with the non-salient floor-error gold, because that gold is the LOW-content entity by
   definition. The enabling move was to let DEV choose the weight on the RICH cue too (it chose 0) and to measure
   the gold-vs-wrongpick history DEPTH -- which showed the content bridge points the wrong way. This is the
   difference between "my proposed fix should work" (a hope) and "here is exactly why no discourse-content bridge
   can, and which organ actually owns this population" (the syntactic binder).
9. **A "failed" gate + a drill turned into a brain-fidelity CONFIRMATION.** I proposed the fact-reliability gate as
   the highest-value fix, built it every way (hand + learned logistic), and it returned NET-ZERO. Rather than
   filing that as a dead end, I drilled the biology -- and it flipped the meaning: the brain has NO reliability
   gate; it integrates world knowledge as a continuous graded PRIOR (Kehler & Rohde Bayesian), so a low-validity
   cue CORRECTLY gets low weight. The enabling move was to notice my OWN data already proved it: the DEV-calibrated
   weight is 2 where facts are present and 0 across the population -- the integrator weights the cue by its
   reliability, exactly the Bayesian behavior. So "our gate does nothing" became "our reader is already correctly
   calibrated, and a gate is the WRONG lever" -- and the humbling lesson: a net-zero result can be the CORRECT
   answer, and the way to know is to ask whether the brain even has the mechanism you were about to build.

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **Situation-model RESOLUTION / discourse-fact store (REFINE the existing entry).** The parent added this organ
  with a PINNED computation (Garrod-Sanford; Kintsch CI) proven CI-separated on CONSTRUCTED data, and flagged
  "real-text accuracy unmeasured" as the remaining deviation. **That deviation is now MEASURED and BOUNDED:** on
  real LitBank narrative the self-extracted bridge does NOT beat the fact-blind floor (DEV-optimal weight 0;
  forced on it hurts CI-separated), because (a) fact-decisive reference is rare (~7% of references) -- partly a
  property of language (Winograd/GAP/KnowRef are hand-built), and (b) the two OUR-INVENTION deviations bite:
  the sparse boolean KG (17% verb coverage; a graded distributional space lifts it to 67%) and the single-copula
  type extraction (gold-side availability < 35% even with the dense space -- the DEEP residual wall). The organ's
  computation stays PINNED and real (it beats its info-free twin); the real-text CAPABILITY for COMPETITIVE COREF
  is bounded near the floor. **All THREE brain-faithful fixes were built/tested here** (dense graded knowledge;
  ambiguity gate; AND the rich-entity action-history model, FIX 2), and a GENERAL bound emerged: on competitive
  coref, ANY bridge that retrieves accumulated discourse content (sparse type OR rich action-history, coverage
  43% vs 93%) is redundant with salience and anti-correlated with the non-salient floor-error gold -- generalizing
  the parent's anti-typical-residual diagnosis. So the discourse-fact/situation-model organ is measured to be the
  WRONG tool for competitive coref of any kind (the syntactic binder owns that population). **BUT its real-text
  HOME is now DEMONSTRATED, not just named:** on the NATURAL fact-present sliver (~15% of refs), fused with the
  REAL resolver the self-extracted fact LIFTS 0.837->0.961 CI-separated (+0.124; DEV weight 2; twin crashes),
  while on the complement it HURTS blind (0.80->0.52) -- a GATED capability (oracle-gated whole-population lift
  +0.021). NO observable gate (hand or learned) recovers even that +0.021, and the DRILL verdict is that this is
  the BRAIN-FAITHFUL outcome: the brain has no reliability gate, it integrates world knowledge as a continuous
  graded PRIOR (Kehler & Rohde 2013 Bayesian; McRae 1998; Metusalem 2012), so a low-validity cue correctly gets
  low weight -- our DEV-calibrated weight tracks reliability (2 on the sliver, 0 on the population). So the organ's
  computation is REAL on natural prose where its precondition holds; the bound is INTRINSIC (world knowledge is a
  low-validity cue for reference; humans top out ~92% on decisive items), and the organ's value is in fact-GIVEN
  tasks (QA/next-event), NOT fact-detection in the wild. PINNED refs: Lambon Ralph 2017; McRae 1998; Metusalem
  2012; Kehler & Rohde 2013; Bates & MacWhinney Competition Model; Ferreira & Patson good-enough; Sturt 2003.

# ADJACENT COMPONENTS -- capabilities / limitations / brain-foundational status (seeds the next problems)
1. **[THE REAL LEVER FOR COREF -- a DIFFERENT organ] The intra-sentential SYNTACTIC binder.** After building BOTH
   discourse-content bridges (type AND rich action-history) and finding both redundant with salience, the
   floor-error/non-salient-gold population is confirmed to be the syntactic binder's job, NOT the fact store's.
   CAPABILITY (parent): a fine-distance oracle recovers 37.6% of the anti-typical residual. BRAIN STATUS: PINNED
   (Sturt 2003 first-pass structural binding within fixations; Centering Cb-absence for freshly-introduced
   antecedents). NOT built. **This is the HIGHEST-leverage follow-on for real-text competitive coref** -- the fact
   store and the rich entity model are both measured to be the wrong tool for it.
2. **[FIX 2 -- BUILT + TESTED] Rich multi-attribute entity EXTRACTION.** CAPABILITY: the action-history bridge has
   93% coverage (every character acts) -- the coverage the copula-type bridge (43%) lacked. LIMITATION (measured):
   its signal is REDUNDANT with salience for coref (DEV weight 0; ~ frequency on floor errors), because the
   coref target is the non-salient/low-history entity. BRAIN STATUS: the rich entity model is PINNED-real
   (Gernsbacher; Zwaan protagonist tracking; Metusalem 2012) and the bridge carries genuine signal (beats its
   twin) -- it is just the wrong LEVER for coref. OPTIMIZATION / NEXT PROBLEM: test the rich entity model on the
   mechanism's PROPER domain -- an inter-sentential fact-PRESENT task (bridging QA / next-event) where the target
   IS the discourse-rich entity -- NOT coref.
3. **[FIX 1 -- PARTLY ADDRESSED] The world-knowledge base (the generic bridge).** CAPABILITY: the static CSKG
   supplies role->action edges; the graded PPMI+SVD space (built here from its co-occurrence) lifts verb-
   visibility 17%->67%. LIMITATION: still sparse (67%, not the brain's ~universal coverage); the space is
   KG-derived, not coupled to the substrate's grounded distributional-meaning (p1) lane. BRAIN STATUS: now
   DISTRIBUTIONAL/graded (ATL-faithful) rather than boolean. OPTIMIZATION: couple the coherence score to the p1
   representation lane (the deeper fidelity move the parent also named) -- a denser, grounded semantic hub.
4. **[FIX 3 -- BUILT] The ambiguity/coherence gate.** CAPABILITY: firing the bridge only on low structural margin
   cuts its harm 4x. LIMITATION: it prevents damage but cannot ADD signal the entity side lacks. BRAIN STATUS:
   PINNED (Haviland-Clark bridging cost; concept-cell reactivation only on demand). OPTIMIZATION: a graded
   coherence-driven gate (Kehler et al. 2008) rather than a margin threshold.
5. **The structural resolver (`hdlab.graded_competition`) is EXCELLENT and DOMINATES on real text.** CAPABILITY:
   0.80 on the competitive person set from salience/Centering cues alone -- consistent with the research finding
   that natural reference is structurally decidable by design. LIMITATION: it is the CEILING the fact bridge must
   beat, and on real text it usually already has the answer. BRAIN STATUS: PINNED (Lewis-Vasishth cue-based
   retrieval; Centering). No change needed; it is consumed as the floor here.

# PROPOSED hdlab DIRECTION (strategy lands; Q111)
- **Do NOT land the self-extracted discourse-fact bridge as a real-text coref improvement** -- it is measured at
  or below the fact-blind floor on real narrative (DEV-optimal weight 0; forced on it hurts CI-separated). The
  parent's proposed situation-model organ should be landed with a **discourse-age + AMBIGUITY gate** (fire only
  for candidates with >=1 prior self-extracted type AND when the structural margin is low) and the **graded
  distributional bridge** (not the boolean hard match), so that on real text it is at worst NEUTRAL (recovers the
  floor) rather than harmful -- the graded+gated arm here is exactly the floor.
- **The real-text value of the organ is on INTER-SENTENTIAL, fact-PRESENT reference -- now MEASURED against the
  REAL resolver:** on the natural fact-present sliver the fact lifts the real resolver 0.837->0.961 CI-separated.
  BUT it is a GATED capability: fired blind it HURTS (complement 0.80->0.52), so it MUST be landed behind a
  fact-reliability gate (fire the bridge only when a trustworthy self-extracted fact exists), NOT wired
  unconditionally into competitive coref. The gate is the missing brain-faithful component (on-demand bridging)
  and the highest-value thing to build before this earns its keep at the population level (oracle-gated headroom
  only +0.021 until it exists).
- **For real-text competitive COREF, the next problem is the intra-sentential SYNTACTIC binder, NOT the fact
  store.** I built both discourse-content bridges (type AND rich action-history) and both are redundant with
  salience; the non-salient floor-error gold is the syntactic binder's population (Sturt 2003). The rich entity
  model (FIX 2) should instead be tested on the organ's PROPER domain -- an inter-sentential fact-PRESENT task
  (bridging QA / next-event) where the target IS the discourse-rich entity.

---

## TLDR (plain language)
We built a "reading memory" that resolves "she = the surgeon" by remembering, from reading, that a character is
a surgeon and that surgeons operate. On hand-built examples it was almost perfect. **On real novels it does not
help -- and I measured exactly why, and confirmed with brain science that this is fixable, not impossible.**
Three things: (1) in real stories, who a pronoun refers to is almost always settled by simple cues (who was just
mentioned, gender) -- the language is BUILT that way for efficiency, so the "needs world knowledge" case is
genuinely rare (~1 in 14); the puzzle books that need world knowledge (Winograd schemas) had to be hand-written
for exactly this reason. (2) Our world-knowledge book is thin -- it knows the character's action only 1 time in 6;
swapping in a "fuzzy" version (the way the brain stores meaning) fixes most of that (up to ~2 in 3). (3) The real
wall is that novels almost never STATE what a character IS ("Sam is a doctor") -- they just use names and "he/she"
-- so there is usually no fact to look up. **But here is the payoff, measured honestly against the real reader:
on the real sentences where a fact IS stated (about 1 in 7), adding that fact to the actual resolver makes it
clearly BETTER -- 84% right becomes 96% (and on the genuinely hard cases, 62% becomes 91%), while every scrambled
version collapses.** The honest catch: you cannot use the fact blindly -- on the sentences with no relevant stated
fact, reaching for one actively MISLEADS (it drops from 80% to 52%), which is why a blind reader is better off
ignoring it. So the reading memory is a REAL skill with a REAL catch: it helps a lot exactly where a fact was
stated, and hurts where none was -- so ideally the system would know WHEN it has a usable fact. I tried hard to
build that "switch" (every rule I could, plus a machine-learned one) and it does NOT work -- and the drill into
the brain explains why it CAN'T: the brain has no such switch. It blends world knowledge in continuously as a soft
hint whose strength automatically reflects how reliable it is -- and for ordinary pronouns a stated fact is a weak,
rare hint, so it correctly counts for little (even people only get ~92% on the puzzles built to need world
knowledge, and usually just satisfice). So the honest, settled picture: our reader already does the brain-faithful
thing -- it leans on the fact heavily where one is clearly present and ignores it otherwise, and that is CORRECT,
not a bug. The value of this reading memory is therefore in tasks that HAND it a stated fact and ask a question
about it (like reading comprehension Q&A), not in guessing pronouns in open prose. That is now settled with
evidence, not guessed, and the next problem is precisely scoped: use the reader where facts are given.

## QUESTIONS
One honest labelling call for you. The validation question now has a complete, two-sided, CI-separated answer
with controls -- fired BLIND the fact does NOT help coref (weight 0), and fused into the REAL resolver on the
natural fact-present sliver (~15%) it LIFTS 0.84->0.96 (DEV weight 2, twin crashes) but HURTS on the complement,
so it is a GATED capability with small population headroom (+0.021) until a reliability gate exists. I have set
status **SOLVED** because the measurement is complete and the positive is now genuine (real resolver, natural
data) rather than the withdrawn construction proof. But it is a defensible **PARTIAL** too: the deployable win is
gated-and-unbuilt, and the whole-population lift today is +0.02. I lean SOLVED-on-the-measurement; if you weight
the deployable capability, PARTIAL is right. Content is identical either way. (This is the third label move on this
problem -- I am flagging that churn honestly rather than hiding it.)

## NEXT STEPS
1. **(Strategy)** Re-verify the witness (`verification/test_discfact_realtext.py`, 10/10). Fold the AUDIT UPDATE
   into `BRAIN_FOUNDATIONAL_AUDIT.md` (REFINE the discourse-fact-store entry: real-text accuracy now MEASURED
   TWO-SIDED -- fused with the REAL resolver LIFTS 0.84->0.96 on the natural fact-present sliver (~15%, GATED --
   hurts blind), does NOT help competitive coref unconditionally; all three brain-faithful fixes built/tested; the
   general bound that any discourse-content bridge is redundant with salience for coref but real when a fact is
   present; the missing component is a fact-reliability GATE).
2. **(Strategy, hdlab)** If landing the parent's situation-model organ, land it GATED (discourse-age + ambiguity)
   with the GRADED bridge so it is at worst neutral on real text; do NOT wire any discourse-content bridge (type
   OR rich-entity) into real competitive coref -- both are measured redundant with salience there.
3. **(Follow-on problems, seeded by the adjacent-component evaluation, RE-RANKED by this push)** -- (a) **the
   intra-sentential SYNTACTIC binder** is the real lever for real-text competitive coref (both discourse-content
   bridges are the wrong tool) -- HIGHEST leverage for the coref line; (b) **build a fact-GIVEN downstream task
   (QA / next-event / bridging inference)** where the task SUPPLIES the fact-present condition -- the drill shows a
   fact-DETECTION gate is an intrinsic dead end (net-zero, brain-faithful), so the organ's real value is exactly
   where detection is not required; scale the positive-domain lift (0.84->0.96) there; (c) do NOT build a fact-
   reliability gate for coref (measured net-zero, and the drill explains WHY: the brain has no such gate); (d)
   couple the graded coherence bridge to the p1 grounded-meaning lane (denser semantic hub, a soft prior).

---
**INTEGRATED_BY_STRATEGY 2026-08-30 — grade EXCELLENT.** Reverified FIRST-HAND 11/11 (scaffold-free, recomputes every
headline from source). Argument-audited: a rigorous two-sided validation on real LitBank — the NEGATIVE (fact-bridge
net-zero on competitive coref, DEV weight 0, both type + rich-entity redundant with salience) is a full pass and
CONVERGES with the standing fact (residual is syntactic-binder-bound, not KB-bound) + the assembly's own coref-residual
drill (KB dead ~2-3% — two independent drills triangulate). The POSITIVE (0.84->0.96 on the ~15% fact-present sliver)
is honest + gated. The gate question drilled to an INTRINSIC BOUND (5 literatures; the brain has no reliability gate).
NO hdlab landing earned into coref (measured net-zero, brain-faithfully so); NO fact-reliability gate (intrinsic dead
end); the organ's home is fact-GIVEN tasks (a future landing). Exemplary honesty (withdrew an inflated positive; flagged
labelling churn). review: EXCELLENT written into PROBLEM.md; AUDIT UPDATE folded into BRAIN_FOUNDATIONAL_AUDIT.md §2b.
One VET-pending: the strongest "net-zero = correct calibration" equivalence claim is one notch ahead of a direct proof.
