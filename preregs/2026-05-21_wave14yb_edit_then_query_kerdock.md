# Pre-registration: wave14yb_edit_then_query_kerdock

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14yb_edit_then_query_kerdock.py](../experiments/exp_wave14yb_edit_then_query_kerdock.py)
Priority source: end-to-end test of cap_map Tier-1 KILLER "Edit-then-query
for fact correction" (currently UNSURE — "can edit, but full pipeline
integration untested"). Composes Bet 2 v3's validated Kerdock erase
primitive with an insert step.
Author: experiment_dev session, pipeline tick 13

## Why

Bet 2 work (v1, v2, v3, v4) validated the **erase** primitive on Kerdock-
keyed substrates — multi-probe Mirage protection holds through M=4N
(and v4 will tell us about 8N). But "GDPR-grade erase" alone is not the
product capability; the product is **edit-then-query**:

1. Store fact (subj, rel, obj)
2. Later: edit the fact to (subj, rel, obj_new) — erase old + insert new
3. Query (subj, rel) → should return obj_new

The cap_map records this as Tier-1 KILLER with current status "can edit
(Bet 2 validated), but full pipeline integration untested." A prior test
`wave14d_query_side_integration` showed 93% W-leak with **random** keys —
i.e., edits didn't stick. With Kerdock keys (which v2/v3/v4 showed break
Mirage), the prediction is that the leak goes away and edit-then-query
works.

## Hypothesis

At N=4096, M_stored=N=4096 (well within v1 envelope), Kerdock 4-coset
codebook (same as v3), 5 seeds, edit 30 of M=4096 facts:

- Edited-fact retrieval accuracy: argmax returns v_new with rate ≥ 0.95
- Kept-fact retrieval accuracy: argmax returns v_orig with rate ≥ 0.95
- Paraphrase robustness (Hamming h=8 perturbation + snap): edited-paraphrase
  retrieval ≥ 0.90, kept-paraphrase ≥ 0.95
- Side-effect rate: ≤ 5% of edited facts cause a measurable shift in any
  kept fact's retrieval

If yes: edit-then-query works end-to-end with Kerdock keys; cap_map row
moves from UNSURE to ✅.

## Multi-probe success criteria (all required for PASS)

1. edit_argmax_acc ≥ 0.95
2. kept_argmax_acc ≥ 0.95
3. edit_paraphrase_acc (h=8 with snap) ≥ 0.90
4. kept_paraphrase_acc (h=8 with snap) ≥ 0.95
5. side_effect_rate ≤ 0.05

Compare to a **random-keys control arm** running the same edit-then-query
pipeline. The contrast should be sharp: random keys should reproduce the
wave14d_query_side_integration 93% W-leak finding while Kerdock breaks
it.

## Kill criterion

Both arms fail edit_argmax_acc < 0.95: edit-then-query doesn't work at
all in this regime; mechanism investigation needed (not just key
structure).

## Verdict labels (6)

- `EDIT_QUERY_KERDOCK_PASS` — Kerdock arm passes all 5; random arm fails
  at edit_argmax (replicates wave14d_query_side_integration leak)
