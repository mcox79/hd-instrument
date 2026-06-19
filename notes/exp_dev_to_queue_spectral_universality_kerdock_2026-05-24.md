# exp_dev -> queue: wave14_spectral_universality_kerdock_v1 — 2026-05-24

**Anchor** for Cap 8 envelope-extension to M/N=8 via Dudeja-Sen-Lu spectral universality (arXiv:2208.02753, IEEE TIT 2023). Replaces the previously-proposed MAMP-SE anchor; Research's pure-math drill (`notes/research_mamp_kerdock_M_over_N_8_drill_2026-05-24.md`) showed MAMP gives the same SE fixed point as VAMP under RUI (Liu-Takeuchi Thm 2), so the MAMP anchor can't resolve the M/N=8 gap. Dudeja-Sen-Lu's structured-deterministic class is the right framework.

**Routing**: `remote_cpu_queue` (Tier B). Research's anchor proposal said local CPU; pre-ship heartbeat check confirmed `local_cpu_runner` status=exited (last beat 2026-05-24T01:50). Tier B is acceptable per `[[feedback-laptop-cpu-quick-probes]]` for 45-60 min jobs.

**Smoke**: PASSED on local desktop. `python experiments/exp_wave14_spectral_universality_kerdock_v1.py --smoke` (~30s wallclock) — all 5 verdict-logic self-tests pass, all 4 surrogate-spectrum self-tests pass (iid Gaussian sigma in MP range, random-sign Hadamard sigma==1 within 1e-10 for square + sub-square cases, Haar-with-target-spectrum reconstructs target sigma within 1e-6). Smoke run at N=1024 M/N in {0.5, 1.0} 1 seed iid_gaussian-only produces Kerdock-vs-iid MSE within 1-20% → verdict KERDOCK_UNIVERSALITY_IN_CLASS, consistent with prereg's HARD PASS band at small M/N. Metrics.json written.

**Hypothesis**: Kerdock-W is in Dudeja-Sen-Lu's universality class across all 5 M/N cells; matches at least one of {iid_gaussian, random_sign_hadamard, haar_kerdock_spectrum} within ±25%. P(HARD PASS) ≈ 0.30; P(MIDDLE BAND novel non-universality at M/N>=4) ≈ 0.30; remainder INCONCLUSIVE.

**Decision bands** (full prereg `preregs/2026-05-24_wave14_spectral_universality_kerdock_v1.md`):
- HARD PASS (`KERDOCK_UNIVERSALITY_IN_CLASS`): Cap 8 ✅ envelope extends to M/N=8.
- HARD FAIL (`KERDOCK_UNIVERSALITY_TEST_INCONCLUSIVE` via surrogate-disagreement): test uninformative; surrogate construction needs debugging.
- MIDDLE BAND (`KERDOCK_UNIVERSALITY_NOVEL_OUT_OF_CLASS`): substrate-novel non-universality finding; Cap 12 promotes to "Kerdock breaks Dudeja-Sen-Lu universality" annotation.

| queue            | name                                       | script                                                          | prereg                                                              | timeout(s) |
|------------------|--------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_spectral_universality_kerdock_v1    | experiments/exp_wave14_spectral_universality_kerdock_v1.py      | preregs/2026-05-24_wave14_spectral_universality_kerdock_v1.md       | 5400       |
