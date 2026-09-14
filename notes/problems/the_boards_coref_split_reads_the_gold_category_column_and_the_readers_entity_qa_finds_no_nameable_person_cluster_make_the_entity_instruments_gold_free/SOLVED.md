---
problem: the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free
status: PARTIAL
bar: "(a) the board's coref and common_noun rows read NO gold column at decision time -- a grep-level witness plus a scrambled-gold-column twin that leaves the rows byte-identical -- with the new floors and the live numbers published and the old numbers retired; (b) test_coref_which_entity... green again with the question builder finding >= the 2026-09-07 count of questions on the 8 docs, OR a numbered located negative naming the entity-layer change that emptied the person clusters; (c) pri 104's forward wire measured through the gold-free rows, up down or neutral with CI."
result: "PHASE 7 HEADLINES FIRST. (1) THE READER THROWS THE CASE AWAY AT ITS SENTENCE SOURCE: `hdlab/scene_segment.parse_conll_sentences` -- the live reader's ONLY sentence source (situation_reader, referent_per_np, space_reader, causation_typing) -- does `cols[3].lower()`. Measured cost to the category organ on 127,919 GUM test tokens, same organ, same text, case the only difference: PROPN P/R/F1 0.9050/0.8232/0.8622 CASED vs 0.9417/0.2996/0.4546 LOWERCASED (-0.4076 F1; it misses 5,024 of 7,173 proper nouns, 70%), all-tag accuracy 0.9302 -> 0.9027 (-0.0275 on EVERY token for EVERY reader consumer); tag agreement 0.9637. For scale, pri 104's wire is worth +0.1921 token F1 -- this is more than double and it is one argument. It also silently kills referent_per_np.frame_heads' documented mid-sentence-CAPITAL cue and lexical_categories.word_shape. The diff adds `parse_conll_sentences(path, lower=True)` with the CURRENT default (byte-identical) and passes it EXPLICITLY at all four hdlab call sites (0 in tools/) so the flip is one visible edit per consumer; flipping it needs a board A/B, which is strategy's. (2) THE CAPABILITY IS REAL AND THE CATEGORY ORGAN IS THE WHOLE GAP: on the 28,688 of 34,001 mentions (0.8437) where the organ reproduces the gold TYPE+HEAD+LEMMA, both arms scored on IDENTICAL items, the GOLD-FREE common-noun margin is +0.0193 CI[+0.0057,+0.0318] CI-SEPARATED against gold's +0.0263 CI[+0.0133,+0.0389] -- 73% of gold's margin recovered. It is destroyed on the full population by the 15.6% the organ gets wrong; closing that is worth up to +0.0173 of margin. (3) AFTER THE HEAD-DOMAIN FIX pri 104's WIRE IS EXACTLY `upos[head]==\"PROPN\"`: the two predicates agree on 17,005 of 17,010 GUM test mentions (0.99971) and the wire is WRONG on all 5 exceptions (long all-PROPN names rejected by MAX_NAME_TOKENS). STRATEGY SHOULD LAND THE SIMPLE FORM; what name_content_tokens genuinely adds is the TOKEN EXTRACTION for the aliaser, not the decision. (4) RESTORING THE CASE IN referent_per_np._mk_referent RECOVERS NOTHING (0 TP either way) because the case is gone one level up -- finding (1). (5) THE NEGATIVE IDS ARE A DESIGN, NOT A DEFECT: online_entity_cluster's docstring specifies the fresh NEGATIVE-INTEGER id so a `CN:` string cannot crash the `rc >= 0` guard (situation_reader:2733) AND so an online file is unmistakable for a gold chain -- the very confusion the instrument fell into. My repair keeps that intent and touches no clustering decision. (6) Q1 APPLIED -- excluding the 18 redacted documents leaves the coref and entity-KB rows IDENTICAL TO THE DIGIT (URG._per_type_acc already skipped them: a redacted pronoun's surface form is `__`, never third-person) and moves only common-noun (gold-free n 3915 -> 3024, acc 0.4891 -> 0.5417, margin +0.0015 -> +0.0020) and salience. (7) BEST GOLD-FREE STACK on the readable population: common-noun 0.5476/0.5400 margin +0.0076 [-0.0046,+0.0185], still not separated; the recall mechanism held a fourth time (strict +0.0030 < loose +0.0056 < connectives +0.0063 < wider gap +0.0073). (8) THE READER-FAITHFUL ARM REFUTES THE COMMON-NOUN ROW AS A CROSS-ARM INSTRUMENT, and I am not claiming the result it produces: feeding the organ the LOWERCASED text the reader actually gets collapses the name population 62% (2,948 -> 1,128 typed names, exactly what PROPN recall 0.2996 predicts) and the common-noun margin goes UP -- +0.0020 -> +0.0047, and with the connective is-a seed to +0.0104 CI[+0.0007,+0.0199] CI-SEPARATED, the only CI-separated gold-free common-noun result on a full population in this session. It is an ARTEFACT: the population is defined by the decision under test, so ~1,800 mis-typed names fall into the row, names resolve easily by repeated surface string, and model AND floor both rise (0.5417/0.5397 -> 0.5940/0.5893). MARGIN OVER A ROW'S OWN RECOMPUTED FLOOR IS NOT COMPARABLE ACROSS ARMS WHOSE TYPING DIFFERS; the instrument that survives is the PAIRED SUBPOPULATION (identical items, identical floor). Meanwhile the pronoun row moves +0.0970 -> +0.0960 while the name population collapses 62% -- the fifth independent confirmation that its inputs are closed-class. AND THIS DEFLATES MY OWN HEADLINE: the -0.4076 PROPN F1 stands (measured at the organ against gold, population-independent) but it is NEARLY INVISIBLE on these two board rows; it lands on the entity files, the aliaser, the crosstype experiencer bind and who-did-what, and should be measured there. ORIGINAL BARS: (a) DONE. All five decision-time gold columns (upos/lemma/feats/head/deprel) replaced by live organs; the SCRAMBLED-GOLD TWIN is BYTE-IDENTICAL to the gold-free arm on every field of every row (witness `twin_identity_check`, two arms). THE HONEST LIVE NUMBERS, all 275 GUM docs, TEST = odd docs, doc-paired bootstrap 2,000 resamples: COREF (pronoun) gold 0.4681/floor 0.3621 margin +0.1060 CI[+0.0786,+0.1327] -> GOLD-FREE 0.4172/floor 0.3202 margin +0.0970 CI[+0.0734,+0.1206], STILL CI-SEPARATED -- the pronoun-coref capability SURVIVES the instrument repair. COMMON-NOUN gold 0.5671/floor 0.5412 margin +0.0259 CI[+0.0134,+0.0385] CI-sep -> GOLD-FREE 0.4891/floor 0.4876 margin +0.0015 CI[-0.0079,+0.0107] NOT SEPARATED: the board's common-noun coref WIN DOES NOT SURVIVE, and the margin decomposes EXACTLY, measured on one population (the readable one, where gold is +0.0272): dropping ONLY the gold appos/cop is-a arcs -0.0097 (gold_noisa +0.0175); dropping lemma/head/feats/deprel too but keeping gold categories -0.0046 (gf2+upos +0.0129, still CI-sep); dropping the gold CATEGORY column as well -0.0109 (gf2 +0.0020) -- the three steps sum to -0.0252, the whole margin, and the two that matter are the CATEGORY ORGAN and the IS-A ARCS. SALIENCE gold 0.2555 -> gold-free 0.2993, neither CI-separated (n=137, underpowered, INFORMATIONAL). (b) THE ZERO-QUESTION DEFECT IS A NUMBERED LOCATED NEGATIVE AND IT IS REPAIRED: on all 8 witness documents the entity layer holds 2,648 entities of which 2,532 carry NEGATIVE online-cluster ids (online_entity_cluster default-ON since 2026-09-09 re-keys every non-pronoun mention to -(c+1)) and all 2,532 named clusters live in that space, while all 570 coref resolutions key on POSITIVE coref-column ids over 52 gold clusters -- KEY OVERLAP 0 ON EVERY DOCUMENT, hence 0 questions and 0/56 person clusters with a surface head. Repaired by naming the question's gold chain from the GOLD MENTION STREAM (the answer key) and the model's answer from the reader's OWN entity files via a new gold-free `CorefResolution.resolved_head`: 200 QUESTIONS BUILT ON THE 8 DOCUMENTS where there were 0, and the witness is green again. AND THE READOUT ITSELF WAS A GOLD PEEK WORTH 0.41 OF ACCURACY: naming the model's pick through the pick's GOLD cluster scores 0.6900 (recency 0.3350, protagonist 0.5050, model-recency +0.355 CI[+0.091,+0.535] CI-sep); naming it through the READER'S OWN entity files scores 0.2800 (recency 0.1200, protagonist 0.2350; +0.160 CI[-0.015,+0.431] and +0.045 CI[-0.160,+0.244], neither separated at n=200 over 8 documents). LitBank is 19c so these are INFORMATIONAL; the instrument finding is not. SECOND, INDEPENDENT DEFECT FOUND AND MEASURED: `referent_per_np._mk_referent` stores `span_toks=[head.lower()]`, so on the LIVE reader's default entity stream the name test (capitalisation) is STRUCTURALLY DEGENERATE -- 0 of 2,123 non-pronoun mentions could ever be typed a name (100% of spans all-lowercase) against 166 of 720 on the raw-cased coref stream. (c) pri 104's forward wire through the GOLD-FREE rows: coref +0.0044 (0.4172 -> 0.4216, margin +0.0970 -> +0.0979), common-noun -0.0090 (margin +0.0015 -> -0.0085), salience -0.0146; none CI-separated. On the reader's own entity stream the wire is not a refinement but the only way the decision exists at all: 150 name mentions typed where the count is identically 0. AND ITS COMMON-NOUN LOSS IS A HEAD-DOMAIN DEFECT IN THE LANDED CODE, LOCATED AND FIXED: `coref._span_head_is_name` takes the last NOUN/PROPN of the WHOLE span, so a span carrying a PP or a relative clause is typed by a PROPN inside a MODIFIER (`the environments identified by Quilis` -> NAME). On 17,010 GUM test mentions the whole-span and NP-domain head rules disagree on 1,415 (8.3%) and change 403 typings (241 common->name); through the gold-free common-noun row the shipped rule scores margin -0.0074 against the domain rule's +0.0023 (+0.0020 with no wire), and with the is-a detector too +0.0059. The one-line fix is in entity_layer_patch.diff and unit-checked on five span shapes. THE DEEPER READING: given the same head, the wire's typing differs from the category organ's plain argmax on 5 mentions net out of 17,010 -- `name_content_tokens(span, upos)` IS `upos[head]=="PROPN"` -- so the wire was never going to add anything over reading the organ on THIS instrument; everything it appeared to do was its head rule. THIRD FINDING, INDEPENDENT OF THE GOLD PEEK: 18 of the 275 GUM documents (GUM_reddit_*, 16,364 of 273,103 tokens = 5.99%) have the FORM column REDACTED TO UNDERSCORES with the gold columns intact, so the live reader has no text there at all; they are 698 of the 802 pronoun->common typing slips. `gum_coref.load_docs` already carries an `exclude_scrubbed=True` parameter that nothing in the body reads."
floor: "Every floor is RECOMPUTED IN PLACE inside each arm, on that arm's own population, by the board's own `_row_from_consumer` (strongest of separate-tracking / recency / same-head string-identity), never pasted across arms. COREF (pronoun): gold 0.3621, caps 0.3608, cat 0.3579, gold-free 0.3202. COMMON-NOUN: gold 0.5412, caps 0.5478, cat 0.5604, gold-free 0.4876. SALIENCE: first-introduced-entity floor, gold 0.1971. The `gold` arm reproduces the board's published coref 0.4681 / common_noun 0.5671 EXACTLY, which is what licenses every comparison here."
controls: "(1) THE SCRAMBLED-GOLD TWIN (bar 8a): the six gold columns are permuted across the tokens of each document (forms and the MISC coref answer key untouched) and the gold-free layer is then applied. Byte-identical on every field of every row, for BOTH gold-free arms (gf2_twin == gf2, gf2_isa_twin == gf2_isa) -- the proof that no gold column is read at decision time. A unit-level twin is in the cell's --self-test (organ tags invariant under the scramble). (2) THE GREP-LEVEL WITNESS: `--witness` enumerates every decision-time gold-column read across the four files in the board's coref chain. (3) HOLD-ONE-GOLD ABLATION, five arms, the signal-loss trace in margin units: restoring the gold upos alone recovers the common-noun margin to +0.0129 CI[+0.0003,+0.0245] (CI-sep) while lemma/head/feats/deprel each recover at most +0.0039; on the pronoun row the single columns recover at most +0.014 and the gold margin is not reached by any of them. (4) THE INFO-FREE TWIN INSIDE EVERY ROW is the board's own (shuffled-identity resolver / random-bridge) and it loses in every arm. (5) PHASE-DIAGRAM SWEEP (the brief authorises sweeping the typing mass): P(PROPN) thresholds 0.30/0.50/0.70 give common-noun margins +0.0010/+0.0013/-0.0031 -- the operating point on the posterior does NOT recover the capability, a clean negative. (6) A CONSTRUCTION-BASED gold-free is-a detector, loose and strict, against the 683 gold appos/cop edges: LOOSE 949 edges at precision 0.119 / recall 0.165 -> common-noun margin +0.0020 -> +0.0056; STRICT 162 edges at precision 0.321 / recall 0.076 -> +0.0030. I predicted precision was the binding constraint and the measurement says the opposite: the bridge is NON-WRITING, so a false edge only offers a candidate the salience competition declines while a missing edge removes the only path -- recall binds, and tripling precision halved the gain. It recovers about a third of the +0.0097 the gold arcs are worth; with gold categories the two stack (+0.0129 -> +0.0140, both CI-sep). (7) THE DUAL-ROUTE LEMMA (Pinker/Ullman rule route when the stored route is silent) is board-IDENTICAL (gf3 == gf2 on every field) and slightly LOWERS lemma-key agreement with gold (0.8196 -> 0.8177): the common-noun identity key needs CONSISTENCY, not correctness. (8) THE READABLE-POPULATION REPLICATION: every headline re-measured with the 18 redacted documents dropped -- gold-free common-noun 0.4891 -> 0.5417, margin still +0.0020 CI[-0.0105,+0.0131] not separated; the conclusion is unchanged, the accuracy is not. (9) PATCH VERIFICATION WITHOUT A REPO WRITE: both diffs are EXECUTED end-to-end by a meta-path loader that runs the patched sources with __file__ set to their real repo paths -- 20 module names routed to the patched sources, the reader reads, span_upos aligns with span_toks on every mention, `tagger=None` leaves the mention dict byte-compatible (no span_upos key), resolved_head populated on 140/140 resolutions, and the GUM organ decision layer types mentions and preserves the gold columns as gold_*. (10) TYPE-CONFUSION COUNTS, 18,197 test mentions: type agreement 0.9088, span-head agreement 0.9432, lemma-key agreement 0.8196; gold-name recall 0.8182, gold-common 0.9602, gold-pronoun 0.9108."
files_changed: "experiments/exp_entity_instruments_gold_free_v1.py (the cell: the gold-free decision layer, the seven arms + the hold-one-gold ablations + the tau sweep, the scrambled-gold twin and its identity check, the grep witness, the type-confusion trace, the scrubbed-document detector, the entity-QA diagnosis and the two-scheme repaired QA instrument, --self-test); notes/problems/<slug>/SOLVED.md; notes/problems/<slug>/gum_coref_gold_free_patch.diff (PROPOSED, NOT applied -- experiments/gum_coref.py + exp_board_coref_gum_v1.py + exp_commonnoun_diffhead_anatomy_gum_v1.py; git apply --check CLEAN); notes/problems/<slug>/entity_layer_patch.diff (PROPOSED, NOT applied -- the forward wire's TEN call sites + EntityAliaser.assign + the two mention builders + situation_reader's gold-free resolved_head + space_reader's builder call site + the repaired entity-QA instrument in experiments/exp_situation_model_qa_v1.py + the repaired witness in verification/test_situation_model_qa.py; git apply --check CLEAN, and every patched source EXECUTED end-to-end before proposal); data/exp_entity_instruments_gold_free_v1/*.json (metrics). NO hdlab/ or tools/ file was edited; no board experiment file was edited in place; no asset was touched."
reverify: ".venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --self-test   # organ tags invariant under a scrambled gold column; lemma/number/gender gold-free; ~15s.   THEN the headline:  OMP_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_entity_instruments_gold_free_v1.py --board --arms gold,caps,cat,gf,gf2,gf2_wire,gf2+upos,gf2_twin --tag _reverify   # expect gold coref 0.4681/0.3621 and common 0.5671/0.5412 EXACTLY (the licence for every comparison); gf2 coref 0.4172/0.3202 margin +0.0970 CI-sep; gf2 common 0.4891/0.4876 margin +0.0015 NOT separated; gf2+upos common margin +0.0152 CI-sep; TWIN gf2_twin vs gf2 BYTE-IDENTICAL=True. ~6 min (2 min of it the first tagging pass).   AND the entity-QA diagnosis:  ... --diagnose --docs 8   # expect key_overlap 0 and questions 0 on all 8 documents, 2,532 of 2,648 entities under negative ids.   AND, AFTER entity_layer_patch.diff lands:  .venv/Scripts/python.exe verification/test_situation_model_qa.py   # expect PASS coref: n=200 questions, cluster-named 0.690 > 0.335 & 0.505, GOLD-FREE 0.280 > 0.120, pos-control 88 > 17."
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
gold -- every column gold, gold appos/cop arcs            margin +0.0272
  drop ONLY the gold is-a arcs          (gold_noisa)      margin +0.0175   [-0.0097]
  drop lemma/head/feats/deprel too, keep gold categories  margin +0.0129   [-0.0046]   (gf2+upos)
  drop the gold CATEGORY column as well                   margin +0.0020   [-0.0109]   (gf2)
                                                                           -------
                                                                           -0.0252  (exact)
