# RESEARCH (Director) — K_max NESS-correction DRILL plan per USER GO on recommendation B. Theoretical drill + empirical-envelope characterization. Closes the gap "substrate reasons deeper than equilibrium-K_max predicts but we have no closed-form NESS-corrected bound". Director-side drill (not Exp-Dev cell-build); produces theory note + empirical envelope.

(Filename has no `to_<recipient>` — Director/Research-side theoretical drill.)

## Context

USER recommendation B: "K_max NESS-correction — theoretical drill + empirical envelope". USER GO via "implement your recommendations" 2026-06-20.

The gap (capability_scorecard.md 2026-06-05 01:20): "K_max formula 3.3 × (1 - α/α_c)² / α is PESSIMISTIC; substrate reasons deeper than predicted; likely NESS-dynamics correction needed". Empirical data: SQ2 K=12 single + SQ2 × hierarchical 24-hop + cleanup-augmented 6× boost — all in the "shouldn't work" regime per the equilibrium formula.

Productization implication: without closed-form NESS-corrected K_max, we can promise substrate depth-bound only by empirical-envelope (e.g. "tested to 24-hop hierarchical"), not theoretical bound. Limits Phase 3 glass-box-LLM depth confidence.

## Drill plan

### Component 1: theoretical drill (literature + algebra)

**Task:** dispatch 2 Research subagents in parallel for:

**(a) Non-equilibrium-corrected Hopfield depth bounds lit-scan:**
- Targets: Crisanti-Sompolinsky 1988 (non-eq Hopfield); Aleksandr 2015 (non-eq SK); Hertz-Krogh-Palmer textbook (NESS Hopfield depth); recent (2020+) non-eq associative memory + NESS / NHSE-class corrections
- Question: does the lit have a closed-form NESS-corrected K_max formula? Or only equilibrium?
- If lit has form: validate against substrate empirical data (24-hop hierarchical + cleanup-augmented 6×)
- If no closed-form: characterize the gap; surface partial-derivations + corrections

**(b) Algebraic re-derivation from substrate's NESS dynamics:**
- Substrate has write-decay equilibrium: W ← (1-α)W + outer-product; alpha = write-rate
- Equilibrium derivation assumes ∂W/∂t = 0 between hops; NESS assumes write-rate × decay-rate = constant
- Question: does the substrate's per-hop SNR have an algebraic NESS correction that extends K_max by the empirical 2-6× factor? Derive from first principles.
- Compose with cleanup-augmentation: 6× boost suggests cleanup acts as iterative-noise-removal that resets SNR per hop; quantify

### Component 2: empirical envelope characterization (no theoretical commitment)

**Task:** Exp-Dev cell-build (when bandwidth opens past CSP + drift + graceful + Pythia-KV + neurogenesis + Phase 0c probes) for K_max empirical envelope:
- Sweep K ∈ {6, 12, 24, 36, 48, 60} at α ∈ {0.1, 0.25, 0.5} × α_c
- N=8192; cleanup-augmented (6× variant); 5 seeds per (K, α)
- Measure: recall_at_K (the deeper-end-of-chain accuracy) + cleanup-iters-required to converge
- HARD-PASS at K=24 (the hierarchical anchor); MIDDLE_BAND at K=36-48; HARD_FAIL at K=60 likely

**Composes with:** the just-authored composition extensions pre-reg (TIER-2 #1, commit 9bbb6954) — that pre-reg sweeps K ∈ {12, 24, 36, 48} at N ∈ {2048, 4096, 8192}; this envelope work can BATCH with that cell or run separately at fixed N=8192 with finer α-sweep.

### Component 3: synthesis (Director)

When (1)(a) lit-scan + (1)(b) algebraic re-derivation results land + Component 2 empirical envelope lands:
- Synthesize: closed-form NESS-corrected K_max + empirical-envelope validation + cleanup-augmentation factor
- Outcome: cert-grade theoretical claim ("substrate K_max follows formula X with NESS correction Y per algebra Z; validated empirically at K=24+ hierarchical + cleanup-augmented 6× boost")
- Productization implication: substrate can be promised depth-bound K with theoretical backing at production-config-points

### Discriminating outcomes

- **Best case:** lit has closed-form NESS-corrected K_max + substrate empirical matches within 10% → strong cert claim
- **Middle case:** lit has partial corrections + my algebraic re-derivation produces a fit → workable theoretical bound with caveats
- **Worst case:** no closed-form possible at substrate's NESS regime → ship the EMPIRICAL ENVELOPE as the production bound; document the theoretical gap as a known open

## Sequencing

- **Component 1 (theoretical):** dispatch 2 Research subagents NOW (parallel); ~1-2 cycles to land
- **Component 2 (empirical):** queue Exp-Dev cell-build at LOW priority (behind active substrate-capability cells); batch with composition extensions cell if feasible
- **Component 3 (synthesis):** Director-side after (1)+(2) land; ~1 cycle

Total wall-clock estimate: 3-5 cycles for full landing.

## Pre-reqs
- No GPU dependencies for Component 1 (theoretical/lit-scan)
- Component 2 GPU cost: ~3 hours GPU (modest; 18 conditions × 5 seeds × N=8192)
- Skunkworks SCHEMA-VET on the empirical envelope pre-reg (when authored post-Component 1 synthesis)

## Standing
- **Research subagents:** I dispatch Component 1 lit-scan + algebraic re-derivation NOW (parallel)
- **Exp-Dev:** Component 2 empirical envelope cell-build queued at LOW priority; can batch with composition extensions cell if feasible
- **Skunkworks:** informational; SCHEMA-VET when Component 2 pre-reg authored post-synthesis
- **Me:** synthesizing Components 1+2 when they land; productization-grade NESS-corrected K_max is the deliverable

-- Research (Director)
