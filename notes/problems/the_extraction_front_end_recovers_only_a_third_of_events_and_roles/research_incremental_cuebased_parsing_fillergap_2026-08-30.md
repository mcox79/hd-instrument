# Brain-mechanism grounding: INCREMENTAL, cue-integrated, PREDICTIVE role assignment for non-passive non-canonical (filler-gap / displaced-argument) constructions

Research drill for problem `the_extraction_front_end_recovers_only_a_third_of_events_and_roles`.
Date: 2026-08-30. Scope: RESEARCH-ONLY literature synthesis. No code or config touched (one file written, this one).

**What this grounds (the OPEN remainder).** Event DETECTION is solved (tense-agnostic; separate drill
`research_brain_event_detection_tense_agnostic_and_nv_disambiguation_2026-08-30.md`). The voice/morphology role
fix (passives: surface-subject→PATIENT, by-phrase→AGENT) is wired. What remains is **NON-PASSIVE NON-CANONICAL
role assignment** — filler-gap / displaced-argument constructions (object relatives, subject/object clefts,
wh-questions, topicalization) where **neither linear word order NOR voice determines who-did-what**. The measured
collapse: the live reader scores non-canonical roles at ~0.12–0.29 (word-order 0.149 / graded_role 0.118 on the
n=1224 pre-verbal-patient subset), while a competent structural parse scores ~0.99. This drill grounds the
brain-faithful mechanism — an **incremental, cue-integrated, predictive structure-builder** — precisely enough to
BUILD and TEST it, with a concrete cue set, weighting scheme, gap-prediction rule, and pre-registered can-fail
predictions.

**FENCED DEAD-ENDS this drill respects (established on-disk; NOT re-proposed):** thematic-fit VECTORS (~0.65
noun-side ceiling regardless of representation), POST-HOC fit gates (irreducible canonical tradeoff), and
fused/linear/precision-weighted POST-HOC cue combination. The resolution below is that cues compete **DURING
attachment (online)**, not after — and §4 (P4) is the experiment that discriminates online from post-hoc.

**Discipline flags applied.** (1) Lit-scan calibration penalty: prediction confidences deflated 0.15–0.25,
novel-synthesis capped ~0.50; stated as hypotheses-pending-VET. (2) Every mechanism marked **PINNED**
(well-replicated brain/behavioral finding) vs **CONTESTED** (active debate / localization-uncertain). (3)
COMPUTATION (copy exactly) vs PARAMETER (sweep, never adopt) flagged for the build. (4) The strategic read
"our attacher ≈ the brain" is a hypothesis, not an established equivalence.

---

## 1. ACTIVE FILLER STRATEGY & GAP PREDICTION — how the brain detects a displaced filler and predicts its gap online

**The core claim (PINNED).** When the parser encounters a displaced constituent (a wh-word, a relative-clause
head, a clefted pivot, a topicalized NP), it does **not** wait for bottom-up evidence of where the argument is
missing. It holds the filler in working memory and **actively posits a gap at the first grammatically licit
position**, binding the filler there immediately.

- **Active Filler Strategy / filler-driven parsing (PINNED).** Frazier & Flores d'Arcais (1989, *J. Memory &
  Language*, "Filler-driven parsing"): the parser is filler-driven — an unassigned filler triggers an active
  search that ranks a gap at the earliest possible site. Clifton & Frazier (1989) formalize the Active Filler
  Strategy: "rank the option of assigning a detected filler to a gap above all others." (Crain & Fodor 1985 is
  the origin of the filled-gap paradigm.)

