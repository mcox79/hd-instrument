---
problem: the_mention_typer_reads_a_three_valued_argmax_so_385_category_corrections_reach_82_of_17010_mentions_give_it_the_graded_posterior_and_the_file_card_evidence
status: PARTIAL
bar: "The typer reads the graded posterior + the card evidence (one organ path, both the reader's stream and the board loader); typing F1 per type up CI-separated vs the argmax on GUM test; coref / common-noun rows not down (up on the paired subpopulation CI-separated or a counted reason); every consumer classified; twin (posterior rows shuffled across mentions) at floor -- OR a numbered located negative naming the consumer that cannot read a graded type and why."
result: "THE TYPING RUNG IS SOLVED CI-SEPARATED AND THE DOWNSTREAM READ IT WAS SUPPOSED TO UNLOCK DOES NOT MOVE -- both measured, and the brief's own premise is refuted with a number. (1) TYPING, GUM TEST (128 documents / 127,919 tokens / 17,010 mentions), operating point chosen on the TRAIN half, doc-paired bootstrap 2,000, the gold mention TYPE+HEAD as the answer key: type accuracy 0.9506 -> 0.9608, +0.0103 CI[+0.0067,+0.0139] CI-SEPARATED; macro F1 0.9352 -> 0.9496, +0.0143 CI[+0.0097,+0.0194] CI-SEPARATED; NAME F1 0.8907 -> 0.9171, +0.0264 CI[+0.0178,+0.0362] with recall 0.8420 -> 0.8855 AND precision UP 0.9455 -> 0.9510; COMMON F1 0.9262 -> 0.9420, +0.0158 CI[+0.0105,+0.0211]; PRONOUN F1 +0.0009 CI[-0.0009,+0.0028] (flat, not down); span-head accuracy 0.9462 -> 0.9490. THROUGH THE PROPOSED DIFF'S OWN SOURCE, exec'd into the live modules with the real `gum_coref.load_docs` path, both loaders in ONE process: type accuracy +0.0089 CI[+0.0057,+0.0123], macro F1 +0.0122 CI[+0.0081,+0.0166], name F1 +0.0216 CI[+0.0140,+0.0303], common F1 +0.0137 CI[+0.0089,+0.0186], head accuracy +0.0028 CI[+0.0012,+0.0045] -- so the measured organ IS the proposed organ. (2) WHAT CARRIES IT, decomposed on the same population: marginalise-then-decide ALONE +0.0012 (n.s.), the graded head ALONE +0.0011 (n.s.), the two together +0.0022 CI[+0.0005,+0.0040] (separated), the Heim file-card term at the type level +0.0000 on top (a measured null, macro +0.0004), and the SPAN-LEVEL NAME-RUN CUE -- counts learned ONLINE from the typer's own confident typings, no gold -- takes it to +0.0103. (3) THE BOARD'S THREE ENTITY ROWS, both typers in ONE process, every floor recomputed in place, the FLOOR arm reproducing the board's landed numbers EXACTLY (coref 0.4178 n=3145, common-noun 0.5461 n=2994) which is the licence for the comparison: coref (pronoun) 0.4178 -> 0.4220 with its margin over the strongest floor +0.0979 -> +0.1026, CI-separated in both arms; ENTITY-KB HARD-LINK margin +0.0387 CI[-0.0071,+0.0884] NOT separated -> +0.0501 CI[+0.0070,+0.0958] CI-SEPARATED (n 1318 -> 1356); COMMON-NOUN 0.5461 -> 0.5375 DOWN, with the counted reason: 88 items LEFT the row because they were re-routed to the name branch, and those 88 were resolved at 0.8301 against the row's own average of 0.5461 -- the row was being held up by MIS-TYPED NAMES (a repeated name string resolves trivially by string identity), and against the answer key the common->name flips are 181 CORRECT to 12 wrong. (4) THE FIXED-POPULATION DOWNSTREAM READ, and it is the honest negative: the LIVE entity-clustering organ (`hdlab.online_entity_cluster`, default-ON) over EVERY gold non-pronoun mention (8,604 items, the answer key fixing the population so the decision cannot move it), B-cubed F 0.8024 -> 0.8028, +0.0004 CI[-0.0019,+0.0026] NOT separated. It is NOT a coverage artefact: 337 mentions were retyped, 111 re-headed and 1,086 (12.6%) landed in a DIFFERENT entity file, and the per-mention decomposition says why the net is zero -- of the 337 retyped, 104 improved, 100 worsened and 133 were flat, net -1.21 B-cubed units. On the same population the EXACT-HEAD-STRING floor beats both arms (0.8128, +0.0103 CI[+0.0070,+0.0140] over the shipped arm), so this organ's clustering is string-identity-bound and a better mention TYPE is not what limits it. (5) THE BRIEF'S PREMISE, RE-MEASURED AND REFUTED WITH A NUMBER: the 385 argmax flips from opening the passage reproduce exactly, and the graded typer lets 86 of them reach a type decision against the shipped typer's 82 (+4), changing 6 heads. The 189 'structurally invisible' flips stay invisible BY CONSTRUCTION -- ADJ<->NOUN, VERB<->NOUN and NOUN<->VERB move mass WITHIN the `common` cell of the type partition, so no marginalisation can see them. The typing gain is real and it comes from somewhere else entirely. (6) THE READER'S OWN STREAM (16 GUM test documents through `referent_per_np.referent_per_np_source`, the reader CASED at HEAD per pri 116): 4,413 mentions, of which 0 OF 4,059 NON-PRONOUN MENTIONS CARRY A MULTI-TOKEN SPAN -- the candidate source stores `span_toks=[head]` -- so the span-level cue that carries the whole gain is INERT there by construction and the graded read changes 9 typings (596 -> 587 name-typed). The reader cannot receive this gain until `referent_per_np` keeps the NP span it has already located; that is the next rung and it is filed with its number."
floor: "THE SHIPPED ARGMAX TYPER, recomputed in place on every population, never pasted: `gum_coref._mention_type_organ` (PRON or a pronoun-list form -> pronoun, PROPN -> name, everything else -> common) over `_head_of_span_organ` (the last NOUN/PROPN of the first nominal domain of the ARGMAX tag sequence). GUM TEST, 128 documents / 17,010 mentions: type accuracy 0.9506, span-head accuracy 0.9462, macro F1 0.9352 (pronoun 0.9888 / name 0.8907 / common 0.9262). On the board rows the same arm reproduces the landed board EXACTLY -- coref (pronoun) 0.4178 over its strongest recomputed floor 0.3199 (separate-tracking), common-noun 0.5461 over 0.5344 (same-head string identity), n 3145 / 2994. On the fixed-population clustering instrument the floors are the shipped typer (B-cubed F 0.8024), the all-singleton partition (0.6074) and exact-head string identity (0.8128, the STRONGEST, and it beats both arms)."
controls: "(1) W1 THE SHIPPED OPERATING POINT IS AN IDENTITY: at support='all', eta=inf, no marginalisation and no cue, the graded typer reproduces the shipped head and the shipped type on 393/393 mentions of 4 documents -- the new code IS the old code at its degenerate operating point. (2) W2 the marginalise-then-decide difference is real and is the Bayes decision: P(PROPN)=.35 against P(NOUN)+P(ADJ)=.65 -> shipped 'name', graded 'common' at P=0.6500. (3) W3 THE INFO-FREE TWIN preserves the SHAPE and destroys the PAIRING -- the posterior rows are permuted across the document's tokens, the entropy multiset is byte-identical and 973/974 rows move; the twin scores type accuracy 0.7177 / macro 0.5837 against the arm's 0.9608 / 0.9496 (+0.2351 CI[+0.2121,+0.2591]). (4) THE SPAN CUE'S OWN INFO-FREE TWIN -- the same online table, the same kappa, the same number of free parameters, a RANDOM symbol per mention: type accuracy 0.9526, +0.0021 CI[0.0000,+0.0042] over the floor, NOT SEPARATED, and the arm beats it +0.0082 CI[+0.0051,+0.0116] / macro +0.0124 CI[+0.0083,+0.0170]. The gain is the cue's CONTENT, not its degrees of freedom. (5) THE OPERATING POINT WAS CHOSEN ON THE TRAIN HALF (129 even-index documents) and every headline is the held-out TEST half; the sweep is in metrics_sweep_train.json. (6) PATCH EQUIVALENCE: every board-path number was produced by exec'ing the PROPOSED DIFF'S OWN SOURCE TEXT into the live modules with `__file__` set to the real repo paths, running the real `gum_coref.load_docs`, both loaders in one process; `git apply --check` CLEAN. (7) W6 BACKWARD IDENTITY: the PATCHED `name_content_tokens` with no posterior is BYTE-IDENTICAL to the shipped one on 393 mentions, on both the capitalisation call and the category call -- so the ten live consumers that do not supply a posterior are unaffected by construction. (8) W7 the span-cue table is COUNTS: empty on construction, round-trips through its asset, and a MISSING asset loads an EMPTY table whose cue is silent (the organ degrades to the graded-without-cue arm, +0.0022, rather than failing). (9) W8 the reader-side hunks are pure CAPABILITY: the mention stream is identical to the shipped one on 336 mentions once the two NEW keys are removed, and 330 of them now carry the posterior row -- nothing downstream moves until a consumer is deliberately wired. (10) THE DECISION-RATE CHECK BEFORE READING THE DOWNSTREAM NULL AS A QUALITY FINDING: 337 retyped / 111 re-headed / 1,086 mentions in a different entity file -- the decision propagated, so the null is a fact about the consumer and not about coverage. (11) THE SPAN_UPOS TRANSMISSION WITNESS: the constructed parallel-category list makes `coref.name_content_tokens` return exactly the typer's decision on 8,597 of 8,604 mentions; the 7 exceptions are `MAX_NAME_TOKENS` truncation (pri 109 found the same 5-exception class on its own instrument). (12) A MEASURED NULL NOT DRESSED UP: the Heim file-card evidence read at the TYPE level (where the category organ gates it off for words WITH a lexical entry) is worth +0.0000 type accuracy and +0.0004 macro F1 on top of the graded read -- it ships because it is in the measured configuration, and its own contribution is a null. (13) A CLEAN NEGATIVE, UNDERSTOOD: the DETERMINER FRAME at the type level (Longobardi 1994 N-to-D; the organ's own `log_detc`/`log_rightc` counts) is MONOTONICALLY NEGATIVE at every weight measured on TRAIN (macro F1 0.9389 -> 0.9386 -> 0.9381 -> 0.9367 -> 0.9322 at kappa_det 0 / 0.25 / 0.5 / 1.0 / 2.0), and the reason is counted, not guessed: `det_context` reads the token IMMEDIATELY LEFT of the HEAD, which inside a multi-token NP is a modifier, not the determiner -- on the answer key 'bare' is the commonest frame for BOTH names (1,162) and common nouns (2,012), so the cue carries almost no information where it is read. (14) THE 19c BAN RESPECTED: every number is modern GUM."
files_changed: "experiments/exp_graded_mention_typing_v1.py (the cell: the graded typer and its operating point, the online SpanCueTable, the 8 witnesses, the typing rung with its two twins, the train sweep, the signal-loss diagnose, the hand-off re-count, the fixed-population clustering instrument, the board rows with both typers in one process, the reader's-own-stream probe, the asset builder, and the patch-equivalence runner); notes/problems/<slug>/graded_mention_typing_patch.diff (PROPOSED, NOT applied -- hdlab/coref.py, hdlab/referent_per_np.py, hdlab/situation_reader.py, experiments/gum_coref.py; `git apply --check` CLEAN at d2be94454); notes/problems/<slug>/SOLVED.md; data/exp_graded_mention_typing_v1/*.json (metrics; the output directory comes from experiments._seed_checkpoint.get_output_dir per Q115) and data/hook_state/mention_span_cue_counts.json (the NEW asset the brief authorises -- 15,666 observations accrued ONLINE from the typer's own confident typings on the GUM TRAIN half, no gold read; rebuildable with --build-asset). NO hdlab/ or tools/ file was edited."
reverify: ".venv/Scripts/python.exe experiments/exp_graded_mention_typing_v1.py --self-test   # ~60s, writes only to data/exp_graded_mention_typing_v1_selftest/; expect W1-W5 PASS, and W6/W7/W8 PASS when HDLAB_P118_PATCH_DIR points at a tree holding the patched sources (apply the diff into a scratch copy, or run the three witnesses after integration).   THEN THE HEADLINE (the typing rung on the held-out half, ~70s):  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_graded_mention_typing_v1.py --typing --split test --eta 0.5 --kappa 0.5 --card-mode all --kappa-caps 1.0 --boot 2000 --out metrics_typing_test.json   # expect floor 0.9506 / 0.9352, graded_span_online 0.9608 / 0.9496, +0.0103 CI[+0.0067,+0.0139] and +0.0143 CI[+0.0097,+0.0194], the posterior twin at 0.7177 and the span cue's own twin NOT separated from the floor.   AND THE BOARD ROWS, both typers in one process (~60s):  ... --board --split test --eta 0.5 --kappa 0.5 --card-mode all --kappa-caps 1.0 --out metrics_board_test.json   # expect the FLOOR arm to reproduce the landed board EXACTLY (coref 0.4178 n=3145, common-noun 0.5461 n=2994), coref -> 0.4220, entity-KB margin +0.0387 -> +0.0501 CI-separated, common-noun -> 0.5375 with 88 items leaving the row at 0.8301.   AND THE FIXED-POPULATION DOWNSTREAM READ (~90s):  ... --cluster --split test --boot 2000 --out metrics_cluster_test.json   # expect B-cubed 0.8024 -> 0.8028 NOT separated, string-identity 0.8128 beating both, the transmission witness 8597/8604 and the decision rate 337 / 111 / 1086.   AND THE PREMISE (~60s):  ... --handoff --split test   # expect 385 argmax flips, 82 type changes under the shipped typer and 86 under the graded one.   AND THE READER'S STREAM (~25s):  ... --reader-stream --split test --docs 16   # expect 0 multi-token spans of 4,059 non-pronoun mentions and 9 typing flips.   THE ASSET, if it needs rebuilding:  HDLAB_P118_PATCH_DIR=<patched tree> ... --build-asset   # ~60s, 15,666 observations from GUM TRAIN, no gold."
---

