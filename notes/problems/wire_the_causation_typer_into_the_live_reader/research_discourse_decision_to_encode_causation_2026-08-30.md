# Research drill: the DISCOURSE-LEVEL decision to ENCODE a causal link in running narrative

**Date:** 2026-08-30 · **Role:** Director / research · **Type:** deep literature drill (research only; no cells, no `hdlab/` edits)
**Problem:** `wire_the_causation_typer_into_the_live_reader`
**Sibling notes (do not duplicate):**
- `research_within_clause_causative_extraction_brain_mechanism_2026-08-30.md` — the SENSE half (Wolff/Talmy truth-table, within-clause).
- `research_force_event_discrimination_deep_2026-08-30.md` — force-vs-event affectedness/eventivity discrimination.
- `research_construction_generalization_of_force_typing_2026-08-30.md` — construction generalization.

**This note is the DISCOURSE half:** given that a clause's main verb is in the force lexicon, *should the reader encode a causal link here at all?* The three siblings ask "which force TYPE" and "is the verb reading causal"; this asks "does the discourse warrant positing a causal EVENT/link for this clause." That is the source of the over-generation on real prose (`she SAW a servant`, `the court HAS its houses`, `CALL a native a pig`, `fog everywhere, MAKING a drizzle`).

---

## 1. The precise question, and a reframe that changes the answer

The force-verb scanner over-generates because it decides at the **wrong grain**. It scans the *verb lexicon* and, for every transitive clause whose verb is force-lexicon-listed, tries to emit a discourse-level causal link. The human comprehender never does this. Two distinct decision levels are being conflated:

- **Level A — is this clause an ASSERTED FORCE-DYNAMIC EVENT?** (within-clause, lexical-semantic: affectedness, force-fit, eventive reading, dominant-sense prior à la Giora). This is the SENSE half, already drilled. It catches `see` (perception; patient not affected) and `call X a Y` (naming/predication; no change of state).
- **Level B — even for a genuine dynamic transitive clause, does the DISCOURSE encode it as a causal-chain EVENT NODE, or merely update the setting/state?** This is the discourse half. It catches the *descriptive/stative/generic/background* over-fires (`the court HAS its houses`; the fog opening of *Bleak House*; atmospheric `MAKING a drizzle`) — clauses whose verbs DO have force/possession senses but which the reader files as **setting**, not as **events**.

**The key mechanistic reframe (this is the load-bearing correction):** causal encoding in the brain is not a per-clause verb operation at all. It is a **by-product of EVENT-MODEL CONSTRUCTION.** The reader segments the input stream into events, foregrounds the subset that *advances* the situation model, and connects foregrounded events with causal arcs. **A clause that does not create a foregrounded event node is never even a candidate for a causal arc.** The scanner over-generates because it operates at verb-lexicon grain instead of event-node grain — a category error, not a threshold error.

**A second correction, directly against the naive intuition "the brain is parsimonious about causation":** the discourse-processing literature shows the brain is actually **EAGER** to infer causal relations — but only **between EVENTS/SEGMENTS**, never off a single within-clause verb. "Causality-by-default" (Sanders 2005; Murray 1997) is a real, robust effect (below). The filter that prevents over-generation is therefore **not** "be stingy with causal relations" — it is **"only foregrounded EVENTS become relata."** Get the event-hood gate right and the causal-relation eagerness is fine.

---

## 2. Pillar-by-pillar synthesis (lead with the psycholinguistics)

### Pillar 1 — Coherence relations are the unit of causal encoding (Hobbs; Kehler 2002; Sanders, Spooren & Noordman 1992)
- **Hobbs (1979, 1990)** and **Kehler (2002, *Coherence, Reference, and the Theory of Grammar*)**: discourse is understood by inferring a small inventory of **coherence relations** between segments, organised under three general principles (Cause-Effect, Resemblance, Contiguity). Kehler's **Cause-Effect** class has four members — **Result, Explanation, Violated Expectation, Denial of Preventer.** Causal structure is a **relation between two segments**, established by connectives + world-knowledge expectations, **not** read off a transitive verb inside one clause.
- **Sanders, Spooren & Noordman (1992), *Toward a taxonomy of coherence relations*** (*Discourse Processes* 15:1): coherence relations decompose into a few **cognitive primitives** — most importantly **causal vs. additive**, plus basic/non-basic order, semantic/pragmatic source, and polarity. "Causal" is a *primitive feature of a relation between segments*, orthogonal to whether any clause contains a force verb.
- **Implication for us:** a causal link is a property the reader assigns to a **pair of segments/events**, licensed by a *causal coherence relation*. A lone force-verb clause with nothing to relate to is not a coherence-relation site. Kehler's own "Denial of Preventer" is the discourse-level cousin of our PREVENT type — evidence the CAUSE/ENABLE/PREVENT distinction lives at the relational level too, but is anchored to segment pairs, not bare verbs.

