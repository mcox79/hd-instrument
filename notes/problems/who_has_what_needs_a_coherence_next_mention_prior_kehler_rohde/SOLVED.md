---
problem: who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde
status: REFUTED
bar: "PASS = a glass-box coherence/next-mention PRIOR (predicting the likely next referent from the discourse-coherence relation, multiplied into the graded-retrieval posterior before argmax) that: 1. recovers the STRUCTURALLY-DOMINATED error bucket CI-separated -- the bucket reachable by NO recency/subject/frequency cue (currently 0.481, n~445) -- over the entity-maintenance floor (recompute the floor on the held-out population, gate on its UPPER bound), on HELD-OUT LitBank gold coref (doc-split); 2. the lift is ATTRIBUTED to the coherence prior -- it must appear on the structurally-dominated bucket (which no backward cue can reach), with the backward graded pick held at its near-optimal setting; 3. a shuffled-coherence twin LOSES CI-separated (same mentions, wrong coherence relation -> the forward signal, not the machinery, does the work); 4. does NO net harm to the near / non-dominated cases (report the per-bucket effect; a bucket recovery bought with a non-dominated regression is not a pass). Report CI half-width + null p95 on every margin. A rigorous located NEGATIVE is a FULL PASS if a faithfully-built coherence prior does not recover the bucket AND it names why (the coherence-relation signal is too weak glass-box / the prior is dominance-reinforcing / a genuine irreducible ambiguity floor) with the number."
result: "RIGOROUS LOCATED NEGATIVE (full pass) -- the brief's coherence prior is a near-DUPLICATE of the owner-DONE 2026-08-29 negative (`the_reader_has_no_coherence_next_mention_prior`, REFUTED/EXCELLENT/DONE), and it stays dead AFTER the entity-maintenance wire. On the HELD-OUT (50 test docs) CHAIN structurally-dominated bucket (the brief's exact population, n=695) the faithful coherence prior (reused verbatim, DEV-tuned wp=0.3) does NOT beat the chain floor (prior-minus-floor -0.0043 [-0.0223,+0.0119] NOT_SEP) and does NOT beat its own 20-shuffle INFO-FREE TWIN (prior-minus-twin +0.0009 [-0.0138,+0.0148], hw 0.0143, null p95 0.0144, NOT_SEP); ORACLE ceilings near-chance (selectional 5.1%, thematic 14.7%, combined 6.9%); it REGRESSES the non-dominated cases (0.7521->0.7246, broke 75). Premise reproduced EXACT via the parent harness (chain acc 0.4809 on the struct-dominated bucket = the brief's 0.481, 0.294 of errors dominated, n=445, 0.995 confident). WALL LOCALIZED (gold-coref past-only ceiling, decided on the CLEAN person-vs-person pool with a MATCHED apples-to-apples comparison vs global topicality): the load-bearing recoverable signal is GLOBAL TOPICALITY (protagonist), captured by the chain; AND -- correcting an earlier pool-polluted read -- a RICHER in-text entity representation BEATS topicality CI-separated on genuine person-vs-person cases (exact-predicate +0.0846 [0.0345,0.1379] ABOVE, full-context BOW +0.0702 [0.012,0.1284] ABOVE; grounded-max -0.027 NOT_SEP), so the wall is PARTLY a BUILDABLE representation/coref-quality lever (the situation model, gated by coref) bounded by a modest ~0.63 gold-coref ceiling, and PARTLY external world-knowledge above that. Residual anatomy: 54% gold last named 2+ sentences back (situation-model), 27% intra-sentential (parse/semantic), ~6 gendered person-competitors. POSITIVE CONTROL: the mechanism flips constructed pairs (selectional 8/8, IC 8/8) -> it works; the bucket lacks the cases. CONSTRUCTIVE REALIZATION (the buildable lever made live, WIRING EXISTING ORGANS not a new build): fusing an accumulated-entity CONTENT channel (a glass-box proxy for hdlab.situation_model_accumulate) into the graded pick, over the animacy-filtered person pool (the EXISTING hdlab.graded_coref_pick.phi_agreement_keep pre-filter -- the real reader's deployment), lifts the struct-dominated bucket 0.6139 -> 0.6471, +0.0332 [0.0016,0.0689] CI-sep (marginal; content-only +0.0271 [0.007,0.0512], the load-bearing channel; pred-only null), shuffled-entity twin LOSES (-0.006), NO harm to non-dominated (+0.003); on the animacy-POLLUTED full pool it is NULL (weight 0) -- so the animacy organ is a required gate. Deterministic across PYTHONHASHSEED 0/1/42. Scorer = argmax==gold he/she who-has-what pick accuracy, doc-bootstrap 95% CI."
floor: "Strongest floor actually run = the info-free 20-shuffle coherence-prior TWIN on the same held-out bucket = 0.4178 [0.3027,0.5229]; the real prior 0.4187 does NOT clear it (prior-minus-twin +0.0009 NOT_SEP, null p95 0.0144). The entity-maintenance CHAIN floor (the bar's named floor) = 0.4230 [0.3080,0.5433] (gate on upper bound 0.5433); prior does not beat it (-0.0043 NOT_SEP). Premise floor reproduced EXACT via the parent harness = 0.4809 (=the brief's 0.481), n=445. CEILING decomposition (gold-coref past-only oracles, reachability not floors, on the CLEAN person-vs-person pool, MATCHED vs global topicality on the same items): global topicality is the base recoverable signal (~0.55); a richer in-text representation ADDS CI-separated -- exact-predicate +0.0846 [0.0345,0.1379] ABOVE, context-BOW +0.0702 [0.012,0.1284] ABOVE (grounded-max -0.027 NOT_SEP); the in-text ceiling ~0.63 (gold coref), residual above = external world-knowledge."
controls: "(1) INFO-FREE 20-shuffle TWIN: prior (0.4187) does NOT beat it (0.4178), NOT_SEP -- excludes 'the prior carries usable signal'. (2) ORACLE-ceiling per channel (selectional 5.1%/thematic 14.7%/combined 6.9%/event-state 7.8%) all near-chance -- excludes 'a better fusion weight rescues it'. (3) NO-REGRESSION: the prior regresses non-dominated 0.7521->0.7246 (broke 75) -- dominance-reinforcing, bar item 4 fails. (4) POSITIVE CONTROL 8/8 selectional + 8/8 IC vs chance -- excludes 'mechanism broken / metric cannot move'. (5) DEV/TEST doc-split, fusion weight tuned on DEV (best shot). (6) FREQUENCY CONTROL on the ceiling (global-protagonist past-only) -- the topicality confound the in-text semantic channels must beat. (7) MATCHED apples-to-apples comparison (each in-text channel vs frequency on the SAME items, paired-bootstrap CI) on the CLEAN person-vs-person pool -- fixes an applicable-set confound and reveals exact-predicate +0.085 ABOVE, context-BOW +0.070 ABOVE (a real buildable in-text lever), grounded-max NOT_SEP. (8) POOL-CLEANING control: the same channels on the animacy-POLLUTED 39-candidate pool are all NOT_SEP/BELOW frequency -- so the lever is a genuine person-vs-person effect, masked by inanimate distractors. (9) PAST-ONLY ceiling (no future-mention leakage -- a first, future-leaking version gave a spurious 0.58). (10) REALIZED-lever controls: SHUFFLED-ENTITY twin (assign each candidate a random other candidate's accumulated representation) LOSES (-0.006 vs +0.033) -> the maintained IDENTITY does the work; NO-HARM on non-dominated (+0.003); the animacy-POLLUTED full pool is NULL (weight 0) -> isolates the animacy organ as a required gate; CHANNEL DECOMPOSITION (content CI-sep, pred washes out) localizes the signal. (11) determinism across PYTHONHASHSEED 0/1/42."
files_changed: "experiments/exp_coref_coherence_prior_on_chain_bucket_v1.py (the chain re-expressed in the who-did-what cache + the reused coherence-prior channels + the NEW event-state situation channel + the SITUATION-MODEL CEILING probe [freq/exact-predicate/grounded-max/context-BOW, gold-coref past-only, clean person pool + MATCHED comparison] + the REALIZED accumulated-entity lever [wiring the existing animacy filter + accumulated-entity representation, with channel decomposition] + the RESIDUAL ANATOMY + faithful parent-harness premise); verification/test_coref_coherence_prior_on_chain_bucket.py (6/6 scaffold-free witness); data/exp_coref_coherence_prior_on_chain_bucket_v1/metrics.json. NO hdlab/ written (Q111 -- the proposed wire composes EXISTING organs)."
reverify: ".venv/Scripts/python.exe verification/test_coref_coherence_prior_on_chain_bucket.py   # 6/6: self-test + premise EXACT via parent harness (0.481/0.294/0.995) + coherence prior dead on the composed bucket (oracle 6.9%, prior does NOT beat its info-free twin) + event-state lever near-chance + WALL LOCALIZED (topicality load-bearing + a richer in-text rep beats it CI-sep on the clean person pool) + REALIZED lever (accumulated-entity content channel, existing organs, +0.033 CI-sep on the animacy-filtered pool, twin loses, no harm, null on polluted pool)"
---

