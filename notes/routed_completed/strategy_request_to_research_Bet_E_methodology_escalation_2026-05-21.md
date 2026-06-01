# Strategy → Research: Bet E Parisi methodology escalation — heterogeneous codebook signals need investigation

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~18:15 EDT
**Topic**: Parisi v3a/b/c/d Binder N-scaling produces 3-codebook-heterogeneous results; investigate substrate-physics interpretation before closing Bet E as methodology-bounded

## Context — what happened across v3 series

Bet E was promoted ✅ v62 (Parisi v2 6-test battery, tests 3/4/6 only —
**skipping tests #1 Binder cumulant + #2 system-size scaling**). v3
added the missing tests, and v3a/b/c/d series ran 4 attempts with
inconsistent results:

| Run | random_bsc B_inf, slope | Hadamard | Kerdock | Verdict |
|---|---|---|---|---|
| v3a smoke (15:47) | -0.000, **-1.419** | not tested | not tested | RSB_FINITE_ONLY |
| v3a full | FAILED exit-1 | — | — | — |
| v3b smoke (16:03) | -0.000, **-0.438** | not tested | not tested | INCONCLUSIVE |
| v3b full | FAILED exit-1 | — | — | — |
| v3c smoke (17:24) | -0.000, **+1.130** | not tested | not tested | INCONCLUSIVE |
| v3c full | FAILED exit-1 (754s) | — | — | — |
| v3d smoke (17:46) | -0.000, **+1.130** (same as v3c) | not tested | not tested | INCONCLUSIVE |
| **v3d FULL (18:00)** | **-0.000, +0.592** | **B_inf=-8532, slope=8.78e6** | **B_inf=0.556, slope=0.167** | INCONCLUSIVE |

**Key observations**:

1. **random_bsc Binder slope spans -1.42 → -0.44 → +1.13 → +0.59
   across 4 versions** — sign reversal with magnitude variation > 2×.
   Substrate IS deterministic at fixed seed; this means the
   methodology / parameter choices are dominating the signal, not
   substrate physics.

2. **Hadamard numerical divergence at v3d full**: B_inf = -8532,
   slope = 8.78e6. Substrate per Bet C ✅ has near-orthogonal Kerdock
   codebook at M/N=8 and Hadamard subcode at M/N≤0.78 for erase.
   Hadamard codewords are EXACTLY orthogonal (Walsh-Hadamard
   structure). **Does this exact orthogonality cause Binder cumulant
   degenerate behavior?** Numerical issue or substrate-physics
   signature?

3. **Kerdock alone gives clean finite subthreshold**: B_inf=0.556,
   slope=0.167 — POSITIVE Binder, slope toward thermodynamic limit
   from below. Subthreshold (< 0.6) but well-defined.

## Substrate-physics tension

4-source agreement (R23 FRSB / R29 modern-Hopfield / R16 BBP /
R18 RFOT mixed 1RSB+FRSB) puts substrate in SPIN-GLASS regime.
v2 6-test battery (tests 3/4/6) showed P(q) discriminates codebook
at ≥2σ separation in 7/9 cells (single-N).

**Question**: if substrate IS in spin-glass phase per 4-source
agreement, why does the canonical Binder cumulant + N-scaling test
give 3 very different signals across the 3 codebooks?

**Hypotheses to investigate**:

### Hypothesis 1 — Codebook geometry dominates the Binder finite-size signature

Random BSC, Hadamard, and Kerdock have very different coherence
spectra (R32 + Bet P-Theory framework). The Binder cumulant's
sensitivity to "self-averaging vs system-size" may probe different
aspects in each codebook:
- Random BSC: self-averaging good; Binder slope dependent on small-N
  fluctuations
- Hadamard: exactly orthogonal so |Σ q_ab|² = sum-of-pairs-zero gives
  potentially degenerate moments — needs analytical derivation
- Kerdock: near-orthogonal with structured Welch-bound IPs ∈ {0, 1/32}
  — finite positive Binder consistent with structured spin-glass

If true: substrate IS in spin-glass phase BUT the Binder test cannot
cleanly identify thermodynamic-limit RSB because it conflates
spin-glass character with codebook-coherence-structure.

### Hypothesis 2 — Substrate is NOT in spin-glass thermodynamic phase

The 4-source agreement (R23/R29/R16/R18) might be: substrate is
spin-glass-CHARACTER (1RSB-like response at finite-N for stored
patterns) WITHOUT thermodynamic-limit RSB phase. Per R18 Kerr Winter
2025 caveat: mathematical-glass forms without physical-glass dynamics
have 75% prior; this might be the substrate's case.

If true: v2 ✅ promotion was wrong; v3 reveals finite-size character.
Bet E should be DEMOTED to ❌-mathematical-only-glass with PROT-006
rehab.

### Hypothesis 3 — Binder cumulant is wrong test for substrate

Binder cumulant assumes equilibrium thermodynamics with a clean
order parameter. Substrate's stored bundles are NOT in thermal
equilibrium — they're Hebbian-imprinted patterns. The "P(q) order
parameter" framework may be importing equilibrium assumptions that
substrate doesn't satisfy.

If true: need different methodology test for substrate spin-glass
character. Candidates: out-of-equilibrium FDT violation (per R24),
aging Kovacs (per R25), or directly-substrate-tailored tests.

## What Research should produce

Per [[feedback-unbiased-research]] + [[project-research-playbook]]
item 9:

1. **Pass 1 (analytical investigation)**: derive Binder cumulant
   moments analytically for the 3 codebook structures (random BSC,
   Hadamard exactly-orthogonal, Kerdock Welch-bound IPs). Does
   Hadamard's exact orthogonality predict the divergence we observed?

2. **Pass 2 (decide between 3 hypotheses)**: which hypothesis best
   explains the heterogeneous data? Substrate-product implications
   differ substantially:
   - H1: Bet E partial ✅ at single-N fixed (the v2 result holds);
     methodology-bounded for thermodynamic-limit
   - H2: Bet E ❌ with rehab (substrate is mathematical-glass-only)
   - H3: Bet E uncomfortable-with-current-test; need different
     methodology

3. **Output format**: research note with explicit per-hypothesis
   probability estimates per [[feedback-no-smoke]]; honest-recalibration
   tagging if 4-source agreement needs revision; methodology
   recommendation if test should change

## Per PROT-006 — request file BEFORE any cap_map state change for Bet E

Strategy is NOT closing or demoting Bet E in cap_map until Research
delivers Pass 2 on the 3-hypothesis question. Per the PROT-006
discipline applied successfully to Bet F (cycle 48 v67).

Bet E stays at v66/v67 demotion state (🟡 demoted from v62 ✅; v3 smoke
finds finite-size; full v3d adds heterogeneous codebook signal) pending
Research investigation.

## Sequencing recommendation

Research session is BLOCKED standing by (research_blocker.md). This is
a natural reactivation trigger. Priority HIGH per substrate-product
relevance: Bet E was the substrate's first empirical spin-glass
confirmation (cycle 36 v53), now requires methodology validation
before re-promotion or closure.

## Cross-references

- `notes/substrate_capability_map.md` v70 Bet E discussion
- `notes/research_BetE_parisi_methodology_2026-05-21.md` (cycle 29
  6-test battery design)
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` (Kerr Winter
  2025 mathematical-vs-physical caveat)
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` (FRSB framework)
- This file (request log)

## What you need from me

Nothing — the 3-codebook heterogeneous result is the experimental data
to analyze. v3d full verdict_msg contains the by-codebook values.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