- `EDIT_QUERY_BOTH_PASS` — both arms pass (surprising; would mean the leak
  doesn't exist at this M; audit)
- `EDIT_QUERY_KERDOCK_PARAPHRASE_FAIL` — Kerdock passes edits + kept but
  paraphrase under snap fails
- `EDIT_QUERY_KERDOCK_SIDE_EFFECTS` — Kerdock passes 4 criteria but
  side_effect_rate > 0.05
- `EDIT_QUERY_BOTH_BROKEN` — kill criterion; mechanism issue
- `EDIT_QUERY_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. Codebook construction: Welch bound preserved (reuse v3 oracle)
2. Pre-edit retrieval: on the unedited substrate, all stored facts should
   retrieve cleanly (argmax_acc ≥ 0.95 at smoke scale, sanity check)
3. Edit op modifies W: after edit, W is measurably different from pre-edit W

## Pre-mortem (3 failure causes)

1. **Insert step is not "clean"**: anti-Hebbian erase removes (v_old, k)
   but the substrate still has memory of v_old via cross-talk with other
   facts. When we insert (v_new, k), the W*k probe should give v_new (since
   erase zeroed W*k). But what about kept facts: W*k_j for j ≠ i? The
   insert step adds v_new * <k_i, k_j>/N to each kept read. For Kerdock
   pairs |IP|/N ≤ 1/64; for random keys, the typical 1/sqrt(N) ~ 0.016
   plus tails. The KEPT side has the same cross-talk issue as the Bet 2
   erase tests. Verdict captures via kept_argmax_acc.

2. **Snap-to-codebook on paraphrase confuses edited vs kept**: paraphrase
   of k_i (Hamming-perturbed) snaps back to k_i for h ≤ N/3 (by Welch-
   bound logic). Then probe = v_after[i] + noise. argmax should still
   return v_after[i]. But if snap fails (h > N/3), behavior is undefined.
   Mitigation: use h=8 (well below N/3 = 1365).

3. **Side effect detection is noisy**: with 30 edits and 100 kept-probe
   facts, expected accidental shifts due to noise are ~5-10. Setting
   threshold at 5% with M=100 means tolerating 5 spurious shifts. Real
   side effects from edits should be ~0 with Kerdock; with random keys
   should be ~1-3 per edit. Verdict criterion should be clear.

## Operational definition

- N = 4096
- M_stored = N = 4096 (within v1's validated envelope to keep the test
  about edit-then-query specifically, not capacity)
- Kerdock arm: 4-coset MM codebook from v3 (sample 4096 from 4*4096=16384)
- Correlated control: same `make_correlated_keys` with rank_L = M/4
- 30 facts edited (anti-Hebbian erase + insert new bipolar value)
- 100 kept facts probed for retention
- 5 seeds
- α = 1.0 (validated)
- Paraphrase Hamming h ∈ {4, 8, 16}, snap-to-codebook in Kerdock arm

Edit operation per fact i:
```
W = W - alpha * outer(W @ k_i, k_i) / (k_i @ k_i)   # erase
W = W + outer(v_new_i, k_i) / N                       # insert
```

Equivalent collapsed update:
```
delta_v = v_new_i - alpha * W @ k_i / (k_i @ k_i) * (k_i @ k_i) / N
       =  v_new_i - alpha * W @ k_i / N    (if alpha=1, just W @ k_i shifted)
```

(Computing the two steps separately is clearer and slightly more numerically
stable; using that form.)

## Cited mechanism / sources

- Bet 2 v1/v2/v3/v4 (own work): erase primitive validated
- ROME/MEMIT (arXiv:2202.05262, 2210.07229): the original edit primitives
- wave14d_query_side_integration (own work, prior): 93% leak with random keys
- v3.make_kerdock_4coset_codebook: codebook construction

## Expected runtime

- Smoke (N=1024, M=1024, 5 facts edited, 1 seed, 1 hamming): ~5 s
- Full (N=4096, M=4096, 30 edits, 5 seeds, 3 hamming, 2 arms): estimated
  2-4 min on GPU

## What product decision this enables

- `EDIT_QUERY_KERDOCK_PASS` → cap_map "edit-then-query" row moves
  UNSURE → ✅. Strong product story: "structured keys make GDPR-grade
  edit pipeline work."
- `EDIT_QUERY_BOTH_PASS` → wave14d_query_side_integration's 93% leak
  doesn't reproduce here; audit setup divergence.
- `KERDOCK_PARAPHRASE_FAIL` / `KERDOCK_SIDE_EFFECTS` → edit-then-query
  partially works; cap_map row gets caveats.
- `BOTH_BROKEN` → mechanism issue beyond key structure; routes to
  mechanism investigation.
