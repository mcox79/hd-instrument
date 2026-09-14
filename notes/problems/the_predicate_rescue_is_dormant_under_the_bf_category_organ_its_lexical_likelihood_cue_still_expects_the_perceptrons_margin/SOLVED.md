---
problem: the_predicate_rescue_is_dormant_under_the_bf_category_organ_its_lexical_likelihood_cue_still_expects_the_perceptrons_margin
status: SOLVED
bar: "PASS = the rescue FIRES on the live chain: recovery of mis-tagged real verbs CI-separated above (a) the dormant stand-in (the bare posterior threshold read) and (b) an information-free twin (random promotion at the matched rate), at a false-verbs-per-sentence budget no worse than the perceptron-era detector's (0.466/sent modern); end-to-end event recall through SituationReader.read() up with the flag ON vs OFF on modern gold; the 7-dimension modern board not down; knowledge as counts with an online observe path; verification/test_predicate_recall_landing_organ.py green under the live tagger -- OR a numbered located negative naming which upstream quantity blocks it."
result: "THE RESCUE FIRES. Under the live brain-foundational category organ the landed rescue was DORMANT: the 2026-09-13 stand-in (post[i]['VERB'] >= 0.3) added ZERO events to the landing witness and recovered 0.2768 / 0.2250 / 0.2385 of the real verbs the organ drops (UD-EWT test / GUM / QA-SRL dev). Re-deriving its noisy-channel LEXICAL LIKELIHOOD from the organ that replaced the perceptron -- the per-lexeme noun/verb bias read straight off the EMISSION COUNTS, the lemma organ's stem route, and the one-predicate-per-clause COMPETITION read as a normalised share of the posterior -- and combining it with six register-invariant structural cues by RESCORLA-WAGNER error-driven cue competition over counts, recovery at a false-verb budget of 0.10/sentence (a FIFTH of the perceptron-era 0.466) is 0.7054 (UD-EWT test, n_pos=112) / 0.5616 (GUM/GENTLE, n_pos=511) / 0.6823 (QA-SRL dev, n_pos=960), 5-fold CV over sentences. Against the DORMANT live read: +0.4293 CI[+0.3301,+0.5264] / +0.3368 CI[+0.2877,+0.3849] / +0.4438 CI[+0.4113,+0.4771], all CI-SEPARATED. Against the INFORMATION-FREE TWIN: +0.6138 CI[+0.5289,+0.6980] (twin p95 0.1339) / +0.4693 CI[+0.4298,+0.5080] (p95 0.1115) / +0.5590 CI[+0.5325,+0.5857] (p95 0.1406), all CI-SEPARATED. Against the STRONGEST floor actually run -- the SAME stand-in cue with its threshold swept to the same budget (0.6875 / 0.4932 / 0.4771): +0.0177 CI[-0.0566,+0.0909] ns (UD-EWT, n_pos=112, underpowered) / +0.0688 CI[+0.0232,+0.1148] SEP / +0.2052 CI[+0.1717,+0.2413] SEP -- CI-separated on BOTH well-powered populations. END-TO-END through the LIVE SituationReader on modern gold (UD-EWT test, 2077 sentences, 2605 gold verbs; the arms reproduce the live reader byte-exactly, 0/300 sentences mismatched): event recall 0.9186 (OFF) -> 0.9305 (dormant stand-in) -> 0.9501 (BF), +0.0315 CI[+0.0249,+0.0384] vs OFF and +0.0196 CI[+0.0136,+0.0260] vs the stand-in, both CI-SEPARATED, at 0.176 false events/sentence (OFF 0.078) and event precision 0.9370 -> 0.8715. THE 7-DIMENSION MODERN BOARD IS NOT DOWN: run A/B with the rescue monkeypatched to the proposed diff, aggregate 0.6109 -> 0.6109 (+0.0000), 5/7 dimensions CI-separated over their floor in BOTH arms; per dimension coref / common_noun_coref / salience / who_did_what_agent / wic byte-identical, who_did_what_patient +0.0008 (n=1255), state -0.0026 (n=378 -- exactly ONE item). THE LANDING WITNESS IS GREEN under the patch: verification/test_predicate_recall_landing_organ.py 30/30 including the new live-chain section (it FAILS on disk today at 'flag-ON adds recovered predicates overall (3 > 3 events)'). The combiner is PLASTIC (associative strengths updated one observation at a time by the delta rule; `observe(cues, label)` is the live online path -- the witness measures a score moving 0.0012 -> 0.9772 over 80 outcomes) and the gate no longer imports nltk at inference (the glass-box morphology organ agrees with the WordNet gate on 5612/5629 UD-EWT word types, 0.99698)."
floor: "(1) THE DORMANT STAND-IN as deployed -- post[i]['VERB'] >= PREDICATE_RESCUE_MIN_P = 0.3 on the live category organ: recovery 0.2768 @ 0.0154 false verbs/sent (UD-EWT test), 0.2250 @ 0.0300 (GUM), 0.2385 @ 0.0245 (QA-SRL). (2) predicate_recall OFF: recovery 0.0 by construction (a dropped verb emits no event). (3) THE STRONGEST FLOOR ACTUALLY RUN, and the one that matters: the SAME cue with its threshold swept to each budget -- 0.6875 / 0.4932 / 0.4771 at fp<=0.10, 0.9554 / 0.8650 / 0.8760 at fp<=0.50. Roughly HALF the recovered signal was the mis-set bar, not the cue: on QA-SRL the decomposition is 0.2385 (dormant) -> 0.4771 (threshold calibrated, same cue, +0.2386) -> 0.6823 (the BF cue block, +0.2052)."
controls: "(1) INFORMATION-FREE TWIN (random promotion of the same number of gated candidates) loses CI-separated on all three populations; the sampled twin's own mean and p95 are reported beside every arm. (2) PAIRED BOOTSTRAP over SENTENCES (2000 resamples) for every delta; CI half-widths 0.027-0.085. (3) HELD-OUT: 5-fold cross-validation over SENTENCES -- no candidate is scored by a model that saw its own sentence; the shipped asset's threshold is reported both full-fit and held-out. (4) THREE MODERN POPULATIONS, two of them entirely outside the organ's count supply (GUM/GENTLE 12+ genres by stride so every genre is represented; QA-SRL dev). 19c is NOT measured (owner ban). (5) ABLATIONS: every channel alone is far weaker than the combination (fp<=0.10, QA-SRL: clause share alone 0.2646, lexical bias alone 0.2917, posterior log-odds alone 0.3812, the six structural cues alone 0.2792, vs 0.6823 combined) -- the COMBINATION is the mechanism, exactly as the parent found. (6) GATE EQUIVALENCE: the glass-box morphology gate vs the landed nltk WordNet gate, 5612/5629 UD-EWT word types (0.99698). (7) ADDITIVE BY CONSTRUCTION: a token the category organ already called VERB or AUX is never touched, so the existing detections stay byte-identical (verified in the witness). (8) THE ARMS ARE THE READER: the end-to-end arms were cross-checked against a live SituationReader on 300 sentences -- 0 mismatches for both OFF and the stand-in. (9) PATCH == CELL: the proposed hdlab diff reproduces the experiment cell's scorer to 0.0 over 4757 tokens / 250 sentences, with identical rescue sets."
files_changed: "experiments/exp_predicate_rescue_bf_cue_v1.py (the cell), data/hook_state/predicate_detector_bf_counts_v1.json (the new asset -- strategy swaps it into data/frontend_assets/ on integration), notes/problems/<slug>/{SOLVED.md, predicate_detector_bf_patch.diff} (the proposed diff against hdlab/predicate_detector.py + the _rescue branch of hdlab/situation_reader.py + verification/test_predicate_recall_landing_organ.py). NO hdlab/ or verification/ file changed on disk."
reverify: ".venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --self-test  (fast); then --full --gate-control (~30 min, rows cached in data/exp_predicate_rescue_bf_cue_v1/) and --reader --reader-cap 2100 (~35 min). After the diff is applied: .venv/Scripts/python.exe verification/test_predicate_recall_landing_organ.py"
---