# The consumer took its point estimate at the wrong level of the hierarchy -- and fixing that is worth +0.0103, while the thing the brief thought was being lost (189 invisible category corrections) turns out to be invisible to *any* three-valued type by construction

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box; count tables only; no external LLM, no spaCy, no nltk, no supervised parser at inference. MODERN gold only (GUM). The treebank columns are the ANSWER KEY and are never read in a decision. **No `hdlab/` or `tools/` file was written** -- the change is `graded_mention_typing_patch.diff` (`git apply --check` CLEAN at `d2be94454`), and every board-path number here was produced by exec'ing that diff's own source text into the live modules.

---

## 1. THE OPENING MOVE: how does the BRAIN do this?

The entity layer's question is not "what part of speech is this word". It is **"does this expression pick out an INDIVIDUAL I have a file on?"**

| what | the pin |
|---|---|
| a proper name is a **rigid designator** -- a word that picks out an individual | Kripke 1980 |
| proper-name processing runs through a **referent route in the left temporal pole**, distinct from the common-noun semantic route, and it sits **ABOVE and is FED BY** the posterior-temporal word-form/category level | Semenza 2006/2009 (proper-name anomia); Damasio et al. 1996 |
| a referring expression's FORM signals the **cognitive status** of its referent on a GRADED, implicational scale -- a consumer reads a distribution over statuses, not a label | Gundel, Hedberg & Zacharski 1993 (Givenness Hierarchy); Ariel 1990 (accessibility bands) |
| the passage history of the string is a **file card**, and it is what separates "the MSM" (a name) from "the CEO" (a common noun) | Heim 1982; this is pri-104's arm, already inside the category organ |
| a multi-word name is stored as **one lexical unit** by the referent route, not assembled from its parts | Semenza 2009; the reason "Game of Thrones" is a name although "Game" is an ordinary noun |

