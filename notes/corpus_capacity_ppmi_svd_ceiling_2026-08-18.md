# Does this corpus support substitutability at all? PPMI + truncated SVD says: partially, and only under supervision.

Answers `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.15's open question, pre-committed
decision branches in sec 6.16. Cell: `experiments/exp_corpus_capacity_ppmi_svd_ceiling_v1.py`.
Landed metrics: `data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json` (`code_version=v1.0`,
`run_mode=full`, `elapsed_s=48.6`). Supplementary robustness check:
`tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`.

**Prior-work check** (`bash tools/substrate_query.sh`, concept keywords "PPMI truncated SVD
classical distributional semantics substitutability co-occurrence capacity ceiling first-order
counts"): confidence=0.3057, marginally above the cosine>0.30 threshold. Top 2 hits are both bare
WordNet/concept-atom nodes for "substitutability" with no method content -- neither builds a
PPMI+SVD instrument or a fitted-oracle capacity diagnostic. NOT a rediscovery.

## The regression gate (STOP-IF i) -- all 8 checks PASS bit-for-bit

Loaded `experiments/exp_dissociation_score_instrument_v1`'s OWN checkpoint (`POPULATION|v1.7|full`
and `SCORES|v1.7|full` in `data/exp_dissociation_score_instrument_v1/units.jsonl`) and recomputed
every AUC via DSI's own `auc_bootstrap`, same seeds:

| arm | expected | measured | delta |
|---|---|---|---|
| F_ORTHOGRAPHIC | 0.5000 | 0.5000 | 0.0 |
| F_FREQUENCY | 0.4901 | 0.4901 | 0.0 |
| F_SCRAMBLE | 0.4664 | 0.4664 | 0.0 |
| F_CONSTANT_PROTOTYPE | 0.5431 | 0.5431 | 0.0 |
| KNOWN_ANSWER (K1) | 0.9599 | 0.9599 | 0.0 |
| RANDOM_VECTOR_STORE (N0) | 0.4862 | 0.4862 | 0.0 |
| INCUMBENT_LIVE_STORE (A0) | 0.0710 | 0.0710 | 0.0 |
| RAW_COUNT_FULL_ACCUM | 0.0510 | 0.0510 | 0.0 |

`INSTRUMENT_LICENSED = True`. None of stop-if (i)/(iv) fired -- the instrument is licensed for
this cell, using the SAME 242-pairs-per-cell matched population, never rebuilt.

## The matrix factorised

Full valid anchor set as rows (n=5491, `mat_ok` from `CTS.load_cache()`, the same population every
sibling cell's `INCUMBENT_LIVE_STORE` uses), union of context words seen near ANY anchor as columns
(`INFO.build_vocab` over every anchor's Pstore checkpoint, `data/exp_cue_information_audit_v1`,
never re-tokenised):

- **shape 5491 x 21576**, **nnz = 1,074,605**, **density = 0.907%**, **total token count =
  1,824,296**.
- Built the FULL row space (not restricted to the 242 pairs' member words) deliberately, so PPMI's
  column marginals are estimated from the corpus's actual context-word frequency distribution
  rather than biased by omitting ~4,900 anchors not in the matched pairs -- the standard
  term-context construction (Levy & Goldberg 2014).
- **Coverage: 242/242 SET_P pairs and 242/242 SET_S pairs have BOTH members present with a
  non-trivial row.** Zero missing anchors.
- No pretrained embedding table imported anywhere; PPMI/SVD/cosine are classical linear algebra
  over this cell's own corpus counts.

## B2_PPMI_SVD -- THE DECISIVE ARM, per k, CI half-widths

| k | AUC | 95% CI | half-width | band |
|---|---|---|---|---|
| 50 | **0.0519** | [0.0349, 0.0714] | 0.0182 | BELOW_0.5_COOCCURRENCE |
| 100 | **0.0285** | [0.0167, 0.0428] | 0.0131 | BELOW_0.5_COOCCURRENCE |
| 300 | **0.0230** | [0.0112, 0.0368] | 0.0128 | BELOW_0.5_COOCCURRENCE |
| 500 | **0.0278** | [0.0132, 0.0451] | 0.0159 | BELOW_0.5_COOCCURRENCE |

No k dropped (max reachable rank = 5490, well above the swept range). **Every k reads CI-separated
BELOW 0.5** -- not merely not-separated from chance, but separated on the co-occurrence side, same
direction as the incumbent (0.0710) and full raw accumulation (0.0510). Best k=50 at 0.0519.
**Stop-if (ii)/Branch A does NOT fire: PPMI+SVD, applied unsupervised, does not beat the substrate
-- it lands in the same co-occurrence-encoding regime the incumbent occupies.**

## B1_PPMI and B3_SECOND_ORDER_COSINE

- `B1_PPMI` (PPMI, no factorisation): AUC **0.0249** [0.0108, 0.0418], BELOW_0.5.
- `B3_SECOND_ORDER_COSINE` (raw context-count cosine, no PPMI weighting, no SVD): AUC **0.0510**
  [0.0335, 0.0708], BELOW_0.5. **Verified bit-identical to DSI's own `RAW_COUNT_FULL_ACCUM` arm**
  (max abs diff across all 484 pair-scores = 8.94e-08) -- an internal consistency self-check that
  this cell's matrix construction agrees with DSI's, not just a close number.

## C1_FITTED_ORACLE -- the capacity ceiling, allowed to cheat

Diagonal reweighting (L2-regularised logistic regression) of the k=100 PPMI-SVD feature space,
fitted directly on the 484 pair labels (P=1, S=0):

- **FITTED IN-SAMPLE (the ceiling number -- NEVER a capability claim): AUC 0.9670** [0.9514,
  0.9805].
- **Held-out, 5-fold pair-level StratifiedKFold (as landed): AUC 0.9606** [0.9430, 0.9754].

**Both clear 0.5 by a wide margin. Stop-if (iii)/Branch B fires: `B2` and `B3` both fail to clear
0.5, but `C1_FITTED_ORACLE` clears it. The information IS present in first-order counts from this
corpus -- but no unsupervised transform tested here (raw PPMI, PPMI+SVD cosine at any of 4 ranks,
raw second-order cosine) reaches it.**

### The fitted-vs-held-out gap needed a second look, and it was smaller than it should be

The landed pair-level CV shows almost no gap (0.967 vs 0.961), which is itself a flag: 617 distinct
words appear across the 484 matched pairs, and **232 of them (37.6%) appear in MORE THAN ONE pair**
(max reuse count 7). A pair-level fold can put the SAME word in both train and test (paired with a
different partner), letting the fit exploit per-word identity rather than a genuinely-unseen-pair
signal.

`tools/verify_ppmi_svd_oracle_group_disjoint_cv.py` re-derives the identical k=100 feature space
and re-scores under a **group-disjoint** split: union-find over the 617 words (grouped by shared
pair membership) yields **148 connected components** (largest holds 7.1% of words), and
`GroupKFold` splits by component so no word crosses the train/test boundary.

| CV scheme | AUC |
|---|---|
| pair-level (word-sharing allowed, matches the landed cell) | 0.9587 |
| **group-disjoint (word-level, no leakage)** | **0.8629** |

**The gap is real** (0.96 -> 0.86 once leakage is controlled) -- the pair-level held-out figure in
the landed metrics.json is optimistic and should not be quoted as the honest generalisation
estimate; 0.8629 is closer to that. **But the qualitative finding is unchanged: even under the
stricter, leakage-controlled test, the fitted oracle clears 0.5 by a wide margin.** The information
is genuinely recoverable from first-order counts by a supervised linear reweighting of the SVD
space, on pairs of words never jointly seen during fitting.

## Which stop-if fired

**Stop-if (iii): `B2` and `B3` both fail to clear 0.5; `C1_FITTED_ORACLE` clears it, fitted AND
(both pair-level and group-disjoint) held-out.** Landed verdict:
`CORPUS_CAPACITY_CEILING__STOP_IF_iii_INFO_PRESENT_NO_UNSUPERVISED_FIRST_ORDER_TRANSFORM_REACHES_IT`.

Per the pre-committed Branch B response (sec 6.16): the build target is **whatever supervision-free
proxy approximates the fitted reweighting** -- not wiring the oracle in (it consulted the labels),
not another unsupervised transform sweep (four were tried: PPMI alone, and PPMI+SVD at k in
{50,100,300,500}, all failed), but a write rule that captures WHAT the diagonal reweighting is
doing to the SVD dimensions -- almost certainly down-weighting the dimensions PPMI+SVD spends on
raw corpus-frequency variation and up-weighting whichever dimensions correlate with paradigmatic
class, which a purely unsupervised factorisation has no signal to prefer.

## The one plain-language sentence

**Yes, partially: a supervised linear reweighting of classical PPMI+SVD features CAN separate
"words that could replace each other" from "words that co-occur constantly but cannot replace each
other" on this corpus, clearing chance by a wide margin even on word-pairs never seen together
during fitting -- but no UNSUPERVISED classical method (raw PPMI, PPMI+SVD cosine at any rank we
tried, or plain co-occurrence-profile cosine) finds that structure on its own, which means the
corpus is not the blocker, but nothing we currently write into the store -- ours or the classical
unsupervised alternative -- discovers the signal without being told the answer first.**

## Honest limits

- The matched population is noun-only (inherited from the licensed instrument, disclosed there).
- `C1_FITTED_ORACLE`'s fitted-in-sample number is a CEILING DIAGNOSTIC and must never be quoted as
  a capability; the group-disjoint held-out figure (0.8629) is the number to cite if a single
  "how much signal is really there" figure is needed.
- `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py` is a supplementary, manually-run robustness
  check -- it is not part of `exp_corpus_capacity_ppmi_svd_ceiling_v1`'s own regression gate or
  landed metrics.json, and was not dispatched via queue_add.
- B2's k sweep stopped at 500 per the pre-registered brief; nothing in the monotonic downward trend
  (0.0519 -> 0.0285 -> 0.0230 -> 0.0278, non-monotone at the top end but never approaching 0.5)
  suggests a larger k would cross 0.5 unsupervised.
