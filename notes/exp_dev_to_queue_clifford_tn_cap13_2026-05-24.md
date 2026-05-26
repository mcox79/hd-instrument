# exp_dev → queue — Clifford-TN Kerdock Magic-Bound Cap 13 candidate (Sub-anchors A + B) — 2026-05-24

Per orchestrator invocation: ship the F-4 Clifford-enhanced tensor networks Cap-13 candidate from `notes/research_new_continents_deep_drill_2026-05-24.md` Section 3. Two-anchor split: CPU theory anchor (small-N closed-form vs v169 baseline) + GPU sanity at substrate-native N=4096.

User-flagged: "GPU is idle." Sub-anchor B ships to overnight_queue to fill GPU pipeline (production-scale eigvalsh on 16384x16384 Gram).

Pause flag CLEARED at dispatch.

Upstream dependencies verified:
  - Cap 8 v169 Schur-Weyl-Pauli-twirled annotation (cap_map row exists at v180; v169 schur-weyl-irrep-masses function in `exp_wave14_cap12_cap8_audit_trail_pipeline_v1.py`).
  - Barnes-Wall Z_4-linear envelope theorem (Calderbank-Hammons-Kumar-Sloane-Sole 1997, public theorem, no internal dependency).
  - Substrate's existing Kerdock construction (`make_kerdock_2coset_codebook` at any N=2^k; `make_kerdock_4coset_codebook` at N in {1024, 4096, 16384}).

| queue            | name                                              | script                                                                 | prereg                                                                | timeout(s) |
|------------------|---------------------------------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_clifford_tn_kerdock_magic_bound_v1         | experiments/exp_wave14_clifford_tn_kerdock_magic_bound_v1.py           | preregs/2026-05-24_wave14_clifford_tn_kerdock_magic_bound_v1.md       | 43200      |
| overnight_queue  | wave14_clifford_tn_kerdock_n4096_sanity_v1        | experiments/exp_wave14_clifford_tn_kerdock_n4096_sanity_v1.py          | preregs/2026-05-24_wave14_clifford_tn_kerdock_n4096_sanity_v1.md      | 5400       |

## Sub-anchor A — wave14_clifford_tn_kerdock_magic_bound_v1 (CPU theory, remote_cpu_queue)

Tests Cap 13 candidate "Clifford-TN bond-dim-1 audit + Barnes-Wall magic monotone" against v169's O(N^3) Schur-Weyl-Pauli-twirled Cap 8 derivation. The bond-dim-1 closed form (Lami-Haug-De Nardis 2025) predicts that for the 2-coset Kerdock codebook (M=2N), the spectral measure is a uniform delta at lambda=1.0 and the Barnes-Wall magic monotone (Kalra-Sinha 2025) is exactly 0.

Sweeps N in {16, 64, 256, 1024} × 5 seeds × n orders {2, 3, 4, 5}. For each (N, seed, n) cell: compute v169 mass_n from eigvalsh of (1/N) A A^T; compute closed-form mass_n from p_k=1; compute rel_err. Compute Barnes-Wall magic monotone for each codeword.

HARD PASS: rel_err < 1e-10 at every cell AND BW magic = 0 everywhere AND TN wallclock scales as O(N log N).
HARD FAIL: rel_err > 0.10 anywhere OR magic > 0.01 anywhere.
MIDDLE BAND: rel_err in (1e-10, 0.05] or magic in (1e-10, 0.01].

ETA: 6-12 hr CPU.

## Sub-anchor B — wave14_clifford_tn_kerdock_n4096_sanity_v1 (GPU, overnight_queue)

Production-scale sanity at substrate-native N=4096 with full 4-coset MM Kerdock (16384 codewords). The bond-dim-1 closed form for 4-coset is a 2-point spectral measure at {0, M/N=4} with masses (3/4, 1/4) and power sums p_k = 4^(k-1).

Sweeps 5 seeds × 5 codeword indices × 4 n orders. For each cell: GPU-accelerated eigvalsh on 16384x16384 Gram; Schur-Weyl mass_n via v169 formula; compare to closed-form prediction.

HARD PASS: rel_err < 0.01 at every cell AND eig_dev_from_2point < 0.20 AND magic < 1e-10.
HARD FAIL: rel_err > 0.10 OR eig_dev_2pt > 2.0 OR magic > 0.01.
MIDDLE BAND: rel_err in (0.01, 0.05] OR eig_dev_2pt in (0.20, 0.80] OR magic in (1e-10, 0.01].

ETA: 30-60 min GPU.

## Smoke results

- **Sub-anchor A** (N=16 / 1 seed / 1 n-order): self-tests 6/6 PASS; experiment VERDICT=HARD_PASS_CLIFFORD_TN_LICENSED with rel_err=0.0, BW magic=0.0. The Kerdock 2-coset Gram eigenvalues at N=16 are exactly uniform (= 1.0 each), v169 reproduces this, and the closed form matches to floating-point precision.
- **Sub-anchor B** (N=1024 / 1 seed / 1 codeword): self-tests 5/5 PASS; experiment VERDICT=HARD_PASS_CLIFFORD_TN_N4096_LICENSED with rel_err=0.0, eig_dev_from_2point=1.0e-4, BW magic=0.0. The 4-coset Gram spectrum at N=1024 is a clean 2-point delta at {0, M/N=4}.
- **Barnes-Wall self-test** (per [[feedback-strategy-spec-formula-selftests]] requirement): BW norm = N for |0>^N stabilizer state at N in {4, 8, 16, 64}; magic = 0. BW norm = N for 2-coset Kerdock codewords at N=8 (all 16 rows); magic = 0. Verified against the Calderbank-Sloane Barnes-Wall minimum-shell-norm theorem.

## Post-ship verification

(Will be filled by `queue_add.sh` post-ship verification step; expected: `[queue-add] VERIFIED: <name> present in remote <queue>/queue.json`.)

## Notes

- Both anchors are Cap 13 candidates per Research deep-drill Section 5: P_deflated=0.50 with novel-synthesis cap; "GENUINE Cap 13 but with the highest risk of being 're-LANGUAGING'" per Section 5 honest assessment.
- The bond-dim-1 closed-form IS the canonical "re-LANGUAGING" risk: it tells us substrate's Cap 8 is structurally a stabilizer-tensor-network contraction, which we already knew. The NET-NEW capability is the Barnes-Wall magic monotone = 0 audit cert (Kalra-Sinha 2025); the v169 reduction is an envelope-extension on Cap 8.
- The Hopfield-cleanup caveat from Research Section 5: this anchor tests the READOUT CODEBOOK, not the iterated-argmax with cleanup. If full Cap 8 pipeline output has nonzero BW magic, that is a FOLLOW-UP anchor — NOT a HARD_FAIL of THIS anchor.
- Remote TN libraries: stim 1.16.0 IS available on remote (verified via probe); quimb/tenpy/qiskit absent. This anchor's experiments do NOT require those libraries — pure numpy/torch on the codebook Gram matrix and the Frobenius character formula. No blockers.
- Queue depth check: GPU queue had 5 pending pre-ship; remote_cpu_queue had 0 pending — Sub-anchor A directly fills the remote-CPU pipeline. GPU underutilization was less acute than user flagged (5 pending already), but Sub-anchor B still adds a production-scale Cap 13 audit to overnight.