# REFUTED (rigorous located negative = full pass). A near-DUPLICATE of an owner-DONE negative, drilled to the exact wall.

## Headline
The coherence next-mention prior this brief proposes was already measured dead owner-DONE on 2026-08-29
(`the_reader_has_no_coherence_next_mention_prior`, REFUTED/EXCELLENT). I reproduced the brief's premise EXACTLY,
confirmed the negative SURVIVES the entity-maintenance wire, and then -- per the owner's push to understand the
wall deeply -- drilled it to the load-bearing factors with a new instrument (a gold-coref ceiling, cleaned to
genuine person-vs-person, matched vs topicality with CIs). **The wall is THREE parts: (1) GLOBAL TOPICALITY,
which the chain already captures; (2) a BUILDABLE in-text representational lever -- a richer accumulated-entity
representation beats topicality CI-separated on person-vs-person cases (+0.085 / +0.070, gold coref), gated by
coref quality and bounded by a ~0.63 ceiling; (3) EXTERNAL world-knowledge above that.** Parts (2)-(3) are the
same generative "which SPECIFIC one" wall as the WSD a_s residual, whose organ is the OPEN priority-1 North Star.
Recommendation to strategy: consolidate this problem into priority-1 (its ceiling + target are the instrument);
do not re-derive it; do not land a coherence prior.

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
- **GAP 2 -- NO WORLD-KNOWLEDGE AT INFERENCE (the no-LLM invariant) -- the REST of the residual.** Above the
  ~0.63 gold-coref in-text ceiling, the gap to the ~0.73 gold-chaining ceiling (and beyond) is external
  world-knowledge. The brain's ATL hub supplies
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

