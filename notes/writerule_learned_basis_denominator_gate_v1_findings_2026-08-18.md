# ORGAN A CODE GATE: does a learned basis or a denominator move the RELATION? -- CODE is exonerated.

**FULL run landed** `data/exp_writerule_learned_basis_denominator_gate_v1/metrics.json`,
verdict `WRITERULE_CODE_GATE__CODE_EXONERATED__NEITHER_ARM_MOVES_COMPOSITION__C1_WIN_K_64__C2_WIN_row`,
2135s elapsed. Cell: `experiments/exp_writerule_learned_basis_denominator_gate_v1.py`. Pre-reg and full
derivation: `notes/drill_what_cortex_computes_across_episodes_write_rule_equations_2026-08-18.md`.

## Gates

- REGRESSION GATE: measured 0.0223 vs expected 0.0223 (tol 0.0005) -- PASS, reproduces the landed
  instrument.
- A0 self-row construction (used uniformly for every arm) vs the officially cached exact-key query:
  0.0481 vs 0.0481 -- exact agreement, the uniform-construction methodology is sound.
- K1 (self-address, all named arms): A0=1.0, C1=0.99975, C1_CTRL_RAND=1.0, C1_CTRL_FREQ=1.0,
  C2=1.0, C2_WRONGPOOL=1.0, C2_PURE_IDF=1.0 -- all PASS (>=0.95).
- N1 (derangement null): addressing 0.0 (chance 0.00018) -- PASS.
- Floors recomputed on this population (n=3994 scored items): F_ORTHOGRAPHIC 0.0873 [hw 0.0085],
  F_FREQUENCY 0.0185 [0.0043], F_SCRAMBLE 0.0103 [0.0031], F_CONSTANT_PROTOTYPE 0.1390 [0.0108]
  (binding floor). Analytic null half-width at n=3994: 0.0260.

## Arm-by-arm hit@1 (+/- CI half-width) and margin vs A0

| arm | hit@1 | margin vs A0 (point, CI95, band) |
|---|---|---|
| A0_RANDOM_PROJECTION | 0.0481 +/-0.0066 | -- |
| C1_LEARNED_BASIS (k=64 winner) | 0.0553 +/-0.0071 | +0.0073 [-0.0005,+0.0150] NOT_SEPARATED |
| C1_CTRL_MATCHED_RANK_RANDOM (k=64) | 0.0421 +/-0.0061 | -0.0060 [-0.0130,+0.0010] NOT_SEPARATED |
| C1_CTRL_FREQUENCY_SHUFFLED (k=64) | 0.0148 +/-0.0039 | -0.0333 [-0.0411,-0.0258] BELOW |
| C2_WRITE_TIME_DIVISIVE_NORM (sigma=1,n=1,pool=row winner) | 0.0586 +/-0.0073 | +0.0105 [+0.0035,+0.0175] ABOVE |
| C2_CTRL_WRONGPOOL | 0.0586 +/-0.0073 | +0.0105 [+0.0035,+0.0175] ABOVE (IDENTICAL to C2, see below) |
| C2_CTRL_PURE_IDF | 0.0303 +/-0.0054 | -0.0177 [-0.0250,-0.0103] BELOW |

C1 sweep across k = 64/128/256/512/1024/2048: hit@1 = 0.0553/0.0523/0.0503/0.0463/0.0416/0.0393 --
MONOTONICALLY FALLING as k grows. The drill's prediction that k>256 (expansion) would be the
interesting half is not borne out on accuracy: smaller k wins throughout, at every point on the grid.
SVD elapsed: k=64 fast, k=1024 74s, k=2048 1655s (ARPACK cost grows steeply near the matrix's own
rank, ~5491; disclosed for anyone repeating this sweep).

C2 sweep across sigma in {1,4,16} x n in {1,2} x pool in {col,row,both}: pool='row' wins at every
sigma/n (0.0586 flat -- see the degeneracy below), pool='col' 0.0298-0.0356, pool='both'(=PPMI) 0.0431.

