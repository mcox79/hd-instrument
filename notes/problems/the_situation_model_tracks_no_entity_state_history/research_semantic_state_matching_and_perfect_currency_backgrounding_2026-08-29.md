# Research drill: semantic (not lexical) state matching + does the perfect background currency?

**For:** SOLVER on `the_situation_model_tracks_no_entity_state_history` (status: SOLVED, extending with two fidelity
upgrades before any hdlab landing). **Dispatched by:** research role, 2026-08-29. **Method:** 4 parallel Sonnet
lit-scan sub-agents (ATL/property-verification; WordNet failure-modes; perfect-currency; aspect wall-check),
synthesized here. Do NOT write code — this is citable literature only. **Copy also placed at**
`notes/research_semantic_state_matching_and_perfect_currency_backgrounding_2026-08-29.md` so it survives a
disk search by name even if this problem folder is archived (the prior aspect-currency drill's note reportedly
did NOT persist to disk per SOLVED.md — this drill deliberately double-writes to prevent a repeat).

---

## HEADLINE

**Upgrade 1 (semantic state matching via synonymy/hypernymy/scalar structure) is PINNED at the representational
level and GO-WITH-BOUNDS as a WordNet-based implementation** — human property/state comprehension is genuinely
graded and feature-based, not lexical-string matching (strong, multi-method evidence), but WordNet is a
lexicographic graph, not a psychological model, and diverges in three specific, well-documented, guardable ways:
**privative adjectives** ("fake"/"former"/"alleged" cancel rather than restrict the noun's properties — WordNet
has no representational slot for this and would wrongly fire hypernym entailment through them), **relative
gradable adjectives** ("tall for a jockey" — context/comparison-class-dependent truth, WordNet has no such
parameter), and **untyped antonymy** (WordNet doesn't distinguish contrary-with-a-middle from
contradictory-with-no-middle, so "not tall" and "not dead" cannot be safely treated the same way).

**Upgrade 2 (aspect-driven currency-CONFIDENCE, PRIOR held with lower confidence than CURRENT/asserted) is NOT
SUPPORTED and would be an overclaim.** No study measures reader confidence/certainty as a function of
perfect-vs-simple marking. The one directly relevant, high-quality, recent experimental result found
(Vos, Minor & Ramchand 2025, eye-tracking) points the OPPOSITE direction: the perfect drove 87-95% commitment
to the result state holding, while simple past showed chance-level (~54%) commitment — i.e. **the perfect is
if anything a MORE reliable cue that a state holds, not a weaker one.** The formal-semantics literature
(McCoard 1978; Iatridou et al. 2001) does not support "current relevance" as a single graded scalar at all — it
splits current-relevance by READING TYPE (target-state readings pattern like non-cancellable entailments;
resultant-state readings are simply silent/unspecified about persistence, which is not the same thing as a
discounted assertion). **Recommendation: do not add a truth-confidence discount tied to PRIOR aspect.** A
DIFFERENT, evidenced mechanism exists and is worth considering instead — an ACCESSIBILITY/salience weight (not
a truth-confidence weight) driven by what gets activated (Ferretti/Kutas/McRae 2007: perfect shifts activation
toward entity/result content and away from process/location content) — but that is a retrieval-ranking
convenience, not a brain-pinned truth-probability mechanism, and must not be used to make PRIOR states more
readily overridden than CURRENT ones without an explicit cancellation cue (that specific behavior is unsupported
and the nearest data argue against it).

---

## QUESTION 1 — SEMANTIC (not lexical) STATE MATCHING

### (a) Is property/state matching genuinely semantic (synonymy + hyponym→hypernym entailment + scalar), not lexical-exact?

**Finding, representational level — STRONG, DIRECT, PINNED.** The anterior temporal lobe (ATL) "hub-and-spoke"
model (**Patterson, Nestor & Rogers 2007**, *Nat Rev Neurosci* 8(12):976-987) holds that concepts/properties are
computed as graded, distributed, transmodal patterns over a high-dimensional conceptual space, not discrete
lexical entries requiring string-identical retrieval. This is triangulated across lesion, TMS, fMRI, MEG and
computational-modeling methods: **rTMS disruption of ATL in healthy subjects reproduces graded (not all-or-none)
semantic degradation matching semantic dementia** (Pobric, Jefferies & Lambon Ralph 2007, *PNAS*); **semantic
dementia patients lose subordinate-level distinctions first while superordinate/category knowledge survives
longer** (Rogers, Lambon Ralph, Garrard et al. 2004, *Psychological Review* 111(1):205-235 — a PDP model showing
this is a direct computational consequence of graded, feature-density-weighted representation, not evidence of a
lexical lookup table degrading). "Ill" and a probe "unwell" therefore occupy overlapping regions of one graded
semantic space in the brain, not two independent dictionary entries.