# SOLVED -- the rescue's lexical likelihood was the perceptron's; the category organ computes it from counts, and the bar it was being compared to was the real defect

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk -- the mechanism is proved in
`experiments/` and the exact `hdlab/` diff is proposed below for strategy to land.

---

## 0. What was actually broken, measured first

Running the landed witness on disk, before building anything:

```
$ .venv/Scripts/python.exe verification/test_predicate_recall_landing_organ.py
  PASS detector rescues the real verb 'presents' (p=0.926 >= th=0.339)      <- the PERCEPTRON path
  ...
AssertionError: FAIL: flag-ON adds recovered predicates overall (3 > 3 events)   <- the LIVE path
```

The organ's own asset still scores perfectly against the perceptron it was fitted to. On the **live** chain it adds
**zero** events. Two separate defects were hiding behind that one line:

| # | defect | number |
|---|---|---|
| 1 | the lexical-likelihood cue (`verb_margin`) reads perceptron weights that no longer exist on the live path | the whole 7-cue combiner is bypassed |
| 2 | the 2026-09-13 stand-in that replaced it reads a **bare posterior against a fixed bar** (`P(VERB) >= 0.3`) | **72.3% / 77.5% / 76.2%** of the real verbs the organ drops sit BELOW that bar (UD-EWT test / GUM / QA-SRL) |
| 3 | the posterior reaches consumers through `tag_with_posterior`, which **truncates at P >= 0.01** | **5.4% / 15.3% / 12.4%** of dropped verbs arrive with NO verb entry at all -- a small real belief and zero are indistinguishable downstream |
| 4 | the landing witness asserted `SituationReader().predicate_recall is False` | the flag has been default-**ON** since 2026-09-05 -- the check was unreachable, so nothing guarded the wire |

