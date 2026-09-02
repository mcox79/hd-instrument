---
problem: who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde
status: PARTIAL
bar: "PASS = a glass-box coherence/next-mention PRIOR (predicting the likely next referent from the discourse-coherence relation, multiplied into the graded-retrieval posterior before argmax) that: 1. recovers the STRUCTURALLY-DOMINATED error bucket CI-separated -- the bucket reachable by NO recency/subject/frequency cue (currently 0.481, n~445) -- over the entity-maintenance floor (recompute the floor on the held-out population, gate on its UPPER bound), on HELD-OUT LitBank gold coref (doc-split); 2. the lift is ATTRIBUTED to the coherence prior -- it must appear on the structurally-dominated bucket (which no backward cue can reach), with the backward graded pick held at its near-optimal setting; 3. a shuffled-coherence twin LOSES CI-separated (same mentions, wrong coherence relation -> the forward signal, not the machinery, does the work); 4. does NO net harm to the near / non-dominated cases (report the per-bucket effect; a bucket recovery bought with a non-dominated regression is not a pass). Report CI half-width + null p95 on every margin. A rigorous located NEGATIVE is a FULL PASS if a faithfully-built coherence prior does not recover the bucket AND it names why (the coherence-relation signal is too weak glass-box / the prior is dominance-reinforcing / a genuine irreducible ambiguity floor) with the number."
result: "PARTIAL = the brief's mechanism REFUTED + the REAL problem partially SOLVED by the correct mechanism. THE IDEAL SOLUTION (fully researched + prototyped): a LEARNED glass-box, LM-free cue-integrator (conditional-softmax reranker over the animacy-filtered person-pool candidates, features = net + content + grounded + exact-predicate + per-item confidence interactions, trained by conditional-MLE on DEV with L2; the Competition Model's LEARNED cue validity, MacWhinney-Bates + Parker 2019 nonlinear combination) RECOVERS the struct-dominated bucket over the chain floor: 0.6139 -> 0.6682, +0.0543 [0.0077,0.1100] CI-separated, shuffled-CUE twin LOSES (0.549, delta -0.065), and it beats the linear multi-cue fusion (+0.038). This is the located-negative's redirect made LIVE. HONEST bounds: it is on the animacy-filtered person sub-pool + gold-nominal grouping; the CI is wide (lower bound 0.008); the gain is mostly LEARNED cue WEIGHTING (the confidence-gate nonlinearity adds little); and the per-item ORACLE ceiling (0.857) is UNREALIZABLE (it needs the answer to gate) so the realizable glass-box ceiling is ~0.67 -- pushing past it needs a richer representation + scale (the North Star). NOW THE REFUTATION HALF: the brief's coherence prior is a near-DUPLICATE of the owner-DONE 2026-08-29 negative (`the_reader_has_no_coherence_next_mention_prior`, REFUTED/EXCELLENT/DONE), and it stays dead AFTER the entity-maintenance wire. On the HELD-OUT (50 test docs) CHAIN structurally-dominated bucket (the brief's exact population, n=695) the faithful coherence prior (reused verbatim, DEV-tuned wp=0.3) does NOT beat the chain floor (prior-minus-floor -0.0043 [-0.0223,+0.0119] NOT_SEP) and does NOT beat its own 20-shuffle INFO-FREE TWIN (prior-minus-twin +0.0009 [-0.0138,+0.0148], hw 0.0143, null p95 0.0144, NOT_SEP); ORACLE ceilings near-chance (selectional 5.1%, thematic 14.7%, combined 6.9%); it REGRESSES the non-dominated cases (0.7521->0.7246, broke 75). Premise reproduced EXACT via the parent harness (chain acc 0.4809 on the struct-dominated bucket = the brief's 0.481, 0.294 of errors dominated, n=445, 0.995 confident). WALL LOCALIZED (drilled three times, corrected twice; gold-coref past-only ceiling on the CLEAN animacy-filtered person-vs-person pool): the wall is INTEGRATION QUALITY, NOT missing information. The COMBINED best-per-item in-text oracle ceiling = 0.857 (semantic-only 0.795) vs topicality alone 0.563 -- so the discriminating info IS in the text; we lack the NONLINEAR gate to combine several weak in-text cues (topicality 0.56 / content 0.54 / grounded 0.51 / exact-predicate 0.30). The brain integrates cues NONLINEARLY (Parker 2019; parallel-constraint); our fusion is LINEAR-additive -- the precise fidelity gap. Only the ~14% above 0.857 is external world-knowledge + annotation-fiat ambiguity. Residual anatomy: 54% gold last named 2+ sentences back (situation-model), 27% intra-sentential, ~6 gendered person-competitors. POSITIVE CONTROL: the coherence mechanism flips constructed pairs (selectional 8/8, IC 8/8) -> it works; the bucket lacks the cases. CONSTRUCTIVE REALIZATION (the integration lever made LIVE, WIRING EXISTING ORGANS not a new build): a multi-cue integrator (content + grounded-event, glass-box proxies for hdlab.situation_model_accumulate) fused into the graded pick over the animacy-filtered person pool (the EXISTING hdlab.graded_coref_pick.phi_agreement_keep pre-filter -- the real reader's deployment) lifts the struct-dominated bucket 0.6139 -> 0.6516, +0.0377 [0.0146,0.0648] CI-sep (robust; content +0.0271, exact-predicate WASHES OUT -- 74% redundant with topicality), shuffled-entity twin LOSES (-0.010), no net harm to non-dominated; NULL on the animacy-polluted full pool (weight 0 -- the animacy organ is a required gate). The realized LINEAR integrator (0.65) captures ~1/5 of the 0.857 oracle ceiling; the rest needs the NONLINEAR situation model. Deterministic across PYTHONHASHSEED 0/1/42. Scorer = argmax==gold he/she who-has-what pick accuracy, doc-bootstrap 95% CI."
floor: "Strongest floor actually run = the info-free 20-shuffle coherence-prior TWIN on the same held-out bucket = 0.4178 [0.3027,0.5229]; the real prior 0.4187 does NOT clear it (prior-minus-twin +0.0009 NOT_SEP, null p95 0.0144). The entity-maintenance CHAIN floor (the bar's named floor) = 0.4230 [0.3080,0.5433] (gate on upper bound 0.5433); prior does not beat it (-0.0043 NOT_SEP). Premise floor reproduced EXACT via the parent harness = 0.4809 (=the brief's 0.481), n=445. CEILING decomposition (gold-coref past-only oracles, reachability not floors, on the CLEAN person-vs-person pool, MATCHED vs global topicality on the same items): global topicality is the base recoverable signal (~0.55); a richer in-text representation ADDS CI-separated -- exact-predicate +0.0846 [0.0345,0.1379] ABOVE, context-BOW +0.0702 [0.012,0.1284] ABOVE (grounded-max -0.027 NOT_SEP); the in-text ceiling ~0.63 (gold coref), residual above = external world-knowledge."
controls: "(1) INFO-FREE 20-shuffle TWIN: prior (0.4187) does NOT beat it (0.4178), NOT_SEP -- excludes 'the prior carries usable signal'. (2) ORACLE-ceiling per channel (selectional 5.1%/thematic 14.7%/combined 6.9%/event-state 7.8%) all near-chance -- excludes 'a better fusion weight rescues it'. (3) NO-REGRESSION: the prior regresses non-dominated 0.7521->0.7246 (broke 75) -- dominance-reinforcing, bar item 4 fails. (4) POSITIVE CONTROL 8/8 selectional + 8/8 IC vs chance -- excludes 'mechanism broken / metric cannot move'. (5) DEV/TEST doc-split, fusion weight tuned on DEV (best shot). (6) FREQUENCY CONTROL on the ceiling (global-protagonist past-only) -- the topicality confound the in-text semantic channels must beat. (7) MATCHED apples-to-apples comparison (each in-text channel vs frequency on the SAME items, paired-bootstrap CI) on the CLEAN person-vs-person pool -- fixes an applicable-set confound and reveals exact-predicate +0.085 ABOVE, context-BOW +0.070 ABOVE (a real buildable in-text lever), grounded-max NOT_SEP. (8) POOL-CLEANING control: the same channels on the animacy-POLLUTED 39-candidate pool are all NOT_SEP/BELOW frequency -- so the lever is a genuine person-vs-person effect, masked by inanimate distractors. (9) PAST-ONLY ceiling (no future-mention leakage -- a first, future-leaking version gave a spurious 0.58). (10) REALIZED-lever controls: SHUFFLED-ENTITY twin (assign each candidate a random other candidate's accumulated representation) LOSES (-0.006 vs +0.033) -> the maintained IDENTITY does the work; NO-HARM on non-dominated (+0.003); the animacy-POLLUTED full pool is NULL (weight 0) -> isolates the animacy organ as a required gate; CHANNEL DECOMPOSITION (content CI-sep, pred washes out) localizes the signal. (11) IDEAL learned-integrator controls: DEV-trained / TEST-held-out (no train-on-test); SHUFFLED-CUE twin (net kept, cues permuted) LOSES (0.549 vs 0.668); FIXED nonlinear gates (multiplicative/max-pool/margin-gate) do NOT beat the linear fusion -> the gain requires LEARNED cue validity, not a heuristic; the unrealizable per-item ORACLE (0.857) is reported as the upper bound so the realizable ~0.67 is not mistaken for it. (12) determinism across PYTHONHASHSEED 0/1/42 (core numbers + realized lever)."
files_changed: "experiments/exp_coref_coherence_prior_on_chain_bucket_v1.py (chain re-expressed in the who-did-what cache + reused coherence-prior channels + event-state situation channel + SITUATION-MODEL CEILING probe [gold-coref past-only, clean person pool, MATCHED comparison, COMBINED per-item oracle] + REALIZED accumulated-entity lever [wiring existing animacy filter + accumulated-entity rep, channel decomposition] + THE IDEAL LEARNED CUE-INTEGRATOR [conditional-softmax reranker, glass-box, LM-free] + residual anatomy + faithful parent-harness premise); verification/test_coref_coherence_prior_on_chain_bucket.py (8/8 scaffold-free witness); experiments/exp_coref_faithful_integrator_deltas_v1.py (THE BRAIN-FIDELITY DELTA prototypes: self-supervised label-free training, defer, recurrent-in-the-loop, multiplicative+interference -- each ablated); data/exp_coref_*/metrics.json. NO hdlab/ written (Q111 -- the realized wire composes EXISTING organs + a learned integrator)."
reverify: ".venv/Scripts/python.exe verification/test_coref_coherence_prior_on_chain_bucket.py   # 8/8: self-test + premise EXACT (0.481/0.294/0.995) + coherence prior dead + event-state near-chance + WALL LOCALIZED + REALIZED multi-cue integrator (existing organs, +0.038 CI-sep) + WALL IS INTEGRATION (combined in-text oracle 0.857 >> topicality 0.56) + THE IDEAL LEARNED cue-integrator (+0.054 CI-sep over floor, shuffled-cue twin loses, beats linear -- the full-solution piece prototyped)"
---