**Feature-based semantic memory — STRONG for object concepts, MODERATE for state/property concepts.**
McRae, Cree, Seidenberg & McNorgan (2005, *Behavior Research Methods* 37(4):547-559) feature-listing norms show
featural overlap (not string identity) predicts priming, verification RT, and typicality. This is well
replicated for nouns. It has been extended to verbs/state predicates (Vinson & Vigliocco 2002; McRae et al.
2008's object+event norms, *BRM* 40(1):183-190) but with a thinner follow-on literature — flagged as a genuine,
not fatal, asymmetry.

**Property verification — STRONG that verification is graded by semantic distance, MODERATE-INDIRECT that
synonym substitution specifically is verified true with a distance-graded profile.** Smith, Shoben & Rips
(1974, *Psych Review* 81:214-241) and Rips, Shoben & Smith (1973, *JVLVB* 12:1-20) established the
property-verification paradigm: RT/accuracy is a graded function of semantic distance, not binary on string
identity. No dedicated paradigm was found that runs the EXACT case ("ill" stored, "unwell" probed, verify true,
measure RT/N400 as a function of distance) inside a discourse/QA context — this specific combination appears to
be a genuine literature gap, assembled here by extension from adjacent paradigms (word-pair priming, category
verification), not a direct hit.

**Entailment during comprehension (the shattered→broken→damaged chain) — the WEAKEST link, genuinely
contested.** The formal linguistic taxonomy (Fellbaum on verb troponymy/entailment; Levin & Rappaport Hovav on
scalar change-of-state verbs) licenses exactly these entailment chains, but that is lexicographic theory, not
processing evidence. Whether comprehenders AUTOMATICALLY draw such chained entailments online sits inside the
active, unresolved **minimalist (McKoon & Ratcliff 1992, *Psych Review* 99:440-466) vs. constructionist**
inference debate — minimalism predicts only LOCALLY-REQUIRED inferences (e.g. anaphora resolution) are drawn
automatically, not elaborative/downstream entailment chains. The single closest DIRECT reading-time evidence is
**Garrod & Sanford (1977, *JVLVB* 16:77-90)**: reading time for a category-anaphor ("the vehicle") referring
back to a hyponym antecedent ("a bus") is a GRADED function of taxonomic distance, during ordinary silent
reading — this is real, direct, strong evidence that hyponym→hypernym computation happens online, but it is
about REFERENCE RESOLUTION (is this NP co-referring), not PROPERTY-TRUTH VERIFICATION (is this predicate true of
that entity) — a related but distinct task. **Sachs (1967, *Percept Psychophys* 2:437-442)** and
**Bransford & Franks (1971, *Cog Psych* 2:331-350)** are the best support for "meaning, not verbatim wording, is
what's stored and matched" (paraphrases accepted as "the same" at high rates after brief delay; false
recognition of an unpresented sentence that integrates presented meaning) — strong and direct, though a memory
paradigm rather than online comprehension.

**Scalar entailment ("very ill" entails "ill") — PINNED at the FORMAL-SEMANTICS level, THEORETICAL-ONLY at the
processing level.** Kennedy & Levin (2008) and Kennedy (2007, *Ling & Phil* 30:1-45) establish this as a
standard, essentially uncontroversial result of degree semantics (upward monotonicity from a higher point on a
scale to a lower threshold). Real-time processing sensitivity to scale STRUCTURE (relative vs absolute) is shown
behaviorally (Visual World eye-tracking on scalar adjectives), but no study was found that behaviorally
demonstrates spontaneous degree-entailment VERIFICATION the way point-3 verification studies demonstrate
category/feature verification.

**Verdict: PINNED (representational substrate: graded, feature-based, not lexical-string) + PLAUSIBLE
(reference-resolution entailment, scalar entailment as formal semantics) — deflated to P≈0.60-0.65 for the
specific claim that comprehenders treat a chained hyponym→hypernym probe as VERIFIED-TRUE during discourse
QA**, since that exact paradigm has not been directly tested (calibration penalty applied per lit-scan
discipline: base confidence ~0.85 on the representational claim, deflated ~0.20-0.25 for the extension to
"verified as true in a QA context specifically," which is inferred rather than directly measured).

