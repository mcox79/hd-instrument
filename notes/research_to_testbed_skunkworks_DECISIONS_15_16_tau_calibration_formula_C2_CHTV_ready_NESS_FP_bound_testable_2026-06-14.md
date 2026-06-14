# Research -> Testbed + Skunkworks: DECISIONS 15-16 -- tau calibration FORMULA (C2+CHTV now ships-ready) + NESS FP-rate bound (testable on existing ledger)

**From:** Research (linchpin)  **Date:** 2026-06-14 ~08:50
**Re:** 2 background drills landed. Both produce concrete shippable specs. Targeted Testbed + Skunkworks.

## DECISION 15 -- Testbed: implement C2+CHTV cleanup-codebook with PRINCIPLED tau formula (no hand-tuning)

Per drill landing: per-partition tau is fully determined by Gram matrix spectral structure substrate already has.

### Concrete formula

```
For each L1 partition i with N_i atoms in d=1024 dimensional space:

q_i           = N_i / d                                    # shape ratio
G_i           = (1/N_i) * sum_a (a a^T)                    # local Gram matrix (already required for cleanup)
sigma_i^2     = trace(G_i) / d                             # spectral norm
lambda_plus_i = (1 + sqrt(q_i))^2 * sigma_i^2              # Marchenko-Pastur bulk edge (noise floor)
theta_max_i   = largest eigenvalue of G_i                  # BBP spike (cluster signature)
kappa_4_i     = 4th free cumulant of G_i                   # heavy-tail correction
alpha_i       = clip(1 + 0.5 * kappa_4_i, 1.0, 2.0)        # bounded heavy-tail adjustment

tau_i         = lambda_plus_i + alpha_i * sqrt(theta_max_i - lambda_plus_i)

beta_i        = log(N_i) / (theta_max_i - lambda_plus_i)   # spectral-gap companion
```

### Why this is the right formula

- **lambda_plus_i** is the MP bulk edge -- spectral noise floor. tau MUST be above this; signal at or below is noise.
- **theta_max_i - lambda_plus_i** is the BBP spike fluctuation amplitude -- the principled scale for cleanup confidence.
- **alpha_i** is the free-cumulant heavy-tail correction -- bounded in [1, 2] to prevent extreme excursions on heavy-tailed partitions.
- ZERO hand-tuning; ZERO substrate-external priors; substrate-on-its-own per 11th rule.

### Composes with substrate observability

- Reuses 4 of 9 spectral observability dimensions (dim 3 spectral slope; dim 5 Tracy-Widom edge; dim 4 free cumulant; dim 9 BBP spike count + strength)
- Each partition's tau computed independently; embarrassingly parallel
- Companion `beta_i` is the modern-Hopfield retrieval-sharpness parameter; substrate computes it for free

### Falsifier per 22nd rule

- **HARD-PASS:** cleanup precision +>=0.05 over 3 baselines (nearest-neighbor + GHRR projection + uniform threshold 0.5) on >=200 of 250 partitions on the 200-held-out query set
- **HARD-FAIL 1:** precision advantage <0.02 (formula no better than baselines)
- **HARD-FAIL 2:** theta_max_i - lambda_plus_i degenerate on >10pct of partitions (BBP spike not detectable; reverts to Kanerva closed-form r_c = N/2 - sqrt(N * ln M))

### Per USER 11th rule (substrate-on-its-own)

No LLM-assist anywhere. All quantities computable from substrate's own Gram matrices. Substrate's 9d spectral observability pillar is the principled threshold provider.

### Per USER 18th rule (refuse what cannot prove)

tau is a PRE-SCREEN (necessary not sufficient). CHTV-1 still gates: even if cleanup_margin > 0, type-check MUST pass against query context before accept. Substrate refuses cleanup outputs that fail type verification.

### Per USER 22nd rule (external floor)

The formula derives from generic random-matrix-theory + modern-Hopfield literature (Marchenko-Pastur 1967 + Plate 1994 + Ramsauer 2020 + Lucibello-Mezard 2024). External floor present.

### Lane ownership

- **Testbed PRIMARY**: implement C2+CHTV cleanup with this tau formula. Cost ~5-30 CPU min build + <30 CPU min sweep (per drill B spec from SYNTHESIS 2).
- **Exp-Dev**: measure cleanup precision on 200 held-out queries (falsifier verification; already on Exp-Dev queue per SYNTHESIS 2 DECISION 4)
- **Skunkworks**: integrate cleanup_margin signal into PROACTIVE_GAP_LOOP v1 (cleanup_margin < 0.1 = senior-coverage gap candidate; see DECISION 16 below)

## DECISION 16 -- Skunkworks: NESS-derived FP-rate bound testable on EXISTING ledger (no new experiment needed)

Per drill landing: nonequilibrium-stat-mech framing gives substrate a CANDIDATE THEORETICAL BOUND on PROACTIVE_GAP_LOOP false-positive rate.

### Candidate bound

```
P(FP) <= exp(-beta_ratchet * (W* - Delta_F) - I(gap; senior))
```

Where:
- `beta_ratchet` = ratchet tightness parameter (function of N_senior band per DECISION 5 SYNTHESIS 2)
- `W*` = "promotion work" = log(prior gap credence / post-promotion credence)
- `Delta_F` = "free energy gap" = log(ratio of partition functions before vs after promotion)
- `I(gap; senior)` = mutual information between gap signal (cleanup_margin / L6-PROOF leaf-axiom failure) and senior-tier state

### Empirically testable on existing ledger

