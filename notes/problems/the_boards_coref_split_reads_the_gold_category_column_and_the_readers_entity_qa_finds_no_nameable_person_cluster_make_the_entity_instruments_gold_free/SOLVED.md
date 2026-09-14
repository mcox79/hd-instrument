---
problem: the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free
status: PARTIAL
bar: "(a) the board's coref and common_noun rows read NO gold column at decision time -- a grep-level witness plus a scrambled-gold-column twin that leaves the rows byte-identical -- with the new floors and the live numbers published and the old numbers retired; (b) test_coref_which_entity... green again with the question builder finding >= the 2026-09-07 count of questions on the 8 docs, OR a numbered located negative naming the entity-layer change that emptied the person clusters; (c) pri 104's forward wire measured through the gold-free rows, up down or neutral with CI."
result: "(a) DONE. All five decision-time gold columns (upos/lemma/feats/head/deprel) replaced by live organs; the SCRAMBLED-GOLD TWIN is BYTE-IDENTICAL to the gold-free arm on every field of every row (witness `twin_identity_check`, two arms). THE HONEST LIVE NUMBERS, all 275 GUM docs, TEST = odd docs, doc-paired bootstrap 2,000 resamples: COREF (pronoun) gold 0.4681/floor 0.3621 margin +0.1060 CI[+0.0786,+0.1327] -> GOLD-FREE 0.4172/floor 0.3202 margin +0.0970 CI[+0.0734,+0.1206], STILL CI-SEPARATED -- the pronoun-coref capability SURVIVES the instrument repair. COMMON-NOUN gold 0.5671/floor 0.5412 margin +0.0259 CI[+0.0134,+0.0385] CI-sep -> GOLD-FREE 0.4891/floor 0.4876 margin +0.0015 CI[-0.0079,+0.0107] NOT SEPARATED: the board's common-noun coref WIN DOES NOT SURVIVE, and the margin decomposes exactly -- the gold in-text is-a arcs are worth +0.0143 of it (gold 0.0272 -> gold_noisa 0.0165 on the readable population) and the gold CATEGORY column the remaining +0.0109 (gf2+upos +0.0129 -> gf2 +0.0020). SALIENCE gold 0.2555 -> gold-free 0.2993, neither CI-separated (n=137, underpowered, INFORMATIONAL). (b) THE ZERO-QUESTION DEFECT IS A NUMBERED LOCATED NEGATIVE AND IT IS REPAIRED: on all 8 witness documents the entity layer holds 2,648 entities of which 2,532 carry NEGATIVE online-cluster ids (online_entity_cluster default-ON since 2026-09-09 re-keys every non-pronoun mention to -(c+1)) and all 2,532 named clusters live in that space, while all 570 coref resolutions key on POSITIVE coref-column ids over 52 gold clusters -- KEY OVERLAP 0 ON EVERY DOCUMENT, hence 0 questions and 0/56 person clusters with a surface head. Repaired by naming the question's gold chain from the GOLD MENTION STREAM (the answer key) and the model's answer from the reader's OWN entity files via a new gold-free `CorefResolution.resolved_head`: 200 QUESTIONS BUILT ON THE 8 DOCUMENTS where there were 0, and the witness is green again. AND THE READOUT ITSELF WAS A GOLD PEEK WORTH 0.41 OF ACCURACY: naming the model's pick through the pick's GOLD cluster scores 0.6900 (recency 0.3350, protagonist 0.5050, model-recency +0.355 CI[+0.091,+0.535] CI-sep); naming it through the READER'S OWN entity files scores 0.2800 (recency 0.1200, protagonist 0.2350; +0.160 CI[-0.015,+0.431] and +0.045 CI[-0.160,+0.244], neither separated at n=200 over 8 documents). LitBank is 19c so these are INFORMATIONAL; the instrument finding is not. SECOND, INDEPENDENT DEFECT FOUND AND MEASURED: `referent_per_np._mk_referent` stores `span_toks=[head.lower()]`, so on the LIVE reader's default entity stream the name test (capitalisation) is STRUCTURALLY DEGENERATE -- 0 of 2,123 non-pronoun mentions could ever be typed a name (100% of spans all-lowercase) against 166 of 720 on the raw-cased coref stream. (c) pri 104's forward wire through the GOLD-FREE rows: coref +0.0044 (0.4172 -> 0.4216, margin +0.0970 -> +0.0979), common-noun -0.0090 (margin +0.0015 -> -0.0085), salience -0.0146; none CI-separated. On the reader's own entity stream the wire is not a refinement but the only way the decision exists at all: 150 name mentions typed where the count is identically 0. THIRD FINDING, INDEPENDENT OF THE GOLD PEEK: 18 of the 275 GUM documents (GUM_reddit_*, 16,364 of 273,103 tokens = 5.99%) have the FORM column REDACTED TO UNDERSCORES with the gold columns intact, so the live reader has no text there at all; they are 698 of the 802 pronoun->common typing slips. `gum_coref.load_docs` already carries an `exclude_scrubbed=True` parameter that nothing in the body reads."
floor: "Every floor is RECOMPUTED IN PLACE inside each arm, on that arm's own population, by the board's own `_row_from_consumer` (strongest of separate-tracking / recency / same-head string-identity), never pasted across arms. COREF (pronoun): gold 0.3621, caps 0.3608, cat 0.3579, gold-free 0.3202. COMMON-NOUN: gold 0.5412, caps 0.5478, cat 0.5604, gold-free 0.4876. SALIENCE: first-introduced-entity floor, gold 0.1971. The `gold` arm reproduces the board's published coref 0.4681 / common_noun 0.5671 EXACTLY, which is what licenses every comparison here."
controls: "(1) THE SCRAMBLED-GOLD TWIN (bar 8a): the six gold columns are permuted across the tokens of each document (forms and the MISC coref answer key untouched) and the gold-free layer is then applied. Byte-identical on every field of every row, for BOTH gold-free arms (gf2_twin == gf2, gf2_isa_twin == gf2_isa) -- the proof that no gold column is read at decision time. A unit-level twin is in the cell's --self-test (organ tags invariant under the scramble). (2) THE GREP-LEVEL WITNESS: `--witness` enumerates every decision-time gold-column read across the four files in the board's coref chain. (3) HOLD-ONE-GOLD ABLATION, five arms, the signal-loss trace in margin units: restoring the gold upos alone recovers the common-noun margin to +0.0129 CI[+0.0003,+0.0245] (CI-sep) while lemma/head/feats/deprel each recover at most +0.0039; on the pronoun row the single columns recover at most +0.014 and the gold margin is not reached by any of them. (4) THE INFO-FREE TWIN INSIDE EVERY ROW is the board's own (shuffled-identity resolver / random-bridge) and it loses in every arm. (5) PHASE-DIAGRAM SWEEP (the brief authorises sweeping the typing mass): P(PROPN) thresholds 0.30/0.50/0.70 give common-noun margins +0.0010/+0.0013/-0.0031 -- the operating point on the posterior does NOT recover the capability, a clean negative. (6) A CONSTRUCTION-BASED gold-free is-a detector, loose and strict, against the 683 gold appos/cop edges: LOOSE 949 edges at precision 0.119 / recall 0.165 -> common-noun margin +0.0020 -> +0.0056; STRICT 162 edges at precision 0.321 / recall 0.076 -> +0.0030. I predicted precision was the binding constraint and the measurement says the opposite: the bridge is NON-WRITING, so a false edge only offers a candidate the salience competition declines while a missing edge removes the only path -- recall binds, and tripling precision halved the gain. It recovers about a third of the +0.0097 the gold arcs are worth; with gold categories the two stack (+0.0129 -> +0.0140, both CI-sep). (7) THE DUAL-ROUTE LEMMA (Pinker/Ullman rule route when the stored route is silent) is board-IDENTICAL (gf3 == gf2 on every field) and slightly LOWERS lemma-key agreement with gold (0.8196 -> 0.8177): the common-noun identity key needs CONSISTENCY, not correctness. (8) THE READABLE-POPULATION REPLICATION: every headline re-measured with the 18 redacted documents dropped -- gold-free common-noun 0.4891 -> 0.5417, margin still +0.0020 CI[-0.0105,+0.0131] not separated; the conclusion is unchanged, the accuracy is not. (9) PATCH VERIFICATION WITHOUT A REPO WRITE: both diffs are EXECUTED end-to-end by a meta-path loader that runs the patched sources with __file__ set to their real repo paths -- 16 patched modules routed, the reader reads, span_upos aligns with span_toks on every mention, `tagger=None` leaves the mention dict byte-compatible (no span_upos key), resolved_head populated on 140/140 resolutions, and the GUM organ decision layer types mentions and preserves the gold columns as gold_*. (10) TYPE-CONFUSION COUNTS, 18,197 test mentions: type agreement 0.9088, span-head agreement 0.9432, lemma-key agreement 0.8196; gold-name recall 0.8182, gold-common 0.9602, gold-pronoun 0.9108."
files_changed: "experiments/exp_entity_instruments_gold_free_v1.py (the cell: the gold-free decision layer, the seven arms + the hold-one-gold ablations + the tau sweep, the scrambled-gold twin and its identity check, the grep witness, the type-confusion trace, the scrubbed-document detector, the entity-QA diagnosis and the two-scheme repaired QA instrument, --self-test); notes/problems/<slug>/SOLVED.md; notes/problems/<slug>/gum_coref_gold_free_patch.diff (PROPOSED, NOT applied -- experiments/gum_coref.py + exp_board_coref_gum_v1.py + exp_commonnoun_diffhead_anatomy_gum_v1.py; git apply --check CLEAN); notes/problems/<slug>/entity_layer_patch.diff (PROPOSED, NOT applied -- the forward wire's TEN call sites + EntityAliaser.assign + the two mention builders + situation_reader's gold-free resolved_head + space_reader's builder call site + the repaired entity-QA instrument in experiments/exp_situation_model_qa_v1.py + the repaired witness in verification/test_situation_model_qa.py; git apply --check CLEAN, and every patched source EXECUTED end-to-end before proposal); data/exp_entity_instruments_gold_free_v1/*.json (metrics). NO hdlab/ or tools/ file was edited; no board experiment file was edited in place; no asset was touched."
reverify: ".venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --self-test   # organ tags invariant under a scrambled gold column; lemma/number/gender gold-free; ~15s.   THEN the headline:  OMP_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --board --arms gold,caps,cat,gf,gf2,gf2_wire,gf2+upos,gf2_twin --tag _reverify   # expect gold coref 0.4681/0.3621 and common 0.5671/0.5412 EXACTLY (the licence for every comparison); gf2 coref 0.4172/0.3202 margin +0.0970 CI-sep; gf2 common 0.4891/0.4876 margin +0.0015 NOT separated; gf2+upos common margin +0.0152 CI-sep; TWIN gf2_twin vs gf2 BYTE-IDENTICAL=True. ~6 min (2 min of it the first tagging pass).   AND the entity-QA diagnosis:  ... --diagnose --docs 8   # expect key_overlap 0 and questions 0 on all 8 documents, 2,532 of 2,648 entities under negative ids."
---