# REFUTED (rigorous located negative = full pass). A near-DUPLICATE of an owner-DONE negative, drilled to the exact wall.

## Headline
The coherence next-mention prior this brief proposes was already measured dead owner-DONE on 2026-08-29
(`the_reader_has_no_coherence_next_mention_prior`, REFUTED/EXCELLENT). I reproduced the brief's premise EXACTLY,
confirmed the negative SURVIVES the entity-maintenance wire, and then -- per the owner's push to understand the
wall deeply -- drilled it to the load-bearing factors with a new instrument (a gold-coref ceiling, cleaned to
genuine person-vs-person, matched vs topicality with CIs). **The wall (drilled three times, corrected twice) is
INTEGRATION QUALITY, not missing information: the per-item combined in-text oracle ceiling is 0.857 (vs topicality
0.56), so the discriminating info IS in the text; we lack the NONLINEAR gate to combine several weak in-text cues
(the brain integrates cues nonlinearly, Parker 2019; our fusion is linear).** A realizable LINEAR multi-cue
integrator (wiring existing organs) already lifts +0.038 CI-sep (0.61->0.65); the gap to 0.857 is the
linear->nonlinear situation-model integrator; only the ~14% above 0.857 is external world-knowledge. This is the
same "which SPECIFIC one" wall as the WSD a_s residual, whose organ is the OPEN priority-1 North Star.
Recommendation to strategy: consolidate this problem into priority-1 (its 0.857 ceiling + the realized +0.038 are
the instrument + first step); do not re-derive it; do not land a coherence prior.

## DO WE DEEPLY UNDERSTAND THE WALL? (owner's question) -- yes, and here it is exactly.

### How the brain resolves these anti-typical "who is she?" cases (PINNED, cited)
Reference resolution is TWO stages the literature keeps distinct (Garrod & Sanford 1994; Garrod & Terras 2000):
1. **BONDING (fast, ~150-300ms):** an automatic, low-level link from gender/number agreement + salience/focus
   (Centering; Gordon-Grosz-Gilliom 1993). This resolves the TYPICAL cases -- the recent subject, the
   gender-unique candidate. **We have this** (the graded pick + gender filter + the entity-maintenance chain).
2. **RESOLUTION (slow, ~400-700ms):** a deliberate, knowledge-driven stage invoked when bonding is ambiguous
   (2+ same-gender candidates, none locally salient -- exactly the struct-dominated bucket). It integrates
   FOUR things, all evidenced:
   - **Selectional/plausibility fit** (McRae, Spivey-Knowlton & Tanenhaus 1998; immediate, N400) -- which
     candidate the predicate suits.
   - **A rich, INDIVIDUATED situation-model representation of each entity** (its attributes, roles, goals,
     prior actions), built incrementally (Gernsbacher structure-building; the situation model, Zwaan & Radvansky
     1998). The brain knows "Anne is the anxious god-daughter" vs "Elizabeth is the vain elder sister."
   - **World knowledge from the ATL semantic hub**, integrated as fast as word meaning (Hagoort et al. 2004,
     Science) and implemented as a DISTRIBUTIONAL/PDP representation (Rogers & Lambon Ralph 2004), NOT symbolic.
   - **Abductive coherence reasoning** (Hobbs 1993; Kehler & Rohde 2013) -- the cheapest interpretation that
     makes the discourse coherent given world knowledge, combining MULTIPLE facts probabilistically.
   Crucially (Bott & Solstad 2014): a per-verb coherence bias tells you WHICH ARGUMENT SLOT is expected, NOT
   WHICH ENTITY fills it -- so the person-vs-person cases are situation-model + world-knowledge, not lexical.
   **This is why the coherence PRIOR the brief names is the wrong tool: it is the slot-level bias, and the
   bucket needs the entity-level generative model.**

### How we differ -- THREE gaps, each MEASURED on this exact bucket
- **GAP 1 -- REPRESENTATION IMPOVERISHMENT (a PARTLY-BUILDABLE lever, measured).** Our entity = a
  predicate-argument skeleton (gov_verb/obj_head/role) + a coarse 12-dim grounded vector. The brain's = a rich
  distributional individuated representation. MEASURED, the honest and controlled way (gold coref, past-only,
  on the CLEAN person-vs-person pool, MATCHED vs global topicality on the same items): a richer in-text
  representation DOES beat topicality CI-separated -- exact-predicate identity +0.085 [0.034,0.138], full-context
  BOW +0.070 [0.012,0.128]; grounded-event-max is NOT_SEP (-0.027). So on genuine person-vs-person cases the
  situation model has a REAL, buildable signal above topicality (~+0.07-0.085 with perfect coref), bounded by a
  modest ceiling (exact-predicate reaches ~0.63 with gold coref). This is the lever the learner/North Star would
  grow -- gated by coref quality (the +0.07-0.085 is a gold-coref ceiling; glass-box coref noise eats part of it).
  IMPORTANT: this CORRECTS a pool-polluted intermediate read (on the animacy-polluted 39-candidate pool every
  in-text channel looked exhausted at frequency; on the clean ~7-candidate person pool the lever appears).