---

## 1. The brain, and the chain rung by rung

**The structure.** Predicate-hood is a noisy-channel decision (Gibson 2013): a **lexical likelihood** -- how verb-like
is this word form, given what it usually does -- combined with a **structural prior**: one predicate per clause
(Spivey-Knowlton 1993), arguments flanking it (Mintz 2003 frequent frames), finite morphology (Monaghan 2005),
morphological decomposition on a separate route (Pinker & Ullman words-and-rules; Rastle & Davis 2008).

**The chain, and its brain-foundational status as the disk shows it:**

| rung | organ | status | what it hands down | what the rescue read | LOST |
|---|---|---|---|---|---|
| tokens | `text.split()` in the reader | trivial | strings | strings | -- |
| categories | `hdlab/lexical_categories.py` | **BF_SPIRIT** (count-based generative + forward-backward, plastic) | the full posterior `[n, T]` **and** the emission rows `log P(w \| c)` | a dict truncated at P>=0.01, then one number against 0.3 | the **emission channel entirely**; the low tail of the posterior; the graded shape |
| lemma / morphology | `hdlab/morphology.py` | **BF** (offline WordNet export, no nltk at inference) | `morphy(w, 'v')` | the landed gate imported **nltk at inference** | glass-box status |
| **this rung** | `hdlab/predicate_detector.py` | **was NOT_BF** (perceptron margin) -> **dormant stand-in** | -- | -- | the whole clause |
| events | `situation_reader._extract_events` | -- | `sm.events` | roles / coref salience / causal / timeline all read it | every downstream read of a dropped clause |

**The key observation.** The posterior the stand-in read is the likelihood and the structural prior **already
multiplied together**. The category organ computes the lexical likelihood separately -- its emission channel *is*
`log P(word | category)` from counts -- and that is exactly the quantity the perceptron's margin was a discriminative
stand-in for. So the cue is re-derived by replicating the OPERATION on the brain-foundational source.

---

## 2. What I built

### 2a. The cue block -- the organ's two channels, read separately