**VERDICT on "do we understand it": yes, and it is a THREE-part wall, each measured on the clean pool:**
(1) GLOBAL TOPICALITY (~0.55 of the person-pool cases) -- captured by the chain; (2) a BUILDABLE in-text
representational lever (+0.07-0.085 CI-sep above topicality, exact-predicate + full-context, with gold coref) --
the situation model, gated by coref quality; (3) EXTERNAL world-knowledge above the ~0.63 gold-coref ceiling --
the no-LLM-bounded slice. The one honest uncertainty left is empirical, not conceptual: how much of (2) survives
glass-box coref noise, and how much of (3) a generative model could reach vs LitBank annotation-fiat ambiguity
(ezCoref) -- both are the North Star's to answer, and this cell's ceiling + anatomy are its instrument. NOTE the
methodological correction that got us here: on the animacy-POLLUTED 39-candidate pool the in-text lever was
INVISIBLE (masked by inanimate distractors + an applicable-set confound); it took cleaning the pool to genuine
person-vs-person + a MATCHED comparison + CIs to reveal it. The verdict is "partly buildable, partly bounded,"
not "purely external."

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
"multiply the posterior", with the RIGHT signal instead of the refuted coherence prior), on the
animacy-filtered person pool: the struct-dominated bucket rises 0.6139 -> 0.6471, **+0.0332 [0.0016,0.0689]
CI-separated** (marginal), the shuffled-entity TWIN LOSES (-0.006), and NO harm to non-dominated (+0.003). The
channel decomposition is informative: the load-bearing signal is CONTENT (lexical cohesion between the pronoun
clause and the entity's accumulated mention-contexts; +0.0271 [0.007,0.0512]) -- the exact-PREDICATE channel,
strongest as an oracle, WASHES OUT as a fused cue (tunes to weight 0), because it fires sparsely and correlates
with the net's existing signal. On the animacy-POLLUTED full pool the whole thing is NULL (weight 0) -- so the
animacy organ is a REQUIRED gate, and coref/pool quality is the first lever, exactly as predicted.
**This is honest about its size:** the gain is MARGINAL and AT THE DETECTION THRESHOLD -- CI lower bound ~0.001
(deterministic across PYTHONHASHSEED 0/42 but the CI barely excludes 0), and it is SPLIT-FRAGILE (on a 40-doc
subset it falls to +0.006, within noise; the +0.033 needs the full 100-doc / 50-test-doc scale to detect). It
uses gold-NOMINAL grouping (entity histories correctly clustered -- the floor's grouping). So it is a
proof-of-concept that the buildable lever is LIVE and twin-attributable, wired from existing organs, at an effect
size the coref-quality gate caps -- NOT a robust capability win. Do not quote +0.033 as a stable number; quote
"a marginal, threshold-level, twin-controlled realized gain."
The full gain (toward the +0.085 gold-coref ceiling, then external world-knowledge toward 0.73) is the North
Star's to realize with better coref + a richer representation. **PROPOSED hdlab WIRE (Q111, default-off): add an
`accumulated_entity` cue to the graded coref pick = phi_agreement_keep (animacy) + a content-cohesion score from
situation_model_accumulate's per-entity register, fused at a small weight; flag OFF -> byte-identical. It is a
COMPOSITION of two landed organs, not a new mechanism.**

## THE UNIFYING FINDING (for planning -- these are ONE wall)
The who-has-what coref residual (this problem), the WSD override-accuracy a_s residual (my previous problem
`wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector`), and the OPEN priority-1 North Star
are the SAME wall: **the generative "which SPECIFIC one" problem -- picking the specific referent/sense from a
world-knowledge situation model.** Detection/likelihood is maxed in both (coref: the graded pick is near-optimal;
WSD: the directional detector AUC ~0.71); the entire remaining gain lives in GENERATION. This convergence is why
the North Star outranks both -- it is the shared organ.

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
NOT_SEP, oracle 6.9%, regresses non-dominated). NEW, sharper localization (gold-coref past-only ceiling,
decided on the CLEAN person-vs-person pool with a MATCHED apples-to-apples comparison vs global topicality):
the wall is THREE parts -- (1) GLOBAL TOPICALITY (captured by the chain), (2) a BUILDABLE in-text representational
lever (exact-predicate +0.085 [0.034,0.138] and full-context BOW +0.070 [0.012,0.128] beat topicality CI-sep on
the clean person pool; grounded-max NOT_SEP), gated by coref quality and bounded by a ~0.63 gold-coref ceiling,
and (3) EXTERNAL world-knowledge above that (the Garrod-Sanford slow RESOLUTION stage). CORRECTS an earlier
pool-polluted read that called the in-text signal "exhausted" -- on the animacy-polluted 39-candidate pool the
lever is masked; on the clean ~7-candidate pool it is CI-separated. Part (3) is the SAME generative "which
SPECIFIC one" wall as the WSD override-accuracy a_s residual; both are the OPEN priority-1 generative-world-
knowledge situation model. The learner (ON, beneficial for word-meaning) builds word-substitutability, the WRONG
representation for parts (2)-(3), which need an ENTITY-level accumulated representation. NEW: part (2) is now
REALIZED LIVE (not just a gold-coref ceiling) by WIRING two EXISTING organs (the phi_agreement_keep animacy
filter + situation_model_accumulate) into the graded pick -- +0.033 CI-sep (marginal) on the animacy-filtered
bucket, twin loses, no harm, null on the polluted pool (the animacy organ is a required gate). See CONSTRUCTIVE
REALIZATION below. Citations to add: Garrod & Sanford 1994 (bonding/resolution);
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
One label call: I marked this REFUTED -- the brief's proposed mechanism (the coherence next-mention prior) is
the wrong fix and a near-duplicate of an owner-DONE negative. But I ALSO solved the real problem underneath with
a DIFFERENT, correct mechanism (the accumulated-entity content channel, wiring existing organs) to a MARGINAL
CI-separated realized gain (+0.033, twin loses, no harm). If you weight the constructive realization over the
refutation you could read it PARTIAL. I chose REFUTED to stay deflated (the realized gain is marginal, on the
animacy-filtered sub-pool, gold-nominal grouping); the content is identical either way. Your call. Otherwise: none.

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