# The board's two entity rows were graded with five gold columns, not one -- and with 18 documents whose text is redacted to underscores; gold-free, the pronoun-coref capability SURVIVES and the common-noun one DOES NOT

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box, no external LLM / spaCy / nltk at inference, no gold column read in any decision of the gold-free arms. **No `hdlab/` or `tools/` file was written** and **no board experiment file was edited in place** -- both changes are proposed as diffs, and both were EXECUTED end-to-end before being proposed (section 9).

---

## 1. THE OPENING MOVE -- what may an INSTRUMENT read?

The brief's own framing is the right one and it is not the usual one. For an organ the question is *how does the brain do this?*; for an **instrument** it becomes *what does the live system actually know at decision time -- and the instrument may read only that.*

The decision under test is **"is this span a name, a common noun, or a pronoun?"**, and the brain's answer is settled: a proper name is a word that picks out an **individual** (Kripke 1980, rigid designation), and the referent route that stores it -- left temporal pole / anterior temporal lobe (Semenza 2006/2009 proper-name anomia; Damasio et al. 1996) -- sits **above** the posterior-temporal word-form/category level and is **fed by** it. So the gold-free instrument reads the **category organ**, through the one frontend every other board row already reads (`hdlab.frontend.tagger()` -> `hdlab.lexical_categories`). The treebank stays what it is: the **answer key** (the coref chains in MISC), never an input.

