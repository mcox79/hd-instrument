# exp_writerule_maxpool_occurrence_v1 -- findings, 2026-08-18

Cell: `experiments/exp_writerule_maxpool_occurrence_v1.py`, commit (this session, not yet pushed).
Metrics: `data/exp_writerule_maxpool_occurrence_v1/metrics.json` (FULL, 59.1s total: REGIME A 31.2s,
REGIME B 18.8s). Smoke: `data/exp_writerule_maxpool_occurrence_v1_reduced/metrics.json` (24s).
Pre-reg: `preregs/2026-08-18_writerule_maxpool_occurrence_v1.md`.

## Regression gates -- both EXACT

REGIME A: A0_SUM AUC = **0.0510** (expected 0.0510, exact). S1_SINGLE_OCC AUC = **0.4173** (expected
0.4173, exact). K1 known-answer AUC = **0.9599** (matches DISS's own landed number exactly). All four
floors reproduce DISS's own landed values to 4 decimals (F_ORTHOGRAPHIC 0.5000, F_FREQUENCY 0.4901,
F_SCRAMBLE 0.4664, F_CONSTANT_PROTOTYPE 0.5431) -- the checkpoint-reused population is byte-identical.

REGIME B: WR.best_single_occurrence_oracle called verbatim on this cell's own idx_decisive (n=300,
NOT guaranteed index-identical to WR's own draw): SUM_ALL=0.0200 (expected 0.0100, within the declared
0.03 tolerance), RANDOM_SINGLE=0.0267 (expected 0.0367, within tolerance). BEST_SINGLE_ORACLE=0.2600
vs expected 0.3033 (delta 0.0433, OUTSIDE the 0.03 tolerance but never hard-gated -- disclosed, most
likely sampling noise from a different 300-item subsample at this base rate). Self-consistency check:
this cell's own vectorised A0_SUM/S1_SINGLE_OCC hit arrays are **0 mismatches** against WR's own
boolean output on the identical idx_decisive -- the construction is proven, not merely claimed,
identical.

## THE RESULT (REGIME A, primary): M1_MAXPOOL is CI-separated WORSE than BOTH A0_SUM and N1

| arm | AUC | CI95 | half-width | band |
|---|---|---|---|---|
| A0_SUM | 0.0510 | [0.0329,0.0714] | 0.0193 | BELOW_0.5_COOCCURRENCE |
| S1_SINGLE_OCC | 0.4173 | [0.3842,0.4501] | 0.0330 | BELOW_0.5_COOCCURRENCE |
| **M1_MAXPOOL** | **0.0299** | [0.0148,0.0481] | 0.0166 | BELOW_0.5_COOCCURRENCE |
| M2_TOPK_MEAN_K2 | 0.0264 | [0.0125,0.0426] | 0.0151 | BELOW_0.5_COOCCURRENCE |
| M2_TOPK_MEAN_K3 | 0.0240 | [0.0111,0.0384] | 0.0137 | BELOW_0.5_COOCCURRENCE |
| M2_TOPK_MEAN_K5 | 0.0217 | [0.0100,0.0357] | 0.0129 | BELOW_0.5_COOCCURRENCE |
| N1_MAXPOOL_RANDOM_OCC | 0.4545 | [0.4043,0.5061] | 0.0509 | NOT_SEPARATED_FROM_CHANCE |
| N2_MAXPOOL_SIZE_MATCHED_SHUFFLE | 0.5296 | [0.4790,0.5812] | 0.0511 | NOT_SEPARATED_FROM_CHANCE |
| KNOWN_ANSWER_WORDNET_PATH_SIM | 0.9599 | [0.9439,0.9741] | 0.0151 | ABOVE_0.5 (control) |
| RANDOM_VECTOR_STORE | 0.4862 | [0.4342,0.5371] | 0.0515 | NOT_SEPARATED (control) |

