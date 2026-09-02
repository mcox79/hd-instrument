# BRAIN MECHANISM DRILL — the SELECTION wall on 19c prose (who-did-what)

Read-only literature drill (SOLVER data, not user-facing). Goal: for each wall, name the brain
mechanism/circuit, the computational-level papers, whether it is learnable from RAW exposure (no gold
labels), and the SPECIFIC way a co-occurrence-only model falls short — then the strongest glass-box
approximation for an FHRR/VSA substrate.

Empirical anchors from SOLVED.md: (1) 27% of items are reachable-but-mispicked = SELECTION, not parse
(base who-did-what 0.428 vs reachability 0.698); (2) flat verb-PREP selectional association is a REAL signal
(AUC 0.64) but does NOT resolve selection and is NOT separable from a shuffled-association twin; (3) copular
"X was a Y" is a base 0/376 representation gap; (4) PP-attachment is only 8% of the reach residual.

---

## HEADLINE

The selection wall is NOT "co-occurrence cannot do this in principle." It is **"FLAT / MARGINAL
co-occurrence cannot; STRUCTURED + COMPOSED co-occurrence largely can."** The project's AUC-0.64 verb-PREP
signal failing its twin is the *textbook predicted symptom* of using the marginal P(prep|verb) instead of
the role-distinguished, argument-composed joint. The brain's mechanism (thematic fit computed from
generalized event knowledge, activated compositionally by words-as-cues) IS learnable from raw parsed
exposure — but only with two ingredients the project's attempt lacked: (a) **role-distinguished slots**
(agent-slot vs patient-slot fillers) and (b) **composition over the arguments seen so far** (agent×verb →
patient). There is an irreducible world/discourse-knowledge residual, but it is smaller than it looks and it
caps the ceiling rather than blocking the route.

---

## 2. THE SELECTION WALL (the core) — which reachable noun is the verb's argument?

### The mechanism, as psycholinguistics has resolved it (four escalating positions)
1. **Selectional restrictions** (Katz & Fodor 1963): hard binary features ([+edible] object of *eat*).
   Falsified as the operative mechanism — violations are frequent, gradient, and interpretable; the brain
   does not gate on binary features.
2. **Graded selectional preference** (Resnik 1996): information-theoretic. Selectional preference strength
   S(v) = KL(P(class|v) ‖ P(class)); selectional association A(v,c) = the class's contribution to that KL.
   Computed over WordNet classes. This is Resnik's key move: **generalize the co-occurrence over a taxonomy
   so rare/unseen nouns inherit their class's preference.** This is a verb→NOUN-class signal — it is exactly
   the family the project built (AUC 0.64) and it is a real but *insufficient* signal (below).