**So the register should:** match state queries via a semantic-distance function (synonym=near, hypernym
1-2 steps=near, unrelated=far), not exact string match — this is well grounded. Do NOT claim the exact
"stored-state, later-synonym-probe, verify-true" paradigm has been directly measured; frame it as a
well-supported extension of adjacent, strong literatures, not a direct replication.

### (b) Is a glass-box WordNet-based matcher (shared synset=synonym; hypernym path=entailment; WordNet-antonym=incompatible) a defensible approximation of the ATL relation, or does it systematically diverge?

**Finding — it is a defensible CHEAP approximation with THREE specific, well-documented, predictable failure
modes, not a psychologically-validated model.** WordNet (Miller 1995; Fellbaum ed. 1998) was built by
lexicographers making dictionary-style sense-splitting judgments, not derived from or validated against
feature-norm/property-listing data — its synset granularity is a lexicographic artifact, not a calibrated
psychological distance. **Budanitsky & Hirst (2006, *Comp Ling* 32(1):13-47)**, the canonical evaluation paper,
shows WordNet path-based measures are fundamentally SIMILARITY (taxonomic) measures and systematically
under-score real human-judged RELATEDNESS that isn't taxonomic (car–gasoline: strongly related, not similar).

**Failure mode 1 — PRIVATIVE ADJECTIVES (the single most important failure mode).** Kamp & Partee (1995,
*Cognition* 57:129-191) formalize the intersective/subsective/privative/non-subsective adjective typology:
"fake gun" is NOT a member of GUN (can't fire — privative, denotation intersects the noun's extension in the
EMPTY set); "former soldier" does NOT entail currently-a-soldier; "alleged criminal" entails NEITHER criminal NOR
not-criminal (suspended, non-subsective). WordNet has **no adjective-type feature anywhere in its data
model** — it stores lexical relations between synsets, not compositional operations over adjective+noun pairs.
A hypernym-path matcher walking "gun" in "fake gun" produces the exact same chain (→weapon→instrument→artifact)
as it would for bare "gun," firing false entailments. This is the sharpest, cleanest wall-check item: **any
[privative-modifier]+[noun] construction where a matcher would otherwise fire a hypernym/synonym entailment from
the bare noun is wrong.** Privative-modifier set to guard against: fake, former, alleged, counterfeit, ex-,
would-be, pretend, fictional, so-called, self-proclaimed, erstwhile, wannabe.

**Failure mode 2 — RELATIVE GRADABLE ADJECTIVES (context/comparison-class-dependent truth).** Kennedy (2007)
and Kennedy & McNally (2005, *Language* 81(2):345-381): relative gradable adjectives (tall, short, expensive,
warm — open scale) have a comparison-class-dependent threshold; "tall for a jockey" and "tall for a basketball
player" can pick out DISJOINT height ranges for the same word. WordNet stores "tall" as one fixed synset with
no scale, no endpoint type, and no comparison-class parameter — so it would treat "tall jockey" ≈ "tall person"
≈ "tall basketball player" as the same claim. Absolute gradable adjectives (full, empty, straight, dead — closed
scale, fixed endpoint) are comparatively SAFE for a symbolic matcher — this is a useful partition: guard relative
gradables (tall/short/warm/expensive/heavy/young/old/strong/fast — high risk), treat absolute gradables (full/
empty/dead/straight/clean/closed/open — endpoint-based) as lower risk.

