# THE MEANING-ASSET POSITIVE, READ PROPERLY -- **ONE ARM OF ELEVEN CLEARS THE SEMANTIC FLOOR, AND IT CLEARS IT BY A CI THAT ENDS AT 0.016**

**`exp_meaning_asset_fair_test_v1`, landed 2026-08-15, 7,228 s (2 hours), `validity_gates_all_passed:
True`.** *The only clean positive in the knowledge-evaluation set, and the first genuine positive
result I have reported tonight.* **It is real. It is also narrower than its verdict string.**

**Verdict as written:** `ASSET_CLEARS_THE_STRONGEST_FLOOR`.

---

## 1. THE SEMANTIC AXIS (SimLex, n=322), ALL ARMS

| arm | rho | vs strongest floor (`A_FREQUENCY`) | CI95 | clears? |
|---|---|---|---|---|
| **`ASSET_RETRAIN_ISOL`** | **0.2581** | **+0.1665** | **[0.016, 0.313]** | ✅ **TRUE** |
| `ASSET_V2_CTX` | 0.2065 | +0.1149 | [-0.034, 0.264] | ✗ |
| `ASSET_RETRAIN_CTX` | 0.2027 | +0.1111 | [-0.040, 0.263] | ✗ |
| `ASSET_V2_ISOL` | 0.1890 | +0.0975 | [-0.055, 0.248] | ✗ |
| `ASSET_V2_TOKEMB` / `ASSET_RETRAIN_TOKEMB` | 0.0783 | **-0.0133** | [-0.160, 0.131] | ✗ |
| `CTRL_RANDINIT_TOKEMB` | **0.0099** | -0.0817 | [-0.223, 0.063] | ✗ |

**➡️ EXACTLY ONE ARM OF ELEVEN CLEARS, AND ITS CI LOWER BOUND IS 0.016 -- it clears by a hair.**
*Three more sit just under with CIs that barely touch zero. **The verdict string is true and describes
one arm; quoting it unqualified would imply eleven.***

## 2. ✅ WHAT IS GENUINELY GOOD HERE, AND IT IS NOT NOTHING

- **THE RANDOM CONTROL SITS AT rho = 0.0099.** *The harness is sound -- an information-free arm scores
  zero, which is the check that failed nowhere tonight but is skipped everywhere.*
- **`validity_gates_all_passed: True`** -- unlike `exp_storage_quality_instrument_v1`, which passed
  10 of 11 and **correctly refused to publish any number at all.**
- **RETRAINING HELPS, AND ONLY IN ONE PLACE:** `RETRAIN_ISOL` 0.2581 vs `V2_ISOL` 0.1890. *And
  `TOKEMB` is **bit-identical** between V2 and RETRAIN (0.0783 both) -- consistent with token
  embeddings being frozen, i.e. the retrain genuinely did not touch that arm. That internal
  consistency is itself a small positive control.*
- **ORDERING IS STABLE AND INTERPRETABLE: `ISOL` > `CTX` > `TOKEMB`** across both V2 and RETRAIN.

## 3. ⚠️ AND ON THE ORTHOGRAPHIC GOLD, EVERY ARM IS **BELOW** ITS FLOOR

| | arm lift | `A_ORTHOGRAPHIC` floor | band |
|---|---|---|---|
| `GOLD_ORTHO`, best arm | 16.80 | **118.12** | **BELOW** |
| `GOLD_FREQBAND`, best arm | 1.037 | `A_FREQUENCY` **7.757** | **BELOW** |
| `GOLD_PLANTED` | ~1.00 | ~1.00 | NOT_SEPARATED |

**That is correct behaviour, not a failure** -- an orthographic floor should dominate an orthographic
gold, and a *planted* gold showing nothing is what a working planted control looks like. **But it
means the phrase "clears the strongest floor" applies to ONE axis and ONE arm, while on two other
axes every arm is beaten by a trivial baseline.**

## 4. HOW THIS SHOULD BE QUOTED FROM NOW ON

> **On SimLex (n=322), the retrained isolated-context meaning asset reaches rho 0.2581 and beats the
> frequency floor by +0.1665, CI [0.016, 0.313] -- the only one of eleven arms to separate, and
> marginally. A random-init control sits at 0.0099. On orthographic and frequency-band golds every
> arm is below its floor.**

*Not "the meaning assets clear the strongest floor."*

## TLDR

I opened the one clearly positive result in this area — a two-hour experiment from the 15th testing
whether our built-but-unused "meaning assets" actually capture meaning.

**The good news is real: one version does.** Judged against human ratings of how similar word pairs
are, it beats the best cheap baseline, and a random control sits at zero as it should — meaning the
test itself is sound.

**But the headline oversells it.** Eleven versions were tested. **One clears the bar, and it clears
by a whisker** — the plausible range for its advantage starts at 0.016, just barely above nothing.
Three others come close but can't be distinguished from the baseline at all.

**And on two other measures, every single version loses to a trivial baseline.** That's actually
correct — those measures are about spelling and word-frequency, where a spelling-based baseline
*should* win — but it means "clears the strongest floor" describes one arm on one measure, not the
whole picture.

**Two details that increase my confidence in the work itself:** the random control scores zero, and
one arm is bit-for-bit identical before and after retraining, which is exactly what should happen if
that part was frozen. Small internal consistencies like that are what a careful experiment looks
like.

## QUESTIONS

None.

## NEXT STEPS

1. **`ASSET_RETRAIN_ISOL` is the one to pursue** -- and it wants a seed replication before anything is
   built on it, since a CI ending at 0.016 is one unlucky sample from vanishing.
2. **Quote it with the arm name and the CI**, never as "the assets clear the floor".
3. `exp_encoding_quality_instrument_v1/v2` remain unread in this set.