Two of these have exact mathematical consequences, and **both are violated on disk**:

**(1) MARGINALISE, THEN DECIDE.** The mention type is a **coarsening** of the category variable. The Bayes decision on a coarsened variable under 0-1 loss is `argmax_t sum_{c in t} P(c | words)` -- marginalise first, decide second. The shipped consumer computes `type(argmax_c P(c | words))`: it takes its point estimate at the CATEGORY level and then coarsens. The two differ whenever the winning single category sits in a type whose TOTAL mass is smaller than a rival's -- `P(PROPN)=.35` against `P(NOUN)+P(ADJ)=.65` is typed `name` by the shipped rule and `common` (at P=0.65) by the correct one (witness W2).

**(2) THE CONSUMER KNOWS IT IS TYPING A NOMINAL.** A mention span has already been segmented as a referring expression, so the categories that cannot head one (DET/ADP/AUX/CCONJ/SCONJ/PART/PUNCT) are excluded by the consumer's own evidence and the posterior is renormalised on the support that can. That is structural knowledge of the consumer, not a fitted number.

And the same argmax defect sits one step earlier, in the **head** rule: "the last NOUN/PROPN of the first nominal domain" is computed on the ARGMAX tag sequence. Graded, each position is scored by its **nominal mass** with a head-finality decay `eta` -- and `eta -> inf` reproduces the shipped rule exactly when the posterior is peaked, which is witness W1 (393/393 heads, 393/393 types identical).

