# exp_cue_information_audit_v1 -- is the answer in the partial cue at all? (2026-08-17)

Cell: `experiments/exp_cue_information_audit_v1.py`. Full run: `data/exp_cue_information_audit_v1/metrics.json`
(elapsed 239.8s). Smoke: `data/exp_cue_information_audit_v1_smoke/metrics.json`. Both self-tests and both
runs PASS; disclosure: one `Bash` call was auto-denied (a bundled `rm -f` + real work, matching the
documented `rm`-bundling fault class in CLAUDE.md) and reported verbatim before retrying without the
deletion; no other denial occurred.

## Recoverability -- reproduced independently, not adopted

The prior fragment's claim (`.claude/scan-out/address-information-audit.json`, attributed, never adopted)
was 400/400 exact, max abs error 0.000e+00. This run checked **every** `keep_ALL` item on disk, not a
sample: `n_checked_full_pop=3994`, `n_L_mismatch=0`, `n_sentidx_none_but_cache_kept_true=0`,
**`max_abs_error=0.0`, `ALL_EXACT=True`**. Recoverability REPRODUCED. The encoder identity `H^T P_a ==
mat[a]` was additionally checked bit-exact on the STORE side (never checked by the prior fragment) for all
5491 working anchors: `max_abs_error_H_T_Pa_vs_mat=0.0`. The cue-kind split was therefore fully
constructible, not reduced.

Regression gate: `C0_PROJECTED_256` on the full landed open pool reproduced the landed number exactly
(`measured=0.0223`, `expected=0.0223`, tol 5e-4, PASS, n=3994) -- this is the identical store/cue/pool/gold
as `exp_cue_to_store_translation_v1` and `exp_task_degeneracy_v1`.

## Arm-by-arm, primary measure (addressing accuracy, context-sentence cue, n=3994, chance=1/5491=0.000182)

| arm | value |
|---|---|
| K1_EXACT_KEY_C0 | 1.0000 (validity: PASS) |
| K1_EXACT_KEY_U0 | 1.0000 (validity: PASS) |
| N1_RANDOM_KEY_C0 | 0.0003 (vs theoretical chance 0.000182) |
| N1_RANDOM_KEY_U0 | 0.0003 |
| C0_PROJECTED_256 | 0.0711 |
| **U0_UNCOMPRESSED** | **0.0849** |

Decisive paired-bootstrap margins (10,000 draws), CI half-width beside each:

- **U0 vs C0: point +0.0138, 95% CI [+0.0083, +0.0195], half-width 0.0056 -> ABOVE, CI-separated.**
- U0 vs N1_U0: +0.0846 [+0.0761, +0.0934], half-width 0.0087 -> ABOVE
- C0 vs N1_C0: +0.0708 [+0.0628, +0.0789], half-width 0.0081 -> ABOVE
- N1's empirical rate (0.0003) sits within ~1 binomial SE of the theoretical chance 0.000182
  (SE approx 0.00027 at n=3994) -- the random-key control is behaving as designed.

## Cue-kind split (secondary, constructible because recoverability held)

- SYNONYM_SET addressing: U0=0.0148 vs C0=0.0035, margin +0.0113 [+0.008, +0.0148] (half-width 0.0034)
  ABOVE. (Its hit@1-vs-WordNet-gold reading is not reported -- would be INADMISSIBLE_CIRCULAR, built from
  the same relation that builds the gold set.)
- WORD_ONSET addressing: U0=0.0008 vs C0=0.0008, margin 0.0 [-0.0013, +0.0013] NOT_SEPARATED -- a
  single-character-prefix cue carries almost nothing either way, as expected.

## Secondary measure (hit@1 vs WordNet gold, n=3994, chance=0.0101)

Both regimes sit BELOW their own binding floor, CI-separated: C0=0.0223 vs F4_CONSTANT_PROTOTYPE_C0=0.1390
(margin -0.1167 [-0.1284,-0.1054], half-width 0.0115); U0=0.0240 vs F1_TRIGRAM_ONLY=0.0871 (margin -0.0631
[-0.0727,-0.0536], half-width 0.0096). Consistent with the standing "we underperform a spell-checker"
finding -- not a new negative, and not what this cell exists to decide (the primary addressing-accuracy
reading above is the decisive one).

## Which stop-if fired

**(iii) U0_UNCOMPRESSED beats C0_PROJECTED_256, CI-separated.** Neither (i) (U0 near C0) nor (ii)
(K1 not at ceiling) fired. `STOP_IF_VERDICT.verdict = "iii_U0_BEATS_C0_compression_is_the_defect"`.

## The one-sentence answer

**Yes -- more of the answer is in the cue than our 256-dim random projection currently delivers**: the
raw, uncompressed count vectors address their target 8.49% of the time under the identical partial cue
where the incumbent projected encoder manages 7.11%, a CI-separated gap (+0.0138 [+0.0083,+0.0195]), so
the compression itself is a measured, real defect rather than the cue being informationally empty --
though both numbers are small in absolute terms, so the cue's information content is real but limited,
and the next question this licenses is an EXPANSION build (sibling plan item 3), not a redirect to the
write side.