```
**The three steps sum to the whole margin**, and their order of size is: **the category organ (-0.0109) > the in-text is-a arcs (-0.0097) >> everything else put together (-0.0046)**.

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

**AND THE WITNESS IS GREEN AGAIN**, run against the patched sources (no repo write):

```
PASS coref: n=200 questions; cluster-named (INFORMATIONAL) model=0.690 > recency=0.335 & mostfreq=0.505;
            GOLD-FREE model=0.280 > recency=0.120 (mostfreq=0.235, reported not asserted);
            pos-control 88 > 17
```

The positive control is the one to look at: **the reader resolves 88 antecedents recency misses and loses 17
that recency gets** -- a 5:1 ratio, on the honest population. That is a capability signal the aggregate
accuracy hides.

**Per document, the honest arm** (`head_named` model): Alice 0.950, Persuasion 0.536, Bleak House 0.500, Tess 0.500, Secret Adversary 0.333, Masque 0.100, Secret Garden 0.036, Bartleby 0.000. The two floors are at 0.000 on five of the eight, so the instrument is **not** degenerate -- it is sparse, and the honest reading is that it is under-powered at 8 documents rather than that the reader is at chance.

## 9. HOW THE DIFFS WERE VERIFIED WITHOUT WRITING TO THE REPO

The standing rule that earned itself on 2026-09-14 07:25 is that **a diff which widens a signature must pass the new argument at every call site, or a builder silently ships a different organ**. `parse_litbank_conll` gained `tagger=`; its call sites in `hdlab/` are **four** (`referent_per_np`, `situation_reader` x2, `space_reader`) and in `tools/` **zero** -- **all four are in the diff**. `EntityAliaser.assign` gained `upos=`; its three call sites are in the diff. All **ten** `name_content_tokens` call sites named in the brief are in the diff.

Both patches were then **executed**: a meta-path loader runs the patched sources with `__file__` set to their **real repo paths**, so every `_REPO`/asset path resolves as it would after landing. **20 module names routed to the patched sources (the 19 patched files plus one byte-identical scratch copy of `hdlab/lexical_categories.py` left over from an earlier generator run, which a `diff -q` confirms is identical to the repo's); the reader reads; `span_upos` aligns with `span_toks` on every mention; `tagger=None` leaves the mention dict byte-compatible (no `span_upos` key); `resolved_head` populated on 140/140 resolutions; the GUM organ layer types mentions and preserves the gold columns as `gold_*`.** Nothing in `hdlab/`, `tools/` or `experiments/` was written.

**The patched `gum_coref._self_test` was run too, and it carries the twin as an in-module assertion:**
`GOLD-FREE TWIN: 66 mentions decided identically under a scrambled gold column: True`, with the existing
assertions unchanged (275 docs / 36,332 mentions / 8,400 chains, 3rd-person pronoun anaphora 1.000) -- i.e.
the default `gold` path is byte-compatible.

> **AND EXECUTING IT CAUGHT A REAL BUG IN MY OWN PATCH, which is the whole point of the rule.** The first
> run of the patched witness failed with `{'model': 0.0, 'recency': 0.335, 'mostfreq': 0.505}`: I had handed
> the answer key to `build_coref_questions` but **not** to `SituationQA._answer_coref`, so the informational
> arm still named the model's pick through `_named_clusters(sm)` -- the negative-id map -- and answered
> `None` on all 200 questions. A `git apply --check` would have passed it; only running it did not.

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

## 13. WHY pri 104's WIRE HURTS THE COMMON-NOUN ROW -- a DEFECT IN THE LANDED CAPABILITY, located

The wire is **board-negative on the common-noun row** (`+0.0020 -> -0.0111`) and I did not leave that as a
shrug. `coref._span_head_is_name` carries **its own head rule**:

```python
idx = [i for i, u in enumerate(upos) if u in _NOMINAL_HEADS and i < len(span_toks)]
return upos[idx[-1]] == "PROPN"          # the last NOUN/PROPN of the WHOLE span
```

**But a coref mention span is not one NP run.** It contains PPs, parentheticals and relative clauses, so the
"last NOUN/PROPN" is routinely a PROPN inside a **modifier**. Measured on the **17,010** GUM test mentions:

- the NP-run head and the plain head-final head **disagree on 1,415 mentions (8.3%)**;
- the wire's typing differs from the NP-run-head argmax on **403** -- **241 common -> name** and 162 name -> common.

And the 241 are exactly the predicted class:

| span | NP-run head | what the wire heads on | wire's type |
|---|---|---|---|
| *the environments identified by **Quilis*** | environments (NOUN) | **Quilis** | **name** |
| *a case from **English*** | case (NOUN) | **English** | **name** |
| *a System Under Test ( **SUT** )* | System (NOUN) | **SUT** | **name** |
| *two scale model ( **TSM** )* | model (NOUN) | **TSM** | **name** |
| *the National Library of the Netherlands* | **Library** (PROPN) | Amsterdam | common |

**THE FIX, BUILT AND MEASURED** (readable population, all four arms in one run):

| arm | COMMON-NOUN n / acc / floor / margin | COREF margin | name/common split |
|---|---|---|---|
| gf2 (no wire) | 3024 / 0.5417 / 0.5397 / **+0.0020** | +0.0970 | 2948 / 5653 |
| **gf2_wire -- the wire AS SHIPPED** | 2981 / 0.5344 / 0.5418 / **-0.0074** | +0.0979 | **3027** / 5574 |
| **gf2_wire2 -- the wire given the NP DOMAIN** | 3026 / 0.5423 / 0.5400 / **+0.0023** | +0.0970 | 2943 / 5658 |
| gf2_isa + wire2 (both fixes) | 3026 / **0.5459** / 0.5400 / **+0.0059** | +0.0970 | 2943 / 5658 |

**One line removes the whole of the damage: -0.0074 -> +0.0023.** The fix is carried in
`entity_layer_patch.diff` (`coref._np_domain` + `_span_head_is_name`, with the name TOKENS taken from the
domain too), and unit-checked on the five span shapes above.

> **AND THE DEEPER READING, which is the one strategy should carry.** With the NP domain, the wire's typing
> and the category organ's plain argmax differ on **5 mentions net** out of 17,010 (2943 vs 2948 names).
> **Given the same head, `name_content_tokens(span, upos)` IS `upos[head] == "PROPN"`** -- so on this
> instrument the wire was never going to add anything over reading the organ directly, and everything it
> appeared to do was its head rule. **The wire's value is not on these two rows at all. It is on the LIVE
> reader's entity stream, where the capitalisation rule is degenerate and the count goes from 0 to 150.**

**This is also the honest correction to my own section 3 framing:** I reported the wire as "neutral-to-mixed";
it is neutral-to-mixed *as shipped*, the mixed half has a located cause, and the cause is one line.

## 14. GENERALIZE (checklist item 3) -- EVERY board arm checked for a decision-time gold read

**The good news, and it is real: the gold peek is CONFINED to the coref chain.** Every other board row already
reads the shared frontend at decision time -- the 2026-09-12 `hdlab.frontend` consolidation did its job.

| board row | arm | reads at decision time | verdict |
|---|---|---|---|
| `coref`, `common_noun_coref`, `salience` | `exp_board_coref_gum_v1` -> `gum_coref` | **five gold columns** | ❌ **THE DEFECT** -- fixed by `gum_coref_gold_free_patch.diff` |
| `who_did_what_agent` | `exp_board_agent_slot_ud_v1` | `hdlab.frontend.tagger()` (line 250). Gold `upos`/`deprel` appear ONLY inside `gold_agent_items` -- the answer key | ✅ correct pattern |
| `who_did_what_patient` | `exp_board_patient_slot_v1` | the shared frontend | ✅ |
| `state` | `exp_situation_model_state_qa_v1` | the shared frontend (heads via `HDLAB_HEADS_SOURCE`) | ✅ |
| `wic` | `exp_board_wic_sense_v1` | the live `sm.select_sense` wire | ✅ |
| *(off-board)* | `exp_board_agent_gum_v1` | `up = [t.upos for t in sent_toks]` at lines 148 and **251, commented `# GOLD pos`**, fed into `_pick_idx` -> the CM competition; `_dense_candidates` also selects by gold `upos` | ⚠️ **INFORMATIONAL** -- it is a diagnostic arm, not a published row, but if it is ever promoted it needs the same `decision_source` treatment |