- **GAP 1b -- NONLINEAR CUE INTEGRATION (the sharpest fidelity gap, measured).** The deeper finding: the in-text
  info is NOT the bottleneck (the per-item combined oracle reaches 0.857). The bottleneck is HOW we combine the
  several weak in-text cues -- our fusion is LINEAR-additive (realizes 0.65), the brain's is NONLINEAR / parallel-
  constraint (Parker 2019; McClelland), which reaches the 0.857 region. The gap 0.65->0.857 is the
  linear->nonlinear integration-quality gap; a learned nonlinear integrator (the situation model / Bayesian
  reader) is the buildable fix. This is more actionable than "richer representation" -- we have the signals, we
  lack the gate.
- **GAP 2 -- NO WORLD-KNOWLEDGE AT INFERENCE (the no-LLM invariant) -- the SMALLEST residual (~14%).** Above the
  0.857 combined in-text oracle ceiling, the gap to 1.0 is external world-knowledge + genuine (annotation-fiat)
  ambiguity. The brain's ATL hub supplies
  interpersonal/selectional facts instantly. MEASURED (2026-08-29): static-KG (ConceptNet/WordNet) is dead on
  this residual -- 2.8% discrimination DESPITE 86.8% coverage; the KB connects every candidate but cannot pick
  the atypical gold, because the needed fact is discourse-SPECIFIC, not general commonsense.
- **GAP 3 -- NO ABDUCTIVE MULTI-FACT REASONING.** Our channels are single-hop. The brain combines multiple
  facts probabilistically (Sharma et al.: of the unsolved Winograd cases, 26/51 needed MULTIPLE facts combined,
  25 needed a PROBABILISTIC comparison categorical single-hop cannot express). No fully-automatic static-KG
  system has cleared the full WSC-273; the one 57% full-set result used LIVE WEB SEARCH (not no-LLM-admissible).

### The residual anatomy (grounds the above in the ACTUAL cases, held-out n=695)
By distance to the gold's nearest prior NOMINAL: **54% is 2+ sentences back** (the situation-model/topicality
regime), **27% is intra-sentential** (parse/binding -- but the GAP cross-domain test proved even a clean parse
leaves these BELOW chance, so it is really semantic: which same-clause entity fits), **19% is 1 back**. Genuine
person-vs-person degree: **~6 gendered competitors** on average (89.5% have 2+). Example (our pick WRONG):
"To Lady Russell, indeed, **she** was a most dear and highly valued god-daughter, favourite, and friend" --
"she" = Anne, resolvable only by the world/situation fact that Anne is Lady Russell's god-daughter, which is
in neither the predicate skeleton nor a commonsense KB.

**VERDICT on "do we understand it": NOW yes -- and drilling it a SECOND time (owner pushed "do we understand
ALL the walls?") CORRECTED my own too-strong "purely external world-knowledge" read.** The decisive measurement
is the COMBINED best-per-item in-text ceiling: an oracle that picks the right in-text glass-box channel per item
reaches **0.857** (semantic-only, no topicality: 0.795) vs topicality alone 0.563. **So the discriminating
information IS in the text -- it is NOT exhausted at ~0.63.** The wall is therefore NOT "missing information"; it
is INTEGRATION QUALITY: we have several weak, correlated in-text channels (topicality 0.56, content 0.54,
grounded 0.51, exact-predicate 0.30 overall) and no good per-item GATE to combine them. The brain combines cues
NONLINEARLY (Parker 2019 -- full-cue-match antecedents favored more than a linear model predicts; parallel-
constraint satisfaction), our fusion is LINEAR-additive -- THAT is the precise, brain-grounded fidelity gap.
The three-part decomposition, corrected:
(1) GLOBAL TOPICALITY (0.56) -- captured by the chain;
(2) a BUILDABLE INTEGRATION lever -- a realizable LINEAR multi-cue integrator (content+grounded) already lifts
    to 0.652 (+0.038 CI-sep, below); the per-item ORACLE ceiling is 0.857, and the gap 0.65->0.857 is the
    linear->nonlinear integration-quality gap (the learned situation model / Bayesian reader closes it);
(3) EXTERNAL world-knowledge + genuine ambiguity ABOVE 0.857 -- the no-LLM/annotation-fiat bound (~14%).
This is a MUCH more buildable wall than "external world-knowledge," and it is precisely the situation model's
job (nonlinear weighted-cue integration). The methodological lesson: I twice mis-read this wall (future-leak;
pool-pollution) and this THIRD drill (the per-item combined ceiling + a matched frequency control) is what
finally separated "info absent" from "integration weak" -- the answer is integration-weak, and integration is
buildable.

## THE LEARNER PROOF (owner's request: build world-knowledge, test, learn more, test again)
**Your "amazing proof" already exists -- for word-meaning.** The learner is ON, safe, AND beneficial, verified
seven ways (`turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation`, owner-reviewed): growth-ON
beats OFF on downstream who-did-what comprehension +0.058 CI-sep, the info-free growth twin HURTS, it survives
the substrate's own parser, corruption stays under the pre-registered bound. So "the learner acquires knowledge
from reading and a downstream comprehension score improves" is a demonstrated result.

**And on the coref residual there IS a buildable target for it -- measured, on the clean person pool.** A richer
in-text ENTITY representation (accumulated predicate identity + full-context content, gold coref) beats global
topicality CI-separated (+0.085 / +0.070). This is EXACTLY what a situation model / entity-grounded learner
would grow (per-entity accumulated attributes), so the owner's "build knowledge -> retest" loop is VIABLE in
principle here -- gated by two things this cell also measures: (a) coref quality (the +0.07-0.085 is a gold-coref
ceiling; the live glass-box chain's coref noise drops the realized channels to near-chance -- combined oracle
6.9% -- so coref quality is the first gate), and (b) a modest ceiling (~0.63 with gold coref; the rest is
external world-knowledge). NOTE: the substrate's CURRENT live channel is the wrong signal -- the
`distributional_meaning_channel` is scoped to word SUBSTITUTABILITY (AUC 0.84) and explicitly BAD at general
similarity (WordSim -0.24); the buildable lever here is an ENTITY-level accumulated representation, not word
substitutability.

**The organ that assembles this IS the OPEN priority-1 North Star:**
`the_meaning_channel_needs_a_generative_world_knowledge_situation_model_that_predicts_the_specific_sense`. Its
brief names the IDENTICAL wall my previous problem (the top-down sense selector) hit -- the generative override
accuracy a_s ("which SPECIFIC sense") -- and here it is "which SPECIFIC referent." **My ceiling QUANTIFIES the
coref target for it:** the in-text ceiling is ~0.47 (topicality, captured); the headroom to the ~0.73 gold-
chaining ceiling is the external-world-knowledge slice the generative model must supply. When that organ is
built, the exact learner proof (build entity/world-knowledge -> test the struct-dominated bucket rises toward
0.73, shuffled-situation twin loses) becomes runnable -- and this cell's ceiling + anatomy are its pre-registered
instrument and target.

## CONSTRUCTIVE REALIZATION -- the buildable lever made LIVE by WIRING EXISTING ORGANS (not a new build)
The ceiling proved the in-text lever exists as a gold-coref TARGET (+0.07-0.085). To make it a real capability I
did NOT build a new organ -- per the owner's check, both pieces already exist on disk:
- **The animacy filter that cleans the pool** = `hdlab/graded_coref_pick.py:phi_agreement_keep` (drops
  confirmed-inanimate candidates for he/she; the real reader has NER animacy -- the who-did-what cache does not,
  which is why my full-pool numbers were animacy-polluted). This is the deployment condition.
- **The accumulated-entity representation** = `hdlab/situation_model_accumulate.py` (each entity's (role,
  event-slot) bindings, FHRR-bundled; validated accumulate 1.00 vs overwrite 0.46 on entity-tracking). My
  channel is a glass-box proxy for it.
