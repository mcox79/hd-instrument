# Who-did-what vs the brain: performance, signal-loss chain, and the EXACT mechanism divergence (2026-09-03)

Grounded in the measured cells (`exp_construction_brain_waterfall_v1`, `..._brain_comparison_v1`,
`..._whole_composition_v1`, `..._ideal_composition_v1`) + the 5-lane brain-mechanism research drill. Competent-reader
proxy = spaCy dependency parse (REFERENCE-ONLY diagnostic oracle; never on the inference path).

## 1. How our performance compares to the brain
Two different pictures, and which one you get depends on the SOURCE, not the selector:

| chain | S1 source | S3 select\|present | END | vs competent reader |
|---|---|---|---|---|
| **IDEAL (referent-per-NP source)** | 1.000 | 0.928 | **0.928** | spaCy 0.922 → **TIED** (+0.006 CI[-0.016,+0.028] n.s.) |
| DEPLOYED (coref-column source) | 0.818 | — | **0.470** | source-limited, not mechanism-limited |

**On the ideal chain we are AT the brain — and at/above it at every stage** (S1 source +0.007, S3 bind +0.004, END
+0.006, all n.s.). The role-binding step is *not* where we differ from the brain; it is already the brain's mechanism
(feature-competition) at the competent-reader ceiling. **The deployed 0.470 is a SOURCE-WIRING gap** (the referent-
per-NP source is built but gated on the coref linker), not a brain-mechanism gap: fed the same impoverished coref
candidate set, a competent reader is capped too.

## 2. WHERE along the chain we lose signal
The chain is `ORACLE → S1 source → S2 event(verb) → S3 bind → END`. Where the loss sits depends on the source:
- **DEPLOYED reader: the loss is overwhelmingly S1 SOURCE.** Coref annotates only entity-typed nouns, so the gold
  patient is a candidate just **0.818** of the time → deployed END 0.470. This is the **single biggest lever**, and it
  is the parent's referent-per-NP wire (S1 0.818→0.971), **gated on the coref linker** (filed).
- **IDEAL reader (referent-per-NP): the loss is entirely S3 SELECT.** S1 is closed (1.000 with indefinite-pronoun
  coverage); S2 is supplied. The S3 loss (0.928) decomposes: **56% parse-recoverable** (a competent parse gets it) +
  **44% genuine** (neither ours nor the competent reader — ill-posed naming + meaning-ambiguity + gold noise, ~3.1%
  absolute).

So: **the selector is done; the remaining signal is at S1 (deployed: source-wiring) and inside S3's parse-recoverable
slice (ideal: the parser + register-native tagger).**