- **The filled-gap effect = the diagnostic evidence (PINNED).** Stowe (1986, *Language & Cognitive Processes*):
  in *"My brother wanted to know who Ruth will bring __ home to __"* vs a filled position, readers **slow down at
  an overt NP that occupies a potential gap site** after a wh-filler (e.g. reading-time spike at "us" in *"who
  Ruth will bring us home to"*). The slowdown proves the parser had **already posited a gap there** and is
  surprised to find the position filled. Gap-positing is therefore **predictive and eager**, not driven by the
  bottom-up detection of a missing argument. Widely replicated (Crain & Fodor 1985; Stowe 1986; and in
  eye-tracking, e.g. active gap-filling regardless of dependency length — Chow & colleagues).

- **The dependency is formed AT THE VERB, and semantic/plausibility cues are checked THERE, online (PINNED —
  keystone for this build).** Traxler & Pickering (1996, *J. Memory & Language* 35:454–475, "Plausibility and the
  processing of unbounded dependencies: an eye-tracking study"): readers show a **plausibility-mismatch slowdown
  at the verb** — *"the garage which the man wrote regularly…"* (implausible: you can't write a garage) is harder
  **immediately at "wrote"**, before any gap site is reached, than *"the book which the man wrote…"*. This is the
  single most important finding for us: **filler-gap resolution integrates structural AND semantic plausibility
  cues ONLINE at the moment of dependency formation**, not after a committed parse. It is the empirical warrant
  that cue integration is *during* attachment.

- **What EXACTLY triggers gap-positing, and how early.** Trigger = an unassigned filler in memory + arrival at a
  head (verb/preposition) that **subcategorizes for an argument whose in-situ position is empty**. The parser
  posits the gap at the **first** such licit position (Active Filler Strategy), constrained by grammar (it does
  **not** posit gaps across islands — Traxler & Pickering Exp. 2; Stowe 1986; Wagers & Phillips). Timing: the
  dependency and its plausibility check register **at the verb**, within the first-pass reading of that region
  (Traxler & Pickering; Wagers & Phillips 2009 place gap-positing "in advance of the bottom-up evidence").

- **CONTESTED sub-point (does not affect the build):** whether the mechanism literally posits an empty-category
  *trace/gap* at a position vs forms a *direct association* between filler and verb (Pickering & Barry 1991
  "direct association"). Both predict the same online, at-the-verb integration; our build implements the
  operational version ("bind the filler to the verb's unfilled slot at the first licit head") which is neutral
  between them.

**Build consequence.** The attacher must be **left-to-right incremental** with a working-memory **filler buffer**;
on hitting a verb it (a) reads the verb's subcategorization frame, (b) for each obligatory slot with no in-situ
filler, posits a gap and binds the most active displaced filler, (c) retracts if the position is overtly filled
(filled-gap), (d) evaluates plausibility/animacy as a cue **at that moment**, not later.

---

## 2. CUE-BASED RETRIEVAL as the core operation — Lewis & Vasishth (2005), McElree, Van Dyke & McElree

**The claim (PINNED as a framework).** Building the filler-verb (and subject-verb) dependency **is a
content-addressable memory-retrieval operation**. At the verb, the parser issues a set of **retrieval cues**;
each item in working memory is activated in proportion to how well its features match the cues; the **most active**
item is retrieved as the argument. This is the SAME content-addressable retrieval the project already pins for
memory retrieval (Van Dyke & McElree similarity-based interference) — **flagged for REUSE below.**

- **Lewis & Vasishth (2005, *Cognitive Science* 29:375–419, "An activation-based model of sentence processing as
  skilled memory retrieval").** Sentence processing = a series of skilled associative retrievals in ACT-R,
  modulated by fluctuating activation and similarity-based interference. Incoming words are integrated into
  syntactic chunks stored with **feature bundles**; a retrieval at the verb uses cues that are **a subset of the
  target's features** — "only features that are cued at the verb constitute retrieval cues" (e.g. number is a cue
  only when the verb morphologically marks agreement). PINNED framework; specific parameterization is CONTESTED
  and under active refinement (Nicenboim & Vasishth 2018 Bayesian evaluation; Engelmann et al.).

- **The retrieval mathematics (ACT-R declarative memory; COPY the computation, SWEEP the parameters).** LV05
  instantiate the standard ACT-R equations (Anderson et al. 2004). For candidate chunk *i* under the cue set at
  the verb:

  - Activation: **A_i = B_i + Σ_j (W_j · S_ji) − P·M_i + ε**
    - **B_i = ln(Σ_k t_k^{−d})** — base-level activation from recency/frequency; decay **d ≈ 0.5**. (This term
      makes recent NPs more retrievable → it is where **locality/DLT effects fall out**, §4.)
    - **S_ji = S_max − ln(fan_j)** — associative strength from cue *j* to chunk *i*; **fan_j = number of chunks in
      memory matching cue *j***. The `ln(fan)` term IS **similarity-based interference / cue overload**: the more
      items share a cued feature, the less each is boosted. **S_max ≈ 1.5** (sweep).
    - **W_j = W / n** — source activation of cue *j*, total goal activation **W (≈1)** split over the **n** active
      cues. This is the **cue-weighting knob** — replace the uniform `W/n` with **learned per-cue weights `w_j`**
      set by cue validity (§3) and swept.
    - **P·M_i** — partial-matching mismatch penalty; **M_i** = degree of feature mismatch (e.g. number
      disagreement), **P** a penalty scalar (sweep).
    - **ε** — logistic noise.
  - Retrieval = **argmax_i A_i**; retrieval latency **T = F · e^{−A_i}** (latency factor **F ≈ 0.14 s**; needed
    only if we model RT); retrieval **probability** ≈ logistic **1/(1+e^{−(A_i−τ)/s})** vs threshold τ.
  - **A usable confidence/abstain signal:** softmax over {A_i}; **if top-two activations are within a margin,
    ABSTAIN** — this maps directly to the arc-parser `margins` (best−second) abstain signal noted in the SOLVED
    file, and to the online "competition is close" state.

  **COMPUTATION (copy exactly):** the activation equation + cue-weighted content-addressable retrieval +
  `ln(fan)` interference. **PARAMETER (sweep, never adopt):** `w_j`, `S_max`, `d`, `P`, `F`, `τ`. (Project
  discipline: "our worst result copied a number; our best copied an operation.")

- **McElree (2000, *J. Psycholinguistic Research*) & McElree, Foraker & Dyer (2003, *JML*).** Speed-accuracy
  tradeoff studies show retrieval of a non-adjacent argument is **direct-access / content-addressable** (retrieval
  *speed* is constant regardless of distance; only *accuracy/probability* drops) — i.e. the parser does **not**
  serially search; it cue-addresses. PINNED. This licenses an **argmax-over-activation** implementation rather
  than a search.

- **Van Dyke & McElree (2006, *JML* 55:157–166, "Retrieval interference in sentence processing"; and Van Dyke
  2007, *JEP:LMC*).** THE reuse anchor. Manipulating retrieval **cues at the verb** (not memory load per se)
  produces interference: a distractor that **matches the verb's cues but is not its grammatical dependent** still
  competes and degrades retrieval. They separate **syntactic-cue interference** (cue = [+subject]/grammatical
  role) from **semantic-cue interference** (cue = "plausible subject of *this* verb"). PINNED and robust. This is
  the exact similarity-based interference the project already pins for memory — **same organ.**

**THE CONCRETE RETRIEVAL CUE SET a faithful implementation uses (for role assignment at the verb).** Two
retrievals per verb — one per licensed argument slot — each with its own cue bundle:

| slot | STRUCTURAL/SYNTACTIC cues | MORPHOLOGICAL cues | SEMANTIC cues |
|---|---|---|---|
| **AGENT/subject** | [+preverbal] / c-commands verb / [+nominative] (pronoun) / [+subject grammatical-fn] / [+displaced-filler]-active-for-first-empty-slot | number agrees with verb; person | animacy (high in hierarchy); agent-thematic-fit (verb's agent prototype) |
| **PATIENT/object** | [+postverbal] / [+gap after verb] / [+accusative] (pronoun) / [+object grammatical-fn] | (English: none on verb) | patient-thematic-fit (verb's patient prototype); lower animacy |

- **Voice flips the STRUCTURAL cue → role mapping** (the already-wired fix): on a passive clause the [+preverbal
  subject] cue maps to PATIENT and the [+by-phrase] cue to AGENT. This is a **cue-remapping**, cleanly inside the
  same retrieval.
- **The displaced filler carries a strong structural cue for the first unfilled slot** (Active Filler Strategy,
  §1): when a verb's object slot is empty (no in-situ postverbal NP), the displaced filler is the highly-active
  retrieval target for the PATIENT/[+gap] cue. This is how object-relatives/clefts get "who-did-what" right
  without word order: the gap-position cue, not linear order, drives the retrieval.

**How they are WEIGHTED & COMBINED (the scheme).** `w_j` per-cue weights initialized by **English cue validity**
(§3: structural/order ≫ agreement > animacy/fit), then swept. Combination is the **weighted-sum activation
A_i** above — cues compete **within a single retrieval at the verb**, so a strong structural cue can outvote a
weak semantic cue (and vice-versa) **online**, with no separate post-hoc gate (this is the escape from the fenced
tradeoff, §4/P4). `ln(fan)` handles interference; `P·M` penalizes agreement/case mismatch.

---

## 3. COMPETITION MODEL — cue validity sets the weights, and it is English-specific

**The claim (PINNED cross-linguistically).** MacWhinney, Bates & Kliegl (1984, *J. Verbal Learning & Verbal
Behavior* 23:127–150, "Cue validity and sentence interpretation in English, German, and Italian"); Bates,
McNew, MacWhinney, Devescovi & Smith (1982, *Cognition*). A cue's processing weight is set by its **cue
validity = availability × reliability** — availability = how often the cue is present when needed; reliability =
how often, when present, it gives the correct role. Weights are **language-specific** and learned.

**The English cue-validity ranking for AGENT/PATIENT assignment (PINNED):**

1. **WORD ORDER (preverbal-position / SVO first-noun-is-agent) — HIGHEST validity, dominant.** English speakers
   "rely overwhelmingly on word order," using a **first-noun strategy in NVN**. Preverbal position is **maximally
   available** (almost always present) and highly reliable in English → it wins even against conflicting cues.
   English speakers will call an inanimate first-noun the agent (*"the rock is kicking the cow"* → rock = agent),
   overriding animacy — the signature English result.
2. **Subject-verb NUMBER AGREEMENT — medium-low validity.** Available only when subject/object differ in number
   AND the verb marks it (English present tense only); **impoverished English morphology → low availability**.
   Used, but weakly, and it is **error-prone via retrieval interference** (agreement attraction, §below).
3. **ANIMACY / semantic thematic-fit — LOW validity in English, but the FALLBACK under conflict.** Low weight in
   English (unlike Italian/Spanish where it is higher); surfaces mainly when word order is neutralized or
   ambiguous. This is exactly why English non-canonical order collapses: word order is misleading and English
   assigns animacy too little weight to recover.
4. **CASE — high reliability but near-zero availability in English** (only pronouns he/him, she/her, who/whom) →
   effectively negligible except on pronominal arguments.

Contrast pins the language-specificity: **German** relies on **case + agreement + animacy** over order;
**Italian** shows **extreme reliance on agreement**. So the weights are not universal — they must be set to
**English** validities and swept, never adopted from another language.

**Agreement attraction confirms agreement is a fallible RETRIEVAL cue (PINNED).** Wagers, Phillips & Lau (2009,
*J. Memory & Language*, "Agreement attraction in comprehension: representations and processes"): comprehenders
accept *"The key to the cabinets **are** rusty"* — the verb's [+plural] agreement cue **mis-retrieves** the
plural attractor "cabinets." This is a **cue-based-retrieval illusion**, direct evidence that (a) agreement is
computed by the §2 retrieval mechanism and (b) it is unreliable → **weight it low and expect interference**
(feeds P5).

**How cue validity integrates ONLINE with the retrieval in §2.** Cue validity **sets the `w_j`** (and, more
subtly, the effective source-activation split) in the activation equation. The Competition Model was originally a
static cue-summation account; **the online instantiation is the LV05 retrieval** — cue validity determines how
much each matching feature boosts a candidate's activation **at the verb, during attachment**. So §3 supplies the
*weights*, §2 supplies the *online competition mechanism*, §1 supplies the *filler/gap trigger*. One integrated
operation.

---

## 4. EXPECTATION / SURPRISAL — Levy (2008), Hale (2001), Gibson (2000 DLT)

**Two forces, opposite signs (both PINNED).**

- **Expectation / surprisal is FACILITATORY (PINNED).** Hale (2001, NAACL, "A probabilistic Earley parser as a
  psycholinguistic model") and Levy (2008, *Cognition* 106:1126–1177, "Expectation-based syntactic
  comprehension"): processing difficulty at a word = its **surprisal, −log P(word | context)**. Structural
  prediction **reduces** cost: when the context makes the upcoming structure (e.g. the relative-clause verb, or
  the gap) **expected**, it is read faster. Levy shows this is equivalent to Hale's surprisal and derives it from
  parallel probabilistic parsing (resource reallocation across the expectation distribution). **For us:** having
  **predicted the gap** (Active Filler Strategy, §1) lowers the surprisal of the resolution at the verb — the
  prediction is what makes the online binding cheap and disambiguating.

- **Memory / locality is INHIBITORY (PINNED).** Gibson (2000, "The dependency locality theory: a
  distance-based theory of linguistic complexity") / Dependency Locality Theory: **integration cost ∝ the
  distance** (number of intervening **new discourse referents**) between a dependent and the head it attaches to;
  plus a **storage cost** for each predicted-but-not-yet-integrated head. Object relatives are hard because the
  filler-gap **integration spans more intervening referents** than subject relatives. **For us:** DLT is what the
  `B_i = ln(Σ t^{−d})` **base-level decay** term computes — a distant filler has decayed, so its activation at
  retrieval is lower → more error/interference. Locality is **built into** the retrieval, not a separate module.

- **The interaction (PINNED phenomenon; unification CONTESTED).** Levy (2008 §, pp. 1139–41) notes **surprisal
  alone does not predict locality**; the two are partially independent (Demberg & Keller 2008 find dependency
  length and surprisal only moderately correlated). The **facilitatory** expectation and the **inhibitory**
  locality can **trade off** (e.g. a longer dependency can be *less* surprising if the intervening material makes
  the continuation more predictable). Recent unification — **lossy-context surprisal** (Futrell, Gibson & Levy
  2020, *Cognitive Science*, "Lossy-context surprisal") — derives DLT locality **from** surprisal over a
  **noisy/decayed memory** of context, i.e. **prediction computed over the same lossy memory that retrieval reads
  from.** That is exactly our architecture: predict the gap (expectation) + retrieve the filler from a
  decaying buffer (locality). Mark the *unification* CONTESTED/active, the *two effects* PINNED.

**Build consequence.** The gap-prediction (§1) is the facilitatory expectation; the base-level decay `B_i` is the
inhibitory locality; both live inside the §2 retrieval. A concrete testable signature: **role accuracy should
degrade with filler-gap distance** (intervening referents) — Gibson DLT (folded into P5).

---

## 5. NEURAL SUBSTRATE — dorsal/ventral streams, MUC unification, and the agrammatic pattern

- **Dorsal stream = complex/non-canonical syntax; ventral = local/canonical combination (PINNED, localization
  details CONTESTED).** Friederici (2011, *Physiol. Rev.*, "The brain basis of language processing: from
  structure to function"; 2017, *Language in Our Brain*): a **ventral** pathway (via uncinate/IFOF, BA45/47 ↔
  temporal) handles local, semantically-driven combination and basic word order; a **dorsal** pathway (the
  **arcuate fasciculus** → **BA44**) handles **hierarchical/complex syntax**, and — the on-point finding — "the
  dorsal stream **only comes into play during the comprehension of syntactically complex sentences, that is,
  sentences involving either clausal embedding or deviations from the basic word order**." **Non-canonical
  filler-gap constructions ARE that regime.** Friederici (2012/2017): BA44 "creates **argument hierarchies** as a
  sentence is computed" and supports the basic binding operation (Merge). So the brain routes exactly our problem
  case to a dedicated structure-building circuit — mechanistic support that role assignment on non-canonical
  order is a **structural** operation, not a semantic-fit lookup (consistent with the fenced fit-vector ceiling).

- **LIFG = Unification, the online binding operation (PINNED framework).** Hagoort (2005, *TICS*; 2013, *Frontiers
  in Psychology*, "MUC (Memory, Unification, Control) and beyond"): **M**emory = stored lexical/syntactic
  knowledge (temporal cortex); **U**nification = **combining retrieved items into structure**, in **LIFG**;
  **C**ontrol = task/attention. LIFG activity **tracks incremental syntactic construction and scales with
  constituent size** during naturalistic comprehension. Unification IS the online integration operation our
  attacher performs; Memory (temporal) is the working-memory buffer §2 retrieves from. MUC and LV05 are
  complementary: MUC gives the neuro-functional division (retrieve-from-memory + unify-in-LIFG), LV05 gives the
  computational retrieval mechanics.

- **Agrammatism, Trace-Deletion, and the agent-first fallback (the parser-free floor as a functional model).**
  - **Trace-Deletion Hypothesis (CONTESTED).** Grodzinsky (1995, 2000, *Behavioral & Brain Sciences*, "The
    neurology of syntax"): Broca's agrammatics cannot represent the **traces of moved constituents**, so on
    movement-derived non-canonical sentences (reversible passives, object relatives, object clefts) they fall
    back on a **linear "agent-first" default** ("take the first NP to be the agent") → **chance performance** on
    reversible non-canonical, **above chance** on canonical actives/subject-relatives. **Explicitly CONTESTED:**
    variability across patients is large; alternatives include the **mapping hypothesis** (Schwartz, Linebarger,
    Saffran) and a **capacity/resource** account (Just, Carpenter et al. 1996, *Science* — comprehension breaks
    down under syntactic working-memory load, not trace-deletion per se). Original observation: Caramazza & Zurif
    (1976) — agrammatics fail reversible but not non-reversible (semantically-constrained) sentences.
  - **The BEHAVIORAL agent-first / canonical-order fallback is ROBUST (PINNED)** even though its mechanistic
    explanation is contested: across accounts, the impaired system defaults to **canonical linear order + whatever
    surface morphology (voice) survives**, and goes to **chance on reversible movement-derived items**.

  **Your claim — CONFIRMED with one qualification.** A **parser-free positional + voice reader** (first-NP-agent,
  flipped by voice, no gap/trace mechanism) **is a faithful functional model of the agrammatic OUTPUT pattern**:
  it is correct on canonical and on cue-supported (non-reversible/passive-marked) items and **at chance on
  reversible non-canonical** items — precisely the agrammatic profile. **Qualification:** it models the *behavior*
  (the output distribution), and it matches the *agent-first default* that all accounts agree on; it does **not**
  adjudicate the contested *mechanism* (trace-deletion vs mapping vs capacity). So state it as: "the current live
  reader is a functional model of **agrammatic comprehension** — it has the ventral/canonical route but **lacks
  the dorsal filler-gap structure-builder** (BA44/arcuate) — and the build adds exactly the missing dorsal
  operation." That framing is defensible and PINNED-supported; do not claim it instantiates trace-deletion
  specifically.

---

## 6. THE BUILD SPEC + PRE-REGISTRATION

### 6a. The minimal incremental cue-based-retrieval role attacher (glass-box, NO external LLM at inference)

**Architecture — one left-to-right incremental pass:**

1. **Encode NPs into a working-memory buffer.** As each NP is read, push a chunk with features:
   `{position_index, category, case(if pronoun), number, animacy, grammatical_fn_so_far, displaced_flag}`.
   `displaced_flag=True` for a wh-word, a relative-clause head NP, a clefted pivot, or a topicalized/fronted NP
   (the filler). Base-level activation decays with recency (`B_i = ln(Σ t^{−d})`, d≈0.5) → **DLT locality falls
   out** (§4).

2. **At each VERB, run one cue-based retrieval per licensed slot** (subcat frame → AGENT slot, PATIENT slot;
   more for ditransitives). For slot *s*, retrieve `argmax_i A_i(s)` where
   **A_i(s) = B_i + Σ_j w_j·S_ji(cue_{s,j}) − P·M_i**, cues per the §2 table, `S_ji = S_max − ln(fan_j)`.

3. **Voice remap (already wired):** on a passive clause, map the [+preverbal-subject] structural cue to the
   PATIENT slot and [+by-phrase] to the AGENT slot before retrieval.

4. **Active Filler Strategy / gap-prediction rule (the new dorsal operation):**
   - If a `displaced` filler is buffered and the verb has an **obligatory slot with no in-situ filler**, POSIT A
     GAP: the filler receives a **strong structural cue** ([+gap]/[+object-position]) for that slot → it is the
     high-activation retrieval target. Bind it (Active Filler Strategy: earliest licit gap).
   - **Filled-gap retraction (Stowe 1986):** if the position is overtly filled by an in-situ NP, do **not** posit
     the gap there; keep the filler active and carry it to the next licit head.
   - **Grammatical constraint:** do not posit a gap across an island / into an already-saturated clause (approx:
     do not bind a filler past a clause boundary that has its own complete argument set).

5. **Online plausibility (Traxler & Pickering 1996):** animacy / thematic-fit enters as a **low-weight cue inside
   the retrieval at the verb** — it can break ties but cannot override a strong structural/gap cue. It is **never
   a post-hoc gate** (this is the whole point — §fenced dead-ends).

6. **Confidence / abstain:** softmax over {A_i(s)}; if top-two within margin `m`, **ABSTAIN** (defer to the
   positional+voice floor or emit low-confidence) — reuses the arc_parser `margins` signal.

**Initial cue weights (English cue validity §3; SWEEP all):** structural/order/gap `w_struct ≈ 0.60` ≫ agreement
`w_agr ≈ 0.20` > animacy/fit `w_anim ≈ 0.20`; case as a high-reliability cue **only when present** (pronouns).
Sweep each in [0,1] normalized; sweep `S_max` (~1.5), `d` (~0.5), `P`, margin `m`. **COPY** the activation
equation + gap rule; **SWEEP** every scalar.

**REUSE (flagged per task §2).** The `ln(fan)` similarity-based-interference retrieval is the **same
content-addressable operation the project already pins for memory retrieval** (Van Dyke & McElree). Do **not**
build a second retrieval engine — wire the role attacher onto the existing retrieval organ, with a role-specific
cue set. This is a one-organ-serves-two-consumers wiring, not a new build.

**Glass-box guarantee:** every cue is an explicit feature test; the score is a weighted sum; the decision is an
argmax with an inspectable per-cue contribution vector. No LLM, no opaque vector.

### 6b. Pre-registered, can-fail predictions (deflated; each: floor, info-free twin, refutation)

Gold: a **non-canonical, non-passive** slice — object relatives, subject/object clefts, wh-questions,
topicalization — from a pre-existing modern gold (UD-EWT dep-derived; QA-SRL; supplement with a controlled
**reversible-sentence** probe set). **Strongest REAL floor = word-order + the now-wired voice fix**, recomputed on
the same items; plus the majority-role constant per subset. **Info-free twin = cue-shuffled / permuted-attachment**
(same machinery, cue→feature bindings scrambled) — MUST LOSE. Report bootstrap CI half-width + null p95 beside
every margin. Confidences are lit-scan-deflated.

- **P1 — Incremental cue-based attachment beats the positional+voice floor on non-passive non-canonical
  (CORE).** On the non-canonical non-passive subset, the incremental attacher raises who-did-what role accuracy
  **CI-separated over word-order+voice**, twin losing. *Floor:* word-order+voice. *Refute:* if it does **not**
  beat word-order+voice CI-separated, the incremental/gap machinery adds nothing over the positional floor here —
  the collapse is not recoverable by this mechanism. *Confidence ~0.55* (structural ceiling is high — competent
  parse ~0.99 — so headroom exists, but our hand-built attacher is weaker than spaCy; deflated).

- **P2 — The Active Filler Strategy is load-bearing (filled-gap discriminator).** On **filled-gap** items (an
  overt NP occupies the first potential gap site), the attacher WITH the ASF + filled-gap retraction assigns the
  displaced filler's role correctly **more often than a "last-resort" variant** that binds the filler only when
  forced at clause end. *Discriminator:* the accuracy gap **specifically on filled-gap items**. *Refute:* no
  differential on filled-gap items ⇒ ASF is inert; a trivial "bind filler to first empty slot" rule suffices and
  the eager-prediction claim is unsupported. *Confidence ~0.50.*

- **P3 — English cue-validity ordering holds: structural cue dominates (Competition Model).** Sweeping `w_j`, the
  optimum has **`w_struct` (order/gap) dominant**; an **animacy/fit-dominant** weighting **degrades** accuracy on
  reversible non-canonical items. *Discriminator:* swept weight profile + reversible-item accuracy under
  order-dominant vs animacy-dominant. *Refute:* if an animacy-dominant weighting **matches or beats** the
  order-dominant one on reversible items, the English Competition-Model ranking does not hold in our data (or the
  structural/gap cue is too noisy to carry the weight it should). *Confidence ~0.60* (well-supported by
  MacWhinney).

- **P4 — ONLINE integration escapes the post-hoc canonical tradeoff (the crux; discriminates from the fenced
  dead-end).** On reversible items with an **atypical agent** (low-animacy agent, e.g. *"the rock that the boy
  kicked"* — but note the agent here is animate; construct items where the displaced/first NP is an atypical
  agent), the **online** attacher (animacy as a low-weight in-retrieval cue) shows **no larger typical−atypical
  accuracy gap** than a structural baseline, WHEREAS a reconstructed **POST-HOC animacy/fit gate** (the fenced
  dead-end, rebuilt only as a control) shows the **canonical tradeoff** (helps atypical, hurts typical). *Refute:*
  if the online attacher shows the **same** typical/atypical tradeoff as the post-hoc gate, integrating cues online
  did **NOT** escape the tradeoff — the mechanism's central claim fails and the redirect to "online" was wrong.
  *Confidence ~0.45* (most novel; novel-synthesis-capped, deflated).

- **P5 — Similarity-based retrieval interference is present (signature that it IS cue-based retrieval).** Accuracy
  is **lower on high-interference items** — two NPs matching the verb's cues (both animate/plausible agents, or a
  number-matching distractor between filler and verb), and **longer filler-gap distance** (Gibson DLT) — than on
  low-interference/short items, CI-separated. *Refute:* if accuracy is **flat** across high- vs low-interference
  and across distance, the model is **not** behaving as content-addressable retrieval (the `ln(fan)`/decay terms
  aren't doing the work) — it is a lookup, not the pinned mechanism. *Confidence ~0.55* (robustly predicted by Van
  Dyke & McElree; the risk is our items don't span enough interference range).

- **P6 — The isolation win survives END-TO-END through the live reader (the phase-gate trap).** Wired into
  `situation_reader.read()` (reusing the existing retrieval organ), the attacher lifts the **end-to-end**
  who-did-what number on the non-canonical subset over the current live front-end, **without regressing canonical**,
  twin losing. *Refute (a valid NEGATIVE = full PASS):* an isolation win that does **not** survive end-to-end →
  name the exact downstream consumer that drops the richer structure (binder / situation model / coref) — that is
  the next problem. *Confidence ~0.50* (phase-gate risk is real and has bitten this project before).

**What would REFUTE the mechanism overall:** P1 fails (no gain over positional+voice) **OR** P4 fails (online shows
the same tradeoff as post-hoc) **OR** P5 fails (no interference/distance signature). P1-fail says the collapse
isn't recoverable by incremental cue-competition at our fidelity; P4-fail kills the specific "online beats
post-hoc" thesis (and would resurrect the fenced tradeoff as truly irreducible); P5-fail says we didn't build
content-addressable retrieval at all. Any of the three is a rigorous, redirecting negative.

---

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b — the parse/role front-end entry)

The non-passive non-canonical role stage's brain-faithful target is now grounded to implementation detail. **PINNED
mechanism:** an INCREMENTAL, predictive, cue-integrated structure-builder = Active Filler Strategy gap-prediction
(Frazier & Flores d'Arcais 1989; Stowe 1986 filled-gap; Traxler & Pickering 1996 online plausibility-at-the-verb)
+ content-addressable cue-based RETRIEVAL at the verb (Lewis & Vasishth 2005; McElree 2000; Van Dyke & McElree 2006
similarity-based interference — **the SAME retrieval the project pins for memory; REUSE it**) + English cue-validity
weighting (MacWhinney, Bates & Kliegl 1984: word-order ≫ agreement > animacy > case) + expectation/locality both
inside the retrieval (Levy 2008 facilitatory surprisal; Gibson 2000 DLT inhibitory locality = base-level decay;
lossy-context surprisal unifies them). **Neural:** dorsal arcuate→BA44 handles exactly "deviations from basic word
order / embedding" (Friederici 2011/2017); LIFG Unification = the online binding op (Hagoort MUC). **The current
parser-free positional+voice reader is a functional model of AGRAMMATIC comprehension** (agent-first fallback,
chance on reversible non-canonical — Grodzinsky 2000 [Trace-Deletion CONTESTED], Caramazza & Zurif 1976, Just et
al. 1996 [capacity account]) — it has the ventral/canonical route and **lacks the dorsal filler-gap
structure-builder**; the build adds exactly that missing dorsal operation. **Fenced dead-ends confirmed as
POST-HOC failures the ONLINE mechanism resolves:** the irreducible canonical tradeoff of a post-hoc fit gate is a
consequence of integrating cues *after* the parse commits; online cue-competition at the verb (P4) is the test that
the redirect is correct.

---

## TLDR (plain language)

For plain "she kicked him" sentences the reader can use word order — first name is the do-er. But English lets the
do-er and the done-to move around: "the man **that the dog chased**", "it was **the dog** that chased the man",
"**who** did the dog chase?". Here word order lies, and our reader falls apart (worse than a coin toss). The brain
does something specific and well-studied: the moment it hears a moved-out word, it **predicts where that word
belongs** and holds it in mind, then **at the verb it pulls back the right word by matching a small set of clues at
once** — where the word sat, whether it agrees in number, whether it's the kind of thing that can do the action.
Crucially it weighs all the clues **at the same instant**, so an unusual do-er ("the rock the boy kicked") doesn't
force a re-do — the strong "this slot is empty, the moved word fills it" clue simply outweighs the weak "rocks
don't usually act" clue on the spot. That is different from what we already tried and shelved (deciding roles first,
then second-guessing with a plausibility check afterward — which provably can't win). The brain even routes exactly
these twisty sentences to a dedicated grammar circuit; damage to it produces the same "just guess the first name is
the do-er" pattern our current reader shows — which means our reader is basically a brain-damaged one, and the fix
is to add back the one missing circuit. The build: read left to right, predict the gap, pull the right word from
memory by weighted clue-matching at the verb, with English's clue weights (word position matters most, agreement
some, meaning least), reusing the memory-retrieval part we already have. Six pre-registered tests can each kill the
idea — most importantly, that judging clues on-the-spot beats judging them afterward.

## QUESTIONS
None blocking. One design choice left to the solver (not the owner): whether P4's post-hoc gate control is worth
rebuilding purely as a contrast (it is a fenced dead-end, but as a *control* it is the cleanest proof the online
redirect is right) — I recommend yes, control-only.

## NEXT STEPS
1. Build the minimal incremental attacher (§6a): incremental pass + filler buffer + per-slot cue-based retrieval,
   REUSING the existing content-addressable retrieval organ; cue set + English-validity weights from §2/§3.
2. Run P1–P6 on the non-canonical non-passive gold (object relatives / clefts / wh / topicalization + a reversible
   probe set); P4 (online vs post-hoc) is the crux and the discriminator from the fenced dead-end.
3. If P1 passes but P6 fails end-to-end, name the downstream consumer that drops the structure — that is the next
   problem (the phase-gate has bitten here before).

---

## References (author, year, finding, URL)

- Bates, E., McNew, S., MacWhinney, B., Devescovi, A. & Smith, S. (1982, *Cognition*). Functional constraints on
  sentence interpretation; cue competition. (Competition Model foundations.)
- Caramazza, A. & Zurif, E.B. (1976, *Brain & Language*). Agrammatics fail semantically REVERSIBLE but not
  non-reversible sentences → syntactic comprehension deficit on non-canonical order.
- Clifton, C. & Frazier, L. (1989). Active Filler Strategy: rank assigning a filler to a gap above other options.
- Crain, S. & Fodor, J.D. (1985). Origin of the filled-gap paradigm; active gap-seeking.
- Frazier, L. & Flores d'Arcais, G.B. (1989, *J. Memory & Language*). Filler-driven parsing: an unassigned filler
  triggers an active earliest-gap search.
- Friederici, A.D. (2011, *Physiological Reviews*, "The brain basis of language processing: from structure to
  function"); (2017, *Language in Our Brain*). Dorsal arcuate→BA44 for complex/non-canonical syntax
  ("deviations from basic word order or embedding"); BA44 builds argument hierarchies / Merge.
  https://www.ehu.eus/HEB/KEPA/Advanced_2012/2011_Friederici_The%20brain%20basis%20of%20language%20processing%20From%20structure%20to%20function.pdf
- Futrell, R., Gibson, E. & Levy, R. (2020, *Cognitive Science*, "Lossy-context surprisal"). DLT locality derived
  from surprisal over a noisy/decayed memory — unifies expectation and locality.
  https://sites.socsci.uci.edu/~rfutrell/papers/futrell2020lossy.pdf
- Gibson, E. (2000, "The dependency locality theory"). Integration cost ∝ distance in intervening discourse
  referents; storage cost for predicted heads.
- Grodzinsky, Y. (1995; 2000, *Behavioral & Brain Sciences*, "The neurology of syntax"). Trace-Deletion
  Hypothesis: traces of moved constituents lost → agent-first default → chance on reversible movement-derived
  sentences. CONTESTED. https://pubmed.ncbi.nlm.nih.gov/10857717/
- Hagoort, P. (2005, *TICS*; 2013, *Frontiers in Psychology*, "MUC (Memory, Unification, Control) and beyond").
  LIFG = Unification (online binding of retrieved items into structure), scales with constituent size.
  https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00416/full
- Hale, J. (2001, NAACL, "A probabilistic Earley parser as a psycholinguistic model"). Surprisal =
  −log P(word|context) as processing difficulty.
- Just, M.A., Carpenter, P.A., et al. (1996, *Science*). Capacity-constrained comprehension; syntactic complexity
  breaks down under working-memory load (alternative to trace-deletion).
- Levy, R. (2008, *Cognition* 106:1126–1177, "Expectation-based syntactic comprehension"). Expectation is
  facilitatory; equivalent to surprisal; surprisal alone doesn't predict locality (pp. 1139–41).
  https://www.mit.edu/~rplevy/papers/levy-2008-cognition.pdf
- Lewis, R.L. & Vasishth, S. (2005, *Cognitive Science* 29:375–419, "An activation-based model of sentence
  processing as skilled memory retrieval"). Parsing = cue-based content-addressable retrieval in ACT-R; cues are a
  subset of target features cued at the verb; similarity-based interference from cue overload.
  https://www.ling.uni-potsdam.de/~vasishth/pdfs/Lewis-VasishthCogSci2005.pdf
- MacWhinney, B., Bates, E. & Kliegl, R. (1984, *J. Verbal Learning & Verbal Behavior* 23:127–150, "Cue validity
  and sentence interpretation in English, German, and Italian"). Cue validity = availability × reliability;
  English = word-order dominant; German = case/agreement/animacy; Italian = agreement.
  https://www.sciencedirect.com/science/article/abs/pii/S0022537184900938
- McElree, B. (2000, *J. Psycholinguistic Research*); McElree, Foraker & Dyer (2003, *JML*). Retrieval of
  non-adjacent arguments is direct-access/content-addressable (distance affects accuracy, not speed).
- Nicenboim, B. & Vasishth, S. (2018, *J. Memory & Language*; arXiv 1612.04174). Bayesian evaluation of cue-based
  retrieval models — parameterization is under active refinement. https://arxiv.org/pdf/1612.04174
- Pickering, M. & Barry, G. (1991). Direct-association alternative to gap/trace positing (CONTESTED mechanism;
  same online prediction). 
- Stowe, L.A. (1986, *Language & Cognitive Processes*). Filled-gap effect: reading-time slowdown at an overt NP in
  a potential gap position after a wh-filler → the parser posited a gap there predictively.
- Traxler, M.J. & Pickering, M.J. (1996, *J. Memory & Language* 35:454–475, "Plausibility and the processing of
  unbounded dependencies: an eye-tracking study"). Plausibility-mismatch slowdown AT THE VERB, before the gap →
  filler-gap dependency formed online and semantics integrated during formation.
  https://www.sciencedirect.com/science/article/abs/pii/S0749596X9690025X
- Van Dyke, J.A. & McElree, B. (2006, *J. Memory & Language* 55:157–166, "Retrieval interference in sentence
  processing"); Van Dyke, J.A. (2007, *JEP:LMC*). Retrieval interference from cue-matching distractors that are
  not grammatical dependents; syntactic vs semantic retrieval cues. (Reuse anchor.)
- Wagers, M.W., Lau, E.F. & Phillips, C. (2009, *J. Memory & Language*, "Agreement attraction in comprehension:
  representations and processes"). Agreement attraction as a cue-based-retrieval illusion → agreement is a
  fallible retrieval cue. http://www.colinphillips.net/wp-content/uploads/2014/08/wagerslau2009.pdf
- Wagers, M.W. & Phillips, C. (2009/2014, *J. Linguistics* / *Language & Cognitive Processes*). Wh-dependencies
  formed in advance of bottom-up evidence; grammatically-constrained (island-sensitive) active retrieval.
  https://people.ucsc.edu/~mwagers/papers/WagersPhillips.CSC.JLING09.pdf
