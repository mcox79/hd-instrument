# exp_typed_role_selectional_asset_writerule_v1 -- FULL landed, WORD_SELECTION_NOT_TYPE

Cell: `experiments/exp_typed_role_selectional_asset_writerule_v1.py`
Pre-reg: `preregs/2026-08-18_typed_role_selectional_asset_writerule_v1.md`
Metrics: `data/exp_typed_role_selectional_asset_writerule_v1/metrics.json`
Verdict: `TYPED_ROLE_SELECTIONAL_ASSET__WORD_SELECTION_NOT_TYPE`

## Pair cell (disclose as a pair, not a solo result)
This cell is one of TWO independent tests of "does the grammatical job a word does carry
substitutability", dispatched in parallel and coordinated peer-to-peer before authoring:
- **This cell**: typed-role features from `data/selectional_preferences_v1/`, a pre-built,
  64MB/737,488-sentence SimpleWiki slot asset (extracted 2026-08-16 by this project's own parser).
  DIFFERENT corpus from A0's.
- **`experiments/exp_typed_role_context_write_rule_dissociation_v1.py`** (teammate
  "typed-role-writerule"): live-parses the SAME 34,169-sentence corpus A0 is built from, via
  `hdlab.arc_parser`/`arc_labeler`/`pos_tagger`. No corpus confound, but not yet landed as of this
  note.
Cross-reference both before treating either as final.

## Regression gate: PASS (8/8, delta=0.0000 on every check)
F_ORTHOGRAPHIC=0.5000, F_FREQUENCY=0.4901, F_SCRAMBLE=0.4664, F_CONSTANT_PROTOTYPE=0.5431 (bar),
K1=0.9599, N0=0.4862, A0=0.0710, RAW_COUNT_FULL_ACCUM=0.0510 -- all reproduced exactly against
`data/exp_dissociation_score_instrument_v1/metrics.json`.

## Population / coverage
242 matched (SET P, SET S) noun pairs, unchanged. 617 distinct words needed; 555/617 (90.0%)
covered by the SimpleWiki selectional-slot asset. Pair coverage BEFORE restriction: SET P
218/242, SET S 185/242 (the coverage-imbalance risk the dispatch brief flagged by name).

## Arm table (FULL, N_BOOT=10000, bar=0.5431)
| arm | AUC | 95% CI | band | margin vs bar | margin vs 0.5 |
|---|---|---|---|---|---|
| A0_INCUMBENT (cited, different corpus) | 0.0710 | [0.0504,0.0930] | BELOW_0.5_COOCCURRENCE | -0.4721 | -0.4290 |
| T1_TYPED_ROLE | 0.5802 | [0.5296,0.6304] | ABOVE_0.5 | +0.0371 | +0.0802 |
| T2_UNTYPED_SAME_COVERAGE | 0.5900 | [0.5393,0.6400] | ABOVE_0.5 | +0.0469 | +0.0900 |
| T3_COMBINED | 0.2264 | [0.1862,0.2682] | BELOW_0.5_COOCCURRENCE | -0.3167 | -0.2736 |
| N1_LABEL_PERMUTED | 0.5516 | [0.5004,0.6025] | ABOVE_0.5 (barely) | +0.0085 | +0.0516 |
| N3_MAGNITUDE_PERMUTED | 0.5630 | [0.5108,0.6153] | ABOVE_0.5 | +0.0199 | +0.0630 |
| N5_COVERAGE_MATCHED (n_P=218,n_S=185) | 0.5217 | [0.4640,0.5789] | NOT_SEPARATED_FROM_CHANCE | -0.0214 | +0.0217 |

## What T2 and T3 did
**T2_UNTYPED_SAME_COVERAGE** (role label stripped, identical contributing words) reads AUC=0.5900,
CI overlapping T1's 0.5802 entirely -- T1 does NOT dominate T2. The ROLE LABEL adds nothing over
mere word-selection (which verbs a noun co-occurs with as ANY argument).

**T3_COMBINED** (Komninos & Manandhar concat-and-renormalize recipe) collapsed to AUC=0.2264,
firmly in the CO-OCCURRENCE direction -- markedly WORSE than either channel alone. T1 (mildly
substitutability, +0.08 over chance) and A0 (strongly co-occurrence, -0.43 under chance) point in
OPPOSITE directions; simple unit-norm concatenation does not average them, it appears dominated by
A0's larger, more extreme cosine spread. Komninos & Manandhar's "combined beats either alone"
result assumed aligned/compatible channels; it does not transfer to anti-correlated channels.
Disclosed as a real (if unintuitive) finding, not a suspected bug -- construction was re-checked.

## Controls
**N1_LABEL_PERMUTED** (word<->slot-type association destroyed, row mass exactly preserved):
AUC=0.5516, CI lower bound 0.5004 -- barely separated from chance, and T1 does NOT dominate N1
(CI overlap). **N3_MAGNITUDE_PERMUTED** (count values shuffled across the same support): 0.5630,
also overlapping T1. Both must-fail controls retain comparable signal to T1 itself -- most
plausibly generic degree/frequency structure surviving into the PPMI-SVD embedding regardless of
which specific slot a word fills, not typed content.
**N5_COVERAGE_MATCHED**: restricting to both-covered pairs (218 P, 185 S, from 242/242) drops T1's
own AUC from 0.5802 to 0.5217 -- NOT_SEPARATED_FROM_CHANCE. The uncovered-pair asymmetry (90% vs
76% coverage) was inflating the full-population number.

## Margins vs the bar (0.5431) and vs chance (0.5), stated separately
T1: +0.0371 above the bar's OWN VALUE numerically, but its 95% CI (0.5296-0.6304) does NOT
CI-separate above 0.5431 -- the bar is inside T1's CI. Margin vs chance 0.5: +0.0802, CI-separated
(lower bound 0.5296 > 0.5). T1 clears chance but not the bar, and even the chance-margin does not
survive T2 or N5.

## Which STOP-IF fired
STOP-IF (ii): T1 dominates A0 (CI 0.5296 > A0's CI upper bound 0.0930) but does NOT dominate T2
-> `WORD_SELECTION_NOT_TYPE`. Two additional, non-forcing negatives corroborate the same read:
T1 does not dominate N1 either, and N5 (coverage-matched) drops T1 to NOT_SEPARATED_FROM_CHANCE.
All three independent checks (T2, N1, N5) point the same way: whatever separates A0 from T1 is not
attributable to the TYPED slot label, and is fragile to the coverage imbalance the asset's
different, larger corpus introduces.

## One-sentence answer
On this pre-built, cross-corpus asset, the grammatical job a word does (its typed argument-slot
label) does NOT carry substitutability beyond what mere word-selection and coverage imbalance
already explain -- a clean, well-controlled negative, pending comparison against the same-corpus
sibling cell (`exp_typed_role_context_write_rule_dissociation_v1`) before treating this axis as
closed.
