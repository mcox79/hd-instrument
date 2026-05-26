# Pre-registration: wave14yc_continual_editing_kerdock

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14yc_continual_editing_kerdock.py](../experiments/exp_wave14yc_continual_editing_kerdock.py)
Priority source: stress-test follow-up to
[wave14yb_edit_then_query_kerdock](../experiments/exp_wave14yb_edit_then_query_kerdock.py)
(EDIT_QUERY_BOTH_PASS); addresses cap_map Tier-1 KILLER "True continual
learning at production scale" (UNSURE)
Author: experiment_dev session, pipeline tick 14

## Why

wave14yb showed edit-then-query forward retrieval works *in one shot*:
edit 30 facts, query all, both Kerdock and correlated arms return v_new
at 100% accuracy. But the cap_map calls out "True continual learning at
production scale" as Tier-1 KILLER — currently UNSURE because we've only
tested single edit batches, not sequential editing under sustained load.

This experiment runs 30 *sequential* edits on the same substrate, querying
all facts after each edit, and reports the accuracy trajectory. Two arms
(Kerdock vs correlated) to match the comparison protocol used throughout
Bet 2. The interesting question: at what edit count (if any) does the
substrate degrade, and does Kerdock structure protect across sequential
edits the way it does for single ones?

## Hypothesis

At N=4096, M_stored=N=4096 (within v1 envelope), 30 sequential edits,
5 seeds:

- Kerdock arm: edited_acc and kept_acc both ≥ 0.95 throughout all 30 edits.
- Correlated arm: at least one of (edited_acc, kept_acc) drops below 0.95
  within the 30 edits — sequential drift accumulates and Kerdock's
  structure-protection becomes load-bearing.

The Bet 2 paraphrase Mirage failure mode (cross-talk via kept facts) was
shown for ONE erase. With sequential edits, each anti-Hebbian update
shifts W slightly via cross-talk; effects could accumulate. Kerdock's
bounded cross-talk (1/sqrt(N)) limits this accumulation; correlated keys
do not.

## Multi-probe success criteria (per arm)

After each edit i ∈ {1, ..., 30}:
- edited_acc[i]: fraction of EDITED facts so far whose query returns v_new
- kept_acc[i]: fraction of NEVER-EDITED facts whose query returns v_orig
- min_edited_acc = min_i(edited_acc[i]) over all edit steps
- min_kept_acc = min_i(kept_acc[i]) over all edit steps

PASS criterion per arm:
- min_edited_acc ≥ 0.95
- min_kept_acc ≥ 0.95

## Kill criterion

Both arms fail PASS by edit 10: continual editing is fundamentally broken
in this regime; mechanism issue beyond key structure.

## Verdict labels (6)

- `CONTINUAL_KERDOCK_HOLDS` — Kerdock PASS; correlated FAILS within 30
  edits. Strong product story: continual editing requires structured keys.
- `CONTINUAL_BOTH_HOLD` — Both PASS throughout. (Possible if 30 edits
  isn't enough load.)
- `CONTINUAL_KERDOCK_DRIFTS` — Kerdock starts to fail before correlated;
  unexpected.
- `CONTINUAL_BOTH_FAIL_FAST` — kill criterion; mechanism issue.
- `CONTINUAL_KERDOCK_EDITED_CLIFF_AT_<I>` / `CONTINUAL_KERDOCK_KEPT_CLIFF_AT_<I>`
  — Kerdock degrades after edit I; envelope characterized.
- `CONTINUAL_INCONCLUSIVE` — missing data.

## Oracle assertions (smoke mode)

1. Pre-edit query accuracy ≥ 0.95 on both arms (substrate stores facts
   correctly before any edits)
2. After first edit: edited_acc = 1.0 on Kerdock arm (single-edit case
   reproduces wave14yb result)

## Pre-mortem (3 failure causes)

1. **Probe cost scales with edit count**: at each edit step we query ALL
   M facts. For M=4096, that's 4096 cleanup operations per edit × 30 edits
   = 122880 ops × 2 arms = ~250K queries. Each is a matmul against value
   codebook of size M=4096. Total ~250K × 4096 × N = ~4 G ops × 2 arms.
   Should fit on GPU within a few minutes.

2. **Sequential edits compound numerical drift**: each anti-Hebbian +
   insert update modifies W. Small numerical errors could accumulate.
   Mitigation: use float32 (standard); track ||W_edit - W_pre||_F over
   edits as a sanity diagnostic.

3. **Edit operations land on previously-edited keys**: if we sample edit
   indices with replacement, an edit at step 15 might target a key that
   was already edited at step 5. The "old value" for that key is then
   v_new_5, not v_orig. This makes the verdict ambiguous. Mitigation:
   sample edit indices WITHOUT replacement (each fact edited at most once);
   that's how we get 30 distinct edits.

## Operational definition

- N = 4096
- M_stored = N = 4096
- Kerdock arm: 4-coset MM codebook (v3-validated); sample 4096 keys
- Correlated arm: rank_L = M/4 = 1024
- Sequential edit count = 30 (distinct facts; no replacement)
- 5 seeds
- α = 1.0
- After each edit, query ALL M facts (cleanup against current v_after
  codebook); compute edited_acc and kept_acc

Edit op (same as wave14yb):
```
W = W - alpha * outer(W @ k_i, k_i) / (k_i . k_i)
W = W + outer(v_new_i, k_i) / N
```

## Cited mechanism / sources

- wave14yb_edit_then_query_kerdock (own work): single-batch edit baseline
- Bet 2 v1-v4 (own work): Kerdock erase primitive validated
- cap_map "True continual learning at production scale" (UNSURE Tier-1)

## Expected runtime

- Smoke (N=1024, M=1024, 5 edits, 1 seed, both arms): ~5-10 s
- Full (N=4096, M=4096, 30 edits, 5 seeds, both arms): estimated
  2-5 min on GPU

## What product decision this enables

- `KERDOCK_HOLDS` → cap_map "continual learning at production scale"
  moves UNSURE → 🟢 (need stress tests at higher load before ✅);
  product story: "continual editing requires structured keys, lasts at
  least 30 edits."
- `BOTH_HOLD` → suggests 30 edits isn't enough load; stress-extend.
- `KERDOCK_DRIFTS` → Kerdock advantage doesn't carry to sequential
  edits; mechanism investigation.
- `BOTH_FAIL_FAST` → continual editing is fundamentally hard regardless
  of keys; substrate needs a different update rule.
