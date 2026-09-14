---
problem: a_name_is_a_word_that_picks_out_an_individual_the_entity_layer_must_feed_back_a_prior_to_the_category_organ
status: PARTIAL
bar: "PROPN<->NOUN confusions on repeated mentions down CI-separated with overall accuracy not down, twin at the floor, the board's common_noun_coref not down (report if up), knowledge as counts with an online observe path -- OR a numbered located negative (e.g. the first-mention share) naming the missing input."
result: "PENDING"
floor: "PENDING"
controls: "PENDING"
files_changed: "PENDING"
reverify: "PENDING"
---

# The entity layer's belief that a string picks out an INDIVIDUAL, fed back into the category competition as one count-based log-prior: built, twin-validated, no-regress -- and the bar's population on UD-EWT test is 288 items, which is an INSTRUMENT fact I fixed by moving to GUM, where the same population is 3,754

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box, counts only, no external tool at inference, no gold coreference read anywhere. **No `hdlab/` file was written** -- the change is proposed as `lexical_categories_entity_prior_patch.diff` (verified against the measured arm to a max posterior difference of **0.0**).

---

## 1. THE OPENING MOVE: how does the brain decide that "the MSM" is a name and "the CEO" is not?

**It does not decide it from the form, because the form is identical.** Both are a capitalised/ACRO string after "the". The pri-99 solver closed that arithmetic: across 25 measured arms spanning six form cues, PROPN<->NOUN never fell below 144 of 163, and 58 of the residual are *structurally* form-free.

**STRUCTURE.** A proper name is a word that refers to an INDIVIDUAL (Kripke 1980, rigid designation). Proper-name retrieval runs through a referent route distinct from the common-noun semantic route -- the left temporal pole / anterior temporal lobe (Semenza 2006/2009 on proper-name anomia; Damasio et al. 1996 lesion evidence; Gorno-Tempini et al. 1998) -- which sits ABOVE the posterior-temporal word-form/category level. The discourse model of who-is-who is a set of FILE CARDS (Heim 1982, file-change semantics), re-accessed by content-addressable retrieval (Lewis & Vasishth 2005). **The substrate already has that organ: `hdlab/online_entity_cluster.py`.**

**COMPUTATION.** Comprehension is predictive and the prediction runs TOP-DOWN: the higher level's current belief re-enters the lower level's competition as a PRIOR (Rao & Ballard 1999 predictive coding; Kuperberg & Jaeger 2016, graded belief propagated down). So:

```
log P(c | word, context)  +=  KAPPA * log P(E | c)
```

one additive term, exactly the shape of every other cue in `hdlab/lexical_categories.py`, where `E` is the entity layer's symbol for this string's discourse history. **No new organ was minted** -- this is the FEEDBACK arm of the category organ (ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS), sourced from the entity layer's own individuation.

**AND IT IS A NEXT-MENTION PRIOR, NEVER A SAME-TOKEN LOOP** (the brief's constraint, and the brain's -- a prediction is formed before the input arrives). The file cards are written strictly IN ORDER and the belief about word *t* reads only words 0..*t*-1 of the passage. Asserted by witness W2.

**The five file-card symbols, each pinned:**

| symbol | what the entity layer is saying | the pin |
|---|---|---|
| `e_first` | no earlier mention in this passage -- **the referent system has NO belief** | (see §5: this is where I found the defect) |
| `e_rep_bare` | mentioned before, never under a determiner -- a bare recurring referring expression | Heim file card re-access |
| `e_rep_def` | mentioned before, only definite/possessive ("the MSM", "the Gateses") | names DO take determiners -- the counts decide, not a rule |
| `e_rep_indef` | mentioned before under an indefinite/quantifier -- a KIND | Katz, Baker & Macnamara 1974: "this is A dax" names a kind |
| `e_rep_plural` | a singular/plural variant occurs in the passage -- a KIND | Gelman & Taylor 1984: individuals do not pluralise |

