# Research: richer context-KEY for sense/affect selection + raising glass-box extraction coverage (2026-08-07)

**Trigger:** two linked questions at the shared bottleneck: (A) how is the CONTEXT KEY that collapses a
polysemous/context-dependent word to the right sense+affect selected (spoil->ruin vs spoil->pamper)? (B) how
does a reliable SITUATION MODEL get extracted from open prose in glass-box fashion, and what raises coverage
(currently ~71-75% precise, ~30-50% coverage)? KB-checked first against `notes/PLAN_B_grounding_word_context_
affect_superposition_map_2026-08-07.md` (today's plan of record for A), `notes/deepdrill_sense_disambiguation_
cues.md` (2026-08-05 brain drill for A), `notes/formalize_situation_model_DMN_integration_spec_2026-08-06.md`
+ `notes/coverage_wall_decomposition_2b_ceiling_and_referent_did_it_happen_2026-08-06.md` (B), and the three
2026-08-06 prior-art scans (classical symbolic / modern neuro-symbolic / VSA-HDC). This drill does NOT re-run
those — it fills the specific gap each left open: PLAN_B's own honest boundary names "richer context keys"
as the unbuilt next increment; the coverage-wall note names OOV/light-verb result-class starvation as one
concrete blocker. Three parallel Sonnet lit-scan sub-agents dispatched (generic NLP/cog-sci terms only, no
project-specific framing off-platform), one per angle: (A) context-key techniques, (B) coverage-raising
techniques, (C) confirm-the-wall + best partial lever.

## HEADLINE

Both halves of the bottleneck have a NAMED, well-precedented, cheap, glass-box computational analog that was
missing from our prior scans. (A) The brain's own strongest local sense-selection cue (governor/selectional-
restriction, per the 2026-08-05 drill) has a direct, decades-old, purely-corpus-count computational form —
Resnik (1996) selectional association / Erk & Pado (2008) structured per-role distributional profile / VerbNet-
Levin class membership — that turns our single scalar (patient animacy) into a small BUNDLE of typed slots,
composable with the ALREADY-PROVEN Stage-3 superposition/bind/bundle mechanism (`04af969c4`, HARD_PASS) without
touching its architecture. (B) VerbNet/Levin verb-CLASS backoff for out-of-vocabulary predicates (Swier &
Stevenson 2004: 50-65% error-rate reduction over a lexicalized baseline, fully unsupervised, zero training
corpus) is a directly-measured, well-evidenced technique that maps onto our own already-diagnosed blocker
("goal verb get/give/make/find/see/do/have, OOV or light, yields NO result-class" — `coverage_wall_
decomposition_2b...md`). Separately, a genuinely NEW lead not surfaced by the 2026-08-06 prior-art scans:
Odin/Eidos (Valenzuela-Escarcega et al. 2015; Sharp et al. 2019) — a cascade rule-grammar with syntactic +
token-level FALLBACK matching (recovers when the parser fails) applied to open-domain causal-relation
extraction on real news/report text — is the closest published near-miss to a robust glass-box extractor, but
its own coverage numbers could not be verified this session (PDF fetch failures on both sides), so it is a
LEAD not an existence-proof. The 45-year wall is RECONFIRMED and SHARPENED: this scan found no glass-box
system, of any era or tradition, with a verified coverage number above ~50-70% on genuinely open (non-
templated) prose for ANY event-structure-extraction task, not just goal-outcome specifically (calibrated
P(open/unsolved field-wide)=0.83, from the confirm-the-wall sub-agent, itself deflated by this note to 0.65 per
the standing lit-scan calibration penalty).

---

## 1. Brain mechanism (carried forward, not re-drilled — already verified 2026-08-05/06)

**(A) Context-key selection.** Semantic CONTROL network (LIFG BA45/47) implements biased competition over
candidate senses held/interfaced by pMTG, with FOUR cues firing near-simultaneously within ~100-200ms
(`notes/deepdrill_sense_disambiguation_cues.md`, live-verified 2026-08-05): (1) dominance/frequency prior
(Giora) — always fires first, unconditionally; (2) syntactic governor / selectional restriction / argument-
structure fit — the strongest LOCAL override, near-categorical when a hard mismatch exists; (3) local
lexical/collocational association (graded thematic fit) — fills in when no categorical mismatch exists; (4)
discourse/situation-model context — slower-building, the only source resolving cross-clause/anaphoric cases.
Full resolution (including active suppression of the loser) extends past 400ms — genuinely recurrent, not
feedforward-only. The ATL semantic hub supplies the underlying graded, amodal, cross-modal-feature-correlation
REPRESENTATION that this competition selects over (`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`).
**This drill's field scan (Section 2 below) directly targets cue (2) and (3): what is the CHEAPEST, most
directly-quantified computational analog of the governor/selectional-restriction cue** — the answer is Resnik
selectional association / VerbNet class membership, below.

**(B) Situation-model extraction/coverage.** Default Mode Network (PCC/precuneus hub, mPFC, angular gyrus,
lateral temporal/ATL, hippocampus/MTL) integrates the stream of role-bound propositions from language cortex
into ONE amodal, continuously-updated model, segmented at prediction-error boundaries (Hasson/Baldassano/Chen
temporal-receptive-window hierarchy), handing completed events to the hippocampus for relational binding
(`notes/formalize_situation_model_DMN_integration_spec_2026-08-06.md`). The brain's coverage is high because
(i) grounded world knowledge supplies priors for implicit/unstated content (the analog of implicit-argument
recovery, Section 2B below), (ii) prediction pre-activates likely continuations before they're stated, and
(iii) integration is WHOLE-PASSAGE and parallel across many cues at once, not a single local-clause pipeline —
exactly the "no single accumulating situation model" gap our own audit already diagnosed as the wall's root
cause. This drill does not re-litigate that diagnosis; it adds two NEW, narrower coverage-raising levers
(Section 2B) that are complementary to the integration-register build already planned (2a-2d).

---

## 2. Field techniques (NEW this session; each judged adopt/adapt/not-applicable vs our owned organs)

### (A) Context-conditioned sense/affect selection — richer context-KEY techniques

| Technique | Mechanism | Glass-box? | Verdict vs our organs |
|---|---|---|---|
| **Resnik (1996) selectional association** | `SelAssoc(v,c) = P(c|v)*log(P(c|v)/P(c)) / SelStr(v)` computed from parsed-corpus verb-argument counts mapped onto a WordNet noun-class hierarchy — yields a DISTRIBUTION over many semantic classes per argument slot, not one bit. | Fully classical: corpus counts + WordNet + closed-form log-ratio. Cheap (no neural training). | **ADOPT.** Directly generalizes our single animacy scalar (which IS a degenerate 2-class case of this) to a multi-class per-slot distribution, using resources (WordNet) already load-bearing elsewhere in the substrate. |
| **Wilks preference semantics (Fass & Wilks 1983)** | Hand-built semantic primitives (ANIMATE, HUMAN, PHYSOBJ, ABSTRACT...) per sense, matched via template unification with GRADED least-violation scoring (a preference, not a hard filter) — several primitives checked per slot at once. | Fully symbolic. | **ADAPT.** The graded multi-primitive-per-slot design (not our current hard animacy bit) is the right shape; the primitive INVENTORY should be small and reused, not hand-authored per word. |
| **Erk & Pado (2008/2010) structured distributional / exemplar models** | Each predicate gets a per-ROLE selectional-preference vector = centroid (or PMI-weighted exemplar set) of the distributional vectors of its typical fillers; disambiguation combines the argument's own vector with the predicate's role-vector. | Fully count-based (co-occurrence + cosine/centroid), no gradient training. | **ADAPT, longer-term.** Compatible with `hdlab/random_indexing.py`'s already-proven accumulator (per `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`) — a per-role centroid is a natural VSA bundle. Second-order build, not the first increment (needs the lexical-similarity organ itself to mature first). |
| **VerbNet / Levin (1993) verb classes** | ~270+ classes bundle thematic roles + selectional restrictions + syntactic-alternation frames; class membership lets a NEVER-SEEN verb inherit its class-mates' restrictions by analogy. | Fully symbolic hand-built resource; cheap to USE (lookup), expensive only to construct originally (already exists, reusable). | **ADOPT, highest near-term value.** This is the SAME mechanism needed for coverage (Section 2B) — one resource, two uses (richer context key AND OOV-verb generalization). Directly answers our own named blocker (OOV/light goal verbs with no result-class). |
| **Multi-cue WSD fusion (Yarowsky decision lists; IMS-style joint feature vector: POS + collocation window + syntactic-dependency features into one classifier)** | Explicitly fuses several cue CHANNELS into one joint context signal rather than a single feature. | Classical (decision lists / SVM over hand features); needs sense-tagged training data as the one non-free ingredient. | **NOT-APPLICABLE as-is** (training-data-hungry), but the ARCHITECTURE (joint multi-channel feature vector -> one competition) is exactly what the brain-mechanism section above prescribes and what our VSA bind/bundle already implements natively without needing supervised training data — the field's "trained classifier" role is played by our OWN bundle+cleanup. |
| **Wilson, Wiebe & Hoffmann (2005/2009) contextual polarity** | Prior-polarity lexicon + NEGATION-SCOPE rules + intensifier/diminisher detection + dependency modifies/modified-by features, fused via rule cascade/small classifier — the DIRECT affective-polarity analog (not just sense) of the multi-cue idea. | Cheap: lexicon + parser + hand rules. | **ADOPT, second slot.** This is the piece our "spoil" example specifically needs beyond sense selection: the AFFECT DIRECTION depends on negation/intensifier scope, not just which sense fired. Directly complements PLAN_B Layer 2 (context->affect binding). |
| **Mitchell & Lapata (2010) / Baroni & Zamparelli (2010) compositional distributional semantics** | Elementwise combination (add/multiply) of constituent word vectors, or a per-word LINEAR MAP (adjective-as-matrix) reweighting the head noun's whole profile — composes a joint context representation from multiple words' full distributional content. | Fully classical (vector arithmetic / closed-form least squares). | **ADAPT, longer-term.** A natural fit for VSA binding generally (binding already IS a composition operator); the adjective-as-matrix idea is a richer alternative to simple binding worth flagging for a future increment, not this one. |

### (B) Raising glass-box extraction coverage

| Technique | Mechanism | Measured coverage/lift | Verdict vs our organs |
|---|---|---|---|
| **VerbNet/Levin class-backoff for OOV predicates (Swier & Stevenson 2004)** | Verb instance -> VerbNet class -> pool class-mates' argument-structure evidence; role assignment for a never-seen verb proceeds by analogy to its class, no per-verb training needed. | **50-65% error-rate reduction** vs a lexicalized (non-class) baseline; first fully unsupervised SRL method, needs NO annotated corpus. | **ADOPT, top near-term lever.** Directly maps onto our own diagnosed blocker: `find_desired_state` fires but "every desired-state has `classes: set()` — the goal verb (get/give/make/find/see/do/have, OOV or light) yields NO result-class" (`coverage_wall_decomposition_2b...md`). A small hand-authored or WordNet-verb-hierarchy-derived class-backoff table (get/give/make/find/see/do/have -> {TRANSFER, CREATION, PERCEPTION, POSSESSION-CHANGE}) is a cheap SUPPLIED-DATA lookup, not a new mechanism — fully compliant with the supply-data/earn-mechanism line. |
| **Open IE pattern generalization (TextRunner -> ReVerb -> OLLIE -> ClausIE -> Stanford OpenIE)** | Progressive move from learned patterns to fully deterministic clause-type detection over a dependency parse (ClausIE: SVOO/SVOC/etc. -> extraction rule per clause type, no learned weights at all). | Each successor reports large relative gains over its predecessor (ClausIE: 2.5-3.5x more correct propositions than OLLIE at comparable precision); absolute open-text coverage numbers were NOT found (a field-wide, not just this scan's, gap — flagged by Niklaus et al. 2018's own survey). | **ADAPT.** ClausIE's fully-deterministic per-clause-type rule set is a candidate FRONT-END for our extraction pipeline (turns any sentence into typed clause structures before our role-filler binding runs), but produces generic SVO structure, not goal/outcome relations — would need our own layer on top, not a replacement. |
| **Implicit SRL / zero-anaphora recovery (Gerber & Chai 2010/2012; SemEval-2010 Task 10)** | Discourse-window search (prior sentences) for fillers of locally-empty argument slots, scored by a feature-weighted classifier over syntactic/discourse features + selectional-preference counts. | Implicit arguments add **71% MORE argument instances** than local annotation sees (i.e., the coverage gap addressed is large) but recovers them at only **~F1 50%**. | **ADAPT, matches our own architecture already.** This is structurally the SAME shape as our own window-widening did-it-happen work (`notes/coverage_wall_decomposition_...md`, 2b) — external confirmation that discourse-window search is the right GENERAL move, but also an honest ceiling warning (~50 F1 even in the literature's best case) that our own +4/18 (2b) result and its HARD-FAIL-on-regression finding are IN LINE with, not below, the field's own numbers. |
| **Narrative event chains/schemas (Chambers & Jurafsky 2008/2009)** | Verbs sharing a coreferring "protagonist" argument across a large corpus get PMI-scored into an unsupervised chain — no hand templates, generalizes to any pattern the corpus exhibits. | 72% precision on FrameNet-frame-element alignment (a downstream evaluation, not sentence-level coverage — a genuine metric mismatch flagged by the sub-agent). | **NOT-APPLICABLE near-term** (needs corpus-scale co-occurrence statistics we don't have infrastructure to accumulate cheaply for this specific narrative-goal-outcome task); worth a scope-expansion drill later, not now. |
| **Odin/Eidos cascade rule-grammar with syntactic+token-level fallback (Valenzuela-Escarcega et al. 2015; Sharp et al. 2019)** | A swappable, declarative rule-grammar cascade that matches on token-level patterns WHEN the syntactic parse fails or produces no dependency match — explicit robustness-to-parse-failure design, applied to open-domain causal-relation extraction on real news/report text. | Not independently verified this session (PDF fetch failed both attempts) — throughput (110 sentences/sec) confirmed, precision/coverage numbers not. | **ADAPT, flagged as the most architecturally-relevant NEW lead.** Our own extraction fragility (ECM copula-referent bug, negator-poisoning, single-extraction-path fallthrough) is exactly the failure mode Odin's fallback-tier design targets — a confidence-tiered cascade (try dependency-syntactic match first; if it fails, fall back to a token-level pattern; if that fails, abstain rather than silently mistype) is a genuinely portable ARCHITECTURE pattern independent of whether Eidos's own numbers hold up. Genuinely new vs the 2026-08-06 prior-art scans (none of the three — classical/neuro-symbolic/VSA — surfaced Odin/Eidos). |

---

## 3. TOP 1-2 transferable techniques

**(i) Richer context KEY (beyond coarse animacy):** **Resnik-style per-slot selectional association, backed by
VerbNet/Levin class membership for the verb slot itself.** Concretely: extend the PLAN_B Stage-3 context key
(currently one scalar: patient animacy) to a small BUNDLE of typed slots — {agent-animacy (owned), patient-
semantic-class via a WordNet-noun-hierarchy lookup (new, cheap), verb-class via a hand-authored or WordNet-
verb-hierarchy Levin-style backoff table (new, cheap, DOUBLES as the coverage fix in 3(ii)), negation/
intensifier polarity-shift flag (new, cheap, Wilson-Wiebe-Hoffmann-style)} — each slot bound and bundled with
the ALREADY-PROVEN, unmodified bind/bundle/unbind/cleanup primitives from `04af969c4`. This is the single
cheapest, most directly brain-matched (governor/selectional-restriction is the strongest verified LOCAL cue)
move: it is SUPPLIED DATA (WordNet/VerbNet-derived lookups) composed by an ALREADY-EARNED mechanism, so it
does not cross the supply-data/earn-mechanism line, and it is a strict, additive extension — the existing
6-word HARD_PASS test is a direct regression check.

**(ii) Raising extraction coverage:** **VerbNet/Levin-style verb-class backoff for OOV/light goal verbs**
(Swier & Stevenson 2004's 50-65% error reduction is the best-evidenced number in this entire scan) as the
near-term, immediately-actionable lever — it is the SAME lookup table as 3(i)'s verb-class slot, so building
it once serves both the context-key AND the coverage question. As a second, architectural lever for the
broader pipeline (not a single-increment fix): **cascade/fallback rule matching (Odin/Eidos pattern)** —
dependency-syntactic match first, token-level pattern fallback on parse failure, explicit abstain rather than
silent mistype on total failure — flagged as the best NEW candidate for reducing the class of bugs already
observed in our own extraction fragility (ECM copula-referent, negator-poisoning), though its own published
coverage numbers are unverified and this should be treated as an architecture lead, not a proven lever.

---

## 4. Honest: is glass-box raw-prose->situation-model still an open wall?

**CONFIRMED and SHARPENED.** The 2026-08-06 prior-art scans established that no one ever built a robust
open-domain glass-box GOAL-OUTCOME tracker specifically. This session's scan asked a broader, harsher
question — has ANY glass-box system, for ANY flavor of event/situation-structure extraction, cleared roughly
50-70% coverage on genuinely open (non-templated, non-domain-restricted) prose — and found the same negative,
now with more supporting detail: 1970s-90s script parsers bottlenecked on hand-authored script-library size
(not syntax); pre-neural PropBank/FrameNet SRL capped hard on parser-error propagation and OOV predicates (best
CoNLL-2005 F1 ~79-80% was on GOLD predicate spans within a curated benchmark, not open-text coverage); RST/
discourse parsing state-of-the-art (~55.7% relation accuracy) sits below even its own noisy human-agreement
ceiling (~65.8%); Open IE systems are the closest to genuinely open-domain robustness but produce generic
SVO-shaped triples, not goal/outcome/causal structure, and their own survey (Niklaus et al. 2018) flags that
open-text coverage claims are themselves under-evaluated field-wide — an absence-of-measurement, not a proven
ceiling, worth naming honestly. **Calibrated P(this remains a genuinely open/unsolved problem field-wide) =
0.83 raw** (confirm-the-wall sub-agent's own estimate, reasoning: the pattern is multi-decade and consistent —
every tradition either narrows domain to hit high accuracy, or stays open and caps under 70%) — **deflated to
P=0.65 per the standing lit-scan calibration penalty** (0.15-0.25 band; using the larger deflation since several
of the sub-agent's own citations for the ceiling numbers are search-snippet, not primary-fetched, and the
Odin/Eidos exception case is explicitly unverified, so the negative claim itself carries more residual
uncertainty than a typical confirmatory lit-scan). **Best partial lever, honestly ranked:** VerbNet/Levin
class-backoff (Section 3(ii)) is the single most measurement-backed partial win in the entire scan (50-65%
error reduction, unsupervised, no training corpus) — it is a LOCAL, per-item coverage fix, not a route to
closing the whole wall, but it is real and immediately actionable. The wall's true closure (per the standing
diagnosis in `notes/formalize_situation_model_DMN_integration_spec_2026-08-06.md`) still requires the
whole-passage INTEGRATION register (2a-2d) that this session's findings do not substitute for — they are
complementary, narrower levers layered on top of that plan, not an alternative to it.

---

## Cheap decisive test

**For (i), richer context key:** extend the existing `exp_word_context_affect_superposition_map_v1` harness
(the Stage-3 HARD_PASS cell, `04af969c4`) with a SECOND context-key slot — verb-class membership via a small
(~10-15 entry) hand-authored Levin-style backoff table covering the goal-verb set already named as blocked
(get/give/make/find/see/do/have + 2-3 synonyms not in the original 6-word seed set, e.g. a near-synonym of
crush/whip never in the original table). Re-run the SAME 6-word HARD_PASS set (regression check) plus 2-3 NEW
held-out OOV words whose sense/affect is only recoverable via class-backoff (previously: no coverage at all).

**For (ii), coverage:** take the 14 currently-unreachable `OUTCOME_NEVER_TYPED` items from
`coverage_wall_decomposition_2b_ceiling_and_referent_did_it_happen_2026-08-06.md` and check, disk-only (no new
infra), how many are unreachable SPECIFICALLY because the goal verb has `classes: set()` (the already-measured
root cause for 12/14) — then apply a small get/give/make/find/see/do/have -> {TRANSFER, CREATION, PERCEPTION,
POSSESSION-CHANGE} backoff table and re-run `congruence_decision` to see how many now get a result-class.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered)

| Prediction | HARD-PASS | HARD-FAIL | MIDDLE_BAND |
|---|---|---|---|
| Multi-slot context key (add verb-class backoff to the existing animacy slot) recovers sense/affect for held-out OOV words without regressing the existing 6-word set | >=2/3 new OOV probes correctly collapse to sense+affect AND the original 6-word HARD_PASS holds byte-identical (or better) AND scramble-control still collapses to chance | 0-1/3 OOV probes recovered, OR any regression on the original 6, OR scramble does not collapse (artifact) | 1-2/3 recovered with zero regression |
| VerbNet/Levin-style verb-class backoff recovers result-class assignment for the 12 goal-verb-`classes:set()` items in the 14-item unreachable tail | >=4/12 items now get a correct result-class (net-new coverage, zero regression on the 13 currently-correct owner items, matching this project's own established "+2-3 per detector" pattern) | <2/12 recovered (would mean the OOV/light-verb diagnosis, though independently confirmed by disk-probe, is not the primary binding constraint once a real backoff table is tried — investigate enablement/granting as the true blocker instead, consistent with the already-banked heterogeneous-tail finding) | 2-3/12 recovered |
| The 45-year glass-box coverage wall is a genuine field-wide ceiling, not an artifact of this scan's search terms | a follow-up direct-fetch of the Odin/Eidos evaluation numbers (currently unverified) shows coverage <70% on open text, confirming the pattern holds even for the closest near-miss found | Odin/Eidos (or an equivalent system) is found with verified coverage >70% on genuinely open, non-templated prose for event/situation-structure extraction — would meaningfully weaken the wall-confirmation and merit an immediate deep-dive | -- |

**P_deflated for "the multi-slot context-key extension clears its own HARD-PASS band on first attempt":** raw
prior ~0.55 (well-precedented mechanism — Resnik/VerbNet backoff is decades-old and the composition machinery
is already proven — but genuinely untested on THIS substrate's specific word set and backoff-table quality).
Deflated per the standard 0.15-0.25 band by 0.15 (most citations for the MECHANISM are solid/converging across
independent sources, though several specific accuracy numbers were flagged unverified by the sub-agents, and
domain-transfer to narrative goal-outcome specifically is untested) — **P_deflated = 0.40**. **P_deflated for
the coverage backoff-table prediction:** raw prior ~0.5 (the root cause was independently disk-probed by the
Director before this drill, a strong internal signal, but Swier & Stevenson's external number is for generic
SRL role assignment, not narrative goal-verb result-class typing specifically — a real domain gap) — deflated
by 0.15 to **P_deflated = 0.35**, both well under the 0.50 novel-synthesis cap.

## Cross-thread synthesis

This drill sits directly between two same-day artifacts and does not duplicate either: `PLAN_B_grounding_
word_context_affect_superposition_map_2026-08-07.md` names "richer context keys" as Stage 3's open honest
boundary without specifying HOW — this drill supplies the specific, cheap, literature-backed HOW (Resnik
selectional association + VerbNet/Levin backoff), reusing the exact bind/bundle/cleanup machinery that plan
already proved. `formalize_situation_model_DMN_integration_spec_2026-08-06.md`'s build plan (2a-2d) targets
INTEGRATION (a shared whole-passage register, cross-sentence carry-forward, cross-character links) as the
keystone coverage fix; this drill's coverage findings (VerbNet backoff, cascade-fallback) are NARROWER,
COMPLEMENTARY, per-item generalization fixes that do not substitute for 2a-2d and should be sequenced as small
side-branches (the backoff table is pure lookup-table plumbing, cheap to slot in alongside 2a-2c without
blocking on them). The `deepdrill_sense_disambiguation_cues.md` (2026-08-05) brain-mechanism ranking
(dominance-default > governor/frame > local-collocation > discourse) is independently corroborated by this
session's field scan converging on the SAME cue (governor/selectional-restriction) as the single best-evidenced,
cheapest computational lever — biology and the computational field agree on where the leverage is, which
raises confidence in the recommendation beyond what either scan alone would support. The three 2026-08-06
prior-art scans (classical symbolic, modern neuro-symbolic, VSA/HDC) established the GOAL-OUTCOME-specific
version of the 45-year wall; this session's confirm-the-wall sub-agent independently re-derived the same
negative from a broader, orthogonal angle (ANY event-structure task, not just goal-outcome) and surfaced one
genuinely new candidate (Odin/Eidos) that none of the three prior scans found — a real, if unverified,
addition to the field map, appropriately flagged as unconfirmed rather than silently folded in as a positive.

## Substrate-product implications

- **Immediate, cheap, buildable increment (serves both A and B):** a single small (~10-15 entry) hand-authored
  or WordNet/VerbNet-hierarchy-derived verb-class backoff table for the goal-verb set already named as blocked
  (`get/give/make/find/see/do/have` + close synonyms) is SUPPLIED DATA (invariant-compliant), reused by (i) the
  context-key extension (PLAN_B Stage 3+) and (ii) the coverage backoff test on the 14-item unreachable tail —
  build once, spend twice. This is the highest-leverage single artifact this drill identifies.
- **Second, cheap, complementary slot:** a negation/intensifier polarity-shift flag (Wilson-Wiebe-Hoffmann
  style) directly targets the AFFECT-DIRECTION half of the context key (not just sense) — relevant to any
  future extension of the "spoil"-class example set beyond the current 6 words.
- **Architectural lead, not yet actionable:** cascade/fallback rule matching (Odin/Eidos pattern) is worth a
  dedicated follow-up drill (direct-fetch the Eidos evaluation paper; the two PDF-fetch failures this session
  are a retrieval artifact, not a content gap) before committing engineering time — flagged, not recommended
  for immediate build.
- **Do not overclaim:** neither lever closes the 45-year wall; both are honest, narrow, well-precedented
  increments layered on top of the already-planned integration-register build (2a-2d), which remains the
  keystone per the standing diagnosis.

## Citations (verified count)

**Disk-verified this session (9 artifacts, read directly):** `notes/PLAN_B_grounding_word_context_affect_
superposition_map_2026-08-07.md`; `notes/deepdrill_sense_disambiguation_cues.md`; `notes/coverage_wall_
decomposition_2b_ceiling_and_referent_did_it_happen_2026-08-06.md`; `notes/formalize_situation_model_DMN_
integration_spec_2026-08-06.md`; `notes/brain_component_map_narrative_comprehension_ROADMAP_2026-08-06.md`;
`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`; status_log grep (last 5 `research_delivery`
entries, 2026-08-06); `tools/orchestrator/research_field_advisor.py` output (this session); prior-art scan
trio (`notes/prior_art_classical_symbolic_story_understanding_2026-08-06.md`, `notes/prior_art_modern_
neurosymbolic_narrative_2026-08-06.md`, `notes/prior_art_vsa_hdc_for_language_2026-08-06.md`, cited by
reference not re-read in full).

**External/field literature — 3 parallel Sonnet lit-scan sub-agents dispatched this session (generic-terms-only
WebSearch/WebFetch, no project-specific framing off-platform). ~40 unique external citations across the three
angles** (Resnik 1996; Fass & Wilks 1983; McRae, Spivey-Knowlton & Tanenhaus 1998; Erk & Pado 2008; Erk, Pado &
Pado 2010; Baroni & Lenci 2010; Gildea & Jurafsky 2002; Kipper VerbNet; Yarowsky 1993/1995; Banerjee & Pedersen
Extended Lesk; Zhong & Ng IMS; Mitchell & Lapata 2010; Baroni & Zamparelli 2010; Wilson, Wiebe & Hoffmann
2005/2009; Polanyi & Zaenen 2004/2006; Chambers & Jurafsky 2008/2009; Regneri, Koller & Pinkal 2010; Gerber &
Chai 2010/2012; Ruppenhofer et al. 2010 SemEval-2010 Task 10; Carreras & Marquez 2005 CoNLL; Punyakanok, Roth &
Yih 2008; Swier & Stevenson 2004; Banko et al. 2007 TextRunner; Fader, Soderland & Etzioni 2011 ReVerb; Mausam
et al. 2012 OLLIE; Del Corro & Gemulla 2013 ClausIE; Angeli, Premkumar & Manning 2015 Stanford OpenIE; DeJong
1979 FRUMP; BORIS (Dyer); Niklaus et al. 2018 OpenIE survey; Elson ProppLearner/DramaBank; Valenzuela-Escarcega
et al. 2015 Odin; Sharp et al. 2019 Eidos; Croce et al. 2010; Hobbs & Stickel 1988 TACITUS) — most VERIFIED
via live search-snippet with multi-source corroboration; several specific numeric claims explicitly flagged
UNVERIFIED this session (PDF-fetch failures) and listed per-technique above rather than silently propagated.

**Total: 9 disk-verified + ~40 external (majority search-verified, several explicit numeric gaps flagged,
zero fabricated numbers) = ~49, with the honest-wall section separately re-deriving (not just citing) the
field-wide negative from a broader angle than the prior three scans covered.**