**The pattern worth naming, because it is the fix:** an instrument is honest when the gold columns appear
**only inside the function that builds the answer key** (`gold_agent_items`, `_gold_agents`) and the model is
handed the frontend. `gum_coref` violated it by putting the gold columns on the `Tok` the model then reads;
the patch keeps them on the `Tok` as `gold_*` so the answer key still works and the model cannot reach them.

## 15. EVERY COMPONENT TOUCHED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | what I did with it | BF status as I found it |
|---|---|---|
| `hdlab/lexical_categories` via `hdlab/frontend.Tagger` | **the gold-free instrument's category source** (tags + PROPN posterior) | **BF_SPIRIT** -- count-based generative category model, graded posterior, no gradient. Name recall on mention heads **0.8182**; that number is now the common-noun row's binding constraint |
| `hdlab/morphology` | the gold-free lemma + number, in its own dual-route mode | **BF** (Pinker/Ullman words-and-rules; glass-box morphy port, no nltk at inference) |
| `hdlab/coref.name_content_tokens` | pri 104's landed forward wire, measured through the gold-free rows and on the live entity stream | **capability landed, NOT LIVE** -- ten unwired call sites, now in `entity_layer_patch.diff`. **Its internal head rule is plain head-final and disagrees with the NP-run head** (section 15) |
| `hdlab/coref.EntityAliaser.assign` | widened to carry `upos` (it calls `name_content_tokens` itself) | the name-variant merger; unchanged computation |
| `hdlab/referent_per_np` | **found the lowercasing defect**: the live entity stream cannot type a name at all (0 of 2,123) | **a DEFECT, not a design** -- the organ's name decision is degenerate on the live path |
| `hdlab/online_entity_cluster` / `hdlab/entity_resolver` | **found the id-space defect** that emptied the entity QA (negative online ids vs positive coref ids) | **BF** (Heim file-change + Lewis-Vasishth ACT-R retrieval); the de-leak is correct -- **the INSTRUMENT was stale** |
| `hdlab/situation_reader` | added the additive, gold-free `CorefResolution.resolved_head`; fed the tagger into both mention builders | no decision changed |
| `hdlab/space_reader` | the fourth `parse_litbank_conll` call site, wired so no builder ships a different organ | -- |
| `experiments/gum_coref` | **the instrument**: a `decision_source="organ"` layer; the gold columns move to `gold_*` | was **NOT_BF as an instrument** (five gold reads at decision time); the patch makes the organ arm selectable |
| `experiments/exp_unified_referent_gum_v1.Resolver` | **not modified** -- it is the model under test; its inputs were replaced | **BF** (DRT file-change, ACT-R salience, Ariel accessibility). **Its pronoun pick survives gold-free** |
| `experiments/exp_commonnoun_diffhead_anatomy_gum_v1._appos_copula_isa` | the gold `appos`/`cop` arcs -> a construction detector | **NOT_BF as built** (reads gold arcs); the construction detector is BF but recovers only a third |
| `hdlab/graded_role_assigner` | **deliberately not touched** (pri 108 holds it); named as the more-BF role source in section 12 | -- |