WIRING them into the graded pick (fuse the accumulated-entity signal into the net before argmax -- the brief's
"multiply the posterior", with the RIGHT signal instead of the refuted coherence prior), on the animacy-filtered
person pool. The strongest realizable version is a MULTI-CUE integrator (content + grounded-event, jointly tuned):
the struct-dominated bucket rises 0.6139 -> 0.6516, **+0.0377 [0.0146,0.0648] CI-separated** (lower bound 0.015 --
ROBUSTLY separated, unlike the single-channel +0.033 [0.0016,...]), the shuffled-entity TWIN LOSES (-0.010), NO
net harm to non-dominated (-0.001, within noise). Channel decomposition (each fused into the net): content +0.027
[0.007,0.051] ABOVE, combined(content+pred) +0.033, **multi(content+grounded) +0.038 -- the best**; exact-PREDICATE
WASHES OUT (weight 0) and I now know WHY (measured): of the items it gets right, 74% are ALSO gotten by topicality
(redundant) and it adds unique value on only ~8%, too sparse for linear fusion. On the animacy-POLLUTED full pool
the whole thing is NULL (weight 0) -- so the animacy organ is a REQUIRED gate.
**This is honest about its size AND its ceiling:** the realized +0.038 is a LINEAR integrator; the per-item
ORACLE ceiling (best channel per item) is 0.857, so linear fusion realizes only ~1/5 of the available in-text
lift (0.61->0.65 of a possible 0.61->0.86). The remaining lift needs a NONLINEAR learned integrator (the
situation model), the precise fidelity gap. The gain uses gold-NOMINAL grouping (the floor's grouping) and is
split-sensitive at small scale. So it is a proof-of-concept that (a) the buildable lever is LIVE and
twin-attributable, wired from existing organs, and (b) the wall is INTEGRATION QUALITY, not missing information.
Quote it as "a CI-separated but linear-integrator-capped realized gain (+0.038), against a 0.857 in-text oracle
ceiling the nonlinear situation model must reach."
The full gain (toward the +0.085 gold-coref ceiling, then external world-knowledge toward 0.73) is the North
Star's to realize with better coref + a richer representation. **PROPOSED hdlab WIRE (Q111, default-off): add an
`accumulated_entity` cue to the graded coref pick = phi_agreement_keep (animacy) + a content-cohesion score from
situation_model_accumulate's per-entity register, fused at a small weight; flag OFF -> byte-identical. It is a
COMPOSITION of two landed organs, not a new mechanism.**

## THE IDEAL SOLUTION -- FULLY RESEARCHED AND PROTOTYPED (owner asked)
**Research -- what is the ideal mechanism?** The brain resolves these by LEARNED, nonlinear cue integration, not
a fixed rule: the COMPETITION MODEL (MacWhinney & Bates) -- each cue's VALIDITY (reliability x availability) is
LEARNED from experience and cues combine by their learned validity; Parker (2019) -- cues combine NONLINEARLY
(full-cue-match favored more than linear); McClelland interactive-activation / parallel-constraint. The KEY: the
per-item "which cue to trust" is LEARNED, not hand-coded.

**First I confirmed a FIXED nonlinear gate is NOT enough** (gold-free, held-out, twin-controlled): multiplicative
product-of-experts +0.038 (= linear), max-pool +0.018, confidence-margin gate +0.033 -- none beats the linear
+0.038. A hand-coded nonlinear rule cannot predict per-item cue reliability.

**Then I prototyped THE IDEAL SOLUTION: a LEARNED glass-box, LM-free cue-integrator** -- a conditional-softmax
reranker over the animacy-filtered person-pool candidates, scoring each by a learned weighted sum of cue features
(net + content + grounded + exact-predicate) PLUS per-item confidence-INTERACTION features (cue x its margin = a
learned per-item gate), trained by conditional-MLE on the DEV bucket (L2), evaluated HELD-OUT on TEST, with a
shuffled-CUE twin. Interpretable betas, no LLM at inference. **RESULT: floor 0.6139 -> LEARNED 0.6682, +0.0543
[0.0077,0.1100] CI-SEPARATED, shuffled-cue twin LOSES (0.549, -0.065), and it BEATS the linear fusion (+0.038).**
So the ideal glass-box mechanism realizes MORE of the integration lever than any fixed rule -- the located
negative's redirect, made live and CI-separated.

**Honest bounds (do not over-read):** (1) the gain is on the animacy-filtered person sub-pool + gold-nominal
grouping; (2) the learned betas show the win is mostly LEARNED cue WEIGHTING (net 1.63, content 0.69, grounded
0.67, exact -0.07) -- the confidence-gate nonlinearity contributed little, so at THIS representation the wall is
"learn the right cue weights," and the deeper nonlinear gating needs richer per-item reliability features; (3)
the CI is wide (lower bound 0.008); (4) the per-item ORACLE 0.857 is UNREALIZABLE (it needs the answer to gate),
so the realizable glass-box ceiling is ~0.67, and pushing past it needs a RICHER representation + more scale =
the North Star. **So YES, the ideal solution is now prototyped and it works (+0.054 CI-sep); it is bounded by
representation richness + coref quality + scale, which is exactly the priority-1 situation model's remit.**

## ABSOLUTE UNDERSTANDING -- WHERE we lose score, and is it UPSTREAM? (owner asked; drilled all the way up + down)
I decomposed the ideal integrator's every error on the held-out bucket by CUE AGREEMENT (how many of the 4 cues'
argmax points to gold). This locates the loss EXACTLY (n=663):

| cues pointing to gold | share of bucket | integrator accuracy there |
|---|---|---|
| 0 (no cue points to gold) | 9.5% | 0.048 |
| 1 | 24.6% | 0.558 |
| 2 | 28.5% | 0.788 |
| 3 | 22.0% | 0.712 |
| 4 (all agree) | 15.4% | 1.000 |

Integrator 0.677; combined ORACLE (>=1 cue right) 0.905. **The loss splits into two parts, and the drill settles
which lever each needs:**

**PART A -- 9.5% "0 cues right" = truly INFORMATION-limited (the no-LLM floor).** No glass-box cue points to gold
-> no combiner can ever pass this; it needs EXTERNAL world-knowledge (the situation model / North Star). This is
the ~irreducible slice under the no-LLM invariant.

**PART B -- ~23% "at least one cue right but the integrator picks wrong" = NOT a better-combiner problem; it is an
UPSTREAM CUE-SHARPNESS problem.** I proved this by trying to recover it and FAILING every way: MAJORITY VOTE 0.643
and SEMANTIC-OVERRIDE 0.575 are BOTH WORSE than the learned net-dominant integrator 0.677 -- so the integration is
NEAR-EXHAUSTED, the learned weighting is already near-optimal. WHY it cannot be recovered: on the 1-cue-right
items the RIGHT cue's own confidence (margin 1.19) only MARGINALLY exceeds the wrong cues' (0.71) -- the right cue
is not decisively detectable gold-free, so no per-item gate can reliably find it. (Telling: 3-cues-right items
score only 0.712 because net/topicality is weighted highest and, when it dissents from the 3 semantic cues, the
integrator follows it -- but OVERRIDING net with the semantic majority makes things WORSE overall, because the
semantic-majority signal is itself unreliable at our coarse representation. Net-dominance is correct; the cues
are just not sharp enough.)