### Pillar 2 — Causal-network necessity / narrative event structure (Trabasso & van den Broek 1985; Trabasso & Sperry 1985; van den Broek 1990)
- **Trabasso & van den Broek (1985), *Causal thinking and the representation of narrative events*** (*JML*): readers build a **causal network** over story events; an event's number of causal connections predicts **recall frequency, recall order, and judged importance** — independent of story-grammar category or drama. Highly-connected events are the *causal spine*; a clause with no consequent event is peripheral / non-node.
- **van den Broek (1990) "causal necessity":** two events are linked by a causal arc iff the earlier is **"necessary in the circumstances"** for the later — a **counterfactual / but-for** criterion (would the later event still have occurred, in the story world, absent the earlier?). **Trabasso & Sperry (1985)** validated this necessity criterion against importance ratings.
- **Implication for us — and an honest limitation:** the true licensing test for a *cross-event* causal arc is counterfactual necessity, which requires world knowledge and is **not glass-box-cheap.** This is *why* the PROBLEM's cross-sentence causal-network typing was a measured negative. **So for the wiring problem, causal-necessity is PINNED as the correct mechanism but is NOT the implementable lever.** The implementable lever is the *upstream* gate: a single transitive clause with no consequent event is not a causal-network node in the first place — kill it at event-segmentation, not at necessity-inference.

### Pillar 3 — Event vs state vs description segmentation (Zwaan & Radvansky 1998; Zacks & Swallow; Magliano)
- **Zwaan & Radvansky (1998) event-indexing model:** readers track **five dimensions** — **time, space, entity/protagonist, causation, intentionality (goals)** — over a network of **EVENT nodes**; nodes are linked by the indices they share. **Causation is indexed over EVENTS.** A discontinuity on a dimension raises updating cost (reading-time spikes). Crucially, **only events get indexed** — stative/descriptive material updates the *setting dimensions* (space/time/entity), it does not mint an event node and therefore carries no causation index.
- **Zacks, Speer, Swallow, Braver & Reynolds (2007) Event Segmentation Theory:** comprehenders continuously predict the near future; **prediction error at event boundaries** triggers a **new event model.** Boundaries are precisely where the situation-model dimensions change. A backgrounded description produces no prediction-error boundary → no new event → no causal-arc candidate.
- **Magliano & Schleich (2000) / Ferretti, Kutas & McRae (2007):** **grammatical ASPECT is an online signal** readers demonstrably use — *imperfective/progressive* keeps an event **open/in-progress** (accessible, ongoing, backgroundable); *perfective/simple past* **closes/bounds** it (a completed, foregroundable event). This is direct experimental evidence that aspect gates event-representation state during reading.
- **Implication for us:** the primary, cheap, glass-box gate is **event-hood/foregrounding**, and **aspect + predicate-type are its measurable online correlates.**

### Pillar 4 — Foreground vs background / grounding (Hopper 1979; Hopper & Thompson 1980; Reinhart 1984)
- **Hopper (1979) "Aspect and Foregrounding in Discourse"** and **Hopper & Thompson (1980) transitivity**: cross-linguistically, **main-line (foreground) events are dynamic action verbs, aspectually PERFECTIVE, sequenced, kinetic**; **supportive (background) material is stative/durative, aspectually IMPERFECTIVE, descriptive.** High **transitivity** (telic, punctual, volitional, affected-and-individuated patient, realis) clusters with foreground; low transitivity clusters with background/description.
- **Reinhart (1984):** foreground clauses are **narrative, bounded (temporally closed), and sequenced**; background clauses are descriptive, unbounded, and unordered relative to the main line.
- **Implication for us:** this is the mechanism that most precisely explains the *Bleak House* fog over-fire. That opening is almost entirely **backgrounded, imperfective, low-transitivity description** — exactly where Hopper predicts the reader posits **no event and no causal arc**, and exactly where the scanner fires. **Aspect + clause-type + transitivity gate whether a clause enters the causal chain** — and every component of that is computable from the parse.