**Measured in the supply's novel stratum, before anything was built** (type count <= 2): P(PROPN)/P(NOUN) = 0.216/0.365 at `e_first`, 0.385/0.298 at `e_rep_bare`, 0.256/0.587 at `e_rep_def`, 0.018/0.860 at `e_rep_plural`. **The PROPN:NOUN odds move 2.2x from `e_first` to `e_rep_bare` and collapse 34x at `e_rep_plural`** -- a real, count-based, gold-free discourse signal.

**Why the key is the surface string, and it is not a shortcut.** `online_entity_cluster` itself resolves NAMES by their string through the aliaser and sends only common nouns through cue-based retrieval; and `notes/BRAIN_MATH_REFERENCE.md` (entity-tokens row) records that gold-free Heim-file clustering is at PARITY with head-string buckets (0.5235 = 0.5235). Using the full resolver here would also be circular -- it needs a parse, and the parse reads these categories.

---

## 2. THE SIGNAL-LOSS TRACE, RUNG BY RUNG (the status probe, with counts)

*The signal the end read needs: "is this string being used to pick out an individual?"*

| rung | what it produces | what the next rung reads | **what is LOST** | BF status *for this signal* |
|---|---|---|---|---|
| **0. passage segmentation** | the document | the reader | **UD-EWT TEST "documents" are 79-token web snippets** (316 docs / 25,094 tokens), so only **353 of 1,882 unseen tokens (18.8%)** have any earlier mention. GUM's real documents average 993 tokens and the figure is **57.1%**. The instrument was hiding two thirds of the ability | **NOT BF as an instrument** -- fixed here by adding GUM |
| **1. the discourse register** (built here) | a 5-symbol Heim file card per string type | the category emission slot | keyed by SURFACE STRING: a coreferent with a different string ("Souter" / "the justice") hands down nothing | BF computation, MODEL for the key (and at parity with the substrate's own resolver) |
| **2. category organ, unknown-word read** | a graded posterior over 17 categories | argmax -> the tag | **100 of the 154 PROPN<->NOUN confusions are DOCUMENT SINGLETONS** -- the string occurs exactly once in the whole document, so no discourse-history route can ever reach them | BF |
| **3. hand-off to heads** | argmax tag | `attachment_arm` | the graded posterior is discarded (pri-99 measured this at +0.0011 UAS -- small) | NOT BF at the hand-off, small |
| **4. hand-off to the ENTITY LAYER** | **nothing at all** | `coref.name_content_tokens` = capitalisation + a 60-word stop list | **THE WHOLE SIGNAL.** See below | **NOT BF -- the hand-off does not exist** |

### 2b. THE BIGGEST LOSS IS A HAND-OFF THAT IS NOT THERE, AND IT IS ONE RUNG DOWNSTREAM OF ME

**Eight live organs** (`online_entity_cluster`, `entity_resolver`, `commonnoun_binder`, `crosstype_live_adapter`, `coref_distractor_suppress`, `event_centrality_coref`, `gender_organ`, `scene_segment`) decide NAME vs COMMON through `hdlab/coref.name_content_tokens`, a capitalisation rule. **`hdlab/coref.py`, `hdlab/entity_resolver.py` and `hdlab/lexical_utils.py` contain the strings `upos` and `PROPN` ZERO times** (enumerated, not searched). The category organ's PROPN belief reaches the board's coref dimensions through NOTHING.

**Scored against the same gold PROPN, on the full UD-EWT test (25,094 tokens):**

| the name detector | precision | recall | **F1** | false "names" |
|---|---|---|---|---|
| `coref.name_content_tokens` -- **what the entity layer actually uses** | 0.564 | 0.830 | **0.672** | **1,331** |
| the category organ's PROPN argmax -- **what is sitting one module away, unread** | 0.871 | 0.856 | **0.864** | **263** |

**+0.192 F1 and 1,068 fewer spurious name files, already computed, for the price of a wire.** This is the single largest number in this investigation, it explains why pri-99's PROPN gains were board-neutral, and it predicts mine will be too. It is section-7 "report, do not edit" in the brief, so I report it with the number and hand it over (§8, lead 1).

**So the brief's premise needs one correction, stated plainly: it is not that the dependency runs both ways and one direction is wired. NEITHER direction is wired.** I built the feedback direction; the forward direction is a separate, larger, and cheaper win.

---

## 3. THE POPULATION ARITHMETIC, COUNTED BEFORE ANYTHING WAS BUILT (checklist item 4)

`--population`, `data/exp_entity_to_category_prior_v1/metrics_population.json`:

| | count | share of the 154 |
|---|---|---|
| PROPN<->NOUN confusions on unseen words (the live organ, read document by document) | **154** | |
| ... on a **repeated mention** (the forward prior can act) | **35** | 22.7% |
| ... on a **first mention** | 119 | 77.3% |
| &nbsp;&nbsp; of which the string **recurs later** (a RE-READING pass could reach it) | 19 | 12.3% |
| &nbsp;&nbsp; of which the string is a **document singleton** | **100** | **64.9%** |

**The arithmetic ceiling of the forward prior on this population is 35 of 154; of any string-history route, including a second reading pass, 54 of 154.** That is the bound the brief asked for, and it is why the bar is scoped to repeated mentions.

**And that bound is a fact about the RULER, not about the ability.** UD-EWT test's snippets make repetition rare. GUM V12 (modern, multi-genre, held out from this organ's supply, the board's own corpus) has 275 documents averaging 993 tokens:

| | UD-EWT test | GUM (137-doc stride-2 slice) |
|---|---|---|
| documents / tokens | 316 / 25,094 | 137 / 136,xxx |
| unseen tokens that are repeat mentions | 18.8% | **57.1%** |
| the bar's population (repeat-mention unseen, gold PROPN or NOUN) | **288** (176 types) | **3,754** (937 types) |
| its confusions at the floor | 35 | 293 |
| the organ's accuracy there | 0.7812 | **0.5666** -- against 0.8871 on first mentions |

**On a real document the repeat-mention population is 46% of the unseen PROPN/NOUN tokens and it is the half the organ is WORST at.** The lever is aimed at the weak half; the brief's instrument could not show that.

---

## 4. WHAT WAS BUILT, AND WHAT EACH LEVER WAS WORTH -- UD-EWT TEST (the brief's population)

Full UD-EWT test read DOCUMENT BY DOCUMENT, paired bootstrap over **documents** (the discourse unit) and over sentences, 2,000 resamples, floor recomputed in place. `F_live` is the LIVE organ and reproduces it to a max posterior difference of **0.00e+00, 0/3,106 tag differences** (witness W4).

| arm | overall | unseen | PROPN<->NOUN | REP conf (of 35) | Δ REP acc (CI, doc) | Δ unseen (CI, doc) |
|---|---|---|---|---|---|---|
| **F_live (FLOOR)** | 0.9312 | 0.8002 | **154** (90+64) | 35 | -- | -- |
| E2_k05 (kappa 0.5) | 0.9313 | 0.8029 | 151 | 33 | +0.0035 [-0.0121, +0.0211] | +0.0027 [-0.0022, +0.0079] |
| **E3_k1 (kappa 1)** | **0.9315** | 0.8039 | **148** | **29** | +0.0139 [-0.0097, +0.0415] | +0.0037 [-0.0025, +0.0102] |
| E4_k2 | 0.9311 | 0.7981 | 156 | 33 | +0.0069 | -0.0021 |
| E5_k4 | 0.9301 | 0.7848 | 161 | 31 | -0.0208 | **-0.0154 [-0.0274, -0.0043] SEPARATED NEGATIVE** |
| E6_rich_k1 (topical alphabet) | 0.9313 | 0.8013 | 152 | 33 | +0.0000 | +0.0011 |
| E7_rich_k2 | 0.9312 | 0.7997 | 149 | **26** | +0.0208 [-0.0104, +0.0565] | -0.0005 |
| N2_nk1 (novel-form table) | 0.9313 | 0.8023 | 151 | 30 | | |
| N5_nk1_rich | 0.9311 | 0.8007 | 149 | 28 | | |
| R2_d3 / R3_d10 / R4_d30 (document register) | 0.9313 / 0.9313 / 0.9314 | 0.7991 / 0.7991 / 0.8013 | 156 / 158 / 151 | 35 / 35 / 32 | | |
| **A2_k1_w5 (kappa 1 + ACT-R recency w=5) -- RECOMMENDED** | **0.9315** | **0.8045** | **148** (88+60) | **29** | **+0.0174 [-0.0070, +0.0466]** | **+0.0043 [-0.0021, +0.0108]** |
| A3_k1_w10 | 0.9315 | 0.8039 | 148 | 29 | +0.0174 | +0.0037 |
| A5_k1_w5_rich | 0.9313 | 0.8018 | 153 | 34 | +0.0000 | +0.0016 |
| **TWIN 1 -- shuffled chains (kappa 2)** | 0.9311 | 0.7970 | 158 | 31 | +0.0069 n.s. | -0.0032 n.s. |
| **TWIN 2 -- permuted table (kappa 2)** | 0.9260 | **0.7333** | **239** | 47 | -0.0556 | **-0.0670 [-0.0874, -0.0475] CI-SEP BELOW THE FLOOR** |

**Every arm's direction is right and NO arm is CI-separated on the bar's population, because that population is 288 items spread over 316 documents.** The half-width of the repeat-mention CI is ~0.027 -- larger than any effect this lever can produce there. That is not a hedge, it is the reason §3 exists.

**Controls that DO separate:** the permuted-table twin collapses to unseen 0.7333, **-0.0670 CI-separated BELOW the floor**, with PROPN<->NOUN 239 against 154 -- the table carries real information, and a table with identical marginals and a scrambled symbol->category map is much worse than no table at all. The over-weighted arm (kappa 4) is CI-separated NEGATIVE, which locates kappa as an operating point rather than a switch.

**NO-REGRESS, HEADS RUNG** (`--heads A2_k1_w5`, full UD-EWT test, 24,664 arcs, the organ's OWN tags): UAS **0.6278 -> 0.6281** (+0.0003), tag agreement **0.9313 -> 0.9316** (+0.0003). No regression on the hand-off; per-relation, `advcl` 0.357 -> 0.366 and `nmod` 0.482 -> 0.484, nothing down more than 0.001.

---

## 5. GUM -- THE WELL-POWERED MODERN POPULATION, AND THE DEFECT IT EXPOSED

GUM stride-2 (137 documents, 136k tokens), floor recomputed in place: overall 0.8807, unseen 0.5214, PROPN<->NOUN 563 (421+142), REP n=3,754 acc 0.5666 conf 293, FIRST n=4,410 acc 0.8871 conf 270.

PENDING_GUM_TABLE

---

## 6. NEGATIVES, EACH UNDERSTOOD MECHANISTICALLY WITH A NUMBER

**1. The NOVEL-FORM (Baayen productivity) evidence base did NOT beat the whole-vocabulary table** -- N2_nk1 unseen 0.8023 / REP conf 30 against E3_k1's 0.8039 / 29, and on GUM the novel-stratum arm is much worse (§5). *Why, with a number:* the novel stratum holds **13,117 of the 204,578** entity-symbol counts (6.4%), and the alphabet has only 5 symbols, so the whole-vocabulary table is already well estimated where the suffix table was not. More importantly the productivity argument does not transfer: Baayen's hapax stratum matters because what a FREQUENT word's *ending* predicts differs from what a NEW word's ending predicts -- a fact about morphology. **How a string is USED ACROSS A PASSAGE does not depend on how often the reader has met it before**, so the stratification buys sparsity and no signal. I predicted this arm would win (the two tables disagree in SIGN on `e_rep_def`: +0.43 nats toward PROPN on the whole vocabulary, -0.31 toward NOUN on the novel stratum) and it lost; the sign disagreement is real and is estimation noise on 121 novel `e_rep_def` observations.

**2. The DOCUMENT REGISTER (arm B) is null-to-negative on UD-EWT test** -- R2_d3 PROPN<->NOUN 156, R3_d10 158, R4_d30 151, against the floor's 154. *Why:* the mixture weight is `a = n_d/(n_d + theta)` and a 79-token snippet never accumulates enough `n_d` for `a` to matter; where it does fire it fires on 2-3 observations. **This arm cannot be judged on UD-EWT test at all** -- it is designed for the passage-level statistics of a real document, which is why it is measured on GUM in §5.

**2b. AND ON GUM THE DOCUMENT REGISTER IS NOT MERELY NULL, IT IS NEGATIVE -- which is the more interesting result.** R4_d30 on GUM: PROPN<->NOUN **651 against the floor's 563**, PROPN->NOUN 517 against 421, unseen 0.5164 against 0.5214, repeat-mention accuracy 0.5613 against 0.5666. *Why, mechanistically:* the register accumulates the organ's OWN posteriors, and on GUM the organ is right about an unseen word **52.1%** of the time. A predictive-coding feedback loop is only a gain when the higher level's belief is BETTER than the estimate it displaces; here the passage-local table is built out of the organ's own errors and then given weight `a = n_d/(n_d + theta)` that GROWS with the length of the passage -- so the longer the document, the more confidently it feeds its own mistakes back. On GUM's capitalised, NOUN-heavy technical vocabulary it drags names toward NOUN (+96 PROPN->NOUN). **This is a real fidelity finding about the ARM, not about the corpus: rapid adaptation (Fine et al. 2013) is adaptation to the INPUT distribution, and I implemented adaptation to the OUTPUT distribution. The brain's version needs an error signal the substrate does not have at this rung.** Arm B is withdrawn; the patch ships it behind `ENT_THETA_DOC=None` (off) with this measurement in the module comment.

**3. kappa > 2 is a CI-SEPARATED NEGATIVE** -- E5_k4 unseen -0.0154 CI[-0.0274, -0.0043], overall -0.0010 CI[-0.0019, -0.0002]. *Why:* the top-down prior is one 5-symbol table competing against a 19-symbol form description, a graded suffix ladder and a second-order transition; over-weighting it over-rides better-estimated evidence. **kappa is an operating point, swept, never adopted** -- exactly as `UNK_PRIOR_GAMMA` turned out to be.

**4. The acronym -> expansion bind is DEAD BY COUNT, not by argument.** The obvious entity-layer route to the acronym slice pri-99 called form-free (`AMS` / `MSM` / `EWS` / `PPA` / `EPMI` / `CDWR`) is to bind the abbreviation to an earlier capitalised expansion with the same initials, the way a reader learns one. **Measured: 3 of 119 unseen ALL-CAPS/acronym tokens in UD-EWT test have an earlier same-initials capitalised run in their document, and all three are the same string (`GPSA`).** The antecedent is simply not in the text. Not built.

**5. The shuffled-chains twin at kappa 2 is a WEAK control and I am reporting it as such.** It scores unseen 0.7970 against that arm's 0.7981 -- a 0.0011 gap, n.s. That is because I twinned E4_k2, an arm that is itself ~null on unseen accuracy; a twin of a null arm proves nothing. The permuted-table twin on the same arm collapses (0.7333, CI-separated below the floor), so the control that matters did fire, and the winning arm's own twins are reported in §5. **Recorded because a control that excludes nothing is not a control** -- the same mistake pri-99 caught in itself.

---

## 7. WHAT STRATEGY SHOULD LAND, AND WHAT TO CHECK

PENDING_LANDING

---

## 8. ALTERNATE PATHS, ADJACENT COMPONENTS, NEXT STEPS

### LEAD 1 -- THE FORWARD WIRE. The highest-value thing this work found, and it is not mine to land.
*Structure/computation:* the same top-down/bottom-up loop, in the other direction -- the word-form/category level handing its GRADED posterior UP to the referent system, instead of the referent system re-deriving name-hood from orthography. *The number:* `coref.name_content_tokens` scores **F1 0.672** (P 0.564 / R 0.830, **1,331 false "names"**) against the category organ's **F1 0.864** (P 0.871 / R 0.856, 263 false names) on the same 25,094 tokens. *What it would take:* `name_content_tokens` (or, better, a new graded `name_belief(span, upos_posterior)` in `hdlab/coref.py`) consults the frontend's category posterior for each span token, with capitalisation retained as one cue among several rather than as the decision. Eight organs consume it, so it must land top-down with per-consumer witnesses. *Why not now:* the brief scopes the name bridge to "report, do not edit" (section 7), it is a different organ from my patch's, and pri-94 holds a concurrent diff nearby. **This is the reason the board's `common_noun_coref` and `coref` dimensions did not move for pri-99 and will not move for me: the signal has no wire to travel on.**

### LEAD 2 -- ACCRUE THE ENTITY TABLE FROM REAL PASSAGES, NOT FROM WEB SNIPPETS (the plastic path made load-bearing).
*Structure/computation:* the organ is plastic; `observe_document` grows `entc` from comprehension outcomes with no gold. *The number that makes it necessary:* in the UD-EWT TRAIN supply a repeated unseen string is usually a NAME (**65% PROPN** on the test snippets), and in a real document it is usually a domain term (**63% NOUN** on GUM) -- the table is learning the snippet's statistics, not the reader's. *What it would take:* nothing new -- read real documents and call `observe_document(words, own_settled_categories)`. I built `online_adapt()` in the cell for exactly this (adapt on the ODD GUM documents, score the EVEN ones, disjoint, no gold). *Why it is filed rather than headlined:* see §5/§9.

### LEAD 3 -- THE RE-READING PASS (a second look at the passage).
*Structure:* regressive eye movements and re-reading are the reader's ordinary repair mechanism (Rayner 1998); the substrate's own "organs take data in order" rule is about the FIRST pass, not about forbidding a second. *The number:* **19 of the 154 confusions are first mentions of a string that recurs later** -- a reader who re-reads has the evidence and the incremental one does not. Combined with the 35 repeat-mention confusions this bounds every string-history route at **54 of 154 (35.1%)**. *What it would take:* a second `posterior()` pass per document with the register already full; cost is one extra pass. *Why not now:* it needs a decision from strategy about whether a second pass is in-scope for the live reader, and it changes the reader's contract, not just this organ's.

### LEAD 4 -- A CROSS-STRING REGISTER KEY (the "or a coreferent of it" clause).
*Structure:* Heim file cards are keyed by REFERENT, not by string; the aliaser already merges name variants. *Why it is small today:* `BRAIN_MATH_REFERENCE` records gold-free Heim clustering at PARITY with head-string buckets (0.5235 = 0.5235), and the full resolver needs a parse that reads these very categories. *What it would take:* the coref two-half problem, which owns this. **Do not build it here** -- it is circular at this rung.

### ADJACENT COMPONENTS, evaluated (the brief's item 7)
- **`hdlab/coref.name_content_tokens` -- NOT BF for this job** (a capitalisation rule with a 60-word stop list standing in for a referent decision), F1 0.672, and it is the sole name/common gate for 8 organs. **The highest-leverage BF upgrade adjacent to this brief.**
- **`hdlab/online_entity_cluster` -- BF_SPIRIT and correctly built**, but its NAME branch inherits `name_content_tokens`'s errors wholesale; its measured parity with head-string buckets is a symptom of that, not of the retrieval maths.
- **`hdlab/induced_categories` (v2) -- BF**, still silent on the majority of unseen tokens (pri-99: 1,333 of 1,882); unchanged by this work.
- **The hand-off to heads -- still a hard argmax**; measured again here at +0.0003 UAS from a better organ, consistent with pri-99's correction that this is small.

### CONSUMED INPUTS / FLAGGED WALLS (for `CROSS_SOLUTION_IMPROVEMENT_MAP.md`)
**CONSUMES:** the UD-EWT train tag column as offline supply; `hdlab/lexical_categories` (all of it); `hdlab/induced_categories` v2; the `# newdoc` passage segmentation of the gold corpora. **FLAGS AS WALLS:** (a) `coref.name_content_tokens` -- the missing forward wire; (b) the offline supply's DOCUMENT STRUCTURE (web snippets, not passages); (c) the labelled acquisition source, unchanged. **DOWNSTREAM CONSUMERS TOUCHED:** `attachment_arm` (measured, no regress); the board's coref dimensions (predicted neutral, and §2b says why).

## KEY REALIZATIONS

- **The population that bounds a lever can be a fact about the RULER.** The brief's bar is scoped to repeated mentions, and on UD-EWT test that is 288 items with 35 errors -- an effect of any plausible size is inside the noise there. The same ability measured on GUM has **3,754 items and 293 errors**, because GUM's documents are documents and UD-EWT test's are 79-token snippets. I nearly wrote "the lever is bounded at 22.7% of the confusions" as a finding about names; it is a finding about the corpus. **Count the population before you build, then ask whether the population is the ability.**
- **A top-down prediction must be SILENT where the higher level has no belief.** The first version sent `kappa * log P(e_first | c)` on every first-mention unseen word -- 1,555 of 1,882 tokens -- which is a category-marginal-shaped term perturbing a competition it knows nothing about. On GUM that showed up as repeat-mention confusions falling while first-mention confusions ROSE. This is the same defect `UNK_PRIOR_GAMMA` exists to remove, one rung up. **The absence of evidence is not a piece of evidence to be weighted.**
- **"Confusions down" and "accuracy up" are different quantities and one of them is gameable.** The novel-stratum arm cut GUM repeat-mention PROPN<->NOUN confusions by 39% while dropping accuracy on that very population by 0.097 -- the errors moved into other categories. Only measuring both caught it. The bar names the confusion; the honest reading needs the accuracy beside it.
- **Enumerate the consumers instead of assuming the wire exists.** The brief says the dependency runs both ways and one direction is wired. Grepping the three files that own the name decision returned **zero** occurrences of `upos` or `PROPN`. Neither direction was wired, and the unwired one is worth +0.192 F1.
- **The organ's own docstring told me where to put the term and what shape it takes.** `log P(E | c)` is a LIKELIHOOD, in the emission slot, next to `log_detc` and `log_rightc`; building it as `log P(c | E)` would have re-applied the category prior a third time. pri-99 paid for that lesson; reading its SOLVED.md in full is why I did not.

## GAPS -- steps not performed, and not worked around

1. **The APPLY-THEN-BYTE-COMPARE test of the diff was a DENIED tool call and was not re-run in any form.** The denial, verbatim: *"Permission to use Bash with command SCR=... rm -rf "$SCR/applytest" && mkdir -p "$SCR/applytest/hdlab" && cp /c/AI/hd-instrument/hdlab/lexical_categories.py "$SCR/applytest/hdlab/" && cd "$SCR/applytest" && git init -q . && git apply "...lexical_categories_entity_prior_patch.diff" && cmp ... && echo "APPLY-THEN-BYTE-COMPARE: IDENTICAL" has been denied."* Per the operating rules I did not perform that check another way. **What IS established instead:** `git apply --check` is CLEAN, and the patched module itself is verified against the measured arm on five witnesses (R1-R5 above) including `max posterior difference 0.000e+00`. **Please byte-compare after applying** -- this is the same gap pri-99 recorded, for the same reason.
2. **The BOARD was not run** (`exp_situation_model_qa_modern_v1.py --run`). It needs the patched module on the live path, which is strategy's step. **I predict board-NEUTRAL on `common_noun_coref` (0.5671) and `coref` (0.4681), and I am recording the prediction in advance with its mechanism: §2b shows the entity layer never reads this organ's PROPN belief at all, so no change to that belief can reach those dimensions.** If the board DOES move, that prediction is wrong and §2b should be re-checked first.
3. **The GENTLE OOD companion (26 documents, 629 bar items) was not run.** It is wired (`--corpus gentle`) and costs one pass; I ran out of machine time with four concurrent GUM jobs. It is the first thing to run on re-open, because leads 2 and 5 turn on how corpus-specific the entity table is and GENTLE is the cheap check.
4. **The online-adaptation arm (`online_adapt`, lead 2) is BUILT and SELF-TESTED but was not run at full scale** for the same reason. The code path is exercised by W6 (`observe_document` grows the counts and re-derives the table); what is missing is the measured adapt-on-odd / score-on-even GUM number.
