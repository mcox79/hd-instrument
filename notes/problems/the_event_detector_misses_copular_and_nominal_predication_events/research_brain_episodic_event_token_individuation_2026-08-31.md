# Finer drill: EPISODIC-EVENT-TOKEN INDIVIDUATION for nominals

Problem: `the_event_detector_misses_copular_and_nominal_predication_events`
Date: 2026-08-31 | Author: hdi_research (finer drill, on top of the copular/nominal p1 drill + the prior sense-selection pin)
Method: online literature scan (generic terms), PINNED (published, cited) vs SPECULATIVE/INFERRED verdicts.
Scope: ONE thing only — how the comprehension system decides a nominal introduces an EPISODIC EVENT TOKEN (a
specific happening at a time → a situation-model event node) vs a GENERIC/KIND or PROPERTY reference, and whether
that yields a CONCRETE LOCAL buildable cue-signature short of a full incremental parser / situation model.

NOT re-derived (inherited pins, do not re-quote): sense selection = argument structure (Grimshaw 1990) +
governing-predicate coercion (Pylkkänen); intrinsically discourse-context-bound in the general case (Kuperberg);
boundedness/telicity is the event-hood feature (Hopper–Thompson foreground signal); copular = Kimian STATE sort.
Already IN USE by the detector: determiner-boundedness, of/by argument structure, prior event-anaphora (→ 2x
precision, 4% coverage). This drill asks what LOCAL cue is MISSING.

---

## Q1 — NEURAL/COMPUTATIONAL: episodic event TOKEN vs KIND/PROPERTY

**VERDICT: PINNED that the brain dissociates a specific SPATIOTEMPORALLY-ANCHORED event token (hippocampal
relational binding) from a decontextualized event KIND/schema (neocortical/semantic, vmPFC for schema) — this IS a
graded continuum, not a clean binary. SPECULATIVE-INFERRED that event NOMINALS route by their episodic-vs-kind
reading onto this same split (no direct nominal contrast found — it is a bridging inference).**

- **PINNED (the memory dissociation):** Complementary Learning Systems — the hippocampus binds a specific
  configuration of elements (what/where/when) into a UNIQUE, spatiotemporally-contextualized episodic trace; the
  neocortex holds generalized, decontextualized semantic/schematic knowledge (kinds, gist). Specificity gradient:
  posterior hippocampus + neocortex carry perceptually-specific detail, anterior hippocampus carries gist, vmPFC
  carries schema; with time/experience a memory can transform from hippocampus-dependent (specific) to
  schematic/semantic (hippocampus-independent) (Yonelinas contextual-binding theory 2019; Sekeres/Moscovitch
  "details, gist and schema" 2017).
- **PINNED (the semantic↔episodic CONTINUUM, and the discriminating feature):** Renoult & Rugg, "From Knowing to
  Remembering: The Semantic–Episodic Distinction" (TICS 2019); Renoult et al., "shared and unique neural correlates
  of personal semantic, general semantic, and episodic memory" (eLife 2023, PMC10662951). The two are NOT strictly
  separate — neural correlates overlap heavily — but the feature that pulls a representation to the EPISODIC pole is
  **anchoring to a unique spatiotemporal context** (a specific time/place), served by hippocampus + posterior-medial
  network binding sensory features held in cortex.
- **PINNED (the linguistic reflex is the SAME feature):** an EPISODIC sentence describes a particular event located
  in space-time; a CHARACTERIZING/GENERIC sentence expresses a regularity via a covert GEN quantifier and is STATIVE
  (Krifka, Pelletier, Carlson et al., *The Generic Book* 1995; "Genericity: An Introduction"). So the linguists'
  "event token" and the memory literature's "episodic" pick out the SAME thing: anchoring to a specific
  spatiotemporal situation. Kind reference lives at the neocortical/semantic pole.
- **SPECULATIVE-INFERRED (the nominal-specific claim, well-motivated but UNMEASURED):** I found NO study contrasting
  an episodic event nominal ("the destruction happened") against a kind-reading nominal ("destruction is terrible")
  on hippocampal-vs-neocortical engagement. The claim that event nominals split this way is a two-step bridging
  inference: (a) episodic reference → hippocampal event-token binding [PINNED, memory lit]; (b) an episodic event
  nominal introduces a situation-model event token located at a time [PINNED, DRT/situation-model]. Therefore an
  episodic nominal SHOULD drive event-token binding and a kind nominal SHOULD drive semantic representation — but this
  is transitivity across two literatures, not a measured contrast. Honesty flag: SPECULATIVE.
- **OPERATIONAL IMPLICATION:** the brain's discriminating feature is **SPATIOTEMPORAL SPECIFICITY / anchoring to a
  unique bounded occurrence at a time.** That is not a lexical property of the noun — it is a property of how the
  nominal is *individuated and located*. So the buildable proxy for "episodic event token" is exactly: does the
  nominal carry LOCAL marks of being an individuated, bounded, time-anchored single occurrence? → Q2.

