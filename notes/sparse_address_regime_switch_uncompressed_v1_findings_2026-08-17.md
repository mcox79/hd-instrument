# exp_sparse_address_regime_switch_uncompressed_v1 -- ITEM 3, unblocked by item 1 (2026-08-17)

Cell: `experiments/exp_sparse_address_regime_switch_uncompressed_v1.py`. Full run:
`data/exp_sparse_address_regime_switch_uncompressed_v1/metrics.json` (elapsed 168s first pass, 23s on
re-run from checkpoint after a verdict-logic fix). Smoke:
`data/exp_sparse_address_regime_switch_uncompressed_v1_smoke/metrics.json`. Self-test and both runs
PASS. Disclosure: one `Bash` call was auto-denied (a bundled `rm -rf` + the real smoke run, matching
the documented rm-bundling fault class); reported verbatim, not retried, re-issued without the
deletion (the output directory did not exist yet, so no teardown was needed at all).

## Prior-work check (substrate-KB, cosine>0.30)

`bash tools/substrate_query.sh "sparse expanded address dense value hippocampal index regime switch
write read asymmetry"` -- top hits at cosine 0.3662 / 0.3496 / 0.3438 are all
`exp_sparse_address_dense_value_v1` (the sibling cell this one directly extends) and its smoke. This
cell is a deliberate EXTENSION (same arm names, same regime-switch design, on item 1's U0-uncompressed
base instead of the sibling's C0-compressed base) -- not an independent rediscovery.

## What item 1 unblocked, and the target this cell reproduces before trusting anything else

`data/exp_cue_information_audit_v1/metrics.json`: on the identical store/cue/pool/gold,
U0_UNCOMPRESSED addresses at 0.0849 under a partial cue vs the incumbent C0_PROJECTED_256's 0.0711
(+0.0138 CI [+0.0083,+0.0195], CI-separated). This cell's A0_FLAT arm (natural, untruncated U0
representation on both key and cue) REPRODUCES that target exactly on its own construction:
`REGRESSION_GATE_U0_TARGET: measured=0.0849, expected=0.0849, PASS=True`.

## What exp_cleanup_basin_conditional_v1 said (read here for the first time, per the task)

Landed 2026-08-16T22:41; nobody had read it before this cell was authored. It stratifies cleanup lift
by tau=cos(cue, own stored row) against the organ's own basin (cliff between tau 0.20 and 0.30). Its
own `PREREGISTERED_READ`: lift is CI-separated ABOVE **only in the LOWEST-tau stratum**
(+0.0036 [+0.0009,+0.0072], b64) and NOT_SEPARATED in every higher stratum including the HIGHEST
(+0.0154 [-0.0039,+0.0347]) -- the OPPOSITE of what basin theory predicts (lift should grow toward the
basin edge, not appear only at the farthest point from any basin). This REFUTES the basin explanation
and licensed NOT building an elaborate settle mechanism here. One cheap check was armed
(T1_SETTLED, score-space anchor-centering) and it landed exactly where expected: NULL
(-0.0010 [-0.0025,+0.0003], NOT_SEPARATED).

## Arm-by-arm, primary measure (addressing accuracy, partial cue, n=3994, chance=1/5491=0.000182)

| arm | K_WRITE | K_READ | ADDRESSING_ACCURACY |
|---|---|---|---|
| A0_FLAT | ALL | ALL | 0.0849 |
| T1_SPARSE_KEY_DENSE_VALUE | 32 | ALL | 0.0704 |
| T2_REGIME_SWITCH | ALL | 8 | 0.0886 (the grid MAXIMUM) |
| C1_SPARSE_BOTH | 32 | 32 | 0.0704 |
| K1_ORACLE_ADDRESS (self-match) | 32/32 | -- | 1.0000 |
| N1_RANDOM_ADDRESS | nnz-matched random | -- | 0.0000 |

Decisive paired-bootstrap margins (10,000 draws), CI half-width beside each, null p95 for N1 is its
own reported value (0.0000 against chance 0.000182):

- **T1 vs A0_FLAT: -0.0145 [-0.0203,-0.0088], half-width 0.0057 -> BELOW, CI-separated.** Sparsifying
  the KEY costs accuracy.