## 16. PRIORITY NEXT STEPS (for strategy)

1. **Decide on the 18 redacted documents** -- one line, and it moves every published GUM number. My recommendation: exclude them and re-publish, because no reader can read `__`; report the excluded count next to every row.
2. **Land `gum_coref_gold_free_patch.diff` and re-publish the coref / common-noun / salience rows gold-free**, retiring `0.4681` / `0.5671` into `reference_retired_claims_never_requote.md` as **gold-split** figures.
3. **Land `entity_layer_patch.diff`** (the wire + the repaired instrument) and run the board A/B; the wire's value is on the entity stream, not on these two rows.
4. **File the arc-labeller `appos`/`cop` lever** against pri 108's labels rung with the number attached (+0.0097 of the common-noun margin).
5. **Do not re-sweep the PROPN posterior mass** on this row -- section 7 is a recorded negative.

# PHASE 7 -- the coordinator's answers applied, and the four mechanisms driven to the bottom

## 17. THE REPUBLISHED BOARD (Q1: exclude the 18 redacted documents) -- before and after, every row

**Answer accepted: it is an instrument defect, not a modelling choice.** Every GUM row, with and without the
18 `GUM_reddit_*` documents whose FORM column is redacted. TEST = odd doc index; the 18 form an even-length
consecutive block, so dropping them preserves the parity of every later document and the test set loses
exactly 9 documents.

| row | arm | **WITH** the redacted docs (n / acc / floor / margin) | **WITHOUT** (n / acc / floor / margin) |
|---|---|---|---|
| **coref (pronoun)** | gold | 3132 / 0.4681 / 0.3621 / **+0.1060** | 3132 / 0.4681 / 0.3621 / **+0.1060** |
| | **gold-free** | 3145 / 0.4172 / 0.3202 / **+0.0970** | 3145 / 0.4172 / 0.3202 / **+0.0970** |
| **common-noun** | gold | 2855 / 0.5671 / 0.5412 / **+0.0259** | 2682 / 0.5690 / 0.5418 / **+0.0272** |
| | **gold-free** | 3915 / 0.4891 / 0.4876 / +0.0015 | **3024 / 0.5417 / 0.5397 / +0.0020** |
| **salience** | gold | 137 / 0.2555 / 0.1971 / +0.0584 | 128 / 0.2656 / 0.2031 / +0.0625 |
| | **gold-free** | 137 / 0.2993 / 0.2190 / +0.0803 | 128 / 0.2734 / 0.2188 / +0.0547 |
| **entity-KB hard-link** | gold | 1307 / 0.4682 / 0.3963 / **+0.0719** | 1307 / 0.4682 / 0.3963 / **+0.0719** |
| | **gold-free** | 1325 / 0.3479 / 0.3079 / +0.0400 | 1325 / 0.3479 / 0.3079 / +0.0400 |

*(CI-separated: gold coref, gold common, gold entity-KB, and the gold-free coref row. Not separated: every
salience cell, the gold-free common-noun row, the gold-free entity-KB row.)*

**AND THE EXCLUSION IS EXACTLY NEUTRAL ON TWO ROWS, FOR A REASON WORTH KNOWING.** The coref and entity-KB
rows are **identical to the digit** with and without. Not luck: `URG._per_type_acc` skips a pronoun unless
its **surface form** is in the third-person list, and a redacted pronoun's surface form is `__`. **The gold
instrument's own surface gate was already excluding those documents silently** -- so the redacted text was
never in the pronoun row, and the two rows it WAS in are the two that move.

**What the exclusion is worth on the row that matters:** the gold-free common-noun population falls
**3915 -> 3024, by 891 items**, while gold's falls only 173. The extra **~718** were redacted `__` tokens the
organ had typed as common nouns -- the same class as the 698 pronoun->common slips. Accuracy rises
**0.4891 -> 0.5417**. **The margin does not: +0.0015 -> +0.0020, still not separated.** The exclusion buys
honesty and a much cleaner population; it does not buy the capability.

**Q2 applied.** The gold-split figures `0.4681` / `0.5671` appear in this document in the table above and in
section 3, and nowhere as a live number; **the gold-free rows are THE board rows**, and strategy files the
gold-split pair into the retired-claims file.

## 18. THE FOUR MECHANISMS, DRIVEN TO THE BOTTOM (the coordinator's probe 1)

### 18a. The common-noun margin: is the residual the ENTITY LAYER's or the CATEGORY ORGAN's?

**The entity layer is not in the dock, and this is a structural fact rather than a measurement: the resolver
is BYTE-IDENTICAL in every arm.** `URG.Resolver(typed_identity=True, bridge=True, bridge_write=False,
type_comparator="typed_spokes")` is constructed the same way for `gold` and for `gf2`; only its INPUTS
change. So nothing that vanishes can be the entity layer's capability -- what vanishes is the quality of what
it is handed. Three independent measurements all land on the category organ:

**(i) The hold-one-gold ablation.** Only the gold category column restores CI-separation
(**+0.0129 [+0.0003,+0.0245]**); lemma/head/feats/deprel recover at most +0.0039 each.

**(ii) The per-component confusion** (18,197 test mentions):

| gold type | -> name | -> common | -> pronoun | recall |
|---|---|---|---|---|
| name | 2786 | 603 | 16 | **0.8182** |
| common | 149 | 5435 | 76 | 0.9602 |
| pronoun | 13 | 802 | 8317 | 0.9108 |

type agreement **0.9088** | span-head agreement **0.9432** | lemma-key agreement **0.8196**