Both tie conventions (mid = DISS's own convention, primary): M1_MAXPOOL optimistic=0.0302,
conservative=0.0296 -- ties are not doing any work at this n (near-continuous cosine scores). n=242
matched pairs per cell (0 dropped by the occurrence-availability filter -- every DISS-matched word had
at least one leak-safe occurrence).

**Paired AUC-difference bootstraps (the decisive numbers, not independent-CI eyeballing):**
- M1 vs A0: **-0.0210 [-0.0393,-0.0020], BELOW, CI-separated.** Max-pooling the target's own
  occurrences scores WORSE at separating substitutability from co-occurrence than the incumbent sum.
- M1 vs N1: **-0.4246 [-0.4777,-0.3718], BELOW, CI-separated, enormous margin.** Max-pooling the
  target's own occurrences is dramatically worse than max-pooling a RANDOM set of OTHER anchors'
  occurrences (which sits at chance, 0.4545).

## What N1_MAXPOOL_RANDOM_OCC decided

**N1 sits at chance (0.4545, NOT_SEPARATED).** This is the opposite of "max inflates similarity by
construction" -- if that were driving M1's score, N1 (max over an equally-sized but content-unrelated
occurrence set) should ALSO be pulled below 0.5, and it is not. N1's own CI cleanly includes 0.5 (and
N2, the frequency-band-donor control, sits slightly above at 0.5296, also NOT_SEPARATED). **So the
depression at M1 is not an artifact of the max operator over more draws -- it requires the target's
OWN occurrence content.** This rules out STOP-IF (ii) ("gain is the max operator, not the occurrences")
in its literal form, because there is no gain to attribute to anything: M1 is a LOSS, and the loss is
specific to the target's own material, not a generic property of max-pooling over N vectors.

## Hit@1 + winner composition (REGIME B, secondary, beside the AUC never instead)

Full-population (n=3,994, richer statistic than the 300-item decisive subsample): A0_SUM hit@1
**0.0270**, S1_SINGLE_OCC hit@1 **0.0328**. On the n=300 decisive subsample:

| arm | hit@1 | no_relation rate | winner co-occ (mean Jaccard) | gold co-occ (mean Jaccard) |
|---|---|---|---|---|
| A0_SUM | 0.0200 | 0.8533 | 0.04113 | 0.01102 |
| S1_SINGLE_OCC | 0.0267 | 0.8567 | 0.03606 | 0.01102 |
| **M1_MAXPOOL** | 0.0233 | 0.8667 | 0.04172 | 0.01102 |
| M2_TOPK_MEAN_K2 | 0.0133 | 0.8600 | 0.04417 | 0.01102 |
| M2_TOPK_MEAN_K3 | 0.0167 | 0.8567 | 0.04305 | 0.01102 |
| M2_TOPK_MEAN_K5 | 0.0233 | 0.8533 | 0.04385 | 0.01102 |
| N1_MAXPOOL_RANDOM_OCC | 0.0200 | 0.9267 | 0.00065 | 0.01102 |
| N2_MAXPOOL_SIZE_MATCHED_SHUFFLE | 0.0067 | 0.9500 | 0.00052 | 0.01102 |

