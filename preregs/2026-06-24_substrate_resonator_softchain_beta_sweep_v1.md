# Pre-registration: substrate_resonator_softchain_beta_sweep_v1

**Date:** 2026-06-24
**Anchor:** substrate_resonator_softchain_beta_sweep_v1
**Queue:** local_cpu_queue
**Lane:** 1 (substrate-native, pure-numpy)
**N_DIM:** 8192 (FULL), 2048 (smoke); **Seeds:** [7, 17, 23]; **n_chains_2hop:** 200

## Scientific question

The 5-cell HARD_FAIL audit on 2026-06-24 (Skunkworks + Research synthesis) identified a smoking-gun wiring bug in both prior cells: `exp_substrate_resonator_multihop_integration_v1` and `exp_substrate_soft_chain_dfe_multihop_v1` both set Modern-Hopfield inverse-temperature `beta = N_DIM = 8192`. At that beta, `softmax(8192 * top_cosine)` is a Dirac delta concentrated at argmax; the "soft superposition" mathematically degenerates to hard winner-take-all, identical to the naive baseline.

**EMPIRICAL PROOF (the smoking gun).** Per-seed top1 values from the prior cells are bit-identical between `ARM_RESONATOR_HARD_2HOP` and `ARM_SOFT_CHAIN_2HOP`: s7 = 0.610 / 0.610; s17 = 0.645 / 0.645; s23 = 0.640 / 0.640. The soft-DFE mechanism (CA3 graded reactivation + 50-yr turbo-decoding lit + brain finite-temperature inference) that 5 disparate fields unanimously recommend was NEVER actually exercised.

**Question this cell answers:** at any beta in the lit-predicted soft regime (where softmax entropy is in `[log(2), log(5)]` nats ~ 0.7-1.6, i.e. top-K candidates have meaningful posterior mass), does substrate's 2-hop chained recovery exceed naive-hard baseline by >= 13pp (chain-grade revival)? OR: do all betas fail equivalently, falsifying the soft-mechanism hypothesis at this substrate regime?

## Pre-registered HARD bands (sacrosanct, symmetric)

PRIMARY METRIC: `best_soft_top1` = max(top1 across {ARM_BETA_2, ARM_BETA_10, ARM_BETA_50})

- **HARD_PASS_REVIVAL**: `best_soft_top1 >= 0.78` (>= 13pp absolute lift over baseline ~0.65) AND `best_soft_cv <= 0.05`. Confirms soft-mechanism rescue closes the multi-hop gap.
- **MIDDLE_BAND**: `best_soft_top1 in [0.70, 0.78)`. Partial rescue; tune K_SET or anisotropic encoder.
- **HARD_FAIL_DECISIVE**: ALL betas in {0.5, 2, 10, 50, 500} produce `abs(top1 - baseline_top1) <= 0.03`. Soft mechanism fundamentally fails at this regime; pivot to encoder-side (anisotropic/sparse) or PageRank-style angle (per META audit L7-alt).
- **SANITY (the wiring-bug confirmation)**: `ARM_BETA_8192 top1` must reproduce `ARM_BASELINE_HARD top1` within `+/- 0.02`. This directly confirms the audit diagnosis: at beta=N_DIM, the soft path degenerates to hard argmax.

## Apples-to-apples checklist (master bias)

- **Lane 1 declared** (substrate-native; pure numpy; no encoder leakage).
- **ONE knob varies = beta.** ALL arms share `E`, `R`, `W`, `K_SET=20`, `n_chains`, `seed`-derived RNG state, V_C, V_P. The only difference per arm is the inverse-temperature passed to the Modern-Hopfield softmax bundle. `ARM_BASELINE_HARD` is the hard-argmax control (no softmax at all); `ARM_BETA_{0.5, 2, 10, 50, 500, 8192}` sweep the softmax temperature.
- **SINGLE primary metric** per arm: top1 on 2-hop chained recovery (predicted final-object equals ground-truth final-object).
- **SAME chain queries per seed across arms**: `make_two_hop_chains(N_CHAINS, V_CONCEPTS, g)` is called once per seed; all arms evaluated on the same `queries` list. No re-randomization between arms.
- **Pre-registered PRIMARY arm:** the BEST of {BETA_2, BETA_10, BETA_50} (the lit-predicted soft regime per Frady-Sommer + Ramsauer-Hopfield + Berrou-Glavieux turbo). Choice is pre-registered, not post-hoc.
- **Pre-registered SANITY check:** BETA_8192 reproduces BASELINE_HARD (the smoking-gun re-verification).
- **No transformer / LLM** anywhere; numpy only. Substrate-only at inference.

## CONFOUND_AUDIT (per master bias checklist 2026-06-24)