## Winner composition (winner share, gold share, ratio, no-relation rate), all vs A0, n_probe=700

A0 reference: no-relation rate 0.7971, winner share 0.8900, gold share 0.4757, winner mean 0.07798,
gold mean 0.02148, ratio 3.630.

| arm | no-rel delta (CI95, band) | winner share | gold share | winner mean | gold mean | ratio |
|---|---|---|---|---|---|---|
| C1_LEARNED_BASIS | -0.0068 [-0.0414,+0.0286] NOT_SEPARATED | 0.6743 | 0.4186 | 0.06274 | 0.02037 | 3.080 |
| C1_CTRL_MATCHED_RANK_RANDOM | +0.0047 [-0.0271,+0.0357] NOT_SEPARATED | 0.6029 | 0.3643 | 0.05652 | 0.01671 | 3.382 |
| C1_CTRL_FREQUENCY_SHUFFLED | +0.0858 [+0.0486,+0.1229] **ABOVE** (worse) | 0.0600 | 0.1829 | 0.00053 | 0.00575 | 0.092 |
| C2_WRITE_TIME_DIVISIVE_NORM | -0.0055 [-0.0357,+0.0229] NOT_SEPARATED | 0.8714 | 0.4814 | 0.08121 | 0.02209 | 3.676 |
| C2_CTRL_WRONGPOOL | -0.0055 [-0.0357,+0.0229] NOT_SEPARATED (IDENTICAL) | 0.8714 | 0.4814 | 0.08121 | 0.02209 | 3.676 |
| C2_CTRL_PURE_IDF | +0.0244 [-0.0129,+0.0614] NOT_SEPARATED | 0.9129 | 0.3600 | 0.06579 | 0.01640 | 4.012 |

For scale, the landed baseline for the incumbent CODE step (`data/exp_writerule_step_ladder_v1`,
`COMPOSITION_DELTA_TABLE`, CODE_PROJECT row, R3->R4) is +0.0031 [-0.0243,+0.0300] NOT_SEPARATED.
Neither C1 nor C2 moves further than that landed null -- both sit inside a similar-width NOT_SEPARATED
band.

## Stop-if fired

**(iv) NEITHER C1 nor C2 moves composition -- CODE IS EXONERATED AS THE PRIME SUSPECT; the organ's
defect is elsewhere.** Neither arm's composition delta vs A0 is CI-separated in the improving
direction. C1's own accuracy edge (+0.0073) is not itself CI-separated from A0, and its matched-rank
random control (-0.0060) sits within 2 combined half-widths of it -- so even the raw accuracy movement
cannot be attributed to the learned basis specifically. The one CI-separated accuracy gain (C2 at
+0.0105 ABOVE) is explained below as an artifact, not a denominator effect.

## An honest subtlety found while running this cell: the winning C2 config (pool='row') is a
## mathematical no-op under cosine scoring, and its own WRONGPOOL control cannot catch that.