- **T2 vs A0_FLAT: +0.0037 [-0.0013,+0.0088], half-width 0.0051 -> NOT_SEPARATED.** The raw grid
  maximum (0.0886) looked like it beat A0_FLAT (0.0849) as a bare point estimate; the PAIRED bootstrap
  (same items, same draws) shows the margin is NOT CI-separated. This correction happened during
  authoring -- an earlier verdict-logic pass omitted this margin entirely and would have missed both
  the apparent win and its correct non-significance.
- **T2 vs T1: +0.0182 [+0.0118,+0.0248], half-width 0.0065 -> ABOVE.** Sparsifying the cue (not the
  key) is reliably better than sparsifying the key, though T2 itself does not clear A0_FLAT.
- **C1 vs T1: 0.0000 [0,0], NOT_SEPARATED, bit-identical.** Flagged with a construction caveat: T1's
  chosen K_WRITE=32 sits ABOVE the cue's own median nnz (12.0 words), so truncating the cue to K=32 is
  a no-op for at least half the items -- this specific tie is partly a construction artifact, not
  solely evidence the key/value distinction is inert. The cleaner read is T1 vs T2 (opposite
  directions: sparsify-key hurts, sparsify-cue helps, though neither clears A0_FLAT CI-separated).
- **K1_ORACLE_ADDRESS = 1.0000 (gate 0.999), PASSES.** N1_RANDOM_ADDRESS = 0.0000 against chance
  0.000182, NEAR_CHANCE. Both validity arms pass independently.
- **T1_SETTLED vs T1: -0.0010 [-0.0025,+0.0003], NOT_SEPARATED** -- the settle check landed exactly
  where the basin cell's finding predicted: null.

## Secondary: hit@1 vs WordNet gold, partial cue, n=3994

Every arm sits BELOW the binding floor (F1_TRIGRAM, 0.0871), CI-separated: A0_FLAT -0.0631
[-0.0727,-0.0536], T1 -0.0661 [-0.0757,-0.0566], T2 -0.0653 [-0.0748,-0.0558], C1 -0.0661
[-0.0757,-0.0566]. Consistent with the standing "we underperform a spell-checker" finding -- not a
new negative, and not the decisive read (addressing accuracy above is).

## Which stop-if fired

**(i) T1 ties/loses to A0_FLAT (BELOW, CI-separated) while K1_ORACLE_ADDRESS passes.** Sparsifying
the KEY costs real accuracy; the instrument is not loose (K1=1.0, N1 at chance). T2_REGIME_SWITCH
(sparsify the cue instead) is directionally the better half of the design (+0.0182 over T1,
CI-separated) but does not itself clear A0_FLAT CI-separated (+0.0037, NOT_SEPARATED) -- so this is
**not** stop-if (iv)'s "efficiency, not capability" either, in the strict sense: no configuration
clears A0_FLAT's own ceiling CI-separated, up or down, in either direction that would count as a clean
efficiency win (T1 and C1 both LOSE accuracy at their sparsified level, not merely match it).

## Capability or efficiency

**Neither, cleanly.** This item did not buy a second capability win beyond item 1's (T2 vs A0_FLAT is
NOT_SEPARATED, not a beat) and it did not buy a clean efficiency win either (T1/C1, the genuinely
sparsified-key arms, LOSE accuracy CI-separated rather than matching it at lower cost). The informative
result is DIRECTIONAL: sparsifying the stored KEY (address) reliably hurts, sparsifying the CUE (read
side) reliably helps relative to sparsifying the key, and the LINK mechanism itself is not the
bottleneck (K1_ORACLE=1.0 at every configuration tested). The honest summary in the task's own
vocabulary: **the sweep sits at or below A0_FLAT's ceiling in its best (T2) configuration once CI is
accounted for** -- so if forced into the (iv) framing, this is closer to "no efficiency and no
capability" than to "efficiency bought" -- and that is reported plainly, not softened.

Data: `data/exp_sparse_address_regime_switch_uncompressed_v1/metrics.json`,
`data/exp_sparse_address_regime_switch_uncompressed_v1_smoke/metrics.json`.
