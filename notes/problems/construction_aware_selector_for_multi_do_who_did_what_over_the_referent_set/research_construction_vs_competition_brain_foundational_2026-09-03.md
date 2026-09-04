# Brain-mechanism research drill: Construction-Grammar vs feature-competition in thematic role assignment (2026-09-03)

5-lane literature scan (CxG-vs-word-order dissociation; brain circuit mechanism; small-clause/resultative patienthood;
register invariance + passive/inversion selector-vs-parse). Depth caveat: most findings are from abstracts / secondary
summaries; full-text was fetched where noted. Verdicts marked PINNED (evidence-backed) vs OUR-INVENTION (a defensible
engineering choice under test). This is the reference cited by `SOLVED.md` §0.

## Q1. When does construction-level knowledge assign a role DIFFERENTLY from linear word-order? (the dissociation)
Construction Grammar's own flagship evidence dissociates the construction from the **VERB'S lexical** meaning, NOT from
word order — and in every signature demonstration the stimuli are in **canonical word order**, so the construction's
template *is* a word-order/grammatical-relation pattern. The two therefore **agree by construction** on canonical
English:
- Goldberg 1995 (*Constructions*, UChicago), 2006 (*Constructions at Work*): "She sneezed the napkin off the table",
  "She baked him a cake" — the ASC supplies roles the verb lacks. But linear position already gets the surface relation
  right in each. Partial exception: the **way-construction** ("dug his way out") has a non-referential fake object — a
  "postverbal NP = affected entity" heuristic misfires (Israel 1996).
- Bencini & Goldberg 2000 (*JML* 43:640): sorting tracks construction not verb — a construction-vs-VERB dissociation
  (canonical stimuli), not construction-vs-order.
- Johnson & Goldberg 2013 (*Lang. & Cog. Proc.* 28:1439): jabberwocky ASC priming — dissociates from verb meaning
  (none present), not from the word-order template.
- Kako 2006 (*Cognition* 101:1): nonce-verb subjects rated agent-like, objects patient-like — itself a **word-order/
  position** effect, not a dissociation from it.
- The genuine order-vs-structure dissociations come from ADJACENT literatures: Bever 1970 (NVN heuristic fails on
  passives/clefts); Ferreira 2003 (*Cog. Psych.* 47:164, role misassignment on noncanonical sentences); Bates &
  MacWhinney Competition Model (cross-linguistic cue conflict — English weights order, case-rich languages let case
  override).
**VERDICT (PINNED):** CxG's added value for role ASSIGNMENT is concentrated in **non-canonical / cue-conflict /
typologically-marked** territory; on canonical English word-order and construction are **redundant**. => our measured
null (construction-aware selection = 0.000 over the proximity/Competition-Model selector) is the EXPECTED,
brain-faithful result.

## Q2. The brain's actual role-binding computation: construction-indexed or feature-competition?
Converges on **feature-competition as the core, general-purpose computation**, with construction/event-specific
knowledge as a complementary *prior*, not the binding mechanism:
- **Frankland & Greene 2015 (PNAS 112:11732); 2020 (Cereb. Cortex 30:3838):** left mid-STC encodes abstract
  agent/patient slots that are **verb-independent AND surface-syntax-independent** (active/passive decoded identically;
  "no region carried information about the surface subject/object"). Event/verb-specific conjunctions live *separately*
  in amPFC; hippocampus pattern-separates. The abstract role code is NOT a construction template. (Full text fetched.)
- **Bornkessel-Schlesewsky & Schlesewsky eADM 2006 (Psych. Review 113:787):** one weighted **prominence-competition**
  (animacy, case, voice, position) computes the Actor; only the cue *weights* re-parameterize per language/construction
  — no per-construction template retrieval. N400 = thematic/actorhood competition (Frisch & Schlesewsky 2001); P600 =
  structural reanalysis. 2019 reframes these as precision-weighted prediction error.
- **Kuperberg 2007/2021:** dual-stream (semantic-memory heuristic + combinatorial), general probabilistic integration
  + stored **event/situation schemas** (verb/event-organized, not construction-indexed). Wang, Kuperberg & Jensen 2018
  (MEG/RSA) = item-specific predictive pre-activation.
- **Hagoort MUC; Vosse & Kempen 2000 (*Cognition* 75:105):** lexicalist unification by **competitive inhibition** among
  candidate attachments — feature/candidate-competition. Blache 2024 shows constructions can be *inputs* to unification
  while the operation stays uniform.
- Oscillatory binding (Martin & Doumas 2017; LISA/DORA) addresses the *binding substrate* (how a bound pair is held),
  orthogonal to the construction-vs-competition question.
**VERDICT (PINNED):** the brain binds roles by graded feature-competition; construction/event knowledge enters as a
complementary prior (amPFC / event schemas). => our deployed `hybrid_role_patient` (Competition Model: order-dominant +
voice/gap/animacy) **is** the brain's mechanism; a construction-template router on top is *less* brain-faithful.

