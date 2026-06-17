# exp_dev hand-off -- research: Drosophila MB sparse recapture (3 architecture forks)

Filed: 2026-06-17 by research sub-agent.

Trigger: Research delivery `notes/research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md` -- 3-angle lit-scan converged on a single mechanism (sparse-coding capacity gain requires supra-linear selection step that the substrate's linear heteroassociative readout does not have). Three named architecture forks identified; ARCH-A is the cheapest decisive test and the only one that preserves the substrate's linear-readout product positioning.

Pause state: check `data/orchestrator_paused.flag` at dispatch time; if paused, exp_dev defers per pause-gate policy.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile, encoding-detail choices (TopK vs L0 vs block-sparse), readout temperature schedule.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) -- ARCH-A SPARSE-KEY DENSE-VALUE PROBE

- Anchor pointer: `notes/research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md` sec (b) ARCH-A + sec (c) HARD-PASS/HARD-FAIL bands.
- Substrate-product reading: sparse-key dense-value is the only fork that preserves the linear-readout architecture. If HARD-PASS, opens a controlled-sparsity routing layer for KEY-SPACE COLLISION CONTROL at high load without losing the dense-bipolar bundle math. If HARD-FAIL, structurally closes the "MB sparse coding recapture in linear heteroassociative substrate" cap_map row at the bipolar-value end.
- Tier hint: likely Tier A or B (small-N, single-config sweep of f_k across {0.05, 0.10, 0.20, 0.50} at fixed N=1024; cell cost SUPER-FAST per laptop policy).
- Why now: cheapest fork; preserves the linear-readout investment; resolves the substrate-internal question of whether sparse coding pays at all without nonlinear readout. Lit precedent is the Olshausen / K-SVD / SAE / sparse-VSA template (Laiho 2015, Hersche 2023) -- well-established but UNVERIFIED for substrate's specific BSC bipolar regime.
- P_deflated = 0.35 (novel-synthesis cap applied; sparse-VSA literature mixed for the specific bundle-readout configuration).

### Anchor 2 (CONDITIONAL on Anchor 1 HARD-FAIL) -- ARCH-B SOFTMAX READOUT

- Anchor pointer: same research note sec (b) ARCH-B + sec (c) HARD-PASS/HARD-FAIL bands.
- Substrate-product reading: drop-in Modern-Hopfield-class readout replacement. Bigger product lift (exponential capacity precedent per Ramsauer 2020) but requires re-tooling all argmax-cosine consumers. Defer behind ARCH-A unless ARCH-A HARD-FAILs.
- Tier hint: Tier B (small-N + single-config; readout swap is a few lines; capacity sweep across M = N, 2N, 4N).
- Why now: only if ARCH-A closes. The substrate already wins at linear-bipolar baseline; ARCH-B is the next-leverage option if the sparse-encode-side fork structurally fails.
- P_deflated = 0.45.

### Anchor 3 (LONG-TAIL) -- ARCH-C WILLSHAW-CLIP

- Anchor pointer: same research note sec (b) ARCH-C + sec (c) HARD-PASS/HARD-FAIL bands.
- Substrate-product reading: parallel substrate (clipped-binary W, thresholded readout); not an extension of the bipolar-linear regime. File as long-tail option, NOT near-term lane unless USER explicitly directs.
- Tier hint: Tier B or C.
- Why now: low priority; only if BOTH ARCH-A and ARCH-B HARD-FAIL and cap_map row needs a structural-rescue probe in a parallel substrate.
- P_deflated = 0.50 (novel-synthesis cap).

---

## Context pointers (pointers, not summaries)

- `notes/research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md` -- THIS research delivery; 3-angle lit-scan + 3 architecture forks + falsifiable predictions.
- `notes/substrate_capability_map.md` -- find the Drosophila MB sparse-recapture row; this delivery proposes METHOD-CONTINGENT bump with three named forks.
- `hdlab/` -- substrate code; ARCH-A is a key-encoding swap (TopK or L0 sparse over bipolar +/- 1) with W = sum val key^T preserved.
- `verification/` -- scaffold-free witness convention per `CLAUDE.md`; any ARCH-A experiment ships with a verification test.

---

## Contract

- exp_dev designs and ships at most ONE anchor per cycle unless pause-gate policy says otherwise.
- Pre-reg per envelope-fail-bands; smoke gate; ship via queue_add.sh; post-ship REMOTE VERIFY; self-test per formula-selftests.
- USER compute policy: super-fast (no large NxN matrix) -> laptop OK; heavy -> remote desktop. ARCH-A at N=1024 fits laptop super-fast bucket.

## Autonomy declaration

exp_dev decides:
- Which anchor to ship first (Anchor 1 unless cap_map state has shifted since this hand-off was filed).
- Sparse-key encoding detail (TopK with hard k vs L0 with soft threshold vs block-sparse with block size).
- Value-side encoding (dense bipolar +/- 1 baseline RECOMMENDED to isolate the sparse-key variable).
- M sweep range, seed count, smoke profile size, FULL profile size.
- Whether to bundle ARCH-A + ARCH-B in a single anchor (paired smoke) or ship as two cycles.
- HARD-PASS / HARD-FAIL bands MAY be tightened beyond the research note's defaults if pre-reg discipline benefits.

If exp_dev sees a reason to deprioritize Anchor 1 or restructure, exp_dev files the reasoning in its anchor pre-reg note. Research does NOT pre-design the experiment.

---

Status log entry will be filed by research at delivery time.