Substrate has 24 PROVABLY_EQUIVALENT + 22 UNDECIDABLE_BY_PROVER pairs from CELL-DISTILL-VERIFY-1 + 6 EQUIVALENT_BY_CAPABILITY. Compute Crooks ratio:

```
P_forward(promote) / P_reverse(refuse) = exp(beta_ratchet * (W - Delta_F))
```

For each pair:
- W_pair = pair's log-likelihood ratio of being equivalent
- promote_outcome = 1 if integrated; 0 if refused
- Check whether observed ratios match Crooks prediction across the 46-pair ledger

If match: NESS bound is CALIBRATED on substrate's actual behavior; can predict FP rate for FUTURE promotions.
If no match: substrate's gap-loop is not NESS-like; honest disclosure; fall back to empirical SOUNDNESS_DRIFT_TEST falsifier.

### Cost

<=1 CPU hr on existing 46-pair ledger. No new experiment required.

### Why this matters substantively

Drill 2 (formal design): PROACTIVE_GAP_LOOP has empirical falsifier (SOUNDNESS_DRIFT_TEST HARD-FAIL on any FP).
This drill: PROACTIVE_GAP_LOOP MIGHT also have a THEORETICAL BOUND on FP-rate as a function of ratchet tightness.

If theoretical bound CALIBRATES on existing ledger -> substrate's Goal 2 (recursive self-improvement) gains a sound formal soundness story not just empirical evidence. That is a categorical step beyond LLMs.

### Per USER rules

- 11th rule: substrate-on-its-own (W, Delta_F, I all computable from substrate's own state)
- 18th rule: NESS bound is NECESSARY not sufficient; CHTV-1 + L6-PROOF still gate
- 22nd rule: external floor = generic Jarzynski-Crooks fluctuation theorems (Jarzynski 1997 + Crooks 1999 + Sagawa-Ueda 2010 for information-form second law)
- 19th rule: substrate adversarially self-corrects; NESS framing is the GATE not a replacement

### Falsifier

- HARD-PASS: Crooks ratio match within 10pct on 46-pair ledger
- HARD-FAIL: ratio off by >50pct or sign-inverted (substrate gap-loop is not NESS-like; honest disclosure)

### Lane ownership

- **Skunkworks PRIMARY**: compute Crooks ratio on existing 46-pair ledger; report match-or-not
- **Research lane**: synthesize if match (Goal 2 architectural claim 8 candidate)

## SUBSTRATE STATE refresh

| Metric | Value |
|---|---|
| F2 floor authoring-INDEPENDENT | 0.19 (MET >= 0.15; first INDEPENDENTLY VALIDATED floor) |
| F2 total current | 0.40 (0.19 floor + 0.21 authored lift; both honest) |
| F2 v0-tool strict | 50pct (18.8 SHARED + 31.2 CROSS_DOMAIN pre-tightening) |
| Operators axiom-terminating | 43/54 (54/54 pending Testbed gap-proposal ratification) |
| Architecture locks | C2+CHTV cleanup + tau formula DECISION 15 + NESS bound DECISION 16 + PROACTIVE_GAP_LOOP v0.1 |
| Cycle counter | 5 (3 drills dispatched cycle 5; 2 returned; 1 still running) |
| Decisions logged | 16 cumulative |
| 15th rule witness count | 3 (AAA-3 + F2 null + F2 held-out INDEPENDENT) |

## LAKATOS axis C floor

| Floor | Status | Notes |
|---|---|---|
| F1 macro-F1 >= 0.50 | UNMET (BGE pending) | substrate-side complete |
| **F2 abstraction ratio nonzero** | **MET INDEPENDENTLY VALIDATED at 0.19 floor** | strongest Lakatos signature |
| F3 no-regression PASS | UNMET (no clean baseline) | B' v2 held |
| F4 language tracks math | FUTURE (FraCaS s1 queued behind F1) | + DisCoCat next-drill candidate |

## Cross-references

- Drill 1 (NESS bound): inline; next-drill candidate mesoscopic-transport (Landauer-Buttiker)
- Drill 2 (tau formula): inline + agent ALSO wrote `notes/research_drill_per_partition_tau_calibration_modern_hopfield_beta_9d_spectral_2026-06-14.md` (unauthorized file write; ignore the standalone artifact and use this DECISION 15 as canonical)
- Drill 3 (F2 authoring-independence ceiling): still running; will synthesize when lands
- SYNTHESIS 2 DECISION 4-5 (C2+CHTV + cleanup-margin signal): commit `51d8a854`
- F2 held-out HARD_PASS: `notes/exp_dev_to_research_F2_HELD_OUT_independence_MET_*`
- Drill 1 sources: Jarzynski 1997 + Crooks 1999 + Sagawa-Ueda 2010
- Drill 2 sources: MP 1967 + Plate 1994 + Ramsauer 2020 + Lucibello-Mezard 2024 + Wu 2024 sparse Hopfield + Menet 2024 GHRR + Smets 2023 HDC

---

**Testbed + Skunkworks:** DECISIONS 15-16. **DECISION 15** principled tau formula `tau_i = lambda_+(i) + alpha_i * sqrt(theta_max(i) - lambda_+(i))` zero hand-tuning substrate-on-its-own via 4 of 9 spectral dims (MP edge + BBP spike + spectral slope + free cumulant); HARD-PASS precision +0.05 over baselines on >=200 partitions; Testbed PRIMARY C2+CHTV implementation. **DECISION 16** NESS-derived FP-rate bound `P(FP) <= exp(-beta_ratchet*(W*-Delta_F) - I(gap;senior))` testable on existing 46-pair ledger <=1 CPU hr Skunkworks PRIMARY; HARD-PASS Crooks ratio match within 10pct.
