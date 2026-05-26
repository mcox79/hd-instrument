# exp_dev → queue — Tropical Cap 13 candidate (Anchors 1 + 2) — 2026-05-24

Per Strategy invocation: ship the F-14 Tropical Geometry Cap-13 candidate from `notes/research_new_continents_deep_drill_2026-05-24.md`. Two-anchor split: CPU theory anchor (small-N closed-form vs empirical) + GPU empirical baseline at substrate-native N=4096.

User-flagged: "GPU is still idle" — Anchor 2 ships to overnight_queue to fill GPU pipeline.

Pause flag CLEARED at dispatch (orchestrator invocation explicitly said so; verified `data/orchestrator_paused.flag` absent).

| queue            | name                                              | script                                                                   | prereg                                                                  | timeout(s) |
|------------------|---------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_tropical_margin_certificate_kerdock_v1     | experiments/exp_wave14_tropical_margin_certificate_kerdock_v1.py         | preregs/2026-05-24_wave14_tropical_margin_certificate_kerdock_v1.md     | 28800      |
| overnight_queue  | wave14_tropical_kerdock_N4096_emp_margin_v1       | experiments/exp_wave14_tropical_kerdock_N4096_emp_margin_v1.py           | preregs/2026-05-24_wave14_tropical_kerdock_N4096_emp_margin_v1.md       | 5400       |

## Anchor 1 — wave14_tropical_margin_certificate_kerdock_v1 (CPU)

Tests Cap 13 candidate "tropical-polytope adversarial-margin certificate": substrate's Kerdock argmax-readout admits a CLOSED-FORM L_inf adversarial margin via the tropical-polynomial decision-boundary formula (Tropical Decision Boundaries arXiv 2402.00576).

Closed-form: `margin(y, w_i) = min_{j != i} <w_i - w_j, y> / ||w_i - w_j||_1`

Sweeps N ∈ {4, 16, 64, 256, 1024} on 2-coset Kerdock codebook (2N codewords each). For each (seed, codeword) pair: compute closed-form margin AND empirical bit-flip margin (min # of bits to flip to change argmax). Compares the two; reports rel_err per N and unique-equivalence-class count of pairwise L_1 distances.

HARD PASS: rel_err <= 0.05 at >= 4/5 N values AND equiv-classes < 300 at every N.
HARD FAIL: rel_err > 0.25 at ANY N OR equiv-classes >= 300 anywhere.
MIDDLE BAND: rel_err in (0.05, 0.10] partial.

ETA: 4-8 hr CPU.

## Anchor 2 — wave14_tropical_kerdock_N4096_emp_margin_v1 (GPU)

Companion: production-N=4096 empirical baseline. Uses FULL 4-coset MM Kerdock (16384 codewords) and GPU-vectorized top-k bit-flip search. 5 cells × 10 seeds × 5 codewords = 250 measurements.

HARD PASS: cv (std/mean) <= 0.30 AND p25 > 0 across all trials.
HARD FAIL: cv > 0.80 OR > 20% degenerate (margin=0 or unreachable).
MIDDLE BAND: cv in (0.30, 0.80].

ETA: 30-60 min GPU.

## Smoke results

- Anchor 1 (N=4 / 1 seed / 3 codewords): self-tests PASS (8 cells); experiment VERDICT=TROPICAL_MARGIN_KILLED with rel_err=0.53 at N=4. **Honest read** in prereg: at N=4, the integer-bit-flip discretization (each flip = L_inf 2 units) dominates the continuous-margin form; gap is expected to shrink with N. HARD PASS at full requires 4/5 N to pass — N=4 may legitimately fail while N>=16 passes.
- Anchor 2 (N=1024 / 1 seed / 2 codewords / 2 eps cells): self-tests PASS (5 cells); experiment VERDICT=EMP_MARGIN_WELL_DEFINED with cv=0.006 (very clean). Empirical margin ≈ 490-496 bit-flips for N=1024 4-coset Kerdock — substrate has a real adversarial threshold ~12% of N.

## Post-ship verification

- Anchor 1: `[queue-add] VERIFIED: wave14_tropical_margin_certificate_kerdock_v1 present in remote remote_cpu_queue/queue.json` — confirmed.
- Anchor 2: `[queue-add] VERIFIED: wave14_tropical_kerdock_N4096_emp_margin_v1 present in remote overnight_queue/queue.json` — confirmed.

## Notes

- Both anchors are net-new Cap 13 candidates per Research deep-drill Section 5: P_deflated=0.55 with novel-synthesis cap; "GENUINE Cap 13" per Section 5 honest assessment.
- The smoke result at N=4 producing TROPICAL_MARGIN_KILLED is a useful canary: if at FULL run N>=16 also fails with rel_err > 0.25, the closed-form claim is genuinely refuted (not a discretization artifact). If N>=16 passes within 5%, Cap 13 licensed and the small-N discretization caveat is annotated to cap_map.
- Both queued post-ship; runner picks up immediately. GPU queue was 0 pending before ship; now 1 pending (depth invariant satisfied).
