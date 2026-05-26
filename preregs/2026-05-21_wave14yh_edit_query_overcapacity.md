# Pre-registration: wave14yh_edit_query_overcapacity

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yh_edit_query_overcapacity.py](../experiments/exp_wave14yh_edit_query_overcapacity.py)
Priority source: extends [wave14yb_edit_then_query_kerdock](../experiments/exp_wave14yb_edit_then_query_kerdock.py)
to over-capacity regime where Bet 2 v2 validated Kerdock holds
Author: experiment_dev session, pipeline tick 18

## Why

yb tested edit-then-query at M=N=4096 (within v1 envelope) and got
EDIT_QUERY_BOTH_PASS. The interesting product question is: does the
edit pipeline hold at M > N (over-capacity, where structure matters)?
Bet 2 v2 showed Kerdock multi-probe holds at M=2N. yh tests if EDIT
operations also hold at M=2N — does Bet 2's structured-key envelope
translate to the full edit pipeline?

## Hypothesis

At N=4096, M=2N=8192 Kerdock keys (from 4-coset MM codebook), 30 edits,
5 seeds: Kerdock arm passes all 5 edit-then-query criteria; correlated
arm fails (as it did in Bet 2 v2 multi-probe).

## Multi-probe success criteria (same as yb)

1. edit_argmax_acc ≥ 0.95
2. kept_argmax_acc ≥ 0.95
3. edit_paraphrase_acc_h8 ≥ 0.90
4. kept_paraphrase_acc_h8 ≥ 0.95
5. side_effect_rate ≤ 0.05

## Verdict labels

- `EDIT_QUERY_OC_KERDOCK_PASS` — Kerdock passes at M=2N
- `EDIT_QUERY_OC_BOTH_PASS` — both arms pass at M=2N
- `EDIT_QUERY_OC_KERDOCK_FAILS` — Kerdock arm fails (regression vs v2)
- `EDIT_QUERY_OC_KERDOCK_PARAPHRASE_FAIL`
- `EDIT_QUERY_OC_INCONCLUSIVE`

## Pre-mortem

1. At M=2N, the substrate is 2x over-capacity; insert step in edit
   operation must still work. yb's insert was at M=N (well-conditioned);
   at M=2N, W has rank ≤ N=4096 storing 8192 (v,k) pairs. Insert
   updates W += outer(v_new, k_i)/N — math is the same; whether
   reads return v_new depends on cross-talk being controlled.
2. Paraphrase + snap: at 2N codewords, snap still maps to nearest codeword.
3. Side effects: with 8192 facts, 100 kept-probe sample may not be representative.

## Operational definition

Reuses yb pipeline. Differences:
- M_stored = 2N = 8192 (vs yb's N=4096)
- Kerdock codebook: 4-coset MM (4N codewords), sample 2N from it
- Other parameters same

## Expected runtime

- Smoke (N=1024, M=2N=2048, 5 edits, 1 seed): ~5-10 s
- Full (N=4096, M=8192, 30 edits, 5 seeds, 3 hamming, 2 arms): ~3-5 min