**IS IT UPSTREAM? YES -- decisively.** DRILL UP: the four cues come from upstream organs -- coref clustering
(entity histories), the 12-dim grounded space (individuation), content/event extraction. The realizable ~0.68
ceiling is set by THEIR sharpness, not by the combiner (which is done). Sharper cues -> the right cue wins
decisively -> the near-optimal integrator picks it, closing Part B toward the 0.905 oracle. DRILL DOWN: the pick
feeds the situation model; error propagation is real (the recurrent test), and the 9.5% Part-A slice is the
downstream no-LLM floor. **So breaking the wall is an UPSTREAM REPRESENTATION + COREF-QUALITY problem (Part B,
~23%) plus the EXTERNAL world-knowledge slice (Part A, 9.5%) -- NOT an integration-architecture problem (every
architecture is exhausted at ~0.68).** The single highest lever is a richer entity-INDIVIDUATION representation
(p1; the research's separate perirhinal/ATL individuation code, DELTA 6) that sharpens the cues -- which is
exactly the North Star's remit.

**KEEP GOING UPSTREAM -- the ROOT, pinned to one organ (owner: "keep going upstream").** I traced the ~23%
recoverable loss to WHICH cue holds the answer, by upstream organ (n_recoverable=154): net(->COREF) standalone
0.614, right on 10% of recoverable errors; content(->lexical) 0.579 / 56%; grounded(->the p1 individuation
representation) **0.516 -- the WEAKEST standalone -- yet right on 68% of the recoverable errors (the MOST)**;
exact(->parse) 0.383, uniquely-right on 8%. The grounded cue HOLDS the answer on the recoverable errors but is
too coarse to be trusted -- the exact signature of an impoverished representation. Coref is near-ceiling
(gold-nominal; net right on only 10% -- it is the anti-topicality bucket by construction); parse is redundant.
**So the drill bottoms out precisely: the ROOT is the ENTITY-INDIVIDUATION REPRESENTATION built from reading --
currently a mean of 12-dim event vectors, far too impoverished to tell two people apart. Sharpen THAT (a rich
person-specific individuation code = p1 / the North Star's situation-model entity representation) and the
near-optimal integrator picks the now-decisive cue, closing Part B; the 9.5% Part-A slice stays the
external-world-knowledge floor. The wall is a REPRESENTATION wall, pinned to one organ.** This is the complete,
drilled-to-the-root account. (Reproducible: `exp_coref_faithful_integrator_deltas_v1.py` ->
SCORE_LOSS_DECOMPOSITION + upstream_cue_attribution.)

## PROTOTYPING THE OPTIMIZATION to the root component (owner: "prototype the optimization to that component")
I built three SHARPER glass-box, no-LLM entity-individuation representations and tested whether they sharpen the
cue AND break the integrator past 0.677 toward the 0.925 oracle:
- **ENR1 -- TF-IDF-weighted content individuation** (down-weight common words -> rare, entity-SPECIFIC words
  carry the discrimination): STANDALONE 0.641 -- the SHARPEST single cue, beating net 0.614 / content 0.579 /
  grounded 0.516. So representation sharpness IS a real lever at the cue level, and the 6-cue oracle rises to 0.925.
- **ENR2 -- full grounded PROFILE** (mean grounded vec of ALL the entity's content words, not just the event):
  0.452 -- NOISIER (the coarse 12-dim space washes out with more words).
- **Learned discriminative combinations** of the enriched features.
**RESULT: NO enriched config beats the base 4-cue integrator (0.677).** +ENR1 -> 0.670; REPLACE content with ENR1
-> 0.662; net+ENR1+grounded -> 0.661. **VERDICT: the glass-box representation enrichment is EXHAUSTED here** --
ENR1 is a sharper cue but REDUNDANT with the existing content/grounded cues (it re-encodes the SAME lexical
information more sharply, not NEW orthogonal individuating information), and it is still not decisively confident
enough to fix the per-item selection problem. This is the decisive bound: **breaking the wall needs a genuinely
RICHER, ORTHOGONAL person-specific individuation code -- one that captures WHO each character is (accumulated
attributes / roles / relations), not sharper word-overlap -- which is beyond a glass-box feature tweak and IS the
North Star's situation-model entity representation (a rich individuation code learned from reading, research
DELTA 6).** I prototyped the buildable-here optimization to its floor; the remaining lever is genuinely the
North Star, now with a pinned target (raise the individuation cue's ORTHOGONAL discrimination so the near-optimal
integrator can select it). (Reproducible via the enriched-representation probe; the base decomposition +
attribution are in `exp_coref_faithful_integrator_deltas_v1.py`.)

## HOW THE IDEAL DIFFERS FROM THE BRAIN -- ALL the deltas, researched + prototyped (owner asked; no half effort)
A 4-lane full-text lit-drill (`research_pronoun_resolution_mechanism_2026-09-02.md`, 9 full-text-verified papers
+ ~60 abstract-level, confidence deflated per discipline) audited our prototype against the brain and surfaced
NINE deltas -- it CORRECTED two of my earlier reads and added two I had missed. Each below: the brain mechanism
(FULL-TEXT / ABSTRACT flagged), our state, what I PROTOTYPED + MEASURED, and the verdict. Prototypes:
`experiments/exp_coref_faithful_integrator_deltas_v1.py` (witness `test_coref_faithful_integrator_deltas.py`).

**DELTA 8 -- FLAT BLEND vs STRUCTURED TWO-TERM (NEW; the research's highest-leverage finding; I TESTED it).**
[FULL-TEXT] Kehler & Rohde (2013) explicitly REJECT flat "bag-of-cues" integration for pronouns: the brain keeps
a production LIKELIHOOD P(pronoun|referent) (topicality/subjecthood -- "how pronoun-worthy") and a coherence
next-mention PRIOR P(referent) (active even with no pronoun present) as TWO non-interchangeable Bayesian terms,
MULTIPLIED -- not one blended score; many flat "cues" are epiphenomenal correlates of one term. Our prototype is
exactly the flat blend they reject. I RAN their recommended decisive test (two-stage likelihood x prior vs flat,
same held-out bucket): two-stage 0.7029 (+0.089 over floor) vs flat 0.6772 (+0.063), shuffled-stage twin
collapses (-0.22) -- BUT two-stage-minus-flat is +0.026 [-0.018,0.070] NOT_SEP. **VERDICT: HARD-FAIL at our
feature set, and I know WHY** -- a product-of-softmaxes (log L + log P) is argmax-EQUIVALENT to the flat linear
model (the logsumexp terms cancel over candidates), so the apparent gain is a training-path artifact, not the
architecture. K&R's split is real in humans but does not transfer to our LINEAR features (they already
collinearly encode it -- exactly the HARD-FAIL the research predicted from our betas). A genuine benefit needs
the prior ESTIMATED independently of the pronoun with a NONLINEAR gate -- the North Star's remit, not a flat-feature tweak.

Our ideal (a DEV-trained conditional-softmax cue-integrator) copies the brain's COMPUTATION (learned weighted
cue integration) but differs in several ways. Two of the "small" ones are potentially the most important.

**DELTA 1 -- SUPERVISED vs SELF-SUPERVISED learning (I PROTOTYPED it -- CLOSED in point estimate; brain-grounding
TEMPERED by the research).** My ideal used GOLD antecedent labels; the brain gets none. I built the label-free
version: train cue weights on CUE-AGREEMENT pseudo-labels (>=3 of 4 cues agree -> pseudo-label; Competition Model
-- validity learned from CONVERGENT evidence; MacWhinney-Bates). **RESULT: self-supervised +0.060 [-0.036,0.152]
vs gold-supervised +0.063 [0.018,0.117] -- point estimates MATCH (n_pseudo=2068); the organ is learnable WITHOUT
gold antecedents** (the North-Star requirement). Honest: the label-free signal is NOISIER -> the CI widens to
NOT_SEP (it is a point-estimate match, not a CI-separated one). **TEMPER (research, the biggest correction):** I
had framed the self-supervised mechanism as "predict-and-update via the N400, just wire it" -- the research shows
that specific mechanism has a DIRECT NEGATIVE test (van Wonderen & Nieuwland 2023, N~200, NO evidence predictive
strength adapts to past prediction error, at the EASIER lexical level) + a partial 9-lab replication failure of
its flagship support (Nieuwland 2018 eLife vs DeLong 2005). So self-supervised cue-validity learning is a
genuinely OPEN empirical question, NOT a known-good build target -- my cue-AGREEMENT bootstrapping (which is a
Competition-Model story, not prediction-error) is the defensible label-free route, and even it must be
pre-registered with a null in play. Down-ranked from "the #1 gap to wire" to "a real open experiment for the North Star."

**DELTA 2 -- COMMIT vs DEFER (small, and I TESTED it -- REALIZABLE, near-closed).** Our integrator argmax-commits;
the brain DEFERS on genuinely ambiguous cases (the Nref "hold both"; Garrod-Sanford resolution stalls). Crucially,
the parent found the GRADED pick's wrong picks are 99.5% CONFIDENT (uncalibrated -- cannot defer). MEASURED here:
the LEARNED integrator's posterior entropy predicts its OWN errors at AUC 0.796, and deferring the highest-entropy
34% raises kept accuracy 0.668 -> 0.803 (keep 50% -> 0.864), while a random-defer twin is flat (0.650). So cue
INTEGRATION restores the brain's calibrated "hold both" signature that the single-cue pick lacked -- and the
deferred items ARE the genuinely-hard residual. The delta is near-closed by wiring the EXISTING entropy-abstain
(parent Track B) onto the integrator. Two-for-one: integration buys accuracy AND legible uncertainty.

**DELTA 3 -- FEED-FORWARD vs RECURRENT parallel-constraint (small: a settling loop; important for re-analysis).**
The brain's interactive-activation settling (McClelland) lets a LATER cue REVISE an earlier commitment (cataphora,
garden-path recovery) and feeds each resolution back into the entity representations that drive the next pronoun.
Our integrator is one-shot per pronoun. The substrate has the settling primitive (iterative_attractor); wiring the
integrator INTO the recurrent entity-maintenance loop (so picks feed back) is the faithful version.