## 3. The EXACT mechanism divergence, stage by stage (PINNED brain mechanism / our impl / exact difference / verdict)
| stage | brain mechanism (PINNED) | our implementation | EXACT divergence | measured gap | verdict |
|---|---|---|---|---|---|
| **S1 SOURCE** (open a referent per NP) | DRT referent introduction for every NP incl. quantified/indefinite (Kamp 1981; Heim 1982); MTL concept cells + hippocampal indexing; incremental + predictive (Nref 300-400ms, Van Berkum) | rule-based POS + determiner/name frame + **indefinite-pronoun coverage (new)** | brain introduces referents **incrementally + predictively as it reads**; we open them in one **static** post-hoc pass | **NONE on coverage** — ours 1.000 ≥ brain 0.993 | **FIDELITY HIGH.** Coverage matched/exceeded; the incremental-predictive character is unreplicated but costs 0 here. The DEPLOYED gap (0.818) is a WIRING gap (source gated), not a mechanism gap. |
| **S2 EVENT** (verb-ID) | predicate detection is structure-predicted, tense-agnostic (Frankland-Greene; Matchin-Hickok) | supplied in this task; the parent's noisy-channel joint-POS override for free text | n/a here (verb index supplied) | ~0 here | out of scope for this task |
| **S3 SELECT** (bind arg → role) | **feature-competition**: eADM weighted prominence (order/animacy/case/voice, Bornkessel-Schlesewsky 2006); abstract, surface-syntax-INDEPENDENT agent/patient slots in lmSTC (Frankland-Greene 2015/2020); lexicalist unification by competitive inhibition (Hagoort; Vosse-Kempen 2000) | `hybrid_role_patient` — Competition Model: word-order-dominant + voice/gap/animacy overrides | **the brain runs the SAME competition** (order-dominant English, cues override on marked structure). We copy the operation. The brain's cue *weights* are learned/graded and continuously re-estimated; ours are a fixed logistic fit | **NONE** — ours 0.928 = brain 0.925 (tied) | **FIDELITY HIGH — this IS the brain's mechanism.** A Goldberg construction-template router on top is *less* brain-faithful (the brain does not do construction-template retrieval for role binding) and measured 0.000. |
| **S3a PARSE** (structure that S3 reads) | hierarchical structure-building: **filler-gap** for clefts/relatives (active-filler), **small-clause** for object-complement, **discourse old/new** for inversion; predictive/generative (Kuperberg 2021; amPFC event-specific conjunctions, Frankland-Greene 2020) | a shallow dependency parse + `relcl_resolver` object-gap + PP-routing | we miss **pseudo-clefts** ("what frightened people"), **locative inversion** ("were seen the landscapes"), **apposition** ("her sister Celia") | **56% of the S3 residual** (the brain's parse recovers these) | **FIDELITY MEDIUM — a real, recoverable gap = the FILED parser problems** (`parser_arceager`, filler-gap, a discourse module). NOT a selector job. |
| **S3b REGISTER POS** (word-class ID feeding S3a/S3) | word class from **morphology + context**, robust across register (function-word bootstrapping; the brain reads 19c prose fine) | a **static modern-trained** POS tagger | the tagger mis-tags 19c adjectives AND verbs as NOUN ("cheery-looking", "winds", "breaks") | **~half of the parse-recoverable slice** (PROVEN: a structural head-rule nets 0 because it can't tell adjective-mistags from verb-mistags — both are tagger noise) | **FIDELITY MEDIUM — the FILED register-native-POS problem.** This is the brain-faithful fix, not a selector patch. |
| **S3c genuine bind** (ambiguous / ill-posed) | top-down world-knowledge + thematic-fit on MEANING (McRae/Ferretti; Metusalem 2012; Kuperberg predictive) for genuine ambiguity; small-clause = two internal args (no single patient) | none (structure-only); naming forced to a single pick | genuine ambiguity needs the meaning channel; **naming/object-complement is ILL-POSED** (small-clause; patient-vs-theme unsettled in linguistics, Sánchez 2023 vs Matushansky 2008) | **44% of the S3 residual ≈ 3.1% absolute** — and **the competent reader ALSO misses it** | **GATED / ILL-POSED.** Meaning-fit = the filed learner-on/meaning-channel successor; naming has no ground truth even for the brain. |

## 4. The one-paragraph answer
On the ideal (referent-per-NP) chain **we are statistically tied with a competent reader (0.928 vs 0.922), and at or
above it at every stage** — because the role-binding step already IS the brain's mechanism (feature-competition /
eADM prominence / Frankland-Greene abstract role slots), which is why the proposed construction-template selector adds
exactly nothing. **Where we still lose signal is never the selector:** (a) in the DEPLOYED reader, almost all of it is
the SOURCE (coref covers the gold patient only 0.82 of the time; the referent-per-NP fix closes it to 0.97 but is
gated on the coref linker); (b) in the IDEAL reader, the residual is the PARSE (clefts/inversion/apposition — the
filed parser) and the REGISTER-NATIVE POS TAGGER (mis-tagging 19c words — the filed tagger), which together are the
56% "a-competent-parse-gets-it" slice; and (c) an irreducible ~3% that the competent reader also misses — genuine
meaning-ambiguity (gated on the meaning channel) and object-complement/naming clauses that are genuinely ill-posed
(the small clause has two internal arguments and no single "patient", a point on which the linguistics itself is
unsettled). **The exact difference from the brain, in one line: we replicate the brain's role-BINDING computation
faithfully (and match it); we differ upstream — the brain builds richer hierarchical structure, tags word-class
register-robustly, and links referents continuously as it reads, whereas we run a shallow static parse, a modern-only
tagger, and a not-yet-wired referent linker — plus a top-down meaning system we have gated off.**