### Pillar 5 — Causal inference is minimal/bridging, selective (McKoon & Ratcliff 1992; Graesser, Singer & Trabasso 1994)
- **McKoon & Ratcliff (1992) minimalist hypothesis:** automatic inferences are limited to those (a) required for **local coherence** or (b) **easily available** from active memory. **Causal-antecedent (bridging) inferences are made when there is a local coherence break;** forward causal-consequence/elaborative inferences are **NOT** routinely made. → the reader does not forward-project a causal consequence for every event; absent a coherence break, a lone transitive clause triggers no extra causal encoding.
- **Graesser, Singer & Trabasso (1994) constructionist / "search after meaning":** readers *do* routinely make **explanation-based** inferences (causal antecedent + superordinate goal) driven by a coherence + explanation search — but these are **goal-directed and selective**, not promiscuous, and are anchored to *why did this event happen* over the evolving model.
- **Reconciliation for us:** both camps agree the reader makes causal inferences **selectively, gated by a coherence break and easy availability** — never one-per-transitive-verb. The suppressor of over-generation is the **absence of a coherence-break trigger** for background/descriptive/stative clauses. Our scanner has no coherence-break gate at all; that is the missing suppressor.

### Pillar 6 — Prediction / expectation-driven interpretation (Kuperberg & Jaeger 2016; Bicknell et al. 2010)
- **Kuperberg & Jaeger (2016):** comprehension is a **hierarchical, actively-generative** process — the evolving discourse model generates top-down predictions at multiple levels (semantic features; **event structure "who did what to whom"**), and processing is driven by **prediction error** against those predictions (N400 = semantic-feature PE; later frontal negativity = event-structure PE).
- **Bicknell, Elman, Hare, McRae & Kutas (2010):** readers use **event/verb-argument knowledge in real time** — a patient is read faster / lower-N400 when it fits the agent+verb *event schema* (`mechanic checked → brakes` vs `journalist checked → brakes`).
- **Implication for us:** the discourse model **conditions each clause's interpretation top-down**, so in a descriptive passage `the court HAS...` is generated/predicted as *description* and never proposed as an event. This is PINNED but the hardest to make glass-box cheaply (it needs the running generative model). The **cheap, static proxy** for "descriptive passage → suppress" is the foreground/background + genericity signal of Pillars 3–4, which is what the local discourse expectation largely tracks.

---

## 3. THE LOAD-BEARING MECHANISM (confirm / correct the hypothesis)

**User's hypothesis:** *a causal link is encoded only for a FOREGROUNDED EVENT that stands in an inferred CAUSAL COHERENCE RELATION / is causally NECESSARY for another event — not for every transitive force-verb clause; description/stative/background clauses are excluded at the event-segmentation stage.*

**Verdict: CONFIRMED, with two refinements that sharpen it into something implementable.**

1. **CONFIRMED — the exclusion happens at EVENT-SEGMENTATION/FOREGROUNDING, upstream of any causal-relation inference.** (Zwaan & Radvansky: only events are indexed; Hopper: background/imperfective/low-transitivity clauses are not main-line events; Zacks: no boundary → no new event.) This is the primary, brain-faithful, *glass-box-cheap* filter and it is exactly the lever this problem needs.

2. **REFINEMENT A — separate the two things the hypothesis bundles.** "Foregrounded EVENT" and "stands in a causal coherence relation / is causally necessary" are **two different gates at two levels:**
   - The **event/foreground gate** (Level B, Pillars 3–4) is cheap, static, glass-box, and is the correct fix for the *within-clause* over-generation. **Use this as the primary lever.**
   - The **causal-relation / causal-necessity gate** (Level cross-event, Pillars 1–2) is the *correct* mechanism for connecting events, but it is world-knowledge-bound (counterfactual necessity) and is **the PROBLEM's measured-dead cross-sentence lever.** **Keep it PINNED-but-report-only; do not build the win on it.**

3. **REFINEMENT B — the brain is EAGER, not stingy, about causal RELATIONS; parsimony lives in EVENT-HOOD.** "Causality-by-default" (Sanders 2005): readers **default to a causal reading** of two adjacent segments absent cues otherwise; Murray (1997): sentence continuations after a period are predominantly causal; Sanders & Noordman (2000): causally-related segments are read **faster** and recalled **better** than additive ones. So over-generation is **not** cured by making causal inference rarer — it is cured by ensuring the relata are genuine **events**. This flips the framing: the fix is a **precision filter on event-hood**, not a suppressor on causation.