| cue | what it is | brain |
|---|---|---|
| `lex_bias` | `log(n(VERB,w)+lam) - log max_{c != VERB/AUX}(n(c,w)+lam)` -- the graded per-lexeme noun/verb bias, straight off the **emission counts** | Lee & Federmeier 2009, graded category competition |
| `stem_bias` | the same bias through the lemma organ's **rule route** (`_log_stem_prior`): *presents* = *present* + `-s`, and the stem is a known verb | Pinker & Ullman dual route; Rastle & Davis obligatory decomposition |
| `verb_share`, `clause_verb_share` | `post_i(VERB) / sum_j post_j(VERB)` over the sentence and over the **clause** -- one-predicate-per-clause as a **COMPETITION** | Spivey-Knowlton 1993 |
| `ctx_odds` | the settled belief as **graded log-odds**, not a probability against a fixed bar | -- |
| `subj_before_g`, `obj_after_g`, `frame_anchor_g`, `clause_verbless_g`, `clause_local_verbless_g` | the structural cues read off the **posterior** (`P(nominal) = P(NOUN)+P(PROPN)+P(PRON)`; "no verb here" = `1 - max_j P(VERB_j)`) instead of off the argmax tag | Mintz 2003; MacDonald 1994 constraint satisfaction |
| `morph_finite`, `rel_position` | unchanged from the landed organ | Monaghan 2005 |

Clause domains are cut with the closed-class cues a reader has **before any parse** (punctuation, coordinators,
subordinators). No parser, no treebank, no external tool at inference.

### 2b. The combiner -- error-driven cue competition, not a fitted weight vector

Two plastic forms were built and measured against each other over **identical binned cue units**, so the only thing
that differs is the learning rule:

- **naive Bayes over counts** (Christiansen & Chater multiple-cue integration): every weight is one pure function of
  two count tables.
- **Rescorla-Wagner** (1972; Ellis 2006, Ramscar et al. 2010 for language cues): `w += eta * (outcome - expectation)`
  over the present cue units, one update per observation.

**Rescorla-Wagner wins on every population** (recovery at fp<=0.10): QA-SRL 0.6823 vs 0.6292, GUM 0.5616 vs 0.4990,
UD-EWT 0.7054 vs 0.6964. The mechanism is the one the theory names: three of the cues (`ctx_odds`, `verb_share`,
`clause_verb_share`) are three reads of ONE channel, and naive Bayes counts that evidence three times while the delta
rule **blocks** it. The glass-box weight dump shows the blocking directly -- at the same bin, `verb_share` carries
+0.1275 and the redundant `clause_verb_share` carries -0.3046.

Knowledge is therefore **plastic, never frozen**: the asset stores associative strengths, `observe(cues, label)` is one
delta-rule update, and the witness checks that the score actually moves with experience.

---

## 3. Results

### 3a. Recovery of the real verbs the live organ drops (5-fold CV over sentences, fp <= 0.10 false verbs/sentence)

| population | n_pos | **dormant stand-in** (live, th=0.3) | stand-in, threshold swept | **BF rescue** | vs dormant | vs twin (p95) | vs swept |
|---|---|---|---|---|---|---|---|
| UD-EWT test | 112 | 0.2768 | 0.6875 | **0.7054** | +0.4293 CI[+0.3301,+0.5264] **SEP** | +0.6138 CI[+0.5289,+0.6980] **SEP** (0.134) | +0.0177 CI[-0.0566,+0.0909] ns |
| GUM/GENTLE | 511 | 0.2250 | 0.4932 | **0.5616** | +0.3368 CI[+0.2877,+0.3849] **SEP** | +0.4693 CI[+0.4298,+0.5080] **SEP** (0.112) | +0.0688 CI[+0.0232,+0.1148] **SEP** |
| QA-SRL dev | 960 | 0.2385 | 0.4771 | **0.6823** | +0.4438 CI[+0.4113,+0.4771] **SEP** | +0.5590 CI[+0.5325,+0.5857] **SEP** (0.141) | +0.2052 CI[+0.1717,+0.2413] **SEP** |

At the perceptron-era budget (fp <= 0.50) the same arm reaches 0.9286 / 0.9217 / 0.9333, still CI-separated over the
swept stand-in on both well-powered populations (+0.0569 / +0.0571).

### 3b. End-to-end through the LIVE reader (UD-EWT test, 2077 sentences, 2605 gold verbs)

The arms were cross-checked against a real `SituationReader` on 300 of those sentences: **0 mismatches** for both OFF
and the stand-in, so these are the reader's numbers.