---

## 2. THE STATUS PROBE -- WHERE THE SIGNAL IS LOST, CHAIN BY CHAIN, WITH COUNTS

*The signal the end read needs: **a graded belief about whether this span picks out an individual, a kind, or a deictic pointer.*** GUM TEST, 128 documents, 17,010 mentions.

| # | rung | what it PRODUCES | what the next rung READS | **WHAT IS LOST** | BF status *for this signal* |
|---|---|---|---|---|---|
| 0 | tokens | the CASED sentence (pri 116, landed at HEAD) | the category organ | nothing -- this rung was repaired last | **BF** |
| 1 | categories (`lexical_categories`) | a **posterior over 17 categories** per token, plus the Heim file-card term folded in for words with no lexical entry | `gum_coref.organ_tags` kept **the argmax only** | **the whole distribution.** The type posterior's median entropy is 0.0004 nats -- 14,349 of 17,010 mentions are peaked past 0.99 -- but the mean confidence where the shipped typer is WRONG is 0.8504 against 0.9852 where it is right, so the uncertainty is exactly where the errors are | computation BF, **HAND-OFF NOT BF -- repaired here** |
| 2 | the span **head** (`_head_of_span_organ`) | the last NOUN/PROPN of the first nominal domain of the ARGMAX sequence | the type rule and the lemma identity key | **915 of 17,010 heads are wrong** (0.9462), and 228 of the 841 typing errors follow from a wrong head. Graded on nominal mass this becomes 0.9490 (+0.0028 CI[+0.0012,+0.0045] through the diff) | **NOT BF -- repaired here** |
| 3 | the **type** (`_mention_type_organ`, `coref.name_content_tokens`) | one of three labels | ten live organs branch on it | **the confidence, and every distinction among NOUN/ADJ/VERB/NUM.** 613 of 841 errors are made with the RIGHT head -- a type error on a correctly-located head. The dominant class is **gold NAME typed common: 502**, and at the gold head their mean name-mass is only 0.2151 (25% carry >= 0.33), so three quarters of them are an UPSTREAM gap and not a hand-off loss | **NOT BF -- repaired here** |
| 3b | the **span**, at the reader | `referent_per_np._mk_referent` stores `span_toks=[head]` | `name_content_tokens` | **the whole span.** 0 of 4,059 non-pronoun mentions on the reader's stream carry more than one token, so every span-level cue is inert there BY CONSTRUCTION | **NOT BF -- named, not repaired (lead 1)** |
| 4 | entity files (`online_entity_cluster`) | a partition over non-pronoun mentions | coref / common-noun / salience / the reader's entity QA | **the type barely matters here.** 1,086 of 8,604 mentions land in a different file under the graded type and B-cubed moves +0.0004; on the same population EXACT-HEAD STRING IDENTITY beats the organ by +0.0103 CI-separated | organ BF_SPIRIT, **but string-identity-bound (lead 2)** |