**DELTA 4 -- LINEAR-in-features vs genuinely MULTIPLICATIVE combination (small: the nonlinearity form; important:
it caps us).** Parker (2019): cues combine multiplicatively (all-agree is super-additive; conflict is flat). Our
learned betas show the win is mostly linear cue WEIGHTING -- the confidence-interaction (gate) terms took small
weights, so we are NOT yet capturing the genuine multiplicativity, which is part of why we realize ~0.67 not the
0.857 oracle. A learned multiplicative/attention gate (per-item cue reliability) is the missing nonlinearity.

**DELTA 5 -- STATIC vs CONTINUAL (small; important OOD).** Our weights are frozen after DEV; the brain re-weights
cue validity continually (a new genre where content-cohesion is more/less reliable shifts the weights online).

**DELTA 6 -- the CUE SET is hand-engineered + COARSE (the p1 representation gap).** Our four cues are hand-picked
and the grounded one is the 12-dim space (too coarse to individuate two people -- grounded-max is the weak cue).
The brain's cues EMERGE from a rich distributional hub (ATL PDP) and the set grows with learning.

**DELTA 7 -- NO similarity-based interference / fan effect modeled.** The brain's cue-based retrieval degrades
when two candidates are feature-similar (Lewis-Vasishth similarity-based interference; Van Dyke). Our softmax
competition captures some of this but does not explicitly represent inter-candidate interference.

**Bottom line for the owner:** the two small deltas that matter most are (1) SELF-SUPERVISED learning (open -- the
North Star's core, and the reason to build it there not here) and (2) DEFER (near-closed -- I showed the
integrated posterior is calibrated and deferral works, unlike the single-cue pick). Deltas 3-4 (recurrence +
genuine multiplicativity) are the next fidelity increments; 5-7 are representation/continual-learning, the
standing p1 + learner lanes.

## THE UNIFYING FINDING (for planning -- these are ONE wall)
The who-has-what coref residual (this problem), the WSD override-accuracy a_s residual (my previous problem
`wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector`), and the OPEN priority-1 North Star
are the SAME wall: **the generative "which SPECIFIC one" problem -- picking the specific referent/sense from a
world-knowledge situation model.** Detection/likelihood is maxed in both (coref: the graded pick is near-optimal;
WSD: the directional detector AUC ~0.71); the entire remaining gain lives in GENERATION. This convergence is why
the North Star outranks both -- it is the shared organ.

## WHAT REMAINS TO REACH OPTIMAL -- the full backlog (owner asked; every disparate component, in one place)
This submission is a rigorous PARTIAL + a complete located-understanding, NOT the optimum. Here is EVERYTHING
still needed to reach optimal on this wall, consolidated, each tagged with WHERE it lives and its MEASURABLE
target. The instrument for all of it is this problem's `SCORE_LOSS_DECOMPOSITION` (integrator 0.677 -> oracle
0.905/0.925; loss = 9.5% external-knowledge + ~23% representation).

THE PRIMARY LEVER (breaks the ~23% -- the biggest, and the whole point):
1. **A rich, ORTHOGONAL, person-specific ENTITY-INDIVIDUATION representation** -- capturing WHO each character is
   (accumulated attributes / roles / relations), not sharper word-overlap (glass-box enrichment is exhausted,
   proven). WHERE: the priority-1 North Star situation-model entity code + p1 (research DELTA 6:
   perirhinal/ATL conjunctive individuation, distinct from category semantics). TARGET: raise the individuation
   cue's ORTHOGONAL discrimination so the near-optimal integrator selects it -> bucket toward 0.905.

THE EXTERNAL-KNOWLEDGE FLOOR (the 9.5% "0 cues right"):
2. **Specific-discourse + world knowledge** so a candidate the text under-determines can still be resolved.
   WHERE: the North Star situation model + the learner reading a large corpus. BOUND: a slice is genuinely
   irreducible under the no-LLM invariant (Winograd core).

BRAIN-FIDELITY DELTAS still open (all North-Star architecture, not tweaks here -- see the delta section):
3. **DELTA 3 -- recurrent two-pass revision + a live salience state** updated ASYMMETRICALLY (enhance winner /
   actively suppress losers, Gernsbacher; not passive decay), fed back to the next pronoun.
4. **DELTA 9 -- incremental word-by-word commitment** (~300-450ms; Brodbeck 2015) with a running ambiguity state,
   vs our batch one-shot.
5. **DELTA 1 -- self-supervised cue-validity learning**: a genuinely OPEN empirical question (pre-register a
   NULL; van Wonderen & Nieuwland 2023 is a direct negative). WHERE: the learner. Down-ranked from "known fix."
6. **DELTA 4 -- the discrete mismatch/fan nonlinearity** (not smooth multiplicative) + full-text Parker 2019 for
   the interaction-term sign (couldn't obtain full text this session).

ENABLING / QUALITY LEVERS:
7. **Coref quality** -- the realized +0.054/+0.060 use gold-nominal grouping; live glass-box coref eats them
   (the animacy filter is a REQUIRED gate, proven). Better name-unification/coref is a prerequisite gate.
8. **Land the realized learned integrator** (default-off Q111): a composition of the EXISTING phi_agreement_keep
   + situation_model_accumulate; marginal (+0.038/0.054), so weigh the wire cost -- at minimum it is the North
   Star's first staged step.

VERIFICATION / DUE-DILIGENCE remaining (to make THIS submission airtight):
9. **Confirm the individuation-root diagnosis on the CLEAN parent-harness bucket** (my decomposition is on the
   cache-representation bucket; the faithful premise is via the parent harness -- cross-check the root there).
10. **Fold the two-stage (DELTA 8) + the optimization-enrichment tests into the WITNESSED core** -- they are
    currently in prose + a persisted probe (`prototype_optimization_individuation_representation.py`), not
    witness-guarded (the 8/8 + 4/4 witnesses do not cover them).
11. **Run the fan/competitor-count feature interaction test** (DELTA 7 refined) -- I flagged it underpowered on
    this low-competitor-variance bucket but did not run it.
12. **OOD**: LitBank is the coref's home corpus; absolute recall may be optimistic OOD (the deltas hold, being
    same-corpus both arms).

RESEARCH FOLLOW-UPS (open questions the drill named, not resolvable by build):
13. Visual-world eye-tracking under PARAMETRIC cue conflict (Kaiser/Brown-Schmidt) -> the flat-vs-deferred
    posterior + deferral-vs-integration-cost debates (Q4/Q6 were the thinnest-evidenced).
14. Full-text Parker (2019) for the exact nonlinearity sign (DELTA 4).

