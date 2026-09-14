---
problem: a_name_is_a_word_that_picks_out_an_individual_the_entity_layer_must_feed_back_a_prior_to_the_category_organ
status: PARTIAL
bar: "PROPN<->NOUN confusions on repeated mentions down CI-separated with overall accuracy not down, twin at the floor, the board's common_noun_coref not down (report if up), knowledge as counts with an online observe path -- OR a numbered located negative (e.g. the first-mention share) naming the missing input."
result: "TWO POPULATIONS, both read DOCUMENT BY DOCUMENT, floor recomputed in place, paired bootstrap over DOCUMENTS (the discourse unit) with 2,000 resamples. (1) THE WELL-POWERED MODERN POPULATION -- GUM V12 stride-2, 138 documents / 7,584 sentences / 136,855 tokens, entirely held out from the organ's supply; the bar's population there is 3,754 repeat-mention unseen tokens with gold PROPN or NOUN (against 288 on UD-EWT test). THE ARM (S2_k2_w5 = the entity-referent prior, kappa 2, ACT-R recency window 5, SILENT where the discourse model has no belief): repeat-mention accuracy 0.5666 -> 0.5767 and its PROPN<->NOUN confusions 293 -> 245 (-16.4%); all-unseen PROPN<->NOUN 563 -> 516 (-8.3%); unseen accuracy 0.5214 -> 0.5254; OVERALL accuracy 0.8807 -> 0.8819; FIRST-mention accuracy EXACTLY unchanged at 0.8871. PAIRED BOOTSTRAP OVER DOCUMENTS, 2,000 resamples: repeat-mention accuracy +0.0101 CI[+0.0015,+0.0192] CI-SEPARATED (half-width 0.0089), unseen accuracy +0.0041 CI[+0.0015,+0.0071] CI-SEPARATED, OVERALL accuracy +0.0012 CI[+0.0006,+0.0018] CI-SEPARATED. Replicated by two sibling arms on the same population (S1_k1_w5 +0.0104 CI[+0.0043,+0.0172]; S3_k2_rich +0.0115 CI[+0.0027,+0.0207]). (2) THE BRIEF'S NAMED POPULATION -- full UD-EWT TEST, 25,094 tokens / 2,077 sentences / 316 documents, 1,882 unseen: PROPN<->NOUN 154 -> 148 (S1_k1_w5), repeat-mention confusions 35 -> 29, repeat-mention accuracy +0.0174 CI[-0.0070,+0.0466] NOT separated, unseen 0.8002 -> 0.8023, overall 0.9312 -> 0.9313, first-mention accuracy exactly the floor's 0.8188. It does not separate there and that is a POPULATION FACT, counted before building: UD-EWT test's documents are 79-token web snippets, so the bar's population is 288 items with 35 errors and a CI half-width of 0.027."
floor: "F_live = the LIVE organ (LexicalCategories.load() on the live asset: lag 2, order 2, shape emission, rare-word mixing, induced-cluster cue, the pri-99 unknown-word cues) read document by document with the prior at kappa 0. BYTE-IDENTICAL to the unmodified class -- max posterior difference 0.00e+00 and 0/3,106 tag differences (self-test W4). UD-EWT test: overall 0.9312, unseen 0.8002, PROPN<->NOUN 154 (90+64), repeat-mention population 288 items / accuracy 0.7812 / 35 confusions. GUM: overall 0.8807, unseen 0.5214, PROPN<->NOUN 563 (421+142), repeat-mention population 3,754 items / accuracy 0.5666 / 293 confusions. No floor was pasted across harnesses; every number is recomputed in place on the item's own population."
controls: "(1) TWIN A -- SHUFFLED CHAINS (the brief's own twin): each token is given the register symbol of a RANDOM other token of the same document, so the document's symbol distribution is preserved exactly and only the token<->history pairing is destroyed. It lands AT THE FLOOR on both populations: UD-EWT test repeat-mention delta +0.0000 CI[-0.0270,+0.0255] (accuracy 0.7812 against the floor's 0.7812); GUM repeat-mention +0.0013 CI[-0.0062,+0.0091] n.s. and unseen delta +0.0000 CI[-0.0018,+0.0020] -- EXACTLY the floor. (2) TWIN B -- PERMUTED TABLE (a DERANGEMENT of the symbol->category map; identical alphabet, identical row marginals, identical smoothing): on the RECOMMENDED arm, GUM repeat-mention -0.0202 CI[-0.0344,-0.0081], unseen -0.0093 CI[-0.0136,-0.0058] and overall -0.0012 CI[-0.0016,-0.0008], ALL THREE CI-SEPARATED BELOW THE FLOOR, PROPN<->NOUN 640 against 563; UD-EWT test unseen -0.0101 CI[-0.0198,-0.0005] CI-separated below, PROPN<->NOUN 169 against 154. (1b) OUT-OF-DOMAIN, AND IT IS A NEGATIVE I AM NOT HIDING: on GENTLE (26 technical/dictionary/proof documents) the recommended arm is CI-SEPARATED NEGATIVE -- repeat-mention -0.0620 CI[-0.1115,-0.0090], unseen -0.0196 CI[-0.0372,-0.0050], overall -0.0031 CI[-0.0058,-0.0008] -- because GENTLE's dominant confusion direction is INVERTED (226 NOUN->PROPN against 58) and the table was accrued from a snippet corpus where repetition means NAME. See SOLVED.md section 5b. (3) FLOOR IDENTITY: kappa 0 reproduces the live class to 0.00e+00. (4) NO-REGRESS, HEADS RUNG under the organ's OWN tags (full UD-EWT test, 24,664 arcs): UAS 0.6278 -> 0.6281, tag agreement 0.9313 -> 0.9316, no relation down by more than 0.001. (5) NO-REGRESS, FIRST MENTIONS: first-mention accuracy is exactly the floor's (0.8188 EWT / 0.8871 GUM) -- the e_first gate is what makes that true, and the ungated arms show what it costs (+22 GUM first-mention confusions). (6) SWEEPS, 30 arms across two corpora: kappa 0.25/0.5/1/2/4 (kappa 4 is CI-SEPARATED NEGATIVE), recency window 2/5/10, novel-stratum vs whole-vocabulary evidence base, register theta 1/3/10/30/100, rare-word gate 2/5/20, topical alphabet, e_first gate on/off. (7) CROSS-CORPUS: every load-bearing claim measured on BOTH UD-EWT test and modern multi-genre GUM. (8) ONLINE PATH: observe_document grows the counts and re-derives log P(E|c) (witness W6). (9) PATCH EQUIVALENCE: the proposed diff, driven passage by passage, reproduces the measured arm to max posterior difference 0.000e+00 on 5,272 tokens, and is INERT (0.000e+00) for any consumer that does not call new_document(). (11) PHASE 7 -- an ORACLE-TEACHER probe (gold-taught online adaptation, never a shippable arm) to separate a broken mechanism from a bad teacher; a THIRD corpus for every phase-7 lever; and the forward-wire harness validated by reproducing the board's published coref 0.4681 / common_noun 0.5671 exactly under its gold arm. (10) A REFUTED ARM, properly: the passage register is CI-SEPARATED NEGATIVE (repeat-mention -0.0053 CI[-0.0104,-0.0008], unseen -0.0050 CI[-0.0087,-0.0019]) and ships off."
files_changed: "notes/problems/<slug>/coref_forward_wire_patch.diff (PHASE 7: the FORWARD WIRE -- hdlab/coref.name_content_tokens reads the category organ instead of capitalisation; git apply --check CLEAN, 0/5,807 span regressions when no categories are supplied); experiments/exp_entity_to_category_prior_v1.py (the cell: the Heim discourse register, the entity-referent prior, the passage register, ACT-R recency, the rare-word gate, the e_first gate, both twins, the document- and sentence-level paired bootstraps, --population, --heads, --self-test with 8 witnesses, GUM/GENTLE corpus support, online_adapt with an oracle-teacher probe, count decay, precision- and card-confidence weighting, the repaired passage register, the passage-local entity table, --name-decision and --forward-wire); notes/problems/<slug>/SOLVED.md; notes/problems/<slug>/lexical_categories_entity_prior_patch.diff (PROPOSED, NOT applied -- strategy lands it per Q111; git apply --check CLEAN); data/hook_state/lexical_categories_entity_counts_w5_candidate.json (4.7 KB candidate counts, written by the cell); data/exp_entity_to_category_prior_v1/*.json (metrics). NO hdlab/ or tools/ file was edited; the live asset was NOT touched."
reverify: ".venv/Scripts/python.exe experiments/exp_entity_to_category_prior_v1.py --self-test    # scaffold-free, 8 witnesses, ~50s; asserts kappa=0 == the live LexicalCategories to 0.0, the strictly-in-order no-same-token-loop property, the Katz/Gelman KIND symbol, the accrued table's odds ordering, and the ONLINE observe_document path.   THEN the headline (writes only to its own metrics file, never into a landed record):  OMP_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=entity_to_category_prior_v1 .venv/Scripts/python.exe experiments/exp_entity_to_category_prior_v1.py --corpus gum --doc-stride 2 --boot 2000 --arms F_live,S2_k2_w5 --twin-of S2_k2_w5 --out-name metrics_reverify.json    # expect floor overall 0.8807 / unseen 0.5214 / PN 563 / REP acc 0.5666 conf 293; arm 0.8819 / 0.5254 / 516 / 0.5767 conf 245; the shuffled-chains twin at the floor and the permuted twin below it. ~40 min.   AND the phase-7 register: --corpus gum --doc-stride 2 --arms O2_reg100_off (expect repeat-mention +0.0037 CI[+0.0008,+0.0073] CI-separated) and --corpus gentle --arms F_live,O2_reg100_off (expect +0.0223 CI[+0.0079,+0.0361] CI-separated)."
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

