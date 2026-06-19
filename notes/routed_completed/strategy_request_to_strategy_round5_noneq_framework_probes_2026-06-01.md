# Strategy request: Round 5 non-eq stat-mech framework probes (4-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_round5_7_drills_synthesis_2026-06-01.md` (full synthesis)
**Trigger**: user "do all" greenlight after recommending non-eq framework probe in response to today's TWO mean-field framework refutations (percolation v312 + free-probability v316)

## TL;DR

4 non-equilibrium stat-mech framework drills landed. **Substrate's empirical home framework cluster is now substantively narrowed**: non-equilibrium dynamical mean-field class with MCT/DMFT phenomenology + Crooks-S-U thermodynamic bounds. Three of four frameworks (DMFT, Crooks, Sagawa-Ueda) deliver OPERATIONALLY USEFUL predictions; one (DDBP) splits into DD (useful) + BP (limited by dense loops).

**Critical structural insight**: Crooks FT is **FINITE-N EXACT** by construction. Today's two refutations were N→∞ assumption failures (percolation N-independence, free-probability free-additivity). Non-eq frameworks below are valid at substrate's actual operating regime.

**Strongest empirical precedent**: Nanomagnetic Hopfield Network (arXiv 2202.02372, Nature Physics 2022) observed MCT signatures directly in artificial Hopfield. **Substrate is in an experimentally-validated MCT/DMFT universality class.**

## TIER 1 DISPATCH (highest-info-per-dollar across 4 frameworks)

| # | Test | Cost | Validates |
|---|---|---|---|
| **NE-1** | **MCT/DMFT aging signature** | **~60s CPU; ZERO theory required** | Pure simulation; binary aging present/absent above α_c |
| **NE-2** | **DMFT retrieval cliff (Hara-Kabashima 2026)** | **~60s CPU; 5-seed × 3 α** | Substrate in DMFT universality class |
| **NE-3** | **Crooks Candidate 2 KL-divergence drift detection** | **trajectory logging in existing multi-hop runs** | Operational drift-detection killer feature |
| NE-4 | S-U Axis 1 Landauer cert cost (log_2(M) bound) | ~5 min CPU; N=128, M up to 32 | Cert sizing for PP-30 + GDPR Art 17 audit |
| NE-5 | S-U Axis 2 audit no-benefit theorem | Trivial add-on | Design constraint: audit is read-only |

**Total cost: ~10 min CPU + trajectory logging instrumentation.** Each pre-reg with explicit HARD-PASS / MIDDLE-BAND / HARD-FAIL per [[feedback-no-preframe-batch-all-pass]].

## NEW CAP_MAP ROW PROPOSED

**"Non-equilibrium stat-mech framework class membership"** — 🔬 0.40-0.55

Anchors:
- MCT/DMFT universality (Hara-Kabashima 2026 + Nanomagnetic Hopfield Nature Physics 2022)
- Crooks finite-N applicability (symmetric J_ij satisfies microreversibility)
- Sagawa-Ueda lower bounds on cert cost + retrieval feedback
- Today's TWO mean-field refutations narrow the space

This row CLOSES the 12-day-overdue framework-class identification (since `[[project-substrate-non-eq-stat-mech-class-2026-05-27]]` first proposed the class but didn't pin specific framework).

## EXPLICIT CLOSURES RECOMMENDED

- **DDBP "unified theory" interpretation** — N-independence argues against simple DD diffusion at depth cliff; close as "DD half useful, BP half limited"
- **S-U Axis 4** — recovers known mean-field, adds nothing; close
- **Crooks Candidate 4** — variance problem near phase transitions; close

## TIER 2 (medium-priority follow-ons; defer per Tier 1 outcomes)

- DDBP App 2 K_crit correlated edits (P=0.30; novel angle vs free-probability)
- DDBP App 4 forgetting first-passage (P=0.35; most theoretically mature)
- Crooks Candidate 1 Jarzynski capacity bound (P=0.30)
- MCT App 4 critical exponents at depth-composition cliff (P=0.28; requires multi-hop MCT extension)
- S-U Axis 3 multi-hop T_crit bound (P=0.35-0.55)

## CONTRACT FOR STRATEGY

1. **Dispatch NE-1 through NE-5 (combined ~10 min CPU)?** Five orthogonal tests across four frameworks; aggregated outcome substantively narrows substrate's theoretical home
2. **Authorize NEW cap_map row** "Non-equilibrium stat-mech framework class membership"?
3. **Confirm CLOSURES** on DDBP-unified / S-U A4 / Crooks C4?
4. **Defer Tier 2 follow-ons** until Tier 1 outcomes inform sequencing?

## METHOD NOTES

- 4 parallel Sonnet drills + synthesis; all generic stat-mech / VSA terms only
- Per [[feedback-no-preframe-batch-all-pass]]: explicit pre-reg bands per design
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; novel-synthesis cap 0.50; additional 0.05-0.10 deflation given today's framework refutations
- Strong literature anchors: Hara-Kabashima 2026 DMFT for Hopfield+plasticity; Nanomagnetic Hopfield Nature Physics 2022; Crooks 1999 + Jarzynski 1997; Sagawa-Ueda 2008

## CLOSING

Move to `routed_completed/` when strategy authorizes Tier 1 dispatch + NEW cap_map row + 3 closures.


**Acted-on 2026-06-01:** NE-1 through NE-5 AUTHORIZED via exp_dev dispatch; NEW PP-33 row ADOPTED at 0.40-0.55 EXPLORATORY in cap_map v319; 3 closures applied (DDBP-unified / S-U A4 / Crooks C4); cap_map intro framework-calibration paragraph updated with non-eq stat-mech context.