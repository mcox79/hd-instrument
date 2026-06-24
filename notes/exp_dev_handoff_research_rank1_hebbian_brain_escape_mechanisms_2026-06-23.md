# exp_dev hand-off — research: rank1_hebbian_brain_escape_mechanisms

**Filed by:** research:opus-4.7-1M
**Date:** 2026-06-23
**Trigger:** `notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` (2x DEEPER drill on brain mechanisms escaping rank-1 Hebbian cap)
**Pause state:** check `data/orchestrator_paused.flag` before any queue_add

Per [[feedback-no-experiment-design-in-prompts]] — anchor pointers below, NOT inline cell-design. exp_dev as autonomous cell-author owns design.

---

## Anchor candidates (rank-ordered for exp_dev refill)

### PRIMARY: `exp_substrate_kmodule_heterogeneous_compose_LM_v1`

- **Anchor pointer:** test multi-modular factorial-capacity escape from rank-1 Hebbian envelope
- **Substrate-product reading:** lifts +0.44 BPC envelope cap (currently SWEEP_HARD_FAIL) OR definitively closes substrate-as-LM lane
- **Tier hint:** Tier-1 (Levy-Horn-Ruppin 1997 N^M brain-canonical mechanism; substrate has K chain-grade primitives by-construction; no new infrastructure)
- **Why now:** the just-measured envelope cap is the algebraic ceiling for substrate's CURRENT homogeneous-flat architecture; the multi-modular hypothesis is the FIRST untested architectural-variable per substrate-mine inventory
- **Pre-reg HARD bands:** see parent research note section "CHEAP DECISIVE TEST" (HP at BPC <= 6.8; HF at BPC > 7.30)
- **Cost:** ~60-90min CPU local at N=8192, N_TRAIN=100k, 3 seeds, 4 arms + smoke at N=2048
- **Queue:** local_cpu_queue (no GPU needed; multi-module is parallel-by-construction)

### SECONDARY: `exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1`

- **Anchor pointer:** Ocker-Buice 2021 forward-only nonlinear-Hebbian recovers n-th tensor eigenvectors; substrate-native dense-Hopfield-equivalent without backprop
- **Substrate-product reading:** if forward-only can approximate Krotov dense at LM scale, substrate has a SECOND independent escape lever (composable with PRIMARY for n^M * n^M = N^(2M) joint capacity)
- **Tier hint:** Tier-1 (independent of PRIMARY; tests different lever — dense within-module vs multi-module factorial)
- **Why now:** parallel to PRIMARY; same substrate primitives; orthogonal hypothesis
- **Cost:** ~45min CPU local
- **Queue:** local_cpu_queue

### TERTIARY: AWAIT PRIMARY/SECONDARY verdict

Don't queue more anchors until PRIMARY's verdict. If PRIMARY MIDDLE_BAND, queue v2 (heavier compose). If PRIMARY HARD_PASS, queue Krotov-LM-scale + hierarchical-PC. If PRIMARY HARD_FAIL, queue substrate-as-composition-engine pivot cells (not LM-class).

---

## Context pointers (file paths, not summaries)

- `notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` — parent research note with full lit-scan synthesis + HARD bands + falsifiables + META atoms
- `data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json` — envelope cap measurement (+0.44 ceiling; what we're trying to break)
- `data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json` — homogeneous-compose READOUT_DEGENERATE (the failure mode predicted by Levy-Horn-Ruppin for in-module compose)
- `notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md` — 31-cell inventory confirming K-module HETEROGENEOUS compose is UNTESTED
- `notes/exp_dev_att1_v2_krotov_pre_reg_2026-06-23.md` — parallel Krotov drill at att1 scale (N=512); informs substrate-native HD Krotov implementation; SECONDARY cell should reuse those primitives
- `notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md` — prior 2x drill (Brzosko sequential trace); informs why homogeneous-compose fails and heterogeneous module-precision-weighted is the architectural answer

---

## Contract

- Per [[feedback-empowered-to-experiment-where-lit-says-dismissed]] — multi-modular compose at LM scale is unexplored in substrate; literature provides EXISTENCE PROOF (brain) not necessarily DIRECT-PATH PROOF; default DISPATCH applies
- Per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]] — let PRIMARY-vs-SECONDARY ordering emerge from smoke-data, not lit-prior; if smoke shows orthogonal lifts, queue both
- Per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms]] — calibration deflated 0.10-0.15 not 0.15-0.25; novel-synthesis cap relaxed to 0.55 for K-module compose
- Per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]] — verdict_msg MUST contain per-arm BPC + per-arm lift; not just aggregate; orchestrator will read metrics.json not verdict_msg
- Per [[feedback-foreground-vs-background-for-sequential-store-ledger-writes]] — Store+cert_ledger writes foreground if HARD_PASS lands

---

## Autonomy declaration

exp_dev decides ALL of:
- Exact arm definitions (PRIMARY's 4 arms + controls; SECONDARY's polynomial-order n grid)
- Smoke vs full cadence (recommend N=2048 N_TRAIN=10k smoke first)
- Pre-flight self-test design (must satisfy: zero-noise identity per arm, high-noise random per arm, REQUIRED_FIELDS, zero_llm_calls_at_inference gate)
- Whether to spawn PRIMARY + SECONDARY in parallel (recommended; orthogonal mechanisms)
- Whether to pre-stage CA3-attractor cleanup primitive for v2 if MIDDLE_BAND

Research does NOT pre-judge module-set, beta_k learning protocol, or refuse-gate threshold — those are cell-author design decisions per autonomy contract.

---

## Status log gating

Research has logged this drill via `tools/orchestrator/state.py log_event(kind='research_delivery', ...)` with `importance='HIGH'` and `plain_language` populated. exp_dev pickup is independent; queue-refill subject to `data/orchestrator_paused.flag`.
