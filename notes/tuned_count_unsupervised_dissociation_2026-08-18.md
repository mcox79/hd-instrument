# DOES A PROPERLY TUNED, FULLY UNSUPERVISED COUNT METHOD REACH SUBSTITUTABILITY? -- NO. 6.18 SURVIVES A FAIRER TEST.

**Cell:** `experiments/exp_tuned_count_unsupervised_dissociation_v1.py`, ANCHOR_NAME
`tuned_count_unsupervised_dissociation_v1`, CODE_VERSION v1.0. FULL run landed cleanly, 456s wall,
`data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json`. Smoke (`--grid reduced`, 46s) ran
first and exercised the full pipeline end to end before the full dispatch. This cell exists
specifically to try to falsify plan sec 6.18's own headline ("the classical method fails on our
corpus") -- it does not falsify it, but it does correct the headline's precision.

## THE OBJECTION UNDER TEST

Plan sec 6.18 ran only VANILLA PPMI+SVD (no context-distribution smoothing, no shift, no
subsampling) and found every k BELOW 0.5. Levy & Goldberg (2014) proved SGNS implicitly factorises a
shifted-PMI matrix; Levy, Goldberg & Dagan (2015) showed a TUNED count method matches SGNS on
similarity tasks. If a held-out-selected tuned arm here cleared 0.5, 6.18's supervision conclusion
would be wrong -- the missing thing would have been hyperparameters, not a learning signal.

**It does not clear 0.5. Not even the most generous, non-held-out, sweep-maximum ceiling clears it.**
6.18's conclusion survives, but the honest statement changes from "the classical method fails" to
"the classical method fails, and tuning it the way the literature prescribes roughly doubles its AUC
without getting remotely close to the substitutability boundary."

## REGRESSION GATE -- 8/8 PASS, PLUS A GENUINE BIT-LEVEL T0 REPRODUCTION

CAP's own `regression_gate()` (imported verbatim from `exp_corpus_capacity_ppmi_svd_ceiling_v1`) was
reused, not copied, and passed all 8 checks at delta 0.0000 against the DSI v1.7 cache: four floors
(0.5000/0.4901/0.4664/0.5431), K1=0.9599, N0=0.4862, A0_INCUMBENT=0.0710, RAW_COUNT_FULL_ACCUM=0.0510.

Beyond that, T0 (vanilla PPMI+SVD) was independently RECOMPUTED here -- not loaded from CAP's cache
-- using CAP's own `ppmi_of` and CAP's own exact seed convention, and matched CAP's landed numbers
to delta 0.0000 at every k:

| k | expected (6.18) | measured here | delta |
|---|---|---|---|
| 50 | 0.0519 | 0.0519 | 0.0000 |
| 100 | 0.0285 | 0.0285 | 0.0000 |
| 300 | 0.0230 | 0.0230 | 0.0000 |
| 500 | 0.0278 | 0.0278 | 0.0000 |

Matrix: 5,491 x 21,576, nnz 1,074,605, density 0.91%, 1,824,296 tokens -- identical to 6.18's. Pair
coverage: 242/242 both members present in both cells, SET P and SET S. Population from
`data/exp_dissociation_score_instrument_v1/units.jsonl` (`POPULATION|v1.7|full`), scores from
`SCORES|v1.7|full`, never rebuilt.

## HOW HYPERPARAMETERS WERE SELECTED WITHOUT TOUCHING THE 242 EVALUATION PAIRS

A HELD-OUT VALIDATION PAIR POPULATION was built by reusing DSI's own population-construction
pipeline (`build_wordnet_synonym_candidates`, `build_cooccurrence_paircounts`,
`build_syntagmatic_candidates`, `match_cells`), verbatim, but restricted to an anchor pool of 4,874
words that EXCLUDES every one of the 617 distinct words appearing anywhere in the 242-pair
evaluation population -- WORD-level disjointness, strictly stronger than pair-level (this guards
against the exact word-identity leakage the group-disjoint oracle recompute found in 6.18: 37.6% of
the 617 eval words recur across eval pairs). This produced 54 matched validation pairs per cell
(`n_pool_anchors_word_disjoint_from_eval=4874`, `n_matched=54`). At smoke scale the restricted pool
was too small (n=4 matched pairs, below the 20-pair usability floor) and the cell correctly fell back
to sweep-ceiling-only reporting for that run, per its own pre-registered escape hatch -- disclosed,
not silently worked around; the full run did not need the fallback.