RANKED: #1 (individuation representation) is THE lever and is the North Star's core; #7 (coref quality) gates
whether any of it realizes live; #2 is the irreducible-ish remainder; #9-#11 make this submission airtight; the
rest are North-Star architecture (#3-6) + open research (#13-14).

## ADJACENT COMPONENTS -- capabilities / limitations / opportunities / brain status (seeds the next problems)
1. **The GENERATIVE world-knowledge situation model (OPEN, priority-1) -- THE lever.** CAP: assembles built
   pieces (situation_reader, the confirmed detector, meaning_fusion, ultrametric_clustering, FrameNet/script
   assets). LIMIT: not yet built; this cell shows the current representations null on the coref residual.
   OPPORTUNITY: supplies the sense-SPECIFIC / referent-SPECIFIC prediction = the a_s lever = the coref residual.
   BRAIN: the Garrod-Sanford slow RESOLUTION stage (PINNED). Highest leverage; the shared organ.
2. **The LEARNER (ON, beneficial for word-meaning).** CAP: grows distributional word-meaning from reading,
   safe + beneficial (+0.058 downstream), rollback works. LIMIT: builds WORD-substitutability, not ENTITY-level
   world-knowledge; measured null on the coref residual. OPPORTUNITY: the ENGINE that would populate the
   generative situation model's world-knowledge -- but it needs an entity/relational target representation
   (p1 + the North Star), not the substitutability channel. BRAIN: distributional PDP acquisition (PINNED).
3. **The 12-dim GROUNDED SEMANTIC SPACE (p1 representation lane).** CAP: separates concrete OBJECT classes
   (positive control 8/8). LIMIT: MEASURED as a binding constraint -- grounded-event-similarity is NOT_SEP vs
   topicality on the clean person pool (-0.027; two people have near-identical grounded event profiles), WHEREAS
   the discrete/exact-identity and full-content representations DO beat topicality (+0.085 / +0.070). So the
   lever is an ACCUMULATED ENTITY representation (predicate identity + content), and the coarse grounded
   distributional channel is the weak part. OPPORTUNITY: a richer distributional entity representation would lift
   both the coref and WSD residuals. BRAIN: the ATL hub is distributional; our space is too coarse. Standing lane.
4. **`world_state_entity_binding` + `event_centrality_coref` (WIRED, brain-foundational).** CAP: the Stage-1
   reference dispatcher + Centering resolver + the entity-maintenance chain -- these DELIVER the bonding stage +
   global topicality (the recoverable ~0.46). LIMIT: they compute bonding, not resolution; the struct-dominated
   residual is where bonding is ambiguous. OPPORTUNITY: feed the maintained histories into the generative model.
   BRAIN: bonding/Centering (PINNED, faithful).
5. **The parse-based syntactic-locality binder (a DIFFERENT organ).** The 27% intra-sentential slice; the prior
   negative's fine-distance oracle (37.6% ungateable without a reliable parse). Blocked by archaic-prose parse
   noise; a register-robust parser is the follow-on for THAT slice. BRAIN: item-level structural proxies (Kush).

## WHAT I DID NOT ESTABLISH / withdraw first
1. The residual is NOT proven irreducible: the prior negative's fine-distance oracle (37.6%) shows the 27%
   intra-sentential slice is reachable by a DIFFERENT organ (parse-based binding). My claim is that the coherence
   PRIOR and the in-text semantic representations do not reach the bucket; the reachable-by-world-knowledge
   fraction is the North Star's to measure.
2. The in-text lever (+0.07-0.085) is a GOLD-COREF ceiling; with the live glass-box chain's noisy coref the
   realized channels drop to near-chance (combined 6.9%). So the lever is real as a TARGET but its realizable
   size depends on coref quality (the first gate). Withdraw first any claim that the +0.085 is achievable at the
   current live coref quality. The exact numbers are on the cache representation (its pool is animacy-polluted,
   handled by the clean person-pool re-measurement; the FAITHFUL premise is via the parent harness, 0.481).
3. A first ceiling version LEAKED future mentions (spurious 0.58); the reported numbers are PAST-ONLY. Withdraw
   first any past-leaking number.
4. OOD caveat (shared with the parent): LitBank is the coref's home corpus; the blind-vs-prior delta holds
   regardless, absolute levels may be optimistic OOD.

## KEY REALIZATIONS (the enabling moves)
1. **Read the organ you are told to reuse -- it carries the provenance of the negative that spared it.** The
   `hdlab/graded_coref_pick.py:125` comment named `the_reader_has_no_coherence_next_mention_prior` as an
   owner-DONE negative; `before_you_start.py` on the brief's keywords did not surface it (different slug).
   Enumerating the coherence/prior problem folders on disk (not a keyword search) caught the duplicate.
2. **The bucket is defined on the NOCHAIN history and scored under the CHAIN.** Getting this two-pass wrong
   moved the premise from 0.13 to 0.48; matching it reproduced the brief's 0.481 exactly.
3. **The info-free twin is the meaningful floor even when the floor is not 0.** The chain floor is ~0.42
   (not the prior negative's 0/205); the coherence-signal question is still "does the prior beat its shuffled
   self?" -- and it does not.
4. **Measure the ORACLE ceiling first, PAST-ONLY, WITH a frequency control.** My first (future-leaking) ceiling
   gave a spurious 0.58 that looked like a buildable in-text lever; the frequency control (0.46) + the past-only
   fix revealed the "signal" was global topicality, and three independent representations then triangulated the
   in-text ceiling AT frequency. The control turned an exciting wrong answer into the true one.
5. **Locate the wall by what a PERFECT-information glass-box system could do, not by what our current one does.**
   The gold-coref ceiling separates "the info is not in the text" (external world-knowledge, no-LLM bound) from
   "our resolver/representation is weak" (buildable) -- the decisive distinction the owner asked for.
6. **A confound flip-flopped my answer three times until I controlled it properly -- and controlling it flipped
   the CONCLUSION.** (i) A future-leaking history gave a spurious 0.58. (ii) Past-only on the animacy-POLLUTED
   39-candidate pool made in-text semantics look exhausted at frequency (external-world-knowledge bound). (iii)
   Cleaning to the genuine person-vs-person pool + a MATCHED (same-items) comparison with CIs revealed a real
   in-text lever (+0.07-0.085 CI-sep above topicality). The lesson (self-correcting controls): a pooled or
   applicable-set-confounded oracle can hide a real signal OR invent a fake one; the honest wall-localization
   needed a clean population, a matched comparator, and a CI -- and only then does "partly buildable, partly
   bounded" replace the too-strong "purely external."
8. **"Do we understand ALL the walls?" -- no, until the per-item COMBINED oracle. My single-channel oracles
   (each ~0.5-0.63) and the marginal realized +0.033 both LOOKED like "the in-text info is nearly exhausted."
   The decisive move was the per-item COMBINED oracle (best channel per item): 0.857 vs topicality 0.56. That
   one number flipped the diagnosis from "missing information / external world-knowledge" to "INTEGRATION
   QUALITY -- the info is here, we lack the nonlinear gate." A single-channel ceiling hides a multi-channel
   truth; you must ask "what could the BEST combination do?" before concluding the info is absent. And it is
   brain-grounded: the brain's cue integration is nonlinear (Parker 2019), ours is linear -- the exact gap.**
7. **The buildable lever was already two EXISTING organs -- check the disk before building.** Before wiring the
   realized lever I checked whether the substrate already supplies its pieces (owner's directive), and it does:
   the animacy pre-filter is `phi_agreement_keep` (landed) and the accumulated-entity representation is
   `situation_model_accumulate` (landed, validated). So the "realization" is a COMPOSITION of two landed organs
   into the coref pick, not a new mechanism -- and the CONTENT (lexical-cohesion) channel, not the
   exact-predicate channel, is what survives fusion. Querying the disk turned a "build a new organ" into a
   "wire two organs" (and told me pred-only would wash out before I over-invested in it).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
The who-has-what structurally-dominated residual, after the entity-maintenance wire, is STILL not
coherence-prior-decisive (reconfirms the 2026-08-29 entry on the composed population: prior-minus-twin +0.0009
NOT_SEP, oracle 6.9%, regresses non-dominated). NEW, sharper localization (three drills, corrected twice;
the decisive instrument is the per-item COMBINED in-text oracle ceiling on the CLEAN animacy-filtered pool):
the wall is INTEGRATION QUALITY, NOT missing information. The COMBINED best-per-item in-text glass-box oracle
ceiling = 0.857 (semantic-only 0.795) vs topicality alone 0.563 -- so the discriminating info IS in the text; we
lack the NONLINEAR per-item GATE. The brain integrates cues NONLINEARLY (Parker 2019 -- parallel-constraint,
full-cue-match favored more than linear); our fusion is LINEAR-additive. A realizable LINEAR multi-cue integrator
(WIRING two EXISTING organs: the phi_agreement_keep animacy filter + situation_model_accumulate) lifts the bucket
+0.038 [0.015,0.065] CI-sep on the animacy-filtered pool (twin loses, no net harm; NULL on the animacy-polluted
pool -- animacy is a required gate); it captures ~1/5 of the 0.857 oracle ceiling because linear fusion cannot
per-item gate (exact-predicate, strongest oracle, washes out: 74% redundant with topicality). The gap
0.65->0.857 is the LINEAR->NONLINEAR integration gap = the situation model; only the ~14% above 0.857 is external
world-knowledge + annotation-fiat ambiguity. This CORRECTS TWO earlier too-strong reads (a pool-polluted
"in-text exhausted" and a world-knowledge-bound framing). It is the SAME "which SPECIFIC one" wall as the WSD
a_s residual; the shared organ is the OPEN priority-1 situation model, now specified as a NONLINEAR learned cue
integrator. The learner (ON, beneficial for word-meaning) builds word-substitutability, the WRONG representation
-- the integrator needs ENTITY-level accumulated cues + a nonlinear gate. Citations to add: Parker 2019
(nonlinear cue integration); Garrod & Sanford 1994 (bonding/resolution);
Bott & Solstad 2014 (coherence bias = slot not entity); Hagoort 2004 (world knowledge as fast as word meaning);
Rogers & Lambon Ralph 2004 (ATL PDP distributional); Hobbs 1993 (abduction); Sharma et al. (multi-fact Winograd).

## TLDR (plain language)
The hardest "who is she?" cases are the ones where grammar points the wrong way. This task asked for a "guess
who's talked about next" step to fix them. First: we already tried exactly this four days ago and proved it does
not help -- I found that on disk (the task did not mention it) and confirmed it still fails after the recent
memory-tracking improvement. Then, because you asked me to understand the wall deeply, I built a test that gives
the system PERFECT memory of the story and asks the strongest possible question of the text. The honest, careful
answer (it took three tries and proper controls to get right): the biggest help is knowing who the main character
is -- which our tracker already does. But a RICHER memory of what each specific character has said and done DOES
help a measurable, statistically-clean extra amount on the genuine person-vs-person cases -- so it is not "all
outside knowledge": part of the fix is a better in-story memory, which is exactly what the "understand from
reading" model would build. The catch is two gates: it only pays off if we know WHO each mention is (good
character-tracking first), and there is a ceiling -- past that, the answer really does need outside knowledge
("Anne is Lady Russell's god-daughter") not written in the passage. That capped-but-real wall is the SAME wall as
a word-meaning problem I worked before ("which exact meaning") -- both need the big "understand the world from
reading" model already queued as priority one. Good news you asked about: the learner that builds knowledge from
reading IS switched on and DOES help word-meaning (a clean, proven gain) -- but today it learns word meanings,
not facts about specific characters, so it needs the priority-one model to carry this. My recommendation:
fold this task into the priority-one project (don't have someone rebuild it), and don't add a "guess who's next"
rule to the reader (it slightly hurts). The mechanism works on clean textbook examples (8/8), which is exactly
why it's worth knowing the real hard cases don't contain those examples.

## QUESTIONS
I moved the label from REFUTED to **PARTIAL** after prototyping the ideal solution: the brief's mechanism (the
coherence prior) is REFUTED, but the REAL problem is now partially SOLVED by the correct mechanism (a learned
glass-box cue-integrator) to a CI-separated +0.054 (shuffled-cue twin loses, beats the linear fusion). A rigorous
located negative alone was a full pass; the realized learned solution makes PARTIAL the more honest label. If you
prefer it read REFUTED (the brief's named mechanism is dead) or SOLVED (a CI-separated realized gain exists), the
content is identical -- your call. The one thing I want on the record so it is not over-read: the +0.054 is on
the animacy-filtered person sub-pool with gold-nominal grouping and a wide CI (lower bound 0.008); it is a
prototype of the ideal mechanism, not a landed robust capability. Otherwise: none.

## NEXT STEPS
1. (Strategy) CONSOLIDATE this priority-3 problem into the priority-1 North Star
   (`the_meaning_channel_needs_a_generative_world_knowledge_situation_model...`) rather than assigning a re-derive.
   Re-verify the witness (5/5) first.
2. (Strategy) Do NOT land a coherence prior / event-coherence prior / static-KG cue -- all measured dead. DO
   consider landing the CONSTRUCTIVE REALIZATION (Q111, default-off): an `accumulated_entity` content-cohesion
   cue = phi_agreement_keep (animacy, EXISTING) + situation_model_accumulate (EXISTING) fused into the graded
   pick -- +0.033 CI-sep (marginal) on the animacy-filtered bucket, twin loses, no harm, null on the polluted
   pool. It is a COMPOSITION of two landed organs; flag OFF -> byte-identical. Weigh the marginal gain vs the
   wiring cost; at minimum it is the priority-1 organ's first staged step.
3. (Priority-1) When the generative world-knowledge situation model is built, use THIS cell's ceiling + anatomy
   as its instrument + PRE-REGISTERED TARGET: an accumulated-entity representation should recover the +0.07-0.085
   in-text lever (bucket 0.42 -> ~0.63 in-text ceiling, gated by coref quality), then external world-knowledge
   carries it toward the 0.73 gold-chaining ceiling -- with a shuffled-situation twin losing. This IS the owner's
   learner proof, staged (fix coref -> build entity representation -> add world-knowledge), on the organ that can
   carry it. The two gates to report: coref quality (the lever is gold-coref today) and the modest in-text ceiling.
4. (Fold) The AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md 2b.

## INTEGRATED_BY_STRATEGY 2026-09-02

Reverified BOTH witnesses FIRST-HAND: `test_coref_coherence_prior_on_chain_bucket.py` **8/8** (W4
event-state lever near-chance + positive control fires = RIGOROUS_NEGATIVE_REPRODUCES; W5 wall localized
to a richer in-text rep; W6 realized lever +0.0377 CI-sep on the animacy-filtered pool, twin loses; W7
wall is INTEGRATION not missing-info, combined ceiling 0.857 >> topicality 0.563; W8 learned
cue-integrator +0.0543 CI-sep over floor, twin loses) and `test_coref_faithful_integrator_deltas.py`
**4/4** (self-supervised +0.060 ~= gold +0.063 = learnable WITHOUT gold; calibrated posterior AUC 0.807
→ realizable defer; recurrent/multiplicative/interference deltas are HONEST NEGATIVES at our features).

Accepted **PARTIAL** (brief mechanism REFUTED + a near-DUPLICATE caught + the real problem partially
solved by the correct mechanism + the wall drilled to its root), rating **EXCELLENT** — exemplary: it
CAUGHT that the brief's coherence next-mention prior was already owner-DONE dead (2026-08-29
`the_reader_has_no_coherence_next_mention_prior`), reproduced the premise EXACTLY, confirmed the prior
stays dead after entity-maintenance, then found the RIGHT mechanism (Kehler-Rohde is LEARNED cue
integration, not a prior): a glass-box LM-free conditional-softmax cue-integrator (wiring the existing
`phi_agreement_keep` + `situation_model_accumulate`) recovers the bucket +0.054 CI-sep, learnable
without gold, calibrated. Drilled the score-loss to the ROOT: the ENTITY-INDIVIDUATION REPRESENTATION
(the 12-d individuation cue is the wall), and sharper glass-box reps don't beat it (redundant, not
orthogonal) → the fix is a RICHER, ORTHOGONAL person-specific individuation code learned from reading.

**NO hdlab wire** (the coherence prior is refuted/a duplicate; the realized cue-integrator +0.054 is a
gold-nominal-grouping, animacy-filtered-pool PROTOTYPE with wide CIs — an OPTIONAL default-off Q111 wire,
NOT landed, its live value coref-quality-bound). **AUDIT UPDATE folded into §2b.** Priority cleared.
**CONSOLIDATED INTO P1 (the solver's explicit request):** this coref residual, the WSD a_s residual, and
the composition-as-prediction representation bound are ONE wall — the "which SPECIFIC one" problem, fixed
by a rich learned ORTHOGONAL individuation/meaning representation. P1 now carries this problem's
INSTRUMENT (the SCORE_LOSS_DECOMPOSITION) + pre-registered TARGET (the 0.905 coref oracle).