| arm | event recall | event precision | false events / sentence |
|---|---|---|---|
| `predicate_recall=False` | 0.9186 | 0.9370 | 0.0775 |
| the dormant stand-in (live today) | 0.9305 | 0.9263 | 0.0929 |
| **the BF rescue** (fp<=0.10 point) | **0.9501** | 0.8715 | 0.1757 |

`BF - OFF` **+0.0315 CI[+0.0249,+0.0384] SEP**; `BF - stand-in` **+0.0196 CI[+0.0136,+0.0260] SEP**.
(`data/exp_predicate_rescue_bf_cue_v1/reader_end_to_end.json`.)
The full operating curve is in `data/exp_predicate_rescue_bf_cue_v1/reader_end_to_end.json`: recall rises
monotonically to 0.9608 at fp<=0.50 while event precision falls to 0.6820 -- **this is a recall-for-precision trade
at the event-set level, and it is reported as one**, which is why the deployed default is the tightest budget at which
the recall gain is still CI-separated over both floors.

### 3c. The board is not down (7-dimension modern board, A/B with the diff monkeypatched in)

| dimension | n | base (live today) | with the BF rescue | delta |
|---|---|---|---|---|
| coref | 3132 | 0.4681 | 0.4681 | +0.0000 |
| common_noun_coref | 2855 | 0.5671 | 0.5671 | +0.0000 |
| salience | 137 | 0.2555 | 0.2555 | +0.0000 |
| who_did_what_agent | 1423 | 0.8271 | 0.8271 | +0.0000 |
| who_did_what_patient | 1255 | 0.8072 | 0.8080 | +0.0008 |
| state | 378 | 0.7328 | 0.7302 | -0.0026 (one item) |
| wic | 120 | 0.7833 | 0.7833 | +0.0000 |
| **aggregate (19c-free)** | 9300 | **0.6109** | **0.6109** | **+0.0000** |

5/7 dimensions CI-separated over their floor in BOTH arms. The additive contract holds through every consumer,
exactly as the parent found when the same wire was measured at a 14x looser false-verb rate.
Artefacts: `data/exp_predicate_rescue_bf_cue_v1_board_{base,bf}/metrics.json`.

### 3d. The landing witness, under the patch

`verification/test_predicate_recall_landing_organ.py`: **30/30**, including the new live-chain section --
the BF rescue recovers *exactly* the dropped verb in each of three held-out modern UD-EWT sentences
(`own` / `land` / `mold`) with no false promotion, never touches a VERB/AUX token, and `observe()` moves a score
from 0.0012 to 0.9772 over 80 outcomes. On disk today the same file **fails**:
`AssertionError: FAIL: flag-ON adds recovered predicates overall (3 > 3 events)`.

### 3e. Where the signal was lost -- the decomposition

On QA-SRL (the best-powered population), at the same false-verb budget:

```
0.2385   the dormant live read  (bare posterior vs a fixed bar of 0.3)
  +0.2386   <- CALIBRATING THE BAR to an FP budget. Same cue. No new information.
0.4771   the same posterior, threshold swept
  +0.2052   <- THE CUE BLOCK: emission counts, the stem route, clause competition, graded structure
0.6823   the BF rescue
```

**Roughly half the recovered signal was a mis-set bar, not a missing cue.** That is the honest headline and it is the
part a reader of the original problem statement would not have predicted.

---

## 4. Every negative, understood

**(a) The exact replication of `verb_margin` on the BF source is the WEAKEST cue, and it INVERTS.**
`lex_llr = le[VERB] - max_{c != VERB/AUX} le[c]` is the literal same operation on the organ's emission rows. It scores
**-4.48 for 'sheet'** (never seen as a verb) against **-5.16 for 'presents'** (which is). Mechanism: `P(w | c)` is a
likelihood over the whole vocabulary, so the add-lambda floor for an unseen (word, category) cell is an arbitrary
constant while a seen cell is a real estimate -- the ratio therefore tracks the word's **frequency**, not its category
bias. Conditioning on the WORD instead of on the CATEGORY removes the frequency term; that is `lex_bias`, and it fixes
the inversion (AUC 0.8402 -> 0.8525 on UD-EWT). **This is the one place where "copy the operation exactly" had to be
read at the computational level rather than the formula level.**