---

## Q2 — BUILDABLE LOCAL CUES (the payoff), RANKED

The unifying principle from Q1: an episodic token is an INDIVIDUATED, BOUNDED, TIME-ANCHORED, NEWLY-INTRODUCED
occurrence. Each surface cue below is a local reflex of one of those four sub-features. Ranked by precision-when-present
× locality/cheapness.

### Rank 1 — COUNTABILITY (count/mass + numeral + plural morphology) — **HIGHEST; the biggest missing lever.**
- **PINNED:** count deverbal nominalizations INDIVIDUATE the event; mass ones do not. Count event nominals are based
  on achievement/accomplishment (bounded) verbs ("a jump", "a crossing", "a death", "an explosion", "an arrival");
  mass event nominals are based on activity/unbounded verbs ("laughter", "sleep", "rain", bare "destruction",
  "violence"). Boundedness is the nominal analog of telicity; countability = event individuation (Mourelatos 1978;
  Bach 1986; Barner, Wagner & Snedeker 2008 "Verbs as a source of individuating mass and count nouns"; the
  event-oriented-adjectives / mass-count deverbal literature).
- **This is MORE than "determiner-boundedness" already in use.** The new, high-value operational pieces are:
  (i) a **cardinal numeral** ("three explosions", "two arrivals") → individuated bounded token(s); (ii) **plural
  morphology** on the eventive noun → count → individuated; (iii) a **mass-event-noun blocklist**
  ("destruction, violence, care, attention, advice, laughter, sleep, behaviour, conduct, growth, progress") that,
  when BARE (no determiner, not plural, no numeral), suppresses to kind/process. Indefinite "a/an" you likely
  already partly capture under determiner-boundedness; numeral + plural + the mass blocklist are the additions.
- **Operational test:** eventive noun is (a/an OR cardinal-numeral OR morphologically-plural) → FIRE as bounded
  episodic token; eventive noun is bare-singular AND in the mass-event lexicon → SUPPRESS (kind/process). Fully
  local, morphological, ~0 cost, high precision.
- **One-line implication:** add numeral+plural detection and a mass-event-noun blocklist; this is the local analog of
  the boundedness/telicity gate the prior drill named, applied at the number+mass-class level.

### Rank 2 — TEMPORAL-ANCHORING PP / adverbial — **HIGH; directly instantiates the Q1 neural feature.**
- **PINNED:** in DRT (Kamp & Reyle 1993, *From Discourse to Logic*) building the representation of an eventuality
  introduces a NEW discourse referent for the event AND, when a temporal locating expression is present, a time
  referent `t` that anchors the eventuality to a specific location on the timeline. A temporal-locating expression is
  the surface signature of the spatiotemporal specificity that pulls a representation to the episodic pole (Q1). Events
  advance the narrative timeline; states/generics do not.
