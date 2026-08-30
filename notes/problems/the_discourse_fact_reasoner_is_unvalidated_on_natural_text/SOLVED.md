---
problem: the_discourse_fact_reasoner_is_unvalidated_on_natural_text
status: PARTIAL
bar: "PASSES only with ALL of: 1. A REAL-TEXT inter-sentential fact-decisive population (built in experiments/ from LitBank/real narrative): a reference (pronoun or definite description) resolvable ONLY by a fact stated earlier about a candidate (NOT by grammar/salience - filter those out, as the parent did), with self-EXTRACTED per-entity facts (no oracle, no gold leak). 2. The fact-store reader beats the fact-BLIND reader CI-separated on real text (the fact-blind graded resolver recomputed on the same population = the floor); the info-free twin (shuffled facts) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. 3. The graceful-degradation curve: accuracy vs the fraction of the deciding fact actually self-extracted (and/or KG coverage) - the honest real-world bound, with the dominant failure mode named (extraction miss / KG gap / no-fact-exists). 4. One-screen summary: population -> floor -> twin -> real-text lift -> degradation curve -> verdict. Heavy -> REMOTE. A rigorous NEGATIVE is a FULL PASS (e.g. 'on real narrative the fact store lifts fact-decisive reference +X CI-sep where the fact IS self-extracted [Y% of cases], but real coverage is Y% so the population-level lift is Z - the constructed 1.0 was an idealized-extraction artifact; the mechanism is real, the bound is extraction/coverage')."
result: "RIGOROUS NEGATIVE (a FULL PASS per the bar). On REAL LitBank person-reference competitive pronoun resolution (n=4023 TEST mentions over 50 held-out novels, SELF-EXTRACTED facts, real sparse CSKG, DEV/TEST split by document), the self-extracted discourse-fact bridge does NOT beat the fact-BLIND graded floor: the DEV-optimal bridge weight is ZERO (held-out DEV rejects it), and FORCED on it HURTS - copula-type bridge 0.783 and all-attribute bridge 0.680 vs the fact-blind FLOOR 0.8049 [0.758,0.846], both CI-separated BELOW (copula delta -0.022 [-0.037,-0.006]; naive -0.125 [-0.160,-0.092]). The mechanism carries REAL but weak signal (it beats its info-free shuffled twin +0.046 [+0.021,+0.072] ABOVE) - it is simply swamped by structural salience and too RARE. The constructed 0.998 is an idealized-extraction + exact-KG artifact: the deciding self-extracted type-fact->verb bridge exists for the gold in only ~7% of references and the pronoun verb is in the sparse KG only ~17% of the time; the controlled degradation curve predicts ~0.60 at real coverage (near the constructed floor 0.55). BEST FAITHFUL SHOT: the two tractable brain-faithful fixes (graded distributional bridge; ambiguity gate) lift verb-visibility 3.8x (17%->67%) and gold-side bridge availability 2.1x (17%->35%) and cut the gate's harm 4x, but STILL do not beat the floor - the residual deep wall is ENTITY-SIDE (real narrative person-entities rarely carry a self-extracted type at all). Scorer = argmax==gold link accuracy, per-doc bootstrap (docs = resampling unit)."
floor: "The fact-BLIND graded resolver (hdlab.graded_competition additive cue net, DEV-tuned weights) recomputed on the SAME real population: person-reference 0.8049 [0.7582,0.8455] (n=4023); full competitive set 0.7752 [0.7286,0.8160] (n=4693). The fact_store arm is CI-separated BELOW it at every positive bridge weight, and the DEV-optimal weight is 0.0 (== the floor exactly)."
controls: "(1) INFO-FREE TWIN (self-extracted attributes SHUFFLED across the item's candidates) -> the real bridge beats the twin +0.046 [+0.021,+0.072] ABOVE (the bridge carries genuine identity signal, not a hollow shape artifact) YET both lose to the floor -> the real signal is swamped. (2) DEV-REJECTION (held-out DEV bridge-weight sweep) -> optimal weight 0.0 for naive, copula, graded, AND graded+gated -> no positive weight helps on held-out data. (3) AMBIGUITY GATE (FIX 3: fire only when the structural margin is low) -> cuts the harm 4x (-0.099 ungated -> -0.024 gated) but does NOT recover a positive lift. (4) GRADED DISTRIBUTIONAL BRIDGE (FIX 1, the ATL-faithful PPMI+SVD coherence) -> lifts verb-visibility 0.175->0.671 and gold-side availability 0.167->0.351, still BELOW floor -> the KG-sparsity wall is real but not the deep one. (5) COVERAGE FUNNEL + FLOOR-ERROR DECOMPOSITION -> on the references where structure/salience FAILS (n=785, the cases needing help) the self-extracted gold type-fact->verb bridge exists in only 5-11%; DOMINANT bottleneck = KG-vocab (17%) then, once graded, ENTITY-SIDE type-fact absence. (6) DEGRADATION (constructed harness, extraction-coverage + KG-coverage knobs) -> monotone floor->0.998, and real-text coordinates land at ~0.60 (near floor) -> the 0.998 is idealized extraction + exact KG. (7) NO-LEAK self-test -> a fact at sent s is invisible to a query before sent s."
files_changed: "experiments/exp_discfact_realtext_validation_v1.py (the honest real-text measurement: coverage funnel + population arms + floor-error decomposition + fact-decisive conditional), experiments/exp_discfact_realtext_degradation_v1.py (the controlled degradation curve connecting the constructed 0.998 to the real-text floor and locating real text on it), experiments/exp_discfact_realtext_fidelity_fixes_v1.py (the best faithful shot: graded distributional bridge + ambiguity gate + residual-bottleneck decomposition), verification/test_discfact_realtext.py (8/8 scaffold-free witness), notes/problems/the_discourse_fact_reasoner_is_unvalidated_on_natural_text/{SOLVED.md, research_realtext_reference_brain_mechanism_2026-08-29.md}. NO hdlab/ write (Q111). Reuses the LANDED harness (build_instances, graded_competition, DiscourseFactStore, the graded PPMI+SVD bridge)."
reverify: ".venv/Scripts/python.exe verification/test_discfact_realtext.py"
---