**(b) Naive-Bayes cue integration loses to the delta rule, and the reason is measurable.** See 2b -- redundant reads of
one channel. The de-correlated naive-Bayes arm (one posterior read only) was also built and is worse than both
(QA-SRL 0.5687): dropping the redundancy costs more information than the double-count costs precision.

**(c) A "constrained decode" cue is provably redundant -- not built, and that is a result.** The obvious form of the
brief's item 4 is: force token *i* to VERB, re-run the organ's forward pass, and read the likelihood gain. In an HMM
that quantity is **exactly `post_i(VERB)`** (the constrained partition function over the free one), which the cue block
already has. The non-redundant version is the SENTENCE-level "this clause contains at least one predicate"
renormalisation, `post_i(VERB) / (1 - Z_noverb/Z)` -- and that belongs inside the organ's own decode, not in a
downstream detector. It is written up as alternate path A below.

**(d) On UD-EWT test the cue block adds only +0.0177 ns over the swept stand-in, and that is expected, not a miss.**
UD-EWT test is the population the organ's count supply comes from, so its posterior is already well calibrated there
and a bare ranking on it is near-optimal. The combination earns its keep exactly where the posterior is least
calibrated: +0.0688 on GUM, +0.2052 on QA-SRL. This reproduces the parent problem's register finding with the tagger
swapped -- "the extra cues matter exactly where the lexical prior is brittle". The UD-EWT arm is also underpowered
(n_pos = 112 against 511 and 960): a CI half-width of 0.085 cannot resolve a 0.018 effect.

**(e) GUM's apparent gate coverage of 0.489 is a GOLD ARTEFACT, not a capability gap.** GUM/GENTLE contains
fill-in-the-blank exercise texts whose blanks are gold-tagged VERB: **106 of 234** dropped "verbs" in the audited
sample are tokens like `____`, `______`, `___`. They never enter the candidate rows, so no reported recovery number is
affected -- but the coverage figure must not be quoted as a lexicon gap.

**(f) The witness sentence, honestly.** On "the lake presents an unbroken sheet of ice" the BF rescue scores
`presents` **0.1457** against `sheet` **0.0010** and `ice` **0.0004** -- it ranks the real verb 50-100x above its
noun-flanked distractors. At the deployed precision-preserving threshold (0.2592) it does **not** fire; at the
recall-oriented threshold recorded in the same asset (0.0929, fp<=0.25) it does. Mechanism, traced upstream exactly as
the brief's item 4 asks: the category organ gives `P(VERB | presents) = 0.0220` and `P(VERB | lake) = 0.0212` -- it has
**no lexical basis at all** for preferring one over the other, and the clause-competition cue therefore splits almost
evenly (0.3769 vs 0.3641). Only the `-s` morphology and the per-lexeme bias separate them. The quantity that would
force the decision is the sentence-level "this clause has no predicate at all" constraint, and the organ never applies
it. **The loss is upstream of the detector, in the organ's decode, and it is named with numbers.**