| | UD-EWT test | GUM (stride-2 slice) |
|---|---|---|
| documents / tokens | 316 / 25,094 | 138 / 136,855 |
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
| **S1_k1_w5** (kappa 1 + recency + SILENT at `e_first`) | 0.9313 | 0.8023 | **148** (83+65) | **29** | +0.0174 | +0.0021 |
| **S2_k2_w5** (kappa 2 + recency + silent) -- the arm recommended on GUM | 0.9312 | 0.8002 | 150 (80+70) | 31 | +0.0070 | +0.0000 |
| S4_k4_w5 (kappa 4 + silent) | 0.9306 | 0.7928 | **146** (76+70) | **27** | -0.0382 | -0.0074 |
| **TWIN 1 of S2 -- shuffled chains** | 0.9312 | 0.7997 | 153 | 34 | **+0.0000 [-0.0270, +0.0255] -- EXACTLY THE FLOOR** | -0.0005 n.s. |
| **TWIN 2 of S2 -- permuted table** | 0.9304 | 0.7901 | 169 (110+59) | 49 | -0.0486 | **-0.0101 [-0.0198, -0.0005] CI-SEP BELOW THE FLOOR** |
| TWIN 1 of E4_k2 -- shuffled chains | 0.9311 | 0.7970 | 158 | 31 | +0.0069 n.s. | -0.0032 n.s. |
| TWIN 2 of E4_k2 -- permuted table | 0.9260 | **0.7333** | **239** | 47 | -0.0556 | **-0.0670 [-0.0874, -0.0475] CI-SEP BELOW THE FLOOR** |

**Every arm's direction is right and NO arm is CI-separated on the bar's population, because that population is 288 items spread over 316 documents.** The half-width of the repeat-mention CI is ~0.027 -- larger than any effect this lever can produce there. That is not a hedge, it is the reason §3 exists, and the same arms DO separate on GUM (§5) where the same population is 3,754 items and the half-width is 0.009.

**The `e_first`-silent arms leave the rest of the corpus EXACTLY alone, which is the point of the gate:** S1/S2/S4 all score first-mention accuracy **0.8188** and first-mention confusions **119** -- the floor's values to the last digit -- because the prior is only read where the entity layer has something to say. S4 (kappa 4) shows the trade at the other end: the fewest confusions of any arm (146) bought with a 0.7-point drop in unseen accuracy. **kappa is an operating point.**

**Controls that DO separate:** the permuted-table twin collapses to unseen 0.7333, **-0.0670 CI-separated BELOW the floor**, with PROPN<->NOUN 239 against 154 -- the table carries real information, and a table with identical marginals and a scrambled symbol->category map is much worse than no table at all. The over-weighted arm (kappa 4) is CI-separated NEGATIVE, which locates kappa as an operating point rather than a switch.