3. **Thematic fit** (McRae, Spivey-Knowlton, Tanenhaus 1998; Ferretti, McRae, Hatherell 2001): the graded
   goodness of a noun as the AGENT vs the PATIENT of a specific verb, measured by human ratings and shown to
   be computed *rapidly and incrementally* and to drive parsing (reduced-relative resolution: "The cop/crook
   arrested…"). Crucial upgrade over Resnik: **thematic fit is ROLE-SPECIFIC** — the same noun can be a great
   patient and a poor agent of the same verb. Ferretti et al.: verbs prime typical agents, patients, and
   instruments *differentially* ("arresting" → cop as agent, criminal as patient).
4. **Generalized event knowledge (GEK) / words-as-cues** (McRae & Matsuki 2009; Elman 2009 "On the meaning
   of words and dinosaur bones"; Metusalem, Kutas, Urbach, Hare, McRae, Elman 2012; Bicknell, Elman, Hare,
   McRae, Kutas 2010): comprehenders hold rich knowledge of events (who does what to whom, with what, where),
   and each word is a CUE that activates the relevant event schema, which then generates expectations about
   the other participants. Metusalem 2012 (N400 ERP): a contextually-anomalous word draws a *reduced* N400 if
   it fits the described EVENT, even after controlling for pairwise lexical association to preceding words and
   to the expected continuation — i.e., the driver is event-level, not word-pair-level. Hodapp & Rabovsky
   2021 / Rabovsky: the N400 itself is an **error-based implicit-learning signal** — prediction error on the
   event's semantic representation.

### The decisive computational fact for a co-occurrence substrate
Bicknell et al. 2010 is the discriminating experiment: the plausibility of a PATIENT depends on the
COMBINATION of agent + verb ("the journalist checked the spelling" fast; "the mechanic checked the spelling"
slow). The marginal P(patient|verb) is the SAME in both — the signal lives entirely in the CONJUNCTION
agent×verb. Chersoni, Santus, Lenci, Blache 2017 ("Is Structure Necessary for Modeling Argument Expectations
in Distributional Semantics?") ran three distributional models on the Bicknell items:
- **DEPS (structured, dependency-typed role slots): ~72%**
- **Bag-of-arguments (unstructured collection of arg fillers): ~58% ≈ chance**
- **Bag-of-words: worse.**

That is the whole answer in one table. A model that pools arguments without role structure — which is what a
flat verb-noun or verb-prep co-occurrence model IS — sits at chance on the compositional selection task. Add
role-distinguished slots + composition and it jumps to ~72%. (Chow et al. 2015 "bag-of-arguments" ERP result
— no N400 difference for role reversals — is the human upper-bound nuance: early prediction may be partly
unstructured, but the *offline correct interpretation* needs roles; DEPS reproduces both.)

### Is it learnable from RAW exposure (no gold labels)? — YES, with structure
- Resnik selectional preference: learnable from a PARSED corpus + WordNet. No gold labels; needs a parser
  (the substrate has arc-eager) and a taxonomy (the substrate has the grounded semantic-graph organ).
- Thematic fit as a structured DSM: Erk 2007 / Erk, Padó, Padó 2010 (EPP exemplar model); Baroni & Lenci
  2010 (Distributional Memory — role prototype = average of dependency-typed fillers); Sayeed, Greenberg,
  Demberg 2016; Chersoni et al. Structured Distributional Model (SDM, 2019). All are **unsupervised over
  parsed raw text** — the only supervision is the (imperfect) parse that assigns typed slots, and that is
  exactly the "learned from usage" the brief itself invokes. No gold thematic-fit labels are needed.
- So "gold target-register data" is the SUPERVISED framing of an UNSUPERVISED mechanism. Correct target: a
  role-distinguished, taxonomically-smoothed, argument-composed selectional store built by running the
  substrate's own parser over 11M words of raw 19c LitBank. FOUNDATION-IS-FREE (static offline asset).

### What a raw co-occurrence-only model FUNDAMENTALLY misses (worst-first)
1. **Role structure.** verb-noun (or verb-prep) co-occurrence pools agent+patient+oblique into one bag. The
   selection question is "which noun is the PATIENT" — a role-typed query. Bag-of-arguments ≈ chance (58%).
2. **Composition / the conjunction.** The informative signal is P(patient | agent, verb), not P(patient |
   verb). Marginal statistics are *provably* uninformative on the Bicknell contrast (same marginal, opposite
   answer). This is precisely why the project's marginal verb-PREP signal (AUC 0.64) does not separate from
   its shuffled twin — the competitors are not distinguished by the marginal.
3. **Referential / discourse restriction.** Altmann & Kamide 1999 (anticipatory eye movements: "the boy will
   eat…" launches looks to the edible object *present in the scene*); Spivey-Knowlton & Sedivy 1995
   (referential context + verb type jointly drive PP attachment). Selection is over the candidates actually
   in the DISCOURSE MODEL, weighted by givenness/salience — a co-occurrence store has no discourse model.
4. **Genuine world/event knowledge for rare or novel events** — the irreducible residual. Structured DSMs
   cap ~70-75% on Bicknell; the top ~25-30% needs event knowledge that text co-occurrence underdetermines
   (novel combinations, causal/physical plausibility). This bounds the CEILING; it does not block the route.
   Note: much of what looks like "world knowledge" IS recoverable via taxonomic smoothing over structured
   contexts — the residual is the part that is genuinely never witnessed.

### Strongest glass-box approximation (FHRR/VSA mapping)
Build a **Structured Selectional / Thematic-Fit Store**, the McRae thematic-fit model realized as a
structured DSM in FHRR:
- **Role-typed filler prototypes.** For each verb v and role r ∈ {agent, patient, obl-of-prep-p}, prototype
  = VSA BUNDLE (superposition) of the dependency-typed fillers observed for (v, r) in parsed raw 19c text.
  This is a native VSA bundle; no new binding algebra (keep FHRR).
- **Composition.** To score a candidate patient n given the already-bound agent a: update the patient-slot
  expectation by (a, v) — e.g., bind agent-role⊗a into the query and take the SDM-style composed expectation
  vector; score = cos(n, composed_expectation). This is the ingredient that turns 58%→72%.
- **Taxonomic smoothing (the Resnik move) via an organ we already own.** Sparse archaic vocabulary is the
  register killer; smooth each candidate through the **grounded semantic-graph organ (PPR spreading
  activation over WordNet++, SOLVED 2026-09-01)** so a never-seen 19c noun inherits its class's fit. This is
  the register lever: same computation, re-estimated statistics.
- **Selection = argmax thematic fit over the reachable candidate set** the parser already produces
  (`_pp_args_for_verb`). The pick becomes semantic, not structural.
- **Controls that must pass (the project's own bar):** must beat a shuffled-role twin AND a bag-of-arguments
  (role-collapsed) twin CI-separated — the twin the project's marginal signal FAILED. If the structured
  store also fails the role-collapsed twin, the located negative deepens to "even structured composition does
  not separate on THIS population," which would implicate gold-quality contamination (below).

### Honest deflation
- Ceiling is bounded (~70-75% mechanism-level on clean data); do NOT promise the structured route closes all
  27%. Expect it to move a meaningful *fraction*, with a residual that is genuine world/discourse knowledge.
- The 27% figure is scored on a copula/oblique-contaminated who-did-what gold (SOLVED.md flags this). Clean
  the gold before quoting a target number, or the structured store will be graded against noise.
- "Raw exposure" here means no GOLD labels, but it DOES need the substrate's own parser to assign typed
  slots. The parser is imperfect on 19c; parse noise propagates into the store. This is acceptable (the brain
  also bootstraps from imperfect structure) but is the second thing to withdraw if the route underperforms.

---

## 1. PP-ATTACHMENT (verb-attach vs noun-attach) — confirm it is NOT the lever

- **Structural (lexically-blind):** Frazier's garden-path — Minimal Attachment (fewest nodes) + Late Closure
  (attach to current constituent), a fast first stage that ignores lexical/semantic content.
- **Lexical preference:** Ford, Bresnan & Kaplan 1982 — the verb's preferred subcategorization frame drives
  attachment ("wanted/positioned the dress on the rack"). Verb-specific.
- **Corpus-lexical:** Hindle & Rooth 1993 — the operative signal is the **COMPETITION** between P(prep|verb)
  and P(prep|noun) as a likelihood ratio / t-score, bootstrapped from unambiguous cases. ~80% from raw
  parsed text, no gold attachment labels. Collins & Brooks 1995 / Ratnaparkhi: the full quadruple
  (verb, N1, prep, N2) matters — **N2 (the preposition's object) is highly informative.**
- **Constraint satisfaction:** MacDonald, Pearlmutter & Seidenberg 1994 — parallel, probabilistic,
  competition-based integration of all constraints at the decision point (no separate structural stage).
- **Discourse:** Spivey-Knowlton & Sedivy 1995 — referential context + verb class modulate attachment.

**Takeaway for this problem:** PP-attachment IS largely a raw-co-occurrence problem and it is largely solved
(Hindle-Rooth), consistent with the SOLVED.md finding that PP-attach is only 8% of the residual. The
project's verb-PREP-only signal is *half of Hindle-Rooth* — it dropped the noun-PREP competitor and N2. But
since PP-attach is 8% and post-hoc re-attach HURTS (integrate at decision-time among real candidates, à la
MacDonald, not surgery), this is correctly de-prioritized. Do NOT re-open it.

---

## 3. REGISTER / SYNTACTIC ADAPTATION — re-weight existing statistics, don't learn new rules

- **Rapid syntactic adaptation:** Fine, Jaeger, Farmer, Qian 2013 (PLoS ONE) — comprehenders re-estimate the
  relative frequency of constructions (e.g., reduced-relative vs main-clause) from recent exposure, within
  tens of sentences. (Caveat: Harrington Stack, James & Watson 2018 partial-replication failure — the effect
  is real but effect sizes and boundary conditions are debated; treat magnitude as uncertain.)
- **Expectation/surprisal:** Levy 2008 — processing difficulty ∝ −log P(word|context); comprehension is
  prediction; adaptation = updating the probability model. Gradient/error-driven updates make more-surprising
  words drive larger adaptation.
- **Learning-as-adaptation:** Chang, Dell & Bock 2006 (Dual-path) — syntactic priming/adaptation is implicit
  learning via prediction-error weight updates on the SAME weights that acquired syntax, at a small learning
  rate. Adaptation and acquisition are one mechanism.
- **Ideal adapter / belief-updating:** Kleinschmidt & Jaeger 2015; beta-binomial belief updating — the
  comprehender maintains generative-model beliefs about the current register/talker and updates which known
  distribution generates the input.

**Consensus mechanism:** register adaptation is primarily **RE-ESTIMATION of the parameters of EXISTING
distributions** (which constructions / subcat frames / selectional preferences are how frequent HERE), i.e.,
Bayesian re-weighting over a mixture of known components — NOT acquisition of new syntactic rules. That is
why minimal exposure suffices. **Implication:** the register fix is to re-estimate the SELECTION store's
statistics on the target register from raw exposure (error-driven), NOT to retrain a parser on gold. Confirms
SOLVED.md's "exposure-driven, no gold parses" and that the parent's "gold target-register data" is the
supervised framing of an unsupervised mechanism.

---

## 4. COPULAR / PREDICATIVE "X was a Y" — a distinct predication binding, not a verb-argument event

- **The copula is semantically light / near-empty** (Mikkelsen; "Copular clauses" handbook chapter): *be* is
  unaccusative, has no external argument, assigns no theta-role. The PREDICATE ("a Y" / adjective) carries the
  predication; the copula carries only tense/agreement/polarity (which still matter for interpretation).
- **The predication relation is configurational:** subject–predicate = a small clause (Stowell); predication
  is established by the subject-predicate configuration, not by the copula's own content. "a Y" is a property
  / kind (type ⟨e,t⟩) ascribed to X.
- **Higgins 1979 taxonomy** — predicational ("X was a doctor": ascribe kind/property) vs specificational
  ("The winner was John": identify referent) vs identificational vs equative. Literary "X was a Y" is
  overwhelmingly PREDICATIONAL — an **is-a / property-ascription**, categorically different from a
  verb→patient thematic-role binding.

**Why it is a representation gap (base 0/376):** UD makes the predicate complement the HEAD and the copula a
leaf `cop` child, so from the copula token the predicate is unreachable by convention — but more deeply, the
reader has **no is-a binding schema** at all. Selectional-preference machinery does not apply (there is no
verb selecting an argument; the copula selects nothing). The fix is a SEPARATE predication binding:
`bind(subject, PREDICATION_role ⊗ predicate-nominal/adjective)` asserting kind/property membership, distinct
from `bind(verb, PATIENT_role ⊗ filler)`. This is a small, register-INDEPENDENT frontend build (make
`predicate_argument_frontend` copula-aware), worth wiring for its own sake — but NOT sold as a register
PP-attach win (SOLVED.md shows it is not twin-separable as a parser gain).

---

## BOTTOM LINE FOR STRATEGY
1. **The SELECTION wall is buildable, not a ceiling.** Route it as a **structured, role-distinguished,
   argument-composed, taxonomically-smoothed selectional/thematic-fit store** (McRae thematic fit ≈ Chersoni
   SDM), realized in FHRR (bundle role-filler prototypes; compose known args; smooth via the grounded
   semantic-graph organ). This is the exact upgrade the literature says turns 58%→72%, and it is what the
   project's FLAT verb-PREP marginal (AUC 0.64, twin-failing) was missing. Learnable from raw parsed exposure
   — no gold labels. Ship it to `role_assignment_is_untested_on_archaic_literary_prose`.
2. **Ceiling is bounded (~70-75% mechanism-level); clean the who-did-what gold first** (copula/oblique
   contamination) or the store is graded against noise. Controls: must beat a shuffled-role twin AND a
   role-collapsed bag-of-arguments twin CI-separated.
3. **Copular predication:** small register-independent frontend build (is-a binding), file separately.
4. **PP-attachment / gold parse/POS data / frequent-frames:** stay retired (8% / 2.2% / net-negative).
5. **Register adaptation = error-driven re-estimation of the SELECTION store's statistics on raw exposure,**
   not gold-parser retraining.