**Failure mode 3 — UNTYPED ANTONYMY (contrary vs contradictory).** Fong (2004, *J Logic Lang Inf* 13:159-171)
identifies this directly as WordNet's central defect for exactly this kind of inference: WordNet's antonym edge
does not distinguish **contradictories** (alive/dead, open/closed — no middle, negating one entails the other)
from **contraries** (hot/cold, tall/short, happy/sad — middle exists, negating one does NOT entail the other;
"not tall" leaves open "average height"). Kennedy's relative/absolute typology maps directly onto this: absolute
(closed-scale) adjectives pattern as contradictories; relative (open-scale) adjectives pattern as contraries.
**Gotzner & Alexandropoulou (2024, *J Semantics* 41(3-4):373-399)** experimentally confirm exactly this
asymmetry: negated absolute adjectives ("not clean") show strong near-entailment strengthening toward the
antonym ("dirty"); negated relative adjectives ("not large") show a much weaker, non-entailing pattern
(could be "medium"). **Also: "not unwell" is NOT simply "well"** — Tessler & Franke (2018, CogSci, "Not
unreasonable") show double negation of a morphological contrary ("un-X") pragmatically lands on a weak-middle
region ("okay," "not particularly sick"), not the positive pole — a naive not(antonym(X)) = positive-pole rule
is wrong here too. Also, WordNet's antonym relation is structurally SPARSE and asymmetric: it lives only on
"head synsets" (satellite synsets attached via `similar-to` get only an INDIRECT antonym), adjectives dominate
(~3,998 of ~7,600 total antonym pairs) while cross-part-of-speech opposition (alive/adj vs. died/verb) is
invisible to the antonym pointer entirely.

**RTE-era corroboration.** PASCAL RTE-challenge-era analyses of WordNet-relation-based entailment systems found
they simultaneously OVER-generate (false positives from loose/wrong-sense matching, e.g. polysemy routing
through the wrong synset) and UNDER-generate (missed entailments from coverage gaps, missing domain senses) —
Sammons, Vydiswaran & Roth (2010, ACL, "Ask Not What Textual Entailment Can Do for You") additionally note
aggregate accuracy figures hide which specific phenomenon (lexical vs syntactic vs coreference) drove any given
pass/fail, so a single "WordNet entailment accuracy" number cannot be trusted as evidence the matcher is reliable
without phenomenon-level breakdown.

**Verdict: OUR-INVENTION-AS-APPROXIMATION, WITH NAMED FAILURE MODES — defensible only WITH guards.** Not PINNED
(WordNet is a lexicographic artifact, not a psychological model; Budanitsky & Hirst is explicit that its
measures are evaluated AGAINST human judgment, not derived FROM it). Confidence that these three failure modes
are real and will bite in practice: HIGH (P≈0.80 — this is characterization of known, well-documented,
reproduced limitations, not novel synthesis, so less deflation applies here than to Q1a/Q2).

**So the register should:** ship the WordNet-based matcher as a CHEAP APPROXIMATION with three MANDATORY guards,
not optional refinements: (1) a privative-modifier blocklist that suppresses hypernym-entailment firing through
"fake/former/alleged/ex-/would-be/pretend/counterfeit/fictional/so-called" + noun spans; (2) a relative-vs-
absolute gradable-adjective flag (relative gradables — tall/short/warm/expensive/heavy/young/old/strong/fast —
should NOT transfer truth across different entities/comparison classes; absolute gradables — full/empty/dead/
straight/clean/open/closed — are safe); (3) type every WordNet antonym pair by scale structure before using it
as an "incompatible/closes-the-prior-state" signal: closed-scale (contradictory, negation-safe) vs open-scale
(contrary, negation NOT safe — "not tall" ≠ "short"), and treat "not un-X" (double negation of a morphological
contrary) as landing in a weak-middle zone, not at the positive pole.

---

## QUESTION 2 — DOES THE PERFECT BACKGROUND CURRENCY?

**Direct answer to the SOLVER's binary design question: the literature does NOT support adding a
currency-CONFIDENCE value that is lower for PRIOR (perfect) than for CURRENT/RESULT (asserted) states. A
PRIOR-open state is, on the available evidence, functionally indistinguishable in truth-confidence from a
CURRENT-open state until contradicted — exactly the binary open/until-explicitly-cancelled design SOLVED.md
already built. Adding a scalar discount on top would be adding an untested mechanism, and the nearest direct
test argues it would point the WRONG DIRECTION.**

**1. "Current relevance"/Extended-Now theory (McCoard 1978; Iatridou, Anagnostopoulou & Izvorski 2001, in
*Ken Hale: A Life in Language*, MIT Press, pp.189-238) — THEORETICAL-ONLY, and the theory itself resists a
"graded confidence dial" framing.** Current-relevance effects are NOT treated in this literature as one unified,
smoothly graded pragmatic default. They split by READING TYPE: **target-state perfects** ("the light has gone
off") are characterized as carrying a result-state inference that is standardly treated as **entailed to hold**
at speech time and is described in the literature as **not a cancellable conversational implicature** — cancelling
it requires an explicit undoing EVENT in the world ("...but I've switched it on again"), not a discourse hedge.
**Resultant-state (weak) perfects** ("John has been to Paris") are simply **silent** about present persistence —
not asserted, not discounted, just unspecified. A system built on "perfect = discounted confidence" would be
conflating "not-at-issue/unspecified" with "asserted-but-doubted," which the formal semantics explicitly treats
as two different things.

**2. Magliano & Schleich (2000, *Discourse Processes* 29(2):83-112) and Madden & Zwaan (2003, *Mem Cogn*
31(5):663-672) — WRONG DIMENSION, do not cite as support.** These manipulate **perfective vs imperfective
VIEWPOINT aspect** ("raked the leaves" vs "was raking the leaves") — a different grammatical category from the
perfect/non-perfect (relative-tense/"taxis") opposition. Real, replicated finding (imperfective keeps an event
more accessible/foregrounded than perfective), but it is about ongoing-vs-completed EVENTS, not about perfect-vs-
simple STATE assertions, and citing it as evidence for the perfect-currency hypothesis would be exactly the
aspect/aspect-category conflation this drill was asked to check for.

**3. Ferretti, Kutas & McRae (2007, *JEP:LMC* 33(1):182-196) — the correct minimal pair (perfect vs
imperfective), but tests ACTIVATION CONTENT, not confidence.** Three experiments (priming, sentence completion,
ERP) converge: perfect ("had skated") does NOT prime associated LOCATIONS the way imperfective ("was skating")
does (21ms facilitation for imperfective, none for perfect); perfect completions bias toward NOUN PHRASES
(entities); N400 shows location-expectancy sensitivity only in the imperfective condition. Authors' own
interpretation: perfect shifts activated event-knowledge toward the RESULTANT/entity phase and away from the
ongoing-PROCESS/location phase, because "the continuing relevance of [location] diminishes" once an event is
complete — a real, well-evidenced backgrounding of PROCESS/LOCATION content. **This paper never measures
certainty, confidence, or willingness-to-revise** — extending "location gets backgrounded" to "the state's
present-truth is held less confidently" is an inferential leap the data do not license.

**4. Foreground/background traditions (Hopper 1979; Givón; Chafe) and Carreiras, Carriedo, Alonso & Fernández
(1997, *Mem Cogn* 25(4):438-446) — adjacent constructs, and the one closest-in-spirit study tests a DIFFERENT
contrast.** Hopper's foreground/background is about NARRATIVE SEQUENCING (perfective=foreground, moves the plot;
imperfective=background, scene-setting) — an entirely different, non-epistemic notion from "how confident am I
this is still true." Carreiras et al. (1997) — the paper closest to the SOLVER's question — actually manipulates
**simple PRESENT vs simple PAST** ("is a lawyer" vs "was a lawyer"), finding present-tense-marked (currently-true)
attributes are MORE accessible (faster probe recognition) than past-tense-marked (no-longer-current) attributes.
This is real, relevant support for the GENERAL principle that grammatical currency-marking changes accessibility
— but it is evidence about SIMPLE tense, not the PERFECT, so it cannot be cited as direct support for a
perfect-specific mechanism without an unlicensed generalization step.

**5. The most direct test found, and it argues AGAINST the hypothesis — Vos, Minor & Ramchand (2025,
*English Lang & Ling* 30(2):339-367, Cambridge), Visual World eye-tracking.** Simple past vs perfect
(past AND present) with accomplishment verbs, two-picture choice (ongoing action vs completed result).
**Simple past: ~54% completed-picture choice — chance level, no reliable gaze clustering toward the result
state.** **Perfect (past or present): 95%/87% completed-picture choice — near-ceiling, highly reliable gaze
clustering (p<.0001).** The authors also tested whether narrative context could push simple past toward a
result-committed reading and found it could NOT — the simple past's weak commitment is structurally robust, not
a pragmatically fragile default that context easily strengthens. **This is the opposite polarity from the
SOLVER's hypothesis**: if anything, the perfect is the MORE reliable signal that a state holds, and the simple
past is the one closer to "genuinely uncertain." Caveats limiting generalization: this tests commitment
IMMEDIATELY following event culmination (not long-run persistence to a much-later point), uses accomplishment-
verb target-state readings (not stative predicates like "was a soldier"), and does NOT test cancellation cost
under later explicit contradiction. **No reading-time or plausibility-judgment study comparing the processing
cost of cancelling a perfect-marked state vs a simple-tense-marked state was found** — this exact paradigm does
not appear to exist in the literature.

**6. Overall calibration (explicit per the SOLVER's request):** the claim "aspect changes a stored
truth-confidence value, PRIOR lower than CURRENT" is **(c) NOT SUPPORTED / would be an overclaim** if presented
as a real brain mechanism. It borrows vocabulary from three genuinely-established but DISTINCT literatures
(current-relevance semantics, situation-model accessibility, narrative foreground/background), conflates them
with each other and with a construct (graded belief in present truth, differentially cancellable) that none of
them measures, and the one study that directly compares perfect against simple tense on a state-commitment
measure found the perfect to be the MORE, not less, reliable cue.

**Verdict: OUR-INVENTION-UNDER-TEST, and the strongest available evidence argues to REJECT the specific
mechanism as framed (lower confidence for PRIOR).** P for "this mechanism is a real, brain-faithful confidence
discount" ≈ 0.10-0.15 after calibration — this is close to a refutation, not merely an unproven hypothesis; per
calibration discipline the deflation is applied to the POSITIVE claim, not to the confidence of the refutation
itself, which rests on one well-designed recent study plus a coherent theoretical account that independently
predicts the same conclusion (silence ≠ discount).

**So the register should:** NOT add a scalar truth-confidence field that discounts PRIOR-aspect states relative
to CURRENT/RESULT ones. Keep the existing binary design (default-persist until an explicit incompatible-state
cancellation cue) — it is already the best fit to what the formal semantics says (silence about persistence,
not a discounted assertion) and is not contradicted by any experimental finding. **If a distinct ACCESSIBILITY
weight is wanted for a different purpose (e.g. ranking which facts surface first in a downstream retrieval/QA
step, not adjudicating truth)**, the evidenced version of that is: perfect-marked states carry entity/result
content preferentially over process/location content (Ferretti et al. 2007) and simple-past-marked (definitively
non-current) content is less accessible than simple-present-marked (currently-true) content (Carreiras et al.
1997) — but label this an ACCESSIBILITY/salience convenience, OUR-INVENTION, not a brain-pinned confidence
value, and do not let it change which cancellation cues the register accepts.

---

## QUESTION 3 — WALL CHECK

Compact guard list, each with the citation basis (or explicit flag where citation support is thinner):

| # | Construction | Naive failure | Fix / guard | Basis |
|---|---|---|---|---|
| 1 | **Privative adjectives** — "fake gun," "former soldier," "alleged criminal," "fictional detective" | Hypernym-path fires through the bare noun, asserting the cancelled/suspended property | Blocklist: fake, former, alleged, counterfeit, ex-, would-be, pretend, fictional, so-called, self-proclaimed, erstwhile — suppress entailment firing when noun is modified by these | Kamp & Partee 1995; Partee privative-adjective work — STRONG |
| 2 | **Relative gradable adjectives, comparison-class-dependent** — "tall for a jockey" | Treats "tall" as one fixed truth value transferable across entities/contexts | Flag relative gradables (tall/short/warm/expensive/heavy/young/old/strong/fast) as non-transferable across entities without the same comparison class; absolute gradables (full/empty/dead/straight/clean/open) are lower-risk | Kennedy 2007; Kennedy & McNally 2005 — STRONG |
| 3 | **Untyped antonym / contrary vs contradictory** — "not tall" ≠ "short"; "not unwell" ≠ "well" | Treats every WordNet antonym-edge negation as flipping fully to the opposite pole | Type each antonym pair by scale structure (closed-scale=contradictory=safe to flip; open-scale=contrary=NOT safe, negation leaves a middle); double-negation of morphological "un-X" lands in a weak-middle zone, not the positive pole | Fong 2004; Gotzner & Alexandropoulou 2024; Tessler & Franke 2018 — STRONG |
| 4 | **Habitual "used to"** — "he used to be a soldier" | Treated identically to perfect "had been X" for currency purposes | "used to" carries a STRONGER (near-conventional) discontinuity implicature than "had been X" — weight it more heavily toward non-currency, do not conflate with the pluperfect's genuinely neutral default | Comrie 1976 — MODERATE (description-level, standard reference, no dedicated processing study found) |
| 5 | **Counterfactual/irrealis** — "if he had been a soldier, he would have..." | Asserts the embedded state into the real narrative timeline | Detect if-clause / subjunctive "were" / modal-perfect ("would/could/might/should have") frames and SUPPRESS assertion into the real-world model entirely — not just discount, exclude | Iatridou 2000 (*Ling Inq* 31(2):231-270) — STRONG |
| 6 | **Negation scope** — "he had never been a soldier," "he had not been ill" | Span-matcher extracts the bare positive-state predicate and only discounts currency, rather than negating existence of the state entirely | Check for negation ("never," "not," "no") in scope over the FULL state predicate before binding; a negated state predicate should not enter the register as a positive span at all | Kaup, Lüdtke & Zwaan 2006; MacDonald & Just 1989 — STRONG (note: their finding is about ONLINE/incremental representation timing, less directly applicable to an offline symbolic parser, but the scope-handling implication is separable and solid) |
| 7 | **Resultant state narrated BEFORE its causing event (flashback / anti-iconic order)** — "The house was in ruins. It had burned down last winter." | Timestamps states/events by narration position, placing the ruined-state before the burning-event in the internal timeline | Pluperfect + resultative-state predicates should trigger a search (forward or backward) for the licensing event rather than defaulting to narration-order timestamping; this is a genuine extra-processing-cost case for humans too, not merely an implementation edge case | Zwaan 1996 (iconicity/time-shift processing cost); Bohan & Sanford-lineage 2019 iconicity-bias study (*Memory* 27(8)) — MODERATE-STRONG |
| 8 | **Evidential/reportative framing** — "she was known to be ill," "was said to be," "seemed" | Asserts the embedded state with the same confidence as direct narrator assertion | Tag as source-attributed/lower-confidence, distinct from direct narrator assertion — this is a genuinely different (and better-evidenced-for-a-confidence-dimension) place to put a confidence gradient than aspect itself | General evidentiality/epistemic-stance + free-indirect-discourse literature — WEAKER (construction-identification supported, no direct psycholinguistic-processing citation located) |
| 9 | **Archaic BE-perfect** — "was become," "is grown," "was come" (19c) | Have-only perfect detector misses it; BE+past-participle surface shape gets misparsed as PASSIVE ("was become [by X]") | Check BE + past-participle-of-known-mutative-intransitive-verb (become, grow, come, go, fall, arrive, wax) with no agent/by-phrase as a candidate archaic PRIOR-aspect perfect, not default to passive; this directly confirms and fixes the residual SOLVED.md already flagged ("archaic BE-perfect ... tagged CURRENT not PRIOR, a minor fidelity gap") | Kytö 1997; Rydén & Brorström 1987 — STRONG on the historical-linguistics side |
| 10 | **Archaic property vocabulary, semantic drift** — "consumptive," "vexed," "genteel," "amiable" | Modern WordNet sense/synset may not match the 19c period sense, producing wrong-synset synonym/hypernym matches | No specific fix beyond flagging for period-sense mismatch risk; general semantic-drift phenomenon, not word-list-specific evidence located | General historical-semantics literature — WEAKEST (flagged as description, not citation) |

---

## SUMMARY

| Upgrade | Verdict | Recommendation | One-line reason |
|---|---|---|---|
| **1. Semantic (WordNet-based) state matching** — synonymy/hypernymy/scalar replacing lexical-exact | PINNED (representational level) / OUR-INVENTION-AS-APPROXIMATION (the WordNet implementation) | **GO-WITH-BOUNDS** | Human state-matching is genuinely semantic (strong, multi-method evidence), and WordNet is a defensible cheap approximation — but ONLY with the three named guards (privative blocklist, relative-gradable context-flag, typed antonymy); shipping without them will produce concrete, predictable, named failures (fake-X, tall-for-Y, not-tall≠short). |
| **2. Currency-CONFIDENCE field (PRIOR < CURRENT)** | OUR-INVENTION-UNDER-TEST, and the best available evidence points AGAINST it | **NO-GO** (as literally framed) | No direct evidence supports a truth-confidence discount for perfect-marked states, and the one directly relevant experimental result (Vos et al. 2025) found the opposite polarity — the perfect is the MORE reliable currency signal, not the weaker one; keep the existing binary open-until-explicitly-cancelled design instead. |

**Does the 19c LitBank corpus age change any of this?** For Upgrade 1: modestly — archaic property vocabulary
("consumptive," "vexed," "genteel") carries a real but under-documented risk of period-sense mismatch against
modern WordNet synsets (item #10 above), worth a light audit but not a blocking concern. For Upgrade 2: **yes, in
one concrete and useful way** — the archaic BE-perfect ("was become," "was grown") is a coverage gap, not a
semantics gap: the perfect/current-relevance mechanism itself (McCoard, Iatridou et al.) describes English
generally and applies unchanged to 19c prose, but a HAVE-only perfect detector will silently miss the BE-perfect
variant and likely misparse it as a passive. This directly confirms and gives a concrete mechanism for the
residual SOLVED.md already flagged under "What I did NOT establish" (archaic BE-perfect tagged CURRENT not
PRIOR) — item #9 in the wall-check table is the fix.

---

## Cheap decisive test

**For Upgrade 1:** build two small held-out probe sets against the existing `state_register.py` /
`StateReader` extraction pipeline — (A) a synonym/hyponym/scalar set (e.g. "ill"→query "unwell";
"shattered"→query "damaged"; "very ill"→query "ill", ~30-50 pairs), and (B) a matched "trap" set exercising
each of the three named failure modes (privative: "fake soldier"/query "soldier"; relative-gradable:
"tall for a jockey"/query "tall" against a different-comparison-class entity; untyped-antonym:
"not tall"/query "short", "not unwell"/query "well"). Measure precision/recall on both. HARD-PASS: adding the
three guards (blocklist, gradable-flag, typed-antonym) fixes ≥80% of set B without regressing set A by more
than a small, CI-bounded margin. HARD-FAIL: the guards cost more true-positive recall on set A than they
recover on set B (net negative), or a hand-audit of real LitBank-extracted state pairs shows WordNet's
hypernym/antonym relation is simply wrong (not just under-specified) on >15% of cases.

**For Upgrade 2:** on the existing construction-gold population (`exp_state_register_query_v1`, n=420, already
at 1.000), build a variant register (B) that adds a scalar confidence discount for PRIOR-aspect spans, alongside
the current binary design (A). Run both on the SUPERSEDE-mechanism subset (same-slot cancellation without an
explicit antonym cue — the one channel SOLVED.md already flagged as measured-but-rare in real prose, ~0
incidence). HARD-PASS for building the confidence field: (B) recovers cases (A) gets wrong, CI-separated, on a
held-out population enriched for long-narrative-distance PRIOR-state queries. HARD-FAIL (the predicted outcome
per this literature review): (B) shows no measurable improvement over (A), or actively degrades recovery of
legitimately-persisting PRIOR states — consistent with Vos et al. 2025's finding that the perfect is not the
weaker signal.

---

## Cross-thread synthesis with prior entries

Confirms and refines the PINNED finding already in `SOLVED.md` / the prior aspect-currency drill: "perfect
aspect routes to the entity/resultant-state layer" (Ferretti/Kutas/McRae 2007) is reconfirmed here with the
precise mechanism (activation shift toward entity/result content, away from process/location — not a
confidence effect). "The perfect's currency is a cancellable pragmatic default (open-through-R), NOT
entailed-closed" is reconfirmed and SHARPENED: the formal-semantics literature treats this as READING-DEPENDENT
silence-about-persistence (resultant-state readings) or near-non-cancellable entailment (target-state
readings) — not a single graded confidence dial — which argues the EXISTING binary design (persist-until-
explicit-cancellation) is already the best fit, and a proposed scalar confidence upgrade would be a step AWAY
from, not toward, brain fidelity. This closes the loop on SOLVED.md's own flagged residual (archaic BE-perfect
mistagging) with a concrete, sourced mechanism (item #9).

## Substrate-product implications

Both findings are directly actionable for the reader substrate, not publication-framed. Upgrade 1, built with
its three guards, would let the reader answer "is X unwell?" / "is the vase damaged?" correctly without
requiring the exact stored wording — a real comprehension capability, cheap to build (WordNet is already
on-disk-available, glass-box, no external LLM at inference). Upgrade 2, as originally framed, would have spent
build effort on a mechanism the literature argues does not exist and might make results WORSE (discounting the
more-reliable signal); redirecting that effort toward the ACCESSIBILITY-weight framing (if wanted at all) or
toward evidentiality/reportative-marking (item #8, which has a more plausible link to a genuine confidence
dimension) is the better use of the same effort.

## Citations (verified count)

**37 distinct scholarly citations** with author/year/venue collected across the 4 lit-scan sub-agents (full
citation lists with URLs are preserved in each sub-agent's returned report; not re-listed exhaustively here to
keep this note scannable — the load-bearing ones are inlined above with full author/year/venue on first
mention). Strength distribution, self-assessed by the sub-agents and re-checked in synthesis: ~18 STRONG/DIRECT,
~11 MODERATE/INDIRECT-BUT-RELEVANT, ~8 THEORETICAL-ONLY-OR-DESCRIPTION-LEVEL (explicitly flagged inline where
used). No citation here was independently full-text-verified beyond what WebSearch/WebFetch returned (abstracts,
secondary summaries, and in most cases at least partial full text) — per lit-scan discipline, treat page-number-
level bibliographic details as spot-check-before-verbatim-quote, not bibliographically final.
