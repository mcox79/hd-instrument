# Research drill: the brain's pronoun -> event binding mechanism

SOLVER-side literature drill for the clause-level graded pronoun->event binder (who-did-what).
Date: 2026-08-29. Scope: LEAD-WITH-BIOLOGY. Neuroscience + psycholinguistics, mechanisms + studies,
one implication per question for the binder. ASCII only.

Frame under test (from brief): Centering (Grosz/Joshi/Weinstein 1995) Cb = preferred antecedent,
combined as graded cue-based retrieval (Lewis & Vasishth 2005) via additive cue activation -> softmax.
Cues already in hand: recency, grammatical-subjecthood, Cb, frequency, first-mention, parallelism,
ACT-R base-level activation.

---

## Q1. STAGED vs FOCUS-DRIVEN

**Answer: focus-driven (b), with pronoun resolution as a confirmatory readout of an already-running
focus/attentional state. Staged (a) is not what the biology shows.**

### Mechanism
Comprehension does not first "solve the pronoun" then "attach the event." It maintains a persistent
attentional pointer at the discourse entity currently in focus, updates a situation model in which the
protagonist ("who") is a continuously tracked dimension, and indexes each incoming clause event onto
that focused entity as the clause is built. The pronoun is a cheap referring form precisely BECAUSE the
referent is already the focused entity; resolving it is confirming the pointer, not searching from
scratch. This is why anticipatory ("who comes next") effects appear BEFORE the pronoun is even read.

### Key studies
- **Gordon, Grosz & Gilliom (1993), Cognitive Science 17:311-347 -- the Repeated-Name Penalty.** A
  repeated proper name for an entity that is the current center is read SLOWER than a pronoun, and the
  penalty appears only when the antecedent is prominent (subject / focused). A name is costly exactly
  when the entity is already in focus. -> Focus is a live state that comprehension is reading against,
  not a per-clause recomputation. Almor (1999) Informational Load Hypothesis gives the same result a
  cost mechanism: a full NP is penalized as redundant information about an already-focused entity.
- **Gernsbacher Structure Building Framework (Gernsbacher & Hargreaves 1988; Gernsbacher 1990).**
  Comprehension = lay a foundation on the first-mentioned entity, MAP incoming clauses onto it,
  ENHANCE the referent's activation and SUPPRESS competitors. The "Advantage of First Mention" (the
  foundation entity stays most accessible regardless of recency) is the foundation-laying + mapping
  process. Event material is mapped onto the standing foundation entity -> event-to-focus binding is
  the default operation, resolution is downstream.
- **Zwaan & Radvansky (1998) event-indexing model; "Who-When-Where" experimental test.** Readers track
  five situation-model dimensions (protagonist/who, time, space, causality, intentionality). Protagonist
  and time updating are resistant to task demands (i.e. obligatory/automatic). A protagonist
  discontinuity reliably slows reading. -> The "who" dimension is a maintained index that events are
  hung on; binding events to the current protagonist is a routine, automatic updating process.
- **Grosz & Sidner (1986) attentional state; Kintsch (1988) Construction-Integration.** Discourse
  processing carries a dynamic focus space (attentional state) that constrains what is salient;
  CI settles a coherent representation by spreading activation and letting the focused/connected nodes
  win. Both are focus-as-running-state architectures, not resolve-then-attach pipelines.
- **Koornneef & Van Berkum (2006) implicit-causality reading/ERP; Van Berkum et al. (1999) / Nieuwland
  & Van Berkum (2006) Nref.** Readers commit to a predicted next-referent BEFORE the pronoun (early
  focusing effects at/around the pronoun, anticipatory). A referentially ambiguous pronoun (two
  compatible foci) triggers a sustained frontal negativity (the Nref) -- a cost of holding >1 focus
  candidate live. -> Resolution is confirmation/selection over a pre-activated focus, not a fresh search.