- **Operational test:** the eventive noun is the object of / adjacent to during / after / before / since / upon / at /
  on / in + {a time, a date, a clock time, "that morning/day/night", "last year", a numbered day}, OR the clause
  carries a temporal locating adverbial binding it ("the explosion at 3 p.m.", "after the collapse", "during the
  riot", "when the destruction happened"). → FIRE as episodic token. Local (one PP / adjacent adverbial), high
  precision, sparser coverage than countability.
- **One-line implication:** add a temporal-anchoring detector (locating-preposition + time expression, or an adjacent
  temporal adverbial) — it is the cheapest direct proxy for the brain's spatiotemporal-specificity discriminator.

### Rank 3 — EVENT-ORIENTED / ASPECTUAL ADJECTIVE — **HIGH precision, LOW coverage; SPLIT by adjective class (critical).**
- **PINNED:** event-oriented adjectives require an event reading and interact with boundedness (Grimshaw 1990;
  event-oriented-adjectives + mass/count deverbal literature). BUT they split into two opposite sub-classes:
  - **SINGLE-OCCURRENCE adjectives** — "sudden, abrupt, brief, momentary, gradual, slow, rapid, immediate,
    instantaneous" → modify ONE bounded occurrence → EPISODIC TOKEN.
  - **FREQUENCY/HABITUAL adjectives** — "frequent, constant, continual, repeated, occasional, periodic, habitual,
    recurrent" → these PROVE event-hood (Grimshaw's diagnostic) but impose a MULTIPLE/HABITUAL/CHARACTERIZING reading,
    i.e. NOT a single episodic token. This is the trap: "frequent explosions" is eventive but GENERIC, not one token.
- **Operational test:** adjacent adjective ∈ single-occurrence set → FIRE episodic token; ∈ frequency set → it IS an
  event nominal but emit it as HABITUAL/generic (do NOT create a single episodic node — or create a habitual node).
  High precision when present; adjectives are sparse so coverage is low.
- **One-line implication:** add TWO small adjective lists; the single-occurrence list fires episodic, the frequency
  list is a NEGATIVE cue for single-token-hood (it proves event-hood but blocks the episodic node).

### Rank 4 — INDEFINITE-INTRODUCTION / discourse-NOVELTY — **MEDIUM-HIGH; overlaps Rank 1; definite is NEUTRAL not positive.**
- **PINNED:** an indefinite ("a/an", or a bare plural introducing new instances) carries a NOVELTY condition — it
  introduces a NEW discourse referent (Heim 1982 File Change Semantics / familiarity theory; Kamp & Reyle 1993). A
  definite ("the") carries a FAMILIARITY condition — it points to an already-introduced referent. Processed rapidly
  online: definiteness marking has an early (300–500 ms) ERP effect and comprehenders PREDICT definite-vs-indefinite
  referents (Carter et al. 2022, *Cognitive Science*, PMC9286847; unexpected indefinites elicit a frontal positivity,
  an "antiuniqueness"/new-referent-introduction signature).
- **Caveat (why it is not higher):** indefinite is a POSITIVE episodic-introduction cue, but DEFINITE is NEUTRAL for
  our purpose — "the destruction" can be (a) anaphoric to an already-introduced episodic token [episodic, good],
  (b) a kind/generic definite [not episodic], or (c) the result-object reading [not an event]. So definiteness does
  NOT split episodic-vs-kind; only the indefinite direction is informative, and it largely coincides with the count
  cue (Rank 1). Your existing prior-event-anaphora feature already handles the useful part of the definite direction.
- **Operational test:** "a/an" or a numeral immediately on an eventive noun that is NOT already anaphoric → new
  episodic token introduced. (Fold into Rank 1; keep definite handled by the existing anaphora feature.)
- **One-line implication:** treat indefinite as a positive introduction cue (mostly subsumed by countability); do NOT
  treat bare definite as evidence of an episodic token.

**Ranked summary (what to ADD):**
1. Countability — numeral + plural morphology + mass-event-noun blocklist (biggest lever, fully local).
2. Temporal-anchoring PP/adverbial (locating-prep + time expression) — direct proxy for the neural feature.
3. Event-oriented adjective — single-occurrence list (fires episodic) vs frequency list (blocks single-token).
4. Indefinite-introduction — positive-only, largely subsumed by (1); definite is neutral.

---

## Q3 — THE BOUNDARY: is the bare-nominal residual IRREDUCIBLY discourse-model-bound?

**VERDICT: PINNED-PARTIAL — YES for the genuinely bare/underspecified residual, but the boundary is NOT at
"nominal-local vs full-parser": there is an intermediate GOVERNING-PREDICATE cue (one dependency hop, no full
situation model) that recovers more before the residual becomes truly model-bound. The final slice — bare nominal +
uninformative predicate — IS irreducibly situation-model-bound.**

- **PINNED (the nominal itself does NOT encode it):** deverbal nouns are "insensitive with regard to the distinction
  between episodic and generic event readings" (event-oriented-adjectives / deverbal-nominalization literature) — the
  episodic-vs-generic distinction is NOT lexicalized in the noun; it is imposed from OUTSIDE. Combined with the
  inherited pins (Brandtner & von Heusinger; Grimm & McNally): the reading of an underspecified deverbal nominal is
  context-imposed, not an inherent lexical split.
- **PINNED (processing keeps it underspecified until context forces it):** comprehenders maintain a shallow /
  underspecified / "good-enough" representation and commit only when context forces resolution; incremental
  interpretation in context is what resolves it, and WITHOUT context resolution is only partial (underspecification
  accounts — Frazier; Frisson & Pickering; quantifier-in-context incremental-interpretation studies, PMC4438783).
  The brain itself does NOT eagerly resolve episodic-vs-kind from the bare lexeme.
- **PINNED (genericity is decided at the PREDICATION level, not the noun):** the generic reading is carried by a
  covert GEN quantifier and a STATIVE characterizing predication ("usually/typically" diagnostic); the episodic
  reading by a particular spatiotemporally-located predication (Krifka et al. 1995). So the deciding feature lives in
  the PREDICATION the nominal enters — which is reachable in TWO tiers:
  - **MIDDLE TIER (buildable now, short of a full model):** the GOVERNING PREDICATE's own type — a one-hop check on
    the matrix verb / copular predicate the nominal is subject/object of. "the destruction **happened / occurred /
    took place / began / was followed by**" → forces EPISODIC token; "the destruction **is terrible / matters / is
    common / is inevitable**" (stative/characterizing predicate) → forces KIND/property. A small "happen-class"
    eventive-matrix-verb list vs a characterizing/stative-predicate signal is one dependency hop, NOT a running
    situation model. This is the coercion source the prior drill named, made into a shallow feature.
  - **IRREDUCIBLE RESIDUAL (genuinely model-bound):** when even the governing predicate is uninformative — "the
    destruction **was total**" vs a prior sentence having introduced a destruction-EVENT — deciding episodic-token
    vs result-object requires knowing whether an event referent is already ACTIVE in the discourse model. "total" is
    compatible with both. No nominal-local and no one-hop-predicate cue can decide it; it needs the running
    situation model's referent inventory (DRT: is there an active event discourse referent this is anaphoric to?).
    This is the honest, irreducible model-bound slice.
- **OPERATIONAL IMPLICATION:** you can cross MORE of the wall now than "nominal-local cues only". Add the MIDDLE-TIER
  governing-predicate check (happen-class matrix verb / characterizing-stative predicate, one dep-hop) AFTER the Rank
  1–4 local cues and BEFORE declaring model-bound. The residual that survives BOTH (bare underspecified nominal +
  uninformative governing predicate) is genuinely situation-model-bound — FLAG it as requiring the incremental
  parser's active-event-referent inventory; do NOT fake it with a bigger local lexicon. That confirms the prior
  drill's strategic verdict but MOVES the boundary: the true residual is smaller than "all bare nominals" by the
  governing-predicate fraction.

---

## TLDR (plain English)
- The brain decides "is this word a real specific happening?" by whether it is pinned to a specific TIME and PLACE and
  is COUNTABLE/BOUNDED — the same feature that separates remembering one event (hippocampus) from knowing a general
  fact (semantic memory). It is not stored in the noun; it is read off how the noun is counted, timed, and predicated.
- The biggest clue we are NOT yet using is COUNTABILITY: "an explosion / three explosions / explosions" is a specific
  bounded happening; bare "destruction / violence / care" is a vague ongoing kind. Add numeral + plural detection and a
  short blocklist of vague mass event-words. Second: a nearby TIME phrase ("after the collapse", "the explosion at 3
  p.m.") is a direct signal of a specific happening. Third: "sudden/brief" = one happening, but "frequent/repeated" =
  many/generic (a trap — it proves it is an event but blocks the single-event reading). Fourth: "a/an" introduces a new
  happening, but "the" alone does not tell us.
- The genuinely hard leftover — "the destruction was total" — cannot be decided from the word alone, and the brain
  can't either; it waits for the story. BUT we can cross more of it than we thought: a quick look at the MAIN VERB the
  noun hangs off ("... happened" vs "... is terrible") decides a big chunk without any story model. Only what survives
  BOTH the local clues AND that main-verb check truly needs the running story — flag those, don't fake them.

## QUESTIONS
None — all three questions resolve to PINNED / PINNED-PARTIAL / SPECULATIVE-INFERRED verdicts.

## NEXT STEPS (for the solver, mechanism-ordered)
1. Add **countability** (cardinal-numeral + plural morphology detection + a mass-event-noun blocklist) as the primary
   new local episodic-token cue — the local analog of the boundedness gate, at the number+mass-class level.
2. Add a **temporal-anchoring** detector (locating-preposition + time/date expression, or adjacent temporal adverbial)
   — the direct surface proxy for the brain's spatiotemporal-specificity discriminator.
3. Add **two adjective lists**: single-occurrence (sudden/brief/abrupt/gradual...) FIRES episodic; frequency
   (frequent/constant/repeated/occasional...) proves event-hood but BLOCKS the single-token node (emit habitual/generic).
4. Treat **indefinite** ("a/an", numeral) as a positive introduction cue (mostly subsumed by 1); do NOT treat bare
   **definite** as episodic evidence — leave it to the existing anaphora feature.
5. Add the **MIDDLE-TIER governing-predicate check** (one dep-hop to the matrix verb / copular predicate:
   happen-class eventive → episodic; characterizing-stative → kind) AFTER 1–4 and BEFORE declaring model-bound.
6. **Flag the true residual** (bare underspecified nominal + uninformative governing predicate) as requiring the
   incremental parser's ACTIVE-EVENT-REFERENT inventory (is there a discourse event referent to be anaphoric to?) —
   this is the build target for the incremental-context wiring, NOT a lexicon fix. The residual is SMALLER than the
   prior drill implied, by the governing-predicate fraction.
7. AUDIT UPDATE candidate for `BRAIN_FOUNDATIONAL_AUDIT.md`: episodic-event-token individuation = spatiotemporal-
   specificity binding (hippocampal, PINNED) with a graded semantic↔episodic continuum (Renoult & Rugg); the nominal
   routing onto it is SPECULATIVE-INFERRED (no direct nominal contrast measured).
