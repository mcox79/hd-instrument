# THE F5 BAR **REPLICATES**: `+2.00` ON FOUR INDEPENDENTLY-BUILT ITEM SETS, **1.1x SPREAD**

**Follows** `notes/THE_F5_BAR_IS_MEASURED_BEFORE_THE_BUILD_...md`, which measured the bar on ONE set.
**Four single-seed wins were withdrawn in one session this week**, so a bar taken from one item
sample is a hypothesis, not a bar.

| arm (DELTA = how much worse the arm ranks the CORRECT word than the intruder) | set 1 | set 2 | set 3 | set 4 |
|---|---|---|---|---|
| **CO-OCCURRENCE SURPRISAL** | **+2.00** | **+2.25** | **+2.00** | **+2.00** |
| FREQUENCY (flag the rarest) | +0.00 | +0.50 | +0.75 | +0.50 |
| LENGTH | +0.50 | +0.00 | +0.00 | +0.50 |
| ORTHOGRAPHIC | +0.00 | **-0.25** | +0.00 | +0.00 |
| POSITION | +0.00 | +0.00 | +0.00 | +0.00 |
| CONSTANT (query-blind) | +0.00 | +0.00 | +0.00 | +0.00 |

```
replication_verdict(...) -> REPLICATED
  same sign on 4/4 seeds, magnitude stable within 1.1x, no control reproduced half the effect
```

*Each set is 120 items built from a different builder seed, each with its own 120-sentence leak
exclusion. Scored in ALL-ITEMS mode -- the new sets have no hand-scores, and the WEAK items dilute
every arm equally, so a DELTA computed the same way on every set stays comparable across sets. **It
is NOT comparable to the hand-scored CLEAN-only headline and the two are never merged.***

## ✅ AND THE BUILDER IS BYTE-DETERMINISTIC

Rebuilding at the default seed reproduced the committed `v8` file with an **identical SHA-256**
(`8374a6ae...`). *So the set F5 will be judged on can be regenerated exactly, and a future
disagreement about the bar is settleable.*

## ⚠️ THE HONEST CAVEAT: **THE FREQUENCY MATCHING IS GOOD, NOT PERFECT**

FREQUENCY's delta averages **+0.44** across the four sets, not zero -- about **22% of the
co-occurrence effect**. `replication_gate` cleared it (no control reached half), but the margin on
set 3 was +0.75 against +2.00, which is **closer than the table's headline suggests.**

**So the bar is CO-OCCURRENCE SURPRISAL, not frequency**, and an F5 that beat only the frequency
floor would have beaten almost nothing. *Reported here because the earlier note's "the matching
worked" is true and could be read as "the frequency confound is gone". It is reduced, not gone.*

## 🎯 THE BAR, NOW REPLICATED

> **F5 must beat co-occurrence surprisal's median rank ~4.0 of ~9 candidates on frequency-matched
> items -- gated on that floor's UPPER bound -- with `replication_gate.py` returning `REPLICATED`
> across >=3 sets, and the ~86% item ceiling stated beside the score.**

## TLDR

The number the new component has to beat was measured on one batch of test sentences. Since four
different claims got withdrawn this week for resting on a single sample, I rebuilt the test set
three more times from scratch and re-measured.

**It came out at +2.00, +2.25, +2.00, +2.00** — about as stable as a measurement gets, and the
formal check agrees. The cheap tricks stayed at roughly zero on every rebuild.

One honest correction to the earlier write-up: I said the frequency matching worked, and it does,
but it isn't perfect — "flag the rarest word" retains about a fifth of the real effect. So the target
to beat is **word counting**, not rarity; beating rarity alone would mean almost nothing.

Also confirmed: rebuilding the set produces a byte-for-byte identical file, so the exact test can be
regenerated later and any disagreement about the bar can be settled.

## QUESTIONS

None.

## NEXT STEPS

1. **NEXT ANGLE A:** the 11 unexamined Tier-1 cells flagged by `read_what_the_cell_told_you.py`.
2. **NEXT ANGLE B:** `notes/STATUS.md` is far over its size cap and is the compaction-recovery entry
   point -- trimming it protects every future session.
3. F5 itself remains cell-authoring work and is not started.