Every hyperparameter (context-smoothing alpha, PMI shift k_shift, subsampling t, eigenvalue
weighting p, SVD rank k) was selected by maximising AUC on these 54 held-out pairs ONLY. The winning
configuration's AUC on the real 242 evaluation pairs was then read ONCE per arm and is reported as
THE RESULT. The best AUC over the same grid scored directly on the evaluation pairs is reported
alongside, always labelled `CEILING_NOT_A_RESULT_DO_NOT_QUOTE_AS_CAPABILITY` -- both numbers come
from the same already-computed SVD vectors, so reporting both costs nothing extra.

## ARM-BY-ARM RESULT (RESULT = held-out-selected, THE number; CEILING = best-over-sweep-on-eval,
labelled, never a capability claim)

| arm | selected config | held-out AUC | **RESULT (eval)** | CEILING (eval) |
|---|---|---|---|---|
| T0_VANILLA_PPMI_SVD | k=50 (best of 50/100/300/500) | n/a | 0.0519 [0.0349,0.0714] | (same, no tuning) |
| T1_CONTEXT_DISTRIBUTION_SMOOTHING | alpha=1.0 (i.e. OFF), k=50 | 0.0432 [0.0151,0.0816] | **0.0519 [0.0344,0.0724]** | 0.0519 [0.0344,0.0724] |
| T2_SHIFTED_PPMI | k_shift=15, k=50 | 0.0775 [0.0312,0.1361] | **0.1144 [0.0863,0.1440]** | 0.1144 [0.0863,0.1440] |
| T3_SUBSAMPLING | t=None (i.e. OFF), k=50 | 0.0432 [0.0147,0.0802] | **0.0519 [0.0345,0.0714]** | 0.0519 [0.0345,0.0714] |
| T4_BEST_COMBINED | alpha=1.0, k_shift=15, t=None, k=50, p=0.5 | 0.0775 [0.0309,0.1375] | **0.1144 [0.0864,0.1449]** | **0.1253 [0.0956,0.1572]** (p=1.0) |
| T5_SGNS_FROM_SCRATCH (IN_IN) | vector_size=100, sg=1, window=5, epochs=5, no import | n/a | **0.4417 [0.3904,0.4927]** | n/a (single config, not swept) |
| K1_KNOWN_ANSWER | reused, DSI cache | n/a | 0.9599 [0.9441,0.9739] | -- |
| N0_RANDOM_VECTOR_STORE | reused, DSI cache | n/a | 0.4862 [0.4353,0.5377] | -- |

**Every RESULT and every CEILING, for every arm, stays CI-separated BELOW 0.5.** The best number
anywhere in this whole sweep -- T4's ceiling, which is not held-out-selected and is explicitly
labelled as not a result -- is 0.1253, with a CI upper bound of 0.1572. That is nowhere near the
0.5 substitutability boundary.

**Held-out selection correctly found that context-distribution smoothing and subsampling did NOT
help on this corpus** -- both T1 and T3 selected the "off" setting (alpha=1.0, t=None) because every
alpha in {0.5, 0.75} and every t in {1e-3, 1e-5} scored WORSE on the 54 held-out pairs than doing
nothing. **Only the shift term helped**, and it helped a lot in relative terms: k_shift=15 roughly
DOUBLES T2/T4's AUC over vanilla (0.0519 -> 0.1144), and this is CI-separated above T0's own best
point estimate (T2's CI lower bound 0.0863 > T0's 0.0519 point estimate) -- a real, held-out-licensed
improvement, just nowhere near enough. T4's own p-sweep (0, 0.5, 1) selected p=0.5 (matching what
T0/CAP already use) via held-out; p=1.0 scored marginally higher directly on eval (the ceiling row),
illustrating exactly the kind of small extra lift that tuning-on-eval would silently harvest if this
cell had not separated selection from reporting.