### Neural signature
LIFG (BA44/45) carries the "unification / integration load" of linking anaphor to antecedent, rising
with antecedent distance and competition (Nieuwland et al. 2007, fMRI). Referent MAINTENANCE across the
discourse is carried by an episodic/binding network -- medial PFC, hippocampus/parahippocampal cortex,
and precuneus (with left angular gyrus + precuneus specifically implicated in backward anaphora). The
split is telling: a temporo-parietal/medial-temporal system HOLDS the focused referent as a bound
situation-model index; frontal cortex pays a cost only to (re)integrate. That is the anatomy of a
focus-driven binder with a confirmatory integration step, not a two-stage resolver.

### Operationalization of "current focus" to bind events to
Maintain a single persistent register `Cb_current` = the highest-ranked forward-looking center (Cf) of
the PREVIOUS clause (by the brief's Cf ranking: subject > object > other), carried forward with a decay.
Per clause: (1) bind the clause event/action to the retrieved pronoun referent, but (2) SEED the
cue-based retrieval with a strong "match-to-`Cb_current`" cue so the focused entity is the odds-on
winner unless another cue-cluster overrides. Update `Cb_current` after each clause. Net: the event
attaches to whatever wins retrieval, but retrieval is biased by a running focus state -- exactly the
brain's "focus-driven with confirmatory readout" shape, and it drops straight into your additive-cue ->
softmax with `Cb_current`-match as one high-weight cue.

**Implication:** Make focus a PERSISTENT STATE VARIABLE (a `Cb_current` register with decay), not a
per-clause recomputation; give match-to-current-focus a high cue weight; bind the event to the
retrieval winner. This is a weighting/state change to the model you already have, not a new stage.

---

## Q2. IS Cb A SEPARABLE CUE (topic persistence beyond most-recent-subject)?

**Answer: YES, separable -- sustained topichood adds antecedent-prediction power beyond "most recent
grammatical subject." But a large part of that power is already latent in your ACT-R base-level
activation cue, so add an EXPLICIT Cb-persistence cue and do not double-count.**

### Mechanism
Centering transition preferences rank discourse states by how well they SUSTAIN the current center:
CONTINUE (Cb stays same, and is Cp/predicted-next) > RETAIN (Cb stays same but not predicted next) >
SMOOTH-SHIFT > ROUGH-SHIFT. The preference is over CONTINUITY of the center, i.e. it explicitly rewards
an entity that has BEEN the Cb, over and above being the most recent subject. Givon's topic-continuity
work makes topicality a scalar tracked by its own measures (referential distance = recency; PERSISTENCE
= how many of the next ~10 clauses the entity survives as an argument). Persistence is a distinct axis
from referential distance -- an entity can be recent-but-not-persistent or persistent-but-not-most-recent.

### Key studies
- **Grosz, Joshi & Weinstein (1995); Brennan, Friedman & Pollard (1987) centering algorithm.** The
  transition ordering (CONTINUE>RETAIN>SHIFT) is defined on center CONTINUITY, not on recency or role
  alone; a candidate that continues the established Cb is preferred even against a more recent competitor.
- **Givon (1983) Topic Continuity in Discourse (quantitative, cross-language).** Referential distance
  (recency) and persistence (forward survival / sustained topichood) are separately measured properties;
  they are only partially correlated. Sustained topichood predicts continued mention independently of
  raw recency. -> Persistence is its own predictive signal.
- **Gordon et al. (1993) + Gordon & Chan (1995).** Repeated-Name-Penalty is strongest for the entity
  that has been the sustained center, not merely the last-mentioned NP -- reading-time evidence that
  sustained centerhood is tracked as its own accessibility signal.
- **Corpus fact (centering instantiations, Poesio et al. 2004; Spanish/English studies).** Cb is
  realized as subject ~73-80% of the time -- so Cb and grammatical-subject are highly correlated but
  NOT identical; the ~20-27% divergence is exactly where a separate Cb cue earns its weight.
- **Base-level learning (Anderson ACT-R; Lewis & Vasishth 2005).** Base-level activation rises with each
  retrieval of an entity and decays with time: B_i = ln(sum_k t_k^-d). An entity repeatedly re-centered
  accrues higher base-level activation. So topic PERSISTENCE is PARTLY encoded already by your
  base-level cue -- but base-level is a smooth recency-weighted retrieval history, whereas centering is
  a discrete "was this the ranked center of the IMMEDIATELY previous clause" signal. They are correlated
  but not the same; the CONTINUE/RETAIN preference is a sharper, clause-local signal than decayed
  base-level.

### Implication
Add an explicit **Cb-persistence / streak cue**: boost a candidate by (was-Cb-of-previous-clause) AND
by a bounded streak count (consecutive clauses as Cb), implementing CONTINUE>RETAIN>SHIFT as a
graded transition-consistency bonus. Keep it SEPARATE from base-level activation but expect partial
collinearity -- fit/regularize their weights jointly so you do not double-count recency. The
incremental win to look for: cases where the sustained topic is NOT the most recent subject (the
~20-27% Cb/subject divergence) -- that is where Cb pays its way.

---

## Q3. THE HARD (CUE-CONFLICT) CASES: how much residual is STRUCTURAL vs genuinely SEMANTIC?

**Answer: The pronoun-binding posterior factorizes into a STRUCTURAL likelihood term and a
SEMANTIC/coherence PRIOR term. A purely structural binder captures the likelihood but is BLIND to the
prior, and cue-conflict cases live disproportionately in the prior. Much of the "semantic" residual is
COHERENCE-RELATION / VERB-SEMANTICS driven (implicit causality, parallelism, result-vs-explanation) --
cheap to approximate WITHOUT a world-knowledge KB. A thin, irreducible core needs real world knowledge,
and that core is exactly the anti-typical residual your sibling problem found KBs dead on.**

### Mechanism (the key result for your ceiling)
Kehler & Rohde's Bayesian model: P(referent | pronoun) proportional to P(pronoun | referent) *
P(referent). The two factors have DIFFERENT drivers, empirically:
- **Likelihood P(pronoun | referent) = production/form bias = STRUCTURAL.** Whether a speaker would
  pronominalize a given referent is driven by grammatical role (subjecthood/obliqueness) and
  information structure (topicality). This is the part your structural cues (recency, subjecthood, Cb,
  first-mention, parallelism) actually model.
- **Prior P(referent) = next-mention bias = SEMANTIC/COHERENCE.** Which entity gets talked about next,
  regardless of referring form, is driven by the coherence relation the comprehender expects (Explanation
  after "because" -> implicit-causality bias; Result; Parallel; Elaboration) and by verb semantics /
  world knowledge. This is the part a structural binder cannot see.

Cue-conflict cases (recency vs subjecthood vs topicality disagree) are precisely where the structural
likelihood is FLAT/ambiguous, so the semantic prior dominates the posterior. That is why they feel hard:
they are the cases the structural factor was never going to resolve.

### Key studies
- **Kehler & Rohde (2013), Theoretical Linguistics; Kehler, Kertz, Rohde & Elman (2008), J. Semantics
  25:1 "Coherence and coreference revisited."** Established the production/comprehension asymmetry:
  pronoun PRODUCTION is insensitive to the semantic/coherence biases that strongly drive
  INTERPRETATION. Structural cues (grammatical role, topicality) govern form; coherence/semantics govern
  which referent. A structural-only model conflates the two and will mis-weight cue-conflict items.
- **Rohde, Kehler & Elman (2006, 2007) next-mention studies.** Coherence relation (e.g. Occasion vs
  Explanation) and verb aspect shift next-mention expectations independently of grammatical role -> the
  prior is real and separable from structure.
- **Koornneef & Van Berkum (2006); Featherstone & Sturt (2010); Kehler et al. implicit causality.**
  Implicit-causality verbs (e.g. "frightened" -> subject-cause; "feared" -> object-cause) shift the
  antecedent expectation by verb semantics alone, measurable at/near the pronoun in reading time and
  ERP. This is a VERB-LEVEL semantic signal -- cheap to tabulate (a verb-bias lexicon), no world KB.
- **Parallelism / coherence transitions (Smyth 1994; Chambers & Smyth 1998).** Grammatical parallelism
  (subject->subject, object->object) is a strong cue for the Parallel/Continue relation -- you already
  have a parallelism cue, which recovers a chunk of the "semantic" residual structurally.
- **Hobbs (1979).** The strong-semantic pole: coherence + inference + world knowledge do the work. The
  irreducible residual (genuine world-knowledge disambiguation, "the trophy didn't fit in the suitcase
  because it was too big/small") lives here -- and matches your sibling finding that world-KBs are dead
  on the anti-typical residual (KBs encode TYPICALITY; the residual is anti-typical by construction).

### How much is structurally recoverable (estimate, deflated)
- Cases where structural cues AGREE and win: already handled -- these are not the residual.
- Cue-conflict cases recoverable by adding a **coherence/verb-bias prior** (implicit-causality lexicon +
  connective "because/so/and" + parallelism): a SUBSTANTIAL slice of the residual, because much apparent
  "semantics" is actually stereotyped verb-bias + coherence-transition regularities, not open world
  knowledge. This is the highest-yield, brain-faithful addition (it IS the prior the brain uses).
- Irreducible factual-world-knowledge core (Hobbs-type, anti-typical): a SMALL but real residual that no
  structural or coherence cue and no typicality-KB will reach. Expect your structural+coherence binder to
  approach, but not fully hit, the perfect-binding ceiling; the last few points are genuinely semantic
  and world-knowledge-bound.

### Implication
Do NOT model pronoun binding as structural-only. Add a **coherence/verb-bias PRIOR term** to the softmax:
(1) an implicit-causality verb-bias score for the main verb (subject-biased vs object-biased), (2) a
connective-conditioned coherence-relation expectation (because -> Explanation/IC; and/then -> Occasion;
so -> Result), (3) keep parallelism as the Parallel-relation cue. Combine multiplicatively with the
structural likelihood (posterior = structural-likelihood x coherence-prior), matching Kehler-Rohde.
Accept a residual ceiling below perfect binding: the remaining anti-typical, world-knowledge cases are
out of reach of any structural OR typicality-KB approach -- flag them, do not chase them with a KB.

---

## Q4. THE ACTIVE FOCUS SET: compete over all entities, or a small maintained working set?

**Answer: A SMALL actively-maintained set, not all prior entities. Restricting the candidate pool to
recently-active entities (roughly the Cf of the last ~1-2 utterances plus the standing Cb) is
brain-faithful AND helps -- it removes similarity-based interference from decayed distractors. But do
NOT hard-prune to a single item: keep a small competitive set so RETAIN/SHIFT are still recoverable.**

### Mechanism
Working memory in comprehension is a tiny focus of attention over a content-addressable long-term store.
Only a very small number of entities are in the privileged, fast-access focal state at once; everything
else is retrieved by cue-match with a cost and with interference. Centering formalizes the same thing:
the Cf list is the small set of entities realized in the CURRENT utterance that are candidate centers for
the NEXT -- a per-utterance active set, not the whole discourse. Retrieval competition happens within
that active set; distant entities compete only weakly and mostly as interference.

### Key studies
- **McElree (2001, 2006) focus of attention; Cowan (2001) ~4-chunk capacity.** Speed-of-access data show
  a sharp dichotomy: focal information (1 item, McElree; a few, Cowan) is retrieved at a distinct, fast
  rate; everything else is content-addressable retrieval at a slower, uniform rate independent of amount
  of interpolated material. -> The brain privileges a tiny active set for immediate binding.
- **Lewis & Vasishth (2005); McElree, Foraker & Dyer (2003).** Cue-based retrieval from a
  content-addressable store is subject to SIMILARITY-BASED INTERFERENCE and fan: adding more items that
  share the retrieval cue (e.g. same gender/number) slows and degrades retrieval. -> A large candidate
  pool of feature-matching distractors HURTS; restricting to recently-active candidates reduces fan and
  interference, improving accuracy.
- **Van Berkum et al. (1999); Nieuwland & Van Berkum (2006, 2008) -- the Nref effect.** A referentially
  ambiguous pronoun (two candidates in the active set both compatible) elicits a SUSTAINED frontal
  negativity. Direct neural evidence that (a) the brain holds a SMALL set of compatible candidates live,
  and (b) it pays an ongoing cost when the set has >1 winner -- i.e. it is competing over a maintained
  active set, and a clean single-focus is the cheap default.
- **Grosz, Joshi & Weinstein (1995) Cf list; Walker (1998) cache model.** Centering's Cf is explicitly a
  small per-utterance forward-center set; a working-memory "cache" holds the locally salient entities and
  the rest is in long-term store, retrieved on demand. Matches the McElree/Cowan architecture exactly.

### Implication
Gate the candidate pool by a **recency/activity window**: default candidates = entities realized in the
last ~1-2 clauses (the Cf set) UNION the standing `Cb_current` (even if slightly older), rather than all
prior compatible entities. This is brain-faithful (focus of attention + Cf set) and should HELP by
cutting similarity-based interference from decayed same-gender/number distractors. Keep the window SOFT,
not hard: do not collapse to one item (that kills RETAIN/SHIFT and any cue-conflict recovery); keep the
small set and let cue-based softmax compete within it. If an entity outside the window is needed
(long-range topic return), let a strong Cb/base-level match pull it back in -- do not delete it, just
down-weight it out of the default competition.

---

## BOTTOM LINE

- **Staged or focus-driven?** FOCUS-DRIVEN. The brain runs a persistent focus/Cb attentional register and
  a situation model in which the protagonist ("who") is continuously tracked; it indexes each clause
  event onto the focused entity as the clause is built, and pronoun resolution is a confirmatory,
  cue-weighted READOUT of that already-running focus (RNP, Advantage of First Mention, event-indexing,
  anticipatory IC/Nref effects all point this way). Build: a `Cb_current` STATE register with decay,
  high cue weight on match-to-focus, event bound to the retrieval winner -- a weighting/state change to
  your existing additive-cue -> softmax, not a new resolve-then-attach stage.

- **Is Cb separable?** YES. Sustained topichood (CONTINUE>RETAIN>SHIFT; Givon persistence) predicts the
  antecedent beyond "most recent grammatical subject," and Cb diverges from subject ~20-27% of the time
  -- that divergence is where the cue earns weight. Caveat: your ACT-R base-level cue ALREADY encodes
  much of topic persistence via retrieval history, so add an explicit Cb-streak cue but fit its weight
  jointly with base-level to avoid double-counting.

- **Residual: structural vs semantic?** The posterior factorizes -- STRUCTURAL likelihood (form/production
  bias: role, topicality) x SEMANTIC/coherence PRIOR (next-mention: implicit causality, coherence
  relation, world knowledge). Your structural cues capture the likelihood; cue-conflict cases live in the
  prior and are invisible to a structural-only binder. A SUBSTANTIAL part of the residual is recoverable
  cheaply and brain-faithfully by adding a coherence/verb-bias PRIOR term (implicit-causality verb
  lexicon + connective-conditioned relation + parallelism) -- no world-knowledge KB needed. A SMALL,
  irreducible core (anti-typical, Hobbs-style world knowledge) is out of reach of any structural cue AND
  of typicality KBs (which is exactly why your sibling problem found KBs dead on it) -- expect to approach
  but not reach perfect binding, and flag that core rather than chase it.

- **Candidate set?** Compete over a SMALL actively-maintained set (Cf of last ~1-2 clauses + standing Cb),
  not all prior entities. Brain-faithful (focus of attention, Cf, Nref) and helps by cutting
  similarity-based interference. Keep the window soft (down-weight, do not delete distant entities) so
  long-range topic return and RETAIN/SHIFT stay recoverable.

---

## TLDR (plain language)
The brain does not first figure out who "she" is and then attach the action. It keeps a running spotlight
on whoever the story is currently about, and hangs each new action on that person as it reads; working out
"she" is just checking the spotlight. So the binder should keep a running "who we're talking about" state
and lean hard on it, rather than re-deciding from scratch every clause. Staying-on-topic (the same person
being the subject several clauses running) is a real, extra clue worth its own signal, though the model
already half-captures it. The genuinely hard cases -- where recency, subject, and topic disagree -- are
mostly decided by the MEANING of the verb and the expected because/so/and relation, which is cheap to add
as a verb-bias table and gives most of the remaining gain; only a thin sliver needs real-world facts that
no lookup table will fix. Finally, only compete among the handful of people mentioned in the last clause or
two plus the current topic, not everyone in the story -- that matches how the brain's small focus works and
should reduce mistakes from look-alike distractors.

## QUESTIONS
None.

## NEXT STEPS (for the SOLVER; not executed here)
1. Add a persistent `Cb_current` register (decay) and a high-weight match-to-focus cue; bind event to the
   retrieval winner. Ablation: fixed-per-clause recompute vs persistent register.
2. Add an explicit Cb-persistence/streak cue (CONTINUE>RETAIN>SHIFT), fit jointly with base-level.
3. Add a coherence/verb-bias PRIOR term (implicit-causality verb lexicon + connective-conditioned relation
   + existing parallelism), combined multiplicatively with the structural likelihood; measure the
   cue-conflict subset specifically.
4. Gate candidates to a soft recency window (Cf of last ~1-2 clauses + standing Cb); measure interference
   reduction vs all-entities competition.
5. Characterize the irreducible residual (anti-typical, world-knowledge) and FLAG rather than chase it.

---

## References
- Gordon, Grosz & Gilliom (1993), Pronouns, Names, and the Centering of Attention in Discourse. https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1703_1
- Almor (1999), Noun-phrase anaphora and focus: the Informational Load Hypothesis. (RNP mechanism; see review) https://www.researchgate.net/publication/353804173_REPEATED-NAME_PENALTY_A_MULTIFACTORIAL_EFFECT_PENALIDADE_DO_NOME_REPETIDO_UM_EFEITO_MULTIFATORIAL
- Gernsbacher (1990) / Gernsbacher & Hargreaves (1988), Language Comprehension as Structure Building. https://gernsbacherlab.org/wp-content/uploads/papers/StrucBding_Frwk_Bt95.pdf
- Zwaan & Radvansky (1998) event-indexing; "Who-When-Where" test. https://link.springer.com/article/10.3758/BF03195811
- Grosz & Sidner (1986), Attention, Intentions, and the Structure of Discourse. (attentional state)
- Grosz, Joshi & Weinstein (1995), Centering: A Framework for Modeling the Local Coherence of Discourse. https://www.researchgate.net/publication/2481213_Centering_A_Framework_for_Modeling_the_Local_Coherence_Of_Discourse
- Lewis & Vasishth (2005), An Activation-Based Model of Sentence Processing as Skilled Memory Retrieval. https://www.ling.uni-potsdam.de/~vasishth/pdfs/Lewis-VasishthCogSci2005.pdf
- McElree (2001, 2006), focus of attention / memory structures subserving sentence comprehension. http://www.colinphillips.net/wp-content/uploads/2020/04/mcelree2003.pdf
- Cowan (2001), The magical number 4 in short-term memory.
- Givon (1983), Topic Continuity in Discourse: A Quantitative Cross-Language Study. https://benjamins.com/catalog/tsl.3
- Kehler, Kertz, Rohde & Elman (2008), Coherence and Coreference Revisited, J. Semantics 25:1. https://www.lel.ed.ac.uk/~hrohde/papers/KehlerKertzRohdeElman.2008.pdf
- Kehler & Rohde (2013), A probabilistic reconciliation of coherence-driven and centering-driven theories of pronoun interpretation, Theoretical Linguistics. https://www.researchgate.net/publication/272575348_A_probabilistic_reconciliation_of_coherence-driven_and_centering-driven_theories_of_pronoun_interpretation
- Rohde & Kehler (later synthesis), Prominence and coherence in a Bayesian theory of pronoun interpretation. https://www.sciencedirect.com/science/article/abs/pii/S0378216618302881
- Koornneef & Van Berkum (2006), implicit causality in pronoun processing (reading/ERP). https://www.sciencedirect.com/science/article/abs/pii/S0749596X05001464
- Van Berkum, Brown, Hagoort & Kok (1999); Nieuwland & Van Berkum (2006, 2008), the Nref (referential ambiguity) effect.
- Nieuwland et al. (2007), Neural mechanisms of anaphoric reference revealed by fMRI (LIFG unification). https://pubmed.ncbi.nlm.nih.gov/21713189/
- Hobbs (1979), Coherence and Coreference (strong-semantic pole).
- Smyth (1994); Chambers & Smyth (1998), parallelism in pronoun resolution.