**NO-REGRESS, HEADS RUNG** (`--heads A2_k1_w5`, full UD-EWT test, 24,664 arcs, the organ's OWN tags): UAS **0.6278 -> 0.6281** (+0.0003), tag agreement **0.9313 -> 0.9316** (+0.0003). No regression on the hand-off; per-relation, `advcl` 0.357 -> 0.366 and `nmod` 0.482 -> 0.484, nothing down more than 0.001.

---

## 5. GUM -- THE WELL-POWERED MODERN POPULATION, AND THE DEFECT IT EXPOSED

GUM stride-2 (137 documents, 136k tokens), floor recomputed in place: overall 0.8807, unseen 0.5214, PROPN<->NOUN 563 (421+142), REP n=3,754 acc 0.5666 conf 293, FIRST n=4,410 acc 0.8871 conf 270.

| arm | overall | unseen | PROPN<->NOUN | **REP acc** (n=3,754) | **REP conf** (of 293) | FIRST acc (n=4,410) | FIRST conf (of 270) |
|---|---|---|---|---|---|---|---|
| **F_live (FLOOR)** | 0.8807 | 0.5214 | 563 (421+142) | 0.5666 | 293 | 0.8871 | 270 |
| A2_k1_w5 (kappa 1, recency 5) | 0.8816 | 0.5253 | 550 | 0.5773 | 258 | 0.8830 | **292** |
| E7_rich_k2 (kappa 2, topical) | 0.8818 | 0.5242 | 569 | 0.5781 | 247 | 0.8746 | **322** |
| N6_nk2_rich (novel-form table) | 0.8782 | 0.4980 | 459 | **0.4699** | 178 | 0.8837 | 281 |
| NR5_nk2r_d30 (novel + register) | 0.8770 | 0.4949 | 519 | 0.4736 | 198 | 0.8816 | 321 |
| R4_d30 (register alone) | 0.8809 | 0.5164 | **651** | 0.5613 | 333 | 0.8839 | 318 |
| **S2_k2_w5 -- RECOMMENDED** (kappa 2, recency 5, **silent at `e_first`**) | **0.8819** | **0.5254** | **516** (362+154) | **0.5767** | **245** | **0.8871** | **271** |

### THE DEFECT GUM EXPOSED, AND THE FIX

**Every arm that sent a prior at `e_first` bought repeat-mention confusions and PAID for them in first mentions.** A2_k1_w5: repeat confusions 293 -> 258 (-12%) but first-mention confusions 270 -> **292** (+8%) and first-mention accuracy 0.8871 -> 0.8830. E7_rich_k2 is worse: -46 repeats bought at +52 firsts. On the 288-item UD-EWT population that trade was invisible; on 4,410 first mentions it is not.

**The diagnosis is a fidelity one, not a tuning one.** At `e_first` the referent system **has never met this string in this passage and therefore has no belief**. `log P(e_first | c)` is not the absence of a prior -- it is a category-marginal-shaped vector that perturbs a competition it knows nothing about, applied to 1,555 of 1,882 unseen tokens on UD-EWT and 4,410 of 8,164 on GUM. **This is the same defect `UNK_PRIOR_GAMMA` exists to remove (a prior applied twice penalises the low-prior categories), one rung up.** A top-down prediction must be SILENT where the higher level has no belief.

**Gating it (`ENT_SKIP_FIRST`, arm S2) keeps the whole gain and returns the cost to zero:**

| | floor | A2 (prior at `e_first` too) | **S2 (silent at `e_first`)** |
|---|---|---|---|
| repeat-mention confusions | 293 | 258 (-12.0%) | **245 (-16.4%)** |
| repeat-mention accuracy | 0.5666 | 0.5773 | **0.5767** |
| **first-mention accuracy** | 0.8871 | 0.8830 (**down**) | **0.8871 (EXACTLY the floor)** |
| first-mention confusions | 270 | 292 (**up 22**) | **271 (up 1)** |
| PROPN<->NOUN, all unseen | 563 | 550 | **516 (-8.3%)** |
| unseen accuracy | 0.5214 | 0.5253 | **0.5254** |
| overall accuracy | 0.8807 | 0.8816 | **0.8819** |

### THE CONFIDENCE INTERVALS -- THE BAR SEPARATES ON THIS POPULATION

Paired bootstrap over **documents** (138 of them; the register is per-passage so the document is the correct resampling unit), 2,000 resamples, floor recomputed in place. `denom` is the number of items the rate is computed over.

| arm | **repeat-mention accuracy** (denom 3,754) | unseen accuracy (denom 16,959) | overall accuracy (denom 136,855) |
|---|---|---|---|
| **S2_k2_w5 -- RECOMMENDED** | **+0.0101 CI[+0.0015, +0.0192] SEPARATED** (hw 0.0089) | **+0.0041 CI[+0.0015, +0.0071] SEPARATED** | **+0.0012 CI[+0.0006, +0.0018] SEPARATED** |
| S1_k1_w5 (kappa 1) | **+0.0104 CI[+0.0043, +0.0172] SEPARATED** (hw 0.0065) | **+0.0039 CI[+0.0020, +0.0061] SEPARATED** | **+0.0008 CI[+0.0005, +0.0012] SEPARATED** |
| S3_k2_rich (topical alphabet) | **+0.0115 CI[+0.0027, +0.0207] SEPARATED** | **+0.0047 CI[+0.0022, +0.0078] SEPARATED** | **+0.0013 CI[+0.0007, +0.0019] SEPARATED** |
| E7_rich_k2 (ungated at `e_first`) | **+0.0115 CI[+0.0027, +0.0207] SEPARATED** | **+0.0028 CI[+0.0001, +0.0058] SEPARATED** | **+0.0011 CI[+0.0005, +0.0017] SEPARATED** |
| N2_nk1 (ungated, novel table) | **+0.0128 CI[+0.0040, +0.0224] SEPARATED** | **+0.0025 CI[+0.0005, +0.0050] SEPARATED** | **+0.0008 CI[+0.0003, +0.0013] SEPARATED** |
| **R4_d30 -- the passage register** | **-0.0053 CI[-0.0104, -0.0008] SEPARATED NEGATIVE** | **-0.0050 CI[-0.0087, -0.0019] SEPARATED NEGATIVE** | +0.0001 n.s. |
| A2_k1_w5 (ungated at `e_first`, kappa 1) | **+0.0107 CI[+0.0044, +0.0176] SEPARATED** | **+0.0040 CI[+0.0020, +0.0063] SEPARATED** | **+0.0008 CI[+0.0005, +0.0012] SEPARATED** |
| **TWIN A of S2 -- shuffled chains** | **+0.0013 CI[-0.0062, +0.0091] -- AT THE FLOOR** | **+0.0000 CI[-0.0018, +0.0020] -- EXACTLY THE FLOOR** | +0.0006 |
| **TWIN B of S2 -- permuted table** | **-0.0202 CI[-0.0344, -0.0081] CI-SEP BELOW THE FLOOR** | **-0.0093 CI[-0.0136, -0.0058] CI-SEP BELOW** | **-0.0012 CI[-0.0016, -0.0008] CI-SEP BELOW** |

**The recommended arm's own control set on the well-powered population is complete and it behaves exactly as it must:** the arm CI-separated ABOVE the floor on all three metrics; the shuffled-chains twin -- same symbol distribution, pairing destroyed -- **exactly at the floor** (unseen delta +0.0000); and the permuted-table twin -- same marginals, mapping deranged -- CI-separated BELOW the floor on all three. **The gain is in the pairing of a token with its own discourse history, which is the claim.**

**THE BAR'S CORE CLAUSE IS MET.** For the recommended arm, on the well-powered modern population: **repeat-mention accuracy +0.0101 CI[+0.0015, +0.0192], CI-SEPARATED**, with **overall accuracy not merely unharmed but UP CI-separated (+0.0012 CI[+0.0006, +0.0018])** and first-mention accuracy exactly the floor's. The same arms on the brief's own UD-EWT-test population have the same sign and size and do not separate, for the reason counted in §3.

**The `e_first` gate costs nothing in separation and buys the first-mention population back:** ungated E7 and gated S3 have identical repeat-mention CIs (+0.0115 [+0.0027, +0.0207]) while E7 loses 52 first-mention confusions and S3 loses 1.

**And the passage register is refuted properly, not merely found unhelpful:** CI-separated NEGATIVE on the bar population AND on all unseen words. That is a control firing against my own arm.

---

## 5b. THE ROBUSTNESS LIMIT, MEASURED AND NOT HIDDEN: THE ARM HURTS OUT OF DOMAIN

GENTLE is GUM's OOD companion -- 26 documents of dictionary entries, esports commentary, legal text, medical text, poetry, mathematical proofs and syllabi, 17,799 tokens, bar population 629.

| | floor | S1_k1_w5 | **S2_k2_w5** | TWIN A: shuffled chains | TWIN B: permuted table |
|---|---|---|---|---|---|
| overall | 0.8674 | 0.8661 | **0.8643** | 0.8660 | 0.8687 |
| unseen | 0.6034 | 0.5954 | **0.5838** | 0.5950 | 0.6114 |
| PROPN<->NOUN | 284 (**58** PROPN->NOUN + **226** NOUN->PROPN) | 296 | **310** | 305 | 265 |
| repeat-mention accuracy | 0.6963 | 0.6725 | **0.6343** | 0.6614 | 0.7472 |
| **delta, repeat-mention (CI, doc)** | -- | -0.0238 [-0.0502, +0.0056] n.s. | **-0.0620 [-0.1115, -0.0090] CI-SEPARATED NEGATIVE** | -0.0350 [-0.0595, -0.0113] CI-sep neg | +0.0509 [-0.0431, +0.1493] n.s. |
| delta, unseen (CI, doc) | -- | **-0.0080 [-0.0160, -0.0004] sep neg** | **-0.0196 [-0.0372, -0.0050] sep neg** | -0.0084 sep neg | +0.0080 n.s. |

**The arm is CI-SEPARATED NEGATIVE on GENTLE. I am stating that as flatly as I stated the GUM win.** The reason is visible in the floor's own confusion split: on UD-EWT test the dominant direction is PROPN->NOUN (90 against 64) and on GUM it is PROPN->NOUN (421 against 142); **on GENTLE it INVERTS -- 226 NOUN->PROPN against 58** -- because a dictionary entry, a mathematical proof and a syllabus are full of capitalised technical COMMON nouns that recur. The prior, whose `e_rep_bare` symbol was accrued from UD-EWT web snippets where a repeated unseen string is 65% a name, pushes exactly those toward PROPN and makes the dominant error worse (226 -> 259).

**Three readings of the twins on this population, stated at the precision the numbers support:** (i) the arm is worse than its own SHUFFLED-CHAINS twin (-0.0620 against -0.0350), so the real token<->history pairing is worse than a random one here -- the mapping is mis-specified, not merely uninformative; (ii) the PERMUTED-TABLE twin's point estimate is ABOVE the floor (+0.0509) but **NOT CI-separated** ([-0.0431, +0.1493]), so "the scrambled table wins" is a suggestive point estimate and I am not claiming it; (iii) on GUM the same twins behave correctly -- shuffled chains at the floor (+0.0016 n.s.) and the permuted table CI-separated BELOW it (unseen -0.0209 [-0.0280, -0.0151]).

**This is not a new mechanism, it is negative 1 confirmed at the extreme.** The prior's COMPUTATION is right; its COUNTS are a fact about the corpus the organ was fed, and UD-EWT train's snippets are the least document-like supply available. Reported as a shipped limitation and not discovered after landing: **the recommended default is measured-correct for modern in-genre prose (GUM, CI-separated on three metrics) and is measured-WRONG for GENTLE-like technical text. Do not point this organ at such a corpus without re-measuring, and see LEAD 2 for the fix and its first measured result.**

**The arm is NEGATIVE on GENTLE, and the reason is visible in the floor's own confusion split.** On UD-EWT test the dominant direction is PROPN->NOUN (90 against 64) and on GUM it is PROPN->NOUN (421 against 142); **on GENTLE it INVERTS -- 226 NOUN->PROPN against 58**, because a dictionary entry, a proof and a syllabus are full of capitalised technical COMMON nouns that recur. The prior, whose `e_rep_bare` symbol was accrued from UD-EWT web snippets where a repeated unseen string is 65% a name, pushes exactly those toward PROPN and makes the dominant error worse (226 -> 259).

**This is not a new mechanism, it is negative 1 confirmed at the extreme.** The prior's COMPUTATION is right; its COUNTS are a fact about the corpus the organ was fed, and UD-EWT train's snippets are the least document-like supply available. **The fix is LEAD 2 and the organ already has the machinery: the table is plastic, and `observe_document` accrues it from whatever the reader actually reads.** Reported as a shipped limitation, not discovered after landing: **the recommended default is correct for modern in-genre prose (GUM, CI-separated) and should be re-measured, or adapted online, before this organ is pointed at a corpus whose capitalised vocabulary is mostly common nouns.**

## 6. NEGATIVES, EACH UNDERSTOOD MECHANISTICALLY WITH A NUMBER

**1. The NOVEL-FORM (Baayen productivity) evidence base did NOT beat the whole-vocabulary table** -- N2_nk1 unseen 0.8023 / REP conf 30 against E3_k1's 0.8039 / 29, and on GUM the novel-stratum arm is much worse (§5). *Why, with a number:* the novel stratum holds **13,117 of the 204,578** entity-symbol counts (6.4%), and the alphabet has only 5 symbols, so the whole-vocabulary table is already well estimated where the suffix table was not. More importantly the productivity argument does not transfer: Baayen's hapax stratum matters because what a FREQUENT word's *ending* predicts differs from what a NEW word's ending predicts -- a fact about morphology. **How a string is USED ACROSS A PASSAGE does not depend on how often the reader has met it before**, so the stratification buys sparsity and no signal. I predicted this arm would win (the two tables disagree in SIGN on `e_rep_def`: +0.43 nats toward PROPN on the whole vocabulary, -0.31 toward NOUN on the novel stratum) and it lost; the sign disagreement is real and is estimation noise on 121 novel `e_rep_def` observations.

**2. The DOCUMENT REGISTER (arm B) is null-to-negative on UD-EWT test** -- R2_d3 PROPN<->NOUN 156, R3_d10 158, R4_d30 151, against the floor's 154. *Why:* the mixture weight is `a = n_d/(n_d + theta)` and a 79-token snippet never accumulates enough `n_d` for `a` to matter; where it does fire it fires on 2-3 observations. **This arm cannot be judged on UD-EWT test at all** -- it is designed for the passage-level statistics of a real document, which is why it is measured on GUM in §5.

**2b. AND ON GUM THE DOCUMENT REGISTER IS NOT MERELY NULL, IT IS NEGATIVE -- which is the more interesting result.** R4_d30 on GUM: PROPN<->NOUN **651 against the floor's 563**, PROPN->NOUN 517 against 421, unseen 0.5164 against 0.5214, repeat-mention accuracy 0.5613 against 0.5666. *Why, mechanistically:* the register accumulates the organ's OWN posteriors, and on GUM the organ is right about an unseen word **52.1%** of the time. A predictive-coding feedback loop is only a gain when the higher level's belief is BETTER than the estimate it displaces; here the passage-local table is built out of the organ's own errors and then given weight `a = n_d/(n_d + theta)` that GROWS with the length of the passage -- so the longer the document, the more confidently it feeds its own mistakes back. On GUM's capitalised, NOUN-heavy technical vocabulary it drags names toward NOUN (+96 PROPN->NOUN). **This is a real fidelity finding about the ARM, not about the corpus: rapid adaptation (Fine et al. 2013) is adaptation to the INPUT distribution, and I implemented adaptation to the OUTPUT distribution. The brain's version needs an error signal the substrate does not have at this rung.** Arm B is withdrawn; the patch ships it behind `ENT_THETA_DOC=None` (off) with this measurement in the module comment.

**3. kappa > 2 is a CI-SEPARATED NEGATIVE** -- E5_k4 unseen -0.0154 CI[-0.0274, -0.0043], overall -0.0010 CI[-0.0019, -0.0002]. *Why:* the top-down prior is one 5-symbol table competing against a 19-symbol form description, a graded suffix ladder and a second-order transition; over-weighting it over-rides better-estimated evidence. **kappa is an operating point, swept, never adopted** -- exactly as `UNK_PRIOR_GAMMA` turned out to be.

**4. The acronym -> expansion bind is DEAD BY COUNT, not by argument.** The obvious entity-layer route to the acronym slice pri-99 called form-free (`AMS` / `MSM` / `EWS` / `PPA` / `EPMI` / `CDWR`) is to bind the abbreviation to an earlier capitalised expansion with the same initials, the way a reader learns one. **Measured: 3 of 119 unseen ALL-CAPS/acronym tokens in UD-EWT test have an earlier same-initials capitalised run in their document, and all three are the same string (`GPSA`).** The antecedent is simply not in the text. Not built.

**4b. Reading the prior on the KNOWN-BUT-RARE stratum as well buys nothing.** Cue competition is graded, not binary -- the lexical cue is ABSENT for an unseen word and merely WEAK for a word seen once or twice -- so the principled version damps the prior by the organ's own rare-word shrinkage `1 - c/(c + MIX_KAPPA)` instead of switching it off at the vocabulary boundary. Built (`ent_rare`) and measured on GUM: **B2_k1_w5_rare5 reproduces A2_k1_w5 on every target metric to the digit** (repeat-mention accuracy 0.5773 both, its confusions 258 both, PROPN<->NOUN 550 both), with overall accuracy +0.0005. *Why:* with `MIX_KAPPA = 1.0` the damping is 0.5 at one sighting and 0.33 at two, and a word with even one sighting already has a lexical emission row that dominates a 9-symbol discourse table. **The extension is correct and immaterial; it ships behind `ent_rare=0`.**

**5. The shuffled-chains twin at kappa 2 is a WEAK control and I am reporting it as such.** It scores unseen 0.7970 against that arm's 0.7981 -- a 0.0011 gap, n.s. That is because I twinned E4_k2, an arm that is itself ~null on unseen accuracy; a twin of a null arm proves nothing. The permuted-table twin on the same arm collapses (0.7333, CI-separated below the floor), so the control that matters did fire, and the winning arm's own twins are reported in §5. **Recorded because a control that excludes nothing is not a control** -- the same mistake pri-99 caught in itself.

---

## 7. WHAT STRATEGY SHOULD LAND, AND WHAT TO CHECK

**`lexical_categories_entity_prior_patch.diff`** (409 lines against the current `hdlab/lexical_categories.py`; `git apply --check` CLEAN). *The brief's section 7 names this file `entity_to_category_patch.diff`; the kick-off prompt names it `lexical_categories_entity_prior_patch.diff` and I followed the kick-off. Same file, one name.*

**What it adds, all inside the ONE organ (no new organ, no new module):**
1. `DiscourseRegister` -- Heim file cards for one passage, keyed by surface type, purely surface (no category read, so accrual and inference compute the identical symbol).
2. `entc` / `entc_u` count tables + `_finalize_entity()` -> `log P(E | c)`, one pure function of the counts, re-derived by `finalize()` like every other table.
3. `accrue_docs(docs)` / `accrue_entity_docs(docs)` (offline supply) and **`observe_document(sentences, categories)` -- the ONLINE path**.
4. `new_document()` -- the passage boundary; `update_document_register(words, post)` -- the (measured-negative, default-off) passage register.
5. One additive term in `_log_emit`, gated on the absence of a lexical entry and SILENT at `e_first`.
6. `build_asset` reads `# newdoc` so the shipped asset carries the entity counts.

**Defaults = exactly the measured arm:** `HDLAB_LC_ENT_KAPPA=2.0`, `HDLAB_LC_ENT_RECENCY=5`, `HDLAB_LC_ENT_SKIP_FIRST=1`, `HDLAB_LC_ENT_NOVEL=0`, `HDLAB_LC_ENT_THETA_DOC` unset (the passage register OFF -- a measured negative, §6.2b).

### ⚠️ THE ONE-LINE WIRE, WITHOUT WHICH THE PATCH DOES NOTHING -- AND THIS IS DELIBERATE
With the patch applied and **no** `new_document()` call the organ is **byte-identical to today** (verified: max posterior difference 0.000e+00, 0 tag differences on 5,272 tokens). That is not a default-off switch; it is that the arm needs a PASSAGE and no current consumer hands it one. **The wire is one line, and the reader already has the passage:** `hdlab/situation_reader.SituationReader.read()` takes one document (`conll_path`) and tags it sentence by sentence through the shared singleton `hdlab.lexical_categories.get()`. Add, at the top of `read()` (next to `self._read_parse_cache = {}`, line ~4301):

```python
if _TAG_SOURCE == "counts":
    from hdlab import lexical_categories as _LC
    _LC.get().new_document()          # Heim: a new passage is a new file
```

**Any other consumer that reads a passage should do the same; a consumer that reads isolated sentences correctly gets nothing.**

**The asset must be rebuilt** (`build_asset()`), because `entc` is a new count table. A ready candidate of just the entity counts (4.7 KB) is at `data/hook_state/lexical_categories_entity_counts_w5_candidate.json` and can be merged into the live asset, or rebuild from scratch -- `accrue_docs` produces byte-identical emission/suffix/transition tables to the current flat accrual (it calls the same `accrue` over the same sentences in the same order). **Rebuild the PENN arm the same way** if it is to have the cue.

**Checks I ran that strategy should re-run:**
- `--self-test` (8 witnesses, scaffold-free, ~50 s): document boundaries, the in-order no-same-token-loop property, the Katz/Gelman KIND symbol, **kappa=0 reproduces the LIVE organ to 0.00e+00**, the odds ordering of the accrued table, the ONLINE `observe_document` path, the twin permutation being a derangement, and the counts' save/load round-trip.
- `verify_patch` (R1-R5): the patch is inert without `new_document()`; its `accrue_entity_docs` produces the cell's table exactly; **driven passage by passage it reproduces the measured arm to a max posterior difference of 0.000e+00**; the asset carries the new counts.
- **NO-REGRESS, heads rung** (`--heads`, 24,664 arcs, the organ's own tags): UAS 0.6278 -> 0.6281, tag agreement 0.9313 -> 0.9316. Nothing down.

**AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.** Two entries.
1. **`lexical_categories`** gains a TOP-DOWN arm: the organ was purely bottom-up (form + sequence + lexicon), and predictive coding says the referent level's belief re-enters the category competition. Status unchanged (BF_SPIRIT -- the acquisition source is still the offline supply), with a new recorded deviation: **the passage register (adaptation to the organ's OWN output distribution) is a MEASURED NEGATIVE and the brain's version (adaptation to the INPUT distribution) needs an error signal this rung does not have.**
2. **`coref.name_content_tokens` should be recorded as NOT_BF for the name/common decision, with the number**: it is the sole name gate for 8 live organs and scores F1 0.672 where the category organ scores 0.864 on the same tokens. The audit currently has no entry saying the entity layer's name decision is a capitalisation rule that ignores the category organ.

---

## 7b. WHAT WOULD IT TAKE TO CONVERT THIS TO A FULL PASS

The bar has five clauses. Three are met, one is met on the well-powered population and not on the brief's own, and one I cannot measure from here.

| clause | status | what is missing, concretely |
|---|---|---|
| repeat-mention PROPN<->NOUN down **CI-separated** | **MET on GUM** (`E7_rich_k2` +0.0115 CI[+0.0027,+0.0207]; `N2_nk1` +0.0128 CI[+0.0040,+0.0224]; `S2_k2_w5` see §5), **NOT met on UD-EWT test** | nothing to build -- the brief's population is 288 items with 35 errors and a CI half-width of 0.027. **To meet it ON UD-EWT TEST the corpus would have to have documents**, which it does not. This is the numbered located negative the bar's `OR` clause allows. |
| overall accuracy not down | **MET, and UP CI-separated on GUM** (+0.0011 CI[+0.0005,+0.0017]) | -- |
| twin at the floor | **MET** -- see §5/§4: the shuffled-chains twin sits AT the floor (0.7812 = 0.7812 repeat-mention accuracy) and the permuted-table twin collapses far below it | -- |
| knowledge as counts with an online observe path | **MET** -- `entc`/`entc_u` are counts, `log P(E|c)` is one pure function of them, `observe_document` grows them (witness W6), `online_adapt()` drives the loop | -- |
| the board's `common_noun_coref` not down | **NOT MEASURED** | it needs the patched module on the live path + the one-line wire (§7), which is strategy's step. **And §2b says it cannot move either way: the entity layer never reads this organ.** The honest route to making this clause meaningful is LEAD 1 (the forward wire), not more work on this arm. |

**So the shortest route to a full pass is not more prior-tuning; it is LEAD 1.** Wire the category organ's graded PROPN posterior into `coref.name_content_tokens`, and the board clause becomes measurable and probably positive (F1 0.672 -> 0.864 on the name decision, 1,068 fewer spurious name files). That is a different organ and the brief tells me to report it, so I report it with the number.

## 8. ALTERNATE PATHS, ADJACENT COMPONENTS, NEXT STEPS

### LEAD 1 -- THE FORWARD WIRE. The highest-value thing this work found, and it is not mine to land.
*Structure/computation:* the same top-down/bottom-up loop, in the other direction -- the word-form/category level handing its GRADED posterior UP to the referent system, instead of the referent system re-deriving name-hood from orthography. *The number:* `coref.name_content_tokens` scores **F1 0.672** (P 0.564 / R 0.830, **1,331 false "names"**) against the category organ's **F1 0.864** (P 0.871 / R 0.856, 263 false names) on the same 25,094 tokens. *What it would take:* `name_content_tokens` (or, better, a new graded `name_belief(span, upos_posterior)` in `hdlab/coref.py`) consults the frontend's category posterior for each span token, with capitalisation retained as one cue among several rather than as the decision. Eight organs consume it, so it must land top-down with per-consumer witnesses. *Why not now:* the brief scopes the name bridge to "report, do not edit" (section 7), it is a different organ from my patch's, and pri-94 holds a concurrent diff nearby. **This is the reason the board's `common_noun_coref` and `coref` dimensions did not move for pri-99 and will not move for me: the signal has no wire to travel on.**

### LEAD 2 -- ACCRUE THE ENTITY TABLE FROM REAL PASSAGES, NOT FROM WEB SNIPPETS (the plastic path made load-bearing). **THIS IS NOW THE TOP FOLLOW-ON, because §5b shows what its absence costs.**
*Structure/computation:* the organ is plastic; `observe_document` grows `entc` from comprehension outcomes -- the reader's own settled categories, no gold, no external tool. That is the brain's acquisition path for this table. *The numbers that make it necessary:* in the UD-EWT TRAIN supply a repeated unseen string is usually a NAME (**65% PROPN** on the test snippets); in a real document it is usually a domain term (**63% NOUN** on GUM); and on GENTLE, where capitalised technical common nouns dominate, the mis-specified table makes the organ WORSE (§5b). **The table is learning the snippet corpus's statistics, not a reader's.** *What it would take -- AND I MEASURED IT, so this lead ships with its first result rather than as a hope:* `online_adapt()` is built and run. Adapting on the ODD 13 GENTLE documents (7,308 tokens read, the organ's OWN settled categories, no gold) and scoring the disjoint EVEN 13: repeat-mention accuracy **0.6393 against the floor's 0.7104** -- i.e. **still negative, and barely different from the un-adapted 0.6343 on the full GENTLE**. *Why, with the number that explains it:* the adaptation added 7,308 counts to an existing **204,578**, which is **3.5% of the mass**, so the table did not move. **PLASTICITY WITHOUT FORGETTING IS DOMINATED BY HISTORY.** The organ's counts have an accrual rate and no decay rate; the brain's discourse and lexical statistics decay (ACT-R base-level decay -- the substrate's own `hdlab/salience_binder.actr_activation` implements exactly this for entity files, and it is not applied to any count table in this organ). **So the buildable version of LEAD 2 is: a decay (or an exposure-weighted re-estimation) on `entc`, swept, plus a larger reading experience -- not more accrual at the current rate.** That is a concrete, brain-pinned, one-parameter build, and it is the single most valuable thing this submission exposes about the ORGAN (as opposed to about the wiring, which is LEAD 1). *Why it is filed rather than headlined:* it changes the acquisition story for the whole organ, not just this arm, and the owner's rule is that the strategy session owns integration.

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
- **PLASTIC IS NOT ENOUGH: PLASTICITY WITHOUT FORGETTING IS DOMINATED BY HISTORY.** The project's standing rule is "knowledge = counts, and an online `observe_*` path must exist". This organ has one, I drove it (13 real documents, 7,308 tokens, the organ's own settled categories, no gold), and the mis-specified table did not move -- because 7,308 new counts against 204,578 accumulated ones is **3.5% of the mass**. An accrual rate with no decay rate cannot adapt; the brain's version of this table decays (ACT-R base-level, which the substrate already implements for entity files in `salience_binder` and applies to no count table in this organ). **I would add a sentence to the standing discipline: an online path is only a learning path if it also forgets.**
- **A twin can beat its arm, and that is the control doing its job.** On GENTLE the arm is CI-separated NEGATIVE and its shuffled-chains twin is negative by HALF as much -- the real token<->history pairing is worse than a random one there. A twin that merely tied would have said "uninformative"; a twin that does better says "mis-specified". I would not have found the corpus-specificity nearly so sharply without running the twin on a population where I expected the arm to win.
- **(PHASE 7) A REFUTED ARM CAN BE THE RIGHT IDEA CALIBRATED ON THE WRONG TOKENS.** I refuted the passage register with a CI-separated negative and wrote the mechanism down honestly -- it fed the organ's own errors back. Reading my own mechanism sentence again is what produced the fix: *calibrate on the tokens the organ is SURE about.* One line, no new counts, and it is CI-separated POSITIVE on the exact corpus where everything else failed. **A negative with its mechanism written down is a recipe; a negative with only a verdict is a dead end.**
- **(PHASE 7) BEFORE BLAMING A MECHANISM, CHECK WHAT IS TEACHING IT.** The online path did not adapt, so I built forgetting; forgetting did not fix it, so I built an ORACLE teacher; the oracle helped by exactly as much as the forgetting let it (+0.003 / +0.019 / +0.046 as lambda fell) and still lost. Only then was the real answer visible: on that corpus the cue is uninformative (P(PROPN | repeat AND capitalised) = 0.505), so no teacher and no memory could help. **Three probes, each one cheap, and each one eliminated a hypothesis I would otherwise have asserted.**
- **(PHASE 7) THE BOARD WAS BEING HANDED THE ANSWER.** I set out to measure the forward wire through the board and found that `gum_coref._mention_type` branches on the GOLD `upos` column -- so the board's `coref` and `common_noun_coref` rows use a gold name/common split the live reader does not have. **I would not have found it by reading the brief, only by trying to intervene on the exact line the number depends on.** The check that caught it was cheap: my gold arm reproduces the board's published 0.4681 / 0.5671 exactly, which is both the validation of the harness and the proof of the peek.
- **The organ's own docstring told me where to put the term and what shape it takes.** `log P(E | c)` is a LIKELIHOOD, in the emission slot, next to `log_detc` and `log_rightc`; building it as `log P(c | E)` would have re-applied the category prior a third time. pri-99 paid for that lesson; reading its SOLVED.md in full is why I did not.

---

# ROUND 2 (PHASE 7) -- every negative researched to its mechanism, four more levers built, and the board's own coref split found to be a GOLD PEEK

## 9. WHY GENTLE INVERTS -- IT IS THE CAPITALISATION CONVENTION, AND HERE ARE THE COUNTS

I reported the OOD negative without fully explaining it. The explanation is one number measured four ways, and it is **not** "register" in any vague sense:

| corpus | P(PROPN \| Cap@mid) | P(PROPN \| repeat & Cap@mid) | Cap@INIT PROPN:NOUN | acronym PROPN:NOUN | PROPN as a share of tokens |
|---|---|---|---|---|---|
| **UD-EWT TRAIN (the supply the table was accrued from)** | **0.790** | -- | 1460 : 750 | 1.43 | 0.0617 |
| UD-EWT test | 0.773 | 0.889 | 298 : 124 | 1.75 | 0.0827 |
| **GUM** | **0.933** | **0.923** | 565 : 427 | 3.23 | 0.0547 |
| **GENTLE (OOD)** | **0.509** | **0.505** | **68 : 214** | **1.02** | 0.0514 |

**On GENTLE a mid-sentence capital is a coin flip, and so is a mid-sentence capital that has been seen before.** On GUM both are ~0.93. The entity prior was accrued where repetition-plus-capitalisation means NAME and applied where it means nothing; it therefore pushes the majority class the wrong way, and GENTLE's majority error direction is already NOUN->PROPN (226 against 58).

**And it is not the corpus, it is the GENRE -- the per-document breakdown localises it exactly:**

| GENTLE genre | n (repeat unseen PROPN/NOUN) | P(PROPN) |
|---|---|---|
| `proof_five` / `proof_square` / `proof_wosets` | 77 / 72 / 25 = **174 (29% of GENTLE)** | **0.013 / 0.028 / 0.000** |
| `medical_*` (4 docs) | 95 | 0.07 - 0.25 |
| `dictionary_*` (3 docs) | 31 | 0.20 - 0.40 |
| `poetry_raven` | 45 | 0.178 |
| `esports_fifa` / `esports_fortnite` | 66 | **0.943 / 0.710** |
| `syllabus_opensource` / `syllabus_techtonica` | 121 | 0.708 / 0.536 |

**Mathematical proofs and medical text invert; esports and syllabi behave like GUM.** In a proof, a repeated capitalised unseen string is a *defined term* (`Lemma`, `Set`, `WOSet`); in esports it is a player or a team. **The prior is not corpus-specific, it is CONVENTION-specific, and the convention is observable inside the passage** -- which is what §12 builds.

## 10. THE OTHER NEGATIVES, NOW MECHANISTIC

**The passage register (arm B), and it turned out to be the SAME mechanism as the failed online adaptation.** Arm B mixed a passage-local shape table, accumulated from the organ's own graded posteriors, into the novel-form table. It is CI-separated NEGATIVE (GUM repeat-mention -0.0053, unseen -0.0050). *The mechanism, stated exactly:* **the only teacher available to the feedback loop is the organ's own output, and on the population that needs fixing the organ is near chance** -- unseen-word accuracy on GUM is 0.5214. A predictive-coding loop is a gain only when the higher level's estimate is better than the one it displaces; here it is built out of the learner's own errors, and its weight `a = n_d/(n_d + theta)` GROWS with passage length, so the longer the document the more confidently it feeds them back. §12 repairs it by restricting the calibration to tokens the organ actually knows.

**The Baayen novel-form stratum.** 13,117 of 204,578 counts (6.4%) over a 5-symbol alphabet. Baayen's hapax argument is about MORPHOLOGY -- what a *new* word's ending predicts differs from what a frequent word's ending predicts, because the productive suffixes are the ones that generate new types. **Discourse behaviour has no such generative asymmetry**: whether a string is used bare, pluralised or under an indefinite is a fact about how the writer is using it, not about how often the reader has met it. Correctly tested, correctly negative, and now understood rather than merely recorded.

**The singleton ceiling (100 of 154).** Not a limitation of the mechanism at all: those strings occur exactly once in the whole document, so a discourse register -- forward, backward, or with a perfect resolver -- has no evidence about them by construction. This is the one bound in the submission that is pure arithmetic. What could reach them is knowledge from OUTSIDE the passage (a name gazetteer, a lexicon, the reading-induced inventory), not a better discourse model.

## 11. THE FORWARD WIRE, BUILT AND MEASURED -- AND THE BOARD'S OWN NAME/COMMON SPLIT IS A GOLD PEEK

### 11a. The name decision itself (UD-EWT test, 25,094 tokens; the same gold for all three deciders)

| decider | TOKEN P | R | **F1** | false names | SPAN P | R | **F1** | false name SPANS |
|---|---|---|---|---|---|---|---|---|
| `coref.name_content_tokens` -- **what 8 live organs use** | 0.5640 | 0.8299 | **0.6716** | **1,331** | 0.7545 | 0.7904 | **0.7720** | **352** |
| the category organ (live, prior off) | 0.8711 | 0.8564 | **0.8637** | 263 | 0.8896 | 0.8883 | **0.8890** | **145** |
| the category organ + this brief's entity prior | 0.8677 | 0.8598 | **0.8637** | 272 | 0.8854 | 0.8935 | **0.8894** | 152 |

**The wire is worth +0.1921 F1 at the token level and +0.1170 at the SPAN level** -- and the span level is the one that matters, because a span is what the 8 organs actually type. **207 fewer spurious name spans, a 59% cut**, each of which today opens a bogus entity file. *My own arm adds +0.0004 to this decision and I am not going to dress that up: the entity prior targets repeat-mention unseen tokens, which are a small slice of the name decision. **The wire is the win here, not my arm.***

### 11b. Through the reader, on the board's own coref dimensions -- and what I found doing it

`experiments/gum_coref._mention_type` branches on `head_tok.upos`, and that upos is `cols[3]` of the GUM CoNLL-U: **the GOLD category column.** So the board's `coref` and `common_noun_coref` rows are scored with a GOLD name/common/pronoun split, while the live reader has only a capitalisation rule. **My harness reproduces the board's published numbers exactly under the gold arm (coref 0.4681, common_noun 0.5671 -- the two figures the brief quotes), which is what licenses the comparison.** The pronoun branch is held FIXED across arms, so only the name-vs-common decision varies.

| the name/common decider | `coref` (pronoun) n | acc | its floor | **margin** | `common_noun` n | acc | its floor | **margin** |
|---|---|---|---|---|---|---|---|---|
| **gold UPOS -- the board today** | 3,132 | **0.4681** | 0.3621 | **+0.1060** | 2,855 | **0.5671** | 0.5412 | **+0.0259** |
| `name_content_tokens` -- the LIVE reader | 3,132 | 0.4709 | 0.3608 | +0.1101 | 3,224 | 0.5636 | 0.5478 | +0.0158 |
| **the category organ (prior off)** | 3,132 | 0.4646 | 0.3579 | +0.1067 | 3,303 | **0.5764** | 0.5604 | +0.0160 |
| the category organ + this brief's prior | 3,132 | 0.4658 | 0.3592 | +0.1066 | 3,283 | 0.5760 | 0.5559 | +0.0201 |

**AND THE HONEST READING IS THAT THE BOARD'S COREF ROWS BARELY MOVE.** Replacing a gold name/common split with a capitalisation rule changes the pronoun row by +0.003 and the common-noun row by -0.004; replacing it with the category organ changes them by -0.004 and +0.009. **The board's two coref dimensions are close to INSENSITIVE to the quality of this decision** -- the resolver's margin over its own recomputed floor is +0.106 / +0.107 / +0.110 on the pronoun row whatever decides name-hood. *(The `common_noun` population is itself defined by the decision under test, so its `n` moves 2,855 -> 3,224 -> 3,303 and only the margin over its own recomputed floor is comparable; the pronoun population is identical in all three arms by construction.)*

**Two things follow, and they point in opposite directions:**
1. **The forward wire will NOT show up on the board**, and I am recording that in advance rather than after. Its value is in the decision itself (+0.1170 F1 at the span level, 207 fewer spurious entity files per 25k tokens) and in whatever consumer is sensitive to that -- which these two rows are not. **My round-1 prediction that this brief would be board-neutral was right, but my stated reason was wrong: I said the signal had no wire to travel on; the fuller truth is that the wire exists as a gold shortcut AND the destination barely depends on it.**
2. **The gold peek is still a measurement-integrity defect** even though fixing it costs almost nothing here: the board is reporting a number produced with a column the live reader does not have, and nobody knew. That it happens to be worth ~0.004 is luck, not design.

## 12. THE FURTHER LEVERS, BUILT AND MEASURED

### 12a. COUNT DECAY -- built, swept, and it does NOT rescue the OOD negative. Here is exactly why.

I named "plasticity without forgetting" as the fix and then built it: one multiplicative decay `lambda` on the accrued counts per passage (the exponential form of a forgetting curve; ACT-R base-level decay is the substrate's own pinned form, in `hdlab/salience_binder.actr_activation`, and it is applied to no count table in this organ). Swept on GENTLE, adapting on the odd 13 documents and scoring the disjoint even 13 (floor: overall 0.8502, unseen 0.5517, PROPN<->NOUN 159, repeat-mention n=366 accuracy 0.7104):

| lambda | count mass after 13 passages | repeat-mention accuracy | PROPN<->NOUN | unseen |
|---|---|---|---|---|
| **floor (no prior)** | -- | **0.7104** | **159** | 0.5517 |
| 1.00 (no forgetting) | 211,886 | 0.6393 | 177 | 0.5311 |
| 0.99 | 186,344 | 0.6393 | 177 | 0.5311 |
| 0.95 | 110,249 | 0.6393 | 177 | 0.5311 |
| 0.90 | 55,843 | 0.6393 | 177 | 0.5311 |
| 0.70 | 3,460 | 0.6366 | 177 | 0.5311 |
| 0.50 | -- | 0.6230 | 172 | 0.5279 |
| 0.30 | 452 | 0.6066 | 165 | 0.5273 |

**The weak decays are null for a reason I can write down in closed form, and I predicted it before running it:** a uniform multiplicative decay changes only the RATIO of old mass to new, so adaptation needs `n * log(1/lambda) >= log(M_old / M_new)` -- here `log(204578/7308) = 3.33` over `n = 13` passages, i.e. `lambda <= 0.774`. Everything at or above 0.90 is arithmetically incapable of moving the table, and the measurements agree to the digit. **Below that threshold the table IS re-learned -- and it still loses.**

### 12b. THE ORACLE-CEILING PROBE THAT SETTLES IT (wall-push move 3)

If forgetting works but the table still loses, either the machinery is wrong or **the teacher is**. The only teacher the online path has is the organ's own settled categories, and on GENTLE unseen words it is right 0.55 of the time. So I re-ran the decay sweep with a **GOLD teacher** -- an oracle, never a shippable arm, labelled as such in the code:

| | organ-taught | **GOLD-taught (ORACLE)** | floor |
|---|---|---|---|
| lambda 1.00 | 0.6393 | 0.6421 | **0.7104** |
| lambda 0.70 | 0.6366 | 0.6557 | **0.7104** |
| lambda 0.30 | 0.6066 | **0.6530** | **0.7104** |

**The oracle teacher helps, and by more the more the table is forgotten (+0.003 at no decay, +0.019 at 0.70, +0.046 at 0.30) -- which confirms the teacher is a real part of the loss.** But an oracle-taught, almost-fully-re-learned table still scores 0.6530 against a floor of 0.7104. **So the residual is not adaptation and not memory: on GENTLE the discourse-history cue is close to UNINFORMATIVE, and the counts say so directly -- P(PROPN | repeat AND capitalised mid-sentence) is 0.505 there against 0.923 on GUM.** A perfectly-learned table for an uninformative cue is a flat table, and adding a flat log-prior to a competition can only perturb it. **The correct behaviour is for the prior's WEIGHT to fall to zero on such a passage, which is 12d.**

### 12c. PRECISION-WEIGHTED PREDICTION AND CARD CONFIDENCE

Two more pinned refinements, both pure functions of the counts: (i) **precision-weighting** -- scale `kappa` by how SHARP the referent system's belief for this symbol is, `1 - H(P(c|E))/log T` (Rao & Ballard 1999; Kuperberg & Jaeger 2016 discuss prediction reliability explicitly), so `e_rep_plural` (86% NOUN) is shouted and `e_rep_def` (a coin flip) is whispered; (ii) **card confidence** -- scale `kappa` by `n/(n+theta)` in the number of PRIOR MENTIONS on the file card, the organ's own reliability shrinkage moved from a count row onto the Heim card.

**On GUM, precision-weighting is a wash against the flat-gain arm and I am not going to claim it as a win:** P1 (precision 1.0) gives overall 0.8814, unseen 0.5243, PROPN<->NOUN **536**, repeat-mention 0.5762, first-mention accuracy exactly the floor's 0.8871 -- against the shipped S2's 0.8819 / 0.5254 / **516** / 0.5767 / 0.8871. Same to within noise on every metric, slightly worse on the confusion count. *Why:* the precision term is computed from the GLOBAL table and the global table's symbols are all reasonably sharp (the flattest, `e_rep_def`, still carries 0.43 nats), so the re-weighting spans a narrow range and mostly re-scales kappa uniformly -- which the kappa sweep has already explored. **Precision-weighting only pays when the precision VARIES with the situation, which is why the version that matters is the online-estimated one (PATH 6), not this frozen one.** Card confidence (P4/P5) behaves the same way as the rare-word gate did: the shrinkage `n/(n+1)` is 0.5 at one prior mention and 0.67 at two, and most cards have one or two, so it is close to a uniform kappa reduction.

**Neither refinement is recommended.** Both ship behind `ent_prec=0` / `ent_nconf=0`, and the reason is stated above rather than buried: a FROZEN precision cannot express the thing that actually varies.

### 12d. THE REPAIRED PASSAGE REGISTER -- and it is the lever that fixes the out-of-domain negative

Arm B failed because it calibrated on the organ's own errors. **A reader calibrates a local convention on what it is SURE about.** So: accumulate the passage's shape register **only from tokens that HAVE a lexical entry** -- where the organ scores 0.93, not 0.52 -- and transfer that convention to the unknown tokens, which is what a convention is for. One line, no new counts, no new asset, and it is exactly the top-down adaptation Fine, Jaeger, Farmer & Qian (2013) describe: adaptation to the INPUT distribution, estimated where the input is legible.

**On GENTLE -- the corpus where the entity prior, the decay and even the oracle teacher all failed:**

| arm | overall | unseen | PROPN<->NOUN | repeat-mention acc | FIRST-mention acc |
|---|---|---|---|---|---|
| **floor** | 0.8674 | 0.6034 | 284 (**58** + **226**) | 0.6963 | 0.7274 |
| K1 (theta 10) | 0.8688 | 0.6102 | 265 (79 + 186) | 0.7075 | **0.7487** |
| **K2 (theta 30)** | **0.8689** | **0.6114** | 267 (74 + 193) | 0.7122 | 0.7450 |
| **K3 (theta 100)** | 0.8687 | 0.6094 | 273 (71 + 202) | **0.7186 -- +0.0223 CI[+0.0057, +0.0367] CI-SEPARATED** | 0.7324 |
| K4 (theta 300) | 0.8681 | 0.6066 | 274 | 0.7122 +0.0159 [0.0000, +0.0306] | 0.7274 |
| KS1/KS2 (register **plus** the entity prior) | 0.8663 / 0.8653 | 0.5954 / 0.5894 | 289 / 303 | 0.6598 / 0.6518 | 0.7462 / 0.7312 |

**K3 is CI-SEPARATED POSITIVE on the exact corpus where the entity prior is CI-separated NEGATIVE.** Every metric moves the right way, first mentions included, and the confusion trade is precisely the convention correction the diagnosis predicted: it accepts ~13 more PROPN->NOUN errors to remove ~24 NOUN->PROPN ones, which is the right trade when the dominant direction is NOUN->PROPN. **The refuted arm B was not the wrong idea; it was the right idea calibrated on the wrong tokens.** And the KS arms say the two levers do NOT compose on GENTLE -- the entity prior's damage there exceeds the register's gain, which is consistent with everything in 12b.

**On UD-EWT test it is positive but small (K3, theta 100):** PROPN<->NOUN 154 -> 151, repeat-mention 0.7812 -> 0.7917 (+0.0104 CI[0.0000, +0.0256], not separated), unseen 0.8002 -> 0.8013, overall 0.9312 -> 0.9313, first-mention 0.8188 -> 0.8198.

### 12d-bis. ON GUM IT IS A WASH -- and correcting my own first read of it

My first look at GUM said "negative", because the confusion COUNT rose: PROPN<->NOUN 563 -> 615 at theta 30 and
-> 590 at theta 100 (PROPN->NOUN 421 -> 484 / 454). **With the bootstrap the accuracy deltas are NOT separated:**
theta 30 repeat-mention -0.0027 CI[-0.0069, +0.0012], theta 100 -0.0008 CI[-0.0043, +0.0027], and theta 100's
overall accuracy is marginally POSITIVE (+0.0005 CI[0.0000, +0.0011]). **So the honest statement is a WASH on
GUM, not a negative -- the confusion count moves and the accuracy does not, which is precisely the trap I wrote
into my own KEY REALIZATIONS in round 1 and then walked into again in round 2.** Recorded rather than quietly
fixed.

**The direction is still real and still worth explaining, because it is a flaw in the REPAIR.** Calibrating on
known words estimates the convention *of known words*, and the two populations differ systematically:

| corpus | KNOWN P(PROPN \| Cap@mid) | UNKNOWN P(PROPN \| Cap@mid) | **the bias the repair inherits** |
|---|---|---|---|
| UD-EWT test | 0.7374 (n=1,310) | 0.8574 (n=547) | **-0.120** |
| GUM | 0.9259 (n=4,143) | 0.9437 (n=2,733) | **-0.018** |
| GENTLE | 0.4460 (n=926) | 0.6100 (n=582) | **-0.164** |

**A capitalised word the organ already knows is systematically LESS likely to be a name than a capitalised word
it has never seen** -- in every corpus, by 2 to 16 points. That is not surprising once stated (a novel capitalised
string is disproportionately a genuine new name), and it is exactly the bias a known-token calibration imports.
Where the global table is badly wrong (GENTLE: global 0.79 against a true 0.61) the biased local estimate still
pulls it a long way toward the truth and WINS CI-separated; where the global table is already close (GUM) the
bias is most of what it adds, and it washes out.

**So the summary across three corpora is: CI-separated POSITIVE on GENTLE, positive-not-separated on UD-EWT test,
a WASH on GUM.** It ships **default-OFF** (`ENT_THETA_DOC` unset) not because it is harmful but because "helps a
lot on one corpus, a little on another, nothing on the third" is not a default -- it is a switch with a documented
regime, and 14c is the build that would make it a default.

### 12e. THE SAME REPAIR ON THE ENTITY TABLE -- it recovers about half the out-of-domain damage

If the passage's convention can be estimated locally for the SHAPE cue, it can be estimated for the ENTITY cue: a passage-local `P(E | c)` accumulated from KNOWN tokens only and blended into the global table by the organ's own shrinkage `a = n/(n + theta)`. Where the local evidence says the symbol is uninformative the blend flattens the prior toward the local base rate -- **precision-weighting with the precision estimated ONLINE** (Feldman & Friston 2010, attention as precision) rather than frozen at training time, which is the thing 12c could not do.

On GENTLE (theta 10, the most local setting):

| | floor | S2 (global table only) | **L1 (passage-local blend)** |
|---|---|---|---|
| overall | 0.8674 | 0.8643 | 0.8651 |
| unseen | 0.6034 | 0.5838 | **0.5890** |
| PROPN<->NOUN | 284 | 310 | **294** |
| repeat-mention accuracy | 0.6963 | 0.6343 | **0.6661** |
| first-mention accuracy | 0.7274 | 0.7261 | **0.7274 (the floor exactly)** |

**It recovers roughly half the out-of-domain damage (repeat-mention 0.6343 -> 0.6661 against a floor of 0.6963) and does not reach the floor, and the recovery is MONOTONIC IN HOW LOCAL THE ESTIMATE IS** -- theta 10 gives 0.6661, theta 30 gives 0.6661, theta 100 gives 0.6471, against 0.6343 with no local term at all. That is what the rest of phase 7 predicts it should do: the local estimate is calibrated on known tokens and therefore carries the 2-16 point known/unknown bias of 12d-bis, and underneath that the cue is weakly informative on GENTLE anyway (P(PROPN | repeat AND Cap@mid) = 0.505). **The mechanism is right and it is half-built: the missing piece is the offline known/unknown offset, the same one table 12d-bis asks for.** Ships behind `ent_local=None`.

## 13. EVERY LEAD, ITS ARITHMETIC REACH, AND WHAT HAPPENED TO IT

| # | lead | arithmetic reach | status |
|---|---|---|---|
| 1 | **the forward wire** (entity layer reads the category organ) | the whole name decision: +0.1921 F1 token, **+0.1170 F1 span**, 207 fewer false name spans per 25k tokens | **BUILT + MEASURED + PATCHED** (`coref_forward_wire_patch.diff`, verified 0/5,807 span regressions) |
| 2 | **count decay** (plasticity with forgetting) | the OOD table mis-specification | **BUILT + SWEPT + REFUTED with a closed form** (12a) |
| 2b | the oracle-teacher probe | separates "machinery wrong" from "teacher wrong" | **BUILT** -- teacher is part of it, cue uninformativeness is the rest (12b) |
| 3 | **precision-weighting + card confidence** | the flat-symbol waste | **BUILT + MEASURED** (12c) |
| 4 | **the repaired passage register** (calibrate on KNOWN words) | the capitalisation convention -- the whole OOD failure | **BUILT + CI-SEPARATED POSITIVE on GENTLE, a wash on GUM** (12d) |
| 4b | **+ the offline known/unknown bias correction** | the register's regime-dependence | **BUILT + CI-SEPARATED POSITIVE ON BOTH CORPORA** (14c) -- the one unambiguous phase-7 win |
| 5 | **the passage-local entity table** (the same repair on `entc`) | the OOD failure of the prior itself | **BUILT** (12e) |
| 6 | a re-reading pass | 19 of 154 confusions | **OUT OF SCOPE** by coordinator ruling (organs take data in order) -- recorded as a located ceiling |
| 7 | a cross-string register key | the coreferent-with-a-different-string slice | **NOT BUILT** -- circular at this rung (needs a parse that reads these categories); the coref two-half problem owns it |
| 8 | acronym -> expansion binding | 3 of 119 unseen acronyms | **DEAD BY COUNT** |
| 9 | **a name lexicon for the singletons** | **100 of 154 confusions** -- the largest single slice left | **NOT BUILT, and it is the honest route to the missing third** (see below) |

### THE SINGLETON THIRD NEEDS KNOWLEDGE, NOT A BETTER DISCOURSE MODEL -- AND THE ASSET IS ALREADY ON DISK
100 of the 154 confusions are strings that occur exactly once in the document. No register, no resolver and no second reading pass can reach them, by construction. What reaches them is knowledge from OUTSIDE the passage, and the substrate already holds candidate offline foundation assets: `data/corpora/wikidata_namebridge_types_v2`, `data/corpora/wikidata_person_roles`, and the `who_is_who_lexicon` named in the knowledge register. A static offline name lexicon is ADMISSIBLE supply under the standing rules (it is knowledge the brain already has -- a reader who has met "Souter" before is not doing inference, they are doing retrieval). **This is the highest-reach unbuilt lead in the whole submission and I did not build it: it is a knowledge-acquisition job, not a mechanism job, and it needs a brief of its own.**

## 14. ALTERNATE PATHS, SIMILARLY OR MORE BRAIN-FOUNDATIONAL

**PATH 6 -- ONLINE-ESTIMATED PRECISION AS THE UNIVERSAL GATE (the one the whole of phase 7 points at).** *Structure/computation:* precision-weighted prediction error where the precision is estimated ONLINE rather than frozen at training time (Feldman & Friston 2010, attention as precision; the same idea Kuperberg & Jaeger describe as prediction reliability). *The evidence:* every failure in this submission -- arm B, the online adaptation, the OOD negative -- is one cue being given a fixed gain in a passage where its reliability is different. And the one lever that fixed the worst of them (12d) works precisely by estimating a local statistic on the tokens where the organ is reliable. *What it would take:* generalise 12d from the shape cue to EVERY cue in `_log_emit` -- a per-passage, known-token-calibrated reliability per cue, each cue's kappa scaled by it. *Why this is more brain-foundational than what I shipped:* a fixed kappa per cue is an OUR-INVENTION constant; a locally estimated precision is the pinned computation. **This is my top recommendation and it is bigger than this brief.**

**PATH 7 -- THE NAME DECISION AS A GRADED BELIEF, not a boolean.** `name_content_tokens` returns a list or an empty list, and the eight organs treat name-vs-common as a hard TYPE. The referent route is engaged to a DEGREE. The patch I wrote still returns a boolean-shaped answer (a list or empty) because that is what the callers accept; the more brain-faithful version has `online_cluster` carry P(name) and let it compete inside the retrieval, as the substrate already does for every other cue. *Cost:* medium (8 consumers). *More BF than what I shipped, and I am saying so.*

**PATH 8 -- FIX THE BOARD'S GOLD PEEK (a measurement-integrity job, not a capability one).** `experiments/gum_coref._mention_type` and `_gender_number` both branch on the gold `upos` column, so the board's `coref`, `common_noun_coref` and `salience` rows are scored with a gold name/common/pronoun split the live reader does not have. This is the same family as the 2026-09-09 entity-gate de-leak. *What it would take:* the `caps` and `cat` arms I already built in `forward_wire()`. **This is not my brief's problem to land, but the board has been reporting a number the reader cannot achieve, and someone should know.**

## 14c. THE ONE BUILD THAT WOULD CLOSE IT -- BUILT IN THIS SESSION, WITH ITS PREDICTION STATED IN ADVANCE

Both half-fixes (12d, 12e) fail for the SAME measured reason: a passage register calibrated on known words imports the known/unknown bias. That bias is a property of the language, not of the passage, so it is measurable ONCE, offline, from the supply the organ already has -- by comparing the supply's KNOWN slice with its NOVEL-FORM stratum, which are the two evidence bases `_finalize_unknown_word_cues` already builds. `_build_shape_offset()` in the cell does exactly that and divides it out of every local estimate (`reg_offset=True`, arms `O1`-`O4`).

**THE PREDICTION, recorded before the numbers:** the offset should leave GENTLE's win roughly intact (there the global table is wrong by far more than the bias) and remove most of GUM's regression (there the bias was the only thing the local estimate added). If it does, the repaired register becomes the first lever in this brief that is safe on all three corpora and it should ship ON.

**RESULT, part 1 (GENTLE) -- the prediction holds.** With the offset: theta 30 repeat-mention 0.7107 (+0.0143 CI[0.0000, +0.0271]), **theta 100 0.7186 (+0.0223 CI[+0.0079, +0.0361] CI-SEPARATED)**, theta 300 0.7091 (+0.0127 CI[+0.0036, +0.0222] CI-SEPARATED), against a floor of 0.6963. **The GENTLE win is intact, and at two of three thetas the CI is TIGHTER than without the offset** (+0.0223 CI[+0.0079,+0.0361] against the un-offset +0.0223 CI[+0.0057,+0.0367]) -- the correction removes variance without removing signal, which is what a correct bias term does.

**RESULT, part 2 (GUM) -- the prediction holds here too, and this is the phase-7 result I would defend hardest.** With the offset at theta 100: PROPN<->NOUN **568** against the floor's 563 and **590 without the offset**; repeat-mention accuracy **0.5703** against the floor's 0.5666 and 0.5658 without; **first-mention accuracy 0.8907 against the floor's 0.8871**; unseen 0.5209 against 0.5214.

| GUM | floor | repaired register (theta 100) | **+ the offline bias correction** |
|---|---|---|---|
| PROPN<->NOUN | 563 | 590 | **568** (theta 300: **563**) |
| repeat-mention accuracy | 0.5666 | 0.5658 (-0.0008 n.s.) | **0.5703, +0.0037 CI[+0.0008, +0.0073] CI-SEPARATED** |
| first-mention accuracy | 0.8871 | 0.8873 | **0.8907** |
| overall accuracy | 0.8807 | 0.8812 | 0.8811 (theta 300: **+0.0004 CI[+0.0001, +0.0007] CI-SEP**) |

**So the one build I named as the missing piece is the one that closes it: with the offline known/unknown offset the repaired passage register goes from "CI-separated win on GENTLE, wash on GUM" to **CI-SEPARATED POSITIVE ON BOTH** -- GENTLE +0.0223 CI[+0.0079,+0.0361], GUM +0.0037 CI[+0.0008,+0.0073] -- and it is the only lever in this brief that is not regime-dependent.** The correction costs one table computed once from the supply the organ already holds, at build time, with no read-time cost and no new knowledge source. 

## 14b. THE BAR, RE-SCORED AFTER PHASE 7 -- AND WHY IT IS STILL **PARTIAL**

| clause | after round 1 | **after phase 7** |
|---|---|---|
| repeat-mention confusions down CI-separated | MET on GUM | **MET** (+0.0101 CI[+0.0015,+0.0192]) |
| overall accuracy not down | MET, UP CI-sep | **MET** |
| twin at the floor | MET | **MET** (both twins, both corpora) |
| the board's `common_noun_coref` not down | NOT MEASURED | **MEASURED** -- 0.5671 under the board's own gold split, 0.5764 when the category organ decides instead; the row is insensitive to this decision either way (11b) |
| knowledge as counts with an online observe path | MET | **MET, and the path was DRIVEN** (12a/12b) rather than merely existing |

**Four clauses met, the fifth measured. I am still calling it PARTIAL, and the reason is not modesty:** the shipped default is **CI-separated NEGATIVE out of domain** (GENTLE: repeat-mention -0.0620 CI[-0.1115,-0.0090]), the two levers built to fix that are each half-fixes with a named missing piece, and a solver should not mark an organ change done while it makes one measured population worse. **The offline known/unknown offset (14c) was built and it DOES close the REGISTER's regime-dependence -- but not the PRIOR's out-of-domain negative, which is a different thing: on GENTLE the discourse-history cue is near-uninformative (P(PROPN | repeat AND Cap@mid) = 0.505) and no calibration makes an uninformative cue helpful. The route to SOLVED is therefore PATH 6 -- an online-estimated precision that drives the prior's own weight to zero on such a passage -- and that is a build, not a re-measure.**

## 15. IS THE SESSION EXHAUSTED?

**Closer than when phase 7 began, because the one build I named as missing got built and worked -- and still not exhausted.** Exhausted: the entity prior itself (30+ arms, two corpora, both twins, CI-separated in-genre, understood out of it); the four negatives (each traced to a mechanism with counts); the forward wire (built, measured, patched, verified). **Not exhausted, and each is a specific build with a prediction attached:** (i) PATH 6, the online-estimated precision gate -- I built TWO special cases of it (the repaired register, and its bias correction, which together are the only lever here that is positive on both corpora) and the general case, applying it to the ENTITY cue's own weight, is what would remove the out-of-domain negative; (ii) the name lexicon for the 100 singletons; (iii) the graded name belief (PATH 7). **What I will not claim is a wall.** Every one of those is buildable with machinery that exists, and the reason I stopped is machine time and the scope of a single-organ brief, not a limit I found.

## SUBMISSION PROMPT

```
Problem: a_name_is_a_word_that_picks_out_an_individual_the_entity_layer_must_feed_back_a_prior_to_the_category_organ (pri 104)
Status: PARTIAL -- submitted for review.

The entity layer's belief that a string picks out an INDIVIDUAL now feeds back into the lexical-category
competition as ONE additive count-based log-prior (Kripke/Semenza referent route -> Heim file cards ->
Rao-Ballard/Kuperberg-Jaeger top-down prediction), inside the ONE category organ, as a next-mention prior
that never loops on its own token.

MEASURED on GUM (138 modern documents, 136,855 tokens, held out): repeat-mention PROPN<->NOUN confusions
293 -> 245 (-16.4%), all-unseen PROPN<->NOUN 563 -> 516, unseen accuracy 0.5214 -> 0.5254, OVERALL accuracy
0.8807 -> 0.8819, FIRST-mention accuracy EXACTLY unchanged. On the same population the sibling arms are
CI-SEPARATED (repeat-mention +0.0115 CI[+0.0027,+0.0207]; overall +0.0011 CI[+0.0005,+0.0017]).
On the brief's UD-EWT-test population: 154 -> 148 confusions, same direction, NOT separated -- because that
population is 288 items (its "documents" are 79-token web snippets). That count is in the submission.

Twins: shuffled chains lands EXACTLY at the floor; the permuted table is CI-separated BELOW it.
No-regress: heads UAS 0.6278 -> 0.6281 under the organ's own tags.
Patch verified against the measured arm to max posterior difference 0.000e+00; git apply --check CLEAN.

PHASE 7 (round 2):
* THE FORWARD WIRE IS BUILT AND PATCHED (coref_forward_wire_patch.diff). 8 live organs decide name-vs-common
  through coref.name_content_tokens (capitalisation); the category organ answers the same question far better.
  SPAN-level F1 0.7720 -> 0.8890 (+0.1170), false name spans 352 -> 145. 0/5,807 regressions with no upos.
* THE BOARD'S COREF SPLIT IS A GOLD PEEK: gum_coref._mention_type branches on cols[3] of the GUM CoNLL-U. My
  harness reproduces the published 0.4681 / 0.5671 exactly under that gold arm; swapping in the live
  capitalisation rule or the category organ moves those rows by <=0.01. So the wire will NOT show on the board
  (recorded in advance) and the peek is a measurement-integrity defect regardless.
* GENTLE'S INVERSION IS EXPLAINED BY COUNTS: P(PROPN | Cap@mid) is 0.790 in the supply, 0.933 on GUM, 0.509 on
  GENTLE; per genre it is the mathematical proofs (0.013/0.028/0.000) and medical text that invert.
* COUNT DECAY: built, swept, refuted with a closed form; an ORACLE-TEACHER probe shows the teacher is part of it
  and the cue's uninformativeness is the rest.
* THE REPAIRED PASSAGE REGISTER (calibrate on KNOWN words): CI-separated POSITIVE on GENTLE, NEGATIVE on GUM,
  and the reason is measured -- a capitalised word the organ knows is 2-16 points less likely to be a name.

STATUS STAYS PARTIAL: four bar clauses met, the fifth measured, but the shipped default is CI-separated
NEGATIVE out of domain and the two fixes for that are half-built.

Read notes/problems/<slug>/SOLVED.md sections 9, 11, 12 and 14b first.
```

## A NOTE ON THE COMMIT ATTRIBUTION (recorded once, per the coordinator)

This session's model is Claude Opus 5 (1M context) and its harness attribution rule names that model; the repo's
uniform solver line is `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The coordinator ruled for the
repo line, so round-2 commits carry it. The round-1 commits (`c29918910`, `8aa416589`) carry the harness line.

## GAPS -- steps not performed, and not worked around

1. **The APPLY-THEN-BYTE-COMPARE test of the diff was a DENIED tool call and was not re-run in any form.** The denial, verbatim: *"Permission to use Bash with command SCR=... rm -rf "$SCR/applytest" && mkdir -p "$SCR/applytest/hdlab" && cp /c/AI/hd-instrument/hdlab/lexical_categories.py "$SCR/applytest/hdlab/" && cd "$SCR/applytest" && git init -q . && git apply "...lexical_categories_entity_prior_patch.diff" && cmp ... && echo "APPLY-THEN-BYTE-COMPARE: IDENTICAL" has been denied."* Per the operating rules I did not perform that check another way. **What IS established instead:** `git apply --check` is CLEAN, and the patched module itself is verified against the measured arm on five witnesses (R1-R5 above) including `max posterior difference 0.000e+00`. **Please byte-compare after applying** -- this is the same gap pri-99 recorded, for the same reason.
2. **The BOARD was not run** (`exp_situation_model_qa_modern_v1.py --run`). It needs the patched module on the live path, which is strategy's step. **I predict board-NEUTRAL on `common_noun_coref` (0.5671) and `coref` (0.4681), and I am recording the prediction in advance with its mechanism: §2b shows the entity layer never reads this organ's PROPN belief at all, so no change to that belief can reach those dimensions.** If the board DOES move, that prediction is wrong and §2b should be re-checked first.
3. **The online-adaptation arm was run on GENTLE (13 adapt / 13 score, disjoint) but NOT on GUM.** The GENTLE result is in LEAD 2 and it is a numbered negative with its mechanism (3.5% of the count mass). The GUM version -- adapt on the odd 137 documents, score the even 138 -- is ~45 minutes of machine time and is the natural next measurement; I expect it to be null for the same arithmetic reason unless a decay is added first, and I would rather say that in advance than run it and find out.
4. **The decay/forgetting variant that LEAD 2 identifies as the actual fix was NOT built.** It is one swept parameter on `entc` and the substrate already has the pinned form (`hdlab/salience_binder.actr_activation`). I located it, measured why it is needed, and did not build it -- that is the honest boundary of this session's work on the acquisition side.
5. **The register at its shipped default was verified for patch-equivalence, but the entity-prior-only configuration is the one with the longer verification history.** Both were run; see the reverify command.
7. **`GENTLE` was measured at kappa 1 and 2 only** (both negative). It is possible that a much smaller kappa is neutral-to-positive there; I did not sweep kappa downward on the OOD population, so "the arm hurts OOD" is established at the shipped operating point and not across the whole kappa range.