## Q3. Object-complement / naming / resultative ("call X Y", "make X Y"): one patient, or ill-posed?
- Small-clause syntax (Stowell 1981; den Dikken 2006 *Relators and Linkers*): the matrix verb's object is the whole
  small clause **[NP Predicate]** (e.g. [the place a haven]) — so "the matrix verb's patient" is a **category error**;
  patienthood, if defined at all, is one level down, between two co-arguments of an embedded predication.
- Canonical **adjectival resultatives** ("painted the barn red") ARE well-posed: "barn" = patient, "red" = result
  predicate (Goldberg & Jackendoff 2004 *Language* 80:532; Rappaport Hovav & Levin 2001 *Language* 77:766; L&RH 1995
  *Unaccusativity*, MIT). A labeler failing here has a fixable gap.
- **Naming/appellative is CONTESTED and unsettled as of 2023:** Sánchez Sánchez 2023 (*Cuadernos de Lingüística*)
  argues naming is a caused-change-of-state resultative (object = "theme"/patient); Matushansky 2008 (*Ling. & Phil.*
  31:573) argues it is a stative/classificatory small clause (the name is a predicate, the object a non-causal theme);
  Bruening 2018 (*Ling. Inquiry* 49:537) argues against small-clause analyses entirely. Both camps agree the naming
  nominal is a predicate, not a second independent argument; they disagree on whether the object is "patient" at all.
**VERDICT (PINNED indeterminacy):** annotator disagreement on naming/object-complement is **expected, theory-grounded
inconsistency, not annotation error**. => our gold's naming inconsistency (spaCy dobj matches 10 / oprd matches 15) is
real; a construction rule cannot win an ill-posed target. The brain-faithful move is a small-clause EXTRACTOR (emit
both args), not a single-patient pick.

## Q4. Generalization / register: is word-order dominance register-invariant?
- The Competition-Model word-order/first-noun default (MacWhinney, Bates & Kliegl 1984) is a robust default, measured
  on canonical stimuli; Ferreira's good-enough processing shows it persists (misfires even in adults on simple modern
  sentences). **Whether cue-WEIGHTING shifts with literary/archaic register is UNTESTED** — a genuine gap; treat
  "register re-weights cues" as an assumption, not a finding.
- Literary/older prose carries MORE non-canonical order: heavy-NP-shift ~5-10% even in modern print (Wasow 1997/2002;
  Arnold et al. 2000; Staub, Clifton & Frazier 2006 "last resort"); quotative inversion concentrated in fiction/
  narrative (Cichosz); locative inversion characteristic of literary description (Bresnan 1994; Birner & Ward 1998).
**VERDICT (PINNED default; register-reweighting = OUR-INVENTION/untested):** word-order dominance is register-robust as
a default. => our measured **register-invariant null** (construction adds 0 on modern AND 19c) is expected. A proximity
selector misfires *more* in non-canonical pockets (more common in literary prose), but the fix there is PARSE +
discourse, not construction re-weighting.

## Q5. Passive / locative inversion / cleft: a SELECTOR job or a PARSE job?
Splits by construction (not uniform):
- **Passive**: selector-fixable via local morphology (aux + participle) per the eADM cue architecture — and already
  handled by our `graded_role_assigner` voice cues. (Ferreira 2003: humans still misassign even with correct cues —
  heuristic-vs-structure competition is architectural.)
- **Locative inversion**: needs BOTH structural detection AND discourse old/new tracking (Bresnan 1994; L&RH 1995;
  Birner & Ward 1998 *Information Status and Noncanonical Word Order*) — least selector-amenable.
- **Clefts**: unambiguously **filler-gap / long-distance dependency** resolution, structurally parallel to wh-movement
  (2026 filler-gap-family work; Bever 1970; Ferreira 2003) — a flat role-selector over a candidate list CANNOT get it;
  the role is defined by an embedded clause's gap position it never sees.
**VERDICT (PINNED):** passive = selector (done); locative inversion = parser + discourse module; cleft = parser
(filler-gap). => the parse-recoverable residual is the FILED parser problems, not a selector cue.

## Bottom line
The measured null (construction-aware selection = 0.000 over the proximity/Competition-Model selector on canonical
English who-did-what) is **the brain-faithful truth, not a wall**: the brain binds roles by feature-competition (which
we already deploy), and Construction Grammar's role-assignment value is redundant with word-order on canonical
English. There is **no genuinely brain-foundational lever left for the SELECTOR** — it is at the competent-reader
ceiling. Every remaining lever is upstream (the referent-per-NP SOURCE + register-native POS + filler-gap PARSE) or in
the gated meaning channel; the naming/object-complement residual is genuinely ill-posed even for the brain.