**(iii) The typed-spoke vocabulary gate, which I expected to be a second independent lever and is not.**
`typed_spokes.coref_type_license` returns False for any head it cannot find in WordNet ("an unknown head is
NOT licensed to bridge"), so the lemma key's vocabulary hit-rate is a hard gate on the bridge. Measured on
the 5,653 common-row mentions: **gold lemma in WordNet 0.9282, organ lemma 0.9151** -- 148 gold-only losses
against 74 organ-only, a **net 74 of 5,653 (1.3%)**. Too small to matter. **And the losses are not lemma
errors at all:** the top gold-only losses are `be->is` (42), `be->'re` (9), `be->been` (7), `say->said` (3),
`come->came` (3) -- **mentions whose head the organ typed as a NOMINAL when it is a VERB.** The one probe I
built to look for a second cause found the first cause again.

> **THE ANSWER, PLAINLY: the residual capability is the CATEGORY ORGAN's. The entity layer's resolver is
> unchanged and un-blamed; the common-noun row's +0.0259 was the gold category column (-0.0109) and the gold
> `appos`/`cop` arcs (-0.0097), and the lemma/head/feats/deprel columns together are worth -0.0046.**

### 18b. The wire after the head fix: does it ADD anything, anywhere?

**No. Say it plainly: after the head-domain fix the wire's name DECISION is `upos[head] == "PROPN"`.**
Measured over **17,010** GUM test mentions: the two predicates **agree on 17,005 (0.99971)**. All **5**
disagreements are the same shape and the wire is **wrong** on every one of them:

```
Chiang Kai Shek Memorial Hall Station     argmax=name   wire=common   head=Station   [PROPN x6]
Phoenix Sky Harbor International Airport  argmax=name   wire=common   head=Airport   [PROPN x5]
Jack Alter Fort Lee Community Center      argmax=name   wire=common   head=Center    [PROPN x6]
```

These are long all-PROPN names that `name_content_tokens` rejects because the extracted token list exceeds
`MAX_NAME_TOKENS`. **So the wire is the simpler predicate plus a length cap that misfires.**

> **RECOMMENDATION TO STRATEGY, stated so it can be acted on without re-deriving it: land the SIMPLE form.**
> The name decision on a typed mention is `categories[np_domain_head] == "PROPN"`. What
> `name_content_tokens` genuinely contributes is **not the decision but the TOKEN EXTRACTION** -- which
> tokens of the span are the name, which is what the `EntityAliaser` needs to merge `Sir Leicester` with
> `Sir Leicester Dedlock`. Keep it for that; do not treat it as a name classifier.

### 18c. The lowercased `span_toks`: the defect is ONE LEVEL UP, and it is bigger

I set out to measure what restoring the case in `referent_per_np._mk_referent` recovers. **It recovers
exactly nothing, and the reason is the finding.**

| decider, 3,869 referent mentions on 8 LitBank docs | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| **today** -- caps rule on the lowercased head | 0 | 0 | 274 | 0.0000 | 0.0000 | **0.0000** |
| **restore the case in `_mk_referent`** | 0 | 0 | 274 | 0.0000 | 0.0000 | **0.0000** |
| **the forward wire** (the organ's category) | 80 | 70 | 194 | 0.5333 | 0.2920 | **0.3774** |

**Because the case is already gone before `_mk_referent` ever runs.** `hdlab/scene_segment.parse_conll_sentences`
-- **the live reader's ONLY sentence source**, used by `situation_reader.read()` and by
`referent_per_np_source` -- is:

```python
def parse_conll_sentences(path: str) -> List[List[str]]:
    """Return the document's sentences as lowercased-token lists (sent_idx-aligned)."""
    ...
            cur.append(cols[3].lower())
```

**Three consequences, none of them previously recorded:**

1. `_mk_referent`'s `.lower()` is **redundant**; restoring it is a no-op (measured above).
2. `referent_per_np.frame_heads` carries a documented capitalisation cue -- *"a mid-sentence CAPITAL = a
   likely proper name the tagger mis-class'd"*, `cap = (i > 0 and w[:1].isupper())` -- which **can never
   fire** on the live path. A second dormant arm, found by this probe.
3. **The category organ itself is tagging lowercased text on every reader path**, so its shape cue
   (`lexical_categories.word_shape` / `word_shape_rich`) is answering a question the input cannot pose.

> **THE PLAIN STATEMENT: on the reader's path, capitalisation is destroyed at the sentence source, so every
> capitalisation-based cue anywhere downstream of `parse_conll_sentences` is dead -- and the forward wire is
> therefore not the best repair of the name decision on that stream, it is the ONLY one available.**

### 18c-bis. A PROPERTY OF MY OWN DIFF THAT FALLS OUT OF 18c, and strategy should know it

`parse_litbank_conll(tagger=...)` tags the tokens it reads **from the CoNLL file**, which are **raw-cased**.
The reader passes `_CachedTagShim(self)`, and `_cached_tag` keys its memo on `tuple(toks)` -- so a raw-cased
sentence is a **different cache key** from the lowercased one the rest of the reader uses. Two consequences,
both stated rather than discovered later:

1. **The coref-mention stream gets CASED tags while every other reader path stays lowercased.** That is an
   accuracy *improvement* for `span_upos` (the organ at 0.8622 PROPN F1 instead of 0.4546) but it is an
   **inconsistency**: the same document is tagged under two different casings within one read.
2. **It costs one extra tagging pass per read** (the cased sentences miss the warm cache).

**Both resolve the moment `lower=False` lands** -- the two streams become the same text and the same cache
key. Until then the inconsistency is in the direction of *more* accuracy for the mention typing, not less,
which is why I left it rather than lowercasing the mention tokens to match. **The `referent_per_np` stream is
unaffected and its wire genuinely runs on lowercased tags** -- which is what the 0 -> 150 measurement in
section 18c used, so that number is faithful to the shipped path.

### 18d. The negative ids: DESIGN, not defect -- and my repair keeps the intent

Answered from the source rather than inferred. `hdlab/online_entity_cluster.py`'s module docstring ends:

> *"WIRE NOTE (for situation_reader): give each online file a FRESH NEGATIVE-INTEGER id, NOT a `CN:` string --
> `_read_world_state`/`_resolve_commonnouns` do `rc >= 0` and crash on a str."*

and states the intent: *"NO gold coreference is read in any clustering DECISION (`m["cluster"]`, the gold eid,
is used ONLY by scorers, never here)."* The guard it names is real: `situation_reader.py:2733`,
`if rc is not None and rc >= 0`.

**So the negative integer was chosen deliberately and for two good reasons** -- it must be an `int` (a `CN:`
string crashes that guard) and it must be **unmistakable for a gold cluster id**, so that no consumer can
silently treat an online file as a gold chain. **The negativity is precisely a guard against the confusion my
instrument fell into**, and the de-leak is correct.

**My repair keeps the intent and does not weaken it.** It touches no clustering decision; it names the
question's gold chain from the GOLD MENTION STREAM (the answer key, which is what the question asks about)
and the model's answer from the reader's OWN files. If anything it *completes* the de-leak: the readout it
replaces (`_named_clusters(sm).get(resolved_cluster)`) was itself a gold read that the 2026-09-09 de-leak had
not noticed.

> **THE GENERAL LESSON, worth carrying: a sentinel that changes TYPE fails loudly; a sentinel that changes
> RANGE fails silently.** The author anticipated the `str` crash and guarded it. The int-in-a-disjoint-range
> case produced `None` on every lookup and ran red for five days with every arm scoring 0.0.

## 19. CONVERT (the coordinator's probe 2) -- the honest live common-noun number, and the lever that moves it

**THE HONEST LIVE NUMBER, with the gold-free rows as the ruler and the redacted documents excluded:**

> **common-noun coref: model `0.5417`, strongest gold-free floor `0.5397` (same-head string identity),
> margin `+0.0020` CI `[-0.0105, +0.0131]` -- NOT separated, n = 3,024.**

**Every lever I could build, measured on that ruler, in one run:**

| arm | model / floor | **margin** | CI | sep? |
|---|---|---|---|---|
| gf2 (the instrument) | 0.5417 / 0.5397 | +0.0020 | [-0.0105,+0.0131] | ✗ |
| + the head-domain wire fix | 0.5423 / 0.5400 | +0.0023 | [-0.0101,+0.0134] | ✗ |
| + the is-a construction detector (loose) | 0.5453 / 0.5397 | +0.0056 | [-0.0065,+0.0168] | ✗ |
| + is-a **strict** (higher precision) | 0.5427 / 0.5397 | +0.0030 | [-0.0097,+0.0140] | ✗ |
| + is-a **+ type-stating connectives** (isa3) | 0.5460 / 0.5397 | +0.0063 | [-0.0058,+0.0172] | ✗ |
| + **connectives and a wider gap** (isa4) | 0.5470 / 0.5397 | +0.0073 | [-0.0048,+0.0181] | ✗ |
| **isa4 + the head-domain fix (best stack)** | **0.5476 / 0.5400** | **+0.0076** | [-0.0046,+0.0185] | ✗ |
| *reference:* gold columns, is-a seed off | 0.5593 / 0.5418 | +0.0175 | [+0.0040,+0.0295] | ✓ |
| *reference:* gold columns, is-a seed on | 0.5690 / 0.5418 | +0.0272 | [+0.0138,+0.0399] | ✓ |

**NO SINGLE LEVER IN MY REMIT MOVES IT CI-SEPARATED, and the stack of all three reaches +0.0076 -- 28% of
the gold margin.** The recall mechanism holds for a fourth time (strict 0.0030 < loose 0.0056 < connectives
0.0063 < wider gap 0.0073): on a **non-writing** bridge a false edge is nearly free and a missing edge is
fatal.

### 19a. AND THEN THE PAIRED SUBPOPULATION SHOWS THE CAPABILITY IS THERE

Both arms restricted to the **28,688 of 34,001 mentions (84.37%)** on which the organ reproduces the gold
**type AND head AND lemma**. The restriction is arm-independent, so the two arms are scored on **identical
items** (n = 2,281, identical floor, identical name/common/pronoun split 2266/4525/7554):

| arm | common-noun model / floor | **margin** | CI | sep? |
|---|---|---|---|---|
| **gold@agree** | 0.6094 / 0.5831 | **+0.0263** | [+0.0133,+0.0389] | **✓** |
| **gold-free@agree** | 0.6024 / 0.5831 | **+0.0193** | [+0.0057,+0.0318] | **✓ CI-SEPARATED** |

and the pronoun row likewise (gold@agree +0.1032, gold-free@agree +0.0975, both separated).

> **THE CONVERSION, STATED HONESTLY: the gold-free common-noun capability IS CI-separated -- on the 84% of
> mentions the category organ types correctly, where it recovers 73% of gold's margin (+0.0193 against
> +0.0263). It is destroyed on the full population by the 15.6% it gets wrong.** That is not a different
> answer from section 18a, it is the same answer measured a fourth way, and it is the strongest form of it:
> **the entity layer's capability is real and the category organ is the whole of the gap.**
>
> **CAVEAT, stated rather than buried:** restricting the mention stream shortens the referent history, so
> these are not the same task as the full row. The restriction is applied identically to both arms and the
> floor is identical (0.5831) in both, which is what makes the comparison fair; but the absolute numbers are
> not comparable to the unrestricted rows.

