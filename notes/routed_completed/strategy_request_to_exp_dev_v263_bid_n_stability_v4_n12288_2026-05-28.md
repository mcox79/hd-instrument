# Strategy request to exp_dev: bid_n_stability_v4 envelope-extension re-run

**Filed:** 2026-05-28 by verdict_handler at v262 -> v263
**Parent:** bid_n_stability_v3_n16384 (v263 TIMEOUT @ 4500s, zero production metrics)
**Grandparent:** bid_n_stability_v2 (v255 MIDDLE_BAND HONEST, N=4096+8192 3-seed, +54%/N-doubling rate)
**Cap_map row affected:** substrate-outside-static-Hopfield scaling-law sub-axis (v255 LIFT to 55-68% STANDS UNCHANGED)

## TASK

Re-attempt the v255 v2 -> v3 envelope-extension at higher N for the BID scaling-law characterization. The v3 N=16384 attempt TIMED OUT at 4500s with zero production metrics. Choose between the rescue paths below per cheapest-first sequencing.

## WHY

v255 established `BID(N=4096) ~65 -> BID(N=8192) ~100` = +54% per-N-doubling, all cells outside Hopfield-class bands. This is the load-bearing evidence for the v255 LIFT to substrate-outside-static-Hopfield-taxonomy 55-68%. The v3 N=16384 cell was scheduled to confirm whether the scaling-law continues (BID ~154 expected, would be HARD_PASS) OR shows asymptote/regime-change at N=8192->16384 (would weaken the LIFT). v3 produced NO DATA either direction; the LIFT row STANDS at its v255 state.

The motivation for re-attempting is DEFENSE-IN-DEPTH, not load-bearing rescue. Per [[feedback-substrate-value-framing-2026-05-26]] "weight product-engineering work HIGHER than additional theoretical confirmation" -- this is LOW-PRIORITY. Do not bump ahead of higher-priority queue items.

## CONTRACT

You decide rescue path; verdict_handler ranked them cheapest-first as:

- **PRIMARY rescue (b) -- bid_n_stability_v4_n12288**: intermediate-N substitute. Tests scaling-law at N=12288 instead of N=16384. Expected wall ~2.25x v2's per-N=8192-cell baseline (~700s) = ~1600s for N=12288 + ~700s control N=8192 = ~2300s + 1.5x safety = 3450s. Fits well under any reasonable timeout. PASS condition: BID(N=12288) ~ 130 +/- some uncertainty corridor (geometric interpolation between BID(N=8192)~100 and the +54%/doubling rate, i.e. BID(N=12288) approx 100 * (12288/8192)^log2(1.54) = 100 * 1.5^0.62 = ~128).

- **ALT rescue (c) -- bid_n_stability_v4_n16384_extended_timeout**: same envelope as v3 but with timeout_s>=7200 per corrected per-cell extrapolation (v2's 1115s was for N=4096+8192 COMBINED; per-N=8192 cell only ~700s; so N=16384 alone = 4 * 700s = 2800s + N=8192 control 700s = 3500s + 1.5x safety = 5250s). Direct asymptote-test.

- **ALT rescue (d) -- bid_n_stability_v4_n16384_2seed**: drop seed count 3 -> 2 to fit 4500s envelope. Compromise.

- **ALT rescue (e) -- split per-N jobs**: highest robustness, most queue traffic.

You may also propose a NEW rescue path verdict_handler did not consider.

## AUTONOMY

- You decide WHICH rescue path (a)-(e) or your own alternate to ship.
- You decide pre-reg formula self-tests per [[feedback-strategy-spec-formula-selftests]] (closed-form formulas must have input -> expected-output pairs verified at design time).
- You decide the explicit `--timeout` flag per [[feedback-per-experiment-timeout-required]]. CRITICAL: re-derive from v2's PER-N=8192-CELL baseline (~700s), NOT v2's TOTAL wall (1115s); the v3 pre-reg conflated these and under-budgeted by ~15%.
- You decide queue (remote_cpu_queue recommended; this is a TwoNN no-CUDA workload at M ~ 2048 pairwise distance = ~17MB memory; CPU FLOPs are the binding constraint).
- You decide PROT-018 N-suffix per BINDING contract (`_n12288` for rescue (b), `_n16384` for rescues (c)/(d)/(e)).
- You may DEFER this rescue if higher-priority work is pending and substrate-product framing does not require N=16384 confirmation in the next session.

## HARD-PASS / HARD-FAIL / MIDDLE_BAND (rescue (b) example -- adjust if you pick a different rescue)

- **HARD_PASS** for rescue (b): BID(N=12288) in [110, 150] AND outside all Hopfield-class bands (>= band_outside threshold). Interpretation: scaling-law continues smoothly through intermediate N.
- **HARD_FAIL** for rescue (b): BID(N=12288) INSIDE any Hopfield-class band (would refute v255 LIFT). 
- **MIDDLE_BAND** for rescue (b): BID(N=12288) outside bands BUT outside [110, 150] interpolation corridor (suggests regime change at intermediate N; would weaken but not refute LIFT).

For rescue (c) use the v3 script's existing pre-reg bands at N=16384.

## NOT IN SCOPE

- Do NOT design new BID variants (e.g. BID with different alpha or M_frac). This is envelope-extension only.
- Do NOT pre-commit cap_map state in the script header. Verdict_handler will assess the result independently.
- Do NOT pad the queue. If rescue (b) fits in remote_cpu_queue with available slot, ship ONE; else file and DEFER.

## PROTs to verify

- PROT-018: anchor name MUST contain `_n<N>` suffix matching production N (binding contract).
- [[feedback-per-experiment-timeout-required]]: `--timeout` MUST be explicit at queue_add time; formula derived from PER-CELL baseline not TOTAL wall.
- [[feedback-strategy-spec-formula-selftests]]: pre-reg formula self-tests MUST verify input -> expected-output for the wall-cost extrapolation.
- [[feedback-no-padding-experiments]]: this is LOW-priority defense-in-depth; ship only if it fits in existing queue rhythm.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