**(g) The remit boundary, counted.** The rescue is ADDITIVE by construction, so a gold VERB the organ called **AUX** is
invisible to it: **38.8% (UD-EWT) / 18.8% (GUM) / 4.7% (QA-SRL)** of all dropped verbs. That is UD's main-verb
*be*/*have* convention -- the single confusion already named as the #1 upstream tag-to-head loss (2026-09-13, 58% of
it). It is not this organ's to fix and it bounds what any additive rescue can reach.

---

## 5. Every component touched, and its brain-foundational status

| component | role here | status | note |
|---|---|---|---|
| `hdlab/lexical_categories.py` | the cue source: emission counts + forward-backward posterior + the stem table | **BF_SPIRIT** (unchanged) | read-only; three of its quantities were previously thrown away before reaching this rung |
| `hdlab/morphology.py` | the rescue gate (`morphy(w,'v')`) | **BF** | replaces an nltk-at-inference import; 0.99698 agreement measured |
| `hdlab/predicate_detector.py` | **this organ** -- new cue block + plastic combiner | **NOT_BF -> BF_SPIRIT** | the perceptron-margin path is left in place for the perceptron baseline; nothing is removed |
| `hdlab/situation_reader.py` (`_add_predicate_recall`) | the wire | unchanged in shape | the stand-in branch is replaced; the perceptron branch and the additive contract are untouched |
| `verification/test_predicate_recall_landing_organ.py` | the witness | -- | two stale premises fixed, a live-chain section added |
| `hdlab/attachment_arm.py` | **not touched** (concurrent pri-94 solver) | -- | -- |

---

## 6. What let the signal be maximised -- the chain, rung by rung

The win came from cracking the chain **to the top**, and the rungs divide cleanly into cracked and not:

**Cracked.**
1. **The bar.** `P(VERB) >= 0.3` was a number, not a decision rule. Replaced by an FP-budget calibration. (+0.2386)
2. **The hand-off.** The rescue was reading a dict truncated at 0.01; it now reads the organ's posterior matrix and
   its emission rows directly -- nothing is thrown away between the organs. (5-15% of positives were arriving as zero)
3. **The likelihood channel.** The emission counts were never reaching this rung at all. Conditioning them on the word
   rather than the category is what makes them usable.
4. **The structural prior as a COMPETITION.** A normalised share over a clause, not a threshold on an unnormalised
   belief. Strongest single new cue (AUC 0.9115 on QA-SRL, above the posterior's own 0.8900).
5. **The hand-off INSIDE this rung.** The structural cues were reading the argmax tag -- a point estimate -- so one
   upstream mis-tag zeroed them. Reading the posterior instead is worth +0.0219 (QA-SRL) and +0.0156 (GUM).
6. **The learning rule.** Error-driven cue competition rather than independent accumulation, because the cues are
   redundant by construction.

**Not cracked (named, with numbers, above).**
- The AUX convention (4.7-38.8% of dropped verbs, invisible to an additive rescue) -- upstream, already filed.
- The sentence-level "at least one predicate" constraint -- belongs in the organ's decode, not here (negative (c), (f)).
- The event-level precision trade (0.9370 -> 0.8715) -- real, reported, and the reason the default is the tight budget.

---

## 7. Alternate paths (similarly or MORE brain-foundational than what I shipped)

**A. Put the clause constraint INSIDE the category organ's decode.** *Structure:* the same constraint-satisfaction
network (MacDonald 1994) that already settles the categories, with one more global factor. *Math:* run the organ's
forward pass twice per clause, once unconstrained (`Z`) and once with the VERB state masked (`Z_noverb`); then
`P(c_i = VERB | the clause has a predicate) = post_i(VERB) / (1 - Z_noverb/Z)`. Exact, cheap (one extra forward pass),
and it makes the *cross-sentence* comparison principled, which a global threshold on an unnormalised posterior is not.
*Why more BF:* the brain does not run a second organ to patch the first; it settles one network. *What it would take:*
a masked second-order forward pass (the live asset is `order=2`) plus a whole-board A/B, because it changes the
posterior every consumer reads. *Why not now:* the category organ is under concurrent work (pri 99 / pri 104) and this
brief's remit is the rescue.

**B. Read the argument-structure expectation from the attachment arm instead of positional windows.**
`subj_before`/`obj_after` are crude proxies for the brain's argument-structure anticipation (Altmann & Kamide 1999).
The attachment arm now produces head marginals; "does forcing token *i* to VERB improve the attachment structure?" is
the parse-coherence cue the parent measured as modest (+0.35 on `global_delta`) under a *supervised* parser. It is
worth redoing now that the heads rung is brain-foundational. *Why not now:* `hdlab/attachment_arm.py` is being edited
by a concurrent solver and a strategy merge is pending.

**C. Close the online loop.** The combiner's `observe` path exists and is never called on the live path. The brain's
confirmation signal is downstream: when a rescued predicate later receives filled argument roles, that is evidence it
was a predicate; when it stays orphaned, evidence it was not. `observe(cues, 1|0)` from the roles rung would make this
organ genuinely learn while reading. *What it would take:* a confirmation signal from the role labeler -- which does
not emit one yet.

**D. Retire the AUX exclusion by making the rescue REPLACE as well as ADD.** The 4.7-38.8% of dropped verbs tagged AUX
are out of reach only because the wire is additive. A *revising* rescue (re-decide AUX vs VERB for main-verb
*be*/*have*) would reach them -- but it breaks the no-regression-by-construction property the wire was landed on, so it
needs its own board A/B and its own problem.

