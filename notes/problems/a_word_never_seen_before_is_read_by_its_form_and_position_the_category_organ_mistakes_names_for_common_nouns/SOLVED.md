---
problem: a_word_never_seen_before_is_read_by_its_form_and_position_the_category_organ_mistakes_names_for_common_nouns
status: PARTIAL
bar: "Unknown-word accuracy up CI-separated (paired bootstrap over sentences) with overall accuracy not down, PROPN<->NOUN confusions down by a third or more, twin at the floor, knowledge as counts with the existing online observe path -- OR a numbered located negative naming the missing input (e.g. the web-noise share)."
result: "FULL UD-EWT TEST, 25,094 tokens / 2,077 sentences, 1,882 unseen; scorer = UPOS argmax of the organ's own posterior at the live default (lag 2, order 2, shape, rare-mix, cluster cue); paired bootstrap over SENTENCES, 2,000 resamples. THE ARM (C1_lr05 = six count-based unknown-word cues): UNSEEN-WORD ACCURACY 0.7519 -> 0.8002, delta +0.0484 CI[+0.0322,+0.0643] CI-SEPARATED (half-width 0.0161). OVERALL accuracy is not merely unharmed but UP CI-separated: 0.9278 -> 0.9312, +0.0033 CI[+0.0016,+0.0051]. PROPN<->NOUN 163 -> 154 = -5.5%, which MISSES the brief's 'down by a third' (needed <=109) -- this is the PARTIAL, and section 5 bounds it with an oracle plus 25 measured arms. GENERALISES to the organ's second inventory: the PENN arm (which the temporal ORDER organ reads) xpos 0.9176 -> 0.9222 (+0.0046 CI[+0.0028,+0.0065] CI-sep), its own unseen slice 0.7402 -> 0.7896 (+0.0494 CI[+0.0335,+0.0662] CI-sep)."
floor: "A0_live = the SAME code path with the cues off, rebuilt from the SAME UD-EWT training supply: unseen 0.7519, overall 0.9278, PROPN<->NOUN 163 (117 + 46). This REPRODUCES the live organ's on-disk numbers EXACTLY (the brief's 0.7519 / 0.9278 / 117 / 46 and the by-shape profile lower 0.760 / Cap 0.783 / digit 0.776 / other 0.657 / ALLCAP 0.597), and the experiment's self-test asserts A0 is byte-identical to `LexicalCategories` itself (posterior max-abs difference 0.0). No floor was pasted across harnesses; every number is recomputed in-place on the item's own population."
controls: "(1) INFORMATION-FREE TWIN -- the winning arm with the shape/suffix SYMBOL->category mapping PERMUTED (identical alphabet, identical row marginals, identical smoothing): unseen 0.3714 vs the arm's 0.8002; the arm beats its twin +0.4288 CI[+0.3991,+0.4582] CI-sep and the twin is far BELOW the floor (-0.3804 CI-sep). THE TWIN ALSO CAUGHT A DEFECT IN ITSELF (it did not permute the joint-cell tables, scoring 0.8559 against 0.8580 -- vacuous; fixed, then 0.595). (2) A0 REGRESSION IDENTITY -- A0 reproduces the unmodified class exactly (self-test, 1e-12). (3) NO-REGRESS, HEADS RUNG (UD-EWT test 700, the organ's OWN tags): hard readout UAS 0.5969 -> 0.5988, GRADED readout 0.5996 -> 0.5999, tag agreement 0.9368 -> 0.9400 -- no regression on either hand-off. (4) NO-REGRESS, PENN ARM: up CI-sep, see result. (5) ABLATION, 25 arms: every cue alone, every cue's weight swept. (6) ORACLE-CEILING PROBE on the missed half (section 5). (7) ISOLATION CONTROL for the Katz frame cue: on the bare floor it moves accuracy not at all (0.7519 -> 0.7529, n.s.) but cuts PROPN<->NOUN 163 -> 144 -- it is specifically a NAME cue, not a general one. (8) ONLINE PATH -- `observe()` grows the counts and re-derives the productivity stratum (novel types 10,453 -> 10,454). (9) PATCH EQUIVALENCE + REGRESSION -- the proposed patch loading the CURRENT live asset with the cues off is byte-identical to the live module (max posterior difference 0.0, 0 tag differences / 6,305 tokens, legacy fallback confirmed); with the proposed defaults it reproduces the measured arm exactly (0.0)."
files_changed: "experiments/exp_category_unknown_word_cues_v1.py (the cell: six cues, 25 arms, the twin, the paired bootstrap, the rung-by-rung chain trace, the mechanism `--explain`, the induced-coverage bound, the Penn and heads (hard + graded) no-regress modes, `--self-test`); notes/problems/<slug>/SOLVED.md; notes/problems/<slug>/lexical_categories_patch.diff (proposed, NOT applied -- strategy lands it per Q111); data/hook_state/lexical_categories_counts_v1_unkcues_candidate.json (candidate counts asset, 2.0 MB, written BY the patched module); data/exp_category_unknown_word_cues_v1/metrics*.json (10 records). NO hdlab/ or tools/ file was edited; the live asset was NOT touched."
reverify: ".venv/Scripts/python.exe experiments/exp_category_unknown_word_cues_v1.py --self-test    # scaffold-free; asserts A0 == the unmodified LexicalCategories to 1e-12, the arm beats its shuffled twin, the shape/position/frame functions, and that observe() re-derives the productivity stratum.  THEN the headline (writes only to its own metrics file, never into a landed record):  OMP_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=category_unknown_word_cues_v1 .venv/Scripts/python.exe experiments/exp_category_unknown_word_cues_v1.py --boot 2000 --arms C1_lr05 --out-name metrics_two_sided_frame.json    # expect unseen 0.8002 vs floor 0.7519, overall 0.9312 vs 0.9278, PROPN<->NOUN 154 vs 163, twin ~0.371"
---

