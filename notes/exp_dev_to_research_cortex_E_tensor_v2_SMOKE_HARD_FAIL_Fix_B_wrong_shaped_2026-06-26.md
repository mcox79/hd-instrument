# cortex_E_tensor_RETEST_fairness_v2 SMOKE HARD_FAIL -- Fix B wrong-shaped (STOP per pre-reg)

**From:** exp_dev (spawn)
**To:** research
**Date:** 2026-06-26
**Status:** STOP at smoke per USER pre-reg gate ("if fairness checks still fail at smoke, STOP and route back to research with diagnosis -- mechanism is fundamentally wrong-shaped"). Full dispatch NOT executed.
**Pre-reg:** `preregs/2026-06-26_cortex_E_tensor_RETEST_fairness_v2.md`
**Cell:** `experiments/exp_cortex_E_tensor_RETEST_fairness_v2.py`
**Smoke metrics:** `data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/metrics.json`

## Verdict per pre-reg

`HARD_FAIL: Fix B failed. cor(E,|W|)=0.984 >= 0.5 -- E mechanism is fundamentally wrong-shaped (E reduces to a magnitude proxy after constant-bump + linear decay).`

## Smoke per-arm (1 seed, N=256, M_OLD=150, M_RECENT=100, J=500, N_USE=45)

| arm | rec_RETRIEVED | rec_UNRETRIEVED | rec_recent | cor(E,\|W\|) | n_down |
|---|---|---|---|---|---|
| BASELINE_NO_DOWNSCALE | 1.000 | 1.000 | 1.000 | -0.033 | 0 |
| **E_GATED_RETEST** | **1.000** | 0.880 | 0.820 | **0.984** | 205 |
| RANDOM_GATED | 0.844 | 0.840 | 0.900 | -0.027 | 205 |
| BASELINE_MAG_GATED | 0.778 | 0.780 | 0.900 | 0.030 | 205 |

`E_retrieved_mean = 499.5` (uniform: every RETRIEVED hit every cycle -> 500 bumps - 500 * 0.001 decay)
`E_unretrieved_mean = 0.0` (UNRETRIEVED got no bumps; decayed to floor)
E is perfectly bimodal: {0.0 for 205 atoms, 499.5 for 45 atoms}.

## Diagnosis (load-bearing for research's next move)

**Fix B did NOT decouple E from magnitude.** Reason:

1. With constant additive bump on HIT + linear decay, E is gated by hit/miss. All 45 RETRIEVED atoms hit every cycle (their keys were repeatedly queried against W; sign-cleanup retrieves them) -> E saturates to 499.5 uniformly. All 205 non-retrieved atoms (105 UNRETRIEVED OLD + 100 RECENT) stay at E=0.

2. The CORRELATION `cor(E, |W|) = 0.984` is therefore a **set-membership correlation**: being in the RETRIEVED-set predicts above-mean Hebbian-readback magnitude `||W @ key_i||`. This is *structural*: the RETRIEVED-set IS implicitly a high-|W| subset because:
   - The cleanup-argmax-correct condition (the hit/miss gate) requires `key_i` to dominate W's response.
   - Atoms with above-average `||W @ key_i||` are exactly the atoms that argmax-correctly under cleanup.
   - So "atoms that get bumped" == "atoms with high effective |W|" by construction.

3. **The pattern is invariant to bump-shape.** Constant-additive bump (Fix B) or EWMA bump (v1) both inherit this: any importance signal driven by retrieval success will correlate with the substrate's own readback-magnitude. Fix B made the bump constant-per-hit, but the HIT itself is magnitude-correlated.

## What's actually interesting in this smoke (under-claim per Fix #28)

- ARM_E_GATED_RETEST.rec_RETRIEVED = 1.000 (preserves what it should; **Fix A worked as designed**).
- E_GATED beats RANDOM on RETRIEVED by +0.156 (RANDOM=0.844).
- E_GATED beats MAG_GATED on RETRIEVED by +0.222 (MAG_GATED=0.778).
- Fix A's RETRIEVED/UNRETRIEVED partition was correctly instrumented and discriminating.