---

## 8. Priority next steps

1. **Land the diff** (`predicate_detector_bf_patch.diff`) and move
   `data/hook_state/predicate_detector_bf_counts_v1.json` -> `data/frontend_assets/`. The patch falls back to the
   staging path and then to the old stand-in read, so it is safe to land before the asset move.
2. **The operating point is open, and the board says it is cheap to loosen.** The asset records calibrated
   thresholds for 0.05 / 0.10 / 0.25 / 0.50 false verbs per sentence; the shipped default is 0.10, and at that point
   the board is flat. Since the board is insensitive to the extra events, a free-text event-recall consumer could
   select 0.25 (recovery 0.9286 / 0.8102 / 0.8635, and the witness sentence fires) by passing `threshold=` to
   `rescue_indices`. Re-run the board at 0.25 before making that the default.
3. **File alternate path A** (the clause constraint inside the organ's decode) as its own problem -- it is the fix for
   the witness sentence and it subsumes half of this organ.
4. **Widen `tag_with_posterior`'s truncation** (P >= 0.01) or give consumers the matrix: 5-15% of this rung's positives
   were arriving as exact zeros, and every other consumer of the graded category signal inherits the same cut.

---

## 9. Submission prompt

```
pri 107 -- the_predicate_rescue_is_dormant_under_the_bf_category_organ_its_lexical_likelihood_cue_still_expects_the_perceptrons_margin

SOLVED. The rescue fires on the live chain. Under the brain-foundational category organ the landed rescue was dormant
(0 extra events on the landing witness; 0.2385 recovery on QA-SRL). Re-derived its noisy-channel lexical likelihood
from the organ that replaced the perceptron -- the per-lexeme noun/verb bias off the EMISSION COUNTS, the lemma
organ's stem route, and one-predicate-per-clause as a normalised COMPETITION over the posterior -- with the six
structural cues read off the posterior instead of the argmax tag, combined by RESCORLA-WAGNER error-driven cue
competition (plastic; observe() is the online path). Recovery at 0.10 false verbs/sentence (a fifth of the
perceptron-era budget): 0.7054 UD-EWT test / 0.5616 GUM / 0.6823 QA-SRL, CI-separated over the dormant live read on
all three (+0.43 / +0.34 / +0.44), over the info-free twin on all three, and over the STRONGEST floor (the same cue
with its threshold swept) on both well-powered populations (+0.0688 GUM, +0.2052 QA-SRL; UD-EWT +0.018 ns,
n_pos=112). End-to-end through the live reader on modern gold: event recall 0.9186 OFF -> 0.9305 stand-in -> 0.9501,
+0.0315 CI[+0.0249,+0.0384] vs OFF, CI-separated, at 0.176 false events/sentence. Honest headline: ~half the recovered
signal was the mis-set bar (0.3), not a missing cue. Gate no longer imports nltk at inference (0.99698 agreement with
the WordNet gate). Located negatives with numbers: 4.7-38.8% of dropped verbs are tagged AUX and invisible to an
ADDITIVE rescue (UD's main-verb be/have convention, already the #1 upstream confusion); the witness sentence
'presents' is ranked 50-100x above its distractors but fires only at the recall-oriented threshold, because the organ
gives it no more lexical support than 'lake' (0.0220 vs 0.0212) -- the fix is a clause-level one-predicate constraint
INSIDE the organ's decode, written up as alternate path A. Board A/B (diff monkeypatched in): aggregate 0.6109 ->
0.6109, 5/7 dims CI-sep over floor in both arms, no dimension moves by more than one item. Landing witness under the
patch: 30/30 (it FAILS on disk today).

Files: experiments/exp_predicate_rescue_bf_cue_v1.py, data/hook_state/predicate_detector_bf_counts_v1.json,
notes/problems/<slug>/{SOLVED.md, predicate_detector_bf_patch.diff}. No hdlab/ file changed on disk.
Reverify: .venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --self-test ; --full ; --reader
```