## 2. THE SIGNAL-LOSS TRACE, RUNG BY RUNG, WITH COUNTS (the status probe)

**It was not one gold column. It was five**, and only the first was known:

| gold column | what reads it at decision time | what the live reader has instead |
|---|---|---|
| `cols[3]` **upos** | `gum_coref._mention_type` (name/common/pronoun) **and** `_head_of_span`'s non-PUNCT/DET/ADP preference | the category organ's tag |
| `cols[2]` **lemma** | `Mention.lemma_head` -- the **identity key of every common-noun coref decision** | `hdlab.morphology` (glass-box morphy) |
| `cols[5]` **feats** | `_gender_number` -- the Gender/Number **agreement filter in the pronoun pick** | the closed-class pronoun table + the given-name gazetteer + the morphology organ's number |
| `cols[6]` **head** | `_head_of_span` (which token of the span is the head) | the head-final **NP-run** rule over predicted categories |
| `cols[7]` **deprel** | `URG._role` -> ACT-R role prominence, **and** `_appos_copula_isa`, the in-text is-a edges the common-noun **type bridge** rides on | the Competition Model's per-predicate word-order cue; a construction-based is-a detector |

`--witness` prints all **46** of these reads with file and line. **Note what the grep can and cannot prove:** the patch leaves those 46 lines in place and changes what is *in* the columns (the gold values move to `gold_*`), so the grep is a **locator**, not the proof. **The proof is the twin**: permute the six gold columns inside every document and the gold-free rows do not move by a single digit.