## T5: SGNS FROM SCRATCH ALSO FAILS, AND ITS OWN CONTROLS ARE CLEAN

Trained gensim Word2Vec (sg=1, negative=5, sample=1e-5, window=5, epochs=5, vector_size=100, random
init, seed-pinned) on 33,839 non-empty tokenised sentences from the SAME corpus (`INFO.
load_corpus_and_buckets()`, cached, not restricted to each anchor's profile-only split --
disclosed simplification, still 100% within-corpus text, nothing imported). Trained in 3.0s,
vocab=22,265. `NO_PRETRAINED_EMBEDDING_TABLE_IMPORTED=true` asserted.

- **T5_IN_IN (cue-vector cosine, the primary/required number): 0.4417 [0.3904, 0.4927]** --
  CI-separated BELOW 0.5, not merely at chance.
- **N1_UNTRAINED_RANDOM_INIT_CONTROL: exactly 0.5000 [0.5000, 0.5000]** -- the untrained control
  behaves exactly as it should (a random unit-norm vector's cosine has zero expected signal, and
  with a matched-pair symmetric construction the AUC point estimate lands exactly on 0.5), so
  T5's 0.4417 is not an interface artifact riding on the pooling geometry -- it is BELOW its own
  untrained control, i.e. training made the arm WORSE at this AUC by this measure, not better.
- **T5_IN_OUT_bonus_diagnostic (cue-vs-outcome geometry, free extra, not required by this brief):
  0.5076 [0.4569, 0.5595]**, NOT_SEPARATED_FROM_CHANCE. Neither geometry clears 0.5.

This corroborates the corpus-size hypothesis from the 2026-08-18 supervision drill: Huebner &
Willits (2018) needed 5,244,672 tokens of child-directed speech for taxonomic/semantic structure to
emerge from next-word prediction; this corpus has 1,824,296 tokens, about a third. A from-scratch
predictive objective on this corpus does not reach substitutability either.

## WINNER COMPOSITION (operational definition invented for this cell -- verified: grep for the
exact phrase across notes/experiments/tools returns zero hits anywhere in this codebase before this
cell; there is no prior definition to reuse)

For each covariate-matched comparison i, winner = whichever of (matchedP[i], matchedS[i]) the arm
scored higher; co_occurs(w1,w2) = nonzero raw corpus count in either direction (the same Pstore
counts M is built from).

| arm | no_relation_rate (all pairs) | gold SET-P co-occ share | SET-S co-occ share | winner co-occ share | ratio (winner/SET-S) |
|---|---|---|---|---|---|
| T0 (and T1, T3, same selected config) | 0.5021 | 0.0000 | 0.9959 | 0.9587 | 0.9627 |
| T2 (and T4, same selected config) | 0.5021 | 0.0000 | 0.9959 | 0.8926 | 0.8963 |
| A0_INCUMBENT | 0.5021 | 0.0000 | 0.9959 | 0.9463 | 0.9502 |
| K1_KNOWN_ANSWER | 0.5021 | 0.0000 | 0.9959 | 0.0458 | 0.0460 |
| N0_RANDOM_VECTOR_STORE | 0.5021 | 0.0000 | 0.9959 | 0.5455 | 0.5477 |