**Honest framing: E carries useful selectivity info; it is NOT independent from magnitude in this regime either.** The "wins on RETRIEVED" finding does NOT recover the pre-reg PASS gate because USER's load-bearing fairness condition was `cor(E,|W|) < 0.30`.

## Why "E does work on RETRIEVED" is consistent with "E is magnitude-coupled"

- Magnitude-based MAG_GATED prunes by `argsort(||W @ key||)[:n_target]`. This is per-atom rank.
- E_GATED prunes by `E < 0.5` which (in this regime) prunes exactly the {E=0} subset == {atoms that never got retrieved}.
- These are different selections: MAG picks the WEAKEST-readback atoms; E picks the NEVER-RETRIEVED atoms. The two subsets only partially overlap.
- E does better on RETRIEVED because E never prunes RETRIEVED (they all have E=499.5). MAG can accidentally prune a RETRIEVED atom if its readback happens to be in the bottom quantile.

So E IS useful as a "did we use this" tag -- but it is NOT an independent importance signal vs |W|. It is a **co-magnitude signal** that exactly tracks the substrate's own retrieval-success structure.

## Routes research could take (NOT exp_dev's call)

1. **Accept the diagnosis and retire the EWMA-as-importance frame.** The USER fairness audit was load-bearing; cor < 0.3 was the structural test; that test failed. Atomize as honest negative + cap mechanism class.

2. **Reframe the claim from "independent importance" to "retrieval-history tag".** E is not an importance signal; it is a "was-this-atom-recently-queried" tag. Under that frame, the cor(E,|W|)=0.98 is expected and not a failure; the PASS bands would change (drop the cor<0.3 requirement, add a "tag-recovery" requirement). This is a research scope-change, not an exp_dev cell-design call.

3. **Try a magnitude-INVARIANT importance signal.** Examples (research probe candidates):
   - **Counterfactual-utility:** does ABLATING this atom degrade recall? If yes, atom is important. Independent of |W| because measured by ablation, not by readback.
   - **Surprisal-weighted bump:** bump E by `(1 - p(observation | substrate))` rather than by `hit`. Requires a generative score; substrate has cleanup attractors so the "low-surprisal" condition is computable.
   - **Random-projection witness:** maintain E as a noise-orthogonal random sketch; correlation with |W| should be ~0 by Johnson-Lindenstrauss.

4. **Run Wave-1.6 ANCHORS 2-4 (ultrametric / SOC / MDL) instead.** These are different mechanism classes per the cortex 4x drill; not contingent on E-tensor. Per handoff section "Recommended dispatch sequence," they were green-lit to run in parallel with ANCHOR 1.

## What exp_dev did NOT do (and why)

- **Did NOT dispatch full run.** Pre-reg + USER deliverable explicitly required STOP at smoke if cor(E,|W|) > 0.5. cor = 0.984.
- **Did NOT retry with different bump shapes.** Per `feedback_encoder_picks_emerge_from_data_not_user_arbitration` analog (the mechanism design is research's scope; cell-author's scope is to honor pre-reg).
- **Did NOT atomize as MEASURED_MECHANISM.** Pure-smoke negative result; Skunkworks owns tier classification. Recommend filing for landed-VET if research wants the smoke-grade evidence in the Store.

## Cost spent

- Authoring + selftest + smoke: ~30 min wall.
- Selftest: PASS (5 mechanism unit-tests including a synthetic decoupling check that PASSES at the unit level -- E[0]=4.9 after 5 hits, E[1]=0 after 0 hits; the failure is at the substrate-coupled level where hit/miss correlates with |W|).

## Asks of research

1. **Ratify or override the pre-reg STOP.** If USER's cor<0.3 is sacrosanct, this is HARD_FAIL period.
2. **Decide route 1/2/3/4 above.** exp_dev will execute whichever.
3. **Consider whether Wave-1.6 ANCHORS 2-4 should be queued now** (parallel mechanism classes; not contingent on E-tensor verdict).

---

-- exp_dev (spawn)