**The arithmetic of the remaining gap, so strategy can price it:** moving the organ's joint (type+head+lemma)
agreement from **0.8437** toward 1.0 is worth up to **+0.0173** of common-noun margin (0.0020 -> 0.0193).
That is 2.3x everything my three levers together bought.

### 19b. THE BIGGEST ORGAN LEVER IS NOT ON THIS BOARD AT ALL -- and it is one line

From section 18c: the live reader's only sentence source lowercases every token. **Measured cost to the
category organ, 127,919 GUM test tokens, same organ, same text, the only difference being case:**

| input the organ receives | PROPN P | PROPN R | **PROPN F1** | all-tag accuracy |
|---|---|---|---|---|
| **cased** (what the GUM board instrument feeds it) | 0.9050 | 0.8232 | **0.8622** | **0.9302** |
| **lowercased** (what the LIVE READER feeds it) | 0.9417 | **0.2996** | **0.4546** | **0.9027** |
| | | | **-0.4076** | **-0.0275** |

**The organ finds 2,149 of 7,173 proper nouns instead of 5,905 -- it misses 5,024 names, 70% of them -- and
loses 2.75 points of accuracy on EVERY token, for EVERY consumer of the reader.** Tag agreement between the
two runs is 0.9637, so one token in 28 changes category purely because the reader threw the case away.

**For scale: pri 104's entire brief fought for +0.1921 token F1 on the name decision. Un-lowercasing the
reader's input is worth +0.4076 PROPN F1 -- more than double -- and it is one line.**

> **AND IT MEANS THE BOARD'S GOLD-FREE ROWS ARE STILL OPTIMISTIC.** I made the instrument gold-free; I did
> not make it reader-faithful. The GUM board hands the organ **cased** forms (`gum_coref` keeps `cols[1]`
> raw), so the gold-free rows above are scored with the organ at **PROPN F1 0.8622**, while the live reader
> runs it at **0.4546**. The `gf2low` arm measures that remaining gap directly.

**WHY I AM NOT FLIPPING IT MYSELF, and what strategy needs to flip it in one step.** `parse_conll_sentences`
is consumed by **five** call sites in `hdlab/` -- `situation_reader:4368`, `referent_per_np:112`,
`space_reader:246`, `causation_typing:840`, and (documented as lowercased) `crosstype_live_adapter:103`,
whose docstring says *"the reader's per-sentence tokens (`parse_conll_sentences`, lowercased ...)"*, i.e. at
least one consumer states the assumption in writing. Changing the default changes the input of every reader
consumer at once and needs a board A/B, which is strategy's. **The diff therefore adds
`parse_conll_sentences(path, lower=True)` with the CURRENT default -- byte-identical -- so the flip is one
argument away and the number above is attached to it.**

## 20. THE ARC-LABELLER `appos`/`cop` LEVER, BRIEF-READY (the coordinator's Q3)