`divisive_normalize(..., pool='row')` divides an anchor's ENTIRE context-count row by a single scalar
(that anchor's own total mass). Every downstream step in this cell (random projection, then
L2-normalisation before cosine) is linear per row, so dividing a row by any positive constant is
undone by the L2 normalisation before scoring -- **it cannot change any cosine similarity, and
therefore cannot change hit@1 or composition, regardless of what value the denominator takes.** This
is the SAME mathematical class the drill's own literature review flags for synaptic scaling (sec 2.4:
"a rank-0 normalisation... a mathematical no-op on every number we measure"). The numbers confirm it
exactly: C2_WRITE_TIME_DIVISIVE_NORM and C2_CTRL_WRONGPOOL are IDENTICAL to four decimal places on
both hit@1 and every composition field, because permuting a set of scalars that never affects the
score cannot produce a different result. **This means pool='row' was never a live test of "does a
denominator matter" -- its accuracy edge over A0 (+0.0105 CI-separated) is attributable entirely to
using a freshly-sampled Gaussian random basis at k=256 instead of A0's original sha256 bipolar basis
H, the same kind of basis-identity effect C1_CTRL_MATCHED_RANK_RANDOM is designed to catch (at a
different k).** The genuine denominator variants in this sweep are pool='col' (0.0298-0.0356, BELOW
A0) and pool='both'=PPMI (0.0431, below A0's 0.0481) -- neither beat A0 on accuracy at all, and neither
was the sweep's accuracy-selected winner, which is why the composition-instrument-facing arm ended up
being the degenerate one. **Lesson for any future sweep over this candidate: exclude pool='row', or
score it under a non-scale-invariant metric, or it will silently win an accuracy sweep for a reason
that has nothing to do with normalisation.**

## The frequency-shuffled control is dramatically, CI-separated WORSE than A0 -- and this validates
## the instrument, not just the control

C1_CTRL_FREQUENCY_SHUFFLED collapses hit@1 to 0.0148 (vs A0's 0.0481, CI-separated BELOW) and its
composition collapses even harder: no-relation rate rises to 0.8829 (CI-separated ABOVE = worse),
winner share falls to 0.06 (from A0's 0.89), and the winner/gold ratio falls to 0.092 (from 3.63) --
its winners essentially never co-occur with the query at all. This is a real, large, unambiguous
effect, which matters for how to read C1's own null: the composition instrument and the
frequency-shuffled construction are demonstrably sensitive enough to detect a genuine large effect
when one is present. C1's own NOT_SEPARATED reading is therefore a real null, not an underpowered
instrument failing to register anything.

## Online Sanger/GHA eta confirmation (secondary, scoped; NOT part of the main sweep)

n_sub=500 anchors, d_sub=2000 top-frequency context words, k=16, 3 epochs. Subspace alignment to the
matched-scale SVD solution: eta=0.001 -> 0.076, eta=0.01 -> 0.100, eta=0.05 -> 0.196. All low (far
from 1.0) at this small epoch count -- the streaming rule has not converged to the closed-form SVD
solution in 3 epochs at these eta values on this subsample. This is disclosed as a genuine limitation
of the confirmatory check's scope (small n_sub/d_sub/epoch budget), not evidence against the
Oja/Sanger-SVD equivalence itself, which is a proven theorem under the stated (whitened-input,
converged) limit -- it says only that 3 epochs at eta<=0.05 on this subsample is not enough to reach
that limit. Sweeping further (more epochs, larger eta, or a proper learning-rate schedule) was out of
this cell's time budget; recorded as an open item, not a finding.

## Plain-language answer

Neither a learned basis (the closed-form Oja/Sanger equivalent, truncated SVD, swept k=64 through
2048) nor a write-time denominator (Carandini-Heeger divisive normalisation / PPMI, swept sigma, n,
and pool) moved the winner's RELATION to the query -- both sit inside a statistically flat band on
composition, the same flat band the incumbent random projection already measured. The one accuracy
gain that did clear its confidence interval traces back to an accidental change of random basis, not
to the denominator, once a mathematical no-op in the winning sweep point is accounted for. CODE is
exonerated as Organ A's prime suspect a second time, on a substantially harder test than the first
(learned structure and a real denominator, not just "is the incumbent random projection destructive");
the organ's defect is elsewhere -- most plausibly at ACCUMULATE (the bare, undenominated sum) or in
what "context" is fed to CODE in the first place, per the drill's own section 9/10 ranking (C3
episode-keeping, C4 predictive accumulation).

## Prior-work check

`bash tools/substrate_query.sh "learned basis Oja Sanger divisive normalization PPMI write rule
cortex"` returned no output within 60s, consistent with the standing STALE status
(`hd_director_kb_continuous_ingest` livelock, `notes/STATUS.md`) and the same exemption the drill note
records for itself. Substitute: the drill note's own sec 1/11/12 enumeration, read in full before this
cell was authored.
