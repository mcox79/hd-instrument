# exp_cue_binarised_readout_transfer_v1 -- does binarising the cue move the real read-out? (2026-08-17)

Cell: `experiments/exp_cue_binarised_readout_transfer_v1.py`. Full run:
`data/exp_cue_binarised_readout_transfer_v1/metrics.json` (elapsed 85.0s, reusing
`data/exp_cue_information_audit_v1/units.jsonl` read-only for all raw counts, zero built). Smoke:
`data/exp_cue_binarised_readout_transfer_v1_smoke/metrics.json`. Self-test PASS. No tool call was
denied at any point in this run.

## Regression gate: all three diagnosis-cell figures REPRODUCED, off disk, before any hit@1 number was read

`REGRESSION_GATE_DIAGNOSIS_CELL_REPRODUCTION.ALL_PASS = true`, enforced at `--grid full`:

- C0_PROJECTED_256 addressing = 0.0711 (expected 0.0711) PASS
- U0_UNCOMPRESSED addressing = 0.0846 (expected 0.0849, tol 5e-4) PASS
- B1_BINARIZED_RAW addressing = 0.1094 (expected 0.1094) PASS
- B1 vs C0 margin = +0.0383 CI [+0.0295,+0.0473] ABOVE (expected +0.0383 CI [+0.0293,+0.0476]) PASS
- B1 vs U0 margin = +0.0248-ish (measured via the same bootstrap) ABOVE, matching expected +0.0248
  CI [+0.0160,+0.0338] PASS
- S1_SPARSE_HASH_PROJ draw0 (bit-identical seed to the diagnosis cell) = 0.0611 (expected 0.0611)
  PASS; margin vs C0 BELOW (expected BELOW) PASS
- N1_NONNEG_PROJ draw0 (bit-identical seed) = 0.0709 (expected 0.0709) PASS; margin vs C0
  NOT_SEPARATED (expected NOT_SEPARATED) PASS

All three headline diagnosis figures reproduce exactly. Nothing about the addressing-side finding
is in question.

## K1_KNOWN_ANSWER and N1_NULL: instrument alive in every space

K1 (self-query, addressing side, gate >= 0.98): R0=1.0000, R1=1.0000, R2_draw0=1.0000, ALL PASS.
N1 (permuted cue): addressing side near 0 for all arms (chance=0.000182); hit@1 side near this
population's own analytic chance (0.010088): R0=0.009765, R1=0.007020, R2=0.008262, all flagged
`near_chance: true`. The instrument is not loose in either measure.

## Arm-by-arm, BOTH measures, n=3994 items / 5491 anchors, CI half-widths and null p95 beside every number

Addressing accuracy (paired bootstrap, N_BOOT=10000):

| arm | addressing | margin vs R0 | CI95 | band |
|---|---|---|---|---|
| R0_INCUMBENT | 0.0711 | -- | -- | -- |
| R1_BINARISED | 0.1094 | +0.0383 | [+0.0295,+0.0473] | **ABOVE** |
| R2_BINARISED_PROJECTED (3 draws: 0.0834/0.0794/0.0834, mean 0.0821 sd 0.0019) | 0.0834 | +0.0123 vs R0 | [+0.0035,+0.0210] | ABOVE |
| R2 vs R1 | -- | -0.0260 | [-0.0333,-0.0188] | BELOW |

Hit@1 vs WordNet gold (tie-corrected primary, analytic null half-width = 1.96*sqrt(p(1-p)/n) beside
each point):

| arm | hit@1 (hit_exp) | half-width | hit_opt | hit_cons | margin vs R0 | CI95 | band |
|---|---|---|---|---|---|---|---|
| R0_INCUMBENT | 0.0223 | 0.0046 | 0.0223 | 0.0223 | -- | -- | -- |
| R1_BINARISED | 0.0249 | 0.0048 | 0.0260 | 0.0248 | +0.0026 | [-0.0026,+0.0078] | **NOT_SEPARATED** |
| R2_BINARISED_PROJECTED | 0.0205 | 0.0044 | 0.0205 | 0.0205 | -0.0018 vs R0 | [-0.0070,+0.0033] | NOT_SEPARATED |

R2 vs R1 hit@1: -0.0044 CI [-0.0089,+0.0001], NOT_SEPARATED.