# A word never seen before: the organ was reading its form with a six-symbol alphabet, a hard single-suffix guess, a frequency-weighted evidence base and a doubled prior — unseen-word accuracy 0.7519 → 0.8002 CI-separated, overall accuracy UP CI-separated, and the name/common-noun half of the bar located with an oracle rather than claimed

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box, counts only, no external tool at inference, no treebank read while learning. **No `hdlab/` written** — the change is proposed as `lexical_categories_patch.diff`.

---

## 1. THE OPENING MOVE: how does a reader categorise a word it has never met?

**Structure.** The visual word-form system (left occipito-temporal) delivers a *morpho-orthographic* description of a novel string — form-based, automatic, semantics-blind ([Rastle & Davis 2008](https://www.tandfonline.com/doi/abs/10.1080/01690960802069730)) — into the same graded category **competition** that already settles known words (MacDonald 1994 constraint satisfaction; Kuperberg & Jaeger 2016 graded belief). That is the organ we already have. **No new organ was minted: four more count tables inside `hdlab/lexical_categories.py`.**

**The four computations, each PINNED at the computational level, each a count table, each swept never adopted:**

| # | the brain's computation | the citation | what the organ did instead |
|---|---|---|---|
| 1 | Capitalisation is read **relative to position** — a reader knows a sentence-initial capital is *forced by the convention* and carries no name evidence, while a capital elsewhere is a name marker | the **orthographic cue hypothesis** — the proper-name advantage is orthographic, not semantic/morphological, and initial capitalisation works "as a clue to which category the word belongs" ([Peressotti, Cubelli & Job 2003](https://pubmed.ncbi.nlm.nih.gov/12852936/)); readers use parafoveal capitalisation to infer syntactic category *during* reading ([Cutter et al.](https://pure.mpg.de/rest/items/item_3158689_5/component/file_3239202/content)) | `word_shape` is **position-blind**: sentence-initial `Cap` and mid-sentence `Cap` are one symbol |
| 2 | A novel form is judged by the company **novel forms** keep — productivity is measured on the **hapax stratum**, because "productive patterns produce many low-frequency words" ([Baayen & Lieber 1991; Baayen 2009](https://quantling.org/~hbaayen/publications/BaayenHSK2009.pdf); [Pierrehumbert & Granell 2018](https://aclanthology.org/W18-5814.pdf)) | as left | the unknown-word estimator is a **token**-count table over the **whole** vocabulary, backing off to the overall tag frequency — which is function words that can never be novel |
| 3 | The word-form description is **finer than six symbols**: case, digits, internal punctuation, ALL-CAPS length | Rastle & Davis, as above | `'E17'`, `'01-Feb-02'`, `'EB3326'`, `'Guaranty.doc'`, `'b/c'`, `'AMS'` share **two** symbols (`digit`, `other`) — exactly the worst slices (0.776, 0.657) |
| 4 | The morpho-orthographic parse is **graded**: every plausible segmentation is activated in parallel and the alternatives are kept alive, weighted by reliability | Rastle & Davis; MacDonald 1994 — **the account this module's own docstring already cites** | a **hard commitment to the single longest suffix with any count** |
| 5 | The emission slot takes a **likelihood**, not a posterior | Bayes; the module is an explicitly generative HMM | `_log_emit_unknown` returns `P(c \| suffix)` and forward-backward then multiplies by `P(c \| prev)` — **the category prior is applied twice** for every unseen word, penalising exactly the low-prior categories, PROPN among them |
| 6 | When the lexical cue is **absent**, the slot cue carries the weight it cannot | Mintz 2003 frequent frames; MacDonald 1994 cue competition | a **blanket** neighbour-word channel was REFUTED on disk (2026-09-13, 0.9152). The brain's form is not blanket |

---

## 2. THE SIGNAL-LOSS TRACE, RUNG BY RUNG, IN COUNTS

*(`--chain-trace`; `data/exp_category_unknown_word_cues_v1/metrics_chain_trace.json`. 25,094 test tokens, 1,882 unseen.)*

| rung | what it produces | what the next rung reads | **what is LOST** | BF status *for this signal* |
|---|---|---|---|---|
| **0. tokenisation** | one token per code/date/filename/URL | the form cue must read the whole string | **305 of 1,882 unseen tokens (16.2%)** arrive with internal structure the reader would segment; the incumbent maps them onto **2** symbols | **NOT BF for this signal** — the brain's letter-position coding reads *inside* the string; we receive a pre-tokenised stream and never decompose it |
| **1. form cue** (`word_shape`) | 6 position-blind symbols | the shape emission factor | position: **223** unseen tokens sit in a forced-capitalisation slot and were indistinguishable from mid-sentence capitals; granularity: 6 symbols where 18 are used | **was NOT BF, now BF** — fixed here (cues 1 + 3) |
| **2. morpho-orthographic parse** | ONE suffix length | the unknown-word estimator | commits to a **4-character** suffix for **1,056 of 1,882**, and **322** of those commitments rest on **≤ 2 observations**; every shorter, better-attested parse is **discarded** | **was NOT BF (a point estimate where the brain keeps alternatives alive), now BF** — the largest single lever |
| **3. reading-acquired inventory** (`induced_categories`, BF) | one **hard** class id per covered word | the cluster emission factor | covers **549 / 1,882 = 29.2%**; the cue is **exactly zero** for the other **1,333**. It hands down a point class, not a distribution | **BF computation, but the hand-off is a POINT and the coverage is the loss** — unfixed |
| **4. lemma / stem route** (`morphology`, BF) | one base form | conflict-triggered stem reanalysis | reaches **188 / 1,882 = 10.0%** — the stem must already be a KNOWN word, so it is structurally silent on a genuinely novel form | **BF, correctly silent** — not a defect, a scope fact |
| **5. sequence model** (order-2 + fixed-lag-2 revision) | a graded posterior | the point readout | nothing lost here; the two-word revision window already equals whole-sentence smoothing (0.9264 both) | **BF** |
| **6. hand-off DOWN to heads** | a **graded posterior**; mean top-category mass on an unseen token **0.8965** | the live default reads the **HARD argmax** | **~10% of the belief is discarded exactly where the organ is least certain.** `arc_scores_graded` exists and measures 0.5400 vs 0.5362 hard, but is not the live default | **NOT BF at the hand-off** — unfixed, and the single clearest remaining loss |

---

## 3. WHAT WAS BUILT, AND WHAT EACH LEVER WAS WORTH

Full UD-EWT test, paired bootstrap over sentences, 2,000 resamples, floor recomputed in-place. *(`metrics.json` = the 14-arm ablation; `metrics_headline.json` = the load-bearing headline; `metrics_graded_parse_sweep_from_log.json` = the graded-parse sweep, with its provenance caveat stated in the file.)*

| arm | unseen | Δ unseen (CI) | overall | PROPN↔NOUN |
|---|---|---|---|---|
| **A0_live (FLOOR)** | 0.7519 | — | 0.9278 | 163 |
| position-aware capitalisation only | 0.7582 | +0.0064 [0.0006, 0.0124] ✔ | 0.9272 | 161 |
| productivity stratum only | 0.7614 | +0.0096 [−0.0038, 0.0230] ✘ | 0.9289 | 172 |
| rich orthographic alphabet only | 0.7747 | +0.0228 [0.0156, 0.0308] ✔ | 0.9295 ✔up | 176 |
| slot cue (κ 0.5), + rich + position + stratum | 0.7848 | +0.0329 [0.0169, 0.0492] ✔ | 0.9296 | 170 |
| graded parse θ=3 (+ rich + position + stratum) | 0.8002 | +0.0484 [0.0328, 0.0647] ✔ | 0.9311 ✔up | 176 |
| graded parse θ=10 | **0.8045** | +0.0526 [0.0367, 0.0698] ✔ | 0.9306 | 178 |
| **A7b_g05 — RECOMMENDED** (rich + position + stratum + graded parse θ=3 + prior γ=0.5) | **0.8002** | **+0.0484 [0.0326, 0.0651] ✔** | **0.9313 ✔up** | **159** |
| **TWIN of the recommended arm** | **0.3555** | −0.3964 ✔ *below the floor* | 0.8420 | 215 |

**Knowledge form (plastic, never frozen).** Cues 1 and 3 are accrued count tables (`shape_pos`, `shape_pos_w`); the slot cue is two more. Cue 2 — the productivity stratum, and with it the suffix, shape and prior tables the unknown-word read uses — is **DERIVED IN `finalize` from the emission counts the organ already keeps**, so it re-derives itself on every `observe()` with no new accrual at all. Verified: one `observe` grew the novel-type count 10,453 → 10,454 and the shape/position counts with it.

---

## 4. WHAT MADE THE BIG WINS BIG *(the owner's addendum: was the mathematical chain cracked to the top?)*

**Yes, and the three largest levers are the same fix wearing three hats: a rung that was handing down a POINT or a CONFLATED value where the brain hands down a GRADED or FACTORED one.** That is the whole story of this problem, and it is why the gains compounded instead of trading off.

| rung | the brain computation | the math replicated | where the graded signal was kept | worth |
|---|---|---|---|---|
| morpho-orthographic parse | parallel activation of every plausible segmentation, alternatives kept alive by reliability | successive abstraction up the suffix ladder, mixed by the organ's **own** shrinkage `a = n/(n+θ)` — the identical form it already uses for rare words | the estimate is now a **mixture over parses** instead of an argmax over parses | **+0.0484** |
| form description | the word-form system's actual alphabet: case, digits, internal punctuation, ALL-CAPS length | 19 symbols × 2 positions as one count table, denominator = the alphabet (a property of the writing system), not the observed-symbol count | the description is **factored**, not collapsed to `digit`/`other` | **+0.0228** |
| cue integration | a cue's weight rises when its competitors are silent | the slot channel gated on the **absence of a lexical entry** — fires on 7.5% of tokens, not all of them | the competition stays **graded**; the blanket version (which is not this computation) is refuted at 0.9152 | **+0.0329** |
| emission slot | Bayes: the slot takes `P(evidence \| c)` | divide the marginal novel-form prior back out, γ swept | the transition prior is now the **only** place the prior enters, at strength γ | PROPN↔NOUN 176 → **159**, overall to its best 0.9313 |

**Where the chain is NOT cracked — the rungs still handing down a point estimate or a conflated value** (each is a live, numbered opportunity, none of them mine to land):
1. **The hand-off to heads is a hard argmax** while the organ holds a posterior whose mean top mass on an unseen token is **0.8965**. The graded path exists and is measured (0.5400 vs 0.5362). This is the clearest remaining loss in the chain.
2. **The reading-acquired inventory hands down one class id, not a distribution**, and is silent on **1,333 of 1,882** unseen tokens.
3. **Tokenisation hands a code/date/URL down as one opaque symbol** (305 unseen tokens). The patch reads the *pattern*; nothing reads the *parts*.
4. **The category ACQUISITION source is still the offline labelled tag column** — the organ's own registry note already flags this as the remaining MODEL element, and it is the biggest one.

---

## 5. THE HALF OF THE BAR THAT WAS MISSED — WITH AN ORACLE, NOT AN EXCUSE

The bar asks for **PROPN↔NOUN down by a third** (163 → ≤ 109). I got **159 (−2.5%)**. Here is the numbered reason.

**It is not an additive error pool; it is a symmetric trade-off on one shared cue.** The mechanism diagnostic (`--explain`) shows exactly what the arm did to those two classes: **PROPN→NOUN fell by 22** (117 → 95) and **NOUN→PROPN rose by 18** (46 → 64). Sharpening the name evidence converts misses in one direction into misses in the other, because both directions are decided by the *same* capitalisation evidence.

**The oracle bounds it.** Applied as a hard rule to unseen tokens, *"a capital in a non-forced position ⇒ PROPN"* scores **precision 0.812, recall 0.658** (tp 500, fp 116, fn 260). You cannot buy recall without paying precision; the criterion slides along one curve.

**And the residual is not made of form-resolvable items.** Decomposing the 163 by the form description:

| slice | count | resolvable from the form? |
|---|---|---|
| PROPN→NOUN, capital in a non-forced position | 52 | yes in principle — but see the trade-off above |
| NOUN→PROPN, capital in a non-forced position | 20 | pulls the criterion the **opposite** way |
| PROPN→NOUN, **lower-case** gold names | 29 | **no — there is no capitalisation cue to read** |
| acronyms (ACRO/ALLCAP, both directions) | 29 | **no from form** — `AMS`/`MSM`/`IIP` are PROPN and `TV`/`CEO` are NOUN with identical form |
| the rest (codes, mixed case, digits) | 33 | partly, and already taken |

**What the residual actually needs, and it is not a form cue.** The examples are decisive: *`Gmail` after "a"; `the Gateses`; `the MSM`; `the AMS`; `the Europeans`; `The IIP`.* Nine of fourteen sampled PROPN→NOUN misses sit **after a determiner** — so the linguist's rule the brief proposed ("`the` before a word says common noun") would have made these *worse*, and the learned slot table is right to encode `P("the" | PROPN) > 0` instead of a rule. What separates `the MSM` (PROPN) from `the CEO` (NOUN) is **whether the string is being used to pick out an individual** — that is the entity layer, which the brief itself says this decision *feeds*. **The dependency runs both ways and the substrate only wires one direction.**

**What it would take to make it fully solved:** a top-down path from the entity layer back into the category competition (predictive coding: the situation model's belief that a referent is an individual re-enters the category posterior as a prior on PROPN). That is a cross-organ wire, not a cue inside this organ, and it is the single highest-value follow-on this work exposes.

**Path A was identified and tried once** — see §6, `A9_joint`. It did not close the gap. **The cheapest remaining path (the slot cue at κ=1.0, the only arm that reduced PROPN↔NOUN on its own, 163 → 154, combined with γ=0.5) was NOT run: that specific full-scale arm run was a DENIED tool call, and per the operating rules I did not perform it another way.** It is the first thing to measure when this is picked up, and it is why the slot cue ships **default-OFF** in the patch with its counts already accrued (a re-measure, not a rebuild).

---

## 6. NEGATIVES, EACH UNDERSTOOD MECHANISTICALLY WITH A NUMBER

1. **Position-aware capitalisation alone is small (+0.0064) and left PROPN↔NOUN flat (163 → 161).** *Why:* I checked the log-odds the cue actually carries before blaming the implementation. Position-blind `Cap` = PROPN 10,224 / PRON 5,257 / NOUN 2,554 / DET 1,397; split by position, `Cap@mid` = PROPN 8,918 / NOUN 1,885. The **dilution was on the PRON/DET side, not the PROPN/NOUN side** — the PROPN-vs-NOUN likelihood ratio only moves from ~11.3 to ~13.5. The cue is real and correctly built; it simply does not target the confusion the brief expected it to.
2. **The productivity stratum alone is not CI-separated (+0.0096, CI [−0.0038, 0.0230]).** *Why:* hapax re-estimation sharpens the tables (hapax-TYPE `Cap@mid` is 0.91 PROPN against 0.66 for the token table) but it also **shrinks every table's mass**, so it adds variance as fast as signal — until it is paired with the graded ladder, which is what turns thin cells from a liability into a back-off step. Together they are +0.0484. **The stratum is a precondition, not a lever.**
3. **Full prior-division (γ = 1.0) is catastrophic: unseen 0.6347 at smoke (−0.1545 CI-sep).** *Why:* removing the whole marginal prior over-promotes the genuinely rare categories (X, INTJ, SYM). It *does* do what it was built to do — PROPN↔NOUN fell 20 → 9 at smoke — which is what identified γ as an **operating point** rather than a boolean. γ = 0.5 keeps the PROPN↔NOUN gain (159) and the accuracy (best overall, 0.9313). *The two priors are not the same object — the transition supplies a contextual prior, the suffix posterior a marginal one — so the correct γ was never going to be 1.*
4. **PATH A — the joint form cell — wins at smoke and does NOT replicate at full scale.** Running the abstraction ladder *inside* the form cell (`P_novel(c | shape@pos) → P(c | suffix, shape@pos)`) is the more brain-faithful statement (the word-form system delivers **one** description, not two independent ones). At 1,500 supply sentences: **0.858 vs 0.829 separable**. At the full 12,544: **0.8002 — exactly the separable arm — with PROPN↔NOUN worse (174 vs 159).** *Why:* conditioning multiplies the number of cells by the alphabet; once each marginal table is well estimated the independence approximation is nearly exact, and the joint cells are sparser than the marginals are wrong. **Kept behind a switch, because the balance flips back for a smaller or a genuinely reading-acquired supply — which is the regime this organ is heading for.**
5. **The right-hand head rule on unseen compounds is a clean negative: 0.439 where the organ already scores 0.791 on the same 139 tokens.** Williams' rule is real, but it presupposes a *correct* compound parse, and splitting a string against a lexicon does not deliver one — `hostage`→host+age, `commits`→comm+its, `Hamdan`→ham+dan; **78 of 139 splits are spurious**. *Not a wall: the missing input is a parse-plausibility score (Hay & Baayen's parsing ratio), which is a segmenter-level job, not a cue.*
6. **The brief's own hypothesis that the residual is web noise is refuted by a count: 149 of 1,882 unseen tokens (7.9%) are web-shaped.** The residual is ordinary novel words and names.
7. **My first twin was vacuous and the twin itself caught it** (0.8559 against the arm's 0.8580, because the shuffle did not reach the joint tables). Recorded because a control that excludes nothing is not a control.

---

## 7. WHAT STRATEGY SHOULD LAND, AND WHAT TO CHECK

**`lexical_categories_patch.diff`** (446 lines against the current `hdlab/lexical_categories.py`; `git apply --check` clean). Defaults = exactly the measured arm: `UNK_RICH_SHAPE=1`, `UNK_POS_SHAPE=1`, `UNK_NOVEL_MAX=2`, `UNK_SUF_THETA=3.0`, `UNK_PRIOR_GAMMA=0.5`, `UNK_JOINT_SHAPE=0`, `UNK_SLOT_KAPPA=0`.

- **`HDLAB_LC_UNK_NOVEL_MAX=0` restores the pre-2026-09-13 unknown-word path exactly** — verified: loading the CURRENT live asset with the cues off gives max posterior difference **0.0** and 0 tag differences on 6,305 tokens, with the legacy position-blind fallback firing (old assets keep working).
- **The asset must be rebuilt** (`build_asset()`); the candidate is at `data/hook_state/lexical_categories_counts_v1_unkcues_candidate.json` (2.0 MB, written by the patched module, save/load round-trip verified). **The live asset was not touched.**
- **Rebuild the PENN arm too** — it gains independently (xpos 0.9176 → 0.9227 CI-sep).
- **⚠️ Verification I did NOT complete:** the apply-then-byte-compare test of the diff against the verified module was a **denied** tool call and was not run another way. `git apply --check` passes; please byte-compare after applying.
- **Not measured by me:** the board (`exp_situation_model_qa_modern_v1.py --run`) — it needs the patched module on the live path, which is strategy's step. The brief flags `common_noun_coref` (0.5671) and `coref` (0.4681) as the dimensions that depend on the name/common-noun split; PROPN↔NOUN moved only −2.5%, so I would **predict board-neutral** and say so in advance rather than after.

**AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`:** the `lexical_categories` entry should record that the *unknown-word sub-computation* was the least brain-foundational part of an otherwise BF_SPIRIT organ — a hard single-suffix commitment (a point estimate where the module's own cited account keeps alternatives alive), a position-blind orthographic symbol, a frequency-weighted evidence base for a productivity question, and a doubled category prior — and that all four are now count-based and graded. The organ's status is unchanged (BF_SPIRIT; the acquisition source is still the offline supply).

**NEXT PROBLEMS this exposes, in priority order:** (1) **the entity layer → category top-down wire** (§5 — the only route to the PROPN↔NOUN third); (2) **make the graded posterior the live hand-off to heads** (10% of the belief is discarded at the point the organ is least certain); (3) **grow the reading-acquired inventory's coverage** (zero cue on 1,333 of 1,882 unseen tokens) — measured on held-out words, as the brief insists; (4) **a morpho-orthographic segmenter with a parse-plausibility score**, which would make negative 5 buildable.

**CONSUMED INPUTS** (for `CROSS_SOLUTION_IMPROVEMENT_MAP.md`): the UD-EWT tag column as offline supply; `induced_categories` v2 (`word2cat`); `hdlab/morphology` (the stem route). **FLAGGED UPSTREAM WALLS:** the labelled acquisition source; the induced inventory's coverage; tokenisation. **DOWNSTREAM CONSUMERS TOUCHED:** `attachment_arm` (measured, no regress), the Penn arm → `temporal_model` (measured, gains).

## KEY REALIZATIONS

- **The lever was not the cue the brief named; it was the *shape of the estimate*.** Position-aware capitalisation — the brief's headline hypothesis — is worth +0.0064. Replacing a **hard argmax over segmentations with a reliability-weighted mixture** is worth +0.0484. I found that only by computing the log-odds the position cue actually carries *before* concluding anything about it, and by counting what the incumbent estimator commits to (a 4-character suffix for 1,056 of 1,882 unseen tokens, 322 of them on ≤ 2 observations).
- **Read the module's own docstring as a specification and check whether it is obeyed.** This organ cites MacDonald 1994 "keep the alternatives alive" at the top of the file and then takes an argmax over suffix parses inside `_log_emit_unknown`. The biggest win was making the code do what its own comment claimed.
- **A quantity that goes up is not the quantity in the bar.** Unseen accuracy rose 4.8 points while PROPN↔NOUN barely moved, because PROPN→NOUN fell 22 and NOUN→PROPN rose 18 — a symmetric trade on shared evidence. Only the per-(gold,pred) confusion *delta* showed that; the headline number hid it completely.
- **Let the counts overrule the linguistic rule.** "`the` before a word says common noun" is in the brief and is *wrong for this population* — `the MSM`, `the Gateses`, `the Europeans` are gold PROPN. The learned frame table encodes the real conditional; a hand-written rule would have cost points.
- **A twin that leaves the winning arm's own table alone is not a twin.** Mine scored 0.8559 against the arm's 0.8580 and I nearly read that as "the cue is uninformative". The control was broken, not the arm.

---

# ROUND 2 — the supervisor's probe: understanding closed by research, path A tried twice, the opportunity space bounded

## 8. WHAT I DID NOT YET UNDERSTAND, AND WHAT THE RESEARCH CHANGED

Three gaps, closed by reading rather than guessing.

**(a) The determiner cue is a PINNED developmental result and I had its shape wrong.** Katz, Baker & Macnamara 1974 (*Child Development* 45:469–473, "What's in a name? A study of how children learn common and proper names"): a 17-month-old hearing *"This is DAX"* takes DAX for an individual's **name**, and hearing *"This is a DAX"* takes it for a **common noun**. Replicated and extended by Gelman & Taylor 1984 and by [Hall 2003](https://onlinelibrary.wiley.com/doi/abs/10.1111/1467-8624.00622) on form-class cues to descriptive proper names. **The cue is the PRESENCE OR ABSENCE of a determiner, not the identity of one.** My round-1 slot cue put ~300 neighbour *word identities* on unseen tokens — that representation cannot encode *absence* at all, and it is ~33× sparser than it needs to be. The correct form is a small table over the **function-word class** of the context with `bare` as its own symbol. That is what round 2 built, and it is a different computation from the round-1 cue, not a re-weighting of it.

**(b) The proper-name capitalisation cue is orthographic and is used online during reading.** [Peressotti, Cubelli & Job 2003](https://pubmed.ncbi.nlm.nih.gov/12852936/) — the orthographic cue hypothesis — show the proper-name advantage survives when semantic, morphological and lexical accounts are ruled out, and that initial capitalisation acts "as a clue to which category the word belongs"; [Cutter et al.](https://pure.mpg.de/rest/items/item_3158689_5/component/file_3239202/content) show readers use *parafoveal* capitalisation to infer syntactic category mid-sentence. This confirms the cue is real and read early — and it is exactly why its *ceiling* (§5) is a fact about English orthography rather than about our implementation.

**(c) The graded hand-off — I over-claimed its cost in round 1, and measuring it corrected me.** I wrote that the hard argmax "discards ~10% of the belief". That is true of the *mass* and misleading about the *cost*. Measured on the full live chain (`arc_scores_graded` vs `heads`, UD-EWT test 700): **at the floor the graded readout buys +0.0027 UAS (0.5969 → 0.5996); under the improved organ it buys only +0.0011 (0.5988 → 0.5999).** Improving the upstream organ *shrinks* the value of the graded hand-off, because a better-calibrated organ is confident where it is right. **Correction to my own round-1 §4 item 1: a real but small hand-off loss (~0.3 UAS points), not the chain's dominant leak.**

## 9. PATH A, TRIED TWICE, MEASURED THE SAME WAY

Full UD-EWT test, 2,000-resample paired bootstrap over sentences, floor recomputed in place.

| arm | unseen | Δ unseen (CI) | overall | **PROPN↔NOUN** |
|---|---|---|---|---|
| **A0_live (floor)** | 0.7519 | — | 0.9278 | **163** |
| round-1 recommendation (A7b_g05) | 0.8002 | +0.0484 [0.0326, 0.0651] ✔ | 0.9313 | 159 |
| **path A-1** joint form cell | 0.8002 | +0.0484 [0.0314, 0.0658] ✔ | 0.9301 | 174 ✘ |
| **path A-2** Katz determiner context κ 0.5 | 0.7981 | +0.0462 [0.0299, 0.0628] ✔ | 0.9311 | 160 |
| Katz context **alone, on the bare floor** | 0.7497 | −0.0021 n.s. | 0.9276 | **151** |
| **C1_lr05 — RECOMMENDED** (two-sided Katz frame, κ 0.5 each side) | **0.8002** | **+0.0484 [0.0322, 0.0643] ✔** | **0.9312 ✔up** | **154** |
| two-sided frame **alone, on the bare floor** | 0.7529 | +0.0011 n.s. | 0.9275 | **144** |
| frame κ 1.0 | 0.7965 | +0.0446 ✔ | 0.9310 | 154 |
| frame κ 1.0, γ 0.75 | 0.7811 | +0.0292 ✔ | 0.9294 | 153 |
| frame κ 1.5 | 0.7821 | +0.0303 ✔ | 0.9298 | 157 |
| frame κ 2.0 | 0.7699 | +0.0181 n.s. | 0.9289 | 155 |
| **twin of C1_lr05** | **0.3714** | −0.3804 ✔ *below the floor* | 0.8426 | 215 |

**The Katz frame behaves exactly as the developmental literature says it should, and that is the strongest evidence it is the right computation:** on the bare floor it changes overall accuracy by nothing (+0.0011, n.s.) while cutting the name/common-noun confusion by **19** (163 → 144). It is a *name* cue, not a general one. In combination it holds the full accuracy gain and takes the confusion to **154**.

**The confusion is now bounded from four directions.** Across **25 measured arms** spanning six brain-foundational cues and their weight sweeps, PROPN↔NOUN never falls below **144**, and never below **153** while keeping the accuracy gain. The bar wants **≤ 109**. Raising the frame weight past 0.5 buys nothing on the confusion and costs up to 3 points of unseen accuracy — a measured plateau, not an assertion.

**Understood negative (path A-1, the joint form cell).** It wins at small supply (1,500 sentences: 0.858 vs 0.829) and ties at full supply (12,544: 0.8002), with the confusion worse (174). *Mechanism:* conditioning multiplies the cells by the alphabet, so once each marginal table is well estimated the independence approximation is nearly exact and the joint cells are sparser than the marginals are wrong. **Kept behind a switch because the balance flips back for a smaller or a reading-acquired supply — the regime this organ is heading for.**

## 10. WHAT WOULD IT TAKE TO MAKE THE PROPN/NOUN HALF FULLY SOLVED

**Not a form cue and not a frame cue — the arithmetic is closed:**

- of the 163 confusions, **58 are structurally form-free** — 29 lower-case gold names and 29 acronyms whose form is identical to common-noun acronyms (`AMS`/`MSM`/`IIP` are PROPN; `TV`/`CEO`/`DVD` are NOUN);
- the capitalisation oracle is **precision 0.812 / recall 0.658** — one criterion on one curve, so buying recall pays in precision (measured: PROPN→NOUN −22 bought NOUN→PROPN +18);
- the Katz frame in its correct pinned form is worth **−19 in isolation, −9 in combination**;
- the induced-inventory coverage gap is worth **at most 78 unseen tokens, and shrinking** (§11).

**What remains is a different kind of evidence: whether the string is being used to pick out an INDIVIDUAL.** `the MSM`, `the Gateses`, `the Europeans` are gold PROPN *with* a determiner; `the CEO` is NOUN. No form or local frame separates them. That evidence lives in the entity layer — which, per the brief, this decision *feeds*. **The dependency is bidirectional and the substrate wires only one direction.** ALTERNATE PATH 1.

## 11. WHAT GROWING THE READING-ACQUIRED INVENTORY WOULD BUY — A BOUND, NOT A CLAIM

The induced inventory fires on 549 of 1,882 unseen tokens; 1,333 get exactly zero.

| | covered (n=549) | uncovered (n=1,333) | gap | tokens if uncovered reached covered accuracy |
|---|---|---|---|---|
| at the floor | 0.8233 | 0.7224 | 0.1009 | ≤ 135 |
| **under C1_lr05** | 0.8415 | 0.7832 | **0.0583** | **≤ 78** |

**Two honest reads.** (i) The upper bound is **≤ 78 unseen tokens ≈ +4.1 points of unseen accuracy**, and it is badly confounded — the covered words are the ones simple-Wikipedia happens to contain, i.e. ordinary words that are easier anyway. (ii) **The new cues have already absorbed 42% of the coverage gap** (0.1009 → 0.0583). Growing the inventory is therefore a *smaller* lever after this work than before it — the opposite of what I would have guessed. Reported as a shrinking bound, not as a projected gain.

## 12. ALTERNATE PATHS — similarly or more brain-foundational, written so strategy can file them

**PATH 1 — the entity → category top-down wire.** *(The one the measurements point at; the most brain-foundational thing left.)*
*Structure:* the anterior-temporal / medial-temporal referent system projecting back onto the posterior-temporal category competition. *Computation:* predictive coding (Kuperberg & Jaeger 2016; Rao & Ballard) — the situation model's current belief that a discourse referent is an **individual** (a token with an identity file) rather than a **kind** re-enters the category posterior as a prior on PROPN, exactly as the transition prior already does. *Math:* one additive log-prior term in `_log_emit`, `log P(c | referent-is-individual)`, a count table accrued from the entity layer's own resolved chains — the same shape as every cue landed here, so no new machinery. *Cost:* medium — the join does not exist; the entity layer must expose a per-token individual-vs-kind belief at read time. *Why not now:* a cross-organ wire, outside a single-organ brief, and it needs the entity layer's signal to be graded first. **The only path the measurements say can reach the missed third.**

**PATH 2 — discourse-level capitalisation and repetition consistency.**
*Structure:* episodic/discourse memory (MINERVA-2 trace accumulation over the document). *Computation:* a novel string that recurs, and recurs capitalised in non-forced positions, is a name; one that alternates case is not. *Math:* per-document type counts of `shape@position`, decayed, read as one more emission. *Cost:* low. *Why not now:* **our evaluation unit is the sentence** — the organ is handed one sentence at a time, so there is no document context to accumulate, and an honest measurement needs a document-level gold.

**PATH 3 — a morpho-orthographic segmenter with a parse-plausibility score.**
*Structure:* the same visual word-form system, one level deeper. *Computation:* Hay & Baayen's parsing ratio — take a decomposition only when the parsed route beats the whole-word route in relative frequency. The module already runs exactly this frequency race for the lemma dual route (`COLLISION_RATIO`), so the mechanism is in the building. *Math:* score each split by the relative frequency of its parts vs the whole, then apply Williams' Right-hand Head Rule above threshold. *Cost:* medium. *Why not now:* the naive version is a measured negative — **0.439 where the organ already scores 0.791**, because **78 of 139 lexicon splits are spurious** (`hostage`→host+age, `Hamdan`→ham+dan). The missing input is the plausibility score, which is a segmenter-level build, not a cue.

**PATH 4 — make the graded posterior the live hand-off to heads.**
*Structure/computation:* keep alternatives alive across the rung boundary instead of committing (MacDonald 1994). *Math:* `arc_scores_graded` already exists and is exact. *Cost:* very low — a default flip. *Why not now, honestly:* **I measured it and it is small** — +0.0027 UAS at the floor, +0.0011 under the improved organ. Worth doing for fidelity, not for the number; I would not sell it as a lever.

**PATH 5 — replace the labelled acquisition supply with the reading-induced inventory.**
*Structure:* the organ's own acquisition arm (`induced_categories`, BF). *Why it belongs here:* it is the **largest remaining MODEL element in this organ** — its own registry note says so — and everything measured in this brief sits on top of an offline labelled tag column. *Cost:* high. *Why not now:* the hand-off already measures UAS 0.44–0.45 under induced categories vs 0.57 under UPOS, and the binding constraint there is ROOT identification, separately filed. **The interaction is the useful part: these cues are strongest exactly where the supply is thin (path A-1 won at 1,500 supply sentences and tied at 12,544), so every κ, θ and γ here must be RE-SWEPT, not assumed, when the supply becomes the reading-induced one.**

## 13. GAPS — steps not performed, and not worked around

1. **The full-scale sweep of the remaining prior-gamma / theta / slot-combination arms was a DENIED tool call.** Not re-run in any form. Consequence: γ has one full-scale point (0.5) plus a smoke reading of 1.0, and the slot cue's combination with the graded parse is unmeasured — which is why the round-1 slot cue ships **default-OFF** with its counts accrued (a re-measure, not a rebuild). The round-2 Katz frame is a *different* computation and is measured and on.
2. **The apply-then-byte-compare test of the diff was a DENIED tool call.** Not re-run in any form. `git apply --check` passes and the patched module itself is verified (max posterior difference 0.0 on both the regression and the equivalence check); **please byte-compare after applying.**
3. **The board was not run** — it needs the patched module on the live path, which is strategy's step. Given PROPN↔NOUN moved −5.5%, I predict **board-neutral** and record the prediction in advance.