**FOR:** the labels rung (pri 108's successor). **REACH: +0.0097 of the board's common-noun margin**, measured
by direct ablation (`gold` +0.0272 -> `gold_noisa` +0.0175, same population, doc-paired bootstrap).

**THE POPULATION.** GUM, TEST = odd doc index, 18 redacted documents excluded; the common-noun coref row,
n = 3,024 mentions over 128 documents. The consumer is `URG.Resolver(typed_identity=True, bridge=True,
bridge_write=False, type_comparator="typed_spokes")` -- the landed Q111 non-writing type bridge.

**THE MECHANISM, and why it is a LABELS problem and not a construction problem.** The bridge is seeded by
`exp_commonnoun_diffhead_anatomy_gum_v1._appos_copula_isa`, which reads the gold **`appos`** and **`cop`
arcs** to extract in-text is-a edges ("Kim, the doctor" / "Kim is a doctor"). Those edges let a definite with
no same-head antecedent bridge to a type-compatible prior referent. **683 gold edges on 80 documents.**

**WHAT I BUILT INSTEAD, AND EXACTLY HOW FAR IT GETS** (this is the evidence that the lever belongs to the
labeller, not to a surface detector):

| gold-free detector | edges | shared with the 683 gold edges | precision | recall | margin recovered |
|---|---|---|---|---|---|
| strict (name + determiner) | 162 | 52 | 0.321 | 0.076 | +0.0010 |
| loose (adjacent nominal runs, comma or BE) | 949 | 113 | 0.119 | 0.165 | +0.0036 |
| + type-stating connectives | -- | -- | -- | -- | +0.0043 |
| + connectives and a wider gap | -- | -- | -- | -- | +0.0053 |
| **the gold arcs** | **683** | -- | 1.0 | 1.0 | **+0.0097** |

**Four points of a monotone recall curve and it plateaus at ~55% of the gold seed.** The residual is the part
a surface detector cannot reach: `appos` and `cop` are **syntactic relations**, and the constructions that
realise them are not separable from ordinary adjacency by word order and commas alone ("the field is data" is
an adjacent nominal pair with a copula and is not a type statement).

**THE ACCEPTANCE TEST, falsifiable:** a gold-free `appos`/`cop` labeller whose edges, substituted into
`_appos_copula_isa`, move the board's gold-free common-noun margin from **+0.0076** (my best stack) to
**>= +0.0150 with a CI excluding zero**, on the readable GUM population, with the random-bridge twin losing.

**RELATED FINDING THE LABELS RUNG SHOULD HAVE:** on a **non-writing** bridge, **recall binds and precision is
nearly free** -- a false edge only offers a candidate the salience competition declines, a missing edge
removes the only path. I built the high-precision arm first and it was half as good. A labeller tuned for
this consumer should be tuned for recall.

## 21. OPPORTUNITIES BEYOND THE BAR, AND ALTERNATE PATHS

**OPPORTUNITIES (ranked by measured reach):**

| # | opportunity | measured reach | whose |
|---|---|---|---|
| 1 | **Stop lowercasing the reader's sentence source** | **+0.4076 PROPN F1, +0.0275 all-tag accuracy, on every reader consumer** | one line + a 5-call-site audit; needs a board A/B |
| 2 | Raise the organ's joint type+head+lemma agreement from 0.8437 | up to **+0.0173** of common-noun margin | the category-organ chain (pri 104/107/110) |
| 3 | A gold-free `appos`/`cop` labeller | **+0.0097** of common-noun margin | the labels rung (section 20) |
| 4 | Land the SIMPLE name predicate (`categories[head] == "PROPN"`) instead of the wire as a classifier | removes 5 wrong rejections / 17,010 and a needless dependency | one line in the diff |
| 5 | Wake `referent_per_np.frame_heads`' capitalisation cue | currently **can never fire**; unmeasured until (1) lands | follows (1) |
| 6 | The is-a connective stack | +0.0056 over the instrument | in the diff, default off |

**ALTERNATE PATHS, similarly or MORE brain-foundational than what I shipped:**

1. **Heads from the attachment arm's parse, not the NP-run rule.** The brain has one attachment competition,
   not a separate "NP head rule". Span-head agreement is 0.9432 today; `+head` bounds it at +0.0139 of the
   coref margin. ~50 min of GUM parsing per arm.
2. **Roles from the Competition-Model role assigner** (`graded_role_assigner.coarse_roles`) rather than the
   word-order cue alone -- the Competition Model is word order **plus animacy plus agreement in competition**.
   I shipped only the word-order cue because the others need heads. Strictly more BF. *(pri 108 holds the file.)*
3. **Let the reader detect its own mentions.** The instrument still takes the treebank's spans. `referent_per_np`
   already finds its own referents; the honest next instrument scores those against the gold chains.
4. **Score the two arms per item on the intersection** rather than as margins over two different populations.
   Section 19a is the first step; a full per-item paired test over the mention intersection is better still.
5. **Give the category organ the case cue it is built for.** `lexical_categories` carries `word_shape` /
   `word_shape_rich`; on the reader's path those cues are answering a question the input cannot pose. This is
   opportunity (1) seen from the organ's side, and it is the most brain-foundational of all of them: a reader
   that cannot see that a word is capitalised is not a reader with a weak cue, it is a reader with a
   **destroyed input channel**.

## 22. THE READER-FAITHFUL ARM -- and it REFUTES the common-noun row as a cross-arm instrument

The gold-free instrument feeds the category organ **cased** GUM forms. **The live reader feeds it lowercased
text** (section 18c). So the rows I published are still not reader-faithful, and `gf2low` closes that gap by
handing the organ exactly what the reader gets.

| arm (readable population) | coref n / acc / floor / margin | common n / acc / floor / margin | NAME mentions typed |
|---|---|---|---|
| **gf2** -- organ on CASED input | 3145 / 0.4172 / 0.3202 / **+0.0970** ✅ | 3024 / 0.5417 / 0.5397 / +0.0020 ❌ | 2,948 |
| **gf2low** -- organ on the reader's LOWERCASED input | 3145 / 0.4108 / 0.3148 / **+0.0960** ✅ | 4212 / 0.5940 / 0.5893 / +0.0047 ❌ | **1,128** |
| **gf2_isa4low** -- same + the connective is-a seed | 3145 / 0.4108 / 0.3148 / **+0.0960** ✅ | 4212 / 0.5997 / 0.5893 / **+0.0104 [+0.0007,+0.0199]** ✅ | **1,128** |

**Two things follow and the second one is more important than the first.**

**(1) THE PRONOUN ROW DOES NOT CARE, for the fifth time.** Margin `+0.0970 -> +0.0960` while the name
population collapses by **62%** (2,948 -> 1,128, exactly what a PROPN recall of 0.2996 predicts). The pronoun
pick's load-bearing inputs are closed-class, so destroying the name decision barely touches it. This is the
same structural fact as section 10, now measured from a fifth direction.

**(2) THE COMMON-NOUN ROW GOES *UP* AND BECOMES CI-SEPARATED WHEN THE CATEGORY ORGAN IS MADE WORSE -- so its
cross-arm margin is not a safe comparison, and I am not claiming the +0.0104 as a win.**

> Making the typing **worse** (lowercasing the input) moves the gold-free common-noun margin from `+0.0020`
> to `+0.0047`, and with the is-a seed to **`+0.0104`, CI-separated** -- the only CI-separated gold-free
> common-noun result on a full population in this entire session. **It is an artefact of the row's
> construction, not a capability.** The common-noun population is *defined by the decision under test*: when
> the organ stops calling things names, ~1,800 name mentions fall into the common-noun row, and names are
> easy to resolve by repeated surface string, so the model **and** the floor both rise (0.5417/0.5397 ->
> 0.5940/0.5893) and the larger n narrows the CI.
>
> **CONCLUSION, and it is a methodological one: "margin over the row's own recomputed floor" is NOT comparable
> across arms whose typing differs.** pri 104 flagged the population shift as a caveat; this measures it and
> shows it can invert the verdict. **The instrument that survives the critique is the PAIRED SUBPOPULATION of
> section 19a** -- identical items, identical floor, and there the honest answer is gold `+0.0263` vs
> gold-free `+0.0193`, both CI-separated.

**AND IT DEFLATES MY OWN HEADLINE LEVER, which I would rather say myself.** The reader's lowercasing costs the
category organ **-0.4076 PROPN F1** and **-0.0275 all-tag accuracy** -- those numbers stand, they are measured
at the organ against gold, and they are population-independent. **But on these two board rows it is nearly
invisible** (coref -0.0010 of margin; common-noun uninterpretable for the reason above). The lever is real and
large *at the organ and at the entity layer*; **the board's two entity rows are not the instrument that can
see it**, exactly as pri 104 found for the name decision itself. Anyone landing the case flip should expect
the board not to move and should measure it where it lands: the entity files, the aliaser, the cross-type
experiencer bind, who-did-what.

## 22b. THE CASE FLIP RUN END-TO-END ON THE READER -- it is SAFE, and it is NEUTRAL on coref

`lower=False` applied at the reader's own call sites, both arms on the same 8 LitBank documents, patched
sources executed with no repo write:

| | weighted `coref_acc` (570 targets) | entities | with heads | NAME mentions typed | coref questions |
|---|---|---|---|---|---|
| **as it ships** (`lower=True`) | **0.6421** | 2,640 | 2,524 | 310 | 200 |
| **`lower=False`** | **0.6421** | **2,748** | **2,632** | 310 | 200 |

**THREE HONEST READINGS.**

1. **NOTHING BROKE.** No crash, no misalignment, no consumer that assumes lowercase failed. That is the
   question that mattered before proposing the flip, and the answer is clean.
2. **THE READER'S PRONOUN COREF DOES NOT MOVE -- 0.6421 to four decimals.** The sixth independent
   confirmation that the pronoun pick's load-bearing inputs are closed-class and do not depend on the name
   decision. Anyone expecting the case flip to lift coref should not.
3. **THE ENTITY LAYER GROWS BY 108 REFERENT FILES (+4.1%), all of them with surface heads** (2,524 -> 2,632).
   That is where the case lands: `referent_per_np._content_head_positions` only opens a referent for a token
   the organ tags NOUN/PROPN, so restoring case finds 108 content heads it was missing on 8 documents -- and
   `frame_heads`' mid-sentence-CAPITAL cue can fire again.

> **ONE NUMBER IN THAT TABLE MUST NOT BE MISREAD, and it is my own diff's doing.** "NAME mentions typed" is
> **identical (310)** because it is counted on the **coref-column** stream, which under my patch is already
> tagged from the RAW-CASED CoNLL tokens (section 18c-bis). It *cannot* move with the flip. The stream the
> flip actually helps is `referent_per_np`, and that is the +108 column.

**SO THE FLIP'S CASE RESTS ON THE ORGAN-LEVEL NUMBER (-0.4076 PROPN F1, -0.0275 all-tag) AND THE +4.1% ENTITY
LAYER, NOT ON ANY COREF ROW.** It is safe to A/B and it should be A/B'd against the consumers that read the
entity layer -- the aliaser, the crosstype experiencer bind, who-did-what -- not against coref.

## 23. IS THE SESSION EXHAUSTED? -- the honest answer, lever by lever

**From this seat, on this brief's remit: YES, and here is the ledger that says so.** Every lever I can build
and measure without stepping into another brief's file or another session's decision has been built and
measured; what remains is either (i) bounded by arithmetic, (ii) owned by a named organ elsewhere, or
(iii) a decision that needs a board A/B, which is strategy's.

| lever | status | why it is closed from here |
|---|---|---|
| the five gold columns -> live organs | **BUILT** | twin byte-identical, twice |
| the NP-run head | **BUILT** | span-head agreement 0.9432; `+head` bounds the residual at +0.0139 coref |
| per-predicate word-order roles | **BUILT** | part of gf -> gf2 |
| dual-route number | **BUILT** | in gf2 |
| dual-route lemma | **BUILT, NULL, EXPLAINED** | the identity key needs consistency, not correctness |
| the posterior-mass sweep | **BUILT, NEGATIVE, EXPLAINED** | accuracy and floor rise together at every tau |
| is-a: strict / loose / connectives / wider gap | **BUILT x4** | monotone in recall, plateaus at +0.0076; the rest is a LABELLER |
| the wire's head-domain defect | **BUILT + FIXED + MEASURED** | -0.0074 -> +0.0023; and the wire is then the simple predicate |
| restore the case in `_mk_referent` | **BUILT, NULL, EXPLAINED** | the case is gone one level up |
| the entity-QA id-space defect | **LOCATED + REPAIRED + WITNESSED** | 0 -> 200 questions, witness green twice |
| the paired-subpopulation conversion | **BUILT, CI-SEPARATED** | +0.0193 [+0.0057,+0.0318] where the organ is right |
| the reader's lowercasing | **LOCATED + MEASURED + PROPOSED** | -0.4076 PROPN F1; flipping it needs a board A/B |
| the category organ's 15.6% | **PRICED, NOT MINE** | worth +0.0173; pri 104 / 107 / 110's chain |
| a gold-free `appos`/`cop` labeller | **PRICED + BRIEF-READY** | +0.0097; section 20; the labels rung's |
| heads from the attachment arm's parse | **NOT BUILT** | ~50 min/arm; bounded at +0.0139; named as alternate path 1 |
| roles from `graded_role_assigner` | **NOT BUILT** | pri 108 holds the file this session |

**THE TWO THINGS I WOULD DO NEXT IF THE REMIT WERE WIDER**, in order, both already priced above: flip
`lower=False` behind a board A/B (**+0.4076 PROPN F1** at the organ), and give the common-noun bridge a real
`appos`/`cop` labeller (**+0.0097**). Neither is a solver's call to land.

**WHAT I GOT WRONG IN THIS SESSION, recorded because the corrections were the useful part:**

1. I predicted **precision** would bind the is-a detector. **Recall binds** -- the strict arm scored half as
   well. The mechanism (a non-writing bridge makes a false edge nearly free) is now measured four times.
2. I reported pri 104's wire as "neutral-to-mixed". It is neutral-to-mixed **as shipped**, and the mixed half
   was a **head-domain bug** that one line removes -- after which the wire is not a classifier at all.
3. I set out to fix the lowercased `span_toks` in `_mk_referent`. That fix is a **no-op**; the defect is one
   level up and is **forty times larger** than the one I was aiming at.
4. My frontmatter mixed two populations in the margin decomposition; corrected, and the corrected version
   sums exactly.
5. My first `gf2low` arm returned numbers identical to its control -- a **broken arm, not a null result** --
   and I caught it only because "identical to the digit" is not something a real switch can do.

**THE ONE SENTENCE I WOULD PUT ON THE BOARD:** *the board's two entity rows were being graded with five gold
columns and eighteen unreadable documents; gold-free, the pronoun-coref capability survives intact, the
common-noun one survives only where the category organ is right -- and the largest single thing standing
between the reader and its own category organ is that the reader lowercases its input before the organ ever
sees it.*

## 24. A CONCURRENT INTEGRATION LANDED MID-SESSION -- and here is the control that says my numbers hold

At **09:11:41** strategy committed pri 104's entity prior (`47942dc00`), which changed **`hdlab/lexical_categories.py`
(+328 lines), the live category asset `lexical_categories_counts_v1.json`, and `hdlab/situation_reader.py`
(+6 lines, the passage-boundary `new_document` wire)** -- i.e. **the very organ every gold-free arm in this
document reads.** My runs straddle it: everything up to `board_arms_convert.json` (09:07) and
`probe_case.json` (09:06) ran on the OLD organ; `board_arms_lower2.json` (09:18) ran on the NEW one.

**THE CONTROL IS FREE, because `gf2` was re-run in both.** Comparing the `gf2` record of the 09:03 publication
run with the `gf2` record of the 09:18 run, every field except elapsed time:

```
gf2 arm BYTE-IDENTICAL across the pri-104 integration (09:03 run vs 09:18 run): True
```

**Identical coref row, identical common-noun row, identical salience, identical entity-KB, identical
2948/5653/8409 mention-type split.** pri 104's own landing note says the board is byte-identical and the
probe moves UPOS 0.9312 -> 0.9313; that is consistent with what I measure here from the other side. **So
every number in this document is comparable, and the two diffs still `git apply --check` clean against the
post-integration tree (re-checked after the landing).**

*Recorded because it was luck that I had a repeated arm to check with -- a solver measuring a live organ
while another session integrates into it should re-run one arm on purpose, not hope one overlaps.*

## GAPS -- steps not performed, and not worked around

1. **The span head from the attachment arm's real parse was NOT measured.** The NP-run rule is a stand-in
   (span-head agreement with gold 0.9432). A full GUM parse is ~50 minutes per arm and I chose six cheaper
   levers instead. `gf2+head` bounds what it could be worth: **+0.0139 of the coref margin**, +0.0010 of the
   common-noun margin.
2. **Roles from `graded_role_assigner` were NOT measured** -- pri 108 holds that file this session, so I used
   the Competition Model's word-order cue alone. Strictly less than the full cue competition.
3. **Mention DETECTION is still gold.** The instrument types the treebank's mention spans; it does not find
   its own. Defensible as the instrument convention, and named as alternate path 3.
4. **A per-item paired comparison on the intersection was not built.** The gold and gold-free arms are
   compared as margins over their own floors on populations that differ by ~1,000 items, which is the board's
   own convention and weaker than a paired test.
5. **A `rm` of one stray scratch file was DENIED by the permission system** and I left it undone rather than
   route around it; a `diff -q` confirms the file is byte-identical to the repo's, so it changed nothing in
   the verification. Verbatim: *"Permission to use Bash with command rm -f
   ".../scratchpad/patchtree/hdlab/lexical_categories.py" && echo removed; cat ".../tasks/bdwklnbes.output"
   has been denied."*
6b. **A PHASE-7 RUN WAS INVALID AND I CAUGHT IT BY LOOKING AT THE ARMS.** The first `gf2low` run returned
   numbers **byte-identical** to `gf2`, which is exactly what a working lowercasing switch could not do. The
   switch was inert (the edit that lowercases the tagger's input had silently not applied). Fixed, asserted
   live (`32 of 752 tags differ between cased and lowercased input` on one document), and re-run. **Recorded
   because an arm that matches its control to the digit is evidence of a broken arm, not of a null result** --
   and the first table I would have published said "the reader's lowercasing costs the board nothing".

6. ~~The final confirmatory witness re-run was still in flight at hand-off.~~ **CLOSED -- it landed and it is
   GREEN, with numbers BYTE-IDENTICAL to the pre-head-domain run:** `n=200 questions; cluster-named
   (INFORMATIONAL) model=0.690 > recency=0.335 & mostfreq=0.505; GOLD-FREE model=0.280 > recency=0.120
   (mostfreq=0.235); pos-control 88 > 17`. **The prediction I recorded in advance held**: the head-domain
   change touches only spans carrying a PP or a relative clause, and on the raw-cased LitBank coref stream
   capitalisation already resolved those, so the wire's decision there does not move. Both witness runs
   (pre- and post-head-domain) and both full structural verifications are green.

## SUBMISSION PROMPT

```
pri 109 -- the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free -- SOLVED (PARTIAL), ready for strategy.

Read notes/problems/the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free/SOLVED.md in full, then:

1. It was FIVE gold columns, not one (upos, lemma, feats, head, deprel), plus 18 GUM documents whose
   FORM column is redacted to underscores. The scrambled-gold twin is byte-identical, so the gold-free
   arm is proven gold-free.
2. Publish the gold-free rows and retire the old ones: COREF 0.4681/0.3621 -> 0.4172/0.3202 (margin
   +0.1060 -> +0.0970, STILL CI-separated -- the pronoun capability is real); COMMON-NOUN
   0.5671/0.5412 -> 0.4891/0.4876 (margin +0.0259 CI-sep -> +0.0015 NOT separated -- the win was the
   gold columns). SALIENCE 0.2555 -> 0.2993, neither separated.
3. Two diffs, both `git apply --check` CLEAN and both EXECUTED end-to-end before proposal:
   gum_coref_gold_free_patch.diff (the instrument) and entity_layer_patch.diff (pri 104's wire at all
   ten call sites + the two mention builders + the repaired entity QA + its witness).
4. Decide the 18 redacted documents (`load_docs` already declares `exclude_scrubbed=True` and ignores it).
5. File the arc-labeller appos/cop lever against pri 108 with its number: +0.0097 of the common-noun margin
   (section 20 is brief-ready: population, mechanism, the four-point recall curve, the acceptance test).

PHASE 7 ADDED FOUR THINGS THAT OUTRANK THE ORIGINAL BARS:
6. THE READER THROWS THE CASE AWAY at its only sentence source (scene_segment.parse_conll_sentences does
   cols[3].lower()). Cost to the category organ, 127,919 GUM tokens: PROPN F1 0.8622 -> 0.4546 (-0.4076; it
   misses 70% of proper nouns) and -0.0275 all-tag accuracy on EVERY token for EVERY reader consumer. The
   diff adds `lower=True` (byte-identical) and passes it explicitly at all four hdlab call sites. FLIPPING IT
   IS THE HIGHEST-VALUE ITEM IN THIS WHOLE AREA and it needs a board A/B, which is yours.
7. THE CAPABILITY IS REAL: on the 84.4% of mentions the organ types correctly, the GOLD-FREE common-noun
   margin is +0.0193 CI[+0.0057,+0.0318] CI-SEPARATED (gold +0.0263). The category organ is the whole gap.
8. AFTER THE HEAD FIX THE WIRE IS EXACTLY upos[head]=="PROPN" (agrees on 17,005/17,010; wrong on all 5
   exceptions). LAND THE SIMPLE FORM; keep name_content_tokens for TOKEN EXTRACTION only.
9. The negative-id re-keying is a DESIGN (online_entity_cluster's own docstring), not a defect; my repair
   keeps its intent.
```