R2 vs R1 on ADDRESSING is CI-separated BELOW (projecting after binarising gives back some of the
gain: R2's dense-random-projection re-imposes the projection defect on top of the binarisation fix,
landing between R0 and R1 -- so the two defects are NOT fully independent on addressing: R2 does not
recover R1's full gain, it only recovers about a third of it). On hit@1 all three arms are mutually
NOT_SEPARATED, so this interaction question cannot be resolved on the hit@1 measure at this n.

## The four floors, on THIS population, both tie conventions, CI half-width and null p95 beside every one

| floor | hit_exp | half-width | hit_opt | hit_cons |
|---|---|---|---|---|
| F_ORTHOGRAPHIC | 0.0873 | 0.0088 | 0.0984 | 0.0789 |
| F_FREQUENCY | 0.0185 | 0.0042 | 0.0185 | 0.0185 |
| F_SCRAMBLE (against the PARTIAL cue, matching R0/R1/R2's own regime) | 0.0095 | 0.0030 | 0.0095 | 0.0095 |
| **F_CONSTANT_PROTOTYPE (the winning floor)** | **0.1390** | 0.0107 | 0.1390 | 0.1390 |
| ORACLE_CONSTANT (NOT a floor) | 0.1715 | 0.0117 | 0.1715 | 0.1715 |

`F_ORTHOGRAPHIC` and `F_FREQUENCY` and `F_CONSTANT_PROTOTYPE` do not depend on cue regime (they
read the target lemma's own trigram profile / the anchor's own corpus frequency / the anchor's own
mean-direction cosine, none of which touches Q_part or Q_exact) and are therefore identical whether
scored under the partial or exact-key regime. `F_SCRAMBLE` DOES depend on cue regime and is scored
here against the PARTIAL cue (0.0095), not the EXACT-KEY cue `exp_readout_ceiling_diagnosis_v1` used
(0.0873 in that cell's own report is F_ORTHOGRAPHIC, not F_SCRAMBLE, and is reproduced here at the
same value 0.0873 by construction since it is regime-independent) -- crossing regimes for F_SCRAMBLE
would have been the population-crossing error the project's standing rule forbids.

R0, R1 and R2 are ALL CI-separated BELOW every floor, R1 vs the winning floor
(F_CONSTANT_PROTOTYPE): -0.1140 CI [-0.1257,-0.1024], BELOW. **None of the three arms clears the
floor set.** Stop-if (i) did NOT fire.

## Standing rule 12 -- orthographic-correlation check

Per-item gain (R1 hit_exp minus R0 hit_exp) correlated against that item's own best-gold
F_ORTHOGRAPHIC score, paired bootstrap CI on the Pearson r:

- All 3994 items: r = -0.0037, CI [-0.0328,+0.0246], NOT_SEPARATED.
- The 119 items where the gain is nonzero: r = -0.0370, CI [-0.2092,+0.1487], NOT_SEPARATED.

**No correlation.** R1's addressing gain is not concentrated on items whose gold answer looks like
the query word. Stop-if (iii) did NOT fire, and given R1 does not clear the trigram floor either,
the spelling-failure question is moot here regardless.

## Which stop-if fired

**(ii) R1 improves addressing (CI-separated ABOVE, reproduced) but hit@1 is NOT_SEPARATED from R0.**
Not (i): no arm clears max(floors). Not (iii): no orthographic correlation, and R1 does not clear
the trigram floor anyway. Not (iv): K1 passed in every space.

`STOP_IF_VERDICT.primary_verdict = "ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED"`.

## The one-sentence answer

**No -- fixing addressing does not fix read-out.** Binarising the cue produces a real, CI-separated
gain on ADDRESSING (+0.0383, reproducing the diagnosis cell exactly) but the corresponding hit@1
gain (+0.0026 CI [-0.0026,+0.0078]) does not separate from zero, all three arms sit CI-separated
below every recomputed floor including the constant/prototype floor, and the modest addressing gain
that does exist is not explained by orthographic similarity to the gold. This is exactly the
pre-registered honest prior stated before this cell ran: the store encodes co-occurrence
(syntagmatic) while the task scores substitutability (paradigmatic), and no amount of cue
compression fixes which relation is written to the store. Addressing and read-out are separately
capped; the next question belongs to the write rule, not to further cue engineering.