### 2b. THE ONE NUMBER THAT REFRAMES THE BRIEF

`--handoff`, both register arms in ONE process, the board's own TEST split:

> **The 385 argmax flips reproduce exactly. The graded typer lets 86 of them reach a mention-type decision, against the shipped typer's 82.**

The brief's premise was that the 189 "structurally invisible" flips (ADJ->NOUN 57, VERB->NOUN 34, NOUN->VERB 16, ADJ->VERB 12) would become visible to a graded type. **They cannot be, and the reason is arithmetic:** those pairs move mass *within the `common` cell of the partition*, so `sum_{c in common} P(c)` is unchanged by construction. They can only reach the decision through the HEAD, and they change the head 6 times. **A graded type is the right repair for a different loss than the one the brief located.**

*This is test 4 of `notes/problems/README.md` applied to my own brief: the number that said the defect was costing something (82 of 17,010) is not the number the fix moves.*

---

## 3. WHAT WAS BUILT, AND WHAT EACH LEVER WAS WORTH

One organ path (`hdlab/coref.mention_type_graded`), sitting beside the gate the ten live consumers already call. Held-out GUM TEST, the operating point chosen on the TRAIN half, doc-paired bootstrap 2,000.

| arm | type acc | head acc | macro F1 | delta vs the floor, CI95 | separated? |
|---|---|---|---|---|---|
| **FLOOR -- the shipped argmax typer** | 0.9506 | 0.9462 | 0.9352 | -- | -- |
| marginalise-then-decide ALONE | 0.9518 | 0.9462 | 0.9359 | +0.0012 [-0.0002,+0.0028] | no |
| the graded HEAD alone | 0.9516 | 0.9490 | 0.9363 | +0.0011 [-0.0002,+0.0023] | no |
| both | 0.9528 | 0.9490 | 0.9370 | **+0.0022 [+0.0005,+0.0040]** | **yes** |
| + the Heim file card at the TYPE level | 0.9528 | 0.9490 | 0.9374 | +0.0022 [+0.0004,+0.0042] | yes (the card's OWN contribution is a null) |
| **+ the SPAN-LEVEL NAME-RUN CUE (online counts)** | **0.9608** | **0.9490** | **0.9496** | **+0.0103 [+0.0067,+0.0139]** | **yes** |
| the span cue's OWN twin (random symbol) | 0.9526 | 0.9490 | 0.9371 | +0.0021 [0.0000,+0.0042] | **no** |
| the info-free twin (posterior rows permuted) | 0.7177 | 0.7710 | 0.5837 | -0.2329 [-0.2572,-0.2101] | separated BELOW |

Per type, floor -> arm: **name F1 0.8907 -> 0.9171** (+0.0264 CI[+0.0178,+0.0362]; recall 0.8420 -> 0.8855 **with precision UP** 0.9455 -> 0.9510), **common F1 0.9262 -> 0.9420** (+0.0158 CI[+0.0105,+0.0211]), pronoun F1 0.9888 -> 0.9897 (+0.0009, n.s., not down).

### 3a. THE LEVER THAT CARRIES IT, AND WHY IT IS THE BRAIN'S

The 502 gold names typed `common` are dominated by **multi-word names whose head is an ordinary English noun**: *Game of Thrones* (head `Game`, name-mass 0.036), *The Rains of Castamere* (head `Rains`, 0.011), *the Slavonic Dances*, *the Symphony From the New World*, *Mutation Operators for GIS*, *Digital Humanities*, *Extract 1* / *Figure 2* / *Listing 1*. The category organ already reads each token's own shape relative to the sentence convention (`word_shape` x `position_class`). **What it cannot see is that the whole phrase is one capitalised unit spanning a preposition** -- and that is exactly the evidence the referent route has, because the referent route stores the NAME, not its parts (Semenza).

So the cue is a property of the SPAN, read EXCLUDING the head so nothing the organ already used is counted twice: how many OTHER mid-sentence capitals the span carries (binned 0/1/2/3+) crossed with whether it carries a lowercase content word (the descriptive-phrase disqualifier `name_content_tokens` already uses). Eight symbols. The table is **counts, learned online from the typer's own confident typings** (p >= 0.95) -- no gold, no fitted parameter, an observe path, and it prints:

| symbol | pronoun | name | common |
|---|---|---|---|
| `o0_l0` (no other capitals, no lowercase content word) | 8,433 | 1,467 | 2,041 |
| `o0_l1` (a lowercase content word) | 7 | 29 | **2,390** |
| `o1_l0` (one other mid-span capital, no lowercase word) | 0 | **513** | 97 |
| `o2_l0` / `o3_l0` | 0 | 90 / 60 | 19 / 28 |

*Fine, Jaeger, Farmer & Qian 2013 (rapid expectation adaptation) is the account: the comprehender learns the passage's naming convention from what it already understands. It is the same mechanism the passage register cites one level down, applied to the one piece of evidence only the consumer that HOLDS THE SPAN can see.*

### 3b. THE BOARD'S THREE ENTITY ROWS -- and the honest reading of the one that falls

Both typers in ONE process, every floor recomputed in place. **The floor arm reproduces the landed board EXACTLY (coref 0.4178 n=3145, common-noun 0.5461 n=2994), which is what licenses every comparison below.**

| row | floor arm | graded arm | margin over the strongest recomputed floor |
|---|---|---|---|
| coref (pronoun) | 0.4178 (n 3145) | **0.4220** (n 3130) | +0.0979 [+0.0752,+0.1213] -> **+0.1026 [+0.0792,+0.1261]**, CI-sep in both |
| entity-KB hard-link | 0.3558 (n 1318) | **0.3569** (n 1356) | +0.0387 [-0.0071,+0.0884] NOT sep -> **+0.0501 [+0.0070,+0.0958] CI-SEPARATED** |
| common-noun | 0.5461 (n 2994) | 0.5375 (n 2906) | +0.0117 [-0.0006,+0.0228] -> +0.0041 [-0.0076,+0.0150] |

**The common-noun row falls, and the reason is counted rather than asserted.** The row's population is *defined by the decision under test*, so a mention the graded typer re-routes LEAVES it. 88 items left, and the arithmetic on the hits says those 88 were resolved at **0.8301** against the row's own average of **0.5461**. Against the answer key the common->name flips are **181 correct to 12 wrong**. So the row was being held up by mis-typed names -- a repeated name string resolves trivially by same-head string identity -- and correcting the typing removes the easiest items from it. **This is pri 109's artefact measured from the other side** (*"MARGIN OVER A ROW'S OWN RECOMPUTED FLOOR IS NOT COMPARABLE ACROSS ARMS WHOSE TYPING DIFFERS"*), and it is the reason section 3c exists.

### 3c. THE FIXED-POPULATION DOWNSTREAM READ -- the negative, and it is understood

Because a typing arm moves the board rows' populations, the decisive downstream instrument is one whose population the decision **cannot** move: the LIVE entity-clustering organ (`hdlab.online_entity_cluster`, default-ON since 2026-09-09) over **every gold non-pronoun mention** (8,604 items; the answer key fixes who is scored, the typer decides only the ROUTE and the identity key), B-cubed against the gold chains.

| arm | B-cubed F | vs the shipped typer |
|---|---|---|
| shipped argmax typer | 0.8024 | -- |
| **graded typer** | **0.8028** | **+0.0004 [-0.0019,+0.0026] NOT SEPARATED** |
| info-free twin (posterior permuted) | 0.6648 | -0.1376, separated below |
| all-singleton floor | 0.6074 | -0.1951, separated below |
| **exact-head string identity** | **0.8128** | **+0.0103 [+0.0070,+0.0140] -- the STRONGEST floor, and it beats BOTH arms** |

**It is not a coverage artefact, and I checked that before reading it as a quality finding:** 337 mentions were retyped, 111 re-headed, and **1,086 (12.6%) landed in a different entity file**. The per-mention decomposition says why the net is zero: of the 337 retyped, **104 improved, 100 worsened, 133 were flat, net -1.21 B-cubed units**.

**The mechanism, stated as a claim that can be attacked:** `online_cluster`'s two routes are near-equivalent in discriminative power on this corpus. The NAME route clusters by the aliaser's canonical name-token set; the COMMON route clusters by exact head-lemma identity under a gender/number filter and ACT-R activation. For a mention whose head string repeats -- which is the overwhelming majority -- **both routes put it with the same prior mentions**. The route only separates them for name VARIANTS ("Barack Obama" / "Obama"), and the exact-head-string floor beating both arms by +0.0103 says the extra machinery is currently net-negative on this population. **A better mention type is not what limits this organ.**

---

## 4. EVERY CONSUMER, CLASSIFIED (checklist item 3)

`name_content_tokens` is the NAME-vs-COMMON gate for **ten** live organs. All ten branch on a boolean; **none reads a graded type.** The diff makes the ONE gate graded, so all ten receive the better decision with **no call-site change** (the pattern pri 104's forward wire used: omit the new argument and the function is byte-identical, witness W6).

| consumer | how it types | what it gets from the diff |
|---|---|---|
| `hdlab/online_entity_cluster.py` | `name_content_tokens(span_toks, upos=span_upos)` | the graded decision as soon as a caller supplies `tag_post` |
| `hdlab/entity_resolver.py` | same | same |
| `hdlab/commonnoun_binder.py` | same | same |
| `hdlab/crosstype_live_adapter.py` | same | same |
| `hdlab/coref_distractor_suppress.py` | same | same |
| `hdlab/event_centrality_coref.py` | same | same |
| `hdlab/gender_organ.py` | same | same |
| `hdlab/unified_referent.py` | same | same |
| `hdlab/lexical_utils.py` | same | same |
| 🔻 `hdlab/scene_segment.py:452` | `name_content_tokens(span_toks)` **with NO `upos`** | **nothing -- this consumer is STILL on the raw capitalisation rule**, a gap pri 104's wire left. A one-line alignment; deliberately NOT in this diff because I have not measured it (lead 4) |
| `experiments/gum_coref._mention_type_organ` (the board's three rows) | the argmax of the category organ | **routed through the one graded typer -- this is where the measured gain lands** |
| `hdlab/referent_per_np._mk_referent` (the reader's stream) | `upos=up[hw]`, single-token span | the posterior row is now CARRIED (W8: pure capability, nothing moves); the gain cannot arrive until the NP span is kept (lead 1) |

---

## 5. WHAT WOULD IT TAKE TO CONVERT THIS TO A FULL PASS

The bar has five clauses. **Met:** the typer reads the graded posterior and the card evidence through one organ path; typing F1 up CI-separated for name and common with pronoun flat; the twin at floor; every consumer classified; the knowledge in counts with an online observe path. **Not met:** *"coref / common-noun rows not down"* -- the common-noun row is down, with a counted reason rather than a paired-subpopulation win, and the downstream read the brief was really after (does better typing buy better entity resolution?) is a measured null.

Every lead I can see, researched, with what it would take:

1. **THE READER'S CANDIDATE SOURCE THROWS THE SPAN AWAY. `referent_per_np._mk_referent` stores `span_toks=[head]` -- 0 of 4,059 non-pronoun mentions carry more than one token.** The lever that is worth +0.0103 on the board loader's stream is *structurally inert* on the reader's. The builder already knows the NP: `_content_head_positions` finds the head and `frame_heads` reads the determiner/possessive left edge. Keeping the span (left edge .. head) would let the same typer run there. **Not built here** because it changes the candidate source's schema for ten consumers and needs its own reader A/B; it is the single highest-value follow-on from this work and I would file it first. *Measured size of what is currently lost: the difference between +0.0103 and +0.0000.*
2. **THE ENTITY-CLUSTERING ORGAN IS STRING-IDENTITY-BOUND.** Exact-head string identity beats it by +0.0103 CI-separated on the fixed population (0.8128 vs 0.8024/0.8028), and a corrected type is as likely to hurt as to help (104 up / 100 down). Before another upstream rung is spent on it, the organ's own routes need the measurement: *what does the NAME route buy over the COMMON route on mentions whose head string does NOT repeat?* That is the sub-population where the route can matter, and it is a cheap, well-defined next brief.
3. **THREE QUARTERS OF THE REMAINING NAME MISSES ARE AN UPSTREAM GAP, NOT A HAND-OFF LOSS.** On the 502 gold names typed common the mean name-mass at the gold head is 0.2151 and only 25% carry >= 0.33. No read of this posterior recovers them. The gap is the category organ's own PROPN evidence on *known common-noun forms used as names* ("College", "Times", "Game", "Rains"), which is pri 109's finding restated: the category organ is the whole common-noun gap. The span cue recovers the ones with a capitalised run; the residue needs **entity-level evidence at the category level** -- the file card keyed on the REFERENT rather than the surface string (pri 112's own alternate path 2).
4. **`scene_segment.py:452` STILL TYPES BY CAPITALISATION** -- the only one of the eleven consumers pri 104's wire missed. One line (`upos=m.get("span_upos")`). Not in this diff because it is an unmeasured behaviour change on a board-visible path; it should be landed with its own A/B.
5. **THE BOARD'S COMMON-NOUN ROW IS PARTLY A TYPING ARTEFACT.** 88 of its 2,994 items are mis-typed names resolved at 0.8301. Any arm that improves typing will LOWER this row. The instrument repair is to define the row's population by the ANSWER KEY's mention type rather than by the arm's -- which is pri 109's paired-subpopulation instrument, and it belongs in `experiments/exp_board_coref_gum_v1.py` rather than in a solver's cell.

**Negatives, understood rather than filed:**
- **The determiner frame at the type level (Longobardi 1994) is monotonically negative** (macro F1 0.9389 -> 0.9322 as kappa_det goes 0 -> 2.0). Understood with counts: `det_context` reads the token immediately left of the HEAD, which inside a multi-token NP is a modifier, not the determiner, so `bare` is the commonest frame for names (1,162) *and* common nouns (2,012). **The stronger form is the SPAN's left-edge determiner**, which the consumer can see and the token-level cue cannot -- untested, and it is the one variant of this lever I would still build.
- **The Heim file-card term at the type level is a measured null** (+0.0000 type accuracy, +0.0004 macro F1). It is the brief's own headline proposal and it does not carry the gain; it ships only because it is inside the measured configuration.
- **Marginalise-then-decide alone is +0.0012, not separated.** The mathematically-correct repair is real but small, because the posterior is peaked on 14,349 of 17,010 mentions. It becomes separated only in combination with the graded head (+0.0022).

---

## KEY REALIZATIONS

1. **The point estimate was taken at the wrong LEVEL of the hierarchy, not merely too early.** The interesting defect was not "the consumer reads an argmax"; it was that the argmax is taken over the *category* variable when the decision is about the *type* variable, which is a coarsening of it. Naming it that way is what produced witness W2 and the whole marginalise-then-decide arm.
2. **Ask what evidence only the CONSUMER can see.** The category organ reads every token's own shape; it cannot read that a whole span is one capitalised unit. Once the question was "what does the level that holds the span know that the level below it does not?", the lever fell out -- and it is worth five times the mathematically-correct repair.
3. **Measure the brief's own premise before building on it.** The 385/189/82 counts were right and the inference from them was wrong: flips *within* a partition cell are invisible to any coarsening of that partition, by arithmetic. Re-running `--handoff` with the new typer (82 -> 86) cost six minutes and saved the submission from claiming a mechanism it does not have.
4. **When a population is defined by the decision under test, build an instrument whose population is not.** The board's common-noun row FALLS under a typing improvement, and both facts are true at once. The fixed-population clustering read is what let the downstream null be stated honestly instead of argued about.
5. **Check the decision rate before reading a null as a quality finding.** 1,086 of 8,604 mentions landed in a different entity file -- so the +0.0004 is a fact about the consumer's two routes being near-equivalent, not about the decision failing to propagate.
6. **Give a new cue its OWN info-free twin, not just the arm's.** The span-cue twin (same table, same kappa, random symbol) sits at +0.0021 n.s. over the floor -- which is what proves the +0.0103 is the cue's content and not its free parameters.

## ALTERNATE PATHS -- other ways to do this read, similarly or MORE brain-foundational

1. **THE FILE CARD KEYED ON THE REFERENT, NOT THE SURFACE STRING.** Heim's cards are files on INDIVIDUALS; ours are keyed by lowercased string. A card keyed on the resolved referent would let "the Digital Humanities" and "DH" share evidence, which is precisely what the 502 residue needs. *More brain-foundational than what I shipped.* It needs the entity resolver inside the category organ's feed loop -- pri 112 noted the same path and it is now expressible because the cards carry times.
2. **A GRADED CONSUMER, NOT A GRADED PRODUCER.** I made the typer graded and every consumer still branches on its argmax. The Givenness Hierarchy is implicational: a mention with P(name)=0.3 should be *offered to the name route with weight 0.3* and to the common route with weight 0.7, and the routes' scores combined -- not routed to one. *Strictly more brain-foundational.* Not built because `online_cluster`'s two routes are structurally different code paths and the measurement in section 3c says the routes barely differ anyway; it should be built after lead 2 shows the routes DO separate somewhere.
3. **THE SPAN'S LEFT-EDGE DETERMINER (Longobardi 1994 N-to-D).** The pinned syntactic fact -- an English proper name in argument position is determinerless -- read where it actually lives, at the NP's left edge instead of at the head's immediate left. The organ's `log_detc` counts are the wrong estimate for it; a span-level table accrued the same way as the name-run table is the right one. Cheap, and the honest successor to the negative in section 5.
4. **TYPE THE MENTION FROM THE PREDICTION, NOT THE INPUT.** Comprehension is predictive (Rao & Ballard 1999; Kuperberg & Jaeger 2016): the discourse model has an expectation about what kind of expression comes next (Centering's Cb continuity predicts a pronoun; a topic shift predicts a name). That expectation is a TOP-DOWN prior on the type, and the substrate has all of it already (`salience_binder`, the Centering ranks). *Structurally the most brain-faithful of the four*, and it is a different organ's arm (the situation model's), not the typer's.

## PRIORITY NEXT STEPS

1. Keep the NP span in `referent_per_np._mk_referent` (lead 1) -- without it the reader gets none of this.
2. Measure `online_entity_cluster`'s NAME route against its COMMON route on the non-repeating-head sub-population (lead 2); if they do not separate there either, the entity layer's next rung is not typing at all.
3. Repair the board's common-noun row to a gold-typed population (lead 5) so a typing improvement stops reading as a regression.
4. `scene_segment.py:452` with its own A/B (lead 4).

## AUDIT UPDATE (`notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- **`hdlab/coref.name_content_tokens` / the entity layer's mention typer: NOT_BF as shipped** -- a point estimate taken at the wrong level of the category hierarchy, three-valued, with the head chosen off the argmax tag sequence. The diff makes it a marginalised decision over the type partition with a graded head and an online span-level cue; **BF_SPIRIT** after it (the Bayes-decision step is pinned; the span-cue symbol alphabet is OUR-INVENTION-UNDER-TEST and swept).
- **`hdlab/online_entity_cluster`: the audit's `BF_SPIRIT` stands, but a deviation should be recorded** -- on the fixed-population B-cubed instrument (8,604 GUM test mentions) it is beaten CI-separated by exact-head string identity (0.8024 vs 0.8128), and its two retrieval routes are near-equivalent on this corpus (a corrected mention type moves 1,086 mentions and nets +0.0004).
- **`hdlab/referent_per_np`: add the deviation** -- the candidate source discards the NP span (0 of 4,059 non-pronoun mentions carry more than one token), so every span-level cue in the entity layer is inert on the reader's own stream.

## DO NOT QUOTE

- The board's common-noun accuracy 0.5375 under the graded typer is **not comparable** to the floor arm's 0.5461: the populations differ by 88 items (2,994 -> 2,906) and the row's population is defined by the decision under test. Quote the counted reason with it or quote neither.
- The reader's-stream numbers (596 -> 587 name-typed, 9 flips) are the **candidate source's own stream on 16 documents**, not a full reader read; no reader witness was run here.
- The `--cluster` B-cubed values are this cell's own instrument over gold non-pronoun mentions; they are **not** the board's coref row and must not be pasted next to it.