- **F1 Fix #28 over-claim**: cell logs per-seed top1 per arm + per-seed bit-identity check between BASELINE_HARD and BETA_8192; verdict_msg cites per-arm numerics; per-seed entropy logged per arm (the load-bearing mechanism evidence). Cert-owner can re-derive every cited number from `per_seed`.
- **H1 capacity-respecting tier**: substrate at N=8192, V_C=200, K_SET=20 with 200 chains x 2 hops = well below capacity (M_eff/N ~ 0.05). The discriminator regime is honest; no by-construction saturation upstream of the beta knob.
- **H2 saturated discriminator**: the smoking-gun audit shows the discriminator WAS saturated in prior cells (Dirac softmax = baseline). THIS cell explicitly de-saturates by sweeping beta down 4 orders of magnitude.
- **H6 single-knob variation**: beta is the only varying knob; verified by code-review of `chain_soft_beta` (only `beta` argument differs across arm invocations).
- **G3 below-threshold framing**: HARD_PASS bar 0.78 is +13pp over baseline; not floor-hugging. MIDDLE_BAND has explicit floor 0.70.
- **K-corpus**: substrate-native synthetic 2-hop chains; no text-encoding leakage; chance = 1/V_CONCEPTS = 0.005; baseline 0.65 is ~130x over chance.
- **No-padding**: 7 arms = baseline + 6 betas; each arm informative (entropy diagnostic varies across betas even when top1 doesn't).

## Smoke evidence (informs band calibration)

Smoke at N=2048, 1 seed, n_chains=100, 7 arms (~1-3s/arm expected on CPU). The smoke runs the SAME mechanism end-to-end and verifies:
1. `selftest` Dirac equivalence: beta=N gives <0.01 nats entropy = Dirac confirmed.
2. `selftest` soft regime: beta=2.0 gives >0.1 nats entropy = soft mechanism exercised.
3. `selftest` naive vs Dirac agreement: 3/4 queries match (Dirac softmax = hard argmax).
4. Smoke prints per-arm top1 + entropy for direct inspection before FULL ship.

If smoke shows BETA_2 top1 within +/- 0.01 of BASELINE_HARD AND smoke entropy > 0.5 nats, then the soft path IS exercised but giving no lift -> updates priors toward HARD_FAIL_DECISIVE.

## Timeout estimate (per Fix #17 / PROT-019 disciplines)

D1 roofline probe in smoke (will measure actual wall before adjusting if needed):
- Per seed: 1 W-ingest (200 triples; ~0.5s at N=8192) + 7 arms x 200 queries x 2 hops each.
- Per query per arm: W @ key (N x N matmul ~ 0.06s at N=8192), then E @ transit cleanup (V_C x N dot ~ <1ms), then top-K argpartition + softmax (~<1ms).
- Per-arm wall: ~200 queries x 2 hops x 0.06s = ~24s. (The W matmul is the bottleneck.)
- Per-seed wall: 1 ingest + 7 arms x 24s = ~170s. With 3 seeds: ~510s.
- Add 2x safety + Python overhead: ~1500s.

**timeout_s = 1800** (30 min budget). Roughly 3-4x safety margin against measured FULL wall. Below PROT-021's 14400s checkpoint floor, so per-seed checkpoint is best-practice (and present) but not required.

PROT-018: anchor name has NO `_n<N>` suffix; PROT-018 N/A.
PROT-019: timeout 1800 < 14400 floor; below PROT-019 large-N tier (anchor not _n>=4096).
PROT-020: local_cpu_queue (not overnight_queue); PROT-020 N/A.

## REQUIRED_FIELDS (queue gate)

Cell emits: `verdict`, `verdict_msg`, `elapsed_s`, `summary`, plus `anchor_name`, `run_mode`, `n_seeds`, `config_version`, `per_seed` (one entry per seed with per-arm top1, entropy, conf, and beta).

## D1 / D2 disciplines

- **D1 roofline**: smoke at N=2048/100chains/1seed measures per-arm wall directly; smoke wall * (8192/2048)^1.5 * (3/1) gives FULL estimate. If smoke per-arm wall > 5s, escalate timeout or skip BETA_0_5 arm (rare; ingest is the bottleneck not the per-query softmax).
- **D2 atexit + per-seed checkpoint**: per-seed CONFIG_VERSION-gated partial JSON written under `data/exp_<anchor>/partial_seed{s}_<mode>.json` between seeds. Resume on re-dispatch. PROT-021 import of `_seed_checkpoint` present.

## Note on cell-author honesty (Fix #28)

Verdict logic reads per-seed per-arm top1 + entropy and aggregates with explicit cv. Verdict_msg includes:
- BASELINE_HARD top1
- best-soft beta + best-soft top1 + delta + cv
- BETA_8192 top1 (sanity dirac check)
- per-beta one-line summary (top1, delta, entropy, cv)

Cert-owner re-derives off `per_seed`; verdict_msg should not be the primary source of any cited number.

## How the cell's verdict maps to the Wave A scientific decision

- HARD_PASS_REVIVAL: substrate's multi-hop is honest; the prior 2 cells' HARD_FAILs were a wiring bug; soft-DFE mechanism transfers from lit. Promote soft-chain primitive to hdlab/. Re-classify prior cells as `HARD_FAIL_MEASUREMENT_CONFOUND` in cert ledger.
- MIDDLE_BAND: soft mechanism partial; the regime needs additional discrimination (K_SET sweep, encoder anisotropy, or hop-3 extension). Route follow-up to Research for a per-K drill.
- HARD_FAIL_DECISIVE: soft mechanism is genuinely insufficient at substrate-isotropic-bipolar regime; pivot to encoder-side (per META audit L2 information-geometry diagnosis) or PageRank-style multi-step accumulation.

Pre-reg complete. Cell + this prereg committed to main BEFORE dispatch.