# What was built and measured

The brief asked: confront the discourse-fact bridge -- graded EXCELLENT on a CONSTRUCTED population (0.998 vs a
0.504 fact-blind floor) with IDEALISED extraction (clean IS-A facts handed in) + EXACT KG edges -- with REAL
narrative, where the reader must SELF-EXTRACT the per-entity facts and the KG is patchy. I built exactly that
measurement, then (per the owner's push and the standing protocol) drilled the wall it exposed with brain
research and gave the brain-faithful fix its best shot. **A rigorous NEGATIVE is a FULL PASS -- and that is what
the disk gives, cleanly and in triplicate.**

## The measurement (bar items 1-2): the self-extracted bridge does NOT survive real text
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

# What I did NOT establish (and would withdraw first if wrong)
1. **This is a NEGATIVE, and I would withdraw first any reading of it as "the mechanism is worthless."** It is
   NOT: the bridge beats its info-free twin (+0.046 CI-sep) -- the reading-built binding is real. The claim I DO
   make is narrow and quantified: on real narrative, self-extracted facts do not lift competitive pronoun
   resolution because (a) fact-decisive reference is rare (~7% of references have the gold's self-extracted
   type-fact bridging the verb) and (b) structural salience already resolves ~80%. Withdraw the strong version
   ("useless") before the weak version ("does not lift real coref at current extraction/KG fidelity").
2. **FIX 2 (rich entity extraction) is NAMED and its NECESSITY is measured (gold-side availability < 35%), but
   NOT BUILT.** I did not show that a richer entity model recovers the lift -- only that it is the residual
   bottleneck. If FIX 2 turns out to also fail (e.g. because the fact-decisive rate is intrinsically ~7%), the
   honest ceiling is even lower; that is the first thing to test next.
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

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **Situation-model RESOLUTION / discourse-fact store (REFINE the existing entry).** The parent added this organ
  with a PINNED computation (Garrod-Sanford; Kintsch CI) proven CI-separated on CONSTRUCTED data, and flagged
  "real-text accuracy unmeasured" as the remaining deviation. **That deviation is now MEASURED and BOUNDED:** on
  real LitBank narrative the self-extracted bridge does NOT beat the fact-blind floor (DEV-optimal weight 0;
  forced on it hurts CI-separated), because (a) fact-decisive reference is rare (~7% of references) -- partly a
  property of language (Winograd/GAP/KnowRef are hand-built), and (b) the two OUR-INVENTION deviations bite:
  the sparse boolean KG (17% verb coverage; a graded distributional space lifts it to 67%) and the single-copula
  type extraction (gold-side availability < 35% even with the dense space -- the DEEP residual wall). The organ's
  computation stays PINNED and real (it beats its info-free twin); the real-text CAPABILITY is bounded near the
  floor by entity-side extraction + KG density. The three brain-faithful fixes (dense graded knowledge; rich
  multi-attribute entity extraction; ambiguity gate) are PINNED to evidence (Lambon Ralph 2017; Gernsbacher/
  Metusalem 2012; Haviland-Clark 1974); FIX 1 + FIX 3 built here, FIX 2 named as the next problem.

# ADJACENT COMPONENTS -- capabilities / limitations / brain-foundational status (seeds the next problems)
1. **[THE DEEP WALL -- FIX 2] Entity/type EXTRACTION (the reading-built half).** CAPABILITY: the parse yields
   copula IS-A + nominal heads; the store reads them off. LIMITATION (measured): real person-entities carry a
   self-extracted type usable by the bridge in < 35% of references (they are named/pronominalised, not typed);
   the copula IS-A rate is ~600 facts across 100 novels. BRAIN STATUS: the brain builds RICH multi-attribute
   entity models (Gernsbacher structure-building; concept cells wired to hundreds of associations; Metusalem 2012
   event knowledge) -- our single-copula-noun type is an OUR-INVENTION placeholder at the FLOOR of fidelity.
   OPTIMIZATION / NEXT PROBLEM: build a rich entity model (accumulate the entity's action history, appositives,
   adjectival/role descriptions, and the p1 grounded-meaning vector), and re-measure -- HIGH leverage, and it is
   the true bottleneck this problem uncovered.
2. **[FIX 1 -- PARTLY ADDRESSED] The world-knowledge base (the generic bridge).** CAPABILITY: the static CSKG
   supplies role->action edges; the graded PPMI+SVD space (built here from its co-occurrence) lifts verb-
   visibility 17%->67%. LIMITATION: still sparse (67%, not the brain's ~universal coverage); the space is
   KG-derived, not coupled to the substrate's grounded distributional-meaning (p1) lane. BRAIN STATUS: now
   DISTRIBUTIONAL/graded (ATL-faithful) rather than boolean. OPTIMIZATION: couple the coherence score to the p1
   representation lane (the deeper fidelity move the parent also named) -- a denser, grounded semantic hub.
3. **[FIX 3 -- BUILT] The ambiguity/coherence gate.** CAPABILITY: firing the bridge only on low structural margin
   cuts its harm 4x. LIMITATION: it prevents damage but cannot ADD signal the entity side lacks. BRAIN STATUS:
   PINNED (Haviland-Clark bridging cost; concept-cell reactivation only on demand). OPTIMIZATION: a graded
   coherence-driven gate (Kehler et al. 2008) rather than a margin threshold.
4. **The structural resolver (`hdlab.graded_competition`) is EXCELLENT and DOMINATES on real text.** CAPABILITY:
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
- **The real-text value of the organ is on the INTER-SENTENTIAL, fact-PRESENT downstream tasks** the parent named
  (bridging QA, next-event prediction, ToM) where the deciding fact IS stated -- NOT competitive coref, where the
  fact-decisive rate is ~7% and salience dominates.
- **File FIX 2 (rich multi-attribute entity extraction) as the next problem** -- it is the measured deep wall, and
  it is the brain-faithful lever (rich entity models) with the most leverage over this whole line.

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
-- so there is usually no fact to look up. The brain gets around this by building a rich mental picture of each
character; our one-word-type reader does not. So the honest result: the reading-reasoning step is REAL (it beats
every scrambled version of itself), but on real prose it is rare and swamped, and the near-perfect lab score came
from handing it clean facts and a perfect knowledge book. The fix is a richer character model -- the next problem.

## QUESTIONS
One labelling judgement for you, as with the parent. I marked this **PARTIAL**, not SOLVED and not REFUTED. The
MEASUREMENT the brief asked for is COMPLETE and rigorous (population built, self-extracted, floor recomputed,
twin run, degradation curve, dominant failure named) and its answer is a quantified NEGATIVE -- which the bar
explicitly counts as a FULL PASS. I avoided **SOLVED** because "SOLVED" reads as "the real-text reading skill
works" (it does not -- it is bounded at the floor), and I avoided **REFUTED** because the mechanism is genuinely
real (it beats its info-free twin) and a brain-faithful route to recover it (rich entity extraction, FIX 2) is
identified though not built. If you would rather it read as SOLVED (measurement complete, negative result) or
REFUTED (the real-text capability claim is dead), the content is identical.

## NEXT STEPS
1. **(Strategy)** Re-verify the witness (`verification/test_discfact_realtext.py`, 8/8). Fold the AUDIT UPDATE
   into `BRAIN_FOUNDATIONAL_AUDIT.md` (REFINE the discourse-fact-store entry: real-text accuracy now MEASURED and
   BOUNDED near the floor; three brain-faithful fixes named, two built).
2. **(Strategy, hdlab)** If landing the parent's situation-model organ, land it GATED (discourse-age + ambiguity)
   with the GRADED bridge so it is at worst neutral on real text; do NOT wire the boolean bridge into real coref.
3. **(Follow-on problems, seeded by the adjacent-component evaluation)** -- (a) **FIX 2: rich multi-attribute
   entity extraction** (the measured deep wall -- accumulate action history + appositives + p1 grounded meaning
   per entity, re-measure the bridge) -- HIGHEST leverage; (b) validate the organ on an inter-sentential
   fact-PRESENT downstream task (bridging QA / next-event) where the deciding fact IS stated -- the mechanism's
   real domain; (c) couple the graded coherence bridge to the p1 grounded-meaning lane (denser semantic hub).