Paired hit@1 diff bootstraps at n=300: M1 vs A0 = +0.0033 [-0.0133,0.0200] NOT_SEPARATED; M1 vs N1 =
+0.0033 [-0.0200,0.0267] NOT_SEPARATED. **Hit@1 has no power to see the AUC-dimension effect at this
n** (base rates ~2%, CI half-width ~0.017-0.023) -- this is exactly the situation the dispatch warned
about ("An arm that raises hit@1 while leaving AUC below 0.5 has not fixed the relation"; here hit@1
is flat in both directions, so it neither confirms nor contradicts the AUC result, it is simply
underpowered at n=300 for a ~2% base rate). **The composition table corroborates the AUC finding
directly**, though: M1_MAXPOOL's winners look almost identical to A0_SUM's on co-occurrence share
(0.04172 vs 0.04113, both ~3.7-3.8x the gold's own 0.01102) -- max-pooling one's own occurrences
produces winners that are JUST as co-occurrence-biased as summing. By contrast N1/N2's winners have
NEAR-ZERO co-occurrence with the query (0.00065/0.00052, actually BELOW gold's own rate) -- their
winners are essentially noise, uninformative in either direction, consistent with scoring random
unrelated content.

## Storage honesty (matched-depth is inherent; this is an efficiency statement, not a mechanism one)

REGIME A: A0_SUM/S1_SINGLE_OCC store 1 vector/word (dim 17,377). M1/M2/N1/N2 store the mean occurrence
count, **54.95 vectors/word (54.95x A0's storage)**, same dimension. REGIME B: A0/S1 store 1
vector/item; M1/M2/N1/N2 store **29.48 vectors/item (29.48x)** over the decisive subsample's own
vocab (dim 21,576). **M1_MAXPOOL loses to A0_SUM while storing ~30-55x more** -- there is no
storage-efficiency reading under which this arm is attractive either.

## STOP-IF: none of the four pre-registered branches fired as literally worded -- a fifth, unanticipated outcome

- (i) M1 beats A0 AND N1: did not fire (M1 loses to both).
- (ii) M1 beats A0 but not N1: did not fire (M1 does not beat A0 at all).
- (iii) M1 ties A0: did not fire in the literal sense (M1 is CI-separated BELOW A0, not tied) -- but
  the PRACTICAL conclusion (iii) points to, "not-collapsing is not sufficient, the write rule's
  remaining suspect is FILTER/SUPERPOSE," still holds and is now stated more strongly.
- (iv) all arms below 0.5: did not fire -- N1 and N2 sit at chance (NOT_SEPARATED), not below 0.5,
  so it is false that "no store this corpus supports can encode substitutability" in general; it is
  specifically the max-pool-of-the-target's-own-material construction that is pulled toward
  co-occurrence, harder than the sum.
- (v) K1 fails: did not fire (K1 = 0.9599, comfortably above the 0.95 gate; instrument licensed).

**The actual, sharper finding: max-pooling the target's own occurrences does not merely fail to fix
the relation -- it makes the store's co-occurrence encoding MEASURABLY WORSE than summing, and this
effect requires the target's own content (the random-occurrence control sits at chance, ruling out a
max-operator artifact).**

## A mechanism reading, offered as a hypothesis-pending-further-VET, not a conclusion

SET S pairs are constructed to CO-OCCUR heavily (top-decile corpus co-occurrence). Any two words that
co-occur a lot are, by construction, more likely to share individual sentences or near-identical local
context, so at least one pair of their INDIVIDUAL occurrence vectors is likely to overlap heavily on
shared local vocabulary -- exactly what a MAX operator is built to find. Summing washes this spike out
across many occurrences; max-pooling preserves and surfaces it. SET P pairs (never co-occurring
synonyms) have no such shared-sentence spike to find, so their max stays low regardless. The net effect
is that max-pooling amplifies co-occurrence signal for co-occurring pairs specifically, which is the
opposite of what the "keep occurrences separate" hypothesis predicted, and it explains why N1 (random,
unrelated occurrence content, no shared-sentence structure with either word) reverts to chance instead
of also depressing.

## Plain-language summary

Keeping a word's occurrences separate and picking the single best match, instead of summing them, does
NOT fix the write rule -- it makes the co-occurrence problem WORSE, not better, and this requires the
word's own real material (a random-occurrence control that uses the same machinery but unrelated
content sits at chance, not depressed). Combined with the two prior findings this organ has landed
(CODE exonerated twice; ACCUMULATE is the measured interference source), the remaining suspects for
Organ A are FILTER and SUPERPOSE, and any future non-collapsing proposal must clear the SAME
random-occurrence control this cell used, because "keep more vectors and take the best" is now a
demonstrated FAILURE mode here, not merely an untested one.