`no_relation_rate_overall` (~0.50) and the SET-P/SET-S co-occurrence shares (0.00 / 0.996) are
population properties, not arm properties -- they re-confirm DSI's own construction guarantee (SET P
= WordNet synonyms with EXACTLY ZERO corpus co-occurrence; SET S = top co-occurring pairs) rather
than measuring anything new; reported once per arm mainly so the arm-dependent number sits next to
its reference frame. The informative number is `winner_cooccurrence_share` / its ratio to SET-S's
own share: **1.0 would mean the arm behaves exactly like a naive "always prefer the collocate" rule
(the incumbent's documented failure mode); 0.0 would mean it never does.** T0/T1/T3 sit at 0.96 --
almost indistinguishable from "always pick the collocate". The shift-tuned arms (T2/T4) move to
0.89 -- a real, measurable reduction in collocate-preference, consistent with their higher AUC, but
still nowhere near K1's 0.046 (a genuine substitutability-aware oracle almost never prefers the
collocate) or even N0's 0.548 (a random, uninformative arm sits near the 50/50 base rate one would
expect from a construction that is exactly half zero-co-occurrence pairs and half top-co-occurring
pairs). Ratio is reported as winner-share over SET-S's own share rather than over SET-P's (gold's
own share is 0.0 by construction, so dividing by it is degenerate -- disclosed in the module
docstring rather than silently avoided).

## FLOORS, TIE CONVENTION, CI WIDTHS

Four floors recomputed on this exact population (via CAP's regression gate, itself reusing DSI's own
recompute): F_ORTHOGRAPHIC 0.5000 [0.4875,0.5124], F_FREQUENCY 0.4901 [0.4376,0.5413], F_SCRAMBLE
0.4664 [0.4148,0.5178], F_CONSTANT_PROTOTYPE 0.5431 [0.4922,0.5953] -- all NOT_SEPARATED_FROM_CHANCE,
as required for the instrument to be licensed. CI half-widths for the tuned arms' RESULT numbers run
0.019-0.029 at n=242; at n=54 (held-out) they run 0.033-0.053 -- a real width, not negligible, but
still far short of closing a 0.35-0.40-point gap to 0.5. This instrument's scorer (`DSI.auc_of`,
Mann-Whitney-U-style, ties credited 0.5 each) has one well-defined tie handling built into the
formula; there is no second tie convention applicable the way there is for a hit@1 metric elsewhere
in this project -- stated explicitly in the cell's own metrics rather than silently omitted.

## WHICH STOP-IF FIRED

**STOP_IF (iii): tuned arms (T2, T4) improve on vanilla T0, CI-separated, but stay below 0.5.**
STOP-IF (ii) (a held-out-selected arm CI-separated above 0.5) did NOT fire -- checked first, per the
pre-registration, and false for every arm including the non-held-out ceiling numbers. STOP-IF (iv)
(no tuned arm beats vanilla at all) also did not fire, since T2/T4 genuinely improved.

## PLAIN-LANGUAGE ANSWER

**A tuned unsupervised count method does not reach substitutability on this corpus.** Doing the
tuning the published literature prescribes -- specifically the PMI shift term, the piece of the
recipe that makes count-based PMI mathematically equivalent to what a neural skip-gram model learns
-- roughly doubles the classical method's AUC (0.05 to 0.11), a real and held-out-licensed gain, but
the substitutability boundary is at 0.5 and even the single most generous number produced anywhere
in this entire sweep (a ceiling number, not a held-out result) is 0.125. Training a from-scratch
neural skip-gram model on the same corpus does no better (0.44, actually below its own untrained
control). **Plan sec 6.18's supervision conclusion survives this fairer test: what this corpus is
missing is not better hyperparameters on the counts it already has -- it is a learning signal, or
more corpus, or both** (the closest published demonstration of predictive structure emerging from
raw text needed roughly three times as many tokens as this corpus has).

## FILES

- `experiments/exp_tuned_count_unsupervised_dissociation_v1.py` -- the cell (self-test, smoke, full
  all landed).
- `data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json` -- full run, INSTRUMENT_LICENSED,
  456s.
- `data/exp_tuned_count_unsupervised_dissociation_v1_reduced/metrics.json` -- smoke run, 46s,
  exercised the fallback-when-held-out-is-too-small path.