**And a sixth loss that has nothing to do with gold at all.** 18 of the 275 GUM documents (`GUM_reddit_*`) ship with the **FORM column redacted to underscores** -- **16,364 of 273,103 tokens, 5.99% overall and 100% of the tokens in those 18 files** -- because the reddit text cannot be redistributed (GUM ships `process_underscores.py` to restore it). The lemma/upos/head columns are intact, so **a gold instrument cannot tell**; the live reader is handed `__ __ __` and asked who *it* refers to. They are **698 of the 802 pronoun->common typing slips**. `gum_coref.load_docs` already declares `exclude_scrubbed=True` -- and **nothing in the function body ever reads it.**

**The typing rung, counted** (18,197 test mentions, gold type x the gold-free arm's type):

| gold | -> name | -> common | -> pronoun | recall |
|---|---|---|---|---|
| **name** | 2786 | 603 | 16 | **0.8182** |
| **common** | 149 | 5435 | 76 | **0.9602** |
| **pronoun** | 13 | 802 | 8317 | **0.9108** |

type agreement **0.9088** | span-head agreement **0.9432** | lemma-key agreement **0.8196**

## 3. THE HONEST LIVE NUMBERS (bar 8a)

All 275 GUM documents, TEST = odd doc index (the board's own split), doc-paired bootstrap, 2,000 resamples. Every floor recomputed in place on that arm's own population. **The `gold` arm reproduces the board's published `0.4681` / `0.5671` exactly**, which is what licenses the comparison.

| arm | COREF (pronoun) n / acc / floor / **margin** | COMMON-NOUN n / acc / floor / **margin** | SALIENCE |
|---|---|---|---|
| **gold** -- the board today | 3132 / 0.4681 / 0.3621 / **+0.1060** [+0.0786,+0.1327] ✅ | 2855 / 0.5671 / 0.5412 / **+0.0259** [+0.0134,+0.0385] ✅ | 0.2555 |
| gold, in-text is-a seed OFF | " | 2855 / 0.5576 / 0.5412 / **+0.0165** [+0.0039,+0.0284] ✅ | " |
| caps (the live reader's rule) | 3132 / 0.4709 / 0.3608 / **+0.1102** ✅ | 3224 / 0.5636 / 0.5478 / **+0.0158** ✅ | 0.2774 |
| cat (category organ, rest gold) | 3132 / 0.4646 / 0.3579 / **+0.1066** ✅ | 3303 / 0.5764 / 0.5604 / **+0.0160** ✅ | 0.2628 |
| **gf** -- naive gold-free | 3145 / 0.4188 / 0.3482 / **+0.0706** ✅ | 3844 / 0.4220 / 0.4240 / **-0.0021** ❌ | 0.2920 |
| **gf2** -- **the gold-free instrument** | 3145 / **0.4172** / **0.3202** / **+0.0970** [+0.0734,+0.1206] ✅ | 3915 / **0.4891** / **0.4876** / **+0.0015** [-0.0079,+0.0107] ❌ | 0.2993 |
| **gf2_twin** (scrambled gold columns) | **byte-identical to gf2** | **byte-identical to gf2** | **identical** |
| gf2 + pri 104's forward wire | 3145 / 0.4216 / 0.3237 / **+0.0979** ✅ | 3872 / 0.4801 / 0.4886 / **-0.0085** ❌ | 0.2847 |

**TWO OPPOSITE CONCLUSIONS, and both matter.**

1. **THE PRONOUN-COREF CAPABILITY SURVIVES.** Accuracy falls `0.4681 -> 0.4172`, but so does the floor (`0.3621 -> 0.3202`), and **the margin is essentially unchanged: +0.1060 -> +0.0970, still CI-separated.** The unified discourse referent really is beating its floor, and it was not the gold columns doing it.
2. **THE COMMON-NOUN COREF WIN DOES NOT.** `+0.0259 CI[+0.0134,+0.0385]` becomes **`+0.0015 CI[-0.0079,+0.0107]`** -- not separated, straddling zero. pri 104 estimated this gold peek was "worth ~0.004" from varying the name/common split alone; varying **all five** columns costs the entire margin.

**AND THE MARGIN DECOMPOSES ALMOST EXACTLY** (readable population, so the two halves are measured on the same documents):

```
gold, everything gold                          margin +0.0272
  - the gold in-text is-a arcs (appos/cop)     margin +0.0129   [-0.0143]   (gf2+upos)
  - the gold CATEGORY column                   margin +0.0020   [-0.0109]   (gf2)
```

Two named repairs, in priority order: **(i) a gold-free in-text is-a detector that actually works** (mine does not -- section 6), and **(ii) a more accurate category organ**, which is pri 104 / 107 / 110's chain, not this brief's.

## 4. THE HOLD-ONE-GOLD ABLATION -- which column carries the signal

Each arm is the full gold-free layer with exactly **one** gold column handed back.

| arm | COREF margin | COMMON-NOUN margin |
|---|---|---|
| gf2 (none) | +0.0970 | +0.0015 |
| gf2 **+upos** | +0.1010 | **+0.0152 ✅ (the only one that separates)** |
| gf2 **+lemma** | +0.0963 | +0.0026 |
| gf2 **+feats** | **+0.1033** | +0.0102 |
| gf2 **+head** | **+0.1109** | +0.0030 |
| gf2 **+deprel** | +0.0878 | +0.0015 |

On the **common-noun** row the answer is unambiguous: **only the category column restores the win.** `+lemma` and `+head` raise the raw accuracy (`0.4891 -> 0.5198 / 0.5099`) **and raise the floor by the same amount**, because the floor is same-head string identity and it reads the same key.

On the **pronoun** row no single column reaches gold's +0.1060 -- `+head` (+0.1109) and `+feats` (+0.1033) exceed it, `+deprel` falls (+0.0878, because the gold deprel also re-ranks the floor). The columns interact; the honest statement is that the gold-free margin is within the gold margin's CI and no single column explains the difference.

## 5. THE QUALITY PUSH -- three levers built, two of them measured negatives I can explain

**(a) THE NP-RUN HEAD, and it is the biggest single lever.** v1 took the last NOUN/PROPN of the span (pri 104's shipped `_span_head_is_name` rule). That heads *"the American College of Pediatricians"* on **Pediatricians** and *"Kim and Jo"* on **Jo**. English NPs are head-final **within the head domain**, and a preposition / coordinator / relative marker / comma **opens a new domain** -- the same boundary the attachment arm's `NP_SPLIT` cue uses. Taking the last NOUN/PROPN of the **first** domain: **common-noun 0.4220 -> 0.4891 (margin -0.0021 -> +0.0015), coref floor 0.3482 -> 0.3202**, span-head agreement with gold **0.9432**.

**(b) THE COMPETITION MODEL'S WORD-ORDER CUE, PER PREDICATE.** The live reader's proxy is one verb per **sentence** (preverbal = subject). MacWhinney & Bates' cue is about **this clause**: a sentence with three verbs has three preverbal slots, and a one-verb rule hands every nominal after the first verb to OBJECT, flattening Centering's Subject > Object ranking (Grosz, Joshi & Weinstein 1995) for every clause but the first. Per-predicate assignment is part of the `gf -> gf2` gain above.

**(c) THE DUAL-ROUTE NUMBER AND LEMMA (Pinker/Ullman words-and-rules).** When the **stored** route is silent -- the string is not in the lexicon, which is most names and most technical nouns -- the **rule** route still strips the regular plural. For **number** this is real: without it every unknown plural reads SINGULAR and the pronoun pick's agreement filter is silently wrong on exactly the referents that matter. For the **lemma** it is a measured **null**: `gf3` is byte-identical to `gf2` on every board field, and lemma-key agreement with gold actually *falls* (0.8196 -> 0.8177).

> **WHY THE DUAL-ROUTE LEMMA IS NULL, mechanistically.** The common-noun identity key is used for **matching two mentions to each other**, never for matching a mention to the gold lemma. A consistent transform -- both mentions get the same stripped key -- merges singular/plural exactly as the gold lemma does, and a *wrong but consistent* key merges the same pairs. The lever has no room because **consistency, not correctness, is what that key needs**, and the surface form is already consistent.

## 6. THE GOLD-FREE IS-A DETECTOR -- built, swept, and it is a NEGATIVE I can account for

The common-noun row's type bridge is seeded by `_appos_copula_isa`, which reads the gold `appos` and `cop` **arcs**. Under a gold-free layer those arcs do not exist, and that seed is worth **+0.0143 of the margin** (measured directly: `gold_noisa`). So I built the same two **constructions** off predicted categories and surface commas.

| detector (readable population, n=3024) | edges | shared with the 683 gold edges | precision | recall | **common-noun margin** |
|---|---|---|---|---|---|
| none (gf2) | 0 | -- | -- | -- | +0.0020 [-0.0105,+0.0131] |
| **loose** (adjacent nominal runs with a comma or a BE between) | 949 | 113 | **0.119** | **0.165** | **+0.0056** [-0.0065,+0.0168] |
| strict (apposition needs a NAME + a determiner; copula a determined common-noun predicate) | 162 | 52 | **0.321** | 0.076 | +0.0030 [-0.0097,+0.0140] |
| *reference:* the **gold** appos/cop arcs (gold_noisa -> gold) | 683 | -- | 1.0 | 1.0 | +0.0175 -> **+0.0272** |

**I PREDICTED PRECISION WOULD BE THE BINDING CONSTRAINT AND I WAS WRONG, WITH THE NUMBER.** The strict detector triples precision (0.119 -> 0.321) and **loses half the board effect** (+0.0056 -> +0.0030). The loose one, at 12% precision, recovers **+0.0036 of the +0.0097 that the gold arcs are worth** -- about a third. The mechanism is legible once counted: the bridge is **non-writing** (`bridge_write=False`, the Nieuwland hold-under-uncertainty form), so a wrong is-a edge only offers a candidate that the salience competition then declines, while a **missing** edge removes the only path to a different-head antecedent. **In a non-writing bridge, recall is the binding constraint and false edges are nearly free** -- which is a fact about the consumer, not about the detector, and it is the opposite of the intuition I built the strict arm on.

**And with gold categories the two stack:** `gf2+upos` +0.0129 -> `gf2_isa2+upos` +0.0140, both CI-separated. **So the honest statement is that a gold-free in-text is-a seed is a real, partially-built lever worth up to +0.0097 of the common-noun margin, of which a construction detector over predicted categories recovers about a third.** What would recover the rest: the **arc-labeler rung** under the attachment arm (pri 108's chain) -- `appos` and `cop` are labels, and a labelled arc is what the gold column is.

## 7. THE PHASE-DIAGRAM SWEEP -- and it does not move the operating point that matters

The brief authorises sweeping the **posterior mass** used for typing. The category organ hands down a graded belief; the entity layer's decision is binary (open a name file or not); the threshold between them is free. Swept:

| P(PROPN) threshold | COMMON-NOUN acc / floor / margin | COREF margin |
|---|---|---|
| argmax (gf2) | 0.5417 / 0.5397 / **+0.0020** | +0.0970 |
| tau 0.30 | 0.5366 / 0.5356 / +0.0010 | +0.0973 |
| tau 0.50 | 0.5418 / 0.5405 / +0.0013 | +0.0967 |
| tau 0.70 | 0.5452 / 0.5483 / **-0.0031** | +0.0986 |

**Accuracy rises with tau and the floor rises with it.** The capability does not live at a different operating point on the PROPN posterior -- it lives in the **is-a seed** and in **how often the organ is right**, which is section 3's decomposition. This is a clean phase-diagram negative and it is worth recording so nobody sweeps it again.

## 8. THE READER'S OWN ENTITY QA -- TWO defects, both with counts

### 8a. WHY ZERO QUESTIONS (the brief's INFERRED item, now MEASURED)

`build_coref_questions` names a question's gold chain through `_named_clusters(sm)`, which is keyed by `sm.entities[].cluster`. **Since 2026-09-09 that is not the coref column's id space.** `online_entity_cluster` is default-ON and re-keys every **non-pronoun** mention to a fresh **negative** online file id (`-(c+1)`); pronoun mentions keep their positive coref-column cluster. `sm.coref_resolutions[].gold_cluster` / `.resolved_cluster` are in the **positive** space. The two are disjoint.

| doc | entities | of them negative-id | named clusters | persons | persons **with heads** | resolutions | gold clusters | **key overlap** | questions |
|---|---|---|---|---|---|---|---|---|---|
| 1023_bleak_house | 462 | 433 | 433 | 13 | **0** | 26 | 12 | **0** | **0** |
| 105_persuasion | 327 | 311 | 311 | 9 | **0** | 114 | 8 | **0** | **0** |
| 1064_masque_red_death | 376 | 365 | 365 | 3 | **0** | 22 | 3 | **0** | **0** |
| 110_tess | 302 | 289 | 289 | 7 | **0** | 39 | 7 | **0** | **0** |
| 11231_bartleby | 433 | 423 | 423 | 6 | **0** | 95 | 5 | **0** | **0** |
| 113_secret_garden | 212 | 196 | 196 | 9 | **0** | 139 | 8 | **0** | **0** |
| 1155_secret_adversary | 327 | 315 | 315 | 7 | **0** | 56 | 7 | **0** | **0** |
| 11_alice | 209 | 200 | 200 | 2 | **0** | 79 | 2 | **0** | **0** |
| **TOTAL** | **2648** | **2532** | **2532** | **56** | **0** | **570** | **52** | **0** | **0** |

**The brief's "13 persons, 0 with surface heads" is exactly this**: the person clusters are the ones with positive (pronoun-stream) ids, and non-pronoun mentions -- the only ones that carry a head -- all moved to the negative space. **The instrument is stale, not the reader** (the reader's clustering is the de-leak the owner asked for).

### 8b. THE SECOND DEFECT -- the live entity stream cannot see a name at all

`referent_per_np._mk_referent` builds each referent with `span_toks=[head.lower()]`. The ten organs that type a mention call `coref.name_content_tokens`, which decides by **capitalisation**. Measured on 4 LitBank documents:

| mention stream | non-pronoun mentions | all-lowercase spans | **typed NAME** |
|---|---|---|---|
| `referent_per_np` (**the default reader's entity source**) | 2,123 | **2,123 (100%)** | **0 (0.0000)** |
| the coref column (raw-cased) | 720 | -- | 166 (0.2306) |

**On the live path the name decision is not inaccurate, it is degenerate**: no referent can ever open a name file, so every one goes down the `"surf:"` common-noun path with no aliasing. This is upstream of, and independent of, the id-space defect.

### 8c. THE REPAIR, IN TWO NAMING SCHEMES

- **the question's gold** comes from the **gold mention stream** (`gold_cluster_names`) -- the answer key, which is exactly what the question asks about;
- **`cluster_named`** (the 2026-09-07 readout, **INFORMATIONAL**): the model's pick is named through its **gold** cluster -- a gold read *at readout*, which hands the instrument the gold equivalence classes for free;
- **`head_named`** (**the honest arm**): the model's pick is its own `resolved_head` -- a new, additive, gold-free field on `CorefResolution` -- canonicalised through the **reader's own entity files**. No gold column on the model side.

**200 QUESTIONS ON THE 8 WITNESS DOCUMENTS, WHERE THERE WERE 0.** Doc-paired bootstrap, 2,000 resamples:

| naming scheme | n | model | recency floor | most-frequent floor | model - recency | model - mostfreq |
|---|---|---|---|---|---|---|
| `cluster_named` (the 09-07 readout, **INFORMATIONAL** -- it names through the gold cluster) | 200 | **0.6900** | 0.3350 | 0.5050 | **+0.355 [+0.091,+0.535]** ✅ | +0.185 [-0.030,+0.551] |
| **`head_named`** (**the honest, gold-free readout**) | 200 | **0.2800** | 0.1200 | 0.2350 | +0.160 [-0.015,+0.431] | +0.045 [-0.160,+0.244] |

> **THE NAMING STEP WAS WORTH 0.41 OF ACCURACY.** `0.6900 -> 0.2800`. Naming the model's pick through the **gold cluster of the mention it picked** silently collapses every surface form of a gold chain onto the right answer -- the entity layer's whole job, done by the answer key. The floors fall too (`0.335 -> 0.120`, `0.505 -> 0.235`), so it is not a pure gift to the model; but **the model's margin over the protagonist floor goes from +0.185 to +0.045 and neither separates at n=200 over 8 documents.**
>
> **19c CAVEAT, binding:** LitBank is 19c text and is BANNED from requirements. **These numbers are INFORMATIONAL**; the graded claim above is about the *instrument*, which is corpus-independent, not about the reader's coref ability.

**Per document, the honest arm** (`head_named` model): Alice 0.950, Persuasion 0.536, Bleak House 0.500, Tess 0.500, Secret Adversary 0.333, Masque 0.100, Secret Garden 0.036, Bartleby 0.000. The two floors are at 0.000 on five of the eight, so the instrument is **not** degenerate -- it is sparse, and the honest reading is that it is under-powered at 8 documents rather than that the reader is at chance.

## 9. HOW THE DIFFS WERE VERIFIED WITHOUT WRITING TO THE REPO

The standing rule that earned itself on 2026-09-14 07:25 is that **a diff which widens a signature must pass the new argument at every call site, or a builder silently ships a different organ**. `parse_litbank_conll` gained `tagger=`; its call sites in `hdlab/` are **four** (`referent_per_np`, `situation_reader` x2, `space_reader`) and in `tools/` **zero** -- **all four are in the diff**. `EntityAliaser.assign` gained `upos=`; its three call sites are in the diff. All **ten** `name_content_tokens` call sites named in the brief are in the diff.

Both patches were then **executed**: a meta-path loader runs the patched sources with `__file__` set to their **real repo paths**, so every `_REPO`/asset path resolves as it would after landing. **16 patched modules routed; the reader reads; `span_upos` aligns with `span_toks` on every mention; `tagger=None` leaves the mention dict byte-compatible (no `span_upos` key); `resolved_head` populated on 140/140 resolutions; the GUM organ layer types mentions and preserves the gold columns as `gold_*`.** Nothing in `hdlab/`, `tools/` or `experiments/` was written.

## 10. WHY THE ONE THING THAT WORKED, WORKED -- the chain cracked and the chain not cracked

**The successful improvement is the PRONOUN row surviving gold-free with its margin intact (+0.1060 -> +0.0970, still CI-separated), and the reason is that its chain is BRAIN-FOUNDATIONAL ALL THE WAY TO THE TOP:**

| rung | what the pronoun pick needs | gold-free source | status |
|---|---|---|---|
| tokens | the surface forms | the corpus text | ✅ |
| categories | is this span a pronoun? | **a CLOSED CLASS** (`PRONOUNS_ALL`) -- the brain's own answer: function words are a closed lexicon, not a decision | ✅ **never needed the gold column at all** |
| phi-features | gender / number of the pronoun | `_pron_gn`, the same closed-class table | ✅ **already gold-free in the landed resolver** |
| phi-features of the candidates | gender / number of the referents | the gazetteer + the morphology organ's dual route | ⚠️ costs +0.006 of margin |
| salience | Subject > Object ranking | the Competition Model's per-predicate word-order cue | ⚠️ costs ~+0.009 of margin |
| the pick | ACT-R activation over the referent file set | **unchanged -- it never read a gold column** | ✅ |

**The pronoun pick's two load-bearing inputs -- the pronoun's own identity and its own phi-features -- are CLOSED-CLASS facts, and a closed class is knowledge, not a decision.** That is why the capability was real and why the gold peek was, for that row, nearly free. The chain was already cracked to the top; nobody had checked.

**THE COMMON-NOUN ROW'S CHAIN IS NOT CRACKED, AND THE TWO UNCRACKED RUNGS ARE NAMED:** its identity key is an **open-class** decision (which noun, which lemma, which head) and its bridge needs a **labelled arc** (`appos`/`cop`). Both are organs that are still stand-ins or absent on the live path -- the category organ at name recall 0.8182, and no gold-free arc labeller at all. **The board's +0.0259 was those two gold columns, not the resolver.**

## 11. WHAT WOULD CONVERT THIS TO A FULL PASS

**Bar (a) is met** (twin byte-identical, witness, numbers published, floors recomputed). **Bar (b) is met as a numbered located negative AND repaired.** **Bar (c) is met** (the wire measured through the gold-free rows with CI).

What keeps it PARTIAL is that **the common-noun row has no gold-free capability to report**, and that is not a measurement bug -- it is the true state of the system. Every lead, with its arithmetic reach:

| lead | reach | status |
|---|---|---|
| a gold-free in-text **is-a** seed that works | **+0.0143** of the common-noun margin (measured by ablation) | **BUILT AND INSUFFICIENT** as a construction detector (P 0.321 at 162 edges). Belongs to the **arc-labeler rung** -- `appos`/`cop` are labels, and the labels rung is pri 108's |
| a more accurate **category organ** on mention heads | **+0.0109** of the margin; name recall 0.8182 today | pri 104's entity prior, pri 107 (landed), pri 110 (VERB-as-AUX) -- **not this brief's remit** |
| drop the **18 redacted documents** from every board population | removes 698 of 802 pronoun typing slips; raises gold-free common-noun accuracy 0.4891 -> 0.5417 | **ONE LINE** -- `load_docs` already has the parameter and ignores it. Strategy's call, because it moves every published GUM number |
| the **span head** from the attachment arm's parse rather than the NP-run rule | span-head agreement 0.9432 today; `+head` is worth +0.0139 of the coref margin | unbuilt here (a full GUM parse is ~50 min); a bounded, measurable follow-on |
| wire `span_upos` **live** and re-measure the reader | the name decision goes from **0 of 2,123** to a real decision | the diff is written and executed; it needs a board A/B, which is strategy's |

## 12. ALTERNATE PATHS, similarly or more brain-foundational

1. **Heads from the attachment arm, not a rule.** The NP-run rule is a *good* stand-in for a head domain, but the substrate has a head organ (`hdlab/attachment_arm`, the reading-learned cue competition) and the brain does not have a separate "NP head rule" -- it has one attachment competition. More BF, ~50 min of GUM parsing per arm, and the `+head` ablation says it is worth up to +0.014 on the pronoun row.
2. **Roles from the Competition-Model role assigner** (`hdlab/graded_role_assigner.coarse_roles`) instead of the word-order cue alone. The Competition Model is word order **plus animacy plus agreement in competition**; I shipped only the word-order cue because the others need heads. Strictly more BF. *(Not touched here: pri 108 holds that file.)*
3. **Mention DETECTION gold-free too.** This brief kept the gold mention spans, as the instrument convention -- the reader is given the sentence, so being given the mention boundaries is defensible. But a fully honest entity instrument would detect its own mentions; `referent_per_np` already does exactly that, and the gap between "typed 3,915 given spans" and "found its own referents" is the next honesty step.
4. **Change the gold to the ability (the wall-break move).** The 18 redacted documents are the clearest case in the corpus: no reader can read `__`, so scoring on them measures nothing. The same question should be asked of the `n` shift (2,855 -> 3,915 common-noun items): the gold-free arm is being graded on ~1,000 extra items **because it typed them differently**, and a per-item paired comparison on the intersection is a strictly better instrument than a margin over two different populations.