**One-sentence statement of the mechanism:**
> The comprehender encodes a causal/force link only for a clause that first passes the **FORCE-SENSE gate** (asserted, affected, eventive force reading — the SENSE half) **AND** the **FOREGROUNDED-EVENT gate** (a dynamic, bounded, specific, main-line event — not a stative/generic/descriptive/backgrounded clause). Cross-event causal *arcs* are then inferred eagerly between such event nodes by coherence + causal-necessity — but that inference has no input at all from a clause that never became an event node.

---

## 4. CONCRETE, GLASS-BOX, IMPLEMENTABLE RECIPE — "should the reader encode a causal link HERE?"

All predicates below are computable from the existing parse (POS, dependency labels, tense/aspect morphology, determiners) + small **closed** lexicons — **no world-knowledge-complete inference.** This is a **precision filter** that runs *before* the force typer types the clause; when it abstains, the reader updates the setting dimensions (space/time/entity) instead of minting a causal link.

**ENCODE a within-clause causal/force link at clause C iff ALL of:**

**(A) FORCE-SENSE gate — existing (`_literalness_gate` + affectedness/eventivity/force-fit).** Unchanged. Handles perception (`see`), cognition, and pure naming by affectedness/eventivity. Keep as the first gate.

**(B) FOREGROUNDED-EVENT gate — NEW (this note's contribution). Four cheap sub-checks, each binary off the parse:**

- **B1 · Dynamicity (not stative/relational).** The head verb is **not** in a closed **STATIVE/RELATIONAL/PERCEPTION/COGNITION stoplist** — {be, have, own, possess, contain, hold, comprise, consist, belong, know, believe, think, seem, appear, resemble, remain, see/hear/feel-as-perception, …}. Kills `the court HAS its houses`, `she SAW a servant`. *(Vendler states + Levin stative classes; a finite, auditable list.)*
- **B2 · Not a naming/predication frame.** Reject **object-complement / secondary-predicate** constructions — `call/name/dub/deem/consider/term X (a) Y` — detected by a secondary predicate on the object (dep label `oprd`/`xcomp`/`ccomp` head on the object, or the "V NP NP/AdjP" object-complement pattern). Kills `CALL a native a pig`. *(These assert a labeling relation, not a caused change.)*
- **B3 · Foreground grounding (Hopper): main-line, not backgrounded adjunct.** The force verb must head a **FOREGROUND-eligible clause** — dependency role `ROOT`, or a coordinate `conj` of a main assertion, or a complement clause of a reporting/perception matrix that is itself foregrounded. **Reject** when the verb heads a **backgrounding structure**: a participial/gerundive free adjunct or absolute (`advcl` whose verb is a present/past participle — `fog everywhere, MAKING a drizzle`), a relative clause (`relcl`/`acl:relcl`), an appositive (`appos`), or a nominal-modifier participle (`acl`). Downweight (do not hard-kill) `advcl` finite subordinate clauses (they can be foreground in *because/so* chains — see B-consequent). Kills the *Bleak House* fog over-fire.
- **B4 · Boundedness + specificity (telic, realis, particular — not generic/habitual).** Require at least one of: **perfective/simple-past/perfect** tense-aspect on the head (Hopper: perfective = foreground; Magliano: perfective closes/bounds the event); OR an explicit **telicity/change-of-state marker** (verb particle, resultative secondary predicate, goal PP, a Levin change-of-state verb). **Reject** a **gnomic/habitual PRESENT** with **kind-referring / bare-plural / generic** arguments (generic subject or object, no specific referent) — that is a setting description, not an event. Kills gnomic `the court MAKES...`, generic `fog MAKES drizzle`.

**(C) CROSS-EVENT ARC — REPORT-ONLY (the measured-dead lever; keep for completeness, do not headline).** If C survives (A)+(B) AND there is a candidate **consequent event node** within the discourse window AND a **causal signal** — a closed-class **causal connective** (`because, since, so, thus, therefore, as a result, hence, consequently, that's why`) or a **but-for/necessity** relation — then *also* record a cross-sentence CausalLink between the two event nodes. Per the PROBLEM's integrated negative, **report this slice separately and state it ties majority-CAUSE**; the within-clause typing (A+B) is the headline.

**Net effect:** (A) removes wrong-sense fires; (B) removes right-sense-but-not-an-event fires (the descriptive/stative/generic/background majority of real-prose over-generation). Together they raise **precision** on "which clauses to type" without touching the typer's proven within-clause 3-way accuracy on its domain.

---

## 5. PINNED vs OUR-INVENTION

| Component | Status | Basis |
|---|---|---|
| Causal encoding is over EVENT nodes; only events get a causation index | **PINNED** | Zwaan & Radvansky 1998 (event-indexing); Zacks et al. 2007 (EST) |
| Foreground/background grounding gated by aspect + transitivity (perfective/dynamic=foreground; imperfective/stative=background) | **PINNED** | Hopper 1979; Hopper & Thompson 1980; Reinhart 1984 |
| Aspect is an ONLINE signal readers use to open/close event representations | **PINNED** | Magliano & Schleich 2000; Ferretti, Kutas & McRae 2007 |
| Causal arcs require causal-necessity ("necessary in the circumstances", counterfactual) between events | **PINNED** (but world-knowledge-bound → report-only here) | Trabasso & van den Broek 1985; Trabasso & Sperry 1985; van den Broek 1990 |
| Causal link = a CAUSAL COHERENCE RELATION between segments (Result/Explanation/…) | **PINNED** | Hobbs 1979/1990; Kehler 2002; Sanders, Spooren & Noordman 1992 |
| Causal inference is selective, gated by local-coherence break / easy availability | **PINNED** | McKoon & Ratcliff 1992; Graesser, Singer & Trabasso 1994 |
| Brain is EAGER (default) about causal RELATIONS between adjacent segments; parsimony is in EVENT-HOOD not in causation | **PINNED** (corrects the naive "brain is stingy" read) | Sanders 2005 causality-by-default; Murray 1997; Sanders & Noordman 2000 |
| Top-down discourse model conditions each clause's interpretation (descriptive passage → suppress) | **PINNED** | Kuperberg & Jaeger 2016; Bicknell et al. 2010 |
| The specific STATIVE/PERCEPTION/COGNITION/NAMING **stoplist** contents | **OUR-INVENTION** (literature-motivated: Vendler/Levin classes) | operationalization |
| Dependency-label → foreground/background **mapping** (ROOT/conj=fg; advcl-participle/acl/relcl/appos=bg) | **OUR-INVENTION** (operationalizes Hopper grounding via the parse; the brain's grounding computation is richer) | operationalization |
| Tense/aspect → boundedness proxy + generic/habitual detector | **OUR-INVENTION** (proxy for Magliano/Hopper aspect signal) | operationalization |
| Connective list + discourse-window size + thresholds/weights | **OUR-INVENTION** | swept, glass-box |

---

## 6. Fit to the PROBLEM's constraints (respect the integrated negatives)

- The recipe's **headline lever is the within-clause FOREGROUNDED-EVENT precision gate** — it lives entirely inside the typer's proven within-clause domain and needs **no** cross-sentence coherence inference. It attacks the exact failure named in the PROBLEM (over-generation on running prose) by raising precision on *which clauses get typed*, not by changing the 3-way typing.
- The **cross-event causal-necessity / coherence gate is PINNED-but-report-only**, matching the integrated `causation_is_typed_per_clause_not_across_the_causal_network` STRONG negative. Do not build the win on it; report the slice and state it ties majority-CAUSE.
- The gate is **default-safe**: on abstain, the reader updates setting dimensions (space/time/entity) — no CausalLink minted — so a byte-identical `causation_typed=False` path is trivial.
- **Corpus-age confound (standing):** validate the foreground/background + genericity gate on **modern annotated text** where eventive/foreground gold exists; McGuffey (~200 yr) is the reader-eval confound. A useful positive control the gate should pass: the *Bleak House* fog opening (backgrounded, imperfective) → the gate abstains on ~all of it, while a genuine main-line causative (`the wind opened the gate`) → passes.

---

## 7. Honest limitations / flags

- **Causal-necessity is the true licensing test and it is NOT glass-box.** The counterfactual "necessary in the circumstances" test (van den Broek) needs world knowledge. The recipe substitutes a *foregrounding + connective + adjacency* proxy for it at the cross-event level, which is strictly weaker — hence report-only.
- **Aspect signal is only as good as the parse's tense/aspect fields** on the target corpus; participial-adjunct vs finite-subordinate detection depends on dependency-label accuracy. Both are measurable, glass-box failure points to instrument.
- **Genericity detection is the softest sub-check** (bare-plural/kind reference is not perfectly parse-decidable); treat B4-genericity as a downweight rather than a hard kill if it costs recall.
- **Lit-scan calibration (standing penalty):** the *mechanism* claims (Pillars 1–6) are well-established PINNED findings. The claim that *the four-part event-gate will materially raise precision on our corpus* is a **hypothesis pending the wired end-to-end measurement**, not a result — deflate accordingly.

---

## TLDR (plain English)
A good reader does not treat every sentence with an action word as "one thing caused another." It first decides whether the sentence even describes a real, finished, foreground **happening** — as opposed to just describing the scene, a state of affairs, or a general habit. Only happenings get connected by cause-and-effect; scenery and descriptions just fill in the background. Our tool over-fires because it reacts to the *word*, not to whether the sentence is a happening. The fix, and it is well supported by decades of reading research, is to add a cheap check — before typing a cause, confirm the clause is a **foreground event** (a dynamic, completed, specific action in the main storyline), not a description, a state, a name-calling, or a bit of atmosphere. That check can be computed from the sentence's grammar alone (tense, verb type, and how the clause hangs off the sentence), so it stays glass-box with no outside knowledge needed.

## QUESTIONS
None — the deliverable was a mechanism + recipe, both delivered. (The one open *empirical* question, whether the four-part gate clears the floor on modern text, is the wiring problem's own measurement, not a question for the owner.)

## NEXT STEPS (for the solver of the wiring problem — not actioned here)
1. Implement the **FOREGROUNDED-EVENT gate (B1–B4)** as a precision pre-filter in front of the within-clause force typer inside a `WiredSituationReader` (experiments only; strategy lands the `situation_reader` edit).
2. Positive control: the *Bleak House* fog opening → gate abstains; `the wind opened the gate` → gate passes + types CAUSE.
3. Measure end-to-end precision on **modern** causative-verb gold with the gate ON vs OFF, and confirm the force-class-shuffle twin still loses (PROBLEM §7 bar).
4. Keep the cross-event arc (C) as a separately-reported slice; state it ties majority-CAUSE.

---

### Sources
- Kehler (2002) *Coherence, Reference, and the Theory of Grammar*; Hobbs (1979/1990) — https://web.stanford.edu/group/cslipublications/cslipublications/pdf/1575862166.pdf
- Sanders, Spooren & Noordman (1992) *Toward a Taxonomy of Coherence Relations*, Discourse Processes 15:1 — https://www.tandfonline.com/doi/abs/10.1080/01638539209544800
- Trabasso & van den Broek (1985) *Causal thinking and the representation of narrative events*, JML — https://cs.uky.edu/~sgware/reading/papers/trabassovandenbroek1985causal.pdf ; validation — https://link.springer.com/article/10.3758/BF03200561
- Zwaan & Radvansky (1998) event-indexing; test — https://link.springer.com/article/10.3758/BF03195811 ; review of event-comprehension models — https://arxiv.org/pdf/2409.18992
- Hopper (1979) *Aspect and Foregrounding in Discourse*; Hopper & Thompson (1980) transitivity — https://www.researchgate.net/publication/242503579_Aspect_and_foregrounding_in_discourse ; aspect constrains events — https://link.springer.com/article/10.3758/BF03196106
- McKoon & Ratcliff (1992) minimalist — https://pubmed.ncbi.nlm.nih.gov/1502273/ ; Graesser, Singer & Trabasso (1994) constructionist — https://www.researchgate.net/publication/15261574_Constructing_Inferences_During_Narrative_Text_Comprehension
- Kuperberg & Jaeger (2016) *What do we mean by prediction in language comprehension?* — https://kuperberg.mgh.harvard.edu/wp-content/uploads/kuperbergjaeger_lcn_15.pdf ; Bicknell et al. (2010) event knowledge in verb-argument processing — https://pmc.ncbi.nlm.nih.gov/articles/PMC2976562/
- Sanders (2005) causality-by-default; Murray (1997); Sanders & Noordman (2000) — via https://aclanthology.org/C12-1163.pdf and https://pmc.ncbi.nlm.nih.gov/articles/PMC11471541/
